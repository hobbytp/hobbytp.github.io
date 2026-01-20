#!/usr/bin/env python3
"""
每日AI动态收集脚本 V2.1 - 专业版
自动收集AI领域的最新动态，包括新模型、新框架、新应用等

V2.1 新增功能：
- 分章节生成（Map-Reduce模式）：每个章节独立生成，避免输出截断
- HuggingFace Trending 算法：基于增长率而非绝对热度
- HuggingFace Daily Papers：新增论文数据源
- 清晰的 ERROR 日志：章节生成失败时明确记录
- 改进的错误处理：GitHub 401 错误优雅处理

V2.0 功能：
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
import sys
import warnings
from dotenv import load_dotenv

# 尝试导入 huggingface_hub
USE_HF_HUB = False
try:
    from huggingface_hub import HfApi, list_models
    USE_HF_HUB = True
    print("[OK] huggingface_hub 库导入成功")
except ImportError:
    print("WARNING: huggingface_hub 库未安装，将使用 HTTP API")

# 加载 .env 文件
load_dotenv()

# 忽略 FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# 添加脚本目录到路径以便导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from update_word_count import calculate_reading_stats
except ImportError:
    # Fallback implementation if import fails
    def calculate_reading_stats(text, reading_speed=400):
        # Fallback: count Chinese characters using regex (same as update_word_count.py)
        # \u4e00-\u9fa5: Chinese chars
        # \u3000-\u303f: CJK symbols and punctuation
        # \uff00-\uffef: Fullwidth symbols
        word_count = len(re.findall(r'[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]', text))
        # If no Chinese chars found (e.g. English text), fall back to simple length or word count
        if word_count == 0 and len(text) > 0:
             word_count = len(text.split())
             
        reading_time = max(1, (word_count + reading_speed - 1) // reading_speed)
        return word_count, reading_time

# 尝试导入 Google GenAI SDK (New)
try:
    from google import genai
    USE_GOOGLE_SDK = True
    print("[OK] google-genai 库导入成功")
except ImportError as e:
    USE_GOOGLE_SDK = False
    print(f"[WARNING] google-genai 库导入失败: {e}")
    try:
        import openai
        print("[OK] openai 库导入成功（回退模式）")
    except ImportError:
        print("ERROR: 既没有 google-genai 也没有 openai 库")
        openai = None

# 尝试导入 Perplexity SDK
try:
    from perplexity import Perplexity
    USE_PERPLEXITY = True
    print("[OK] perplexity 库导入成功")
except ImportError as e:
    USE_PERPLEXITY = False
    print(f"[WARNING] perplexity 库导入失败: {e}")
    print("   安装: pip install perplexityai")

# 尝试导入 ai_news_collector_lib
try:
    from ai_news_collector_lib import (
        AdvancedAINewsCollector,
        AdvancedSearchConfig,
        ReportGenerator,
    )
    USE_AI_NEWS_LIB = True
    print("[OK] ai_news_collector_lib 库导入成功")
except ImportError as e:
    try:
        from ai_news_collector import (
            AdvancedAINewsCollector, 
            AdvancedSearchConfig,
            ReportGenerator,
        )
        USE_AI_NEWS_LIB = True
        print("[OK] ai_news_collector 库导入成功（回退模式）")
    except ImportError as e2:
        USE_AI_NEWS_LIB = False
        print(f"[WARNING] ai_news_collector_lib 库导入失败: {e}")
        print("   安装: pip install ai-news-collector-lib[advanced]")

class DailyAICollectorV2_1:
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
                    # 新 SDK 初始化
                    self.ai_client = genai.Client(api_key=gemini_key)
                    self.use_google_sdk = True
                    print("[OK] Google GenAI SDK 初始化成功")
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
                    print("[OK] OpenAI兼容客户端初始化成功")
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
                self.perplexity_client = Perplexity(
                    api_key=self.perplexity_key,
                    timeout=60.0
                )
                print(f"[OK] Perplexity API 初始化成功 (key长度: {len(self.perplexity_key)})")
            except Exception as e:
                print(f"ERROR: Perplexity 初始化失败: {e}")
                self.perplexity_client = None
        else:
            self.perplexity_client = None
            if not USE_PERPLEXITY:
                print("[WARNING] Perplexity SDK 未安装")
            elif not self.perplexity_key:
                print("[WARNING] PERPLEXITY_API_KEY 未设置")

        self.github_token = os.getenv('GITHUB_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_API_KEY')
        
        # 检查 ai_news_collector_lib 需要的环境变量
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.google_search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.brave_search_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        self.metasosearch_api_key = os.getenv('METASOSEARCH_API_KEY')
        
        print(f"GitHub Token: {'已设置' if self.github_token else '未设置'}")
        print(f"HuggingFace Token: {'已设置' if self.hf_token else '未设置'}")
        print(f"News API Key: {'已设置' if self.news_api_key else '未设置'}")
        print(f"Tavily API Key: {'已设置' if self.tavily_api_key else '未设置'}")
        print(f"Google Search API Key: {'已设置' if self.google_search_api_key else '未设置'}")
        print(f"Google Search Engine ID: {'已设置' if self.google_search_engine_id else '未设置'}")
        print(f"Serper API Key: {'已设置' if self.serper_api_key else '未设置'}")
        print(f"Brave Search API Key: {'已设置' if self.brave_search_api_key else '未设置'}")
        print(f"Metasosearch API Key: {'已设置' if self.metasosearch_api_key else '未设置'}")
        
        self.content_dir = Path("content/zh/daily_ai")
        self.content_dir.mkdir(exist_ok=True)
        
        # 用于去重的集合
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        
    def get_date_range(self, hours_back: int = 24) -> tuple:
        """获取时间范围（默认过去24小时）"""
        now = datetime.datetime.now(datetime.timezone.utc)
        today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        start_time = today_8am - datetime.timedelta(hours=hours_back)
        return start_time, today_8am
    
    def load_history_items(self, days_back: int = 7) -> Set[str]:
        """加载最近N天的历史项目，用于去重"""
        history_urls = set()
        history_titles = set()
        
        now = datetime.datetime.now(datetime.timezone.utc)
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
    
    def is_within_time_range(self, item: Dict, source: str) -> bool:
        """检查项目是否在时间范围内"""
        yesterday, today = self.get_date_range(hours_back=24)
        
        if source == 'github':
            created_at = item.get('created_at', '')
            if created_at:
                try:
                    create_time = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                    return create_time >= yesterday
                except ValueError:
                    return False
        
        elif source == 'huggingface':
            created_at = item.get('createdAt', '')
            if created_at:
                try:
                    create_time = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    return create_time >= yesterday
                except (ValueError, TypeError):
                    return False
        
        elif source == 'arxiv':
            # ArXiv 的时间检查在搜索参数中已经处理
            return True
        
        elif source == 'ai_news_lib' or source == 'google_search':
            published_date = item.get('published_date', '')
            if published_date:
                try:
                    # 处理可能的时间格式
                    if 'T' in published_date:
                        pub_time = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    else:
                        # 尝试多种日期格式
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S']:
                            try:
                                pub_time = datetime.datetime.strptime(published_date, fmt)
                                break
                            except:
                                continue
                        else:
                            # 如果所有格式都失败
                            return False
                    
                    # 确保时区一致性
                    if pub_time.tzinfo is None:
                        # 假设为本地时间或UTC，这里统一先不带时区比较或设为UTC? 
                        # 简单起见，如果无时区，跟 removed tz 的 yesterday 比较
                        # 或者给 pub_time 加上 utc
                        pub_time = pub_time.replace(tzinfo=datetime.timezone.utc)
                    
                    return pub_time >= yesterday
                except (ValueError, TypeError):
                    return False
        
        return True  # 如果无法确定时间，默认通过
    
    def calculate_quality_score(self, item: Dict, source: str) -> float:
        """计算内容质量分数（0-10分）"""
        score = 5.0  # 基础分
        
        if source == 'github':
            stars = item.get('stargazers_count', 0)
            score += min(stars / 150, 4.0)  # 提高 stars 权重（最多加4分）
            
            # 是否有详细描述
            desc_len = len(item.get('description', ''))
            if desc_len > 100:
                score += 1.5  # 提高描述权重
            elif desc_len > 50:
                score += 1.0
            
            # 最近更新时间
            updated_at = item.get('updated_at', '')
            if updated_at:
                try:
                    update_time = datetime.datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
                    days_ago = (datetime.datetime.now() - update_time).days
                    if days_ago <= 1:
                        score += 1.5  # 提高时效性权重
                    elif days_ago <= 7:
                        score += 1.0
                except (ValueError, TypeError):
                    pass
        
        elif source == 'huggingface':
            downloads = item.get('downloads', 0)
            score += min(downloads / 500, 3.0)  # 提高 downloads 权重（最多加3分）
            
            # 是否有 pipeline_tag
            if item.get('pipeline_tag'):
                score += 1.0  # 提高标签权重
        
        elif source == 'arxiv':
            # 作者数量
            authors = len(item.get('authors', []))
            score += min(authors / 3, 1.5)  # 提高作者权重
            
            # 摘要长度
            summary_len = len(item.get('summary', ''))
            if 200 < summary_len < 2000:
                score += 1.5  # 提高摘要质量权重
            elif 100 < summary_len < 3000:
                score += 1.0
        
        elif source == 'perplexity':
            # Perplexity 结果通常质量较高
            score += 2.0
            
            # 检查是否有发布日期
            if item.get('date'):
                score += 0.5
        
        elif source == 'ai_news_lib':
            # ai_news_collector_lib 结果质量较高（多源聚合）
            score += 2.5
            
            # 检查关键词数量
            keywords = item.get('keywords', [])
            if len(keywords) > 3:
                score += 1.0
            elif len(keywords) > 0:
                score += 0.5
                
            # 检查发布日期
            if item.get('published_date'):
                score += 0.5
        
        elif source == 'google_focus':
            # Google Search 今日焦点，质量通常较高
            score += 2.5
            
            # 检查标题长度和内容丰富度
            title_len = len(item.get('title', ''))
            snippet_len = len(item.get('snippet', ''))
            
            if title_len > 20 and snippet_len > 100:
                score += 1.5
            elif title_len > 10 and snippet_len > 50:
                score += 1.0
            
            # 检查是否有发布时间
            if item.get('published_date'):
                score += 1.0
        
        elif source == 'applications':
            # 应用与产品，多源并行搜索
            score += 2.0
            
            # 检查关键词
            keywords = item.get('keywords', [])
            if len(keywords) > 3:
                score += 1.5
            elif len(keywords) > 0:
                score += 0.5
            
            # 检查内容丰富度
            snippet_len = len(item.get('snippet', ''))
            if snippet_len > 150:
                score += 1.0
            elif snippet_len > 80:
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
            today_str = today.strftime('%Y-%m-%d')
            
            # 多查询搜索：最近24小时的 AI 新闻（使用更精确的日期过滤）
            # 添加当前年份/日期到查询中，增强相关性，并明确时区
            # 使用北京时间 (UTC+8) 来确保日期边界清晰
            timezone_context = "Beijing time UTC+8"
            queries = [
                f"Most important AI news and events on {today_str} ({timezone_context})",
                f"AI breakthroughs and product launches from {yesterday.strftime('%Y-%m-%d')} to {today_str} ({timezone_context})",
                f"Major AI company announcements on {today_str} ({timezone_context})"
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

    def search_ai_news_lib(self) -> List[Dict]:
        """使用 ai_news_collector_lib 搜索多源 AI 新闻"""
        if not USE_AI_NEWS_LIB:
            print("WARNING: ai_news_collector_lib 未导入，跳过搜索")
            return []
        
        try:
            yesterday, today = self.get_date_range(hours_back=24)
            
            # 构建搜索配置 - 启用您配置的所有API源
            search_config = AdvancedSearchConfig(
                # 基础源
                enable_hackernews=True,
                enable_arxiv=True,
                enable_duckduckgo=True,
                enable_rss_feeds=True,
                
                # 您配置的API源
                enable_newsapi=True,        # NEWS_API_KEY
                enable_tavily=True,         # TAVILY_API_KEY  
                enable_google_search=True,  # GOOGLE_SEARCH_API_KEY
                enable_serper=True,         # SERPER_API_KEY
                enable_brave_search=True,   # BRAVE_SEARCH_API_KEY
                enable_metasota_search=True, # METASOSEARCH_API_KEY
                
                # 搜索参数 - 严格限制时间范围
                max_articles_per_source=3,
                days_back=0,  # 改为0，只搜索今天的内容
                similarity_threshold=0.85,
                
                # 高级功能
                enable_content_extraction=False,  # 减少处理时间
                enable_keyword_extraction=True,
                cache_results=False,  # 禁用缓存，避免旧信息重复使用
            )
            
            # 创建收集器
            collector = AdvancedAINewsCollector(search_config)
            
            # 定义搜索主题（聚焦24小时内的AI动态）
            # 在查询中加入明确的日期，帮助搜索引擎定位
            date_query_suffix = f" {today.strftime('%Y-%m-%d')}"
            topics = [
                f"latest AI model releases{date_query_suffix}",
                f"new AI tools and frameworks launched{date_query_suffix}",
                f"AI research breakthroughs and papers{date_query_suffix}",
                f"AI company news and product updates{date_query_suffix}"
            ]
            
            print(f"使用 ai_news_collector_lib 搜索 AI 新闻...")
            
            # 异步收集（如果支持批量主题）
            import asyncio
            
            async def collect_async():
                if hasattr(collector, 'collect_multiple_topics'):
                    return await collector.collect_multiple_topics(topics)
                else:
                    # 兼容回退：逐主题收集
                    results = []
                    for topic in topics:
                        if hasattr(collector, 'collect_news_advanced'):
                            result = await collector.collect_news_advanced(topic)
                            results.append(result)
                    
                    # 合并结果
                    all_articles = []
                    for r in results:
                        all_articles.extend(r.get('articles', []))
                    return {"articles": all_articles, "unique_articles": len(all_articles)}
            
            # 运行异步收集
            result = asyncio.run(collect_async())
            articles = result.get('articles', [])
            
            print(f"ai_news_collector_lib 找到 {len(articles)} 条结果")
            print(f"开始时间过滤，目标时间范围: {yesterday.strftime('%Y-%m-%d %H:%M')} 到 {today.strftime('%Y-%m-%d %H:%M')}")
            
            # 转换为统一格式并严格过滤时间
            formatted_results = []
            for article in articles:
                # 检查发布时间 - ai_news_collector_lib使用'published'字段
                published_date = article.get('published', '') or article.get('published_date', '')
                
                # 如果没有发布时间，直接跳过
                if not published_date or published_date == '':
                    print(f"跳过无发布时间文章: {article.get('title', '')[:50]}...")
                    continue
                
                try:
                    # 解析发布时间
                    if 'T' in published_date:
                        pub_time = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    else:
                        pub_time = datetime.datetime.strptime(published_date, '%Y-%m-%d')
                    
                    # 确保时区一致性 - 如果pub_time没有时区信息，假设为UTC
                    if pub_time.tzinfo is None:
                        pub_time = pub_time.replace(tzinfo=datetime.timezone.utc)
                    
                    # 检查发布时间是否在合理范围内（不能是未来时间）
                    now = datetime.datetime.now(datetime.timezone.utc)
                    if pub_time > now:
                        print(f"跳过未来时间文章: {article.get('title', '')[:50]}... (发布时间: {published_date})")
                        continue
                    
                    # 额外检查：如果发布时间超过7天，也跳过（防止极端情况）
                    if pub_time < now - datetime.timedelta(days=7):
                        print(f"过滤掉过旧文章: {article.get('title', '')[:50]}... (发布时间: {published_date})")
                        continue
                    
                    # 检查是否在24小时内
                    if pub_time < yesterday:
                        print(f"过滤掉过期文章: {article.get('title', '')[:50]}... (发布时间: {published_date})")
                        continue
                        
                except Exception as e:
                    print(f"时间解析错误: {published_date}, 错误: {e}")
                    # 如果时间解析失败，跳过该文章
                    continue
                
                item = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'snippet': article.get('description', '')[:300],
                    'source': article.get('source', 'ai_news_lib'),
                    'published_date': published_date,
                    'keywords': article.get('keywords', [])
                }
                formatted_results.append(item)
            
            print(f"ai_news_collector_lib 时间过滤后剩余 {len(formatted_results)} 条结果")
            return formatted_results
            
        except Exception as e:
            print(f"ai_news_collector_lib 搜索错误: {e}")
            import traceback
            traceback.print_exc()
            print("提示: ai_news_collector_lib 调用失败，将跳过此数据源")
            return []
    
    def search_focus_news(self) -> List[Dict]:
        """使用 Google Search 搜索大模型厂商相关新闻（今日焦点）"""
        if not self.google_search_api_key or not self.google_search_engine_id:
            print("WARNING: Google Search API 未配置，跳过今日焦点搜索")
            return []
        
        try:
            yesterday, today = self.get_date_range(hours_back=24)
            
            # 定义大模型厂商关键词
            companies = [
                "OpenAI", "Google Gemini", "Anthropic Claude", 
                "xAI Grok", "Meta Llama", "Mistral", "Microsoft","Apple","Amazon",
                "Qwen", "通义千问","DeepSeek", "seedream","字节跳动","GLM", "智谱", "Kimi", "月之暗面"
            ]
            
            # 构建搜索查询
            query = f"({' OR '.join(companies)}) AND (AI OR 大模型 OR 发布 OR release OR announcement OR 更新) after:{yesterday.strftime('%Y-%m-%d')}"
            
            print(f"使用 Google Search 搜索今日焦点: {query[:100]}...")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_search_api_key,
                'cx': self.google_search_engine_id,
                'q': query,
                'num': 10,  # 最多返回10条
                'dateRestrict': 'd1',  # 过去1天
                'sort': 'date'  # 按日期排序
            }
            
            response = requests.get(url, params=params, timeout=30)
            print(f"Google Search API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                formatted_results = []
                for item in items:
                    news_item = {
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', '')[:300],
                        'source': 'google_search',
                        'published_date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', ''),
                    }
                    
                    # 去重检查
                    if not self.is_duplicate(news_item):
                        # 严格的时间检查
                        if self.is_within_time_range(news_item, 'google_search'):
                            news_item['quality_score'] = self.calculate_quality_score(news_item, 'google_focus')
                            formatted_results.append(news_item)
                        else:
                            print(f"过滤掉过旧的焦点新闻: {news_item.get('title', '')} ({news_item.get('published_date', '无日期')})")
                
                # 按质量评分排序
                formatted_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                
                print(f"Google Search 今日焦点找到 {len(formatted_results)} 条结果")
                return formatted_results[:5]  # 返回前5条高质量新闻
            else:
                print(f"Google Search API错误: {response.status_code}")
                if response.status_code == 429:
                    print("提示: API配额已用完，请稍后再试")
                    
        except Exception as e:
            print(f"Google Search 搜索错误: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    def search_applications(self) -> List[Dict]:
        """使用多源并行搜索AI应用与产品（应用与产品章节）"""
        if not USE_AI_NEWS_LIB:
            print("WARNING: ai_news_collector_lib 未导入，跳过应用搜索")
            return []
        
        try:
            yesterday, today = self.get_date_range(hours_back=24)
            
            # 构建搜索配置 - 仅启用指定的API源（针对应用与产品）
            search_config = AdvancedSearchConfig(
                # 禁用基础源
                enable_hackernews=False,
                enable_arxiv=False,
                enable_duckduckgo=False,
                enable_rss_feeds=False,
                
                # 仅启用指定的API源
                enable_newsapi=True,        # NEWS_API_KEY
                enable_tavily=True,         # TAVILY_API_KEY  
                enable_google_search=True,  # GOOGLE_SEARCH_API_KEY
                enable_serper=True,         # SERPER_API_KEY
                enable_brave_search=True,   # BRAVE_SEARCH_API_KEY
                enable_metasota_search=False, # 不使用
                
                # 搜索参数
                max_articles_per_source=5,
                days_back=0,
                similarity_threshold=0.85,
                
                # 高级功能
                enable_content_extraction=False,
                enable_keyword_extraction=True,
                cache_results=False,
            )
            
            # 创建收集器
            collector = AdvancedAINewsCollector(search_config)
            
            # 定义应用与产品相关的搜索主题
            date_query_suffix = f" {today.strftime('%Y-%m-%d')}"
            topics = [
                f"new AI applications launched{date_query_suffix}",
                f"AI product releases and updates{date_query_suffix}",
                f"AI tools for consumers and businesses{date_query_suffix}",
                f"AI-powered apps and services{date_query_suffix}"
            ]
            
            print(f"使用多源并行搜索 AI 应用与产品...")
            
            # 异步收集
            import asyncio
            
            async def collect_async():
                if hasattr(collector, 'collect_multiple_topics'):
                    return await collector.collect_multiple_topics(topics)
                else:
                    results = []
                    for topic in topics:
                        if hasattr(collector, 'collect_news_advanced'):
                            result = await collector.collect_news_advanced(topic)
                            results.append(result)
                    
                    all_articles = []
                    for r in results:
                        all_articles.extend(r.get('articles', []))
                    return {"articles": all_articles, "unique_articles": len(all_articles)}
            
            result = asyncio.run(collect_async())
            articles = result.get('articles', [])
            
            print(f"应用与产品搜索找到 {len(articles)} 条结果")
            
            # 转换格式并过滤
            formatted_results = []
            for article in articles:
                published_date = article.get('published', '') or article.get('published_date', '')
                
                if not published_date:
                    continue
                
                try:
                    if 'T' in published_date:
                        pub_time = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    else:
                        pub_time = datetime.datetime.strptime(published_date, '%Y-%m-%d')
                    
                    if pub_time.tzinfo is None:
                        pub_time = pub_time.replace(tzinfo=datetime.timezone.utc)
                    
                    now = datetime.datetime.now(datetime.timezone.utc)
                    if pub_time > now or pub_time < yesterday:
                        continue
                        
                except Exception:
                    continue
                
                item = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'snippet': article.get('description', '')[:300],
                    'source': article.get('source', 'multi_source'),
                    'published_date': published_date,
                    'keywords': article.get('keywords', [])
                }
                
                if not self.is_duplicate(item):
                    item['quality_score'] = self.calculate_quality_score(item, 'applications')
                    formatted_results.append(item)
            
            # 按质量评分排序
            formatted_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            print(f"应用与产品搜索过滤后剩余 {len(formatted_results)} 条结果")
            return formatted_results[:10]  # 返回前10条
            
        except Exception as e:
            print(f"应用与产品搜索错误: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_github_trending(self) -> List[Dict]:
        """搜索GitHub Star快速增长的AI项目（工具与框架）"""
        if not self.github_token:
            print("WARNING: GitHub token未设置，跳过GitHub搜索")
            return []
            
        headers = {'Authorization': f'Bearer {self.github_token}'}
        url = 'https://api.github.com/search/repositories'
        
        yesterday, today = self.get_date_range(hours_back=24)
        
        # 策略：搜索最近7天创建的AI项目，按stars排序
        # 新项目star增长快，能反映出快速获得关注的优质项目
        week_ago = (yesterday - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        # 扩展搜索关键词，覆盖更多AI相关项目
        queries = [
            f'AI agent created:{week_ago}..{today_str}',
            f'AI coding created:{week_ago}..{today_str}',
            f'AI Tool created:{week_ago}..{today_str}',
            f'AI Algorithm created:{week_ago}..{today_str}',
            f'AI MCP created:{week_ago}..{today_str}',
            f'Claude Code related created:{week_ago}..{today_str}'
        ]
        
        all_projects = []
        
        for query in queries:
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 20
            }
            
            try:
                print(f"搜索GitHub项目: {query[:60]}...")
                response = requests.get(url, headers=headers, params=params, timeout=30)
                print(f"GitHub API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    # 计算star增长率（stars/天数）
                    for item in items:
                        created_at = item.get('created_at', '')
                        stars = item.get('stargazers_count', 0)
                        
                        if created_at:
                            try:
                                create_time = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                                days_since_creation = max(1, (datetime.datetime.now() - create_time).days)
                                item['stars_per_day'] = stars / days_since_creation
                                item['days_old'] = days_since_creation
                            except (ValueError, TypeError):
                                item['stars_per_day'] = 0
                                item['days_old'] = 999
                        else:
                            item['stars_per_day'] = 0
                            item['days_old'] = 999
                        
                        # 去重检查
                        if not self.is_duplicate(item):
                            item['quality_score'] = self.calculate_quality_score(item, 'github')
                            all_projects.append(item)
                    
                    print(f"找到 {len(items)} 个项目")
                    
                elif response.status_code == 403:
                    print("GitHub API 限流，跳过后续查询")
                    break
                elif response.status_code == 401:
                    print("[ERROR] GitHub Token 无效 (401 Unauthorized)")
                    print("        请检查 .env 文件中的 GITHUB_TOKEN 是否正确")
                    print("        运行 'python scripts/test_github_token.py' 验证Token有效性")
                    break
                else:
                    print(f"GitHub API错误: {response.status_code}")
                    
            except Exception as e:
                print(f"GitHub搜索错误: {e}")
        
        if not all_projects:
            return []
        
        # 按 star 增长率排序（优先）或按 quality_score 排序
        all_projects.sort(key=lambda x: (x.get('stars_per_day', 0), x.get('quality_score', 0)), reverse=True)
        
        print(f"GitHub: 共找到 {len(all_projects)} 个项目，按star增长率排序")
        
        # 返回前10个快速增长的项目
        top_projects = all_projects[:10]
        for p in top_projects:
            print(f"  - {p.get('name', '')}: {p.get('stargazers_count', 0)} stars ({p.get('stars_per_day', 0):.1f} stars/day)")
        
        return top_projects
    
    def search_huggingface_models(self) -> List[Dict]:
        """搜索 Hugging Face 热门模型（基于 likes/trending）
        
        策略优先级:
        1. 使用 huggingface_hub 库的 list_models(sort='trending') - 官方推荐
        2. 使用 huggingface_hub 库的 list_models(sort='likes') - Fallback
        3. 使用 HTTP API - 最终 Fallback
        """
        if not self.hf_token:
            print("WARNING: Hugging Face token 未设置，跳过 HF 搜索")
            return []
        
        # 策略1: 使用 huggingface_hub 官方库 (推荐)
        if USE_HF_HUB:
            try:
                print("搜索 Hugging Face 热门模型 (huggingface_hub 库)...")
                api = HfApi(token=self.hf_token)
                
                # 尝试 sort='trending' (按过去7天 likes 增长排序)
                # 如果不支持 trending，回退到 likes
                sort_options = ['trending', 'likes', 'downloads']
                
                for sort_by in sort_options:
                    try:
                        models = list(api.list_models(
                            sort=sort_by,
                            direction=-1,
                            limit=20
                        ))
                        
                        if models:
                            print(f"HF API (sort={sort_by}): 找到 {len(models)} 个模型")
                            
                            filtered_models = []
                            for m in models[:15]:
                                model = {
                                    'modelId': m.id if hasattr(m, 'id') else str(m),
                                    'pipeline_tag': m.pipeline_tag if hasattr(m, 'pipeline_tag') else '未知',
                                    'downloads': m.downloads if hasattr(m, 'downloads') else 0,
                                    'likes': m.likes if hasattr(m, 'likes') else 0,
                                    'lastModified': str(m.last_modified) if hasattr(m, 'last_modified') else '',
                                    'author': m.author if hasattr(m, 'author') else '',
                                    'source_type': f'hf_hub_{sort_by}'
                                }
                                
                                if not self.is_duplicate(model) and model['modelId']:
                                    model['quality_score'] = self.calculate_quality_score(model, 'huggingface')
                                    filtered_models.append(model)
                            
                            filtered_models.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                            print(f"HF (huggingface_hub): 筛选后 {len(filtered_models)} 个模型")
                            return filtered_models[:5]
                    except Exception as e:
                        print(f"HF sort={sort_by} 失败: {e}")
                        continue
                        
            except Exception as e:
                print(f"huggingface_hub 库调用失败: {e}")
        
        # 策略2: HTTP API Fallback
        print("使用 HTTP API Fallback...")
        headers = {'Authorization': f'Bearer {self.hf_token}'}
        fallback_url = 'https://huggingface.co/api/models'
        params = {
            'sort': 'likes',
            'direction': -1,
            'limit': 30
        }
        
        try:
            response = requests.get(fallback_url, headers=headers, params=params, timeout=30)
            print(f"HF HTTP API 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                models = response.json()
                
                filtered_models = []
                for model in models[:20]:
                    if self.is_duplicate(model):
                        continue
                    
                    normalized = {
                        'modelId': model.get('modelId', model.get('id', '')),
                        'pipeline_tag': model.get('pipeline_tag', '未知'),
                        'downloads': model.get('downloads', 0),
                        'likes': model.get('likes', 0),
                        'lastModified': model.get('lastModified', ''),
                        'source_type': 'http_api'
                    }
                    
                    if normalized['modelId']:
                        normalized['quality_score'] = self.calculate_quality_score(normalized, 'huggingface')
                        filtered_models.append(normalized)
                
                filtered_models.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                print(f"HF HTTP Fallback: 找到 {len(filtered_models)} 个模型")
                return filtered_models[:5]
            else:
                print(f"HF HTTP API 错误: {response.status_code}")
        except Exception as e:
            print(f"Hugging Face HTTP 搜索错误: {e}")
            
        return []
    
    def search_arxiv_papers(self) -> List[Dict]:
        """搜索ArXiv最新AI论文（缩短时间窗口至24小时）"""
        url = 'http://export.arxiv.org/api/query'
        
        yesterday, today = self.get_date_range(hours_back=24)
        start_date = yesterday.strftime('%Y%m%d')
        end_date = today.strftime('%Y%m%d')
        
        # 使用更严格的时间范围，只搜索今天提交的论文
        params = {
            'search_query': f'cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[{start_date}0000 TO {end_date}2359]',
            'start': 0,
            'max_results': 30,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            print(f"搜索ArXiv论文: {start_date} 到 {end_date}")
            response = requests.get(url, params=params, timeout=30)
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
                        
                        if not self.is_duplicate(paper) and self.is_within_time_range(paper, 'arxiv'):
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
    
    def search_huggingface_papers(self) -> List[Dict]:
        """搜索 HuggingFace Daily Papers (热门AI论文推荐)"""
        try:
            print("搜索 HuggingFace Daily Papers...")
            url = 'https://huggingface.co/api/daily_papers'
            headers = {'Authorization': f'Bearer {self.hf_token}'} if self.hf_token else {}
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"HuggingFace Papers API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                papers = response.json()
                
                formatted_papers = []
                for paper in papers[:10]:
                    paper_item = {
                        'title': paper.get('title', ''),
                        'authors': [a.get('name', '') for a in paper.get('authors', [])[:3]],
                        'summary': paper.get('summary', '')[:300],
                        'link': f"https://huggingface.co/papers/{paper.get('id', '')}",
                        'upvotes': paper.get('upvotes', 0),
                        'source': 'huggingface_papers'
                    }
                    
                    if not self.is_duplicate(paper_item) and paper_item['title']:
                        paper_item['quality_score'] = min(10.0, 7.0 + paper_item['upvotes'] / 50)
                        formatted_papers.append(paper_item)
                
                formatted_papers.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                print(f"HuggingFace Papers: 找到 {len(formatted_papers)} 篇论文")
                return formatted_papers[:5]
            else:
                print(f"HuggingFace Papers API错误: {response.status_code}")
                
        except Exception as e:
            print(f"HuggingFace Papers搜索错误: {e}")
            
        return []
    
    def _generate_section(self, section_name: str, section_data: List[Dict], section_prompt: str) -> str:
        """生成单个章节的AI内容 (Map-Reduce中的Map步骤)
        
        Args:
            section_name: 章节名称（用于日志）
            section_data: 该章节的数据
            section_prompt: 该章节的生成提示
            
        Returns:
            生成的章节内容，如果失败返回None
        """
        if not section_data:
            return None
            
        if not self.ai_client:
            return None
            
        try:
            if self.use_google_sdk:
                response = self.ai_client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=section_prompt,
                    config={'temperature': 0.5, 'max_output_tokens': 1500}
                )
                content = response.text if hasattr(response, 'text') else None
            else:
                response = self.ai_client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=[{"role": "user", "content": section_prompt}],
                    max_tokens=1500,
                    temperature=0.5
                )
                content = response.choices[0].message.content if response.choices else None
            
            if content and len(content.strip()) > 50:
                return content.strip()
            else:
                print(f"[WARNING] Section '{section_name}' AI生成内容过短或为空")
                return None
                
        except Exception as e:
            print(f"[ERROR] Section '{section_name}' AI生成失败: {e}")
            return None
    
    def generate_ai_summary(self, collected_data: Dict) -> str:
        """使用AI生成每日动态摘要 (Section-by-Section Generation / Map-Reduce)
        
        V2.1改进：每个章节独立生成，避免输出截断和"懒惰生成"问题
        """
        focus_news = collected_data.get('focus_news', [])
        hf_models = collected_data.get('hf_models', [])
        arxiv_papers = collected_data.get('arxiv_papers', [])
        hf_papers = collected_data.get('hf_papers', [])
        github_projects = collected_data.get('github_projects', [])
        applications = collected_data.get('applications', [])
        
        print(f"数据收集统计（按章节）:")
        print(f"   今日焦点（Google）: {len(focus_news)}")
        print(f"   模型与算法（HuggingFace）: {len(hf_models)}")
        print(f"   学术前沿（arXiv）: {len(arxiv_papers)}")
        print(f"   HuggingFace论文: {len(hf_papers)}")
        print(f"   工具与框架（GitHub）: {len(github_projects)}")
        print(f"   应用与产品（多源）: {len(applications)}")
        
        total_items = len(focus_news) + len(hf_models) + len(arxiv_papers) + len(github_projects) + len(applications) + len(hf_papers)
        
        if total_items == 0:
            print("WARNING: 没有收集到任何数据")
            return self.generate_fallback_summary(collected_data)
        
        print("开始分章节AI生成摘要 (Section-by-Section)...")
        
        sections = []
        section_errors = []
        
        # Section 1: 今日焦点
        if focus_news:
            prompt = f"""你是AI技术分析师。请基于以下数据生成"今日焦点"章节。

