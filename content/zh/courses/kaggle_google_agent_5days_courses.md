---
title: "Kaggle 5-Day AI Agents Intensive（Google）课程笔记"
date: "2025-12-21T22:00:00+08:00"
draft: false
tags: ["Kaggle", "Google", "AI Agents", "Gemini", "ADK", "MCP", "A2A", "课程"]
categories: ["courses"]
description: "Kaggle Learn Guide：Google 5 天 AI Agents 强化课程中文整理（Setup + Day1~Day5），覆盖 agents 基础、工具与 MCP、上下文工程、质量评估与可观测性、从原型到生产与 A2A 协议，并保留原始资源链接。"
---


## 课程简介

本课程来自 Kaggle Learn Guide：**5-Day AI Agents Intensive Course with Google**。

- 课程形式：5 天强化学习（最初为 2025-11-10 ~ 2025-11-14 直播），现在可按自学节奏学习
- 课程目标：理解并动手实践 AI agent 的核心组件（模型、工具、编排、记忆、评估），并掌握从 LLM 原型走向可生产化系统的方法
- 学习方式：每天包含概念讲解 + 白皮书 + 配套 codelab/Notebook（部分天数有可选的录播直播）

原始课程页（英文）：

- [Kaggle Learn Guide：5-Day Agents](https://www.kaggle.com/learn-guide/5-day-agents)


## 为期5天的人工智能代理密集课程

与谷歌合作的为期5天的人工智能代理密集课程是一个动手实践的项目，最初于2025年11月10日至14日举行。现在它作为一个自我节奏的Kaggle学习指南提供，任何人都可以探索人工智能代理的基础、架构和实用开发。
该课程由谷歌的机器学习研究人员和工程师设计，旨在帮助开发人员探索人工智能代理的基础和实际应用。你将学习核心组件——模型、工具、编排、内存和评估。最后，你将发现代理如何超越大型语言模型原型，成为生产就绪的系统。
每天的课程结合了概念深入探讨与动手实践的示例、代码实验室和现场讨论。到最后，你将准备好构建、评估和部署解决现实世界问题的代理。

## 涵盖哪些内容？

- 第1天 - **代理简介**：探索人工智能代理的基础概念、它们的定义特征，以及代理架构如何与传统的LLM应用程序不同，为构建智能、自治系统奠定基础。

- 第2天 - **代理工具与模型上下文协议（MCP）的互操作性**：深入了解工具的世界，理解人工智能代理如何通过利用外部功能和API "采取行动"，并探索MCP所提供工具的发现和使用的简便性。

- 第3天 - **上下文工程（Context Engineering）**：会话与记忆：探索如何构建能够记住过去互动并保持上下文的人工智能代理。学习如何实现短期和长期记忆，以创建更强大的代理，能够处理复杂的、多轮任务。

- 第4天 - **代理质量**：评估与可观测性：本节将介绍代理质量：学习通过掌握评估和改进代理的关键学科来构建健壮且可靠的人工智能代理。本节将涵盖可观察性、日志记录和追踪，以提供可见性，以及优化代理性能的关键指标和评估策略。

- 第5天 - **原型到生产**：超越本地测试，学习如何为实际应用部署和扩展人工智能代理。本节将涵盖部署代理的最佳实践，以便他人能够使用它们，包括如何使用Agent2Agent（A2A）协议创建真正的多代理系统。


## 课前准备（Setup Instructions）

为了确保你可以顺利完成 codelab，请先完成以下准备：

1. Kaggle 账号
   - [注册 Kaggle](https://www.kaggle.com/)
   - [了解 Kaggle Notebooks（视频）](https://www.youtube.com/watch?v=BPQDZLPtgDc)
   - [完成手机号验证（codelab 必需）](https://www.kaggle.com/settings)
2. Google AI Studio 账号
   - [注册/登录](https://aistudio.google.com/)
   - [创建 API Key](https://aistudio.google.com/app/apikey)
3. Kaggle Discord
   - [加入 Kaggle Discord（交流与协作）](http://discord.gg/kaggle)

## Day 1：Introduction to Agents（Agent 入门）

本白皮书介绍了人工智能代理。它提出了代理能力的分类法，强调了为确保可靠性和治理而建立代理运维（Agent Ops）规范的必要性，并探讨了通过身份和受限策略实现代理互操作性和安全性的重要性。

在代码实验室中，你将使用由Gemini提供支持的代理开发工具包（ADK）构建你的第一个人工智能代理和第一个多代理系统，并使其能够使用谷歌搜索来回答包含最新信息的问题。在第二个代码实验室中，重点将是多代理系统，你将学习如何创建专业代理团队并探索不同的架构模式。

### Day 1 核心内容

- 介绍 AI agent 的基本概念与能力分级（taxonomy）
- 强调 Agent Ops（可靠性/治理）的重要性
- 讨论 agent 的互操作性与安全：身份（identity）与约束策略（constrained policies）

### Day 1 动手实践（codelabs）

- 使用 **Agent Development Kit（ADK）** + **Gemini** 构建你的第一个 agent，并让它通过 **Google Search** 获取最新信息
- 构建第一个多智能体系统：组建“专业分工”的 agent 团队，理解不同的多 agent 架构模式

### Day 1 作业（Assignments）

1. [播客（本单元摘要）](https://www.youtube.com/watch?v=zTxvGzpfF-g)
2. [“Introduction to Agents” 白皮书](https://www.kaggle.com/whitepaper-introduction-to-agents)
3. Codelab / Notebook
   - [Day 1a（From prompt to action）](https://www.kaggle.com/code/kaggle5daysofai/day-1a-from-prompt-to-action)
   - [Day 1b（Agent architectures）](https://www.kaggle.com/code/kaggle5daysofai/day-1b-agent-architectures)

### Day 1 注意事项

- 开始前请确认已完成 [Kaggle 手机号验证](https://www.kaggle.com/settings)
- 常见问题排查：[Troubleshooting / FAQs](https://www.kaggle.com/code/kaggle5daysofai/day-0-troubleshooting-and-faqs)
- 可选阅读：[NotebookLM “互动对话”功能说明](https://support.google.com/notebooklm/answer/15731776)

## Day 2：Agent Tools & Interoperability with Model Context Protocol (MCP)

本白皮书聚焦于外部工具功能，这些功能使智能体能够执行超出其训练数据集范围的操作或获取实时数据，并介绍了设计高效工具的最佳实践。您将了解模型上下文协议（MCP），重点了解其架构组件、通信层、风险以及企业就绪差距。

在代码实验室中，您将通过将自己的Python函数转化为智能体可执行的操作，为您的智能体创建自定义工具。您还将使用模型上下文协议（MCP）并实现长期运行的操作，在此过程中，智能体可以在等待人工批准时暂停工具调用，之后再恢复运行。

### Day 2 核心内容

- 理解“工具（tools / functions）”如何让 agent 执行动作或获取训练集之外的实时信息
- 学习工具设计的最佳实践
- 介绍 MCP（Model Context Protocol）：组件、通信层、风险与企业落地差距

### Day 2 动手实践（codelabs）

- 把你的 Python 函数变成 agent 的可调用动作
- 使用 MCP，并实现需要“人类批准后继续”的长耗时操作（long-running operations）

### Day 2 作业（Assignments）

1. [播客（本单元摘要）](https://www.youtube.com/watch?v=Cr4NA6rxHAM)
2. [“Agent Tools & Interoperability with Model Context Protocol (MCP)” 白皮书](https://www.kaggle.com/whitepaper-agent-tools-and-interoperability-with-mcp)
3. Codelab / Notebook
   - [Day 2a（Agent tools）](https://www.kaggle.com/code/kaggle5daysofai/day-2a-agent-tools)
   - [Day 2b（Tools best practices + MCP + long-running ops）](https://www.kaggle.com/code/kaggle5daysofai/day-2b-agent-tools-best-practices)

### Day 2 可选：录播直播

- [YouTube livestream](https://www.youtube.com/live/8Gk1BE3uYek)
- 嘉宾讨论中提到的外部团队：[Reified](https://reifiedllc.com/)

## Day 3：Context Engineering: Sessions & Memory（上下文工程：会话与记忆）

这篇白皮书探讨了上下文工程作为动态组装和管理代理上下文窗口内信息的实践，以创建有状态和个性化的人工智能体验。它将会话定义为单个即时对话历史的容器，将记忆定义为长期持久性机制。

在代码实验中，您将学习如何通过在ADK中进行上下文工程来管理对话历史，使代理有状态，并在会话中工作记忆，使您的代理能够记住上下文并进行连贯的多轮对话。在第二个笔记本中，您将为您的代理提供跨不同会话持久的长期记忆。
### Day 3 核心内容

- 上下文工程（Context Engineering）：动态组装与管理上下文窗口信息，打造“有状态”的个性化体验
- Sessions：单次对话历史的容器
- Memory：跨会话的长期持久化机制

### Day 3 动手实践（codelabs）

- 在 ADK 中通过上下文工程管理对话历史，让 agent 具备多轮对话一致性
- 为 agent 增加长期记忆，使其跨 sessions 也能记住信息

### Day 3 作业（Assignments）

1. [播客（本单元摘要）](https://www.youtube.com/watch?v=FMcExVE15a4)
2. [“Context Engineering: Sessions & Memory” 白皮书](https://www.kaggle.com/whitepaper-context-engineering-sessions-and-memory)
3. Codelab / Notebook
   - [Day 3a（Agent sessions）](https://www.kaggle.com/code/kaggle5daysofai/day-3a-agent-sessions)
   - [Day 3b（Agent memory）](https://www.kaggle.com/code/kaggle5daysofai/day-3b-agent-memory)

### Day 3 可选：录播直播

- [YouTube livestream](https://www.youtube.com/live/8o-GXj8A3nE)
- 嘉宾讨论中提到的外部团队：[Cohere](https://cohere.com/)

## Day 4：Agent Quality（Agent 质量）

本白皮书通过引入一个全面的评估框架，解决了确保人工智能代理质量的挑战。实现这一目标所需的技术基础是可观测性，它建立在三大支柱之上：日志（日志记录）、追踪（叙事记录）和指标（健康报告），借助大语言模型即评判者（LLM-as-a-Judge）和人机协同（HITL）评估等可扩展方法，形成持续的反馈循环。

在代码实验室中，你将学习如何使用日志、追踪和指标来全面了解代理的决策过程，从而能够调试故障并理解代理行为方式的原因。在第二个代码实验室中，你将学习如何评估代理，以对代理的响应质量和工具使用情况进行评分。

### Day 4 核心内容

- 如何系统性保证 agent 质量：提出整体评估框架
- 可观测性（Observability）三支柱：
  - Logs（日志：像日记）
  - Traces（链路：像叙事）
  - Metrics（指标：像体检报告）
- 结合 LLM-as-a-Judge 与 Human-in-the-Loop（HITL）形成持续反馈闭环

### Day 4 动手实践（codelabs）

- 使用 logs / traces / metrics 观察并调试 agent 的决策过程
- 评估 agent：为回答质量与工具使用打分

### Day 4 作业（Assignments）

1. [播客（本单元摘要）](https://www.youtube.com/watch?v=LFQRy-Ci-lk)
2. [“Agent Quality” 白皮书](https://www.kaggle.com/whitepaper-agent-quality)
3. Codelab / Notebook
   - [Day 4a（Agent observability）](https://www.kaggle.com/code/kaggle5daysofai/day-4a-agent-observability):实施可观测性以帮助你调试智能体。
   - [Day 4b（Agent evaluation）](https://www.kaggle.com/code/kaggle5daysofai/day-4b-agent-evaluation):评估你的智能体，评估其质量并获取反馈。

### Day 4 可选：录播直播

- [YouTube livestream](https://www.youtube.com/live/JW1Yybfxyr4)
- 嘉宾讨论中提到的外部团队：[NVIDIA](https://www.nvidia.com/)

## Day 5：Prototype to Production（从原型到生产）

本白皮书提供了一份关于人工智能代理运行生命周期的技术指南，重点关注部署、扩展和产品化。它探讨了将智能代理系统从原型转变为企业级解决方案所面临的挑战，并特别关注了Agent2Agent（A2A）协议。

在代码实验室中，您将学习如何构建由多个独立代理组成的系统，这些代理能够使用A2A协议进行通信和协作。您还将学习如何通过将代理部署到谷歌云的Vertex AI Agent Engine，将您的代理从本地机器转变为可投入生产、可扩展的服务。

### Day 5 核心内容

- agent 的生产化生命周期：部署、扩缩容、工程化
- 从原型到企业级系统的挑战
- 重点介绍 A2A（Agent2Agent）Protocol：构建真正的多 agent 协作系统

### Day 5 动手实践（codelabs）

- 使用 A2A Protocol 构建可通信协作的多 agent 系统
- 将 agent 部署到 Google Cloud 的 Vertex AI Agent Engine（可选）

### Day 5 作业（Assignments）

1. [播客（本单元摘要）](https://www.youtube.com/watch?v=8Wyt9l7ge-g)
2. [“Prototype to Production” 白皮书](https://www.kaggle.com/whitepaper-prototype-to-production)
3. Codelab / Notebook
   - [Day 5a（A2A communication）](https://www.kaggle.com/code/kaggle5daysofai/day-5a-agent2agent-communication)：使用 A2A Protocol 构建可通信协作的多 agent 系统。
   - （Optional）[Day 5b（Agent deployment）](https://www.kaggle.com/code/kaggle5daysofai/day-5b-agent-deployment)：部署你的Agent到Google Cloud的Agent Engine。

### Day 5 可选：录播直播

- [YouTube livestream](https://www.youtube.com/live/4XjPh5or0ws)

## 完成后

课程页的祝贺与结语：

- [Kaggle Learn Guide：5-Day Agents](https://www.kaggle.com/learn-guide/5-day-agents)
