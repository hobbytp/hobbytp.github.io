
# 智能体设计模式介绍

这里使用卡片式展现智能体设计模式。

## 智能体设计模式背景介绍

我们可以将**智能体设计模式**理解为一套用于构建高级、自主化AI系统的**“架构蓝图”或“可复用的策略手册”** [1, 2, 3]。就像建筑师使用蓝图来建造坚固的房屋，或者软件工程师使用“工厂模式”、“单例模式”来编写可靠的代码一样，AI工程师使用智能体设计模式来构建和组织能够自主思考、规划和行动的AI工作流 [1, 4]。

要完全理解这个概念，我们可以将其拆分为两个部分来理解：**“智能体化 (Agentic)”** 和 **“设计模式 (Design Pattern)”**。

### 1. 什么是“智能体化 (Agentic)”？

“智能体化”描述的是一种新型AI系统的核心特征，它标志着AI从一个被动的工具（你问我答）演变为一个主动的、目标驱动的协作者 [5, 6]。一个“智能体（Agent）”通常具备以下能力：

* **自主性 (Autonomy)**：能够在没有持续人类指令的情况下，为实现特定目标而独立执行多步骤任务 [7]。
* **感知与行动 (Perception and Action)**：能够感知其环境（通过API、数据库、用户输入等），并采取行动（调用工具、执行代码、与外部系统交互）[7]。
* **规划与推理 (Planning and Reasoning)**：其核心“大脑”通常是一个大型语言模型（LLM），能够分解复杂目标、制定行动计划，并根据新信息进行调整 [5, 8, 9]。

简单来说，传统的生成式AI像一个知识渊博但被动的“内容生成器”，而智能体AI则像一个主动的“问题解决者”或“数字员工” [7, 10]。

### 2. 什么是“设计模式 (Design Pattern)”？

在AI领域，“设计模式”是针对构建智能体时遇到的**常见问题所提炼出的、可复用的解决方案** [1, 3]。随着AI工作流变得越来越复杂，开发者们发现他们总是在解决类似的问题：如何让AI自我纠错？如何让多个AI协同工作？如何让AI动态选择最合适的工具？

智能体设计模式就是对这些解决方案的标准化和归纳，它为智能体、工具和工作流的组织方式提供了清晰的架构模板 [11, 4]。

### 为什么智能体设计模式如此重要？

如果没有设计模式，构建复杂的AI系统就像在没有章法的情况下随意堆砌砖块，最终的成品可能会混乱、不可靠且难以维护。设计模式的价值在于：

* **提高可靠性 (Reliability)**：通过标准化的结构，使智能体的行为更可预测，减少“幻觉”和错误 [1, 9]。
* **增强可扩展性 (Scalability)**：模块化的设计使得添加新功能或替换组件变得更加容易，而不会破坏整个系统 [1, 4]。
* **提升可维护性 (Maintainability)**：清晰的架构使得调试和定位问题变得更加简单 [11]。

### 一个核心的设计模式示例：思考-行动-观察循环

最基础也最核心的智能体设计模式之一是 **“思考-行动-观察”（Thought, Action, Observation）循环**，也称为ReAct模式 [11, 12]。这个模式模拟了人类解决问题的基本过程：

1. **思考 (Thought)**：智能体首先分析当前任务和已有信息，进行推理并决定下一步该做什么。例如：“用户想知道旧金山的天气，我的知识库里没有实时信息，所以我需要调用天气查询工具。” [11]
2. **行动 (Action)**：根据思考结果，智能体选择并执行一个具体的动作，通常是调用一个外部工具（如API）。例如：执行 `get_weather(city="San Francisco")` [11, 4]。
3. **观察 (Observation)**：智能体接收并处理行动产生的结果。例如：从API得到返回结果“旧金山当前晴天，15摄氏度。” [11]。

这个“思考-行动-观察”的循环会不断重复，直到智能体认为任务已经完成，然后它会综合所有信息，给出最终答案 [11]。

### 总结

