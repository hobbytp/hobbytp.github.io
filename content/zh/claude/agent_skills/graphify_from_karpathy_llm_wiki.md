---
title: Graphify 操作手册 for Claude Code
date: "2026-04-08T23:00:00+08:00"
draft: false
tags: ["OpenSkills", "Claude", "Skills"]
categories: ["ai_programming"]
description: "OpenSkills 是一个用于在 Cursor 和 Trae 中使用 Claude Skills 的开源工具，提供了详细的安装和使用指南。"
wordCount: 2691
readingTime: 7
---

## 项目介绍

根据Andre Karpathy 个人知识库工作流启发而诞生的开源项目**Graphify**，它能将原始代码、文档和论文转化为结构化的知识图谱。该工具支持与 Claude Code 及 Cursor 等 AI 助手深度集成，通过 AST 解析和语义提取技术，将原本散乱的文件映射为可查询、可视化的关联网络。Graphify 显著提升了开发者理解复杂代码库的效率，能够实现精准的问题定位、跨模态的论文与代码对比，并支持将分析结果导出至 Obsidian 进行持久化管理。相较于传统的线性记忆系统，它为 AI 助手叠加了一层结构化认知层，大幅减少了 Token 消耗并增强了逻辑推理能力。该项目标志着个人知识库从简单的文档堆砌向智能图谱导航的重大进化。


本手册假设你已经安装好了 `graphify`，并且已经在 Claude Code 中开始使用。这里不再介绍安装，只讲进入日常使用后的命令、功能和推荐工作流。

`graphify` 的定位不是普通搜索工具，而是把代码、文档、论文、图片等内容抽取成一张可导航的知识图谱，让 Claude 在回答问题前先理解结构、关系、社区和关键节点。

## 1. graphify 会给你什么

当你执行一次 `/graphify` 后，通常会在项目里得到一个 `graphify-out/` 目录，常见产物如下：

- `graph.html`
  交互式知识图谱，可搜索节点、查看关系、按社区浏览。
- `GRAPH_REPORT.md`
  面向人的报告，通常包含：
  - God Nodes
  - Surprising Connections
  - Suggested Questions
- `graph.json`
  持久化图数据，后续的查询、解释、路径追踪都基于它。
- `wiki/`
  可选导出，适合 agent 通过普通 Markdown 导航整个知识库。
- `graph.svg`
  可选导出，适合嵌入文档。
- `graph.graphml`
  可选导出，适合 Gephi、yEd 等图工具。
- `cypher.txt`
  可选导出，适合导入 Neo4j。

## 2. 你最常用的命令

在 Claude Code 中，最常用的是以下几类：

```text
/graphify
/graphify <path>
/graphify <path> --mode deep
/graphify <path> --update
/graphify <path> --cluster-only
/graphify <path> --watch
/graphify query "<question>"
/graphify query "<question>" --dfs
/graphify path "A" "B"
/graphify explain "NodeName"
/graphify add <url>
```

下面按功能分类说明。

## 3. 基础构图命令

### 3.1 `/graphify`

作用：对当前目录运行完整构图流程。

适用场景：
- 你已经在项目根目录
- 你想先把整个代码库或资料目录图谱化

示例：

```text
/graphify
```

### 3.2 `/graphify <path>`

作用：对指定目录构图。

适用场景：
- 只想分析某个子目录
- 想分析某个 `raw/` 资料目录
- 想分析项目外的另一个目录

示例：

```text
/graphify ./raw
/graphify ./docs
/graphify ../another-project
```

### 3.3 `/graphify <path> --mode deep`

作用：开启更深入的语义提取，生成更多 `INFERRED` 推断边。

适用场景：
- 你想发现更隐含的架构关系
- 你想增强跨文件、跨材料的语义连接

特点：
- 结果更丰富
- 推断边更多
- 通常更慢一些

示例：

```text
/graphify . --mode deep
```

## 4. 更新、重建与持续同步

### 4.1 `/graphify <path> --update`

作用：只处理新增或修改过的文件，并合并到已有图谱。

适用场景：
- 你已经跑过一次图谱
- 最近改了代码或补了资料
- 不想全量重跑

示例：

```text
/graphify . --update
```

### 4.2 `/graphify <path> --cluster-only`

作用：跳过内容抽取，只基于已有 `graph.json` 重新做社区聚类与报告。

适用场景：
- 图已经存在
- 你只想重新做 community 分析

示例：

```text
/graphify . --cluster-only
```

### 4.3 `/graphify <path> --no-viz`

作用：跳过 HTML 可视化，只生成报告和 JSON。

适用场景：
- 你只关心结构数据和报告
- 不需要 `graph.html`

示例：

```text
/graphify . --no-viz
```

### 4.4 `/graphify <path> --watch`