数据：
{json.dumps(focus_news, ensure_ascii=False, indent=2)}

输出格式：
## 📰 今日焦点

对于每条新闻，按以下格式输出：
### 🔥 [标题](链接)
- **简介**: 一句话核心总结
- **为何重要**: 简述影响力

要求：展示所有或大部分条目（至少{min(len(focus_news), 5)}条），按热度排序。"""
            
            content = self._generate_section("今日焦点", focus_news, prompt)
            if content:
                sections.append(content)
            else:
                section_errors.append("今日焦点")
                sections.append(self._fallback_focus_news(focus_news))
        
        # Section 2: 模型与算法
        if hf_models:
            prompt = f"""你是AI技术分析师。请基于以下数据生成"模型与算法"章节。

数据：
{json.dumps(hf_models, ensure_ascii=False, indent=2)}

输出格式：
## 🧠 模型与算法

对于每个模型，按以下格式输出：
### [模型ID](https://huggingface.co/模型ID)
- **类型**: Pipeline Tag
- **热度**: 下载量/Likes
- **介绍**: 核心能力简述

要求：展示所有或大部分条目（至少{min(len(hf_models), 4)}个）。"""
            
            content = self._generate_section("模型与算法", hf_models, prompt)
            if content:
                sections.append(content)
            else:
                section_errors.append("模型与算法")
                sections.append(self._fallback_hf_models(hf_models))
        
        # Section 3: 工具与框架
        if github_projects:
            prompt = f"""你是AI技术分析师。请基于以下数据生成"工具与框架"章节。

