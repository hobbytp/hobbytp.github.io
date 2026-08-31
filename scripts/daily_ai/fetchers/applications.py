import requests
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import List

from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher

PRODUCT_FEEDS = [
    {
        "name": "Product Hunt AI",
        "url": "https://www.producthunt.com/feed"
    }
]

AI_APP_KEYWORDS = [
    'ai', 'copilot', 'agent', 'assistant', 'bot', 'llm', 'gpt', 'generator',
    'automation', 'transcribe', 'voice', 'video', 'search', 'workflow'
]


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class ApplicationsFetcher(BaseFetcher):
    """
    抓取最新 AI 落地产品与商业应用（支持 Product Hunt 与 Hacker News Show HN 产品过滤）
    """

    def __init__(self, hours_back: int = 48):
        super().__init__()
        self.hours_back = hours_back

    def fetch(self, limit: int = 8) -> List[ArticleItem]:
        items: List[ArticleItem] = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.hours_back)

        # 1. 抓取 Product Hunt RSS
        for feed_info in PRODUCT_FEEDS:
            try:
                resp = requests.get(feed_info["url"], headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Collector/3.0"
                }, timeout=12)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    # Atom feed entries
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for entry in root.findall(".//atom:entry", ns)[:25] or root.findall(".//entry")[:25]:
                        title_elem = entry.find("atom:title", ns) or entry.find("title")
                        link_elem = entry.find("atom:link", ns) or entry.find("link")
                        summary_elem = entry.find("atom:summary", ns) or entry.find("summary") or entry.find("atom:content", ns) or entry.find("content")
                        updated_elem = entry.find("atom:updated", ns) or entry.find("updated") or entry.find("atom:published", ns) or entry.find("published")

                        title = clean_text(title_elem.text) if title_elem is not None and title_elem.text else ""
                        link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                        summary = clean_text(summary_elem.text) if summary_elem is not None and summary_elem.text else ""
                        pub_str = updated_elem.text.strip() if updated_elem is not None and updated_elem.text else ""

                        if not title or not link:
                            continue

                        # 过滤是否属于 AI 产品
                        combined = f"{title} {summary}".lower()
                        if not any(re.search(r'\b' + kw + r'\b', combined) for kw in AI_APP_KEYWORDS):
                            continue

                        items.append(ArticleItem(
                            title=title,
                            url=link,
                            source="Product Hunt",
                            description=summary[:200] if summary else "新发布 AI 商业产品",
                            published_date=pub_str
                        ))
            except Exception as e:
                # print(f"[DEBUG] Product Hunt fetch error: {e}")
                pass

        # 2. 抓取 Hacker News 的 Show HN AI 产品
        try:
            cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=self.hours_back)).timestamp())
            url = f"https://hn.algolia.com/api/v1/search?query=Show%20HN%20AI&tags=show_hn&numericFilters=created_at_i>{cutoff_ts},points>=8&hitsPerPage=15"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                for hit in resp.json().get("hits", []):
                    title = clean_text(hit.get("title") or "").replace("Show HN:", "").strip()
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    points = hit.get("points") or 0
                    snippet = clean_text(hit.get("story_text") or "")[:150]
                    desc = f"极客新产品发布 | 热度: {points} points" + (f" | {snippet}" if snippet else "")
                    
                    items.append(ArticleItem(
                        title=title,
                        url=url,
                        source="Show HN Launch",
                        description=desc,
                        published_date=hit.get("created_at", "")
                    ))
        except Exception:
            pass

        print(f"[INFO] Applications: 成功捕获 {len(items)} 个新锐 AI 应用与落地产品")
        return items[:limit]
