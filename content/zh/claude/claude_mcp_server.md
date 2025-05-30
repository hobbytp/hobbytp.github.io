---
title: "Claude MCP Server 介绍"
date: "2025-05-14T20:10:00+08:00"
draft: false
tags: ["AI", "Agent", "MCP", "Protocol"]
categories: ["ai_tools"]
description: "MCP Server 是 Claude 的 MCP 协议的实现，用于在本地运行 MCP 协议。"
---
MCP Server 是 Claude 的 MCP 协议的实现，用于在本地运行 MCP 协议。

## MCP介绍

## MCP 的已知问题

refer to : <https://www.aci.dev/blog/mcp-has-mcps-the-model-context-protocol-has-many-critical-problems>

### 1. 设计缺陷

- **面向个人开发者**：MCP的架构主要是为单用户场景设计的，缺乏多租户能力，无法满足企业级需求。
- **认证机制混乱**：每个服务器实现自己的认证方案，导致生态系统碎片化。许多客户端（如Cursor）目前不支持传递认证令牌，使得认证服务器无法与这些客户端配合使用。
- 没有注册机制
- 没有发现机制
- 没有过滤机制：当多个MCP Server提供多个tools时，客户端需要手动过滤。不然很容易就超过大模型的限制了（比如40个tool calling）

### 2. 开发体验痛点

- **调试困难**：开发者需要同时使用多个工具（如MCP Inspector和Chrome DevTools），调试过程繁琐。
- **工具发现基础**：`list_tools()`接口的分页功能非常基础，缺乏过滤和搜索能力，服务器开发者需要自行实现分页逻辑。
- **名称冲突**：集成多个MCP服务器时，开发者必须手动处理工具名称冲突。

### 3. 生态系统碎片化

- **重复造轮子**：开发者在构建API连接器、文件系统访问和数据库集成时，质量不一致，导致重复劳动。
- **“解耦”是神话**：服务器开发者被迫为客户端能力的最低公分母设计，若某个客户端不支持特定的认证方法，服务器将无法使用。

### 4. 协议问题

- **标准输入和SSE**：标准输入的使用限制了服务器的部署和使用，SSE与HTTP POST的混合架构显得尴尬，尽管未来承诺将支持可流式传输的HTTP，但为何不一开始就采用这一方案令人困惑。

### 5. 复杂性隐患

- **新特性导致膨胀**：未来的每一个新特性（如OAuth、发现、远程MCP支持）都将增加服务器实现的复杂性，违背了MCP简化的承诺。
- **用户需求简单**：大多数用户仅需工具调用，这可以通过更简单的专门平台（如ACI.dev）实现，而不需要如此繁重的架构。

### 总结

MCP在设计、开发体验、生态系统、协议及复杂性等方面存在多重问题，影响了其广泛应用和用户体验。这些问题需要在未来的版本中得到认真解决。

## MCP社区的用法

### ACI.dev

<https://www.aci.dev/docs/introduction/quickstart>

## MCP Client 开发

## MCP Server 开发

## MCP Server 搜集

AI代码辅助： Cursor和Cline都支持MCP Server

| 序号 | 名称 | 链接 |
| ---- | ---- | ---- |
| 1 | Smithery.ai | <https://smithery.ai/> |
| 2 | MCP.so | <https://mcp.so/> |
| 3 | Potkey.ai | <https://portkey.ai/mcp-servers> |
| 4 | 阿里云百炼 | <https://bailian.console.aliyun.com/mcp-market?tab=mcp#/mcp-market> |
| 5 | HiMCP | <https://himcp.ai/> |
| 6 | Awesome MCP Servers | <https://mcpservers.org/> |
| 7 | MCP Market | <https://mcpmarket.com/> |
| 8 | PulseMCP | <https://www.pulsemcp.com/servers> |
| 9 | Glama MCP | <https://glama.ai/mcp/servers> |
| 10 | cursor.directory | <https://cursor.directory/mcp> |
| 11 | MCP 官方开源库 | <https://github.com/modelcontextprotocol/servers> |
| 12 | Cline's MCP Marketplace | <https://github.com/cline/mcp-marketplace> |
| 13 | MCP Hub | <https://www.aimcp.info/en> |
| 14 | Reddit MCP 官方社区 | <https://www.reddit.com/r/mcp/> |
| 15 | shareMCP | <https://sharemcp.cn/> |
| 16 | MCPServers | <https://www.mcpservers.cn/> |
| 17 | Awesome-MCP-ZH | <https://github.com/yzfly/Awesome-MCP-ZH> |

