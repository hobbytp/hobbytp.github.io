+++
title = "Agent2Agent (A2A) 协议"
date = "2025-04-11T20:10:00+08:00"
draft = false
tags = ["AI", "Agent", "A2A", "协议", "技术"]
categories = ["Agent", "A2A"]
description = "本文介绍了Google推出的新一代Agent2Agent (A2A) 协议，并对其技术原理、主要贡献、论文方法、评估结果和局限性进行了详细解读。"
+++

## 什么是 Agent2Agent (A2A) 协议？

A2A 协议是一种旨在实现人工智能代理之间无缝通信和协作的开放标准。它定义了一套通用的消息传递格式和交互模式，使得不同的 AI 代理能够相互发现、协商能力、执行任务并共享结果，从而更有效地完成复杂的最终用户请求。该协议旨在促进构建更强大、更通用的代理系统，这些系统可以跨越不同的环境和平台协同工作。

### A2A 协议是如何工作的？

A2A 协议主要围绕客户端代理和远程代理之间的交互。客户端代理发起任务，而远程代理则执行这些任务并提供结果。这个过程通常包括以下几个关键步骤：**能力发现**（通过代理卡广告代理的能力）、**任务管理**（使用任务对象跟踪任务的生命周期和状态）、**协作**（代理之间交换包含内容和指令的消息）以及 **用户体验协商**（代理协商内容格式和用户界面能力）。对于长时间运行的任务，代理可以通过轮询或推送通知来保持同步。任务的结果以“工件”的形式返回。

### 什么是“代理卡 (Agent Card)”？它的作用是什么？

代理卡是一个 JSON 格式的文档，远程代理使用它来宣传自身的能力、技能以及认证机制。客户端代理通过查询代理卡的 URL（通常托管在 `/.well-known/agent.json` 路径下）来发现潜在的代理。代理卡包含了代理的名称、描述、URL、提供者信息、版本、文档链接、支持的能力（如流式传输和推送通知）、认证要求、默认输入输出模式以及它所拥有的技能列表。客户端代理利用代理卡的信息来识别最适合执行特定任务的代理，并了解如何与其进行通信。

### A2A 协议中“任务 (Task)”的概念是什么？

在 A2A 协议中，“任务”是一个有状态的实体，它允许客户端代理和远程代理为了达成特定的结果而进行协作。一个任务由客户端代理创建，其状态由远程代理管理。任务可以立即完成，也可以是长时间运行的。在任务的生命周期中，客户端和远程代理可以通过交换“消息 (Message)”来沟通上下文、指令和状态，而远程代理则将任务的执行结果以“工件 (Artifact)”的形式发送给客户端。任务还可以包含一个可选的会话 ID (sessionId)，用于将多个相关的任务组织在一起。

### A2A 协议是如何处理长时间运行的任务和状态更新的？

对于需要较长时间才能完成的任务，A2A 协议支持多种机制来跟踪和获取状态更新。客户端代理可以定期**轮询 (polling)** 远程代理以获取最新的任务状态和工件。此外，如果远程代理支持，它可以利用 **服务器发送事件 (SSE)** 建立持久连接，实时向客户端推送状态更新和工件。A2A 协议还定义了 **推送通知 (push notifications)** 机制，即使在客户端与代理断开连接的情况下，代理也可以通过外部通知服务向客户端发送更新通知。

### A2A 协议中“消息 (Message)”和“工件 (Artifact)”有什么区别？

在 A2A 协议中，“消息 (Message)”和“工件 (Artifact)”代表了代理之间交换的不同类型的内容。“消息”包含的是任何非最终结果的内容，例如代理的思考过程、用户上下文、指令、错误或状态信息。一个消息可以包含多个“部分 (Part)”，每个部分可以有不同的内容类型（如文本、文件或数据）。“工件 (Artifact)”则是任务的最终结果，它是不可变的，可以命名，并且也可以包含多个“部分”。例如，一个生成网页的任务可能会产生一个 HTML 工件和一个图像工件。

