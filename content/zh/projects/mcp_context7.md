---
title: Context7
date: "2025-06-29T22:30:00+08:00"
lastmod: "2025-06-29T22:30:00+08:00"
draft: false
tags:  ["Context7","MCP"]
categories: ["projects"]
description: Context7 是一个用于 LLM 和 AI 编码编辑器的 MCP 服务器，可以提供最新的代码文档和代码示例，使得生成的代码更准确、版本相关且避免过时或虚假信息。非常适合配合AI编码助手使用更新版本的API。

--- 

## 介绍

Context7 是一个用于 LLM 和 AI 编码编辑器的 MCP 服务器，可以提供最新的代码文档和代码示例，使得生成的代码更准确、版本相关且避免过时或虚假信息。其主要功能包括：

1. **功能特点**：
   - 向 LLM 提供实时、版本特定的库文档和代码示例。
   - 无需切换标签或手动查找文档，直接将信息嵌入至提示中。
   - 避免生成错误的 API 或过时代码。

2. **安装要求**：
   - Node.js >= v18.0.0。
   - 支持多个 MCP 客户端（如 Cursor、Windsurf、Claude Desktop 等）。
   - 可通过多种集成方式进行安装（如 Docker、VS Code、Gemini CLI 等）。

3. **核心工具**：
   - `resolve-library-id`：解析库名以获取 Context7 兼容的库 ID。
   - `get-library-docs`：使用库 ID 获取相关文档，并支持主题聚焦和令牌限制。

4. **开发与运行**：
   - 使用 Bun 进行依赖安装、构建和运行。
   - 支持 `stdio`、`http` 和 `sse` 等多种数据传输方式。

5. **问题排查**：
   - 提供解决模块丢失、ESM 解析以及 TLS 证书问题的指导。

6. **免责声明**：
   - 项目内容由社区贡献，可能存在文档不准确或不安全的情况，用户需自行判断风险。

7. **开源许可**：
   - MIT License。

综上，Context7 提供了一个让 LLM 更高效的实时文档服务功能，是 AI 编码助手的强大支持工具。

## MCP 客户端

### 最常见的配置

```json
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    ... other mcp servers
  }
```

**注意**：更多配置请参考[Context7 npmjs](https://www.npmjs.com/package/@upstash/context7-mcp)

### 在Cursor中配置

### 在Gemini CLI中配置

在~/.gemini/settings.json中添加：“context7相关配置”，重新启动gemini cli即可。
在gemini cli中输入"/mcp",即可看到context7的mcp server。

```json
{
  "theme": "Default",
  "selectedAuthType": "gemini-api-key",
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },  
    "taskmaster-ai": {
      "command": "npx",
      "args": [
      "-y",
      "--package=task-master-ai",
      "task-master-ai"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "xxx",
        "OPENAI_API_KEY": "xxx",
        "GOOGLE_API_KEY": "xxx"
      }
    },  
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server"
      ]
    }
  },
  "preferredEditor": "cursor"
}
```
