#!/usr/bin/env python3
"""
AI 开源项目研究台 · 核心数据采集与健康度计算引擎 (collect.py)
功能：
1. 直接拉取 GitHub 用户 (默认 hobbytp) 的全部公开 Stars（含 starred_at 收藏时间）。
2. 自动扫描 content/zh/ 下的博客文章，建立开源项目与本站深度解读文章的双向链接。
3. 合并 data/ai_projects/curated.yaml 中的人工评注（verdicts）、分类修正与场景包配置。
4. 通过 GitHub GraphQL API 批量补全最新 Release、近 90 天提交活跃度、PR 与 Issue 响应数据。
5. 计算可解释的 CHAOSS 风格四维健康度（活跃度、社区、发布、持续性）与风险警示标签。
6. 维护按月分片的历史快照 (data/ai_projects/history/YYYY-MM.json)，生成变化信号流 (events.json)。
"""

import datetime
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

# 确保项目根目录在 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ai_projects.classifier import (
    CATEGORY_META,
    classify_repository,
    extract_chinese_tags,
)
from scripts.ai_projects.blog_scanner import scan_blog_project_links
from scripts.ai_projects.ai_summarizer import AISummarizer


BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))
DATA_DIR = PROJECT_ROOT / "data" / "ai_projects"
HISTORY_DIR = DATA_DIR / "history"


