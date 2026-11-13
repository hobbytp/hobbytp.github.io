---
title: "Stanford CS329Z：Engineering AI Agents"
date: "2026-11-13T13:35:00+08:00"
draft: false
tags: ["AI", "Agent", "Stanford", "LLM", "系统工程"]
categories: ["courses"]
description: "斯坦福大学 2026 秋季新课 CS329Z《Engineering AI Agents》，系统讲授从基础 LLM 流水线、复合 AI 系统到自主智能体的工程构建、优化、数据飞轮、评测与安全。"
wordCount: 2513
readingTime: 7

ai_cover: "/images/generated-covers/stanford_cs329z_engineering_ai_agents.webp"
cover:
  image: "/images/generated-covers/stanford_cs329z_engineering_ai_agents.webp"
  alt: "Stanford CS329Z：Engineering AI Agents"
  ai_generated: true
---

## **Stanford CS329Z：Engineering AI Agents（AI 智能体工程）**

**课程主页**：[https://cs329z.stanford.edu/](https://cs329z.stanford.edu/)  
**开设学期**：Stanford / Fall 2026（3 学分，课程编号 27855）  
**先修要求**：CS224N、CS224U、CS224V、CS336 或同等自然语言处理（NLP）背景

> 随着 AI 应用从单一语言模型（Monolithic LLMs）向**复合 AI 系统（Compound AI Systems）**演进——即由 LLM、检索器（Retrievers）、工具（Tools）和优化器（Optimizers）等多个组件协同构成的智能系统——AI 应用的构建范式正在发生根本性转变。CS329Z 聚焦“如何工程化构建智能体系统”，覆盖从简单 LLM 流水线、复合 AI 系统到自主智能体（Autonomous Agents）的完整技术光谱。

---

### 👨‍🏫 **授课团队（Instructors & TAs）**

- **授课教师（Instructors）**：
  - [Diyi Yang](https://cs.stanford.edu/~diyiy/)
  - [Michael Ryan](https://michryan.com/)
  - [John Yang](https://john-b-yang.github.io/)
- **助教团队（TAs）**：[Owen Queen](https://owencqueen.github.io/)、[Anusheh Chaudry](https://www.linkedin.com/in/anushehchaudry/)、[Shreyas Sharma](https://www.linkedin.com/in/shreyas-n-sharma/)、[Houjun Liu](https://nlp.stanford.edu/~houjun/)

---

### 📘 **课程大纲与完整日程（Schedule）**

课程在每周一、周三下午 1:30–2:50（Pacific Time）于 Skilling Auditorium 线下授课，共 11 周，涵盖基础模块、设计模式、记忆与多智能体、优化、数据与评测、安全以及代码/个人智能体等前沿专题：

| 周次 | 日期 | 主题与核心内容 | 课件 / 视频 / 代码 |
| :--- | :--- | :--- | :--- |
| **Week 1** | 9/23 (Wed) | **Foundations & Landscape — What Are Agentic Systems?**<br>课程介绍、智能体简史与核心解剖（LLM 核心、推理、记忆、工具、环境）；复合 AI 系统、工作流（Workflows）与智能体（Agents）的区别，以及可靠性、训练、安全与评测挑战。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture01.pdf) · [Video](https://youtu.be/DGI4vucR71w) |
| **Week 2** | 9/28 (Mon) | **LLMs for Builders**<br>面向构建者的语言模型内部机制：解码策略、Transformer 注意力机制（含线性/混合注意力）与上下文长度、预训练到后训练流水线、推理与测试时扩展（Test-time Scaling）、结构化输入输出与受限解码、上下文工程（Context Engineering）。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture02.pdf) · [Video](https://youtu.be/Vr1NzH8bT44) |
| **Week 2** | 9/30 (Wed) | **Building Blocks — Retrieval-Augmented Generation (RAG)**<br>端到端 RAG 流水线：索引（分块、Contextual Retrieval、RAPTOR、HNSW）、从 BM25/DPR 到混合检索、重排序与 ColBERT、Agentic RAG（Self-RAG、Search-R1）及常见失效模式；课程项目概览。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture03.pdf) · [Video](https://youtu.be/psLc-46GqY0) |
| **Week 3** | 10/5 (Mon) | **Tool Use & Function Calling**<br>LLM 工具调用原理与学习方式（Toolformer）、通过 Gorilla 与 ToolLLM 扩展至数千 API、从 REST 到 Function Calling 再到 MCP（Model Context Protocol）的标准接口、使用 BFCL / ToolBench / τ-bench 评测工具调用。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture04.pdf) · [Video](https://youtu.be/s0S38lz6O7M) |
| **Week 3** | 10/7 (Wed) | **Frameworks & Orchestration**<br>智能体工程的数据、系统与评测三大支柱；DSPy（Signatures、Modules、Optimizers）与 LangGraph（State、Nodes、Edges）现场演示；开源 Agent Harness 巡礼（mini-SWE-agent、OpenHands、Pi）、Temporal 持久化编排与可观测性工具。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture05.pdf) · [Code](https://github.com/cs329z/lecture5-frameworks) |
| **Week 4** | 10/12 (Mon) | **Agent Design Patterns & Scaffolds**<br>工作流与智能体设计模式：五种可组合工作流模式、推理与行动模式（ReAct、Reflexion、CodeAct、ReWOO）、上下文管理模式（事件日志、压缩、观测掩码、上下文隔离）及 Pi harness 案例分析。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture06.pdf) |
| **Week 4** | 10/14 (Wed) | **Memory & Multi-Agent Systems — Agent Memory Architectures**<br>四种记忆类型（工作、情景、语义、程序性记忆）；四大架构模式：技能库、类似 MemGPT 的分层记忆、反思性整合（Reflective Consolidation）与记忆维护；遗忘、隐私与过度个性化问题。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture07.pdf) |
| **Week 5** | 10/19 (Mon) | **Multi-Agent Systems**<br>何时使用单智能体 vs 多智能体；编排模式（Orchestrator、Swarm、Hybrid）；通过 Handoffs、消息板与 A2A 协议进行通信；协作基础设施（任务账本、共享内存、Worktree 隔离）及多智能体系统失败原因分析。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture08.pdf) |
| **Week 5** | 10/21 (Wed) | **Optimization**<br>上下文优化（Bootstrapped Few-shot、MIPROv2、OPRO、TextGrad、GEPA）、权重优化（Agent Rollouts 上的 SFT、PPO 与 GRPO 强化学习、On-policy 蒸馏）、Agents as Optimizers（Darwin Gödel Machine、autoresearch），以及何时优化 Prompt vs 权重。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture09.pdf) |
| **Week 6** | 10/26 (Mon) | **Guest Lecture: Terminal-Bench**<br>特邀嘉宾 Ryan Marten 与 Alex Shaw（Laude Institute，Terminal-Bench 联合创始人）分享如何在命令行终端环境中评测 AI 智能体完成真实任务的能力。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture10.pdf) |
| **Week 6** | 10/28 (Wed) | **Data for Agentic Systems — What Data Do Agents Need?**<br>轨迹（Traces）、演示与反馈数据；用于优化 vs 用于评测的数据；数据飞轮（Data Flywheels）、合成数据生成以及从人机交互中采集数据。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture11.pdf) |
| **Week 7** | 11/2 (Mon) | **Data Selection & Quality**<br>寻找信息量最大的数据、过滤与选择策略、小而精的基准测试（Tiny-but-targeted Benchmarks）、标注实践、质量评估与基于 Agent Traces 构建数据集（如 SWE-smith）。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture12.pdf) |
| **Week 7** | 11/4 (Wed) | **Evaluation Fundamentals & Benchmark Design**<br>评测为何困难、**4-Tuple 框架**（Request, Environment, Stopping Criteria, Scorer）设计、优秀基准的属性、真实脚手架（Scaffolding）与可靠性维度。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture13.pdf) |
| **Week 8** | 11/9 (Mon) | **Fireside Chat with Andrew Ng**<br>Diyi Yang 主持与 Andrew Ng（DeepLearning.AI 创始人、Coursera 联合创始人、Google Brain 创始负责人、斯坦福兼职教授）炉边对话。 | — |
| **Week 8** | 11/11 (Wed) | **LLM-as-Judge & Evaluation Infrastructure**<br>三种评分器类型、Judge Prompt 设计、已知偏见、Pairwise vs Pointwise 评测、非确定性指标（`pass@k` vs `pass^k`）、评测 Harness 设计与 Anthropic 8 步评测路线图。 | [Slides](https://web.stanford.edu/class/cs329z/slides/lecture15.pdf) |
| **Week 9** | 11/16 (Mon) | **Guest Lecture: SWE-bench**<br>特邀嘉宾 Carlos Jimenez 与 Alexander Wettig（Anthropic，SWE-bench 作者）探讨代码智能体及更广泛能力评测的演进与未来。 | — |
| **Week 9** | 11/18 (Wed) | **Agent Safety & Guardrails**<br>工具访问的隐私风险、提示词注入（含间接注入）、红队测试、沙箱与权限模型、输出护栏、责任考量、负责任部署与 Human-in-the-loop 模式。 | — |
| **Week 10** | 11/23 & 11/25 | **No Class — Thanksgiving Recess（感恩节假期）** | — |
| **Week 11** | 11/30 (Mon) | **Coding & Software Agents**<br>端到端解析代码智能体（SWE-agent、Claude Code、OpenHands 架构）、作为设计决策的 Scaffolds、SWE-bench 与 4-Tuple 框架实践及软件开发未来。 | — |
| **Week 11** | 12/2 (Wed) | **Personal Agents**<br>从被动响应到主动服务：通用用户模型（GUM）、下一步动作预测（Next Action Prediction）、开源主动个人智能体（如 OpenClaw）、隐私与信任影响及混合主动权（Mixed Initiative）。 | — |
| **Finals** | 12/9 (Wed) | **Final Project Demo Day**<br>期末课程项目现场演示（3:30–6:30 p.m.）。 | — |

---

### 🛠️ **课程实践与考核体系（Coursework & Grading）**

课程极其强调**“从零实现（From Scratch）”与“严谨评测（Rigorous Evaluation）”**：

1. **两次实战编程作业（Homework 15% + 口试测验 Quizzes 15%）**
   - **[HW1: Build an Agentic Harness](https://github.com/cs329z/assignment1-harness)**（第 3–6 周）：**不使用任何 Agent 框架**，仅基于基础的 Chat Completion API 从零构建企业内部 AI 助手——从检索与推理企业邮件归档的 LLM 流水线起步，逐步扩展为具备工具调用、终端（Terminal）、记忆与人类协同（Human-in-the-loop）的完整 Agent Harness。
   - **[HW2: Evaluate an Agent](https://github.com/cs329z/assignment2-harness)**（第 6–9 周）：针对给定预构建智能体设计完整评测套件，包含基于代码的评分器（Code-based Graders）、至少一个 LLM-as-Judge 评测、基于 **4-Tuple 框架**构建的基准任务以及错误模式分析。
   - **HW-based Quizzes**：每次作业后均设 10 分钟闭卷测验，考察学生对自身架构权衡与设计决策的理解。

2. **论文精讲视频与同行评审（Paper Video 10% + Peer Review 20%）**
   - 每位学生需选择一篇近期 Agent 论文录制 10–15 分钟讲解视频（[要求说明 PDF](https://web.stanford.edu/class/cs329z/assignments/paper_video.pdf)）。
   - 整个学期包含 4 轮同行评审（Paper Videos、Midway Demos、HW2 评测集、Final Demos），每轮需按评审表反馈 2 份同学作品。

3. **学期大项目（Course Project 40%）**
   - 推荐 3 人组队（1–3 人），每组配备课程团队导师（Mentor），统一采用 **ICLR 论文格式**提交，并在所有阶段强制附带 **AI-Use Disclosure Statement（AI 使用声明）**。
   - **三大里程碑**：
     - **Proposal（Week 3，5%）**：1–2 页立项报告，明确问题定义、现有方案局限与设计方向。
     - **Midpoint Demo & Midway Report（Week 7，10%）**：录制可运行原型的演示视频 + GitHub 仓库 + 3–4 页中期报告（聚焦环境、数据与评测方法）。
     - **Final Report & Demo Day（Finals Week，25%）**：8 页 ICLR 格式论文（20 分）+ 现场 Demo Day 展示 + **可复现性评分（5 分）**（助教将直接按仓库 README 在单任务实例上运行验证）。

---

### 🚀 **课程特色与技术亮点**

- **从手写轮子到框架抽象**：先在 HW1 中手写 RAG、Tool Use 与 Agent Loop 理解底层工程权衡，再在 Lecture 5 切入 DSPy 与 LangGraph 等声明式/图编排框架，避免“只会调包不懂原理”。
- **紧贴 2025–2026 最前沿研究与工程实践**：课程阅读列表大量收录最新论文与工业界工程博客，涵盖 Anthropic（*Building Effective Agents*、*Effective Context Engineering*、*Claude Code Best Practices*、*Demystifying Evals*）、MCP 协议、Terminal-Bench、SWE-smith、GEPA 反射式提示词进化、AutoMetrics 以及主动式个人智能体等。
- **把“数据与评测”提升到与“架构”同等高度**：专门用两周时间系统讲授 Agent 数据飞轮、Traces 采集、4-Tuple 基准设计与 LLM-as-Judge 基础设施，直击现实中 Agent “Demo 惊艳、生产不可靠”的痛点。

---

### 📚 **参考链接**

- 课程官网：[Stanford CS329Z: Engineering AI Agents](https://cs329z.stanford.edu/)
- 课程安排与政策：[Course Logistics](https://cs329z.stanford.edu/logistics.html)
- 课程项目指南：[Course Project](https://cs329z.stanford.edu/project.html)
- 开源作业与代码示例：
  - [Lecture 5 Frameworks Code](https://github.com/cs329z/lecture5-frameworks)
  - [HW1: Build an Agentic Harness](https://github.com/cs329z/assignment1-harness)
  - [HW2: Evaluate an Agent](https://github.com/cs329z/assignment2-harness)