MCP Client 搜集

| 序号 | 名称 | 网址 | 系统支持 |
| ---- | ---- | ---- | ---- |
| 1 | Cherry Studio | <https://cherry-ai.com/> | Windows、MacOS、Linux |
| 2 | Cursor | <https://www.cursor.com/> | Windows、MacOS、Linux |
| 3 | 5ire | <https://5ire.app/> | Windows、MacOS |
| 4 | Continue | <https://continue.dev/> | Windows、MacOS |
| 5 | Cline | <https://marketplace.visualstudio.co>... | Windows、MacOS |
| 6 | ChatMCP | <https://github.com/daodao97/chat>... | Windows、MacOS、Linux |
| 7 | Claude Desktop | <https://claude.ai/download> | Windows、MacOS |
| 8 | ClaudeMind | <https://claudemind.com/> | Windows、MacOS |
| 9 | HyperChat | <https://github.com/BigSweetPotato>... | Windows、MacOS |
| 10 | Zed | <https://zed.dev/> | Windows、MacOS |
| 11 | ChatWise | <https://chatwise.app/> | Windows、MacOS |

## MCP Gateway

### Alibaba Higress

<https://higress.io/zh/docs/mcp-gateway/overview>

### solo agentgateway

### ACI.dev

ACI(Agent-Computer Interfaces)

### MetaMCP

## MCP Hub

## MCP 社区

### ​魔搭MCP广场（ModelScope）

定位：中国最大AI开源社区推出的MCP服务聚合平台，截至2025年4月已收录1486个服务
​亮点：支付宝、MiniMax等头部企业MCP服务独家首发，提供配套调试工具和在线实验场
​服务类型：覆盖支付（支付宝MCP）、地图（高德/百度）、开发者工具（GitHub MCP）等20+场景

### ​阿里云百炼MCP生态

​功能：全生命周期MCP服务管理，支持5分钟快速构建AI Agent
​特色能力：无影AgentBay提供企业级MCP协议云基础设施，集成阿里云Hologres AI等工具链

### 蚂蚁智能体百宝箱

​核心服务：国内首个支付领域MCP中枢，支持自然语言调用交易创建、退款等支付宝能力
​行业扩展：已接入金融风控、合同管理等企业级工具，日均调用量超百万次

### ​ShareMCP社区

​定位：非盈利开发者共享平台，提供MCP Server托管服务
​活跃度：周均新增20+工具，涵盖物联网设备控制、自动化测试等场景

- ​腾讯云：大模型知识引擎已支持MCP协议，重点布局文旅、医疗行业工具链
- ​火山引擎：2025年4月宣布兼容MCP标准，发力短视频内容生成领域
- ​合众伟奇：推出制造业多智能体协议MACP，实现AI Agent间无损通信

## MCP server 搜集

[smithery](https://smithery.ai/)
[Github库：Awesome MCP Server](https://github.com/appcypher/awesome-mcp-servers?tab=readme-ov-file)

## Demos

### LangChain + Firecrawl MCP Server

LangChain 可以通过 langchain-mcp-adapters 库调用 Firecrawl 的 MCP 工具，需设置 MCP 服务器。
Firecrawl MCP 服务器通过 npx -y firecrawl-mcp 启动，需配置 FIRECRAWL_API_KEY。
根据提供的 JSON 配置，Firecrawl MCP 服务器通过以下命令启动：
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your_api_key_here"
      }
    }
  }
}
在 Python 代码中，使用 langchain-mcp-adapters 的 StdioServerParameters 配置此服务器。

```python
import os
from langchain_mcp_adapters import StdioServerParameters, StdioMCPClient
from langchain.agents import initialize_agent, AgentType
from langchain_openai import OpenAI

# 设置 OpenAI API 密钥（根据需要替换为其他 LLM）
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# 确保 FIRECRAWL_API_KEY 已设置
assert "FIRECRAWL_API_KEY" in os.environ, "请设置 FIRECRAWL_API_KEY 环境变量"

# 配置 MCP 客户端
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "firecrawl-mcp"],
    env={"FIRECRAWL_API_KEY": os.environ["FIRECRAWL_API_KEY"]}
)

mcp_client = StdioMCPClient(server_params)
tools = mcp_client.get_tools()

# 初始化 LLM
llm = OpenAI(temperature=0)

# 初始化代理
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 示例：运行代理以抓取网页内容
response = agent.run("请抓取 https://firecrawl.dev 的内容")
print(response)
```