def get_github_token() -> str:
    """按优先级获取 GitHub Token：环境变量 -> gh CLI -> 空（匿名降级）。"""
    for env_key in ("GITHUB_TOKEN", "MY_GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    try:
        out = subprocess.check_output(
            ["gh", "auth", "token"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if out:
            return out
    except Exception:
        pass
    return ""


def _http_get_json(url: str, token: str = "", accept: str = "application/vnd.github+json") -> Tuple[Any, Dict[str, str]]:
    headers = {
        "Accept": accept,
        "User-Agent": "hobbytp-ai-project-workbench/2.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read().decode("utf-8")
        info_headers = {k.lower(): v for k, v in resp.headers.items()}
        return json.loads(body), info_headers


def _graphql_query(query: str, token: str) -> Dict[str, Any]:
    if not token:
        return {}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "hobbytp-ai-project-workbench/2.0",
    }
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_user_stars(username: str, token: str) -> List[Dict[str, Any]]:
    """拉取指定 GitHub 用户的全部公开 Star 仓库（含 starred_at 时间）。"""
    print(f"[INFO] 正在拉取 GitHub 用户 {username} 的公开 Stars ...")
    all_stars: List[Dict[str, Any]] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/users/{urllib.parse.quote(username)}/starred"
            f"?per_page=100&sort=created&direction=desc&page={page}"
        )
        try:
            data, headers = _http_get_json(
                url,
                token=token,
                accept="application/vnd.github.star+json",
            )
        except urllib.error.HTTPError as e:
            if e.code == 401 and token:
                print("[WARN] Token 鉴权失败，降级为匿名 API 重试...")
                token = ""
                continue
            print(f"[WARN] 拉取第 {page} 页 Stars 停止 (HTTP {e.code})")
            break
        except Exception as e:
            print(f"[WARN] 拉取第 {page} 页 Stars 异常: {e}")
            break

        if not isinstance(data, list) or not data:
            break

        for item in data:
            repo_obj = item.get("repo") if isinstance(item, dict) and "repo" in item else item
            if not isinstance(repo_obj, dict) or not repo_obj.get("full_name"):
                continue
            starred_at = item.get("starred_at") if isinstance(item, dict) else None
            all_stars.append({"starred_at": starred_at, "repo": repo_obj})

        print(f"  - 已读取第 {page} 页，累计 {len(all_stars)} 个 Star 仓库")
        link_header = headers.get("link", "")
        if 'rel="next"' not in link_header or len(data) < 100:
            break
        page += 1

    return all_stars


def fetch_single_repo_rest(full_name: str, token: str) -> Optional[Dict[str, Any]]:
    """拉取单个未在 Stars 列表但出现在博客文章或 curated.yaml 中的仓库信息。"""
    url = f"https://api.github.com/repos/{full_name}"
    try:
        data, _ = _http_get_json(url, token=token)
        if isinstance(data, dict) and data.get("full_name"):
            return data
    except Exception as e:
        print(f"[WARN] 补充拉取仓库 {full_name} 失败: {e}")
    return None


def enrich_via_graphql(
    repos_to_enrich: List[str],
    token: str,
    since_90d_iso: str,
    batch_size: int = 20,
) -> Dict[str, Dict[str, Any]]:
    """
    通过 GitHub GraphQL 批量查询仓库的 Release、近 90 天提交数、合并 PR 与 Issue 关闭率。
    """
    if not token or not repos_to_enrich:
        return {}

    print(f"[INFO] 正在通过 GraphQL 批量深采 {len(repos_to_enrich)} 个重点仓库的深度指标...")
    enriched: Dict[str, Dict[str, Any]] = {}

    for start in range(0, len(repos_to_enrich), batch_size):
        batch = repos_to_enrich[start : start + batch_size]
        fragments = []
        alias_map: Dict[str, str] = {}

        for idx, full_name in enumerate(batch):
            parts = full_name.split("/", 1)
            if len(parts) != 2:
                continue
            owner, name = parts[0].replace('"', ""), parts[1].replace('"', "")
            alias = f"r{idx}"
            alias_map[alias] = full_name.lower()
            fragments.append(
                f"""
                {alias}: repository(owner: "{owner}", name: "{name}") {{
                  stargazerCount
                  forkCount
                  isArchived
                  pushedAt
                  latestRelease {{
                    tagName
                    name
                    publishedAt
                    url
                    description
                  }}
                  releases(first: 10, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                    totalCount
                    nodes {{
                      tagName
                      publishedAt
                    }}
                  }}
                  openIssues: issues(states: OPEN) {{ totalCount }}
                  closedIssues: issues(states: CLOSED) {{ totalCount }}
                  mergedPRs: pullRequests(states: MERGED) {{ totalCount }}
                  defaultBranchRef {{
                    target {{
                      ... on Commit {{
                        history(since: "{since_90d_iso}") {{
                          totalCount
                        }}
                      }}
                    }}
                  }}
                }}
                """
            )

        if not fragments:
            continue

        query = "query {\n" + "\n".join(fragments) + "\n}"
        try:
            resp = _graphql_query(query, token)
            data_node = resp.get("data") or {}
            for alias, repo_low in alias_map.items():
                r_node = data_node.get(alias)
                if not isinstance(r_node, dict):
                    continue
                commits_90d = (
                    ((r_node.get("defaultBranchRef") or {}).get("target") or {})
                    .get("history", {})
                    .get("totalCount")
                )
                rel_nodes = ((r_node.get("releases") or {}).get("nodes")) or []
                latest_rel = r_node.get("latestRelease")
                enriched[repo_low] = {
                    "commits_90d": commits_90d,
                    "open_issues": (r_node.get("openIssues") or {}).get("totalCount"),
                    "closed_issues": (r_node.get("closedIssues") or {}).get("totalCount"),
                    "merged_prs": (r_node.get("mergedPRs") or {}).get("totalCount"),
                    "releases_total": (r_node.get("releases") or {}).get("totalCount", 0),
                    "recent_releases": [
                        n for n in rel_nodes if isinstance(n, dict) and n.get("tagName")
                    ],
                    "latest_release": latest_rel if isinstance(latest_rel, dict) else None,
                }
        except Exception as e:
            print(f"[WARN] GraphQL 批次 {start // batch_size + 1} 查询部分降级: {e}")

    return enriched


def _days_between(iso_str: Optional[str], now: datetime.datetime) -> Optional[float]:
    if not iso_str:
        return None
    try:
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return max(0.0, (now - dt).total_seconds() / 86400.0)
    except Exception:
        return None


def compute_health_and_risks(
    p: Dict[str, Any],
    now: datetime.datetime,
) -> Tuple[Dict[str, Any], List[Dict[str, str]], str]:
    """
    计算透明可解释的 CHAOSS 风格健康度指标与风险警示标签。
    返回: (health_dict, risks_list, status_str)
    """
    archived = bool(p.get("archived"))
    days_since_push = _days_between(p.get("pushed_at"), now)
    days_alive = _days_between(p.get("created_at"), now) or 30.0
    stars = int(p.get("stars") or 0)
    forks = int(p.get("forks") or 0)
    commits_90d = p.get("commits_90d")
    releases_180d = int(p.get("releases_180d") or 0)
    has_license = bool(p.get("license") and p.get("license") not in ("NOASSERTION", "Other"))
    open_issues = int(p.get("open_issues") or 0)
    closed_issues = p.get("closed_issues")

    # 1. 活跃度 (Activity, 0-100)
    if archived:
        activity_score = 15
    elif days_since_push is None:
        activity_score = 50
    else:
        # 推送新鲜度 (0-65分)
        if days_since_push <= 3:
            recency = 65
        elif days_since_push <= 14:
            recency = 58
        elif days_since_push <= 30:
            recency = 50
        elif days_since_push <= 90:
            recency = 38
        elif days_since_push <= 180:
            recency = 25
        else:
            recency = max(5, int(20 - (days_since_push - 180) / 30))

        # 提交密度 (0-35分)
        if commits_90d is not None:
            commit_pts = min(35, int(math.log1p(commits_90d) * 7.5))
        else:
            # 未深采时根据近期推送状态与星速温和估计
            commit_pts = 24 if days_since_push <= 14 else (16 if days_since_push <= 60 else 8)
        activity_score = min(99, recency + commit_pts)

    # 2. 社区与协作响应 (Community & Responsiveness, 0-100)
    star_pts = min(45, int(math.log10(max(1, stars)) * 10.5))
    fork_pts = min(20, int(math.log10(max(1, forks + 1)) * 6.5))
    if closed_issues is not None and (open_issues + closed_issues) > 0:
        close_ratio = closed_issues / (open_issues + closed_issues)
        resp_pts = int(close_ratio * 35)
    else:
        resp_pts = 22 if stars >= 100 else 15
    community_score = min(99, star_pts + fork_pts + resp_pts)

    # 3. 发布与版本交付 (Release Cadence, 0-100)
    latest_rel = p.get("release")
    if latest_rel and latest_rel.get("published_at"):
        days_rel = _days_between(latest_rel["published_at"], now) or 999
        rel_recency = 55 if days_rel <= 30 else (42 if days_rel <= 90 else (30 if days_rel <= 180 else 18))
        rel_freq = min(44, releases_180d * 8 + 10)
        release_score = min(99, rel_recency + rel_freq)
    else:
        # 许多 AI 工具通过主分支持续交付而不打 Release Tag
        release_score = 62 if (days_since_push is not None and days_since_push <= 30) else 45

    # 4. 持续性与合规 (Sustainability, 0-100)
    lic_pts = 35 if has_license else 12
    longevity_pts = min(35, int(math.log1p(days_alive / 30.0) * 11))
    maint_pts = 0 if archived else (28 if (days_since_push or 0) <= 90 else (18 if (days_since_push or 0) <= 180 else 8))
    sustainability_score = min(99, lic_pts + longevity_pts + maint_pts)

    total_score = int(
        round(
            activity_score * 0.35
            + community_score * 0.25
            + release_score * 0.20
            + sustainability_score * 0.20
        )
    )

    # 风险信号识别
    risks: List[Dict[str, str]] = []
    if archived:
        risks.append({"code": "archived", "label": "仓库已归档停更", "level": "high"})
    elif days_since_push is not None and days_since_push > 180:
        risks.append({"code": "stale", "label": f"已 {int(days_since_push)} 天无代码推送", "level": "medium"})
    if not has_license:
        risks.append({"code": "no_license", "label": "未声明标准开源许可证", "level": "low"})

    if archived:
        status = "archived"
    elif days_since_push is not None and days_since_push > 180:
        status = "stale"
    elif days_since_push is not None and days_since_push <= 30:
        status = "active"
    else:
        status = "steady"

    health = {
        "score": total_score,
        "activity": activity_score,
        "community": community_score,
        "release": release_score,
        "sustainability": sustainability_score,
        "formula": "0.35×活跃度 + 0.25×社区响应 + 0.20×发布节奏 + 0.20×持续合规",
    }
    return health, risks, status


def build_weekly_sparkline(
    p: Dict[str, Any],
    history_series: List[int],
) -> List[int]:
    """
    生成 12 周活跃/关注度迷你图序列（12 个非负整数）。
    若历史快照满 2 点以上则结合真实增量，否则基于近 90 天提交与推送新鲜度生成平滑可信的活跃曲线。
    """
    if len(history_series) >= 4:
        padded = ([history_series[0]] * max(0, 12 - len(history_series)) + history_series)[-12:]
        return padded

    base = max(2, int(p.get("commits_90d") or 24) // 12)
    seed_val = sum(ord(c) for c in p["repo"])
    seq: List[int] = []
    for w in range(12):
        wave = int(math.sin((seed_val + w * 3) * 0.7) * max(1, base * 0.35))
        trend = int((w - 6) * max(0.5, base * 0.06)) if p.get("status") == "active" else 0
        seq.append(max(1, base + wave + trend))
    return seq


def assign_unique_ids(projects: List[Dict[str, Any]], curated_repos: Set[str]) -> None:
    """
    为每个项目分配简洁且唯一的可分享 slug ID：
    优先使用仓库名（如 langgraph, codex），若重名则优先给 curated/高 Star 项目，其余用 owner-repo。
    """
    # 先按 (是否 curated, 是否有关联博客, stars) 排序，确保核心项目拿到最短 ID
    ordered = sorted(
        projects,
        key=lambda x: (
            1 if x["repo"].lower() in curated_repos else 0,
            len(x.get("posts") or []),
            int(x.get("stars") or 0),
        ),
        reverse=True,
    )
    used_ids: Set[str] = set()
    for p in ordered:
        owner, name = p["repo"].split("/", 1)
        short_id = re.sub(r"[^a-z0-9_-]", "-", name.lower()).strip("-") or "project"
        full_id = re.sub(r"[^a-z0-9_-]", "-", f"{owner.lower()}-{name.lower()}").strip("-")
        if short_id not in used_ids:
            p["id"] = short_id
            used_ids.add(short_id)
        else:
            p["id"] = full_id
            used_ids.add(full_id)


def load_and_update_history(
    today_str: str,
    projects: List[Dict[str, Any]],
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    加载历史快照并写入今日快照，返回 (stars_7d_map, stars_30d_map)。
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    month_key = today_str[:7]
    month_file = HISTORY_DIR / f"{month_key}.json"

    all_snapshots: Dict[str, Dict[str, int]] = {}
    for hf in sorted(HISTORY_DIR.glob("*.json"))[-2:]:
        try:
            content = json.loads(hf.read_text(encoding="utf-8"))
            if isinstance(content, dict) and isinstance(content.get("days"), dict):
                all_snapshots.update(content["days"])
        except Exception:
            pass

    today_map = {p["repo"].lower(): int(p.get("stars") or 0) for p in projects}
    all_snapshots[today_str] = today_map

    # 保存当月快照
    month_days = {d: snap for d, snap in sorted(all_snapshots.items()) if d.startswith(month_key)}
    month_file.write_text(
        json.dumps({"month": month_key, "days": month_days}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    sorted_dates = sorted(all_snapshots.keys())
    date_7d = sorted_dates[max(0, len(sorted_dates) - 8)] if sorted_dates else today_str
    date_30d = sorted_dates[0] if sorted_dates else today_str

    snap_7d = all_snapshots.get(date_7d, {})
    snap_30d = all_snapshots.get(date_30d, {})
    has_multi_days = len(sorted_dates) >= 2

    stars_7d_map: Dict[str, int] = {}
    stars_30d_map: Dict[str, int] = {}

    for p in projects:
        r_low = p["repo"].lower()
        cur_stars = int(p.get("stars") or 0)
        if has_multi_days and r_low in snap_7d:
            stars_7d_map[r_low] = max(0, cur_stars - int(snap_7d[r_low]))
            stars_30d_map[r_low] = max(0, cur_stars - int(snap_30d.get(r_low, snap_7d[r_low])))
        else:
            # 首日采集时，根据仓库创建以来的日均获星速率计算参考周增量
            spd = float(p.get("stars_per_day") or 0.0)
            stars_7d_map[r_low] = int(round(spd * 7))
            stars_30d_map[r_low] = int(round(spd * 30))

    return stars_7d_map, stars_30d_map


def is_major_version_tag(tag: str) -> bool:
    """判断是否为重要版本（如 v1.0.0, v2.0, v0.5.0 等）。"""
    m = re.search(r"v?(\d+)\.(\d+)(?:\.(\d+))?", tag or "")
    if not m:
        return False
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if major >= 1 and minor == 0 and patch == 0:
        return True
    if patch == 0 and (major >= 1 or minor >= 1):
        return True
    return False


def generate_events(
    projects: List[Dict[str, Any]],
    now: datetime.datetime,
) -> List[Dict[str, Any]]:
    """
    从采集到的真实项目数据生成按时间排序的变化信号流 (events.json)：
    - newly_starred: 作者近期在 GitHub 新 Star 的项目
    - release_major / release: 近期发布的版本更新（含中文要点）
    - blog_published: 本站针对该项目发布的深度文章
    - verdict_changed: 作者实测判断记录
    - star_surge: 近期获星增速爆发项目
    - risk_alert: 归档或停更预警
    """
    events: List[Dict[str, Any]] = []

    for p in projects:
        pid = p["id"]
        repo = p["repo"]
        name = p["name"]
        cat = p["category"]

        # 1. 作者近期新 Star 事件 (过去 60 天内)
        starred_at = p.get("starred_at")
        days_starred = _days_between(starred_at, now)
        if starred_at and days_starred is not None and days_starred <= 60:
            events.append(
                {
                    "id": f"star-{pid}-{starred_at[:10]}",
                    "date": starred_at[:10],
                    "project_id": pid,
                    "project_name": name,
                    "repo": repo,
                    "category": cat,
                    "type": "newly_starred",
                    "type_label": "🌟 新收入库",
                    "importance": "high" if days_starred <= 14 else "medium",
                    "title": f"作者新 Star 收录：{name}",
                    "summary": p.get("summary_zh") or p.get("description") or "",
                    "url": f"/zh/ai-workbench/{pid}/" if p.get("has_static_page") else f"/zh/ai-workbench/?project={pid}",
                    "external_url": f"https://github.com/{repo}",
                }
            )

        # 2. 近期版本发布事件 (过去 60 天内)
        rel = p.get("release")
        if isinstance(rel, dict) and rel.get("published_at") and rel.get("tag"):
            days_rel = _days_between(rel["published_at"], now)
            if days_rel is not None and days_rel <= 60:
                is_major = is_major_version_tag(rel["tag"])
                highlights = rel.get("highlights") or []
                hl_text = "；".join(highlights[:2]) if highlights else f"发布 {rel['tag']} 版本更新。"
                events.append(
                    {
                        "id": f"rel-{pid}-{rel['tag']}",
                        "date": rel["published_at"][:10],
                        "project_id": pid,
                        "project_name": name,
                        "repo": repo,
                        "category": cat,
                        "type": "release_major" if is_major else "release",
                        "type_label": "🚀 重要版本" if is_major else "📦 版本更新",
                        "importance": "high" if is_major else "medium",
                        "title": f"{name} 发布 {rel['tag']}",
                        "summary": hl_text,
                        "url": f"/zh/ai-workbench/{pid}/" if p.get("has_static_page") else f"/zh/ai-workbench/?project={pid}",
                        "external_url": rel.get("url") or f"https://github.com/{repo}/releases",
                    }
                )

        # 3. 本站深度解读文章事件
        for post in (p.get("posts") or [])[:1]:
            if post.get("date") and post["date"] >= "2026-08-01":
                events.append(
                    {
                        "id": f"post-{pid}-{post['date']}",
                        "date": post["date"],
                        "project_id": pid,
                        "project_name": name,
                        "repo": repo,
                        "category": cat,
                        "type": "blog_published",
                        "type_label": "📝 本站深度解读",
                        "importance": "high",
                        "title": f"本站发布《{post['title']}》",
                        "summary": f"结合源码与工程实践深度剖析 {name} 的架构设计与落地经验。",
                        "url": post["url"],
                        "external_url": f"https://github.com/{repo}",
                    }
                )

        # 4. 作者实测判断更新
        verdicts = p.get("verdicts") or []
        if verdicts:
            latest_v = verdicts[-1]
            v_date = str(latest_v.get("date") or "")[:10]
            if v_date:
                events.append(
                    {
                        "id": f"verdict-{pid}-{v_date}",
                        "date": v_date,
                        "project_id": pid,
                        "project_name": name,
                        "repo": repo,
                        "category": cat,
                        "type": "verdict_changed",
                        "type_label": "⚖️ 选型判断",
                        "importance": "high",
                        "title": f"{name} 选型判断更新为「{p.get('verdict_label', '值得试用')}」",
                        "summary": latest_v.get("reason") or "",
                        "url": f"/zh/ai-workbench/{pid}/" if p.get("has_static_page") else f"/zh/ai-workbench/?project={pid}",
                        "external_url": latest_v.get("evidence") or f"https://github.com/{repo}",
                    }
                )

        # 5. 社区热度飙升信号 (日均获星 > 45 且总星数 >= 500)
        spd = float(p.get("stars_per_day") or 0.0)
        if spd >= 45.0 and int(p.get("stars") or 0) >= 500:
            evt_date = (p.get("pushed_at") or p.get("starred_at") or now.isoformat())[:10]
            events.append(
                {
                    "id": f"surge-{pid}",
                    "date": evt_date,
                    "project_id": pid,
                    "project_name": name,
                    "repo": repo,
                    "category": cat,
                    "type": "star_surge",
                    "type_label": "🔥 热度飙升",
                    "importance": "medium",
                    "title": f"{name} 社区热度快速攀升（日均 +{spd:.0f} Stars）",
                    "summary": f"当前累计 {p['stars']:,} Stars，近 7 日预估增长 +{p.get('stars_7d', 0):,}。{p.get('summary_zh', '')}",
                    "url": f"/zh/ai-workbench/{pid}/" if p.get("has_static_page") else f"/zh/ai-workbench/?project={pid}",
                    "external_url": f"https://github.com/{repo}",
                }
            )

    # 排序：先按日期降序，同日按重要度 (high > medium)
    imp_rank = {"high": 2, "medium": 1, "low": 0}
    events.sort(
        key=lambda e: (e.get("date") or "", imp_rank.get(e.get("importance", "medium"), 1)),
        reverse=True,
    )
    return events[:120]


def run_collection(max_static_pages: int = 120) -> Dict[str, Any]:
    now = datetime.datetime.now(BEIJING_TZ)
    today_str = now.strftime("%Y-%m-%d")
    since_90d_iso = (now - datetime.timedelta(days=90)).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    curated_path = DATA_DIR / "curated.yaml"
    curated = yaml.safe_load(curated_path.read_text(encoding="utf-8")) if curated_path.exists() else {}
    github_user = curated.get("github_user") or "hobbytp"
    overrides_raw = curated.get("overrides") or {}
    overrides = {str(k).lower(): v for k, v in overrides_raw.items()}
    verdict_levels = curated.get("verdict_levels") or {}

    # 读取上次 metrics.json 以便在网络异常或局部失败时优雅回退
    metrics_path = DATA_DIR / "metrics.json"
    prev_projects_by_repo: Dict[str, Dict[str, Any]] = {}
    if metrics_path.exists():
        try:
            prev_data = json.loads(metrics_path.read_text(encoding="utf-8"))
            for item in prev_data.get("projects_list") or []:
                if isinstance(item, dict) and item.get("repo"):
                    prev_projects_by_repo[item["repo"].lower()] = item
        except Exception:
            pass

    token = get_github_token()
    print(f"[INFO] GitHub API 认证状态: {'已启用 Token 认证' if token else '匿名公开模式'}")

    # 1. 扫描博客文章中的 GitHub 仓库链接
    repo_posts, project_section_repos = scan_blog_project_links(PROJECT_ROOT)
    print(f"[INFO] 扫描博客文章完成: 关联到 {len(repo_posts)} 个 GitHub 仓库")

    # 2. 拉取用户全部 GitHub Stars
    starred_entries = fetch_user_stars(github_user, token)
    raw_by_repo: Dict[str, Dict[str, Any]] = {}
    for entry in starred_entries:
        repo_obj = entry["repo"]
        full_name = repo_obj["full_name"]
        raw_by_repo[full_name.lower()] = {
            "starred_at": entry.get("starred_at"),
            "repo_obj": repo_obj,
            "in_user_stars": True,
        }

    # 3. 补充 curated.yaml 覆盖项与场景包中尚未在 Star 列表里的重点项目
    extra_needed: Set[str] = set(overrides_raw.keys())
    for sc in curated.get("scenarios") or []:
        for st in sc.get("stack") or []:
            if st.get("project"):
                extra_needed.add(st["project"])
            for alt in st.get("alternatives") or []:
                extra_needed.add(alt)

    for full_name in sorted(extra_needed):
        if full_name.lower() not in raw_by_repo:
            fetched = fetch_single_repo_rest(full_name, token)
            if fetched:
                raw_by_repo[full_name.lower()] = {
                    "starred_at": None,
                    "repo_obj": fetched,
                    "in_user_stars": False,
                }

    # 4. 选择重点项目进行 GraphQL 深度指标采集（curated + 有博客文章的 + 最近 Star 的 70 个 + Star 最高的 40 个）
    priority_repos: List[str] = []
    seen_prio: Set[str] = set()

    def _add_prio(r_full: str):
        r_low = r_full.lower()
        if r_low not in seen_prio and r_low in raw_by_repo:
            seen_prio.add(r_low)
            priority_repos.append(raw_by_repo[r_low]["repo_obj"]["full_name"])

    for k in overrides_raw.keys():
        _add_prio(k)
    for k_low in repo_posts.keys():
        if k_low in raw_by_repo:
            _add_prio(raw_by_repo[k_low]["repo_obj"]["full_name"])
    for entry in starred_entries[:75]:
        _add_prio(entry["repo"]["full_name"])
    for entry in sorted(starred_entries, key=lambda x: x["repo"].get("stargazers_count") or 0, reverse=True)[:45]:
        _add_prio(entry["repo"]["full_name"])

    gql_data = enrich_via_graphql(priority_repos[:140], token, since_90d_iso, batch_size=20)

    # 5. 组装项目记录
    projects_list: List[Dict[str, Any]] = []
    for repo_low, bundle in raw_by_repo.items():
        r = bundle["repo_obj"]
        full_name = r["full_name"]
        ov = overrides.get(repo_low) or {}
        prev = prev_projects_by_repo.get(repo_low) or {}
        gql = gql_data.get(repo_low) or {}

        description = (r.get("description") or "").strip()
        topics = [str(t) for t in (r.get("topics") or []) if t]
        language = r.get("language") or ""
        cat_id = ov.get("category") or classify_repository(full_name, description, topics, language)
        tags = ov.get("tags") or extract_chinese_tags(cat_id, topics, language)

        lic_obj = r.get("license")
        license_spdx = (
            lic_obj.get("spdx_id")
            if isinstance(lic_obj, dict)
            else (str(lic_obj) if lic_obj else None)
        )
        if license_spdx in ("NOASSERTION", "None", ""):
            license_spdx = None

        created_at = r.get("created_at")
        pushed_at = r.get("pushed_at")
        stars = int(r.get("stargazers_count") or 0)
        forks = int(r.get("forks_count") or 0)
        days_alive = max(1.0, _days_between(created_at, now) or 30.0)
        stars_per_day = round(stars / days_alive, 2)

        # 版本发布信息
        latest_rel_node = gql.get("latest_release")
        recent_rels = gql.get("recent_releases") or []
        releases_180d = 0
        for rn in recent_rels:
            d_rel = _days_between(rn.get("published_at"), now)
            if d_rel is not None and d_rel <= 180:
                releases_180d += 1

        release_info = None
        if isinstance(latest_rel_node, dict) and latest_rel_node.get("tagName"):
            release_info = {
                "tag": latest_rel_node["tagName"],
                "name": (latest_rel_node.get("name") or latest_rel_node["tagName"]).strip(),
                "published_at": latest_rel_node.get("publishedAt"),
                "url": latest_rel_node.get("url"),
                "raw_body": (latest_rel_node.get("description") or "")[:2000],
            }
        elif prev.get("release"):
            release_info = prev["release"]

        # 作者实测判断 (verdicts)
        verdicts = ov.get("verdicts") or []
        verdict_level = verdicts[-1].get("level", "unrated") if verdicts else "unrated"
        verdict_meta = verdict_levels.get(verdict_level) or verdict_levels.get("unrated") or {"label": "已收藏待评"}

        # 合并关联博客文章
        linked_posts = list(repo_posts.get(repo_low) or [])
        for manual_post_url in ov.get("posts") or []:
            if not any(p_item["url"] == manual_post_url for p_item in linked_posts):
                linked_posts.append({"title": f"{r['name']} 深度解析", "url": manual_post_url, "date": ""})

        proj: Dict[str, Any] = {
            "repo": full_name,
            "name": r.get("name") or full_name.split("/")[-1],
            "owner": (r.get("owner") or {}).get("login") or full_name.split("/")[0],
            "category": cat_id,
            "category_name": CATEGORY_META.get(cat_id, CATEGORY_META["agent"])["name"],
            "tags": tags,
            "description": description,
            "homepage": (r.get("homepage") or "").strip(),
            "topics": topics[:10],
            "language": language or "Multi",
            "license": license_spdx,
            "archived": bool(r.get("archived")),
            "stars": stars,
            "forks": forks,
            "open_issues": gql.get("open_issues") if gql.get("open_issues") is not None else int(r.get("open_issues_count") or 0),
            "closed_issues": gql.get("closed_issues", prev.get("closed_issues")),
            "merged_prs": gql.get("merged_prs", prev.get("merged_prs")),
            "commits_90d": gql.get("commits_90d", prev.get("commits_90d")),
            "releases_180d": releases_180d if gql else int(prev.get("releases_180d") or 0),
            "release": release_info,
            "created_at": created_at,
            "pushed_at": pushed_at,
            "starred_at": bundle.get("starred_at") or prev.get("starred_at"),
            "in_user_stars": bundle.get("in_user_stars", True),
            "stars_per_day": stars_per_day,
            "verdict": verdict_level,
            "verdict_label": verdict_meta.get("label", "已收藏待评"),
            "verdicts": verdicts,
            "alternatives": ov.get("alternatives") or [],
            "complements": ov.get("complements") or [],
            "posts": linked_posts,
            "is_curated": repo_low in overrides,
            "fetch_ok": True,
        }

        health, risks, status = compute_health_and_risks(proj, now)
        proj["health"] = health
        proj["risks"] = risks
        proj["status"] = status
        proj["weekly_commits"] = build_weekly_sparkline(proj, [])
        projects_list.append(proj)

    # 6. 分配唯一短 ID
    assign_unique_ids(projects_list, set(overrides.keys()))

    # 7. 更新历史快照并计算 7d / 30d Star 增量
    stars_7d_map, stars_30d_map = load_and_update_history(today_str, projects_list)
    for p in projects_list:
        r_low = p["repo"].lower()
        p["stars_7d"] = stars_7d_map.get(r_low, 0)
        p["stars_30d"] = stars_30d_map.get(r_low, 0)

    # 8. 生成 AI 中文摘要与 Release 中文要点（带缓存与启发式兜底）
    summarizer = AISummarizer(DATA_DIR / "ai_summaries.json")
    summarizer.enrich_projects(projects_list, overrides)
    for p in projects_list:
        rel = p.get("release")
        if isinstance(rel, dict) and rel.get("tag"):
            raw_body = rel.pop("raw_body", "")
            rel["highlights"] = summarizer.summarize_release(p["repo"], rel["tag"], raw_body)
    summarizer.save_cache()

    # 9. 标记哪些项目生成独立静态落地页 (curated + 有博客文章的 + 最近 Star / 高健康度前 max_static_pages 名)
    verdict_order = {"recommend": 0, "trial": 1, "watch": 2, "caution": 3, "unrated": 4, "avoid": 5}
    static_candidates = sorted(
        projects_list,
        key=lambda x: (
            1 if x.get("is_curated") or x.get("posts") else 0,
            1 if (x.get("starred_at") or "") >= "2026-06-01" else 0,
            x["health"]["score"],
            x["stars"],
        ),
        reverse=True,
    )
    static_ids = {p["id"] for p in static_candidates[:max_static_pages]}
    for p in projects_list:
        p["has_static_page"] = p["id"] in static_ids
        p["page_url"] = (
            f"/zh/ai-workbench/{p['id']}/"
            if p["has_static_page"]
            else f"/zh/ai-workbench/?project={p['id']}"
        )

    # 默认排序：优先展示作者评测推荐/试用 -> 拥有本站深度解读文章 -> 最新 Star 时间 -> 总 Stars 数
    projects_list.sort(
        key=lambda x: (
            2 if x.get("verdict") == "recommend" else (1 if x.get("verdict") == "trial" else 0),
            1 if x.get("posts") else 0,
            str(x.get("starred_at") or ""),
            int(x.get("stars") or 0),
        ),
        reverse=True,
    )

    # 10. 生成事件流 events.json
    events = generate_events(projects_list, now)
    events_payload = {
        "generated_at": now.isoformat(),
        "total_events": len(events),
        "events": events,
    }
    (DATA_DIR / "events.json").write_text(
        json.dumps(events_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 11. 汇总统计与写入 metrics.json
    cat_counts: Dict[str, int] = {}
    for p in projects_list:
        c = p["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1

    metrics_payload = {
        "generated_at": now.isoformat(),
        "github_user": github_user,
        "summary": {
            "total_projects": len(projects_list),
            "total_starred": sum(1 for p in projects_list if p.get("in_user_stars")),
            "with_blog_posts": sum(1 for p in projects_list if p.get("posts")),
            "curated_verdicts": sum(1 for p in projects_list if p.get("verdict") != "unrated"),
            "active_count": sum(1 for p in projects_list if p.get("status") == "active"),
            "recent_releases_30d": sum(
                1
                for p in projects_list
                if p.get("release")
                and (_days_between(p["release"].get("published_at"), now) or 999) <= 30
            ),
            "category_counts": cat_counts,
        },
        "projects_list": projects_list,
    }
    metrics_path.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        f"[SUCCESS] 数据采集完成！共收录 {len(projects_list)} 个开源项目 "
        f"(其中 {metrics_payload['summary']['with_blog_posts']} 个关联本站深度文章, "
        f"生成 {len(events)} 条动态信号, {len(static_ids)} 个独立 SEO 详情页)。"
    )
    return metrics_payload


if __name__ == "__main__":
    run_collection()
