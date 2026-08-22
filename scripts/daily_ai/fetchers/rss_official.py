import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
import html
import re

from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher

try:
    import feedparser
    USE_FEEDPARSER = True
except ImportError:
    USE_FEEDPARSER = False


# 精选的高信噪比官方发布源与权威科技媒体
OFFICIAL_AI_FEEDS = [
    # 官方第一手实验室/大厂
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "tier": "official"
    },
    {
        "name": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss.xml",
        "tier": "official"
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": "official"
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "tier": "official"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "tier": "official"
    },
    {
        "name": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "tier": "official"
    },
    {
        "name": "Meta AI Blog",
        "url": "https://about.fb.com/news/category/technology/artificial-intelligence/feed/",
        "tier": "official"
    },
    # 垂直权威媒体与前沿报道
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "tier": "media"
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "tier": "media"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "tier": "media"
    },
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "tier": "media"
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "tier": "media"
    }
]


def clean_html(text: str) -> str:
    """清理 HTML 标签和多余空白"""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_date(date_str: str) -> Optional[datetime]:
    """多格式日期解析"""
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass
    
    # ISO 8601 格式回退
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str.strip().replace("Z", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            continue
    return None


class OfficialRSSFetcher(BaseFetcher):
    """
    抓取顶级大厂实验室与权威垂直科技媒体的官方 RSS/Atom 源
    高信噪比、零 API Key 依赖、100% 官方一手
    """

    def __init__(self, hours_back: int = 36):
        super().__init__()
        self.hours_back = hours_back
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AI-News-Collector/3.0"
        }

    def _fetch_single_feed(self, feed_info: Dict[str, str], cutoff_time: datetime) -> List[ArticleItem]:
        items: List[ArticleItem] = []
        feed_name = feed_info["name"]
        feed_url = feed_info["url"]

        try:
            if USE_FEEDPARSER:
                feed = feedparser.parse(feed_url, request_headers=self.headers)
                for entry in feed.entries[:10]:
                    title = clean_html(getattr(entry, "title", ""))
                    link = getattr(entry, "link", "")
                    summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
                    published_str = getattr(entry, "published", "") or getattr(entry, "updated", "")
                    
                    if not title or not link:
                        continue

                    pub_dt = parse_date(published_str)
                    if pub_dt and pub_dt < cutoff_time:
                        continue

                    items.append(ArticleItem(
                        title=title,
                        url=link,
                        source=feed_name,
                        description=summary[:500],
                        published_date=pub_dt.isoformat() if pub_dt else "recent"
                    ))
            else:
                resp = requests.get(feed_url, headers=self.headers, timeout=10)
                if resp.status_code != 200:
                    return items

                root = ET.fromstring(resp.content)
                # RSS 2.0 channel/item
                for item in root.findall(".//item")[:10]:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    desc_elem = item.find("description")
                    date_elem = item.find("pubDate")

                    title = clean_html(title_elem.text) if title_elem is not None and title_elem.text else ""
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    desc = clean_html(desc_elem.text) if desc_elem is not None and desc_elem.text else ""
                    pub_str = date_elem.text.strip() if date_elem is not None and date_elem.text else ""

                    if not title or not link:
                        continue

                    pub_dt = parse_date(pub_str)
                    if pub_dt and pub_dt < cutoff_time:
                        continue

                    items.append(ArticleItem(
                        title=title,
                        url=link,
                        source=feed_name,
                        description=desc[:500],
                        published_date=pub_dt.isoformat() if pub_dt else "recent"
                    ))

                # Atom entry
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall(".//atom:entry", ns)[:10] or root.findall(".//entry")[:10]:
                    title_elem = entry.find("atom:title", ns) or entry.find("title")
                    link_elem = entry.find("atom:link", ns) or entry.find("link")
                    summary_elem = entry.find("atom:summary", ns) or entry.find("summary") or entry.find("atom:content", ns) or entry.find("content")
                    updated_elem = entry.find("atom:updated", ns) or entry.find("updated") or entry.find("atom:published", ns) or entry.find("published")

                    title = clean_html(title_elem.text) if title_elem is not None and title_elem.text else ""
                    link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    summary = clean_html(summary_elem.text) if summary_elem is not None and summary_elem.text else ""
                    pub_str = updated_elem.text.strip() if updated_elem is not None and updated_elem.text else ""

                    if not title or not link:
                        continue

                    pub_dt = parse_date(pub_str)
                    if pub_dt and pub_dt < cutoff_time:
                        continue

                    items.append(ArticleItem(
                        title=title,
                        url=link,
                        source=feed_name,
                        description=summary[:500],
                        published_date=pub_dt.isoformat() if pub_dt else "recent"
                    ))

        except Exception as e:
            # 单个源失败不阻断整体流程
            # print(f"[DEBUG] RSS {feed_name} 请求略过: {e}")
            pass

        return items

    def fetch(self) -> List[ArticleItem]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.hours_back)
        all_articles: List[ArticleItem] = []
        seen_urls = set()

        for feed_info in OFFICIAL_AI_FEEDS:
            feed_items = self._fetch_single_feed(feed_info, cutoff_time)
            for item in feed_items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    all_articles.append(item)

        print(f"[INFO] 官方RSS源抓取完毕，共捕获 {len(all_articles)} 篇一手资讯")
        return all_articles
