---
title: "CCManager：多AI编码助手会话管理工具"
date: "2025-10-29T14:20:00+08:00"
draft: false
tags: ["ccmanager", "code_assistant", "git"]
categories: ["projects","code_assistant"]
description: "CCManager：多AI编码助手会话管理工具，无需借助tmux，完全独立运行"
---

CCManager 是一个 CLI 应用程序，用于管理多个 AI 编码助手会话（Claude Code、Gemini CLI、Codex CLI 等）以及 Git 项目工作树。

### 主要功能

1. **多会话管理**：支持并行运行多个 AI 助手会话，支持多项目管理。
2. **状态显示**：实时显示会话状态（等待、忙碌、空闲）。
3. **无需 tmux**：完全独立运行，不依赖 tmux。
4. **工作树操作**：创建、合并和删除 Git 工作树，支持在工作树间复制 Claude 会话数据以保持上下文。
5. **自定义快捷键**：支持 UI 或配置文件调整快捷键。
6. **状态钩子**：支持自动化命令触发（如通知、日志记录）。
7. **多项目支持**：能在单一界面下高效管理多个 Git 仓库。
8. **Devcontainer 集成**：支持在容器中运行 AI 会话，同时保持主机功能完备。
9. **自动目录生成**：基于分支名自动生成工作树路径。

### 安装与使用

- 使用命令安装：`npm install -g ccmanager`
- 发起会话命令：`ccmanager` 或 `npx ccmanager`
- 配置选项：支持通过 UI 或配置文件对命令参数、快捷键、状态钩子等进行自定义。

### 支持助手

- **Claude Code**：默认支持。
- **Gemini CLI**：提供专属状态检测。
- **其他支持**：支持 Codex CLI、Copilot CLI 等。

### 适用场景

- 为开发者提供简化和高效的 AI 编码助手会话管理工具，特别适合不使用 tmux 的用户。

项目技术基于 TypeScript，代码维护良好，当前为 v2.9.2

## 参考文献

- [CCManager Github](https://github.com/kbwo/ccmanager)