### A2A 协议如何考虑企业级应用的安全性和认证？

A2A 协议强调与现有企业安全基础设施的无缝集成，而不是发明新的安全标准。它将企业级代理视为标准的基于 HTTP 的应用程序，并依赖于企业标准的认证、授权、数据隐私、追踪和监控机制。协议本身通过代理卡传递认证需求（方案和凭据），而实际的凭据协商和传输（例如 OAuth 令牌）则发生在 A2A 协议之外，通常通过 HTTP 头部进行。A2A 服务器需要验证客户端和用户的身份，并基于技能和工具进行细粒度的授权。对于推送通知，A2A 也提供了一些安全建议，例如验证通知 URL 和使用非对称或对称密钥进行签名验证。

### 如何参与 A2A 协议的开发和贡献？

A2A 协议是一个开源项目，Google 鼓励社区积极参与其发展。参与者可以通过以下方式做出贡献：阅读技术文档和 JSON 规范以理解协议；使用和测试提供的代码示例；针对协议的改进提出反馈（通过 GitHub Issues）；参与 GitHub Discussions 中的社区讨论；提交代码贡献（遵循贡献指南）；以及通过 Google 表单发送私有反馈。未来的计划包括协议本身的增强（如更完善的代理发现、动态 UX 协商）以及示例和文档的改进。

## Agent2Agent (A2A) 协议学习指南

### 核心概念

- Agent（代理）: 能够自主执行任务并与其他 Agent 或用户通信的软件实体。
- Client Agent（客户端代理）: 负责发起和管理任务，并与远程 Agent 交互的 Agent。
- Remote Agent（远程代理）: 接收并处理来自客户端 Agent 的任务请求，并返回结果或执行操作的 Agent。
- Agent Card（代理卡片）: JSON 格式的元数据，描述了 Agent 的名称、描述、URL、提供者、版本、能力、技能、认证方式以及支持的输入/输出模式等信息。用于 Agent 的发现和能力声明。
- Task（任务）: 客户端 Agent 请求远程 Agent 完成的特定工作单元。Task 具有状态和生命周期，可以立即完成或长时间运行。
- Artifact（工件）: 远程 Agent 执行 Task 后生成的结果，可以是文本、文件或其他数据形式。Artifact 是不可变的，并且可以包含多个 Part。
- Message（消息）: 客户端 Agent 和远程 Agent 之间交换的非 Artifact 内容，包括状态更新、指令、错误信息、元数据等。Message 也可以包含多个 Part。
- Part（部分）: 构成 Message 或 Artifact 的基本内容单元，具有特定的内容类型（如 text、file、data）和可选的元数据。
- Skill（技能）: Agent 具备的特定能力或功能，Agent Card 中会列出 Agent 支持的技能，包括 ID、名称、描述、标签、示例、输入/输出模式等。
- Streaming（流式传输）: 一种通信模式，允许远程 Agent 在 Task 执行过程中逐步发送状态更新和 Artifact 的 Part，而无需等待 Task 完全完成。
- Push Notification（推送通知）: 一种机制，允许远程 Agent 在 Task 状态发生变化时，通过外部通知服务通知客户端 Agent，即使客户端 Agent 未主动连接。

### Agent 发现

- Open Discovery（开放发现）: 推荐 Agent 在其域名下的 /.well-known/agent.json 路径托管 Agent Card，客户端通过 DNS 解析域名并发送 HTTP GET 请求获取。
- Curated Discovery (Registry-Based)（策展发现/基于注册表的发现）: 通过中心化的 Agent 目录或注册表来发现 Agent，注册表由管理员维护和管理。
- Private Discovery (API-Based)（私有发现/基于 API 的发现）: 通过自定义的 API 接口来交换和发现 Agent Card。
- Securing Agent Cards（保护代理卡片）: Agent Card 可能包含敏感信息，可以通过身份验证和授权机制进行保护，例如 mTLS。

