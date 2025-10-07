
## AutoGen 0.4 版本

根据我搜索到的信息，AutoGen 最新版本（特别是 0.4 版本及更高版本）引入了许多新特性和改进，主要集中在以下几个方面：

  核心架构和 API (Core & API)

* 异步架构 (Asynchronous Architecture): AutoGen 0.4 完全转向异步架构，所有操作都使用 async/await。这提高了性能和可伸缩性，尤其是在处理 I/O 密集型任务（如网络请求）时。
* 模块化和解耦 (Modularity and Decoupling):
  * 核心抽象（如 IAgent）被移至 AutoGen.Core 包，去除了对 OpenAI 的直接依赖。
  * OpenAI 特定的组件（如 GPTAgent, OpenAIChatAgent）被移至独立的 AutoGen.OpenAI 包。
  * 这种模块化设计使得集成其他模型提供商（如 Anthropic, Ollama）变得更加容易。
* 消息类型 (Message Types): 引入了更具体的消息类型，如 TextMessage, ImageMessage, 和 MultiModalMessage，以更好地支持多模态应用。
* 流式处理 (Streaming): 增强了对流式响应的支持，IStreamingAgent 和 IStreamingMiddleware 的 API 也得到了简化，可以直接返回 IAsyncEnumerable<IStreamingMessage>。

  智能体和工作流 (Agents & Workflows)

* 图聊天 (Graph Chat): 引入了 GraphFlow 和 DiGraphBuilder，允许创建复杂的、有条件的对话工作流。这使得可以构建更精细的多智能体协作模式，例如带有条件分支和循环的流程。
* 多模态智能体 (Multimodal Agents): 增强了对多模态输入的支持。例如，AssistantAgent 现在可以处理包含文本和图像的 MultiModalMessage。MultimodalWebSurfer
     智能体可以浏览网页并处理多模态内容。
* 工具使用 (Tool Use):
  * 简化了工具（函数）的注册和使用。
  * AssistantAgent 可以通过设置 reflect_on_tool_use=True 来让模型反思工具的使用情况。
* 群聊模式 (Group Chat):
  * RoundRobinGroupChat 允许多个智能体以轮询方式协作。
  * SelectorGroupChat 支持自定义发言人选择逻辑，可以实现更灵活的对话管理。

  生态系统和集成 (Ecosystem & Integrations)

* AutoGen Studio: 提供了一个 UI 工具，用于构建和管理多智能体工作流，并支持实验性的身份验证功能。
* 更广泛的模型支持: 通过 OllamaChatCompletionClient, AnthropicChatCompletionClient 等，更容易地集成本地运行的 LLM（如 Llama 3.2, DeepSeek-R1）和其他商业模型。
* .NET 版本 (AutoGen.Net): .NET 版本的 AutoGen 也在快速发展，增加了对流式处理、图聊天和源码生成器（从 FunctionAttribute 生成 FunctionContract）的支持。

  其他

* 任务中心化记忆 (Task-Centric Memory): 这是一个实验性功能，旨在为智能体提供更持久和与任务相关的记忆。
* Web Surfer 智能体: MultimodalWebSurfer 智能体可以使用浏览器执行网页浏览任务，并与用户代理进行交互。

  总而言之，AutoGen 的最新版本在异步化、模块化、多模态能力和高级工作流定制方面取得了显著进展，使其成为一个功能更强大、更灵活的 agentic AI 开发框架。