作用：进入监听模式，监控目录变更并持续同步图谱。

典型行为：
- 如果变化的是代码文件，会自动重建代码相关图结构
- 如果变化的是文档、论文或图片，通常会提示你再跑一次 `--update`

适用场景：
- 你在持续开发一个项目
- 希望图谱尽量保持最新

示例：

```text
/graphify . --watch
```

## 5. 图谱查询与导航

当图谱已经存在后，graphify 最有价值的能力之一，就是让 Claude 按图谱导航，而不是只靠关键词搜文件。

### 5.1 `/graphify query "<question>"`

作用：对图谱做广度优先查询，返回与问题相关的节点和关系。

适用场景：
- 想问某个概念周边都连接了什么
- 想先看全局相关结构

示例：

```text
/graphify query "what connects auth to database?"
/graphify query "rate limiting related components"
```

### 5.2 `/graphify query "<question>" --dfs`

作用：改为深度优先遍历，更适合追一条具体链路。

适用场景：
- 想追调用链
- 想追依赖传播路径
- 想看从一个点如何深入走到另一个结构域

示例：

```text
/graphify query "how does request validation reach persistence?" --dfs
```

### 5.3 `/graphify query "<question>" --budget N`

作用：限制输出预算，避免结果过长。

适用场景：
- 问题太宽
- 图太大
- 你只想先看压缩版答案

示例：

```text
/graphify query "what connects attention to optimizer?" --budget 1500
```

### 5.4 `/graphify path "A" "B"`

作用：查找两个概念之间的最短路径。

适用场景：
- 你已经知道两个点
- 你想知道它们中间是如何连起来的

示例：

```text
/graphify path "AuthModule" "Database"
/graphify path "DigestAuth" "Response"
```

### 5.5 `/graphify explain "NodeName"`

作用：解释单个节点是什么、来自哪里、与谁相连、为什么重要。

适用场景：
- 遇到陌生类、模块、概念
- 想快速理解它在系统中的角色

示例：

```text
/graphify explain "SwinTransformer"
/graphify explain "RetryPolicy"
```

## 6. 导入外部资料

### 6.1 `/graphify add <url>`

作用：抓取一个 URL，保存到语料目录，再更新图谱。

适合纳入图谱的内容包括：
- 网页
- 推文 / X 帖子
- arXiv 页面
- PDF
- 图片链接

示例：

```text
/graphify add https://arxiv.org/abs/1706.03762
/graphify add https://example.com/design-doc
```

### 6.2 附加元信息

你还可以给导入内容附带作者和贡献者信息：

```text
/graphify add https://example.com/post --author "Alice" --contributor "Bob"
```

含义：
- `--author`：原作者
- `--contributor`：是谁把该内容加入当前语料库

## 7. 导出与系统集成

### 7.1 `/graphify <path> --wiki`

作用：把知识图谱转成一组 Markdown wiki 页面。

适用场景：
- 想让 agent 用普通文件方式导航
- 想让人类直接通过 Markdown 浏览社区和节点

示例：

```text
/graphify . --wiki
```

### 7.2 `/graphify <path> --obsidian --obsidian-dir <dir>`

作用：导出到 Obsidian vault。

适用场景：
- 想把图谱融入个人知识管理系统

### 7.3 `/graphify <path> --svg`

作用：额外导出 `graph.svg`。

适用场景：
- 想把图直接嵌入文档、Notion、GitHub 页面

### 7.4 `/graphify <path> --graphml`

作用：导出 `graph.graphml`。

适用场景：
- 想在 Gephi、yEd 等外部图工具中进一步分析

### 7.5 `/graphify <path> --neo4j`

作用：生成供 Neo4j 导入的 Cypher 文件。

### 7.6 `/graphify <path> --neo4j-push bolt://...`

作用：把图直接推送到运行中的 Neo4j。

### 7.7 `/graphify <path> --mcp`

作用：启动 MCP stdio server，让其他 agent 或工具直接查询图谱。

## 8. 图谱中的三类关系可信度

graphify 的重要特点之一，是它不会把所有边都伪装成“硬事实”。每条边都会标记可信度类别。

### 8.1 `EXTRACTED`

表示这条关系是从源材料中直接抽取出来的。

常见来源：
- import
- 显式调用
- 明确引用
- 文档中直接陈述的关系

这是最强的一类证据。

### 8.2 `INFERRED`

表示这是基于上下文做出的合理推断。

常见例子：
- 两个模块共享关键数据结构
- 两个概念在功能上明显服务于同一流程
- 某个设计意图隐含了依赖关系

这类边通常带有 `confidence_score`。

### 8.3 `AMBIGUOUS`

表示 graphify 认为这里可能有关系，但不够确定，因此显式标记为待人工复核。

