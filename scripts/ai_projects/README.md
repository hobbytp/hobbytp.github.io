# AI 开源项目研究台 (AI Project Workbench)

> **为热爱 AI 开源项目的人打造：实时追踪、量化评估、场景选型与周报自动生成的端到端研究工作台。**

---

## 📌 项目概述

「AI 开源项目研究台」是一个与个人 GitHub Stars 深度联动的开源项目研究与选型体系。它解决了以往开源项目收集“容易积灰、无法知晓近期维护状态、缺乏中文技术边界与深度解读”的痛点。

### 核心亮点
1. **自动从 GitHub Stars 同步**：无需人工搬运，日常在 GitHub（`@hobbytp`）点击 Star 即可自动入库、分类并追踪。
2. **三层数据结构**：
   - **客观事实**：通过 GitHub REST 与 GraphQL API 自动化采集（Release、近 90 天提交、Issue 响应、许可证、Stars 增速等）。
   - **AI 中文解读**：复用仓库大模型接口（Gemini / DashScope / OpenAI + 启发式规则兜底），增量生成一句话中文技术定位、适用场景与版本更新要点。
   - **作者实测判断**：人工维护在 `curated.yaml` 中（`recommend` 主力推荐、`trial` 值得试用、`watch` 持续观察等），自动化脚本绝不篡改。
3. **CHAOSS 风格可解释健康度**：摒弃不可复核的演示评分，按公开公式量化「活跃度 (35%) + 社区响应 (25%) + 发布节奏 (20%) + 持续合规 (20%)」。
4. **双向关联博客深度长文**：自动扫描本站 `content/zh/projects/` 文章中的 GitHub 链接，为重点项目建立「项目档案 ↔ 源码级长文剖析」双向跳转。
5. **四大一级交互视图**：
   - 🗂️ **项目库**：多维即时筛选、卡片/紧凑表格切换、URL Query 状态同步、最多 3 项横向对比（高亮优势项）。
   - 📡 **变化信号流**：新 Star 入库、重要发版、本站新发解读、热度飙升事件，支持 RSS 与 JSON 输出。
   - 🧭 **实战场景包**：按实际任务（如企业级 AI 编程线束、深度研究智能体、长记忆 MCP 底座等）组织组件方案。
   - ⭐ **我的关注与 Stars 对照**：纯前端 `localStorage` 保存个人状态与笔记；访客可输入任意 GitHub 用户名，对照双方重合关注。
6. **每周自动生成《AI 开源周报》**：每周自动汇总新收录、重大版本发布与热度跃升榜，生成 Markdown 博客文章。

---

## 📁 目录与文件结构

```tree
hobbytp.github.io/
├── scripts/ai_projects/             # 自动化脚本与核心逻辑
│   ├── collect.py                  # 核心采集引擎 (拉取 Stars、GraphQL 深采、计算健康度)
│   ├── ai_summarizer.py            # AI 中文摘要器 (带增量哈希缓存与无密钥规则兜底)
│   ├── weekly_digest.py            # 每周《AI 开源周报》自动生成脚本
│   ├── classifier.py               # 10 大领域规则分类器与中文标签提取
│   ├── blog_scanner.py             # 博客文章与 GitHub 仓库双向链接扫描器
│   ├── test_workbench.py           # 自动化单元测试与数据完整性校验套件
│   └── README.md                   # 本文档
│
├── data/ai_projects/                # 数据持久化目录
│   ├── curated.yaml                # 人工策展叠加层 (分类、场景包、作者实测判断)
│   ├── metrics.json                # 项目全集快照与指标统计 (自动生成)
│   ├── events.json                 # 变化信号流 (自动生成)
│   ├── ai_summaries.json           # 增量 AI 中文摘要缓存 (自动生成)
│   ├── weekly_latest.json          # 最新一期周报元数据 (自动生成)
│   └── history/                    # 按月分片的 Stars 历史快照
│       └── YYYY-MM.json
│
├── content/zh/ai-workbench/        # 页面内容与 Hugo Content Adapter
│   ├── _index.md                   # 研究台入口页面 Front Matter
│   └── _content.gotmpl             # Content Adapter (从数据动态生成重点项目独立页面)
│
├── content/zh/projects/weekly/     # 每周自动生成的《AI 开源周报》文章
│   └── 2026-w46.md
│
├── layouts/ai-workbench/           # Hugo 模板
│   ├── list.html                   # 研究台主页面模板 (四视图、横向对比、弹窗)
│   ├── single.html                 # 单项目档案独立 SEO 落地页
│   ├── rss.xml                     # 变化信号 RSS 订阅源
│   └── index.json                  # 全局结构化 JSON 输出
│
├── assets/
│   ├── css/extended/ai-workbench.css  # 适配 PaperMod 亮/暗色模式的专属样式
│   └── js/ai-workbench.js             # 客户端即时筛选、对比、关注与 Stars 对照交互
│
└── .github/workflows/
    └── ai-projects-collect.yml     # 每日定时采集与每周周报 GitHub Actions 工作流
```

