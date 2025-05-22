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

## 参考

[cline + DS + MCP](https://mp.weixin.qq.com/s/PuHwfJk3EZv8eR4y10EAvQ)
