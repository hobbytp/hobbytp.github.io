from typing import List
import asyncio
from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

try:
    from ai_news_collector_lib import AdvancedSearchConfig, AdvancedAINewsCollector
    USE_AI_LIB = True
except ImportError:
    USE_AI_LIB = False


class MultiEngineNewsFetcher(BaseFetcher):
    """全网多引擎聚合热搜感知 (基于 ai_news_collector_lib，支持 DuckDuckGo, Tavily, Brave 等)"""

    def fetch(self, query: str = "最新突破性 AI大模型 人工智能 科技新闻") -> List[ArticleItem]:
        results = []
        if not USE_AI_LIB:
            print("[WARNING] 未检测到 ai_news_collector_lib 依赖，跳过多引擎热搜感知。")
            return results

        print("[INFO] 正在调度采集源: MultiEngineNewsFetcher (多引擎聚合检索) ...")
        try:
            from scripts.daily_ai.config.config_loader import config as llm_config

            search_config = AdvancedSearchConfig()
            # 仅开启可靠且高效的纯搜索引擎源，关闭重复或容易异常的外部服务
            search_config.enable_duckduckgo = True
            search_config.enable_tavily = bool(env_config.TAVILY_API_KEY)
            search_config.tavily_api_key = env_config.TAVILY_API_KEY if env_config.TAVILY_API_KEY else None
            search_config.enable_brave_search = bool(env_config.BRAVE_SEARCH_API_KEY)
            search_config.brave_search_api_key = env_config.BRAVE_SEARCH_API_KEY if env_config.BRAVE_SEARCH_API_KEY else None

            # 彻底关闭失效或易产生挂起重试的源
            search_config.enable_perplexity = False
            search_config.perplexity_api_key = None
            search_config.enable_metasota_search = False
            search_config.metasota_search_api_key = None
            search_config.enable_hackernews = False
            search_config.enable_arxiv = False
            search_config.enable_rss_feeds = False
            search_config.enable_newsapi = False
            search_config.enable_google_search = False
            search_config.enable_serper = False
            search_config.enable_baidu_search = False
            search_config.enable_youtube = False
            search_config.enable_github_search = False
            search_config.enable_huggingface = False

            search_config.days_back = 1
            search_config.max_articles_per_source = 3
            search_config.enable_keyword_extraction = True
            search_config.enable_sentiment_analysis = True
            search_config.enable_content_extraction = False  # 关闭重量级网页全文抓取，防止慢速卡死
            search_config.keyword_count = 4

            # LLM 增强配置
            provider = llm_config.provider_name.lower()
            if provider in ["google", "gemini"]:
                provider = "google-gemini"
            search_config.llm_provider = provider
            search_config.llm_model = llm_config.model_name

            if llm_config.api_key:
                search_config.llm_api_key = llm_config.api_key
                search_config.enable_query_enhancement = True
            else:
                search_config.enable_query_enhancement = False

            active_sources = ["duckduckgo"]
            if search_config.enable_tavily:
                active_sources.append("tavily")
            if search_config.enable_brave_search:
                active_sources.append("brave_search")

            collector = AdvancedAINewsCollector(config=search_config)

            async def _collect():
                return await collector.collect_news(query, sources=active_sources)

            # 增加 30 秒强制超时保护，确保 CI/CD 绝不挂起
            lib_results = asyncio.run(asyncio.wait_for(_collect(), timeout=30.0))

            items = getattr(lib_results, 'articles', [])
            for item in items:
                results.append(ArticleItem(
                    title=item.title,
                    url=item.url,
                    source=item.source,
                    description=item.summary or item.content[:200] if hasattr(item, 'summary') else "",
                    published_date=getattr(item, 'published', getattr(item, 'published_date', None)),
                    keywords=getattr(item, 'keywords', []) or [],
                    sentiment=getattr(item, 'sentiment', None)
                ))

            print(f"[OK] 多引擎聚合检索成功，获取到 {len(results)} 条热搜记录")
        except asyncio.TimeoutError:
            print("[WARNING] 多引擎聚合检索请求超时(>30s)，自动跳过以保障主流程顺畅执行。")
        except Exception as e:
            print(f"[ERROR] 多引擎聚合检索执行异常: {e}")

        return results


# 保持别名兼容
PerplexityFallbackFetcher = MultiEngineNewsFetcher
