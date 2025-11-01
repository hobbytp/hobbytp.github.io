

Graphiti 是一个用于 AI 代理构建和查询动态图时序知识图的开源框架。相较传统的检索增强生成（RAG）方法，Graphiti 提供实时增量数据更新、双时间轴数据模型和高效的混合检索功能，可处理动态用户交互、企业数据和外部信息的整合。它支持精准历史查询、语义搜索、关键词搜索和图遍历，适合构建交互式、上下文感知的 AI 应用。

Graphiti 核心特性包括：
- 实时增量更新，无需重新计算完整图数据。
- 明确的事件时间和引入时间支持精准的历史查询。
- 多模式混合检索，支持低延迟查询。
- 开发者自定义实体定义和灵活的本体创建。
- 高并发支持和适合大规模数据场景。

Graphiti 与 Zep 平台集成，用于 AI 上下文工程，为 AI 代理提供记忆支持和动态数据管理。

安装要求包括 Python 3.10+、Neo4j、FalkorDB 或 Amazon Neptune 数据库。支持 OpenAI 与其他 LLM 服务进行集成。同时，Graphiti 提供详细的快速入门指南和 MCP 服务，支持用户管理关系和检索操作。




- [Graphiti framework](https://github.com/getzep/graphiti)
- [Graphiti MCP](https://github.com/getzep/graphiti/blob/main/mcp_server/README.md)