#### 关键要点

- LangChain 可以通过 `langchain-mcp-adapters` 库调用 Firecrawl 的 MCP 工具，需设置 MCP 服务器。
- Firecrawl MCP 服务器通过 `npx -y firecrawl-mcp` 启动，需配置 `FIRECRAWL_API_KEY`。
- LangChain 代理可以利用 Firecrawl 的工具（如抓取、爬取、搜索）执行网页数据提取任务。
- 需要安装 `langchain-mcp-adapters`、`langchain` 和 `langchain-openai`，并确保 `npx` 已安装。
- 直接调用 Firecrawl 工具无需 MCP，但用户明确要求通过 MCP。

#### 设置环境

要使用 LangChain 通过 MCP 调用 Firecrawl 工具，首先需要安装必要的 Python 包和 Node.js 的 `npx` 工具。运行以下命令：

```bash
pip install langchain-mcp-adapters langchain langchain-openai
```

确保已安装 Node.js 和 npm，因为 `npx` 用于启动 Firecrawl MCP 服务器。获取 Firecrawl API 密钥并设置环境变量：

```bash
export FIRECRAWL_API_KEY=your_api_key_here
```

#### 配置 MCP 服务器

根据提供的 JSON 配置，Firecrawl MCP 服务器通过以下命令启动：

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

在 Python 代码中，使用 `langchain-mcp-adapters` 的 `StdioServerParameters` 配置此服务器。

#### 示例代码

以下 Python 代码展示了如何通过 MCP 调用 Firecrawl 工具并在 LangChain 代理中使用：

```python
import os
from langchain_mcp_adapters import StdioServerParameters, StdioMCPClient
from langchain.agents import initialize_agent, AgentType
from langchain_openai import OpenAI

# 设置 OpenAI API 密钥（根据需要替换为其他 LLM）
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# 确保 FIRECRAWL_API_KEY 已设置
assert "FIRECRAWL_API_KEY" in os.environ, "请设置 FIRECRAWL_API_KEY 环境变量"

# 配置 MCP 客户端
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "firecrawl-mcp"],
    env={"FIRECRAWL_API_KEY": os.environ["FIRECRAWL_API_KEY"]}
)

mcp_client = StdioMCPClient(server_params)
tools = mcp_client.get_tools()

# 初始化 LLM
llm = OpenAI(temperature=0)

# 初始化代理
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 示例：运行代理以抓取网页内容
response = agent.run("请抓取 https://firecrawl.dev 的内容")
print(response)
```

#### 使用说明

- **运行代理**：上述代码创建一个 LangChain 代理，自动选择合适的 Firecrawl 工具（如 `scrape`）来处理请求。
- **直接调用工具**：如果需要调用特定工具（如 `scrape`），可以从 `tools` 列表中选择并运行，例如：

```python
scrape_tool = next(tool for tool in tools if tool.name == "scrape")
result = scrape_tool.run({"url": "https://firecrawl.dev"})
```

- **注意事项**：确保 `npx` 可执行，且 `firecrawl-mcp` 包已通过 npm 全局安装（`npm install -g firecrawl-mcp`）。如果遇到问题，可尝试在 Windows 上运行 `cmd /c "set FIRECRAWL_API_KEY=your-api-key && npx -y firecrawl-mcp"`。

---

### 详细报告

用户提供的 JSON 配置表明，Firecrawl MCP 服务器通过 `npx -y firecrawl-mcp` 启动，并需要设置 `FIRECRAWL_API_KEY` 环境变量。本报告详细说明如何在 LangChain 中通过 MCP 调用 Firecrawl 工具，并提供完整的 Python 代码实现。

#### Firecrawl 功能

Firecrawl 提供多种功能，适合 LLM 应用：