数据：
{json.dumps(github_projects[:8], ensure_ascii=False, indent=2)}

输出格式：
## 🛠️ 工具与框架

对于每个项目，按以下格式输出：
### [项目名](html_url)
- **功能**: 简要说明
- **趋势**: Stars数量 (stars_per_day stars/day)

要求：展示前5-8个项目，按增长率排序。"""
            
            content = self._generate_section("工具与框架", github_projects, prompt)
            if content:
                sections.append(content)
            else:
                section_errors.append("工具与框架")
                sections.append(self._fallback_github(github_projects))
        else:
            sections.append("## 🛠️ 工具与框架\n\n⚠️ 今日暂无新工具框架发布。\n")
        
        # Section 4: 应用与产品
        if applications:
            prompt = f"""你是AI技术分析师。请基于以下数据生成"应用与产品"章节。

数据：
{json.dumps(applications[:8], ensure_ascii=False, indent=2)}

输出格式：
## 📱 应用与产品

对于每个应用，按以下格式输出：
### [应用名](url)
- **来源**: 数据源名称
- **介绍**: 功能与价值

要求：展示前5-8个应用。"""
            
            content = self._generate_section("应用与产品", applications, prompt)
            if content:
                sections.append(content)
            else:
                section_errors.append("应用与产品")
                sections.append(self._fallback_applications(applications))
        
        # Section 5: 学术前沿 (合并ArXiv和HuggingFace Papers)
        all_papers = arxiv_papers + hf_papers
        if all_papers:
            prompt = f"""你是AI技术分析师。请基于以下数据生成"学术前沿"章节。

