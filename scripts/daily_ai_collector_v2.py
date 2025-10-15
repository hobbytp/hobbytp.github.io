#!/usr/bin/env python3
"""
每日AI动态收集脚本 V2.0 - 专业版
自动收集AI领域的最新动态，包括新模型、新框架、新应用等
新增功能：
- Perplexity API 集成（获取 AI 新闻和趋势）
- 缩短时间窗口至 24 小时（真正的每日动态）
- 数据去重功能
- 内容质量评分和排序
- 简化的分类体系
"""

import os
import json
import requests
import datetime
from typing import List, Dict, Any, Set
from pathlib import Path
import yaml
import hashlib
import re

# 尝试导入 Google Gemini SDK
try:
    import google.generativeai as genai
    USE_GOOGLE_SDK = True
    print("✅ google.generativeai 库导入成功")
except ImportError as e:
    USE_GOOGLE_SDK = False
    print(f"⚠️ google.generativeai 库导入失败: {e}")
    try:
        import openai
        print("✅ openai 库导入成功（回退模式）")
    except ImportError:
        print("ERROR: 既没有 google-generativeai 也没有 openai 库")
        openai = None

# 尝试导入 Perplexity SDK
try:
    from perplexity import Perplexity
    USE_PERPLEXITY = True
    print("✅ perplexity 库导入成功")
except ImportError as e:
    USE_PERPLEXITY = False
    print(f"⚠️ perplexity 库导入失败: {e}")
    print("   安装: pip install perplexityai")

