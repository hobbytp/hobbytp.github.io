#!/usr/bin/env python3
import sys
import os
import datetime
from pathlib import Path

# 添加项目根目录到 Python Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from scripts.daily_ai.fetchers.google_search import GoogleSearchFetcher
from scripts.daily_ai.fetchers.huggingface import HuggingFaceModelsFetcher, HuggingFacePapersFetcher
from scripts.daily_ai.fetchers.arxiv import ArxivFetcher
from scripts.daily_ai.fetchers.github_trending import GitHubTrendingFetcher
from scripts.daily_ai.fetchers.perplexity_fallback import PerplexityFallbackFetcher
from scripts.daily_ai.processors.deduplicator import Deduplicator
from scripts.daily_ai.processors.quality_scorer import QualityScorer
from scripts.daily_ai.generators.chapter_writer import ChapterWriter
from scripts.daily_ai.renderers.jinja_renderer import JinjaRenderer

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
        # Fetchers
        self.fetchers = {
            'focus_news': GoogleSearchFetcher(),
            'hf_models': HuggingFaceModelsFetcher(),
            'arxiv_papers': ArxivFetcher(),
            'hf_papers': HuggingFacePapersFetcher(),
            'github_projects': GitHubTrendingFetcher(),
            'perplexity_news': PerplexityFallbackFetcher()
        }
        
        # Processors
        self.dedup = Deduplicator()
        self.scorer = QualityScorer()
        
        # Generator & Renderer
        self.writer = ChapterWriter()
        self.renderer = JinjaRenderer()
        
        self.content_dir = project_root / "content" / "zh" / "daily_ai"
        
    def _fetch_all(self):
        print("====== [Pipeline Step 1] Fetching Data ======")
        data = {}
        for key, fetcher in self.fetchers.items():
            print(f"[INFO] 正在抓取: {fetcher.name} ...")
            try:
                 data[key] = fetcher.fetch()
            except Exception as e:
                 print(f"[ERROR] {fetcher.name} 抓取抛出异常: {e}")
                 data[key] = []
                 
        # 聚合 Papers: arXiv + HuggingFace Papers 合并为 arxiv_papers
        hf_papers = data.pop('hf_papers', [])
        data['arxiv_papers'] = data.get('arxiv_papers', []) + hf_papers
        return data
        
    def _process_data(self, data):
        print("====== [Pipeline Step 2] Processing Data ======")
        processed_data = {}
        for key, items in data.items():
             if not items:
                 processed_data[key] = []
                 continue
                 
             unique_items = self.dedup.process(items)
             scored_items = self.scorer.process(unique_items)
             
             # 取 Top K 丢给生成器
             top_k = 5
             if key == 'focus_news': top_k = 3
             
             processed_data[key] = scored_items[:top_k]
             print(f"[INFO] {key} - 清洗后保留 Top {len(processed_data[key])}")
             
        return processed_data
        
    def _generate_chapters(self, processed_data):
        print("====== [Pipeline Step 3] Generating Content via LLMs ======")
        chapters = {}
        for key, items in processed_data.items():
            if items:
                 content = self.writer.write_section(key, items)
                 chapters[f"{key}_content"] = content
            else:
                 chapters[f"{key}_content"] = ""
        
        # 生成编辑点评 (基于所有其他章节的成果)
        print("[INFO] 生成编辑点评...")
        summary_prompt = "请作为技术主编，一句话总结今日的最大看点，并点评产业趋势。不要加标题格式，直接输出正文。"
        chapters["editor_review_content"] = self.writer.ai.generate(summary_prompt)
        
        return chapters

    def run(self):
         # 1. Fetch
         raw_data = self._fetch_all()
         
         # 2. Process
         processed_data = self._process_data(raw_data)
         stats = {k: len(v) for k, v in processed_data.items()}
         total_items = sum(stats.values())
         
         # 3. Generate 
         chapters = self._generate_chapters(processed_data)
         
         # 4. Render
         print("====== [Pipeline Step 4] Rendering View ======")
         now = datetime.datetime.now()
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
             "reading_time": 0,    # Placeholder
             "word_count": 0       # Placeholder
         }
         context.update(chapters)
         
         # 预渲染一次算字数
         temp_md = self.renderer.render("default.md.j2", context)
         word_count, reading_time = calculate_reading_stats(temp_md)
         context["word_count"] = word_count
         context["reading_time"] = reading_time
         
         final_md = self.renderer.render("default.md.j2", context)
         
         file_path = self.content_dir / f"{date_str}.md"
         self.content_dir.mkdir(parents=True, exist_ok=True)
         with open(file_path, "w", encoding="utf-8") as f:
             f.write(final_md)
             
         print(f"[OK] 每日AI动态 v3 架构完成！文件生成至: {file_path}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