数据：
{json.dumps(all_papers[:10], ensure_ascii=False, indent=2)}

输出格式：
## 📚 学术前沿

对于每篇论文，按以下格式输出：
### [论文标题](链接)
- **作者**: 主要作者
- **摘要**: 核心创新点（1-2句）

要求：展示前5-8篇论文，按质量评分排序。"""
            
            content = self._generate_section("学术前沿", all_papers, prompt)
            if content:
                sections.append(content)
            else:
                section_errors.append("学术前沿")
                sections.append(self._fallback_arxiv(arxiv_papers))
        
        # Section 6: 编辑点评 (基于所有已生成章节)
        all_sections_text = "\n".join(sections)
        editor_prompt = f"""你是AI技术分析师。请基于以下已生成的今日AI动态摘要，撰写编辑点评。

已生成内容：
{all_sections_text[:3000]}

输出格式：
## 💡 编辑点评

- 总结今日整体趋势（2-3点）
- 最值得关注的一个技术突破

要求：简洁专业，2-3段即可。"""
        
        editor_content = self._generate_section("编辑点评", [{"summary": "all"}], editor_prompt)
        if editor_content:
            sections.append(editor_content)
        else:
            section_errors.append("编辑点评")
            sections.append(self._fallback_editor_review(collected_data))
        
        # 汇总错误日志
        if section_errors:
            print(f"[ERROR] 以下章节AI生成失败，使用了fallback: {section_errors}")
        
        # 组装最终摘要
        final_summary = "\n\n".join(sections)
        print(f"AI摘要生成完成（长度: {len(final_summary)}，错误章节: {len(section_errors)}）")
        
        return final_summary
    
    def _fallback_focus_news(self, focus_news: List[Dict]) -> str:
        """今日焦点章节的fallback生成器"""
        summary = "## 📰 今日焦点\n\n"
        sorted_news = sorted(focus_news, key=lambda x: x.get('quality_score', 0), reverse=True)
        for item in sorted_news[:5]:
            title = item.get('title', '未知标题')
            url = item.get('url', '')
            snippet = item.get('snippet', '')[:150]
            score = item.get('quality_score', 5.0)
            heat_icon = "🔥🔥🔥" if score >= 8.0 else "🔥🔥" if score >= 7.0 else "🔥"
            summary += f"### {heat_icon} [{title}]({url})\n"
            summary += f"- **简介**: {snippet}...\n"
            summary += f"- **质量评分**: {score:.1f}/10\n\n"
        return summary
    
    def _fallback_hf_models(self, hf_models: List[Dict]) -> str:
        """模型与算法章节的fallback生成器"""
        summary = "## 🧠 模型与算法\n\n"
        for model in hf_models[:5]:
            model_id = model.get('modelId', '未知模型')
            pipeline = model.get('pipeline_tag', '未知类型')
            downloads = model.get('downloads', 0)
            summary += f"### {model_id}\n"
            summary += f"- **类型**: {pipeline}\n"
            summary += f"- **下载量**: {downloads:,}\n"
            summary += f"- **链接**: https://huggingface.co/{model_id}\n\n"
        return summary
    
    def _fallback_github(self, github_projects: List[Dict]) -> str:
        """工具与框架章节的fallback生成器"""
        summary = "## 🛠️ 工具与框架\n\n"
        for project in github_projects[:5]:
            name = project.get('name', '未知项目')
            desc = project.get('description', '无描述')
            url = project.get('html_url', '')
            stars = project.get('stargazers_count', 0)
            stars_per_day = project.get('stars_per_day', 0)
            summary += f"### [{name}]({url})\n"
            summary += f"- **功能**: {desc}\n"
            summary += f"- **Stars**: {stars:,} ({stars_per_day:.1f} stars/day)\n\n"
        return summary
    
    def _fallback_applications(self, applications: List[Dict]) -> str:
        """应用与产品章节的fallback生成器"""
        summary = "## 📱 应用与产品\n\n"
        for app in applications[:5]:
            title = app.get('title', '未知应用')
            url = app.get('url', '')
            snippet = app.get('snippet', '无描述')[:150]
            source = app.get('source', '未知来源')
            summary += f"### [{title}]({url})\n"
            summary += f"- **来源**: {source}\n"
            summary += f"- **简介**: {snippet}...\n\n"
        return summary
    
    def _fallback_arxiv(self, arxiv_papers: List[Dict]) -> str:
        """学术前沿章节的fallback生成器"""
        summary = "## 📚 学术前沿\n\n"
        for paper in arxiv_papers[:5]:
            title = paper.get('title', '未知标题')
            authors = ', '.join(paper.get('authors', [])[:3])
            if len(paper.get('authors', [])) > 3:
                authors += ' 等'
            link = paper.get('link', '')
            abstract = paper.get('summary', '无摘要')[:200]
            summary += f"### [{title}]({link})\n"
            summary += f"- **作者**: {authors}\n"
            summary += f"- **摘要**: {abstract}...\n\n"
        return summary
    
    def _fallback_editor_review(self, collected_data: Dict) -> str:
        """编辑点评章节的fallback生成器"""
        focus_news = collected_data.get('focus_news', [])
        hf_models = collected_data.get('hf_models', [])
        arxiv_papers = collected_data.get('arxiv_papers', [])
        hf_papers = collected_data.get('hf_papers', [])  # V2.1 新增
        github_projects = collected_data.get('github_projects', [])
        applications = collected_data.get('applications', [])
        
        total_items = len(focus_news) + len(hf_models) + len(arxiv_papers) + len(hf_papers) + len(github_projects) + len(applications)
        
        summary = "## 💡 编辑点评\n\n"
        summary += f"今日共收集到 {total_items} 条AI动态（分章节数据源），其中：\n"
        if focus_news:
            summary += f"- 📰 今日焦点: {len(focus_news)} 条\n"
        if hf_models:
            summary += f"- 🧠 模型与算法: {len(hf_models)} 个\n"
        if github_projects:
            summary += f"- 🛠️ 工具与框架: {len(github_projects)} 个\n"
        if applications:
            summary += f"- 📱 应用与产品: {len(applications)} 条\n"
        if arxiv_papers or hf_papers:
            summary += f"- 📚 学术前沿: {len(arxiv_papers) + len(hf_papers)} 篇\n"
        summary += "\n**V2.1新特性**：采用分章节独立生成，确保内容完整不截断。\n"
        return summary

    def generate_fallback_summary(self, collected_data: Dict) -> str:
        """生成备用摘要（新分章节专用数据源）"""
        print("使用 fallback 摘要生成器（新策略：按章节分配数据源）...")
        summary = ""
        
        # 今日焦点 - 使用 focus_news (Google Search - 大模型厂商)
        summary += "## 📰 今日焦点\n\n"
        focus_news = collected_data.get('focus_news', [])
        
        if focus_news:
            print(f"DEBUG: 从 focus_news 中生成今日焦点 ({len(focus_news)} 条)")
            # 按质量评分排序
            sorted_news = sorted(focus_news, key=lambda x: x.get('quality_score', 0), reverse=True)
            
            for item in sorted_news[:3]:
                title = item.get('title', '未知标题')
                url = item.get('url', '')
                snippet = item.get('snippet', '')[:150] 
                score = item.get('quality_score', 5.0)
                
                if title and url:
                    heat_icon = "🔥🔥🔥" if score >= 8.0 else "🔥🔥" if score >= 7.0 else "🔥"
                    summary += f"### {heat_icon} [{title}]({url})\n"
                    summary += f"- **简介**: {snippet}...\n"
                    summary += f"- **来源**: Google Search（大模型厂商）\n"
                    summary += f"- **质量评分**: {score:.1f}/10\n\n"
        else:
            summary += "⚠️ 今日暂无大模型厂商重要新闻发布。\n\n"
        
        # 模型与算法 - 使用 hf_models (HuggingFace)
        summary += "## 🧠 模型与算法\n\n"
        hf_models = collected_data.get('hf_models', [])
        if hf_models:
            for model in hf_models[:5]:
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
            summary += "⚠️ 今日暂无新模型发布。\n\n"
        
        # 工具与框架 - 使用 github_projects (GitHub Star快速增长)
        summary += "## 🛠️ 工具与框架\n\n"
        github_projects = collected_data.get('github_projects', [])
        if github_projects:
            for project in github_projects[:5]:
                name = project.get('name', '未知项目')
                desc = project.get('description', '无描述')
                url = project.get('html_url', '')
                stars = project.get('stargazers_count', 0)
                stars_per_day = project.get('stars_per_day', 0)
                score = project.get('quality_score', 5.0)
                rating = '⭐' * min(5, int(score / 2))
                summary += f"### [{name}]({url})\n"
                summary += f"- **功能**: {desc}\n"
                summary += f"- **Stars**: {stars:,} ({stars_per_day:.1f} stars/day)\n"
                summary += f"- **推荐指数**: {rating}\n\n"
        else:
            summary += "⚠️ 今日暂无新工具框架发布。\n\n"
        
        # 应用与产品 - 使用 applications (多源并行搜索)
        summary += "## 📱 应用与产品\n\n"
        applications = collected_data.get('applications', [])
        if applications:
            for app in applications[:5]:
                title = app.get('title', '未知应用')
                url = app.get('url', '')
                snippet = app.get('snippet', '无描述')[:150]
                source = app.get('source', '未知来源')
                score = app.get('quality_score', 5.0)
                summary += f"### [{title}]({url})\n"
                summary += f"- **简介**: {snippet}...\n"
                summary += f"- **来源**: {source}\n"
                summary += f"- **质量评分**: {score:.1f}/10\n\n"
        else:
            summary += "⚠️ 今日暂无新应用与产品发布。\n\n"
        
        # 全网热搜 - 使用 perplexity_news
        perplexity_news = collected_data.get('perplexity_news', [])
        if perplexity_news:
             summary += "## 🌐 全网热搜 (Perplexity)\n\n"
             # 简单去重 (URL)
             shown_urls = set()
             for item in perplexity_news[:5]:
                 url = item.get('url', '')
                 if url in shown_urls: continue
                 shown_urls.add(url)
                 
                 title = item.get('title', '无标题')
                 snippet = item.get('snippet', '')[:150]
                 date = item.get('date', '')
                 
                 summary += f"### [{title}]({url})\n"
                 summary += f"- **摘要**: {snippet}...\n"
                 summary += f"- **时间**: {date}\n\n"
        
        # 学术前沿 - 使用 arxiv_papers (arXiv)
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
            summary += "⚠️ 今日暂无重要论文发布。\n\n"
        
        # 编辑点评
        summary += "## 💡 编辑点评\n\n"
        total_items = len(focus_news) + len(hf_models) + len(arxiv_papers) + len(github_projects) + len(applications)
        if total_items > 0:
            summary += f"今日共收集到 {total_items} 条AI动态（按章节分配数据源），其中：\n"
            if focus_news:
                summary += f"- 📰 今日焦点（Google）: {len(focus_news)} 条\n"
            if hf_models:
                summary += f"- 🧠 模型与算法（HuggingFace）: {len(hf_models)} 个\n"
            if arxiv_papers:
                summary += f"- 📚 学术前沿（arXiv）: {len(arxiv_papers)} 篇\n"
            if github_projects:
                summary += f"- 🛠️ 工具与框架（GitHub）: {len(github_projects)} 个\n"
            if applications:
                summary += f"- 📱 应用与产品（多源）: {len(applications)} 条\n"
            summary += "\n内容质量均经过自动评分和排序，优先展示高质量项目。\n"
            summary += "\n**新策略**：采用分章节专用数据源，确保内容更精准、更聚焦。\n"
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
        
        # 收集数据（按新章节分配数据源）
        print("=" * 60)
        print("开始收集数据（新策略：按章节分配专用数据源）...")
        print("=" * 60)
        
        collected_data = {
            # 今日焦点 - 仅使用 Google Search 搜索大模型厂商
            'focus_news': self.search_focus_news(),
            
            # 模型与算法 - 仅使用 HuggingFace
            'hf_models': self.search_huggingface_models(),
            
            # 学术前沿 - arXiv + HuggingFace Papers
            'arxiv_papers': self.search_arxiv_papers(),
            'hf_papers': self.search_huggingface_papers(),  # V2.1 新增
            
            # 工具与框架 - GitHub Star 快速增长
            'github_projects': self.search_github_trending(),
            
            # 应用与产品 - NewsAPI, Tavily, Google, Serper, Brave 并行搜索
            'applications': self.search_applications(), 
            
            # 深度搜索 - Perplexity (补充视角)
            'perplexity_news': self.search_perplexity_ai_news(),
        }
        
        print("=" * 60)
        print("数据收集完成，开始生成摘要...")
        print("=" * 60)
        
        # 生成AI摘要
        ai_summary = self.generate_ai_summary(collected_data)
        
        # 统计信息
        total_items = sum(len(v) for v in collected_data.values())
        
        # 构建页脚（用于统计字数）
        footer = """