---

## 🚀 怎么使用？

### 1. 环境准备

需要 Python 3.10+，推荐使用现代包管理器 `uv`（也可以使用系统的 `python`）：

```bash
# 安装必要依赖
pip install pyyaml requests google-genai openai
# 或者使用 uv（免手动预装环境）
uv run --with pyyaml python <脚本>
```

**关于 GitHub API 凭证**：
- 脚本会自动检查 `GITHUB_TOKEN` / `MY_GITHUB_TOKEN` / `GH_TOKEN` 环境变量。
- 若本机已安装并登录 GitHub CLI（`gh auth login`），脚本会自动通过 `gh auth token` 调取凭证，获得每小时 5000 次的高频 API 配额。
- 若无 Token，则自动降级为匿名公开模式（受 60 次/小时限制）。

---

### 2. 核心操作命令

#### ① 运行数据全量采集与健康度计算
从 GitHub 用户（默认 `@hobbytp`）拉取公开 Stars，扫描博客关联文章，并通过 GraphQL 深采指标并计算 CHAOSS 分数：

```bash
# 使用 uv
uv run --with pyyaml python scripts/ai_projects/collect.py

# 或使用标准 python
python scripts/ai_projects/collect.py
```
*执行产物*：更新 `data/ai_projects/metrics.json`、`events.json`、`ai_summaries.json` 和 `history/YYYY-MM.json`。

---

#### ② 手动生成本周《AI 开源周报》
汇总本周新 Star 项目、重要 Release 中文要点、热度飙升榜并生成博客文章：

```bash
# 使用 uv
uv run --with pyyaml python scripts/ai_projects/weekly_digest.py

# 或使用标准 python
python scripts/ai_projects/weekly_digest.py
```
*执行产物*：
- 新增/更新文章：`content/zh/projects/weekly/YYYY-WXX.md`（自动带有 Front Matter，支持全站搜索与分类展示）。
- 更新数据：`data/ai_projects/weekly_latest.json`（供研究台主页顶部横幅调用）。

---

#### ③ 运行单元测试与数据完整性校验
运行自动化测试套件，检查领域分类规则、指标计算逻辑、Release 提取以及数据文件完整性：

```bash
# 使用 uv
uv run --with pyyaml python scripts/ai_projects/test_workbench.py

# 或使用标准 python
python scripts/ai_projects/test_workbench.py
```

---

### 3. 本地预览与调试

启动 Hugo 本地开发服务器预览研究台页面：

```bash
# 使用项目自带 Makefile
make dev
# 或快速模式
make dev-fast
```

在浏览器打开：
- 研究台主页：`http://localhost:1313/zh/ai-workbench/`
- 重点项目独立页：`http://localhost:1313/zh/ai-workbench/langgraph/`
- RSS 信号源：`http://localhost:1313/zh/ai-workbench/index.xml`
- 数据 JSON：`http://localhost:1313/zh/ai-workbench/index.json`
- 最新周报：`http://localhost:1313/zh/projects/weekly/2026-w46/`

---

## 🛠️ 日常维护与扩展指南

### 1. 我想收录新项目怎么做？
你**不需要手动编辑 JSON 或运行录入命令**：
1. **最便捷方式**：在 GitHub 上给目标仓库点一下 **Star** 即可。下次运行采集脚本或每日定时 GitHub Actions 执行后，该仓库将自动同步并出现在研究台和周报中。
2. **写博客时引用**：在 `content/zh/projects/` 的文章中直接写入仓库 GitHub 链接，扫描器会自动纳为重点关注并建立双向链接。

