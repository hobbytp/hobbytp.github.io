---
title: "Nanobot 深度剖析：如何用 4000 行代码构建超轻量级个人 AI 助理"
date: 2024-03-15
tags: ["AI Agent", "nanobot", "OpenClaw"]
categories: ["projects"]
description: "Nanobot 是一个超轻量级的个人 AI 助理框架，仅用 4000 行代码实现了 ReAct 循环、多渠道消息总线、工具/技能系统、长短期记忆、子智能体协同等功能。可以看成是 OpenClaw 的极简版，是一个非常好的学习项目。"
wordCount: 2183
readingTime: 6
---


## 1. 引言：从 OpenClaw 到 Nanobot 的极简演进

在 AI Agent（智能体）框架的探索中，**OpenClaw (Clawdbot)** 曾以其强大的功能和复杂的架构（43万+行代码）树立了一个标杆。然而，对于许多开发者而言，这种"巨无霸"级别的框架往往意味着极高的理解门槛和维护成本。

开发者需要的往往不是一个"什么都能做"的庞然大物，而是一个**"足够小、足够快、足够好改"**的内核。

**Nanobot (纳米机器人)** 正是基于这一理念诞生的**超轻量级 (Ultra-Lightweight)** 个人 AI 助理框架。它的核心设计哲学是 **"Less is More"**：仅用约 **4000 行核心代码**（不到 OpenClaw 的 1%），就复刻了 Agent 的核心能力，实现了包括 **ReAct 循环、多渠道消息总线、工具/技能系统、长短期记忆、子智能体协同** 在内的完整功能体系。

本文将以资深架构师的视角，带你深入剖析 Nanobot 的源码架构，看看它是如何以极简的代码量，实现与 **Gemini CLI / OpenCode** 类似的强大 Agent 架构，并保持极高的可扩展性。

## 2. 核心架构：极简主义的胜利

Nanobot 的架构呈现出一种清晰的 **"三明治"** 结构，极大地降低了各模块间的耦合度。

![Architecture](nanobot_arch.png)

### 2.1 消息总线 (Message Bus)：解耦的艺术

在 `nanobot/bus` 模块中，Nanobot 实现了一个基于 `asyncio` 的异步消息总线。这是整个系统解耦的关键。

- **Inbound Queue (入站队列)**：所有的外部输入（Telegram 消息、CLI 命令、定时任务触发）都被封装为统一的 `InboundMessage` 对象，推入此队列。Agent 核心循环只通过 `consume_inbound()` 消费消息，完全不关心消息来自哪里。
- **Outbound Queue (出站队列)**：Agent 的所有输出（回复文本、工具结果）被封装为 `OutboundMessage` 对象，推入此队列。Channel Manager 监听此队列，根据 `channel_id` 将消息路由回对应的平台（如调用 Telegram API 发送回复）。

这种设计使得 **Agent Core（大脑）** 与 **Channels（手脚）** 彻底分离。增加一个新的聊天渠道（如 Slack 或 WeChat），只需编写一个适配器将 API 数据转换为 `InboundMessage`，无需修改任何核心逻辑。

### 2.2 Agent Loop (大脑循环)：ReAct 的精炼实现

`nanobot.agent.loop.AgentLoop` 是整个系统的心脏。

> **架构对比：Nanobot vs. Gemini CLI / OpenCode**
> 
> 如果你熟悉 **Gemini CLI** 或 **OpenCode** 的架构，你会发现 Nanobot 的 Agent Loop 设计与之如出一辙，体现了现代 Agent 架构的共识：
> 1.  **Event-Driven**: 都是基于事件驱动的消息处理循环。
> 2.  **Context Construction**: 都强调动态上下文构建（Identity + Context + History）。
> 3.  **Tool Use**: 都依赖 LLM 的 Function Calling 能力来驱动外部操作。
> 
> Nanobot 的独特之处在于其**极致的精简**。它剥离了复杂的图编排和多余的抽象层，回归了最本质的 `while` 循环，使得核心逻辑在 `loop.py` 中仅用 300 多行代码就清晰地表达了出来。

Agent Loop 的具体流程如下：

1.  **Wait**: 异步等待总线上的新消息。
2.  **Context**: 使用 `ContextBuilder` 动态组装上下文。这包括：
    -   系统提示词 (System Prompt)：包含身份定义、时间、环境信息。
    -   记忆 (Memory)：加载短期（今日）和长期记忆。
    -   技能 (Skills)：加载当前激活的技能描述。
    -   历史记录 (History)：加载当前会话的上下文。
3.  **Think (LLM Call)**: 将组装好的 Messages 发送给 LLM。
4.  **Act (Tool Execution)**: 检测 LLM 是否返回了 `tool_calls`。
    -   如果有，通过 `ToolRegistry` 查找并执行对应工具（如 `web_search`, `read_file`）。
    -   将执行结果封装为 `Tool Message` 追加到上下文，**再次进入 Think 阶段**（ReAct 循环）。
    -   循环直到 LLM 输出最终文本或达到最大迭代次数。
5.  **Respond**: 将最终结果推送到 `Outbound Queue`。

这段逻辑在 `loop.py` 中仅用 300 多行代码就清晰地表达了出来，没有任何黑魔法，极其适合源码阅读和教学。

## 3. 关键特性与实现原理

除了核心循环，Nanobot 在几个关键子系统的设计上也颇具巧思。

