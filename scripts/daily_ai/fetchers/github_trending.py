
import requests
import re
from datetime import datetime, timedelta, timezone
from typing import List
from scripts.daily_ai.models import GitHubProjectItem
from scripts.daily_ai.fetchers.base import BaseFetcher
from scripts.daily_ai.config.env_config import env_config

# 低质与非代码项目黑名单关键词
EXCLUDED_PATTERNS = [
    r'awesome[-_]',
    r'tutorial',
    r'interview',
    r'course',
    r'roadmap',
    r'cheatsheet',
    r'cheat[-_]sheet',
    r'learning[-_]path',
    r'resources',
    r'collection',
    r'must[-_]read'
]


class GitHubTrendingFetcher(BaseFetcher):
    """获取 GitHub Trending AI 项目 (侧重最近创建并爆发增长的高价值极客开源工具)"""

    def __init__(self, topics: List[str] = None):
        super().__init__()
        self.topics = topics or [
            'llm',
            'agent',
            'generative-ai',
            'rag',
            'inference',
            'multi-agent',
            'vision-language-model',
            'ai-tools'
        ]

    def _make_headers(self, authenticated: bool = True) -> dict:
        h = {'Accept': 'application/vnd.github.v3+json'}
        if authenticated and env_config.GITHUB_TOKEN:
            h['Authorization'] = f'token {env_config.GITHUB_TOKEN}'
        return h

    def _is_valid_project(self, name: str, description: str) -> bool:
        combined = f"{name} {description}".lower()
        for pattern in EXCLUDED_PATTERNS:
            if re.search(pattern, combined):
                return False
        return True

    def fetch(self, per_topic: int = 30, limit: int = 10) -> List[GitHubProjectItem]:
        use_auth = bool(env_config.GITHUB_TOKEN)
        all_items: dict = {}
        
        # 关注最近 14 天内创建的项目，确保是真正新鲜的工具
        date_threshold = (datetime.now(timezone.utc) - timedelta(days=14)).strftime('%Y-%m-%d')

        for topic in self.topics:
            url = (
                f"https://api.github.com/search/repositories"
                f"?q=topic:{topic}+created:>{date_threshold}&sort=stars&order=desc&per_page={per_topic}"
            )
            try:
                response = requests.get(url, headers=self._make_headers(use_auth), timeout=15)

                if response.status_code == 401 and use_auth:
                    print("[WARNING] GitHub Token 无效 (401)，降级为匿名模式")
                    use_auth = False
                    response = requests.get(url, headers=self._make_headers(False), timeout=15)

                if response.status_code == 403:
                    print("[WARNING] GitHub API 限流，停止后续 topic 查询")
                    break
                if response.status_code != 200:
                    continue

                for item in response.json().get('items', []):
                    html_url = item.get('html_url', '')
                    name = item.get('name', '')
                    description = item.get('description') or ''
                    stars_count = item.get('stargazers_count', 0)

                    if not html_url or html_url in all_items:
                        continue

                    # 基础质量门槛：描述清晰，过滤课程与资料集合
                    if stars_count < 10 or len(description) < 10:
                        continue

                    if not self._is_valid_project(name, description):
                        continue

                    # 计算日均获星速率
                    try:
                        created_at = datetime.strptime(
                            item['created_at'], '%Y-%m-%dT%H:%M:%SZ'
                        ).replace(tzinfo=timezone.utc)
                        days_alive = max(0.5, (datetime.now(timezone.utc) - created_at).total_seconds() / 86400)
                    except (KeyError, ValueError):
                        days_alive = 1.0

                    stars_per_day = stars_count / days_alive

                    all_items[html_url] = GitHubProjectItem(
                        title=name,
                        url=html_url,
                        source='GitHub',
                        description=description,
                        stars=stars_count,
                        stars_per_day=round(stars_per_day, 1),
                        language=item.get('language') or 'Unknown',
                        published_date=item.get('created_at', ''),
                    )

            except Exception as e:
                print(f"[ERROR] GitHub 抓取 topic={topic} 失败: {e}")

        # 按每日获星增速倒序排序，返回前 limit 名
        projects = sorted(all_items.values(), key=lambda x: x.stars_per_day, reverse=True)
        print(f"[INFO] GitHub 筛选完成: 从 {len(all_items)} 个候选项目中精选 Top {len(projects[:limit])}")
        return projects[:limit]