- **抓取（Scrape）**：提取单个 URL 的内容，返回 markdown 或 HTML。
- **批量抓取（Batch Scrape）**：处理多个 URL，返回 markdown 或 HTML 数组。
- **爬取（Crawl）**：爬取网站及其子页面，返回每页的 markdown 或 HTML。
- **映射（Map）**：发现相关 URL，返回 URL 列表。
- **搜索（Search）**：执行网页搜索，返回结果列表。
- **提取（Extract）**：将网页内容转换为结构化 JSON 数据。
- **深度研究（Deep Research）**：进行深入分析，返回摘要和来源。
- **生成 LLMs.txt**：创建特定格式的文本文件。

这些功能通过 Firecrawl MCP 服务器以工具形式提供，LangChain 可以通过 `langchain-mcp-adapters` 库访问这些工具。

#### MCP 协议

MCP（Model Context Protocol）是一个开放协议，旨在标准化 AI 代理与外部工具的交互。它允许 LLM 动态发现和调用工具，无需为每个工具编写自定义代码。Firecrawl 的 MCP 服务器（`firecrawl-mcp`）通过 Node.js 包运行，提供上述工具的接口。LangChain 通过 `langchain-mcp-adapters` 库支持 MCP，将 MCP 工具转换为 LangChain 兼容的工具。

#### 设置环境

要通过 MCP 在 LangChain 中调用 Firecrawl，需要以下准备：

1. **安装 Python 包**：

   ```bash
   pip install langchain-mcp-adapters langchain langchain-openai
   ```

