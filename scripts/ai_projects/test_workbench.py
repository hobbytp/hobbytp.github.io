#!/usr/bin/env python3
"""
AI 开源项目研究台 (AI Project Workbench) 自动化单元测试与数据完整性校验套件。
"""

import datetime
import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ai_projects.classifier import (
    classify_repository,
    extract_chinese_tags,
    build_heuristic_summary,
)
from scripts.ai_projects.ai_summarizer import extract_release_highlights_heuristic
from scripts.ai_projects.collect import (
    compute_health_and_risks,
    is_major_version_tag,
    assign_unique_ids,
)


class TestAIProjectWorkbench(unittest.TestCase):
    def test_classifier_categories(self):
        self.assertEqual(
            classify_repository("langchain-ai/langgraph", "Build resilient language agents as graphs", ["agent"]),
            "agent",
        )
        self.assertEqual(
            classify_repository("openai/codex", "Lightweight coding agent that runs in your terminal", ["cli"]),
            "coding",
        )
        self.assertEqual(
            classify_repository("oraios/serena", "Coding agent toolkit with semantic retrieval and MCP server", ["mcp"]),
            "skills",
        )
        self.assertEqual(
            classify_repository("getzep/graphiti", "Build real-time knowledge graphs for AI agents", ["rag", "memory"]),
            "knowledge",
        )
        self.assertEqual(
            classify_repository("OpenSenseNova/SenseNova-6.8-Code2Video", "Code-driven video generation", ["video"]),
            "media",
        )
        self.assertEqual(
            classify_repository("microsoft/PyRIT", "Python Risk Identification Tool for generative AI red-teaming", []),
            "security",
        )

    def test_tags_and_heuristic_summary(self):
        tags = extract_chinese_tags("skills", ["mcp", "rag", "python"], "Python")
        self.assertIn("MCP协议", tags)
        summary = build_heuristic_summary(
            "OpenSenseNova/SenseNova-6.8-Code2Video",
            "Code2Video: A code-driven video generation framework",
            "media",
            ["text-to-video"],
            "Python",
        )
        self.assertTrue(len(summary["summary_zh"]) > 10)
        self.assertTrue(len(summary["good_for"]) >= 1)
        self.assertTrue(len(summary["not_for"]) >= 1)

    def test_health_and_risks_calculation(self):
        now = datetime.datetime(2026, 11, 11, 8, 0, tzinfo=datetime.timezone.utc)
        active_proj = {
            "repo": "langchain-ai/langgraph",
            "archived": False,
            "pushed_at": "2026-11-10T10:00:00Z",
            "created_at": "2024-01-10T00:00:00Z",
            "stars": 18000,
            "forks": 3000,
            "commits_90d": 420,
            "releases_180d": 8,
            "license": "MIT",
            "open_issues": 100,
            "closed_issues": 900,
            "release": {"tag": "v0.4.0", "published_at": "2026-11-01T00:00:00Z"},
        }
        health, risks, status = compute_health_and_risks(active_proj, now)
        self.assertEqual(status, "active")
        self.assertEqual(len(risks), 0)
        self.assertGreaterEqual(health["score"], 80)

        archived_proj = {
            "repo": "old/abandoned",
            "archived": True,
            "pushed_at": "2024-01-01T00:00:00Z",
            "created_at": "2023-01-01T00:00:00Z",
            "stars": 50,
            "forks": 2,
            "license": None,
        }
        health2, risks2, status2 = compute_health_and_risks(archived_proj, now)
        self.assertEqual(status2, "archived")
        risk_codes = {r["code"] for r in risks2}
        self.assertIn("archived", risk_codes)
        self.assertIn("no_license", risk_codes)
        self.assertLess(health2["score"], health["score"])

    def test_release_helpers(self):
        self.assertTrue(is_major_version_tag("v1.0.0"))
        self.assertTrue(is_major_version_tag("0.5.0"))
        self.assertFalse(is_major_version_tag("v0.5.3"))

        body = """
        ## What's Changed
        - Added multi-agent checkpoint streaming support (#123)
        - Improved GraphQL batching performance by 3x by @alice
        Full Changelog: https://github.com/org/repo/compare/v0.1...v0.2
        """
        hl = extract_release_highlights_heuristic(body, "v0.2.0")
        self.assertEqual(len(hl), 2)
        self.assertIn("Added multi-agent checkpoint streaming support", hl[0])

    def test_unique_id_assignment(self):
        projs = [
            {"repo": "langchain-ai/langgraph", "stars": 10000, "posts": [{"url": "/a"}]},
            {"repo": "other-user/langgraph", "stars": 20, "posts": []},
        ]
        assign_unique_ids(projs, {"langchain-ai/langgraph"})
        id_map = {p["repo"]: p["id"] for p in projs}
        self.assertEqual(id_map["langchain-ai/langgraph"], "langgraph")
        self.assertEqual(id_map["other-user/langgraph"], "other-user-langgraph")

    def test_generated_data_files_integrity(self):
        data_dir = PROJECT_ROOT / "data" / "ai_projects"
        metrics_path = data_dir / "metrics.json"
        events_path = data_dir / "events.json"
        weekly_path = data_dir / "weekly_latest.json"

        self.assertTrue(metrics_path.exists(), "metrics.json 必须存在")
        self.assertTrue(events_path.exists(), "events.json 必须存在")
        self.assertTrue(weekly_path.exists(), "weekly_latest.json 必须存在")

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(metrics["summary"]["total_projects"], 500)
        self.assertGreaterEqual(metrics["summary"]["with_blog_posts"], 20)

        events = json.loads(events_path.read_text(encoding="utf-8"))
        self.assertGreater(len(events["events"]), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)

