---
title: "Claude Code 介绍"
date: "2025-07-20T23:10:00+08:00"
draft: false
tags: ["Agent", "Claude", "Code"]
categories: ["ai_tools"]
description: "Claude Code 是 Claude 的命令行工具，用于代理编码，提供灵活的、可定制的、可脚本化的和安全的编程方式。"
---

## 摘要

Claude Code 是一种命令行工具，用于代理编码，提供灵活的、可定制的、可脚本化的和安全的编程方式。
本文介绍Claude Code的快速上手，有用的功能，以及一些最佳实践。

### 关键点

- Claude Code 是一个用于代理编码的命令行工具，提供灵活和低级别的模型访问。
- CLAUDE.md 文件可以用于自动化上下文提取，是记录常用命令、代码风格和开发环境设置的理想场所。
- Claude Code 可以通过多种方式管理允许的工具，确保安全性。
- 可以通过自定义斜杠命令和使用 MCP 服务器扩展 Claude 的功能。
- 常见工作流程包括探索-计划-编码-提交，以及测试驱动开发等。
- Claude Code 支持无头模式，可用于自动化和持续集成。
- 多 Claude 工作流可以提高效率，例如一个 Claude 编写代码，另一个进行验证。
- 使用 git worktrees 可以在同一代码库的不同分支上同时运行多个 Claude 会话。

## 快速上手 （Windows版本 - VS code + powershell terminal）

Step 1:在VS code或Cursor里面的，打开一个powershell的terminal，输入以下命令：

```bash

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Navigate to your project
cd your-awesome-project
```

Step 2: 在项目中进行配置
建立.claude文件夹，里面建立一个settings.json文件，内容如下：
更多具体配置参考：<https://docs.anthropic.com/en/docs/claude-code/settings>

```json
{
    "installMethod": "unknown",
    "autoUpdates": true,
    "hasCompletedOnboarding": true,
    "env": {
      "CLAUDE_CODE_MAX_OUTPUT_TOKENS": 1024000,
      "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic/",
      "ANTHROPIC_API_KEY": "sk-fIIumnFFi4BvpbbRrc8wI8vQYAOJ65MCr0M9BVnCGVeUci9x"
    },
    "enabledMcpjsonServers": ["memory", "github"]
}
```

Step 3: 集成Kimi K2 model

Step 4: 配置MCP服务器
在.claude文件夹里面建立一个mcp.json文件，内容如下：

```json
{
 "mcpServers": {
  "task-master-ai": {
   "command": "npx",
   "args": ["-y", "--package=task-master-ai", "task-master-ai"],
   "env": {
    "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY_HERE",
    "PERPLEXITY_API_KEY": "PERPLEXITY_API_KEY_HERE",
    "OPENAI_API_KEY": "sk-WO6DtsQqCPPd7YF3A94cC7E9E76a4dE0AbCf3f980c59CfB3",
    "OPENAI_BASE_URL": "https://api.openai120.com/v1",
    "GOOGLE_API_KEY": "GOOGLE_API_KEY_HERE",
    "XAI_API_KEY": "XAI_API_KEY_HERE",
    "OPENROUTER_API_KEY": "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",
    "MISTRAL_API_KEY": "MISTRAL_API_KEY_HERE",
    "AZURE_OPENAI_API_KEY": "AZURE_OPENAI_API_KEY_HERE",
    "OLLAMA_API_KEY": "OLLAMA_API_KEY_HERE"
   }
  },
  "context7": {
   "command": "npx",
   "args": ["-y", "@upstash/context7-mcp"]
  },
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
  }
 }
}
```

Step 5: 集成到IDE

# Start coding with Claude

claude

Step 4: 集成到github action workflow
Claude code action 允许您在GitHub Actions工作流中运行Claude Code。您可以使用此功能在Claude Code基础上构建任何自定义工作流。

参考[Claude Code Github Action 文档](https://docs.anthropic.com/en/docs/claude-code/github-actions)
参考[claude-code-action](https://github.com/anthropics/claude-code-action)
参考[claude-code-action 使用示例](https://github.com/anthropics/claude-code-action/blob/main/examples/)

### 有用或有趣的功能

#### 自定义斜杠功能

### 最佳实践

[该文](https://www.anthropic.com/engineering/claude-code-best-practices)介绍了使用 Claude Code 的最佳实践，包括如何设置、优化以及常见的工作流程。
