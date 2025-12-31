---
title: "每周一个MCP：Mem0 记忆管家——把长期记忆能力接到你的 Agent 上"
date: "2025-12-31T23:00:00+08:00"
tags: ["mcp", "Python", "技术", "mem0", "agent"]
categories: ["projects"]
draft: false
description: "这个MCP服务器将 Mem0 的记忆 REST 能力封装成 MCP Tools，让对话式 Agent 获得可检索、可更新、可清理的长期记忆能力，解决“聊完就忘”“记忆不可控”的工程痛点。"
wordCount: 2818
readingTime: 8
---

## 背景/简介 (Background)

这次选的 MCP Server，本质是一个 **“Mem0 的 MCP 适配层”**：它把 Mem0 的 REST/SDK 操作封装成标准 MCP Tools（`add_memory / search_memories / get_memories / update_memory / delete_memory ...`），让 LLM/Agent 在对话中能以**工具调用**的方式读写长期记忆。

在没有这类 MCP Server 之前，长期记忆通常会落在三种低效方案里：

- **痛点 1：把信息塞进 Prompt/系统提示词**  
  上下文越用越长、成本越高，而且不好做精细权限控制。
- **痛点 2：自己写一套记忆服务**  
  要做 embedding、索引、过滤、分页、更新、删除、租户隔离……工程量巨大。
- **痛点 3：记忆“可写不可控”**  
  写入容易，后续检索、更新、删除、按 user/agent/run 精准管理很困难。

这个 MCP Server 的解决方案很直接：

- **解决方案：** 用 FastMCP 暴露一组工具，把 Mem0 的能力变成“对话可调用 API”。  
- **核心价值：** 让 Agent 的长期记忆具备 **可检索（semantic search）/可分页列举（filters + pagination）/可更新/可删除/可按实体管理** 的工程化闭环。

---

## 核心功能 (Key Features)