### 核心对象

- Task Object（任务对象）: 包含 Task 的唯一 ID、可选的 Session ID、当前状态 (TaskState)、可选的历史记录 (history)、相关的 Artifacts、元数据 (metadata) 等。
- Artifact Object（工件对象）: 包含工件的名称、描述、Parts 数组、索引、是否追加、是否为最后一块以及可选的元数据。
- Message Object（消息对象）: 包含消息的角色 (role - user 或 agent)、Parts 数组以及可选的元数据。
- Part Objects（部分对象）:
  - TextPart: 包含类型 "text" 和文本内容 "text"。
  - FilePart: 包含类型 "file" 和文件内容对象 "file" (包含 name, mimeType, bytes 或 uri)。
  - DataPart: 包含类型 "data" 和任意 JSON 数据 "data"。
- PushNotificationConfig Object（推送通知配置对象）: 包含推送通知服务的 URL、可选的令牌 (token) 和认证信息 (authentication - schemes)。

### 核心方法 (JSON-RPC)

- tasks/send: 客户端发送消息以创建新 Task、恢复中断的 Task 或重新打开已完成的 Task。
- tasks/get: 客户端检索 Task 的 Artifacts 和可选的历史记录。
- tasks/cancel: 客户端取消先前提交的 Task。
- tasks/sendSubscribe: 客户端发送消息并订阅 Task 的流式更新。
- tasks/resubscribe: 断开连接的客户端重新订阅支持流式传输的远程 Agent 以接收 Task 更新。
- tasks/pushNotification/set: 客户端设置接收 Task 状态更改的推送通知配置。
- tasks/pushNotification/get: 客户端检索当前为 Task 配置的推送通知配置。

### 企业就绪

- A2A 旨在与现有的企业安全基础设施无缝集成，不创造新的安全标准。
- 依赖标准的 HTTP 协议进行传输，利用 TLS 进行安全通信。
Agent 通过数字证书进行服务器身份验证。
客户端和用户身份通过协议外的机制进行管理和传递，通常通过 HTTP 头部。
- 推荐 Agent 基于技能 (Skills) 和工具 (Tools) 进行授权管理。

### 推送通知

- 支持 Agent 在连接和断开连接状态下向客户端发送 Task 更新。
- 客户端可以通过 Agent Card 查询 Agent 是否支持推送通知。
- Agent 在适当的时机发送通知，例如 Task 进入最终状态或需要用户输入时。
- Agent 需要验证客户端提供的推送通知 URL 的安全性，例如通过发送挑战请求。
通知接收方需要验证接收到的通知的真实性，例如使用非对称密钥 (JWT + JWKS) 或对称密钥进行签名验证。
建议实施重放攻击预防机制（例如检查事件时间戳）和密钥轮换机制。

### 典型流程

- Discovery（发现）: 客户端从服务器的 /.well-known/agent.json URL 获取 Agent Card。
- Initiation（初始化）: 客户端发送包含初始用户消息和唯一 Task ID 的 tasks/send 或 tasks/sendSubscribe 请求。
- Processing（处理）:(Streaming): 服务器作为 Task 进行发送 SSE 事件（状态更新、工件）。
- (Non-Streaming): 服务器同步处理 Task 并在响应中返回最终的 Task 对象。
- Interaction (Optional)（交互 - 可选）: 如果 Task 进入 input-required 状态，客户端使用相同的 Task ID 通过 tasks/send 或 tasks/sendSubscribe 发送后续消息。
- Completion（完成）: Task 最终达到终端状态 (completed, failed, canceled)。

### 简答题 (Quiz)

