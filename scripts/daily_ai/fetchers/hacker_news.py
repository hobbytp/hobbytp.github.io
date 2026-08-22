import requests
import html
import re
from datetime import datetime, timedelta, timezone
from typing import List

from scripts.daily_ai.models import ArticleItem
from scripts.daily_ai.fetchers.base import BaseFetcher


def clean_text(text: str) -> str:
    """清理 HTML 实体、链接与多余空白"""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class HackerNewsFetcher(BaseFetcher):
    """
    抓取 Hacker News (HN) 过去指定时间窗内的高赞 AI 话题与开源发布 (Show HN)
    基于官方 Algolia 搜索引擎接口，硬核时间窗与高赞阈值过滤
    """

    def __init__(self, min_points: int = 15, hours_back: int = 48):
        super().__init__()
        self.min_points = min_points
        self.hours_back = hours_back

    def fetch(self, limit: int = 10) -> List[ArticleItem]:
        items: List[ArticleItem] = []
        try:
            cutoff_timestamp = int((datetime.now(timezone.utc) - timedelta(hours=self.hours_back)).timestamp())
            
            queries = ['AI', 'LLM', 'Agent', 'OpenAI', 'Claude', 'DeepSeek']
            seen_story_ids = set()

            for q in queries:
                url = f"https://hn.algolia.com/api/v1/search?query={q}&numericFilters=created_at_i>{cutoff_timestamp},points>={self.min_points}&hitsPerPage=15"
                resp = requests.get(url, timeout=12)
                if resp.status_code != 200:
                    continue

                data = resp.json()
                for hit in data.get("hits", []):
                    object_id = hit.get("objectID")
                    if not object_id or object_id in seen_story_ids:
                        continue

                    title = clean_text(hit.get("title") or "")
                    points = hit.get("points") or 0
                    num_comments = hit.get("num_comments") or 0
                    created_at = hit.get("created_at") or ""

                    # 硬过滤：低于最小点赞数直接剔除
                    if points < self.min_points:
                        continue

                    # 过滤纯求职或无关招聘内容
                    if any(bad_kw in title.lower() for bad_kw in ["ask hn: who is hiring", "freelancer", "seeking", "hiring"]):
                        continue

                    seen_story_ids.add(object_id)
                    story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"

                    raw_snippet = hit.get("story_text") or ""
                    cleaned_snippet = clean_text(raw_snippet)[:120] if raw_snippet else ""

                    description = f"HN 极客热度: 🔺{points} Points | 💬{num_comments} 讨论"
                    if cleaned_snippet:
                        description += f" | {cleaned_snippet}"

                    item = ArticleItem(
                        title=title,
                        url=story_url,
                        source="Hacker News",
                        description=description,
                        published_date=created_at
                    )
                    item.quality_score = 5.0 + min(3.0, points / 20.0) + min(2.0, num_comments / 10.0)
                    items.append(item)


            # 按热度评分降序排列
            items = sorted(items, key=lambda x: x.quality_score, reverse=True)
            print(f"[INFO] Hacker News: 在过去 {self.hours_back}h 且 Points>={self.min_points} 条件下精选 {len(items)} 条极客热议")
        except Exception as e:
            print(f"[ERROR] Hacker News 抓取异常: {e}")

        return items[:limit]


