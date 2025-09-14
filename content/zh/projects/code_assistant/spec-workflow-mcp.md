---
title: "Claude Code Spec Workflow, 也支持MCP方式"
date: "2025-09-14T22:30:00+08:00"
draft: false
tags: ["mcp", "spec", "workflow"]
categories: ["projects","code_assistant"]
description: "Claude Code Spec Workflow, 也支持MCP方式"
---

该 GitHub 项目“[spec-workflow-mcp](https://github.com/Pimzino/spec-workflow-mcp)”是项目[Claude Code Spec Workflow](https://github.com/Pimzino/claude-code-spec-workflow)的延续，是为了支持所有能使用MCP的AI Coding Assistants,比如Cursor，Cline, Copilot等。这里的Spec和AWS的Kiro的Spec是同一个意思，和github spec-kit里的spec也是同一个意思。

## 摘要

**spec-workflow-mcp**是一款基于模型上下文协议（MCP）的服务器，旨在为AI辅助软件开发提供结构化的规范驱动工作流工具。主要功能包括：

1. **结构化开发工作流** - 按顺序创建规范：需求→设计→任务。
2. **实时 Web 仪表盘** - 实时监控规范、任务和进度。
3. **VSCode 扩展** - 为VSCode用户提供集成的侧边栏仪表盘。
4. **审批工作流** - 完整的审批流程，支持修订。
5. **任务进度跟踪** - 可视化进度条和详细状态。
6. **多语言支持** - 提供11种语言，包括中文、英文、日语等。

项目提供快速上手指南，包括通过CLI或VSCode扩展启动。支持使用仪表盘或VSCode完成规范的创建、管理和任务执行。代码主要使用TypeScript开发，并附带详细的文档和贡献指南。项目采用GPL-3.0许可证，已有1.7k星标。

**注意**这个项目可以和github的spec-kit项目连起来看，这个项目可以立即使用起来，而spec-kit更倾向于定制一个标准，所以进度会更慢一些。

## 快速上手

在cursor里面配置MCP Server.
**注意**： 作为一台 MCP 服务器，在 MCP 启动过程中设置特定的客户端项目路径是相当不寻常的。因为这意味着它无法同时支持更多的客户端。所以我开了一个[issue #94](https://github.com/Pimzino/spec-workflow-mcp/issues/94)

```json
{
  "mcpServers": {
    "spec-workflow": {
      "command": "npx",
      "args": ["-y", "@pimzino/spec-workflow-mcp@latest", "/path/to/your/project"]
    }
  }
}
```

可以参考视频[MCP Server配置 - 在Cursor中集成规范驱动开发](https://www.youtube.com/watch?v=ruAy8oBR5lA&t=439s)，该视频的完整版本在下面的“**完整实战**”章节。

## 完整实战

实战视频可以参考这个视频：
[AI超元域: 支持Cursor！Claude Code Spec Workflow为Claude Code完美复现Kiro的Spec-Driven规范驱动开发！](https://www.youtube.com/watch?v=ruAy8oBR5lA)

- 集成Claude Code CLI使用（基于<https://github.com/Pimzino/claude-code-spec-workflow）>
- 集成Cursor使用（基于<https://github.com/Pimzino/spec-workflow-mcp>, 使用MCP Server的方式）