2. **安装 Node.js 和 npm**：确保 `npx` 可执行，用于运行 `firecrawl-mcp`。
3. **获取 API 密钥**：从 [Firecrawl API 密钥页面](https://www.firecrawl.dev/app/api-keys) 获取 `FIRECRAWL_API_KEY` 并设置环境变量：

   ```bash
   export FIRECRAWL_API_KEY=your_api_key_here
   ```

4. **安装 Firecrawl MCP（可选）**：全局安装 `firecrawl-mcp` 以确保命令可用：

   ```bash
   npm install -g firecrawl-mcp
   ```

#### 配置 MCP 服务器

用户提供的 JSON 配置如下：

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

此配置指定使用 `npx -y firecrawl-mcp` 启动 Firecrawl MCP 服务器，并通过环境变量传递 API 密钥。在 LangChain 中，使用 `StdioServerParameters` 实现此配置。

#### Python 代码实现

以下是完整的 Python 代码，用于通过 MCP 调用 Firecrawl 工具并在 LangChain 代理中使用：

```python
import os
from langchain_mcp_adapters import StdioServerParameters, StdioMCPClient
from langchain.agents import initialize_agent, AgentType
from langchain_openai import OpenAI

# 设置 OpenAI API 密钥（可替换为其他 LLM）
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# 确保 FIRECRAWL_API_KEY 已设置
assert "FIRECRAWL_API_KEY" in os.environ, "请设置 FIRECRAWL_API_KEY 环境变量"

# 配置 MCP 客户端
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "firecrawl-mcp"],
    env={"FIRECRAWL_API_KEY": os.environ["FIRECRAWL_API_KEY"]}
)

mcp_client = StdioMCPClient(server_params)
tools = mcp_client.get_tools()

# 初始化 LLM
llm = OpenAI(temperature=0)

# 初始化代理
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 示例：运行代理以抓取网页内容
response = agent.run("请抓取 https://firecrawl.dev 的内容")
print(response)
```

#### 代码说明

- **环境变量**：代码检查 `FIRECRAWL_API_KEY` 是否设置，并设置 `OPENAI_API_KEY`（如使用 OpenAI LLM）。
- **MCP 客户端**：`StdioServerParameters` 配置 `npx -y firecrawl-mcp` 命令和环境变量，`StdioMCPClient` 启动服务器并获取工具。
- **代理初始化**：使用 `initialize_agent` 创建一个零样本 ReAct 代理，加载 Firecrawl 工具，允许根据自然语言查询选择合适的工具。
- **运行示例**：代理运行查询“请抓取 <https://firecrawl.dev> 的内容”，自动调用 Firecrawl 的 `scrape` 工具。

#### 直接调用特定工具

如果需要直接调用特定 Firecrawl 工具（如 `scrape`），可以从 `tools` 列表中选择并运行：

```python
scrape_tool = next(tool for tool in tools if tool.name == "scrape")
result = scrape_tool.run({"url": "https://firecrawl.dev"})
print(result)
```

#### 替代方法：直接集成

虽然用户要求通过 MCP 调用 Firecrawl，LangChain 也支持直接使用 `FireCrawlLoader` 调用 Firecrawl，无需 MCP：

```python
from langchain_community.document_loaders.firecrawl import FireCrawlLoader

loader = FireCrawlLoader(
    api_key=os.environ["FIRECRAWL_API_KEY"],
    url="https://firecrawl.dev",
    mode="scrape"
)
documents = loader.load()
```

此方法更简单，但不使用 MCP，可能不符合用户要求。

#### 注意事项

- **依赖项**：确保 `npx` 和 `firecrawl-mcp` 可用。如果遇到问题，可尝试手动安装 `firecrawl-mcp` 或在 Windows 上使用 `cmd /c "set FIRECRAWL_API_KEY=your-api-key && npx -y firecrawl-mcp"`。
- **LLM 选择**：代码使用 OpenAI，但可替换为其他 LangChain 支持的 LLM（如 Hugging Face 模型）。
- **错误处理**：MCP 服务器支持自动重试（最多 3 次，初始延迟 1000ms，最大延迟 10000ms，退避因子 2），但需确保网络稳定。
- **性能优化**：对于批量操作，可使用 Firecrawl 的 `batch_scrape` 或 `crawl` 工具，通过 MCP 客户端调用。

#### 工具列表

Firecrawl MCP 服务器提供的工具包括：

| 工具名称         | 功能描述                              | 返回格式            |
|------------------|-------------------------------------|-------------------|
| Scrape           | 抓取单个 URL 的内容                  | Markdown/HTML     |
| Batch Scrape     | 抓取多个 URL 的内容                  | Markdown/HTML 数组 |
| Crawl            | 爬取网站及其子页面                   | Markdown/HTML 数组 |
| Map              | 发现相关 URL                        | URL 列表          |
| Search           | 执行网页搜索                        | 结果列表          |
| Extract          | 将网页内容转换为结构化数据            | JSON              |
| Deep Research    | 进行深入分析，返回摘要和来源          | 摘要和来源        |
| Generate LLMs.txt| 创建特定格式的文本文件               | 文本              |

#### 结论

通过 `langchain-mcp-adapters`，LangChain 可以无缝调用 Firecrawl MCP 服务器的工具，适合需要动态网页抓取的 AI 应用。用户提供的配置通过 `StdioServerParameters` 实现，代理可以根据自然语言查询自动选择工具。直接调用特定工具也是可行的，具体取决于应用需求。

## 参考

- [cline + DS + MCP](https://mp.weixin.qq.com/s/PuHwfJk3EZv8eR4y10EAvQ)
关键引用
- [Firecrawl 官方网站](https://www.firecrawl.dev/)
- [LangChain MCP Adapters GitHub](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol 介绍](https://modelcontextprotocol.io/introduction)
- [LangChain 文档](https://python.langchain.com/docs/)
- [Firecrawl MCP Server GitHub](https://github.com/mendableai/firecrawl-mcp-server)
- [LangChain Firecrawl 集成](https://python.langchain.com/docs/integrations/document_loaders/firecrawl/)
- [LangChain MCP 适配器公告](https://changelog.langchain.com/announcements/mcp-adapters-for-langchain-and-langgraph)
- [使用 LangChain 和 MCP](https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c)
- [创建 MCP 客户端服务器](https://www.analyticsvidhya.com/blog/2025/04/mcp-client-server-using-langchain/)
- [MCP 介绍](https://huggingface.co/blog/Kseniase/mcp)
- [LangChain.js 连接 MCP 服务器](https://blog.marcnuri.com/connecting-to-mcp-server-with-langchainjs)
- [LangChain MCP 工具 PyPI](https://pypi.org/project/langchain-mcp-tools/)
- [LangChain MCP 适配器指南](https://composio.dev/blog/langchain-mcp-adapter-a-step-by-step-guide-to-build-mcp-agents/)
- [LangDB Firecrawl MCP](https://langdb.ai/app/mcp-servers/firecrawl)
- [Langfuse Firecrawl 监控](https://langfuse.com/docs/integrations/other/firecrawl)
- [Firecrawl 初学者教程](https://apidog.com/blog/firecrawl-web-scraping/)
- [LangChain MCP RAG 教程](https://gaodalie.substack.com/p/langchain-mcp-rag-ollama-the-key)