---

### 2. 如何添加作者实测判断（Verdicts）与修正分类？
打开 `data/ai_projects/curated.yaml`，在 `overrides` 节点下增加对应仓库配置（以 `owner/repo` 为键，全小写）：

```yaml
overrides:
  langchain-ai/langgraph:
    category: agent               # 可选：手动覆盖所属领域
    tags: [工作流, 状态机, 人工介入] # 可选：自定义中文标签
    summary_zh: 以有向图和显式状态机编排复杂多步骤 Agent，原生支持断点续跑与人工介入
    good_for:
      - 需要长链路状态控制与人工审批节点的生产级 Agent
    not_for:
      - 单轮问答或简单线性链式调用
    alternatives: [microsoft/autogen, camel-ai/camel]
    complements: [getzep/graphiti, promptfoo/promptfoo]
    verdicts:
      - date: "2026-10-11"
        level: recommend          # 级别：recommend / trial / watch / caution / avoid
        reason: 状态控制粒度与持久化恢复机制最稳健，适合生产环境精细编排
        evidence: /zh/projects/langgraph/
```

**判断等级说明**：
- `recommend`（主力推荐）：已在真实工作流中深度验证，高价值优先采用。
- `trial`（值得试用）：解决特定痛点表现亮眼，建议小规模实测。
- `watch`（持续观察）：理念或势头出色，但生态仍在快速演进。
- `caution`（谨慎评估）：维护节奏放缓或复杂度过高。
- `avoid`（暂不推荐）：已归档停更或投入产出比过低。
- `unrated`（已收藏待评）：默认状态。

---

### 3. 如何新增/调整实战场景包？
在 `data/ai_projects/curated.yaml` 的 `scenarios` 下添加新的场景，前端「实战场景包」视图会自动渲染：

```yaml
scenarios:
  - id: my-new-scenario
    title: 场景名称
    goal: 解决的具体工程目标
    not_for: 不适用的反例场景
    stack:
      - project: owner/repo-a
        role: 担任的核心职责
        alternatives: [owner/repo-b]
```

---

### 4. 自动化 GitHub Actions 运行逻辑
工作流配置于 `.github/workflows/ai-projects-collect.yml`：
- **定时触发**：每天北京时间早上 06:30（UTC 22:30）自动运行。
- **自动判定**：周一自动执行 `weekly_digest.py` 并生成周报；其余时间仅同步最新 Stars 与指标。
- **手动触发**：支持在 GitHub Actions 页面点击 `Run workflow`，可选择是否强制生成本周周报。
- **仅增量提交**：只有当 `data/ai_projects/` 或周报文章有实际变更时，才会自动提交并推送到仓库，不产生冗余 Commit。

---

## 💡 常见问题 (FAQ)

### Q1: GitHub API 会不会被限流？
- 脚本中拉取 Stars 分页每页 100 条（500+ 个 Star 仅消耗 6 次请求）。
- 重点仓库采集采用 **GraphQL 批量分片查询**（每次并发查询 20 个仓库），140 个重点仓库仅消耗 7 次 GraphQL 请求。
- 在配置了 Token 的情况下，每次采集总请求数 < 20 次，远低于 GitHub 5000 次/小时的限额。

### Q2: 如果没有配置大模型 API Key 会影响页面生成吗？
**完全不影响**。`ai_summarizer.py` 内置双重兜底：
1. 本地增量缓存 `ai_summaries.json`（避免重复调用消耗配额）。
2. 当所有 AI 客户端（Gemini / DashScope / OpenAI）均未配置或遇到网络错误时，自动触发高质量**结构化启发式规则兜底**，从仓库描述、Topics、分类与 Release Notes 提取中英文要点，站点依然能全量正常构建。

### Q3: 访客导入 Stars 是否安全？
**绝对安全**。访客在浏览器导入 Stars 走的是浏览器的原生 `fetch` 与 GitHub 公开接口，纯前端只读处理并在 `localStorage` 缓存，不收集任何用户隐私，前端代码也不包含任何站长凭据。