- 什么是 Agent Card？它在 A2A 协议中扮演什么角色？
- 简述 A2A 协议中 Task 的生命周期，并列举至少三种可能的 Task 状态。
- Artifact 和 Message 在 A2A 协议中有什么区别？它们各自包含哪些基本元素？
- 解释 A2A 协议中的“Streaming”特性及其优势。
- 描述 A2A 协议中推荐的 Agent 发现机制——“Open Discovery”是如何工作的？
- A2A 协议是如何处理 Agent 之间的身份验证的？是否在协议层面定义了具体的认证方式？
- 什么是 Skill？Agent Card 中如何描述 Skill？Skill 在授权管理中有什么作用？
- 简述 A2A 协议中推送通知的基本流程。Agent 在发送推送通知时需要考虑哪些安全因素？
- 描述 tasks/send 和 tasks/get 这两个核心方法的主要功能。
- 在 A2A 协议中，如果一个 Task 需要用户提供额外的输入才能继续执行，Agent 会如何通知 Client？Client 又该如何响应？

### 简答题答案 (Answer Key)

- Agent Card 是一个 JSON 格式的元数据文档，用于描述 Agent 的基本信息、能力、技能和认证方式。它在 A2A 协议中扮演着 Agent 广告自身能力、供客户端发现和选择合适 Agent 的关键角色。
- Task 由客户端创建并发送给远程 Agent，经历不同的状态，如 submitted（已提交）、working（工作中）、input-required（需要输入）、completed（已完成）、failed（失败）、canceled（已取消）等。Task 的状态由远程 Agent 决定。
- Artifact 是远程 Agent 执行 Task 后生成的结果，代表任务的产出，是不可变的。Message 是 Agent 之间交换的非结果内容，用于通信状态、指令、错误等。两者都可以包含多个 Part 作为内容单元。
- “Streaming”是一种流式传输模式，允许远程 Agent 在 Task 执行过程中逐步发送状态更新 (TaskStatusUpdateEvent) 和 Artifact 的部分内容 (TaskArtifactUpdateEvent)。这种方式可以提高响应速度，尤其对于长时间运行或生成大量数据的任务。
- “Open Discovery”推荐 Agent 在其服务器域名下的 /.well-known/agent.json 路径托管 Agent Card。客户端通过 DNS 解析得到服务器 IP 地址，然后向该特定路径发送 HTTP GET 请求来获取 Agent Card。
- A2A 协议本身并不定义具体的 Agent 身份验证方式。它通过 Agent Card 的 authentication 字段声明 Agent 支持的认证方案（如 OAuth2、Bearer 等），具体的认证流程需要在协议之外进行，认证凭据通常通过 HTTP 头部传递。
- Skill 是 Agent 具备的特定能力或功能。Agent Card 的 skills 数组中包含了 Skill 的 ID、名称、描述、标签、输入/输出模式等信息。在授权管理中，Agent 可以基于 Skill 来限制客户端的访问权限，例如只允许具有特定 OAuth Scope 的客户端调用某个技能。
- 推送通知的基本流程是客户端在发送 Task 时或通过 tasks/pushNotification/set 方法配置推送通知的 URL和认证信息，远程 Agent 在 Task 状态变化时向该 URL 发送通知。Agent 需要验证 URL 的合法性，并考虑使用签名等方式确保通知的安全性。
- tasks/send 方法用于客户端向远程 Agent 发送消息，可以创建新的 Task、恢复中断的 Task 或重新打开已完成的 Task。tasks/get 方法用于客户端向远程 Agent 请求获取指定 Task 的 Artifacts，还可以选择获取 Task 的历史消息。
- 如果 Task 进入 input-required 状态，远程 Agent 会在 Task 的 status 字段中将 state 设置为 input-required，并且通常会在 message 字段中包含一个描述需要用户提供的具体信息的 Message 对象。客户端需要解析这个 Message，获取所需信息，然后通过 tasks/send 或 tasks/sendSubscribe 方法发送包含必要输入的新消息以恢复 Task 的执行。

### 论述题

