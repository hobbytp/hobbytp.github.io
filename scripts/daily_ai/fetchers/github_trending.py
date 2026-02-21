import requests
from datetime import datetime
from typing import List
from scripts.daily_ai.models import GitHubProjectItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config


class GitHubTrendingFetcher(BaseFetcher):
    """获取 GitHub Trending AI 项目并按 stars-per-day 增速排序"""

    def __init__(self, topics: List[str] = None):
        super().__init__()
        self.topics = topics or [
            'artificial-intelligence',
            'machine-learning',
            'llm',
            'generative-ai',
        ]

    def _make_headers(self, authenticated: bool = True) -> dict:
        h = {'Accept': 'application/vnd.github.v3+json'}
        if authenticated and env_config.GITHUB_TOKEN:
            h['Authorization'] = f'token {env_config.GITHUB_TOKEN}'
        return h

    def fetch(self, per_topic: int = 20, limit: int = 10) -> List[GitHubProjectItem]:
        # 首先尝试认证模式，遇到 401 时降级为匿名模式
        use_auth = bool(env_config.GITHUB_TOKEN)

        all_items: dict = {}  # keyed by html_url to deduplicate

        for topic in self.topics:
            url = (
                f"https://api.github.com/search/repositories"
                f"?q=topic:{topic}&sort=stars&order=desc&per_page={per_topic}"
            )
            try:
                response = requests.get(url, headers=self._make_headers(use_auth), timeout=15)

                # Token expired / invalid → retry without auth, and stay anonymous for rest
                if response.status_code == 401 and use_auth:
                    print("[WARNING] GitHub Token 无效 (401)，降级为匿名模式")
                    use_auth = False
                    response = requests.get(url, headers=self._make_headers(False), timeout=15)

                if response.status_code == 403:
                    print("[WARNING] GitHub API 限流，停止后续 topic 查询")
                    break
                if response.status_code != 200:
                    print(f"[WARNING] GitHub topic={topic} 返回 {response.status_code}")
                    continue

                for item in response.json().get('items', []):
                    html_url = item.get('html_url', '')
                    if not html_url or html_url in all_items:
                        continue

                    description = item.get('description') or ''
                    stars_count = item.get('stargazers_count', 0)
                    if stars_count < 10 or len(description) < 5:
                        continue

                    # 计算每天平均获星速度
                    try:
                        created_at = datetime.strptime(
                            item['created_at'], '%Y-%m-%dT%H:%M:%SZ'
                        )
                        days_alive = max(1, (datetime.utcnow() - created_at).days)
                    except (KeyError, ValueError):
                        days_alive = 999

                    stars_per_day = stars_count / days_alive

                    all_items[html_url] = GitHubProjectItem(
                        title=item.get('name', 'Unknown'),
                        url=html_url,
                        source='GitHub',
                        description=description,
                        stars=stars_count,
                        stars_per_day=stars_per_day,
                        language=item.get('language') or 'Unknown',
                        published_date=item.get('created_at', ''),
                    )

            except Exception as e:
                print(f"[ERROR] GitHub 抓取 topic={topic} 失败: {e}")

        # 按每日增速倒序排序，返回前 limit 名
        projects = sorted(all_items.values(), key=lambda x: x.stars_per_day, reverse=True)
        print(f"[INFO] GitHub: 合计 {len(all_items)} 项目，返回前 {limit} 名")
        return projects[:limit]
