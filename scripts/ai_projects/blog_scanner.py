#!/usr/bin/env python3
"""
扫描博客 content/zh/ 下的文章，自动发现文中引用的 GitHub 开源仓库，
建立「开源项目 <-> 本站深度解读文章」的双向关联。
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


GITHUB_REPO_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    re.I,
)

EXCLUDED_OWNERS = {
    "orgs",
    "topics",
    "features",
    "settings",
    "users",
    "sponsors",
    "login",
    "marketplace",
    "about",
    "pricing",
    "security",
    "enterprise",
    "collections",
    "trending",
    "search",
    "notifications",
    "new",
    "codespaces",
    "copilot",
    "readme",
    "customer-stories",
}

EXCLUDED_REPOS = {
    "hobbytp/hobbytp.github.io",
    "adityatelange/hugo-papermod",
}

# 针对 content/zh/projects/ 下部分仅提项目名或使用短链接的知名项目映射
FILENAME_REPO_HINTS: Dict[str, str] = {
    "langgraph.md": "langchain-ai/langgraph",
    "langchain.md": "langchain-ai/langchain",
    "autogen.md": "microsoft/autogen",
    "storm.md": "stanford-oval/storm",
    "taskmaster.md": "eyaltoledano/claude-task-master",
    "openmanus.md": "FoundationAgents/OpenManus",
    "openevolve.md": "codelion/openevolve",
    "tradingagents.md": "TauricResearch/TradingAgents",
    "deerflow.md": "bytedance/deer-flow",
    "ui-tars-desktop.md": "bytedance/UI-TARS-desktop",
    "agentgateway.md": "agentgateway/agentgateway",
    "openai_codex_cli.md": "openai/codex",
    "skyworkai_deepresearchagent.md": "SkyworkAI/DeepResearchAgent",
    "serena_mcp.md": "oraios/serena",
    "mcp_context7.md": "upstash/context7",
    "graphiti.md": "getzep/graphiti",
    "mem0.md": "mem0ai/mem0",
    "mem0_mcp.md": "mem0ai/mem0",
    "trendradar.md": "sansan0/TrendRadar",
    "ccmanager.md": "kbwo/ccmanager",
    "claude-code-router.md": "musistudio/claude-code-router",
    "gemini_cli_arch.md": "google-gemini/gemini-cli",
    "opencode_arch.md": "sst/opencode",
    "spec-kit.md": "github/spec-kit",
    "spec-workflow-mcp.md": "Pimzino/claude-code-spec-workflow",
    "nanobot.md": "nanobot-ai/nanobot",
    "open_autoglm.md": "zai-org/Open-AutoGLM",
    "nanochat.md": "karpathy/nanochat",
    "llm_council.md": "karpathy/llm-council",
    "qlib_rdagent.md": "microsoft/RD-Agent",
    "fastapi_mcp.md": "tadata-org/fastapi_mcp",
    "windows_mcp.md": "CursorTouch/Windows-MCP",
    "openenv.md": "meta-pytorch/OpenEnv",
}


def _parse_front_matter(text: str) -> Tuple[Dict, str]:
    """提取 Markdown YAML Front Matter 与正文。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
        if not isinstance(meta, dict):
            return {}, parts[2]
        return meta, parts[2]
    except Exception:
        return {}, parts[2]


def _clean_repo(owner: str, repo: str) -> str:
    repo = re.sub(r"\.git$", "", repo.strip(".,;:!?)>]\"'"))
    owner = owner.strip()
    if not owner or not repo:
        return ""
    if owner.lower() in EXCLUDED_OWNERS:
        return ""
    if repo.lower() in ("issues", "pulls", "releases", "discussions", "wiki", "actions", "blob", "tree"):
        return ""
    full = f"{owner}/{repo}"
    if full.lower() in EXCLUDED_REPOS:
        return ""
    return full


def _compute_rel_permalink(content_zh_dir: Path, md_path: Path, meta: Dict) -> str:
    """根据文件路径计算 Hugo 站内链接（默认中文 /zh/...）。"""
    if meta.get("url"):
        u = str(meta["url"]).strip()
        if not u.startswith("/"):
            u = "/" + u
        return u
    rel = md_path.relative_to(content_zh_dir).as_posix()
    if rel.endswith("/_index.md") or rel == "_index.md":
        prefix = rel[: -len("_index.md")].strip("/")
        return f"/zh/{prefix}/" if prefix else "/zh/"
    if rel.endswith(".md"):
        slug_path = rel[:-3].lower()
        return f"/zh/{slug_path}/"
    return f"/zh/{rel}"


def scan_blog_project_links(project_root: Path) -> Tuple[Dict[str, List[Dict[str, str]]], Set[str]]:
    """
    扫描 content/zh/ 下文章（排除 daily_ai 自动日报以保证高相关度），
    返回:
      1. repo_lower -> [{"title": ..., "url": ..., "date": ...}]
      2. 在 content/zh/projects/ 专门立项分析过的仓库集合（canonical case）
    """
    content_zh = project_root / "content" / "zh"
    repo_posts: Dict[str, List[Dict[str, str]]] = {}
    project_section_repos: Set[str] = set()

    if not content_zh.exists():
        return repo_posts, project_section_repos

    for md_path in sorted(content_zh.rglob("*.md")):
        if md_path.name == "_index.md":
            continue
        rel_parts = md_path.relative_to(content_zh).parts
        # 跳过每日 AI 动态简报，只关联专题文章与项目深度解读
        if rel_parts and rel_parts[0] in ("daily_ai", "draft"):
            continue

        try:
            raw = md_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        meta, body = _parse_front_matter(raw)
        if meta.get("draft") is True:
            continue

        title = str(meta.get("title") or md_path.stem).strip()
        date_val = str(meta.get("date") or "")[:10]
        url = _compute_rel_permalink(content_zh, md_path, meta)
        is_projects_dir = bool(rel_parts and rel_parts[0] == "projects")

        found_repos: Set[str] = set()
        # 1. 文件名提示匹配
        fname_low = md_path.name.lower()
        if fname_low in FILENAME_REPO_HINTS:
            hint_repo = FILENAME_REPO_HINTS[fname_low]
            found_repos.add(hint_repo)
            if is_projects_dir:
                project_section_repos.add(hint_repo)

        # 2. 正文 GitHub 链接扫描
        for match in GITHUB_REPO_RE.finditer(raw):
            cleaned = _clean_repo(match.group(1), match.group(2))
            if cleaned:
                found_repos.add(cleaned)
                if is_projects_dir and len(found_repos) <= 3:
                    project_section_repos.add(cleaned)

        for repo in found_repos:
            key = repo.lower()
            entry = {"title": title, "url": url, "date": date_val}
            existing = repo_posts.setdefault(key, [])
            if not any(e["url"] == url for e in existing):
                existing.append(entry)

    # 按日期降序排列每个项目的关联文章
    for key in repo_posts:
        repo_posts[key].sort(key=lambda x: x.get("date", ""), reverse=True)

    return repo_posts, project_section_repos

