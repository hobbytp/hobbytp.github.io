from typing import List
from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

try:
    from perplexity import Perplexity
    USE_PERPLEXITY = True
except ImportError:
    USE_PERPLEXITY = False

try:
    from ai_news_collector_lib import FlexibleAINewsCollector, FlexibleSearchConfig, EngineConfig
    USE_AI_LIB = True
except ImportError:
    USE_AI_LIB = False

class PerplexityFallbackFetcher(BaseFetcher):
    """全网热搜感知 (带降级策略：优先 Perplexity，失败则 fallback 到 ai_news_collector_lib 的多引擎聚合)"""
    
    def __init__(self):
        super().__init__()
        self.perplexity_client = None
        if USE_PERPLEXITY and env_config.PERPLEXITY_API_KEY:
            try:
                 self.perplexity_client = Perplexity(api_key=env_config.PERPLEXITY_API_KEY, timeout=60.0)
            except Exception:
                 pass
                 
    def fetch(self, query: str = "过去24小时内，AI大模型、人工智能领域最重大、最引发热议的5个突破性新闻起因是什么？") -> List[ArticleItem]:
        results = []
        success = False
        
        # 1. 优先尝试 Perplexity
        if self.perplexity_client:
            print("[INFO] 尝试使用 Perplexity 获取热点...")
            try:
                # 尝试调用 search 方法 (可能是 sync 或 async，这里假设是 sync 或库支持)
                # 如果库版本不同，可能需要调整
                if hasattr(self.perplexity_client, 'search_sync'):
                    response = self.perplexity_client.search_sync(query)
                elif hasattr(self.perplexity_client, 'search'):
                    response = self.perplexity_client.search(query)
                    # 如果返回是协程，则需要 await，但这里是在同步方法中
                    import inspect
                    if inspect.iscoroutine(response):
                        import asyncio
                        response = asyncio.run(response)
                else:
                    raise AttributeError("Perplexity client has no search method")

                answer = response.get('answer', '')
                sources = response.get('citations', [])
                
                if answer and sources:
                    results.append(ArticleItem(
                        title="Perplexity 全网AI热搜总览",
                        url=sources[0] if sources else "https://perplexity.ai",
                        source="Perplexity",
                        description=answer[:1000],
                        published_date="recent"
                    ))
                    success = True
                    print("[OK] Perplexity 获取成功")
                else:
                    print("[WARNING] Perplexity 响应结构异常，无结果。准备降级。")
            except Exception as e:
                print(f"[WARNING] Perplexity 调用失败 ({e})。配额可能耗尽或网络异常，准备降级。")
                
        # 2. 如果 Perplexity 失败，立刻降级到 ai_news_collector_lib (利用 v0.1.5 的特性)
        if not success and USE_AI_LIB:
            print("[INFO] 启用容灾降级：使用 ai_news_collector_lib 多引擎聚合搜索")
            import asyncio
            try:
                # 关闭需要付费或无关的，开启免费多源
                from scripts.daily_ai.config.config_loader import config as llm_config
                from ai_news_collector_lib import AdvancedSearchConfig, AdvancedAINewsCollector
                
                search_config = AdvancedSearchConfig()
                search_config.enable_duckduckgo = True
                search_config.enable_tavily = bool(env_config.TAVILY_API_KEY)
                search_config.enable_brave_search = bool(env_config.BRAVE_SEARCH_API_KEY)
                search_config.enable_newsapi = False
                search_config.enable_google_search = False
                search_config.enable_serper = False
                search_config.days_back = 1
                search_config.max_articles_per_source = 3
                search_config.enable_query_enhancement = True
                
                # 映射 provider 名称，确保 ai_news_collector_lib 能识别
                provider = llm_config.provider_name.lower()
                if provider == "google":
                    provider = "gemini"
                search_config.llm_provider = provider
                search_config.llm_model = llm_config.model_name
                
                if llm_config.api_key:
                     search_config.llm_api_key = llm_config.api_key
                
                collector = AdvancedAINewsCollector(config=search_config)
                # 使用大模型重写基础query，发散给搜索源
                lib_results = asyncio.run(collector.collect_news("最新突破性 AI大模型 人工智能 新闻"))
                
                # 修复: SearchResult 对象不可迭代，需访问 articles 属性
                items = getattr(lib_results, 'articles', [])
                
                for item in items:
                     results.append(ArticleItem(
                         title=item.title,
                         url=item.url,
                         source=item.source,
                         description=item.summary or item.content[:200] if hasattr(item, 'summary') else "",
                         published_date=item.published_date
                     ))
                     
                print(f"[OK] 降级搜索成功，获取到 {len(results)} 条聚合热搜记录")
                
            except Exception as e:
                print(f"[ERROR] ai_news_collector_lib 降级搜索也失败了: {e}")
                
        return results