使用建议：
- 不要把 `AMBIGUOUS` 当作结论
- 可把它当作下一步调查入口

## 9. graphify 在 Claude Code 里的核心能力

从用户角度看，graphify 在 Claude Code 中主要提供以下几类功能。

### 9.1 知识图谱构建

把以下内容统一拉进同一张图里：
- 代码
- 文档
- PDF
- 图片
- 笔记

### 9.2 社区发现

自动把节点按关系密度分成多个主题社区，帮助你看清系统有哪些“结构块”。

### 9.3 关键节点识别

自动找出 God Nodes，也就是连接最多、最可能是核心抽象或中枢的节点。

### 9.4 意外连接发现

自动展示跨模块、跨材料、跨社区的非显然连接。

### 9.5 图谱问答导航

通过 `query`、`path`、`explain` 三组命令，沿图结构回答问题。

### 9.6 持久化记忆

图谱存储在 `graph.json` 中，不依赖单次会话。你下次回来时，Claude 仍然可以基于已有图继续工作。

### 9.7 持续同步

通过 `--watch`、增量更新和 Git hooks，让图谱跟着项目演化。

## 10. Claude Code 的常驻增强能力

除了 `/graphify` 这类 slash 命令，graphify 还提供项目级常驻增强。它们是在终端里运行的 `graphify` CLI 命令，不是 slash 命令。

### 10.1 `graphify claude install`

作用：
- 向当前项目的 `CLAUDE.md` 写入 graphify 规则
- 向 `.claude/settings.json` 写入 PreToolUse hook

效果：
- Claude 在 `Glob` 和 `Grep` 之前，会优先被提示查看 `graphify-out/GRAPH_REPORT.md`
- 这样 Claude 更倾向于先用图谱理解结构，再搜索原始文件

### 10.2 `graphify claude uninstall`

作用：移除上述本地项目级增强。

## 11. Git 自动同步能力

以下也是终端命令，不是 slash 命令：

- `graphify hook install`
- `graphify hook uninstall`
- `graphify hook status`

功能：
- `post-commit` 后自动重建代码相关图谱
- `post-checkout` 切分支后自动重建代码相关图谱

适合：
- 长期维护的仓库
- 多分支工作流
- 希望图谱和代码版本变化保持同步

## 12. 推荐工作流

如果你第一次进入一个陌生项目，推荐这样使用：

### 12.1 第一步：先构图

```text
/graphify .
```

### 12.2 第二步：优先看报告

重点关注：
- God Nodes
- Surprising Connections
- Suggested Questions

### 12.3 第三步：深挖关键节点和路径

```text
/graphify explain "某个核心模块"
/graphify path "入口模块" "数据库"
```

### 12.4 第四步：改完代码后做增量更新

```text
/graphify . --update
```

### 12.5 第五步：如果长期使用这个项目

在终端里执行：

```bash
graphify claude install
graphify hook install
```

这样 Claude Code 会更稳定地优先参考图谱，Git 提交和切分支后也会自动更新代码图结构。

## 13. 什么时候该用哪条命令

如果你想：

- 看整个项目结构：`/graphify .`
- 只更新最近变更：`/graphify . --update`
- 只重做社区分析：`/graphify . --cluster-only`
- 持续监听项目变化：`/graphify . --watch`
- 追两个概念如何连起来：`/graphify path "A" "B"`
- 解释一个陌生节点：`/graphify explain "X"`
- 让图谱回答一个开放问题：`/graphify query "..."`
- 沿更深链路追踪：`/graphify query "..." --dfs`
- 控制输出长度：`/graphify query "..." --budget N`
- 把外部网页或论文加入图谱：`/graphify add <url>`
- 导出给 wiki / Obsidian / Neo4j / Gephi：使用对应导出参数
- 让 Claude Code 平时优先参考图谱：`graphify claude install`

## 14. 使用建议

- 第一次使用时，优先构图，再问问题。
- 看结论时，一定区分 `EXTRACTED`、`INFERRED`、`AMBIGUOUS`。
- 如果项目不仅有代码，还有设计文档、论文、截图、白板照片，graphify 的价值会更高。
- 对大型项目，优先用 `--update` 而不是每次全量重跑。
- 如果你是长期维护者，建议结合 `graphify claude install` 和 `graphify hook install` 一起用。

## 15. 一句话总结

可以把 graphify 理解为：先帮 Claude Code 生成一张“项目地图”，再让它沿着地图回答问题，而不是在原始文件里盲搜。

## 参考

* [Graphify开源项目](https://github.com/safishamsi/graphify)
* [AI超元域解说视频](https://www.youtube.com/watch?v=m_5OLW52JwI)
* [AI超元域笔记](https://www.aivi.fyi/llms/graphify)