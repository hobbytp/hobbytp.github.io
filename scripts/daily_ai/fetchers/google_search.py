import requests
from typing import List
from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

class GoogleSearchFetcher(BaseFetcher):
    """获取大厂 AI 焦点新闻"""
    def fetch(self, q: str = "OpenAI OR Gemini OR Anthropic OR DeepSeek OR xAI OR Grok") -> List[ArticleItem]:
        news = []
        if not (env_config.GOOGLE_SEARCH_API_KEY and env_config.GOOGLE_SEARCH_ENGINE_ID):
            print("[WARNING] Google Search 凭证不完整，跳过此源。")
            return news
            
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': env_config.GOOGLE_SEARCH_API_KEY,
                'cx': env_config.GOOGLE_SEARCH_ENGINE_ID,
                'q': q,
                'sort': 'date',
                'num': 10,
                'dateRestrict': 'd1' # 最近1天
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    news.append(ArticleItem(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        source="Google Search",
                        description=item.get('snippet', ''),
                        published_date="recent"
                    ))
            else:
                print(f"[ERROR] Google Search API 返回错误: {response.text}")
        except Exception as e:
             print(f"[ERROR] Google Search 抓取失败: {e}")
             
        return news
