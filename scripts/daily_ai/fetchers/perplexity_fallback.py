"""
全网热搜感知模块（兼容别名，已将底层升级为纯净的 MultiEngineNewsFetcher）
"""
from scripts.daily_ai.fetchers.multi_engine_news import MultiEngineNewsFetcher, PerplexityFallbackFetcher

__all__ = ["MultiEngineNewsFetcher", "PerplexityFallbackFetcher"]
