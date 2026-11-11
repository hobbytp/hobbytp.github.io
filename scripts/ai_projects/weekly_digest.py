#!/usr/bin/env python3
"""
AI 开源周报自动生成引擎 (weekly_digest.py)
基于 data/ai_projects/metrics.json 与 events.json，
汇总作者近期新 Star 的开源项目、重要版本发布、社区热度跃升与风险信号，
生成结构化博客周报文章 content/zh/projects/weekly/YYYY-WXX.md，
并更新 data/ai_projects/weekly_latest.json 供研究台首屏展示。
"""

import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "ai_projects"
WEEKLY_CONTENT_DIR = PROJECT_ROOT / "content" / "zh" / "projects" / "weekly"
BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))


def _calc_reading_stats(text: str) -> tuple[int, int]:
    cjk_count = len(re.findall(r"[\u4e00-\u9fa5]", text))
    en_words = len(re.findall(r"[A-Za-z0-9_]+", text))
    total = cjk_count + en_words // 2
    reading_time = max(1, (total + 399) // 400)
    return total, reading_time


def _generate_executive_intro(
    newly_starred: List[Dict[str, Any]],
    recent_releases: List[Dict[str, Any]],
    surging: List[Dict[str, Any]],
) -> str:
    """尝试调用 AIClient 生成周报开篇导读，若未配置密钥则生成高质量结构化导读。"""
    star_names = "、".join([f"`{p['name']}`" for p in newly_starred[:5]])
    rel_names = "、".join(
        [f"`{p['name']} ({p['release']['tag']})`" for p in recent_releases[:4] if p.get("release")]
    )

    fallback_intro = (
        f"本期周报基于 [AI 开源项目研究台](/zh/ai-workbench/) 的实时追踪数据生成。"
        f"近期新收录关注焦点集中在 {star_names or '智能体与多模态工具'} 等项目，"
        f"反映出社区正从单一对话框架向**代码驱动视频生成、可视化概念解释、跨平台智能体触达与规范化研发线束**演进。"
    )
    if rel_names:
        fallback_intro += f" 同时，{rel_names} 等核心底座相继发布了新版本迭代，建议在实际工程选型中结合下方更新要点评估升级。"

    try:
        from scripts.daily_ai.generators.ai_client import AIClient
        client = AIClient()
        if client.client or client.bk_client:
            ctx = (
                "新收录项目: "
                + "; ".join([f"{p['repo']} ({p.get('summary_zh', '')})" for p in newly_starred[:6]])
                + "\n重要发版: "
                + "; ".join(
                    [
                        f"{p['repo']} {p['release']['tag']}: {' / '.join(p['release'].get('highlights', [])[:2])}"
                        for p in recent_releases[:5]
                        if p.get("release")
                    ]
                )
            )
            prompt = (
                "你是一位资深 AI 开源技术主编。请根据以下本周 GitHub Stars 新收录项目与重要版本发布，写一段 120~180 字的《AI 开源周报》开篇趋势导读。"
                "要求：直接输出正文段落，点明本周技术趋势主线与核心看点，文风专业凝练，不要标题或客套话。\n\n"
                + ctx
            )
            res = client.generate(prompt).strip()
            if res and not res.startswith("> 暂无") and not res.startswith("由于所有"):
                return res
    except Exception:
        pass

    return fallback_intro


def generate_weekly_digest() -> Dict[str, Any]:
    metrics_file = DATA_DIR / "metrics.json"
    if not metrics_file.exists():
        raise FileNotFoundError("未找到 data/ai_projects/metrics.json，请先运行 collect.py")

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    projects: List[Dict[str, Any]] = metrics.get("projects_list") or []
    summary = metrics.get("summary") or {}

    now = datetime.datetime.now(BEIJING_TZ)
    iso_year, iso_week, _ = now.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"
    date_str = now.strftime("%Y-%m-%d")

    # 1. 筛选近期新 Star 项目（按 starred_at 排序前 8 个）
    newly_starred = sorted(
        [p for p in projects if p.get("starred_at")],
        key=lambda x: x.get("starred_at") or "",
        reverse=True,
    )[:8]

    # 2. 筛选近期发布新版本的项目（按 release.published_at 排序前 8 个）
    recent_releases = sorted(
        [p for p in projects if isinstance(p.get("release"), dict) and p["release"].get("published_at")],
        key=lambda x: x["release"].get("published_at") or "",
        reverse=True,
    )[:8]

    # 3. 筛选热度增速最快项目（按 stars_per_day 排序前 6 个）
    surging = sorted(
        [p for p in projects if int(p.get("stars") or 0) >= 300 and not p.get("archived")],
        key=lambda x: float(x.get("stars_per_day") or 0.0),
        reverse=True,
    )[:6]

    # 4. 筛选本站有深度解读文章的项目
    with_posts = [p for p in projects if p.get("posts")][:8]

    intro_text = _generate_executive_intro(newly_starred, recent_releases, surging)

    lines: List[str] = []
    lines.append(f"> 💡 **研究台直达**：本文数据由 [AI 开源项目研究台](/zh/ai-workbench/) 自动同步自 GitHub `@hobbytp` 的公开 Stars 收藏与版本监控流。点击任意项目可查看 CHAOSS 四维健康度、适用边界与历史判断。")
    lines.append("")
    lines.append("## 1. 本周趋势导读与生态速览")
    lines.append("")
    lines.append(intro_text)
    lines.append("")
    lines.append("| 指标维度 | 当前数值 | 说明 |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **研究台收录总数** | **{summary.get('total_projects', len(projects))}** 个 | 同步自 `@hobbytp` GitHub Stars 与博客深度解析 |")
    lines.append(f"| **近期活跃维护** | **{summary.get('active_count', 0)}** 个 | 近 30 天内有代码推送或版本迭代 |")
    lines.append(f"| **近 30 天版本发布** | **{summary.get('recent_releases_30d', 0)}** 个 | 发布正式 Release 标签的项目数 |")
    lines.append(f"| **本站深度解读覆盖** | **{summary.get('with_blog_posts', 0)}** 个 | 拥有配套源码级长文剖析的项目 |")
    lines.append("")

    # 章节 2: 近期新 Star 收录
    lines.append("## 2. 🌟 近期新 Star 收录解析")
    lines.append("")
    lines.append("以下为近期新加入 GitHub Stars 收藏夹并纳入研究台追踪的代表性开源项目：")
    lines.append("")
    for p in newly_starred:
        star_date = (p.get("starred_at") or "")[:10]
        lic = p.get("license") or "未声明"
        tags_str = " · ".join([f"`{t}`" for t in (p.get("tags") or [])[:4]])
        lines.append(f"### [{p['name']}]({p['page_url']}) (`{p['repo']}`)")
        lines.append("")
        lines.append(
            f"- **领域分类**：{p.get('category_name', '')} | **Star 时间**：`{star_date}` | "
            f"**Stars**：`{p['stars']:,}` (`+{p.get('stars_7d', 0):,}/7d`) | "
            f"**语言/协议**：`{p.get('language', 'Multi')}` / `{lic}` | **健康度**：`{p['health']['score']}/100`"
        )
        if tags_str:
            lines.append(f"- **核心标签**：{tags_str}")
        lines.append(f"- **技术定位**：{p.get('summary_zh') or p.get('description') or '暂无描述'}")
        good_for = p.get("good_for") or []
        if good_for:
            lines.append(f"- **适用场景**：{'；'.join(good_for[:2])}")
        lines.append(
            f"- **快捷入口**：[站内项目档案 →]({p['page_url']}) · [GitHub 仓库 ↗](https://github.com/{p['repo']})"
        )
        lines.append("")

    # 章节 3: 重要版本发布
    lines.append("## 3. 🚀 重要版本发布追踪 (Release Radar)")
    lines.append("")
    if recent_releases:
        for p in recent_releases:
            rel = p["release"]
            pub_date = (rel.get("published_at") or "")[:10]
            rel_url = rel.get("url") or f"https://github.com/{p['repo']}/releases"
            lines.append(f"### [{p['name']}]({p['page_url']}) 发布 `{rel['tag']}` ({pub_date})")
            lines.append("")
            lines.append(f"- **所属领域**：{p.get('category_name', '')} · **当前选型判断**：`{p.get('verdict_label', '已收藏待评')}`")
            for hl in (rel.get("highlights") or [])[:3]:
                lines.append(f"- **更新要点**：{hl}")
            lines.append(f"- **查看详情**：[Release 说明 ↗]({rel_url}) · [站内项目页 →]({p['page_url']})")
            lines.append("")
    else:
        lines.append("近期暂无新增 Release 标签记录。")
        lines.append("")

    # 章节 4: 社区热度跃升榜
    lines.append("## 4. 🔥 社区热度增速榜 (Breakout Momentum)")
    lines.append("")
    lines.append("| 开源项目 | 领域 | 当前 Stars | 日均获星速率 | 综合健康度 | 一句话定位 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for p in surging:
        short_sum = (p.get("summary_zh") or p.get("description") or "")[:48].replace("|", " ")
        lines.append(
            f"| [{p['name']}]({p['page_url']}) | {p.get('category_name', '')} | `{p['stars']:,}` | "
            f"`+{p.get('stars_per_day', 0):.1f}/天` | `{p['health']['score']}` | {short_sum} |"
        )
    lines.append("")

    # 章节 5: 本站深度解读关联
    if with_posts:
        lines.append("## 5. 📚 本站配套深度解读文章")
        lines.append("")
        for p in with_posts:
            post = p["posts"][0]
            lines.append(
                f"- **[{p['name']} (`{p['repo']}`)]({p['page_url']})** — "
                f"阅读本站长文：[《{post['title']}》]({post['url']})（选型结论：`{p.get('verdict_label', '')}`）"
            )
        lines.append("")

    body_md = "\n".join(lines)
    word_count, reading_time = _calc_reading_stats(body_md)

    top_names = "、".join([p["name"] for p in newly_starred[:3]])
    title = f"AI 开源项目周报 ({week_id})：{top_names} 等新锐项目入库与生态追踪"
    description = (
        f"汇总 {week_id} 周期内 @hobbytp GitHub Stars 最新收录的 AI 开源项目（{top_names} 等）、"
        f"核心框架版本迭代要点与 CHAOSS 健康度追踪。"
    )

    front_matter = (
        "---\n"
        f'title: "{title}"\n'
        f'date: "{now.strftime("%Y-%m-%dT%H:%M:%S+08:00")}"\n'
        "draft: false\n"
        'categories: ["projects"]\n'
        'tags: ["AI开源周报", "开源项目", "GitHub Stars", "Agent", "工程实践"]\n'
        f'description: "{description}"\n'
        f"wordCount: {word_count}\n"
        f"readingTime: {reading_time}\n"
        "---\n\n"
    )

    WEEKLY_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = WEEKLY_CONTENT_DIR / f"{week_id.lower()}.md"
    out_file.write_text(front_matter + body_md, encoding="utf-8")

    weekly_meta = {
        "week": week_id,
        "date": date_str,
        "title": title,
        "description": description,
        "url": f"/zh/projects/weekly/{week_id.lower()}/",
        "newly_starred_sample": [p["name"] for p in newly_starred[:4]],
        "release_sample": [
            f"{p['name']} {p['release']['tag']}"
            for p in recent_releases[:3]
            if p.get("release")
        ],
    }
    (DATA_DIR / "weekly_latest.json").write_text(
        json.dumps(weekly_meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[SUCCESS] 已生成本周 AI 开源周报: {out_file} ({word_count} 字)")
    return weekly_meta


if __name__ == "__main__":
    generate_weekly_digest()