总而言之，**Agentic Design Pattern** 是AI工程领域走向成熟的标志。它将行业的关注点从“如何构建更强大的模型”转向**“如何用模型构建更强大的系统”** [9]。它提供了一套结构化的方法论，帮助开发者将大型语言模型的原始能力，转化为能够可靠、可扩展地解决复杂现实世界问题的、真正自主的AI智能体系统。

## 智能体设计模式介绍模版

**方式一：**

以下是介绍一个设计模式时建议采取的六个关键角度：

```
- 背景与问题：为什么需要这个模式？它解决什么问题？
- 定义与核心思想：这个模式是什么？它的核心思想是什么？
- 结构（UML）：通过UML类图或序列图展示模式的结构。
- 关键参与者：模式中的各个角色及其职责。
- 工作流程：模式如何运作？步骤是什么？
- 代码示例：一个简单的代码示例，展示模式的应用。
- 优缺点：模式的优点和缺点。
- 应用场景：在什么情况下使用这个模式？
- 与其他模式的关系：与其他设计模式的比较或关联。
- 实际应用案例：在真实项目或知名框架/库中的应用。
```

**方式二**

```
- 1. 模式概述与核心概念（Overview & Core Concept）
- 2. 架构与工作流（Architecture & Workflow）
- 3. 价值与核心优势（Value & Key Advantages）
- 4. 适用场景与用例（Use Cases）
- 5. 局限性与设计权衡（Limitations & Trade-offs）
- 6. 实现方式与图形化表示（Implementation & Visualization）
```

**方式三**

更好的介绍方式：融合与优化（The Hybrid Approach）

为了最大化模式文档的有效性、严谨性和实用性，最好的方法是**融合这两种方式的核心优势**，并参考设计模式文档的通用指导原则：

一个优化的模式介绍模板应该像一个**架构决策记录（Architecture Decision Record, ADR）**，侧重于**问题、解决方案、权衡因素和实现蓝图**。

| 优化后的介绍模块 | 目的（解决的问题） |
| :--- | :--- |
| **I. 概述、背景与核心问题（Context & Problem）** | **为什么需要它？** 明确模式解决的 LLM 局限（如幻觉、单步失败、复杂性）。 |
| **II. 核心思想、角色与机制（Core Concept & Workflow）** | **它是什么？** **关键角色**（如 Producer/Critic、Coordinator/Worker） 及其**完整操作循环/流程**（如 ReAct 的 Thought-Action-Observation 循环）。 |
| **III. 架构蓝图与可视化（Architecture & Visualization）** | **它长什么样？** 使用流程图、DAG 或状态图等**现代图形**来清晰展示数据流和控制流（包括循环、节点、条件边）。 |
| **IV. 优势、价值与设计权衡（Value & Trade-offs）** | **好处是什么？代价是什么？** 明确列出其带来的**可靠性、透明度**等优势，以及随之而来的**成本增加**、**延迟**或**架构复杂性**。 |
| **V. 适用场景与选择标准（Use Cases & Selection Criteria）** | **何时使用？** 基于**任务特性**（确定性 vs. 动态性）、**延迟要求**和**质量要求**来指导选择。 |
| **VI. 实现、框架支持与关联模式（Implementation & Relations）**| **如何落地？** 提供**框架支持**（LangGraph、CrewAI 等）和简要的**代码逻辑**。明确说明该模式通常与其他哪些模式**组合使用**（如 Planning 经常与 Sequential 或 Hierarchical 结合）。 |

这种混合方法**结合了方式一的严谨结构和方式二对权衡及实践的关注**，是介绍智能体设计模式的最佳方式，因为它不仅解释了模式的结构，更强调了在实际工程决策中如何应用它。

智能体设计模式的介绍方式，应该在传统的软件工程严谨性（方式一）和新兴的 AI 系统特有的**实用性与权衡分析**（方式二）之间找到最佳平衡点。

以下是对这两种介绍方式的优势分析，以及在此基础上提出的优化建议。

---

### 方式一：传统软件模式模板（Formal Software Pattern Template）

方式一继承了经典软件设计模式（如 GoF 模式）的模板，强调结构、角色和代码实现，具有高度的**严谨性和可追溯性**。

