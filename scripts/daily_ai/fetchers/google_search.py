import requests
from urllib.parse import urlparse
from typing import List
from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

class GoogleSearchFetcher(BaseFetcher):
    """获取大厂 AI 焦点新闻 (过滤噪音社交媒体，聚焦官方发布与权威科技报道)"""
    
    DEFAULT_QUERY = (
        '(OpenAI OR Anthropic OR "Google DeepMind" OR DeepSeek OR "Meta AI" OR Mistral OR Qwen OR Grok) '
        '(announces OR releases OR launches OR introduces OR breakthrough OR "open source" OR benchmark) '
        '-site:twitter.com -site:x.com -site:linkedin.com -site:facebook.com -site:reddit.com -site:quora.com'
    )

    def fetch(self, q: str = None) -> List[ArticleItem]:
        news = []
        if not (env_config.GOOGLE_SEARCH_API_KEY and env_config.GOOGLE_SEARCH_ENGINE_ID):
            print("[WARNING] Google Search 凭证不完整，跳过此源。")
            return news
            
        search_query = q or self.DEFAULT_QUERY
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': env_config.GOOGLE_SEARCH_API_KEY,
                'cx': env_config.GOOGLE_SEARCH_ENGINE_ID,
                'q': search_query,
                'sort': 'date',
                'num': 10,
                'dateRestrict': 'd2' # 最近1-2天
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    link = item.get('link', '')
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    
                    # 过滤空链接和明显噪音
                    if not link or not title:
                        continue
                    
                    # 提取主域名作为更明确的来源标识
                    domain = urlparse(link).netloc.replace('www.', '')
                    
                    news.append(ArticleItem(
                        title=title,
                        url=link,
                        source=f"Google ({domain})" if domain else "Google Search",
                        description=snippet,
                        published_date="recent"
                    ))
                print(f"[INFO] Google Search 抓取成功，获取 {len(news)} 条精选新闻")
            else:
                print(f"[ERROR] Google Search API 返回错误: {response.text[:200]}")
        except Exception as e:
             print(f"[ERROR] Google Search 抓取失败: {e}")
             
        return news

