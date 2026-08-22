#!/usr/bin/env python3
import sys
import os
import datetime
from pathlib import Path

# 添加项目根目录到 Python Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from scripts.daily_ai.fetchers.rss_official import OfficialRSSFetcher
from scripts.daily_ai.fetchers.google_search import GoogleSearchFetcher
from scripts.daily_ai.fetchers.hacker_news import HackerNewsFetcher
from scripts.daily_ai.fetchers.huggingface import HuggingFaceModelsFetcher, HuggingFacePapersFetcher
from scripts.daily_ai.fetchers.arxiv import ArxivFetcher
from scripts.daily_ai.fetchers.github_trending import GitHubTrendingFetcher
from scripts.daily_ai.fetchers.applications import ApplicationsFetcher
from scripts.daily_ai.fetchers.perplexity_fallback import PerplexityFallbackFetcher
from scripts.daily_ai.processors.deduplicator import Deduplicator
from scripts.daily_ai.processors.quality_scorer import QualityScorer
from scripts.daily_ai.generators.chapter_writer import ChapterWriter
from scripts.daily_ai.renderers.jinja_renderer import JinjaRenderer

BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))

try:
    from scripts.update_word_count import calculate_reading_stats
except ImportError:
    import re
    def calculate_reading_stats(text, reading_speed=400):
        # Fallback reading stats
        word_count = len(re.findall(r'[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]', text))
        if word_count == 0 and len(text) > 0:
             word_count = len(text.split())
        reading_time = max(1, (word_count + reading_speed - 1) // reading_speed)
        return word_count, reading_time

class Orchestrator:
    def __init__(self):
        # Fetchers 注册表
        self.fetchers = {
            'official_rss': OfficialRSSFetcher(),
            'google_search': GoogleSearchFetcher(),
            'hacker_news': HackerNewsFetcher(min_points=15, hours_back=48),
            'hf_models': HuggingFaceModelsFetcher(),
            'arxiv_papers': ArxivFetcher(),
            'hf_papers': HuggingFacePapersFetcher(),
            'github_projects': GitHubTrendingFetcher(),
            'applications': ApplicationsFetcher(),
            'perplexity_news': PerplexityFallbackFetcher()
        }
        
        # Processors
        history_file = project_root / "scripts" / "daily_ai" / "data" / "history.json"
        self.dedup = Deduplicator(history_file=history_file)
        self.scorer = QualityScorer()
        
        # Generator & Renderer
        self.writer = ChapterWriter()
        self.renderer = JinjaRenderer()
        
        self.content_dir = project_root / "content" / "zh" / "daily_ai"
        
    def _fetch_all(self):
        print("====== [Pipeline Step 1] 多源高信噪比数据采集 ======")
        raw_data = {}
        for key, fetcher in self.fetchers.items():
            print(f"[INFO] 正在调度采集源: {fetcher.name} ({key}) ...")
            try:
                 raw_data[key] = fetcher.fetch()
            except Exception as e:
                 print(f"[ERROR] {fetcher.name} 抓取抛出异常: {e}")
                 raw_data[key] = []
                 
        # 逻辑合并与归类
        data = {}
        # 1. 焦点新闻: 官方 RSS + Google 搜索聚合
        data['focus_news'] = raw_data.get('official_rss', []) + raw_data.get('google_search', [])
        
        # 2. 开源模型: Hugging Face Models
        data['hf_models'] = raw_data.get('hf_models', [])
        
        # 3. 学术论文: HF Daily Papers (高赞) + arXiv
        data['arxiv_papers'] = raw_data.get('hf_papers', []) + raw_data.get('arxiv_papers', [])
        
        # 4. 开源工具: GitHub Trending
        data['github_projects'] = raw_data.get('github_projects', [])
        
        # 5. 极客热议: Hacker News
        data['hacker_news'] = raw_data.get('hacker_news', [])
        
        # 6. 落地应用: Product Hunt & Show HN Apps
        data['applications'] = raw_data.get('applications', [])
        
        # 7. 感知层兜底 (仅在焦点过少时补充)
        if len(data['focus_news']) < 2 and raw_data.get('perplexity_news'):
            data['perplexity_news'] = raw_data.get('perplexity_news', [])

        return data
        
    def _process_data(self, data):
        print("====== [Pipeline Step 2] 数据脱水、语义去重与质量打分 ======")
        processed_data = {}
        top_k_map = {
            'focus_news': 4,
            'hf_models': 4,
            'arxiv_papers': 4,
            'github_projects': 4,
            'hacker_news': 3,
            'applications': 3,
            'perplexity_news': 2
        }

        for key, items in data.items():
            if not items:
                processed_data[key] = []
                continue
                
            unique_items = self.dedup.process(items)
            scored_items = self.scorer.process(unique_items)
            
            top_k = top_k_map.get(key, 3)
            processed_data[key] = scored_items[:top_k]
            print(f"[INFO] 章节【{key}】: 经过评分雷达精选 Top {len(processed_data[key])} 条内容")
             
        return processed_data
        
    def _generate_chapters(self, processed_data):
        print("====== [Pipeline Step 3] 结构化 Prompt 注入与多角色内容生成 ======")
        chapters = {}
        all_written_sections = []

        for key, items in processed_data.items():
            if items:
                content = self.writer.write_section(key, items)
                chapters[f"{key}_content"] = content
                all_written_sections.append(f"【{key}】\n{content}")
            else:
                chapters[f"{key}_content"] = ""
        
        combined_text = "\n\n".join(all_written_sections)

        # 1. 生成 60 秒极客速览 (Executive Summary)
        print("[INFO] 正在生成【60秒极客速览】...")
        summary_prompt = (
            "你是一位资深科技媒体主编。请根据以下今日AI核心动态内容，提炼出【今日最重要的3大极客看点】。\n"
            "写作要求：\n"
            "- 用极度精炼、抓人眼球的 bullet points，每条不超过40字，点明核心价值与影响。\n"
            "- 直接输出3条列表（格式如：1. 🚀 ... \n2. 🧠 ... \n3. 🛠️ ...），不要输出任何前言、客套话或结尾套话。\n\n"
            f"今日精选内容：\n{combined_text[:3000]}"
        )
        summary_res = self.writer.ai.generate(summary_prompt)
        if not summary_res or "生成失败" in summary_res or "未初始化" in summary_res:
            # 智能提取 Top 3 条目的核心标题作为速览
            top_highlights = []
            if processed_data.get('focus_news'):
                top_highlights.append(f"1. 🚀 **重大焦点**：{processed_data['focus_news'][0].title}")
            if processed_data.get('hf_models'):
                top_highlights.append(f"2. 🧠 **开源模型**：{processed_data['hf_models'][0].title} 引发社区广泛关注")
            if processed_data.get('github_projects'):
                top_highlights.append(f"3. 🛠️ **极客工具**：{processed_data['github_projects'][0].title} Star 增速强劲")
            summary_res = "\n".join(top_highlights) if top_highlights else "今日 AI 行业动态持续演进，官方实验室与开源生态百花齐放。"

        chapters["executive_summary"] = summary_res

        # 2. 生成编辑总评与趋势洞察
        print("[INFO] 正在生成【编辑总评与趋势洞察】...")
        review_prompt = (
            "你是一位资深人工智能首席分析师。请基于今日的全部动态，撰写一段150字左右的独到产业趋势点评。\n"
            "写作要求：\n"
            "- 从技术演进、商业壁垒或算力生态的角度一针见血地点评今日核心风向。\n"
            "- 语气冷静、犀利、专业，严禁任何公关套话（如“未来可期”、“让我们拭目以待”）。\n"
            "- 直接输出点评正文段落，不要加任何标题。\n\n"
            f"今日动态清单：\n{combined_text[:3000]}"
        )
        review_res = self.writer.ai.generate(review_prompt)
        if not review_res or "生成失败" in review_res or "未初始化" in review_res:
            review_res = (
                "今日动态显示，大模型厂商正加速从单纯的基础参数竞赛转向高价值垂类场景深耕与推理工程优化；"
                "同时，开源社区在极客工具、多模态部署与小参数蒸馏架构上的创新势头尤为迅猛，"
                "端侧推理与全栈智能体系统正在成为落地应用的核心主战场。"
            )
        chapters["editor_review_content"] = review_res
        
        return chapters


    def run(self):
        # 1. Fetch
        raw_data = self._fetch_all()
        
        # 2. Process
        processed_data = self._process_data(raw_data)
        stats = {k: len(v) for k, v in processed_data.items()}
        total_items = sum(stats.values())
        
        if total_items == 0:
            print("[WARNING] 今日未能获取到有效数据，停止生成。")
            return
            
        # 3. Generate 
        chapters = self._generate_chapters(processed_data)
        
        # 4. Render
        print("====== [Pipeline Step 4] Jinja 视图渲染与发布 ======")
        now = datetime.datetime.now(BEIJING_TZ)
        yesterday = now - datetime.timedelta(days=1)
        date_str = now.strftime('%Y-%m-%d')
        time_range = f"{yesterday.strftime('%Y年%m月%d日 %H:%M')} - {now.strftime('%Y年%m月%d日 %H:%M')}"
        current_time = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

        
        context = {
            "date_str": date_str,
            "time_range": time_range,
            "current_time": current_time,
            "total_items": total_items,
            "stats": stats,
            "reading_time": 0,
            "word_count": 0
        }
        context.update(chapters)
        
        # 预渲染一次计算字数和预计阅读时长
        temp_md = self.renderer.render("default.md.j2", context)
        word_count, reading_time = calculate_reading_stats(temp_md)
        context["word_count"] = word_count
        context["reading_time"] = reading_time
        
        final_md = self.renderer.render("default.md.j2", context)
        
        file_path = self.content_dir / f"{date_str}.md"
        self.content_dir.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_md)
            
        # 持久化保存去重状态
        self.dedup.save_state()
            
        print(f"[OK] 每日AI动态管线执行成功！文章已生成至: {file_path}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