#### 优势

1. **架构严谨性与互操作性：** 明确要求**结构（UML）**，这对于传统的软件架构师和工程师来说，是理解系统组件、关系和交互（如时序）的标准语言。在多智能体系统（MAS）设计模式的文献综述中，**UML** 是图形描述中最常见的建模方式（占图形描述的 73%）。
2. **全面性和可读性：** 通过明确划分**关键参与者**、**工作流程**、**代码示例**和**优缺点**等段落，确保了文档的完整性和结构清晰。
3. **连接传统工程：** 强调**与其他模式的关系**和**实际应用案例**，这有助于将新兴的 Agentic AI 领域与已建立的软件工程实践联系起来，展示其在不同技术环境中的应用潜力。
4. **关注底层实现细节：** 明确包含**代码示例**，能够帮助开发者理解模式如何在具体的编程环境（如 LangChain 或 CrewAI）中被实例化和应用。

#### 局限性

1. **AI 特有权衡不足：** 虽然包含“优缺点”，但可能没有足够强调 **AI 系统特有的设计权衡**，例如**成本、延迟、可靠性**和**可观测性**等核心指标。
2. **UML 适用性挑战：** 智能体工作流往往涉及**动态、非确定性的循环**和**LLM 驱动的决策**。使用传统的 UML 类图或序列图来表示这些**动态控制流**、**状态变化**和**非确定性路由**可能会比较僵硬和复杂，不如流程图或图结构（如 LangGraph 的状态图）直观。

---

### 方式二：智能体实用模式模板（Agentic Practical Template）

方式二更加侧重于模式的**价值、实际应用**和**工程化权衡**，这与当前 Agentic AI 系统架构决策的焦点高度吻合。

#### 优势

1. **强调价值和商业驱动：** 明确突出了**价值与核心优势**，直接回答了“为什么要做”的问题，这对于业务决策者和产品经理至关重要。
2. **核心权衡分析：** **局限性与设计权衡**（Limitations & Trade-offs）是选择智能体模式的**核心依据**。例如，规划模式和层级模式虽然能解决复杂问题，但会显著**增加延迟和运营成本**；而顺序模式则提供了**低延迟和可预测的行为**。方式二明确了这种关键的架构决策因素。
3. **聚焦动态机制：** **架构与工作流**是智能体模式的本质，因为它定义了智能体如何感知、规划和行动。例如，ReAct 模式的核心在于其“思考-行动-观察”的**循环机制**。
4. **可视化指导：** **实现方式与图形化表示**直接关联了抽象模式与具体工程实践，例如使用 LangGraph 的**节点和条件边**来表示循环和路由。

#### 局限性

1. **缺乏严谨的结构分离：** 虽然它涵盖了关键信息，但将“实现方式”和“图形化表示”放在一起，可能不如方式一那样清晰地分离“角色”和“代码示例”。
2. **弱化关联性：** 缺少明确的“与其他模式的关系”一项，这在智能体设计中是一个弱点，因为复杂系统通常是**多种模式的组合**（如 Planning + Reflection + Tool Use）。

---

## 记忆模式

## 一、四大基础设计模式

### 1. **反射模式 (Reflection Pattern)**

* **核心能力**：自我评估和改进

* **功能特点**：
  * 监控过去的行为和结果
  * 识别错误或效率低下的地方
  * 基于反馈调整推理策略或工具使用
* **应用案例**：GitHub Copilot通过自我检查来优化代码，包括生成初始代码、审查错误、运行沙箱测试、优化建议等

### 2. **工具使用模式 (Tool Use Pattern)**

* **核心能力**：扩展智能体能力边界

* **功能特点**：
  * 调用外部API和系统
  * 实时信息访问
  * 执行专门化算法
  * 数据分析和文档生成
* **企业影响**：富士通通过专门化智能体减少提案制作时间67%

### 3. **规划模式 (Planning Pattern)**

* **核心能力**：战略性问题分解

* **功能特点**：
  * 将复杂任务分解为子任务
  * 动态排序和优先级设置
  * 根据中间结果调整计划