结合memo-mcp的[核心代码](https://github.com/mem0ai/mem0-mcp/blob/main/src/mem0_mcp_server/server.py)，这个 Server 的能力可以总结为三层：

### 1) 记忆写入：结构化对话或单句摘要都支持
- **功能点一：`add_memory` 写入长期记忆**  
  - 既支持 `text`（一句话摘要），也支持 `messages`（多轮对话结构：`role/content`）。
  - 自动处理 “如果只给 text，就转成单轮 conversation” 的兼容逻辑。
- **功能点二：多维度作用域（user/agent/app/run）**  
  - 参数包含 `user_id / agent_id / app_id / run_id`，可用于做多租户隔离或按运行实例隔离。
- **功能点三：可选 graph memory**  
  - `enable_graph` 默认关闭（强调简单、快），但可通过 session config 或 env 决定默认值。

### 2) 记忆检索：语义搜索 + 结构化过滤双通道
- **功能点四：`search_memories` 语义搜索**  
  - `query` 走语义检索，`filters` 做范围约束（AND/OR/NOT）。
- **功能点五：`get_memories` 纯过滤分页列举**  
  - 用 `page / page_size` 浏览记录，适合“审计/回放/治理”。

> 关键工程细节：`user_id` 会被 **自动注入 filters**  
> `_with_default_filters` 会确保没有显式 user_id 时，默认加上 `{"user_id": default_user_id}`，避免“误查到别人的记忆”。

### 3) 记忆治理：更新、删除、实体级清理
- **功能点六：`get_memory` 单条读取**
- **功能点七：`update_memory` 覆写文本**
- **功能点八：`delete_memory` 删除单条**
- **功能点九：`delete_all_memories` 按范围清空（保留实体）**
- **功能点十：`delete_entities` 删除实体并级联清理**
- **功能点十一：`list_entities` 列出有哪些 user/agent/app/run 存在记忆**

| 特性 | 传统方式 | 使用本 MCP 后 |
| :-- | :-- | :-- |
| 集成成本 | 自建 DB/Embedding/鉴权/分页 | 工具化封装，直接调用 |
| 记忆可控性 | 写入后难治理 | 支持更新、删除、按实体清理 |
| 租户隔离 | 容易误查误写 | 默认注入 `user_id` 过滤，降低串数据风险 |
| 可靠性 | 错误处理分散 | `MemoryError` 统一封装返回结构化错误 |

---

## 快速开始 (Quick Start)

> 下面以“本地跑 stdio + 在客户端配置 MCP”作为最常见的接入路径示例。

### 1. 安装 (Installation)

通过 pip 安装（示例，按项目实际包名调整）

````bash
pip install mem0 mcp python-dotenv pydantic
# 如果 server 在一个项目里：
pip install -e .
````

### 2. 配置 (Configuration)

#### 环境变量（必需）
这个 Server **硬依赖 `MEM0_API_KEY`**（可以来自 env 或 session config）。

````bash
export MEM0_API_KEY="your-mem0-api-key"
export MEM0_DEFAULT_USER_ID="mem0-mcp"     # 可选，默认就是 mem0-mcp
export MEM0_ENABLE_GRAPH_DEFAULT="false"   # 可选
````

#### Claude Desktop (claude_desktop_config.json)

````json
{
  "mcpServers": {
    "mem0": {
      "command": "python",
      "args": ["-m", "mem0_mcp.server"],
      "env": {
        "MEM0_API_KEY": "your-mem0-api-key",
        "MEM0_DEFAULT_USER_ID": "pengge",
        "MEM0_ENABLE_GRAPH_DEFAULT": "false"
      }
    }
  }
}
````

#### Cursor / VS Code (MCP Settings)
- Name: `mem0`
- Type: `stdio`
- Command: `python`
- Args: `-m mem0_mcp.server`
- Env: `MEM0_API_KEY=...`

---

## 使用示例 (Usage Examples)

### 场景一：写入“用户偏好”记忆
- 用户指令：
  > “把我的偏好记下来：我更喜欢用 Python 写 MCP Server，默认 user_id 用 pengge。”

- 预期行为（工具调用）：
  - 调用 `add_memory`，`text` 为摘要；或用 `messages` 存多轮上下文。
  - 若未显式指定 `user_id`，会使用默认 `MEM0_DEFAULT_USER_ID`（且在没有 agent_id/run_id 时生效）。

### 场景二：语义检索“我之前说过什么”
- 用户指令：
  > “帮我回忆一下我之前提到的关于 MAS 框架和测试时扩展的想法。”

- 预期行为：
  - 调用 `search_memories(query=...)`
  - `filters` 未写 user_id 时会自动注入默认 user 过滤，避免跨用户泄漏。

### 场景三：记忆治理（更新/删除）
- 用户指令：
  > “把 memory_id=xxx 的那条记忆改成更准确的描述：……”
- 预期行为：
  - 调用 `update_memory(memory_id, text)`

- 用户指令：
  > “删除 memory_id=yyy 这条（我确认）。”
- 预期行为：
  - 调用 `delete_memory(memory_id)`

---

## 最佳实践 (Best Practices)

1. **默认 user_id 注入是好事，但别盲信：显式传 scope 更安全**
   - 生产环境建议：调用端总是明确传 `user_id`（以及必要的 `app_id/run_id`），把“默认注入”当成兜底，而不是主策略。

2. **把 filters 当成“访问控制的一部分”**
   - 你现在的 `_with_default_filters` 只是注入 `user_id`，并不能替代真正的鉴权。  
   - 如果你要对外提供服务（多租户），建议在 MCP 层加入更严格的校验：例如禁止客户端传入非自身 user_id。

3. **graph 默认关闭很合理：只在确有需求时开启**
   - graph 能带来关系推理，但也会增加复杂度与不确定性。  
   - 推荐做法：在 system prompt 或工具调用层面“按需开启”，并记录到 metadata 里用于审计。

4. **错误返回建议统一为结构化 JSON**
   - `_mem0_call` 会把 `MemoryError` 的 `status/payload` 一起返回，方便上层做重试、降级与提示。

5. **缓存 client 的策略要注意生命周期**
   - `_CLIENT_CACHE` 以 `api_key` 为 key 缓存 `MemoryClient`，对长期运行进程是 OK 的。  
   - 如果在无服务器/短生命周期容器频繁启动，缓存意义不大；如果多 key 并发，注意 cache 的大小与回收策略。

---

## 总结 (Conclusion)

这个 Mem0 MCP Server 的价值不是“又一个工具”，而是把长期记忆能力做成了 **可运营、可治理、可集成** 的标准化接口：  
- 对 Agent 来说：能记、能搜、能翻、能改、能删；  
- 对工程来说：默认注入 user filter、统一错误封装、支持 session config、支持 graph 开关；  
- 对产品来说：长期记忆终于从“玄学提示词”变成“有 CRUD 的可控资产”。

如果在搞一套多 Agent 协作系统（MAS），这类 server 甚至可以作为“团队记忆中枢”，把每个 Agent 的 run 记忆汇总、可回放、可追责。

---

## 参考 (References)

- Mem0: https://mem0.ai/ （按实际文档地址替换）
- MCP / FastMCP: https://modelcontextprotocol.io/ （按实际文档地址替换）


## 脑洞很大的建议

**把它升级成“记忆编译器（Memory Compiler）+ 记忆防火墙（Memory Firewall）”的双层架构：**

1. **Memory Compiler：把原始对话编译成多种记忆工件（Artifacts）**
   - 同一次 `add_memory(messages=...)` 不只存一条文本，而是生成：
     - `summary`：一句话事实
     - `preferences`：偏好键值对（可 JSON schema）
     - `tasks`：待办/承诺（可带 due date）
     - `entities`：人/项目/库/链接的实体抽取
     - `embeddings`：多向量（按主题/按实体）
   - 然后以 `metadata` 标注 `artifact_type`，实现“同源多视图”检索。

2. **Memory Firewall：在写入与读取阶段做策略审计**
   - 写入阶段（pre-write）：
     - 过滤敏感信息（API key、身份证、银行卡等）
     - 检测“幻觉型记忆”（模型不确定的内容不允许落库）
     - 强制要求 `confidence` 字段低于阈值则仅写入“候选记忆区”
   - 读取阶段（post-search）：
     - 只返回与当前会话 scope 匹配的记忆
     - 对“可能误导决策的记忆”加上风险标签（stale/low_confidence）

3. **引入“时间衰减 + 版本分叉”的记忆演化机制**
   - 每条记忆不是覆盖更新，而是形成版本树：
     - `update_memory` 变成“写入新版本 + 旧版本降权”
     - 检索时按时间衰减与可信度打分：  
       例如 \[score = sim \times decay(t) \times confidence\]
   - 会得到“可追溯”的长期记忆，而不是“被覆盖后无法审计”的文本。

4. **把 `run_id` 变成可观测性主键，做“Agent 行为回放”**
   - 每次工具调用都带 `run_id`，再存一条“Memory Index”：
     - 本次写入了哪些 memory_id
     - 本次检索命中了哪些 memory_id
   - 最终能做一个“Agent Debugger”：一键回放某次 run 为什么做出这个回答（它看到哪些记忆、写入了哪些记忆）。

## 附录

下面我用一张**完整的 ASCII 架构图**，把这份 Mem0 MCP Server 的所有层次、模块、数据流都标清楚：

```
═══════════════════════════════════════════════════════════════════════════════
                          Mem0 MCP Server 完整架构
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                          1. 客户端 / 运行时层                                 │
│                                                                             │
│   [Claude Desktop]  [Cursor]  [VS Code]  [Custom Agent]  [Smithery Platform]│
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               │ MCP Protocol (JSON-RPC)
                               │
                               v
╔═════════════════════════════════════════════════════════════════════════════╗
║                          2. MCP 传输层 (Transport)                           ║
║                                                                             ║
║  ┌─────────────────────┐          ┌─────────────────────────────────────┐  ║
║  │  stdio Transport    │          │  HTTP Transport                     │  ║
║  │  server.run("stdio")│          │  host: 0.0.0.0                      │  ║
║  │                     │          │  port: 8081                         │  ║
║  └──────────┬──────────┘          └──────────┬──────────────────────────┘  ║
║             │                                │                             ║
║             └────────────────┬───────────────┘                             ║
║                              │                                             ║
║                              │ TransportSecuritySettings                   ║
║                              │ (dns_rebinding_protection=false)            ║
╚══════════════════════════════╪═════════════════════════════════════════════╝
                               │
                               v
╔═════════════════════════════════════════════════════════════════════════════╗
║                     3. FastMCP Server 应用层 (create_server)                 ║
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │                      3.1 启动配置 / 环境初始化                         │   ║
║  │                                                                     │   ║
║  │  • load_dotenv()  ──────────────────────> .env 文件                 │   ║
║  │  • ENV_API_KEY                                                      │   ║
║  │  • ENV_DEFAULT_USER_ID = "mem0-mcp"                                 │   ║
║  │  • ENV_ENABLE_GRAPH_DEFAULT = false                                 │   ║
║  │  • logging.basicConfig(level=INFO)                                  │   ║
║  │  • @smithery.server(config_schema=ConfigSchema)                     │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │                      3.2 对外暴露能力 (MCP Surface)                    │   ║
║  │                                                                     │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐  │   ║
║  │  │  Prompt:                                                     │  │   ║
║  │  │    @server.prompt()                                          │  │   ║
║  │  │    └─> memory_assistant()  (使用指南 / 最佳实践)              │  │   ║
║  │  └──────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                     │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐  │   ║
║  │  │  Tools (9 个工具):                                            │  │   ║
║  │  │                                                              │  │   ║
║  │  │  写入类:                                                      │  │   ║
║  │  │    • add_memory(text, messages, user_id, agent_id, ...)     │  │   ║
║  │  │                                                              │  │   ║
║  │  │  查询类:                                                      │  │   ║
║  │  │    • search_memories(query, filters, limit, enable_graph)   │  │   ║
║  │  │    • get_memories(filters, page, page_size, enable_graph)   │  │   ║
║  │  │    • get_memory(memory_id)                                  │  │   ║
║  │  │                                                              │  │   ║
║  │  │  更新类:                                                      │  │   ║
║  │  │    • update_memory(memory_id, text)                         │  │   ║
║  │  │                                                              │  │   ║
║  │  │  删除类:                                                      │  │   ║
║  │  │    • delete_memory(memory_id)                               │  │   ║
║  │  │    • delete_all_memories(user_id, agent_id, app_id, run_id)│  │   ║
║  │  │                                                              │  │   ║
║  │  │  治理类:                                                      │  │   ║
║  │  │    • list_entities()                                        │  │   ║
║  │  │    • delete_entities(user_id, agent_id, app_id, run_id)    │  │   ║
║  │  └──────────────────────────────────────────────────────────────┘  │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════╪══════════════════════════════════════════════╝
                               │
                               │ (所有工具调用共享的内部管道)
                               │
                               v
╔═════════════════════════════════════════════════════════════════════════════╗
║                        4. 核心内部模块 (Core Modules)                         ║
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.1 配置解析模块                                                     │   ║
║  │                                                                     │   ║
║  │  _resolve_settings(ctx) -> (api_key, default_user, graph_default)  │   ║
║  │      │                                                              │   ║
║  │      ├─> session_config.mem0_api_key  (优先级 1)                    │   ║
║  │      ├─> ENV_API_KEY                  (优先级 2)                    │   ║
║  │      └─> if not api_key: raise RuntimeError                        │   ║
║  │                                                                     │   ║
║  │  _config_value(source, field)  (兼容 dict / object)                 │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                               │                                             ║
║                               v                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.2 客户端缓存模块                                                   │   ║
║  │                                                                     │   ║
║  │  _CLIENT_CACHE: Dict[api_key, MemoryClient]                        │   ║
║  │      │                                                              │   ║
║  │      └─> _mem0_client(api_key)                                     │   ║
║  │             │                                                       │   ║
║  │             ├─ cache hit  ──> 复用已有 MemoryClient                 │   ║
║  │             └─ cache miss ──> MemoryClient(api_key) -> 写入缓存     │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                               │                                             ║
║                               v                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.3 默认过滤注入模块 (读路径隔离)                                     │   ║
║  │                                                                     │   ║
║  │  _with_default_filters(default_user_id, filters) -> filters        │   ║
║  │      │                                                              │   ║
║  │      ├─ filters 为空:                                               │   ║
║  │      │    return {"AND": [{"user_id": default_user_id}]}           │   ║
║  │      │                                                              │   ║
║  │      ├─ filters 无 AND/OR/NOT:                                      │   ║
║  │      │    包一层: {"AND": [filters]}                                │   ║
║  │      │                                                              │   ║
║  │      └─ filters 内没有 user_id:                                     │   ║
║  │           filters["AND"].insert(0, {"user_id": default_user_id})   │   ║
║  │                                                                     │   ║
║  │  (确保每次读操作都带上 user_id，防止跨租户泄漏)                       │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                               │                                             ║
║                               v                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.4 统一错误封装模块                                                 │   ║
║  │                                                                     │   ║
║  │  _mem0_call(func, *args, **kwargs) -> JSON string                  │   ║
║  │      │                                                              │   ║
║  │      ├─ try:                                                        │   ║
║  │      │    result = func(*args, **kwargs)                           │   ║
║  │      │    return json.dumps(result)                                │   ║
║  │      │                                                              │   ║
║  │      └─ except MemoryError as exc:                                 │   ║
║  │           logger.error("Mem0 call failed: %s", exc)                │   ║
║  │           return json.dumps({                                      │   ║
║  │               "error": str(exc),                                   │   ║
║  │               "status": exc.status,                                │   ║
║  │               "payload": exc.payload                               │   ║
║  │           })                                                        │   ║
║  │                                                                     │   ║
║  │  (让模型能稳定处理错误，避免裸异常中断对话)                            │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                               │                                             ║
║                               v                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.5 Graph 开关辅助模块                                               │   ║
║  │                                                                     │   ║
║  │  _default_enable_graph(enable_graph, default) -> bool              │   ║
║  │      └─> 如果 enable_graph 为 None，使用 default (默认 false)        │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  4.6 Schema 验证模块 (schemas.py)                                     │   ║
║  │                                                                     │   ║
║  │  • AddMemoryArgs                                                    │   ║
║  │  • SearchMemoriesArgs                                               │   ║
║  │  • GetMemoriesArgs                                                  │   ║
║  │  • DeleteAllArgs                                                    │   ║
║  │  • DeleteEntitiesArgs                                               │   ║
║  │  • ToolMessage                                                      │   ║
║  │  • ConfigSchema                                                     │   ║
║  │                                                                     │   ║
║  │  (Pydantic 模型，确保参数类型安全 + 自动校验)                          │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════╪══════════════════════════════════════════════╝
                               │
                               │ (调用 Mem0 SDK)
                               │
                               v
╔═════════════════════════════════════════════════════════════════════════════╗
║                       5. Mem0 SDK 层 (mem0.MemoryClient)                     ║
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  MemoryClient(api_key)                                              │   ║
║  │      │                                                              │   ║
║  │      ├─> add(conversation, user_id, agent_id, metadata, ...)       │   ║
║  │      ├─> search(query, filters, limit, enable_graph, ...)          │   ║
║  │      ├─> get_all(filters, page, page_size, enable_graph, ...)      │   ║
║  │      ├─> get(memory_id)                                            │   ║
║  │      ├─> update(memory_id, text)                                   │   ║
║  │      ├─> delete(memory_id)                                         │   ║
║  │      ├─> delete_all(user_id, agent_id, app_id, run_id)            │   ║
║  │      ├─> users()                                                   │   ║
║  │      └─> delete_users(user_id, agent_id, app_id, run_id)          │   ║
║  │                                                                     │   ║
║  │  (封装 Mem0 REST API 调用，处理认证、序列化、异常)                    │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════╪══════════════════════════════════════════════╝
                               │
                               │ HTTPS / REST API
                               │
                               v
┌─────────────────────────────────────────────────────────────────────────────┐
│                        6. Mem0 Service (外部服务)                             │
│                                                                             │
│  • Memory Storage (持久化存储)                                               │
│  • Semantic Search (语义检索 / Embedding)                                    │
│  • Graph Memory (可选，关系推理)                                              │
│  • Multi-tenancy (user_id / agent_id / app_id / run_id 隔离)                │
│                                                                             │
│  返回:                                                                       │
│    - 成功: JSON 结果 (memories / entities / ...)                             │
│    - 失败: MemoryError(status, payload)                                     │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              关键数据流示例
═══════════════════════════════════════════════════════════════════════════════

【示例 1: add_memory 写入路径】

  Client 调用 add_memory(text="鹏哥喜欢用 Python 写 MCP", user_id="pengge")
      │
      v
  _resolve_settings(ctx)  ──> (api_key, default_user="mem0-mcp", graph_default=false)
      │
      v
  AddMemoryArgs 构造 payload:
      {
        "user_id": "pengge",
        "enable_graph": false
      }
      │
      v
  如果 messages 为空 && text 存在:
      conversation = [{"role": "user", "content": "鹏哥喜欢用 Python 写 MCP"}]
      │
      v
  _mem0_client(api_key)  ──> 从 _CLIENT_CACHE 获取 / 创建 MemoryClient
      │
      v
  _mem0_call(client.add, conversation, **payload)
      │
      ├─ try: client.add(...)  ──> Mem0 Service
      │      └─> 返回 {"memory_id": "abc123", ...}
      │
      └─ return json.dumps(result)
      │
      v
  返回给 Client: {"memory_id": "abc123", ...}


【示例 2: search_memories 检索路径 (带默认隔离)】

  Client 调用 search_memories(query="鹏哥的偏好", filters=None)
      │
      v
  _resolve_settings(ctx)  ──> (api_key, default_user="mem0-mcp", graph_default=false)
      │
      v
  SearchMemoriesArgs 构造 payload:
      {
        "query": "鹏哥的偏好",
        "filters": None,
        "enable_graph": false
      }
      │
      v
  _with_default_filters(default_user="mem0-mcp", filters=None)
      │
      └─> filters 为空，返回: {"AND": [{"user_id": "mem0-mcp"}]}
      │
      v
  payload["filters"] = {"AND": [{"user_id": "mem0-mcp"}]}
      │
      v
  _mem0_client(api_key)  ──> 从缓存获取 MemoryClient
      │
      v
  _mem0_call(client.search, **payload)
      │
      ├─ try: client.search(...)  ──> Mem0 Service
      │      └─> 返回 [{"memory_id": "abc123", "text": "...", "score": 0.95}, ...]
      │
      └─ return json.dumps(result)
      │
      v
  返回给 Client: [{"memory_id": "abc123", ...}, ...]


【示例 3: delete_entities 治理路径 (带 scope 校验)】

  Client 调用 delete_entities(user_id="pengge")
      │
      v
  _resolve_settings(ctx)  ──> (api_key, ...)
      │
      v
  DeleteEntitiesArgs 构造:
      {
        "user_id": "pengge",
        "agent_id": None,
        "app_id": None,
        "run_id": None
      }
      │
      v
  校验: any([user_id, agent_id, app_id, run_id])  ──> True (有 user_id)
      │
      v
  _mem0_client(api_key)
      │
      v
  _mem0_call(client.delete_users, user_id="pengge")
      │
      ├─ try: client.delete_users(...)  ──> Mem0 Service (级联删除该 user 的所有记忆)
      │      └─> 返回 {"deleted": true, "count": 42}
      │
      └─ return json.dumps(result)
      │
      v
  返回给 Client: {"deleted": true, "count": 42}


═══════════════════════════════════════════════════════════════════════════════
                              核心设计亮点
═══════════════════════════════════════════════════════════════════════════════

1. 配置三段式兜底 (session_config > env > error)
   └─> 兼容 Smithery probe (启动时不强制 API key)

2. Client 缓存 (按 api_key 复用 MemoryClient)
   └─> 减少连接开销，适合长期运行进程

3. 默认隔离注入 (_with_default_filters)
   └─> 读操作自动加 user_id，降低跨租户泄漏风险

4. 统一错误封装 (_mem0_call)
   └─> MemoryError -> 结构化 JSON，模型能稳定处理

5. Schema 验证 (Pydantic)
   └─> 参数类型安全 + 自动校验，减少运行时错误

6. Graph 默认关闭
   └─> 简化查询、提升速度，按需开启

7. 工具描述详尽
   └─> 包含 filter 示例、分页说明，降低模型调用错误率

8. Smithery 兼容
   └─> @smithery.server + ConfigSchema，支持平台化部署
```

---

## 这张架构图的"读图要点"

鹏哥，这张图按**自顶向下**的方式把 6 层都标清楚了：

1. **客户端层**：谁在调用（Claude/Cursor/自定义 Agent/Smithery）
2. **传输层**：stdio / HTTP 两种方式，带 DNS rebinding 保护开关
3. **应用层**：FastMCP Server 暴露 9 个 tools + 1 个 prompt
4. **核心模块层**：配置解析、client 缓存、默认过滤注入、错误封装、schema 验证
5. **SDK 层**：mem0.MemoryClient 封装 REST 调用
6. **服务层**：Mem0 Service（存储/检索/graph/多租户）

右侧的**数据流示例**把三条典型路径（写入/检索/删除）的完整调用链都走了一遍，你可以直接对着代码验证。

---

## 脑洞建议：把"核心模块层"再拆成"可插拔中间件链"

现在 `_resolve_settings / _with_default_filters / _mem0_call` 是"隐式调用"，如果你要做生产化改造，可以把它们显式化成一个 **Middleware Pipeline**：

```
Tool 调用
  │
  v
┌─────────────────────────────────────┐
│  Middleware Chain (按顺序执行)       │
│                                     │
│  1. AuthZMiddleware                 │
│     └─> 禁止伪造 user_id             │
│                                     │
│  2. PIIMiddleware                   │
│     └─> 写入前扫描敏感信息            │
│                                     │
│  3. AuditMiddleware                 │
│     └─> 记录输入/输出/耗时            │
│                                     │
│  4. CacheMiddleware                 │
│     └─> 对 search 做短 TTL cache     │
│                                     │
│  5. _resolve_settings               │
│  6. _with_default_filters           │
│  7. _mem0_call                      │
└─────────────────────────────────────┘
```

这样你能在**不改 tool 签名**的情况下，通过"注册 middleware"的方式扩展能力。要不要我给你写一版"最小侵入改造方案"？