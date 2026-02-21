from typing import List
from urllib.parse import urlparse
from scripts.daily_ai.models import BaseItem

class Deduplicator:
    def __init__(self, history_urls: set = None, history_titles: set = None):
         self.seen_urls = history_urls or set()
         self.seen_titles = history_titles or set()
         
    def _normalize_url(self, url: str) -> str:
        if not url: return ""
        try:
             parsed = urlparse(url)
             return f"{parsed.netloc}{parsed.path}".rstrip('/').lower()
        except:
             return url.lower()
             
    def process(self, items: List[BaseItem]) -> List[BaseItem]:
         unique_items = []
         for item in items:
             title_lower = item.title.lower().strip()
             url_norm = self._normalize_url(item.url)
             
             if title_lower and title_lower in self.seen_titles:
                 print(f"  - 跳过重复标题: {title_lower[:30]}...")
                 continue
                 
             if url_norm and url_norm in self.seen_urls:
                 print(f"  - 跳过重复URL: {url_norm}")
                 continue
                 
             self.seen_titles.add(title_lower)
             if url_norm: self.seen_urls.add(url_norm)
             
             unique_items.append(item)
             
         return unique_items
