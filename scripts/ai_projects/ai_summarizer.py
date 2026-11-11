#!/usr/bin/env python3
"""
开源项目与版本发布 AI 中文摘要生成器（带增量哈希缓存与无密钥规则兜底）。
复用 scripts/daily_ai/generators/ai_client.py 的 AIClient，
当配置有 GEMINI_API_KEY / DASHSCOPE_API_KEY / OPENAI_API_KEY 时调用大模型提炼，
否则自动使用结构化规则提炼，绝不阻塞采集或站点构建。
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from scripts.ai_projects.classifier import build_heuristic_summary


def _content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def extract_release_highlights_heuristic(body: str, tag: str = "") -> List[str]:
    """当未启用 LLM 或 Release Body 较短时，从 Release Notes 中提取关键更新条目。"""
    if not body or not body.strip():
        return [f"发布版本 {tag}，包含常规功能迭代与问题修复。"]

    lines = body.splitlines()
    bullets: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        # 跳过纯链接、纯致谢或签名行
        if line.lower().startswith(("full changelog", "all contributors", "new contributors", "sha256", "---")):
            continue
        if re.match(r"^[-*•]\s+", line) or re.match(r"^\d+\.\s+", line):
            cleaned = re.sub(r"^([-*•]|\d+\.)\s+", "", line)
            # 去掉 PR 链接与多余 @mention
            cleaned = re.sub(r"https?://\S+", "", cleaned)
            cleaned = re.sub(r"\s+by\s+@[A-Za-z0-9_-]+.*", "", cleaned)
            cleaned = re.sub(r"\(#\d+\)", "", cleaned).strip()
            if 8 <= len(cleaned) <= 180:
                bullets.append(cleaned)
        if len(bullets) >= 4:
            break

    if not bullets:
        first_para = re.sub(r"\s+", " ", re.sub(r"[#*`>]", "", body)).strip()
        if first_para:
            bullets.append(first_para[:160])
        else:
            bullets.append(f"发布 {tag} 版本更新。")

    return bullets[:4]


class AISummarizer:
    def __init__(self, cache_path: Path, max_llm_batches_per_run: int = 3):
        self.cache_path = cache_path
        self.max_llm_batches = max_llm_batches_per_run
        self.cache: Dict[str, Any] = self._load_cache()
        self.ai_client = self._init_ai_client()

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data.setdefault("projects", {})
                    data.setdefault("releases", {})
                    return data
            except Exception:
                pass
        return {"version": 1, "projects": {}, "releases": {}}

    def save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _init_ai_client(self):
        try:
            from scripts.daily_ai.generators.ai_client import AIClient
            client = AIClient()
            if client.client or client.bk_client:
                return client
        except Exception:
            pass
        return None

    def enrich_projects(
        self,
        projects: List[Dict[str, Any]],
        overrides: Dict[str, Any],
    ) -> None:
        """
        为项目列表填充 summary_zh, good_for, not_for, summary_source：
        优先级：curated.yaml 人工覆盖 > ai_summaries.json 缓存 > LLM 批量生成 > 启发式规则生成
        """
        pending_llm: List[Dict[str, Any]] = []
        proj_cache = self.cache.setdefault("projects", {})

        for p in projects:
            repo = p["repo"]
            repo_low = repo.lower()
            ov = overrides.get(repo_low) or {}

            # 1. 人工覆盖优先
            if ov.get("summary_zh"):
                p["summary_zh"] = ov["summary_zh"]
                p["good_for"] = ov.get("good_for") or []
                p["not_for"] = ov.get("not_for") or []
                p["summary_source"] = "curated"
                continue

            desc_hash = _content_hash(f"{repo}:{p.get('description', '')}:{p.get('category', '')}")
            cached = proj_cache.get(repo_low)
            if cached and cached.get("hash") == desc_hash and cached.get("summary_zh"):
                p["summary_zh"] = cached["summary_zh"]
                p["good_for"] = cached.get("good_for") or []
                p["not_for"] = cached.get("not_for") or []
                p["summary_source"] = cached.get("source", "ai")
                continue

            # 先填入启发式摘要，若 LLM 可用则排入待加强队列（优先最新 Star 或高 Star 项目）
            heur = build_heuristic_summary(
                repo,
                p.get("description", ""),
                p.get("category", "agent"),
                p.get("topics", []),
                p.get("language", ""),
            )
            p["summary_zh"] = ov.get("summary_zh") or heur["summary_zh"]
            p["good_for"] = ov.get("good_for") or heur["good_for"]
            p["not_for"] = ov.get("not_for") or heur["not_for"]
            p["summary_source"] = "heuristic"

            if self.ai_client:
                pending_llm.append(p)

        # 2. 若配置有 LLM 客户端，按优先级批量提炼中文卡片（每次 10 个，最多 max_llm_batches 批）
        if self.ai_client and pending_llm:
            pending_llm.sort(
                key=lambda x: (x.get("starred_at") or "", x.get("stars") or 0),
                reverse=True,
            )
            batch_size = 10
            for b_idx in range(min(self.max_llm_batches, (len(pending_llm) + batch_size - 1) // batch_size)):
                batch = pending_llm[b_idx * batch_size : (b_idx + 1) * batch_size]
                self._run_llm_project_batch(batch)

    def _run_llm_project_batch(self, batch: List[Dict[str, Any]]) -> None:
        items_text = []
        for idx, p in enumerate(batch, 1):
            items_text.append(
                f"{idx}. repo: {p['repo']} | category: {p.get('category')} | "
                f"lang: {p.get('language')} | topics: {', '.join(p.get('topics', [])[:6])} | "
                f"desc: {p.get('description', '')}"
            )
        prompt = (
            "你是一位资深开源 AI 架构师。请为以下 GitHub 开源项目输出结构化中文技术卡片。\n"
            "要求：\n"
            "1. summary_zh：一句话中文技术定位（35~75字，直接点明核心机制与解决的问题，不要空洞套话）。\n"
            "2. good_for：数组，包含 2 条具体适用场景。\n"
            "3. not_for：数组，包含 1 条不适用场景或选型注意点。\n"
            "请严格输出 JSON 数组，格式为：[{\"repo\": \"owner/name\", \"summary_zh\": \"...\", \"good_for\": [\"...\"], \"not_for\": [\"...\"]}]\n\n"
            "项目列表：\n" + "\n".join(items_text)
        )
        try:
            raw = self.ai_client.generate(prompt)
            match = re.search(r"\[.*\]", raw, re.S)
            if not match:
                return
            parsed = json.loads(match.group(0))
            if not isinstance(parsed, list):
                return
            by_repo = {str(item.get("repo", "")).lower(): item for item in parsed if isinstance(item, dict)}
            proj_cache = self.cache.setdefault("projects", {})
            for p in batch:
                r_low = p["repo"].lower()
                hit = by_repo.get(r_low)
                if hit and hit.get("summary_zh"):
                    p["summary_zh"] = str(hit["summary_zh"]).strip()
                    if isinstance(hit.get("good_for"), list) and hit["good_for"]:
                        p["good_for"] = [str(x).strip() for x in hit["good_for"][:3]]
                    if isinstance(hit.get("not_for"), list) and hit["not_for"]:
                        p["not_for"] = [str(x).strip() for x in hit["not_for"][:2]]
                    p["summary_source"] = "ai"
                    proj_cache[r_low] = {
                        "hash": _content_hash(f"{p['repo']}:{p.get('description', '')}:{p.get('category', '')}"),
                        "summary_zh": p["summary_zh"],
                        "good_for": p["good_for"],
                        "not_for": p["not_for"],
                        "source": "ai",
                    }
        except Exception as e:
            print(f"[WARN] LLM 项目摘要批量生成降级为规则兜底: {e}")

    def summarize_release(self, repo: str, tag: str, body: str) -> List[str]:
        """获取或生成版本发布的中文要点列表。"""
        if not tag:
            return []
        rel_cache = self.cache.setdefault("releases", {})
        cache_key = f"{repo.lower()}@{tag}"
        if cache_key in rel_cache and rel_cache[cache_key].get("highlights"):
            return rel_cache[cache_key]["highlights"]

        highlights = extract_release_highlights_heuristic(body, tag)
        if self.ai_client and body and len(body.strip()) > 60:
            prompt = (
                f"请将开源项目 {repo} 的 {tag} 版本发布说明提炼为 2~3 条简明中文要点（每条不超过 60 字，突出核心新增能力、架构改进或破坏性变更）。\n"
                "严格输出 JSON 字符串数组，例如：[\"新增...\", \"修复...\"]\n\n"
                f"Release Notes:\n{body[:2500]}"
            )
            try:
                raw = self.ai_client.generate(prompt)
                match = re.search(r"\[.*\]", raw, re.S)
                if match:
                    arr = json.loads(match.group(0))
                    if isinstance(arr, list) and arr:
                        highlights = [str(x).strip() for x in arr[:3] if str(x).strip()]
            except Exception:
                pass

        rel_cache[cache_key] = {"tag": tag, "highlights": highlights}
        return highlights