## 📊 数据来源

本报告采用**分章节专用数据源**策略：

- 📰 **今日焦点**: Google Search（专注大模型厂商：OpenAI, Gemini, Anthropic, xAI, Meta, Qwen, DeepSeek, GLM, Kimi等）
- 🌐 **全网热搜**: Perplexity AI（深度语义搜索补全）
- 🧠 **模型与算法**: HuggingFace（新开源模型）
- 📚 **学术前沿**: arXiv（最新AI论文）
- 🛠️ **工具与框架**: GitHub（Star快速增长的AI项目）
- 📱 **应用与产品**: NewsAPI, Tavily, Google, Serper, Brave（多源并行搜索）

所有内容经过**质量评分**、**去重**和**智能排序**，确保信息的价值和时效性。

---

> 💡 **提示**: 本内容由 AI 自动生成，每日北京时间 08:00 更新。  
> 如有遗漏或错误，欢迎通过 [Issues](https://github.com/hobbytp/hobbytp.github.io/issues) 反馈。
"""

        # 预计算正文部分的字数和阅读时间（用于Header中的显示）
        # 正文 = AI摘要 + 页脚
        body_for_calc = ai_summary + "\n" + footer
        _, estimated_reading_time = calculate_reading_stats(body_for_calc, reading_speed=400)
        
        # 构建Header
        header = f"""# 每日AI动态 - {date_str}

> 📅 **时间范围**: {time_range} (北京时间)  
> 📊 **内容统计**: 共 {total_items} 条动态  
> ⏱️ **预计阅读**: {estimated_reading_time} 分钟"""

        # 组装完整正文
        full_body = f"{header}\n\n---\n\n{ai_summary}\n\n---\n{footer}"
        
        # 最终统计字数和阅读时间（包括Header）
        word_count, reading_time = calculate_reading_stats(full_body, reading_speed=400)

        # 创建Markdown内容
        content = f"""---
title: "每日AI动态 - {date_str}"
date: {today.strftime('%Y-%m-%dT%H:%M:%S+08:00')}
draft: false
categories: ["news"]
tags: ["AI动态", "技术更新", "行业趋势"]
description: "{date_str}的AI技术动态汇总"
readingTime: {reading_time}
wordCount: {word_count}
totalItems: {total_items}
---

{full_body}
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
        print(f"[OK] 每日AI动态已保存到: {file_path}")
        print("=" * 60)
        return file_path

def main():
    """主函数"""
    print("=" * 60)
    print("每日AI动态收集器 V2.1 - 专业版 (Section-by-Section Generation)")
    print("=" * 60)
    
    collector = DailyAICollectorV2_1()
    file_path = collector.save_daily_content()
    
    print(f"\n[OK] 收集完成: {file_path}")
    print("\n新功能：")
    print("  [OK] Perplexity AI 新闻搜索")
    print("  [OK] 24小时时间窗口（真正的每日动态）")
    print("  [OK] 智能去重")
    print("  [OK] 内容质量评分")
    print("  [OK] 新的分类体系")
    print("  [OK] 改进的展现格式")

if __name__ == "__main__":
    main()