- 探讨 A2A 协议在构建复杂的、跨多个 AI Agent 协作的智能应用方面的潜力与挑战。请结合 Agent 发现、任务管理和数据交换等方面进行分析。
- 分析 A2A 协议中 Agent Card 的设计对于实现 Agent 的互操作性和可发现性的重要性。你认为
- Agent Card 未来可能需要包含哪些额外的信息？
比较和对比 A2A 协议中同步 (non-streaming) 和异步 (streaming 和 push notification) 的任务处理方式，并讨论在不同应用场景下选择哪种方式更为合适。
讨论 A2A 协议在企业环境中的应用前景，并分析其在企业就绪性（安全性、身份验证、授权、监控等方面）方面需要考虑的关键因素。
基于你对 A2A 协议的理解，设计一个具体的应用场景，描述 Client Agent 如何利用 A2A 协议与多个 Remote Agent 协作完成一个复杂的任务。请详细说明 Agent 之间的交互流程、数据格式和可能的错误处理机制。

# 术语表

- A2A (Agent-to-Agent): Agent 之间的通信协议的简称。
- API (Application Programming Interface): 应用程序编程接口，允许不同的软件组件进行交互的一组规则和规范。
- Artifact (工件): Task 执行后生成的结果数据。
- Agent (代理): 能够自主执行任务并与其他系统交互的软件实体。
- Agent Card (代理卡片): 描述 Agent 元数据的 JSON 文档。
- Authentication (身份验证): 验证用户或 Agent 身份的过程。
- Authorization (授权): 确定已验证身份的用户或 Agent 是否具有执行特定操作或访问特定资源的权限。
- Client (客户端): 在 A2A 协议中，通常指发起 Task 请求的 Agent。
- JSON (JavaScript Object Notation): 一种轻量级的数据交换格式。
- JSON-RPC: 一种无状态的、轻量级的远程过程调用 (RPC) 协议，使用 JSON 作为数据格式。
- Metadata (元数据): 描述数据的数据。
- Message (消息): Agent 之间交换的通信内容，不包括最终结果 (Artifact)。
- OAuth (Open Authorization): 一种开放标准的授权协议，允许用户授权第三方应用访问其在另一服务上存储的信息，而无需将凭据泄露给第三方应用。
- OpenAPI: 一种用于描述、生产、消费和可视化 RESTful Web 服务的规范格式。
- Part (部分): 构成 Message 或 Artifact 的内容单元。
- Push Notification (推送通知): 一种将信息从服务器主动发送到客户端的技术。
- Remote Agent (远程代理): 接收并处理来自客户端的 Task 请求的 Agent。
- Schema (模式): 定义数据结构和约束的蓝图。
- SDK (Software Development Kit): 软件开发工具包，包含开发应用程序所需的工具、库和文档。
- Server-Sent Events (SSE): 一种服务器推送技术，允许服务器通过 HTTP 连接单向地向客户端发送事件流。
- Skill (技能): Agent 具备的特定能力或功能。
- Streaming (流式传输): 逐步传输数据的过程。
- Task (任务): 客户端请求远程 Agent 执行的工作单元。
- TLS (Transport Layer Security): 传输层安全协议，用于在网络通信中提供加密和数据完整性。
- URL (Uniform Resource Locator): 统一资源定位符，用于标识互联网上的资源。
- URI (Uniform Resource Identifier): 统一资源标识符，用于标识资源。

# 参考

- [Announcing the Agent2Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [Building the industry’s best agentic AI ecosystem with partners](https://cloud.google.com/blog/topics/partners/best-agentic-ecosystem-helping-partners-build-ai-agents-next25)
- [A2A Github](https://github.com/google/a2a)
- [Google's Agent2Agent (A2A) Protocol: A New Era of AI Agent Collaboration and Its Organizational Impact](https://blog.wadan.co.jp/en/tech/agent2agent-protocol)