* **实施案例**：ContraForce的安全交付平台实现80%的事件调查和响应自动化

### 4. **多智能体协作模式 (Multi-Agent Collaboration Pattern)**

* **核心能力**：通过专业化实现可扩展性

* **编排子模式**：
  * 顺序编排 (Sequential orchestration)
  * 并发编排 (Concurrent orchestration)
  * 群聊/制作-检查模式 (Group chat/maker-checker patterns)
  * 动态交接 (Dynamic handoff)
  * 管理编排 (Managerial orchestration)
* **成功案例**：JM Family的BAQA Genie系统节省60%的QA时间

## 二、高级实现模式

### 1. **记忆增强智能体 (Memory-Augmented Agents)**

* **应用场景**：需要记忆历史上下文的系统

* **实现方式**：向量存储器存储历史交互，生成个性化响应

### 2. **协调器-工作者架构 (Orchestrator-Worker Architecture)**

* **特点**：中心化控制，全局监督

* **功能**：
  * 分解复杂问题
  * 分配任务给专门化工作智能体
  * 综合部分结果生成完整解决方案

### 3. **人在回路集成 (Human-in-the-Loop Integration)**

* **目的**：在关键决策点保留人类判断

* **应用**：特殊业务逻辑或需要人类监督的流程

## 三、实施架构层次

### **技术基础三层架构**

1. **工具层 (Tool Layer)**：与外部数据源和服务接口
2. **动作层 (Action Layer)**：协调LLM与外部世界的交互
3. **推理层 (Reasoning Layer)**：核心智能处理和决策制定

## 四、实施指导原则

### **不同复杂度的应用策略**

* **简单应用**：单智能体架构+工具使用模式

* **复杂工作流**：多智能体监督模式，支持任务委派
* **企业部署**：模块化、可扩展、信任感知设计

## The Different Type of Model Thoughts

<https://medium.com/@Mustafa77/ai-agents-part2-agentic-design-patterns-architectures-11c7a5541042>

These steps come in the form of thoughts, underpinning every action and observation an agent takes. There are different types of thoughts a model can have, specifically:

Planning Thoughts, where models break down a problem into small steps.
e.g., To help them move apartments, I’ll need to find moving companies, compareprices, check availability for their date”
Analysis Thoughts, where models draw insights based on observations. e.g., Looking at their spending patterns, they’re overpaying for subscriptions the rarely use.
Decision-Making Thoughts, where models make specific decisions based on inputs.
e.g., Since they need it by tomorrow, I should suggest express shipping despite theextra cost” e.g., “To optimize this code, I should first profile it to identify bottlenecks.
Problem-Solving Thoughts, where models theorize over what could be the root cause of a problem.
e.g., They mentioned being lactose intolerant last week, so I’ll exclude dairy from these recipe suggestions.
Memory Integration Thoughts, where models remember details stored in their memory.
e.g., They mentioned being lactose intolerant last week, so I’ll exclude dairy from these recipe suggestions.
Self-reflection Thoughts, where models reflect on the style and quality of their output.
e.g., I was too technical in my explanation — let me simplify this using everyday analogies.
Goal-setting Thoughts, where models determine important goals for them to be able to solve the presented objective.
e.g., Before planning their workout routine, I need to understand their fitness level and available time.
Prioritization Thoughts, where models determine the priority levels of different tasks.
e.g., They should book the flights before the hotel, since flight prices increase faster.

英文版：
[github](https://github.com/sarwarbeing-ai/Agentic_Design_Patterns)

[Google Doc](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview?tab=t.0)

中文版：
[github](https://github.com/ginobefun/agentic-design-patterns-cn)

<https://ai.plainenglish.io/agentic-design-patterns-building-intelligent-systems-a-practical-guide-384aab713691>

1 OpenAI, A Practical Guide to Building Agents, <https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>
1 LangGraph Multi Agent Systems, <https://langchain-ai.github.io/langgraph/concepts/multi_agent/>

<https://hdst.medium.com/inside-the-minds-of-machines-agentic-design-patterns-every-ai-builder-should-know-78c10d9f5823>
