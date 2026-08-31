---
title: "Matt Pocock Skills 使用指南"
date: "2026-08-24T12:00:00+08:00"
draft: false
tags: ["Matt Pocock", "AI Skills", "Agent Workflow"]
categories: ["ai_programming"]
description: "从需求澄清、规格拆分到实现、测试和复盘，系统介绍 Matt Pocock Skills 的工程与内容工作流。"
---

入口关系已经清楚：工程侧是一条“澄清 → 规格化 → 拆票 → 实现 → 测试/审查”的主链；生产力侧更像可插入任何工作的沟通与知识管理层。现在补看这些通用 skill 的实际产物和边界，避免把它们描述成并不存在的自媒体专用工具。

> **视觉学习版：** [进入 Matt Pocock Skills 视觉学习系统](/zh/ai_programming/mattpocock-skills-visual-learning/)，通过 12 张工作地图理解入口选择、功能流、架构决策、调试和持续维护。



这套 skills 最适合被理解成一套“工作流操作系统”，而不是一堆零散命令。核心原则是：

> 先澄清，再形成可验证的产物；先切小，再执行；始终保留反馈和复盘。

## 一、先完成一次性配置

在每个代码仓库中先运行：

```text
/setup-matt-pocock-skills
```

它会配置：

- 使用 GitHub、Linear 还是本地文件作为 issue tracker
- triage 使用的标签
- `CONTEXT.md`、ADR 等文档的保存位置

之后遇到不确定该用什么 skill，可以直接运行：

```text
/ask-matt
```

它本身就是总路由器，定义在 ask-matt/SKILL.md。

## 二、软件开发主流程

### 1. 想法或需求还比较模糊

使用：

```text
/grill-with-docs
```

它会通过连续提问澄清：

- 用户真正要解决的问题
- 边界和异常情况
- 领域术语
- 已经做出的重要决定

同时维护：

- `CONTEXT.md`
- 领域词汇
- ADR 决策记录

如果没有代码仓库，只是讨论一个想法，则使用：

```text
/grill-me
```

### 2. 需要先验证设计

如果问题无法靠讨论解决，例如：

- UI 到底应该长什么样
- 状态机是否合理
- 某种交互是否自然
- 一个算法方案是否可行

使用：

```text
/prototype
```

原型的目标不是直接写生产代码，而是回答一个具体问题。

### 3. 工作规模较大

如果任务超过一个 session 的承载能力：

```text
/to-spec
/to-tickets
```

`/to-tickets` 会把工作拆成可独立验证的纵向切片，并明确每个 ticket 的阻塞关系。

如果是大型、方向还不清楚的项目，则先用：

```text
/wayfinder
```

它先解决“有哪些关键决策”，而不是直接开始写代码。

### 4. 开始实现

```text
/implement
```

它会：

- 根据 spec 或 ticket 开始实现
- 内部使用 `/tdd`
- 按一个个垂直切片推进
- 最后运行 `/code-review`
- 在完成后提交变更

如果只是一个很具体的小行为，也可以直接使用：

```text
/tdd
```

### 5. 代码出问题

普通问题可以直接描述给 agent。对于难复现、回归或性能问题，使用：

```text
/diagnosing-bugs
```

它要求先建立一个能够稳定失败的反馈回路，再经历：

```text
复现 → 缩小范围 → 提出假设 → 加 instrumentation → 修复 → 回归测试
```

### 6. 持续维护代码质量

每隔几天运行：

```text
/improve-codebase-architecture
```

它会扫描代码库，找出适合“加深模块边界”的位置。选定一个候选后，再回到：

```text
/grill-with-docs
```

然后进入 spec、ticket、实现流程。

## 三、一个实际的软件开发例子

比如你想做“团队邀请功能”：

```text
/grill-with-docs
```

明确邀请者、被邀请者、过期、重复邀请等规则。

```text
/prototype
```

验证邀请状态和 UI 是否合理。

```text
/to-spec
```

形成正式需求。

```text
/to-tickets
```

拆成：

1. 创建邀请
2. 发送邀请邮件
3. 接受邀请
4. 处理过期和重复邀请

```text
/implement
```

逐个实现，每个 ticket 内部走 TDD。

```text
/code-review
```

从“是否符合规范”和“是否符合原始 spec”两个维度检查。

这条主链可以概括为：

```text
想法
  → grill-with-docs
  → prototype（必要时）
  → to-spec
  → to-tickets
  → implement
  → tdd
  → code-review
```

## 四、自媒体日常工作的用法

仓库目前没有专门针对“小红书、公众号、视频脚本”的 skills，所以不要把工程 skill 生搬硬套。更合适的方式是使用它们的思考和反馈机制。

### 选题和内容定位

```text
/grill-me
```

用来追问：

- 这篇内容服务谁
- 读者看完要获得什么
- 为什么现在要发布
- 你的独特观点是什么
- 哪些内容不应该写

### 资料研究

```text
/research
```

适合调查：

- 行业事实
- 一手资料
- 竞品内容
- 平台规则
- 用户痛点

让它把来源和结论沉淀成 Markdown，之后再写内容，而不是边搜边凭印象创作。

### 采访和获取外部信息

```text
/to-questionnaire
```

适合把你需要从客户、专家、用户那里获得的信息，整理成一份可以异步发送的问卷。

例如：

- 用户为什么购买
- 使用前后的变化
- 最常见的阻碍
- 哪句话最能描述真实体验

### 内容生产

可以把每篇内容当作一个小型“纵向切片”：

```text
选题
  → 明确受众和结果
  → research
  → 形成观点
  → 写初稿
  → 让 agent 挑战反例
  → 发布
  → 记录数据和反馈
```

建议在内容工作区维护：

```text
content/
  ideas.md
  research/
  drafts/
  published/
  learnings.md
  CONTEXT.md
```

其中：

- `ideas.md` 保存选题池
- `research/` 保存有来源的调研
- `drafts/` 保存不同版本
- `published/` 保存最终稿和发布时间
- `learnings.md` 记录哪些标题、结构、观点有效
- `CONTEXT.md` 保存你的受众、语气、栏目和禁区

### 长期学习和能力建设

```text
/teach
```

适合建立持续学习项目，例如：

- 学习视频剪辑
- 学习写标题
- 学习个人品牌定位
- 学习某个专业领域

它会维护课程、参考资料、学习记录和练习结果，而不是只回答一次问题。

### 沟通没有对齐

```text
/wait-what
```

当你觉得 agent 的解释没有落地时使用。它会用更简单的语言，结合 `CONTEXT.md` 中已经约定的术语重新解释。

### 跨 session 或跨 agent 工作

```text
/handoff
```

适合：

- 把选题交给另一个 session
- 把调研交给写作 session
- 把脚本交给剪辑环节
- 把工作交给同事或其他 agent

## 五、推荐的日常节奏

### 软件开发

- 每个新需求：`/grill-with-docs`
- 大需求：`/to-spec` → `/to-tickets`
- 实现：`/implement`
- 难 bug：`/diagnosing-bugs`
- 每几天：`/improve-codebase-architecture`
- 合并前：`/code-review`

### 自媒体

- 每周选题会：`/grill-me`
- 需要事实支持：`/research`
- 需要用户或专家信息：`/to-questionnaire`
- 跨人或跨 session：`/handoff`
- 每周复盘：让 agent 对比 `published/` 和 `learnings.md`
- 长期能力提升：`/teach`

最重要的是不要每次都调用所有 skills。先用 `/ask-matt` 判断自己处于哪个阶段，再调用对应的一个或两个 skill。这样这套系统才会成为稳定的工作节奏，而不是额外的流程负担。