class DailyAICollectorV2:
    def __init__(self):
        # 初始化 Gemini API
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            print("WARNING: GEMINI_API_KEY 未设置！")
            self.ai_client = None
            self.use_google_sdk = False
        else:
            print(f"GEMINI_API_KEY 已设置 (长度: {len(gemini_key)})")
            
            if USE_GOOGLE_SDK:
                try:
                    genai.configure(api_key=gemini_key)
                    self.ai_client = genai.GenerativeModel('gemini-2.5-flash')
                    self.use_google_sdk = True
                    print("✅ Google Gemini SDK 初始化成功 (模型: gemini-2.5-flash)")
                except Exception as e:
                    print(f"ERROR: Google SDK 初始化失败: {e}")
                    self.ai_client = None
                    self.use_google_sdk = False
            elif openai:
                try:
                    self.ai_client = openai.OpenAI(
                        api_key=gemini_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                    )
                    self.use_google_sdk = False
                    print("✅ OpenAI兼容客户端初始化成功")
                except Exception as e:
                    print(f"ERROR: OpenAI客户端初始化失败: {e}")
                    self.ai_client = None
                    self.use_google_sdk = False
            else:
                print("ERROR: 没有可用的 AI 客户端库")
                self.ai_client = None
                self.use_google_sdk = False

        # 初始化 Perplexity API
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        if USE_PERPLEXITY and self.perplexity_key:
            try:
                self.perplexity_client = Perplexity(api_key=self.perplexity_key)
                print(f"✅ Perplexity API 初始化成功 (key长度: {len(self.perplexity_key)})")
            except Exception as e:
                print(f"ERROR: Perplexity 初始化失败: {e}")
                self.perplexity_client = None
        else:
            self.perplexity_client = None
            if not USE_PERPLEXITY:
                print("⚠️ Perplexity SDK 未安装")
            elif not self.perplexity_key:
                print("⚠️ PERPLEXITY_API_KEY 未设置")

        self.github_token = os.getenv('GITHUB_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_API_KEY')
        
        print(f"GitHub Token: {'已设置' if self.github_token else '未设置'}")
        print(f"HuggingFace Token: {'已设置' if self.hf_token else '未设置'}")
        
        self.content_dir = Path("content/zh/daily_ai")
        self.content_dir.mkdir(exist_ok=True)
        
        # 用于去重的集合
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        
    def get_date_range(self, hours_back: int = 24) -> tuple:
        """获取时间范围（默认过去24小时）"""
        now = datetime.datetime.now()
        today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        start_time = today_8am - datetime.timedelta(hours=hours_back)
        return start_time, today_8am
    
    def load_history_items(self, days_back: int = 7) -> Set[str]:
        """加载最近N天的历史项目，用于去重"""
        history_urls = set()
        history_titles = set()
        
        now = datetime.datetime.now()
        for i in range(days_back):
            date = now - datetime.timedelta(days=i)
            file_path = self.content_dir / f"{date.strftime('%Y-%m-%d')}.md"
            
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # 提取 URL
                    urls = re.findall(r'https?://[^\s\)]+', content)
                    history_urls.update(urls)
                    # 提取标题（Markdown heading）
                    titles = re.findall(r'###\s+(.+)', content)
                    history_titles.update(titles)
                except Exception as e:
                    print(f"读取历史文件失败 {file_path}: {e}")
        
        print(f"加载了 {len(history_urls)} 个历史URL，{len(history_titles)} 个历史标题")
        return history_urls | history_titles
    
    def is_duplicate(self, item: Dict) -> bool:
        """检查项目是否重复"""
        # 检查 URL
        url = item.get('html_url') or item.get('link') or item.get('url', '')
        if url and url in self.seen_urls:
            return True
        if url:
            self.seen_urls.add(url)
        
        # 检查标题
        title = item.get('name') or item.get('title') or item.get('modelId', '')
        if title and title in self.seen_titles:
            return True
        if title:
            self.seen_titles.add(title)
        
        return False
    
    def calculate_quality_score(self, item: Dict, source: str) -> float:
        """计算内容质量分数（0-10分）"""
        score = 5.0  # 基础分
        
        if source == 'github':
            stars = item.get('stargazers_count', 0)
            score += min(stars / 200, 3.0)  # stars 权重（最多加3分）
            
            # 是否有详细描述
            desc_len = len(item.get('description', ''))
            if desc_len > 100:
                score += 1.0
            elif desc_len > 50:
                score += 0.5
            
            # 最近更新时间
            updated_at = item.get('updated_at', '')
            if updated_at:
                try:
                    update_time = datetime.datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
                    days_ago = (datetime.datetime.now() - update_time).days
                    if days_ago <= 1:
                        score += 1.0
                    elif days_ago <= 7:
                        score += 0.5
                except:
                    pass
        
        elif source == 'huggingface':
            downloads = item.get('downloads', 0)
            score += min(downloads / 1000, 2.0)  # downloads 权重
            
            # 是否有 pipeline_tag
            if item.get('pipeline_tag'):
                score += 0.5
        
        elif source == 'arxiv':
            # 作者数量
            authors = len(item.get('authors', []))
            score += min(authors / 5, 1.0)
            
            # 摘要长度
            summary_len = len(item.get('summary', ''))
            if 200 < summary_len < 2000:
                score += 1.0
            elif 100 < summary_len < 3000:
                score += 0.5
        
        elif source == 'perplexity':
            # Perplexity 结果通常质量较高
            score += 2.0
            
            # 检查是否有发布日期
            if item.get('date'):
                score += 0.5
        
        return min(score, 10.0)  # 最高10分
    
    def search_perplexity_ai_news(self) -> List[Dict]:
        """使用 Perplexity 搜索 AI 新闻和趋势"""
        if not self.perplexity_client:
            print("WARNING: Perplexity 客户端未初始化，跳过搜索")
            return []
        
        try:
            yesterday, today = self.get_date_range(hours_back=24)
            date_str = yesterday.strftime('%Y-%m-%d')
            
            # 多查询搜索：AI新闻、模型发布、工具发布
            queries = [
                f"latest AI news and breakthroughs since {date_str}",
                f"new AI models released since {date_str}",
                f"new AI tools and frameworks since {date_str}"
            ]
            
            print(f"使用 Perplexity 搜索: {queries}")
            
            search = self.perplexity_client.search.create(
                query=queries,
                max_results=5,
                max_tokens_per_page=1024
            )
            
            all_results = []
            query_types = ['news', 'models', 'tools']
            
            if hasattr(search, 'results'):
                # 处理多查询结果
                for query_idx, query_results in enumerate(search.results):
                    # 安全获取 query_type，超出索引则使用 'general'
                    query_type = query_types[query_idx] if query_idx < len(query_types) else 'general'
                    
                    if isinstance(query_results, list):
                        # query_results 是列表
                        for result in query_results:
                            item = {
                                'title': result.title if hasattr(result, 'title') else '',
                                'url': result.url if hasattr(result, 'url') else '',
                                'snippet': result.snippet if hasattr(result, 'snippet') else '',
                                'date': result.date if hasattr(result, 'date') else '',
                                'query_type': query_type
                            }
                            all_results.append(item)
                    else:
                        # query_results 是单个结果对象
                        item = {
                            'title': query_results.title if hasattr(query_results, 'title') else '',
                            'url': query_results.url if hasattr(query_results, 'url') else '',
                            'snippet': query_results.snippet if hasattr(query_results, 'snippet') else '',
                            'date': query_results.date if hasattr(query_results, 'date') else '',
                            'query_type': query_type
                        }
                        all_results.append(item)
            
            print(f"Perplexity 找到 {len(all_results)} 条结果")
            return all_results
            
        except Exception as e:
            print(f"Perplexity 搜索错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print("完整错误堆栈:")
            traceback.print_exc()
            print("提示: Perplexity API 调用失败，将跳过新闻搜索")
            return []
    
    def search_github_trending(self) -> List[Dict]:
        """搜索GitHub热门AI项目（缩短时间窗口至24小时）"""
        if not self.github_token:
            print("WARNING: GitHub token未设置，跳过GitHub搜索")
            return []
            
        headers = {'Authorization': f'Bearer {self.github_token}'}
        url = 'https://api.github.com/search/repositories'
        
        # 缩短为过去24小时
        yesterday, today = self.get_date_range(hours_back=24)
        date_str = yesterday.strftime('%Y-%m-%d')
        
        params = {
            'q': f'AI machine-learning deep-learning created:>{date_str} language:python',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 30  # 增加获取数量，后续会过滤
        }
        
        try:
            print(f"搜索GitHub项目: created:>{date_str}")
            response = requests.get(url, headers=headers, params=params)
            print(f"GitHub API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                # 去重和质量评分
                filtered_items = []
                for item in items:
                    if not self.is_duplicate(item):
                        item['quality_score'] = self.calculate_quality_score(item, 'github')
                        filtered_items.append(item)
                
                # 按质量分数排序
                filtered_items.sort(key=lambda x: x['quality_score'], reverse=True)
                
                print(f"GitHub: 原始 {len(items)} 个，去重后 {len(filtered_items)} 个")
                return filtered_items[:10]  # 返回前10个高质量项目
            else:
                print(f"GitHub API错误: {response.status_code}")
        except Exception as e:
            print(f"GitHub搜索错误: {e}")
            
        return []
    
    def search_huggingface_models(self) -> List[Dict]:
        """搜索Hugging Face新模型（缩短时间窗口至24小时）"""
        if not self.hf_token:
            print("WARNING: Hugging Face token未设置，跳过HF搜索")
            return []
            
        headers = {'Authorization': f'Bearer {self.hf_token}'}
        url = 'https://huggingface.co/api/models'
        
        yesterday, today = self.get_date_range(hours_back=24)
        date_str = yesterday.strftime('%Y-%m-%d')
        
        params = {
            'filter': 'pytorch',
            'sort': 'createdAt',
            'direction': -1,
            'limit': 50
        }
        
        try:
            print(f"搜索Hugging Face模型")
            response = requests.get(url, headers=headers, params=params)
            print(f"HF API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                models = response.json()
                
                # 过滤最近24小时的模型
                filtered_models = []
                for model in models:
                    created_at = model.get('createdAt', '')
                    if created_at and created_at >= date_str:
                        if not self.is_duplicate(model):
                            model['quality_score'] = self.calculate_quality_score(model, 'huggingface')
                            filtered_models.append(model)
                
                filtered_models.sort(key=lambda x: x['quality_score'], reverse=True)
                
                print(f"HF: 原始 {len(models)} 个，筛选后 {len(filtered_models)} 个")
                return filtered_models[:5]
            else:
                print(f"HF API错误: {response.status_code}")
        except Exception as e:
            print(f"Hugging Face搜索错误: {e}")
            
        return []
    
    def search_arxiv_papers(self) -> List[Dict]:
        """搜索ArXiv最新AI论文（缩短时间窗口至24小时）"""
        url = 'http://export.arxiv.org/api/query'
        
        yesterday, today = self.get_date_range(hours_back=24)
        start_date = yesterday.strftime('%Y%m%d')
        end_date = today.strftime('%Y%m%d')
        
        params = {
            'search_query': f'cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[{start_date}0000 TO {end_date}2359]',
            'start': 0,
            'max_results': 30,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            print(f"搜索ArXiv论文: {start_date} 到 {end_date}")
            response = requests.get(url, params=params)
            print(f"ArXiv API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                    
                    if title_elem is not None and summary_elem is not None and link_elem is not None:
                        paper = {
                            'title': title_elem.text.strip() if title_elem.text else '无标题',
                            'authors': [author.find('{http://www.w3.org/2005/Atom}name').text 
                                      for author in entry.findall('{http://www.w3.org/2005/Atom}author')
                                      if author.find('{http://www.w3.org/2005/Atom}name') is not None],
                            'summary': summary_elem.text.strip() if summary_elem.text else '无摘要',
                            'link': link_elem.text.strip() if link_elem.text else ''
                        }
                        
                        if not self.is_duplicate(paper):
                            paper['quality_score'] = self.calculate_quality_score(paper, 'arxiv')
                            papers.append(paper)
                
                papers.sort(key=lambda x: x['quality_score'], reverse=True)
                
                print(f"ArXiv: 找到 {len(papers)} 篇论文（已去重和排序）")
                return papers[:10]
            else:
                print(f"ArXiv API错误: {response.status_code}")
        except Exception as e:
            print(f"ArXiv搜索错误: {e}")
            
        return []
    
    def generate_ai_summary(self, collected_data: Dict) -> str:
        """使用AI生成每日动态摘要（新分类体系）"""
        github_count = len(collected_data.get('github_projects', []))
        hf_count = len(collected_data.get('hf_models', []))
        arxiv_count = len(collected_data.get('arxiv_papers', []))
        perplexity_count = len(collected_data.get('perplexity_news', []))
        
        print(f"数据收集统计:")
        print(f"   Perplexity新闻: {perplexity_count}")
        print(f"   GitHub项目: {github_count}")
        print(f"   HF模型: {hf_count}")
        print(f"   ArXiv论文: {arxiv_count}")
        
        total_items = github_count + hf_count + arxiv_count + perplexity_count
        
        if total_items == 0:
            print("WARNING: 没有收集到任何数据")
            return self.generate_fallback_summary(collected_data)
        
        if not self.ai_client:
            print("WARNING: AI客户端未初始化")
            return self.generate_fallback_summary(collected_data)
        
        prompt = f"""基于以下收集的AI技术动态数据，生成一份专业的每日AI动态报告。

收集到的数据：
{json.dumps(collected_data, ensure_ascii=False, indent=2)}

请按照以下**新的分类体系**生成内容：

## 📰 今日焦点
精选2-3条最重要的AI新闻/发布，每条包含：
- 🔥 热度标识（根据重要性：🔥🔥🔥 高 / 🔥🔥 中 / 🔥 普通）
- 标题和一句话总结
- 为什么重要
- 链接

## 🧠 模型与算法
包含新发布的模型（大语言模型、多模态模型、专业领域模型等），每项包含：
- 模型名称和链接
- 核心特性
- 性能数据（如有）
- 适用场景

## 🛠️ 工具与框架
包含开发框架、训练工具、部署方案，每项包含：
- 工具名称和链接
- 主要功能
- Stars 数量（GitHub项目）
- 推荐指数（⭐⭐⭐⭐⭐）

## 📱 应用与产品
包含商业产品、开源应用、Demo原型，每项包含：
- 应用名称和链接
- 功能描述
- 技术栈
- 实用性评估

## 📚 学术前沿
包含最新论文，每项包含：
- 论文标题和链接
- 作者
- 核心贡献
- 创新点

## 💡 编辑点评
根据今日内容，提供：
- 技术趋势观察（2-3条）
- 值得关注的方向
- 行业影响分析

**要求**：
1. 内容要准确、专业、有价值
2. 突出重点，避免信息堆砌
3. 使用 Emoji 增加可读性
4. 如果某个分类数据不足，可以合并到其他分类或简要说明
5. 使用中文，语言简洁专业
6. 为每个重要项目添加质量评价（基于 stars、下载量、作者等）
"""
        
        try:
            print("开始AI生成摘要（新格式）...")
            
            if self.use_google_sdk:
                response = self.ai_client.generate_content(prompt)
                content = response.text if hasattr(response, 'text') else None
            else:
                response = self.ai_client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=3000,
                    temperature=0.7
                )
                content = response.choices[0].message.content if response.choices else None
            
            if not content or content.strip() == "":
                print("WARNING: AI返回了空内容")
                return self.generate_fallback_summary(collected_data)
            
            print(f"AI摘要生成完成（长度: {len(content)}）")
            return content
            
        except Exception as e:
            print(f"AI生成摘要错误: {e}")
            import traceback
            traceback.print_exc()
            return self.generate_fallback_summary(collected_data)
    
    def generate_fallback_summary(self, collected_data: Dict) -> str:
        """生成备用摘要（新格式）"""
        print("使用 fallback 摘要生成器（新格式）...")
        summary = ""
        
        # 今日焦点
        summary += "## 📰 今日焦点\n\n"
        focus_items = []
        
        # 从 Perplexity 结果中选择焦点
        perplexity_news = collected_data.get('perplexity_news', [])
        if perplexity_news:
            for item in perplexity_news[:2]:
                title = item.get('title', '未知标题')
                url = item.get('url', '')
                snippet = item.get('snippet', '')[:150]
                summary += f"### 🔥🔥 [{title}]({url})\n"
                summary += f"- **简介**: {snippet}...\n"
                summary += f"- **来源**: Perplexity AI 新闻搜索\n\n"
                focus_items.append(title)
        
        # 从 GitHub 高质量项目中选择
        github_projects = sorted(
            collected_data.get('github_projects', []),
            key=lambda x: x.get('quality_score', 0),
            reverse=True
        )
        if github_projects and len(focus_items) < 3:
            item = github_projects[0]
            name = item.get('name', '未知项目')
            desc = item.get('description', '无描述')
            url = item.get('html_url', '')
            stars = item.get('stargazers_count', 0)
            summary += f"### 🔥 [{name}]({url})\n"
            summary += f"- **描述**: {desc}\n"
            summary += f"- **热度**: ⭐ {stars} stars\n"
            summary += f"- **推荐理由**: 高质量开源项目，值得关注\n\n"
        
        if not focus_items and not github_projects:
            summary += "暂无特别突出的焦点新闻。\n\n"
        
        # 模型与算法
        summary += "## 🧠 模型与算法\n\n"
        hf_models = collected_data.get('hf_models', [])
        if hf_models:
            for model in hf_models[:3]:
                model_id = model.get('modelId', '未知模型')
                pipeline = model.get('pipeline_tag', '未知类型')
                downloads = model.get('downloads', 0)
                score = model.get('quality_score', 5.0)
                stars = '⭐' * int(score / 2)
                summary += f"### {model_id}\n"
                summary += f"- **类型**: {pipeline}\n"
                summary += f"- **下载量**: {downloads:,}\n"
                summary += f"- **评分**: {stars} ({score:.1f}/10)\n"
                summary += f"- **链接**: https://huggingface.co/{model_id}\n\n"
        else:
            summary += "今日暂无新模型发布。\n\n"
        
        # 工具与框架
        summary += "## 🛠️ 工具与框架\n\n"
        if github_projects:
            for project in github_projects[:5]:
                name = project.get('name', '未知项目')
                desc = project.get('description', '无描述')
                url = project.get('html_url', '')
                stars = project.get('stargazers_count', 0)
                score = project.get('quality_score', 5.0)
                rating = '⭐' * min(5, int(score / 2))
                summary += f"### [{name}]({url})\n"
                summary += f"- **功能**: {desc}\n"
                summary += f"- **Stars**: {stars:,}\n"
                summary += f"- **推荐指数**: {rating}\n\n"
        else:
            summary += "今日暂无新工具框架发布。\n\n"
        
        # 学术前沿
        summary += "## 📚 学术前沿\n\n"
        arxiv_papers = collected_data.get('arxiv_papers', [])
        if arxiv_papers:
            for paper in arxiv_papers[:5]:
                title = paper.get('title', '未知标题')
                authors = ', '.join(paper.get('authors', [])[:3])
                if len(paper.get('authors', [])) > 3:
                    authors += ' 等'
                link = paper.get('link', '')
                abstract = paper.get('summary', '无摘要')[:200]
                score = paper.get('quality_score', 5.0)
                summary += f"### [{title}]({link})\n"
                summary += f"- **作者**: {authors}\n"
                summary += f"- **摘要**: {abstract}...\n"
                summary += f"- **质量评分**: {score:.1f}/10\n\n"
        else:
            summary += "今日暂无重要论文发布。\n\n"
        
        # 编辑点评
        summary += "## 💡 编辑点评\n\n"
        total_items = len(github_projects) + len(hf_models) + len(arxiv_papers) + len(perplexity_news)
        if total_items > 0:
            summary += f"今日共收集到 {total_items} 条AI动态，其中：\n"
            if perplexity_news:
                summary += f"- 📰 AI新闻: {len(perplexity_news)} 条\n"
            if github_projects:
                summary += f"- 🛠️ GitHub项目: {len(github_projects)} 个\n"
            if hf_models:
                summary += f"- 🧠 新模型: {len(hf_models)} 个\n"
            if arxiv_papers:
                summary += f"- 📚 学术论文: {len(arxiv_papers)} 篇\n"
            summary += "\n内容质量均经过自动评分和排序，优先展示高质量项目。\n"
        else:
            summary += "今日数据收集遇到问题，建议稍后重试或手动检查数据源。\n\n"
            summary += "可能原因：API限流、网络问题、或确实无新内容发布。\n"
        
        return summary
    
    def create_daily_content(self) -> str:
        """创建每日内容文件"""
        yesterday, today = self.get_date_range(hours_back=24)
        date_str = today.strftime('%Y-%m-%d')
        time_range = f"{yesterday.strftime('%Y年%m月%d日 %H:%M')} - {today.strftime('%Y年%m月%d日 %H:%M')}"
        
        print(f"时间范围: {time_range}")
        
        # 加载历史数据用于去重
        self.seen_urls = self.load_history_items(days_back=7)
        self.seen_titles = set()  # 重置标题集合
        
        # 收集数据
        print("=" * 60)
        print("开始收集数据...")
        print("=" * 60)
        
        collected_data = {
            'perplexity_news': self.search_perplexity_ai_news(),
            'github_projects': self.search_github_trending(),
            'hf_models': self.search_huggingface_models(),
            'arxiv_papers': self.search_arxiv_papers()
        }
        
        print("=" * 60)
        print("数据收集完成，开始生成摘要...")
        print("=" * 60)
        
        # 生成AI摘要
        ai_summary = self.generate_ai_summary(collected_data)
        
        # 统计信息
        total_items = sum(len(v) for v in collected_data.values())
        
        # 创建Markdown内容
        content = f"""---
title: "每日AI动态 - {date_str}"
date: {today.isoformat()}+08:00
draft: false
categories: ["daily_ai"]
tags: ["AI动态", "技术更新", "行业趋势"]
description: "{date_str}的AI技术动态汇总"
readingTime: "{max(3, total_items // 3)} min"
totalItems: {total_items}
---

# 每日AI动态 - {date_str}

> 📅 **时间范围**: {time_range} (北京时间)  
> 📊 **内容统计**: 共 {total_items} 条动态  
> ⏱️ **预计阅读**: {max(3, total_items // 3)} 分钟

---

{ai_summary}

---

## 📊 数据来源

本报告数据来源于：
- 🔍 **Perplexity AI**: 实时AI新闻搜索
- 💻 **GitHub**: AI相关开源项目
- 🤗 **Hugging Face**: 新模型发布
- 📄 **arXiv**: 最新学术论文

所有内容经过**质量评分**、**去重**和**智能排序**，确保信息的价值和时效性。

---

> 💡 **提示**: 本内容由 AI 自动生成，每日北京时间 08:00 更新。  
> 如有遗漏或错误，欢迎通过 [Issues](https://github.com/hobbytp/hobbytp.github.io/issues) 反馈。
"""
        
        return content
    
    def save_daily_content(self):
        """保存每日内容"""
        content = self.create_daily_content()
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        file_path = self.content_dir / f"{date_str}.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("=" * 60)
        print(f"✅ 每日AI动态已保存到: {file_path}")
        print("=" * 60)
        return file_path

def main():
    """主函数"""
    print("=" * 60)
    print("每日AI动态收集器 V2.0 - 专业版")
    print("=" * 60)
    
    collector = DailyAICollectorV2()
    file_path = collector.save_daily_content()
    
    print(f"\n✅ 收集完成: {file_path}")
    print("\n新功能：")
    print("  ✅ Perplexity AI 新闻搜索")
    print("  ✅ 24小时时间窗口（真正的每日动态）")
    print("  ✅ 智能去重")
    print("  ✅ 内容质量评分")
    print("  ✅ 新的分类体系")
    print("  ✅ 改进的展现格式")

if __name__ == "__main__":
    main()