### 3.1 LLM 抽象：Registry 模式的单一事实来源

在 `nanobot.providers` 中，开发者可能会惊讶地发现没有复杂的工厂模式或大量的继承类。Nanobot 采用了一个 `registry.py` 文件作为 **"单一事实来源 (Single Source of Truth)"**。

-   **ProviderSpec**: 使用 `dataclass` 定义了每个 Provider 的元数据（名称、Env Var Key、模型前缀、API Base 等）。
-   **LiteLLM 集成**: 底层复用强大的 `litellm` 库，上层通过 `LiteLLMProvider` 类根据 Registry 中的配置动态调整环境变量和参数。

这种设计使得添加一个新的 LLM Provider 变得异常简单：**只需在 `registry.py` 的元组中添加一项配置**。无需编写新的 Class，无需修改逻辑代码。对于 DeepSeek、Moonshot (Kimi)、Qwen 等国产模型或是 OpenRouter 这样的网关，都能通过简单的配置无缝接入。

### 3.2 技能系统 (Skills)：Markdown 即代码

Nanobot 的技能系统 (`nanobot/agent/skills.py`) 采用了一种非常具有 "Agent Native" 风格的设计：**技能即文档**。

每个技能本质上是一个目录下的 `SKILL.md` 文件。这个 Markdown 文件包含了：
-   **元数据 (Frontmatter)**: 定义技能名称、描述、依赖项（如需要安装 `ffmpeg`）。
-   **Prompt**: 自然语言描述的技能使用说明，教会 LLM 何时及如何使用特定工具。

当 Agent 启动时，`SkillsLoader` 会扫描这些文件。对于标记为 `always=true` 的核心技能，内容会被直接注入 System Prompt。对于其他技能，Agent 会先看到一个摘要列表，当它认为需要使用某项技能时，会主动调用 `read_file` 工具去读取 `SKILL.md` 的详细内容——这模拟了人类查阅手册的学习过程，大大节省了 Token 开销。

### 3.3 记忆系统 (Memory)：长短结合

记忆是 Agent 拥有"灵魂"的关键。Nanobot 的 `MemoryStore` (`nanobot/agent/memory.py`) 实现了轻量级的双层记忆：

1.  **短期/每日记忆 (`memory/YYYY-MM-DD.md`)**:
    -   自动按日期归档。
    -   记录当天的临时笔记、待办事项和即时上下文。
    -   类似于人类的"工作记忆"或"日记"。

2.  **长期记忆 (`memory/MEMORY.md`)**:
    -   存放用户偏好、重要事实、长期计划。
    -   Agent 会被 Prompt 引导将重要信息显式写入此文件。
    -   类似于人类的"海马体"转存后的长期记忆。

这种基于文件系统的记忆实现虽然简单，但对于个人助理场景极其有效。用户可以直接用编辑器查看和修改记忆文件，透明且易于管理。

### 3.4 子智能体 (Subagents)：分身有术

当面对复杂的耗时任务（如"调研一下市面上所有的开源 Agent 框架并写份报告"）时，单线程的 Agent 往往会因为上下文过长或等待时间过久而卡住。

Nanobot 引入了 **Subagent (`nanobot/agent/subagent.py`)** 机制。主 Agent 可以调用 `spawn_subagent` 工具，在后台启动一个独立的 Agent 实例。
-   **独立上下文**: Subagent 拥有全新的、干净的上下文窗口，只包含任务描述和必要的工具。
-   **后台执行**: 主 Agent 可以继续响应用户的其他请求，不必阻塞等待。
-   **结果回调**: Subagent 完成任务后，会通过 `system` 消息通道将结果"汇报"给主 Agent，主 Agent 再决定如何通知用户。

这实现了类似操作系统的多进程并发模型，极大地提升了 Agent 处理复杂任务的能力。

## 4. 多渠道接入：Bridge 连接世界

为了让 Agent 无处不在，Nanobot 支持了 Telegram, Discord, Slack, WhatsApp, Feishu, DingTalk 等多种渠道。

实现上，Nanobot 采用了混合策略：
-   **Native Integrations**: 对于提供完善 Python SDK/API 的平台（如 Telegram, Discord, Feishu），直接在 `nanobot/channels` 中实现适配器。
-   **Bridge Integrations**: 对于像 WhatsApp 这样较难直接接入的平台，Nanobot 提供了一个独立的 `bridge/` (Node.js) 服务，通过 WebSocket 与主进程通信。

这种灵活的架构保证了核心 Python 代码的纯净，同时又能利用生态中最成熟的库来接入各种 IM 平台。

## 5. 总结

Nanobot 像是一把精致的瑞士军刀。它没有试图去造一个"无所不能"的重型机械，而是专注于提供一个**清晰、可扩展、易于理解**的 Agent 核心框架。

对于开发者而言，4000 行代码不仅是功能的载体，更是学习 Agent 架构的绝佳教材。你可以在一个周末读完所有源码，完全理解它的运作机制，并根据自己的需求随意魔改——这正是开源最迷人的地方。

在这个 AI 快速迭代的时代，也许这种轻量级、模块化、可掌控的代码库，才是构建个人 AI 应用的最佳基石。

---
**项目地址**: [https://github.com/HKUDS/nanobot](https://github.com/HKUDS/nanobot)  
**安装**: `pip install nanobot-ai`
