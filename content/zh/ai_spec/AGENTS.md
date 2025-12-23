---
title: AGENTS.md 规范深度解读
date: "2025-12-10T22:10:00+08:00"
draft: false
tags: ["AI", "AGENTS.md", "coding agent"]
categories: ["ai_spec"]
description: "**AGENTS.md** 是由 OpenAI 开发的一种简单、开放的格式，用于指导编码代理（AI Coding Agent（如 GitHub Copilot、Cursor、Windsurf 等））看的“操作手册”。它由 OpenAI 开发并贡献给 Agentic AI Foundation (AAIF)。"
wordCount: 3017
readingTime: 8
---

**AGENTS.md** 是由 OpenAI 开发的一种简单、开放的格式，用于指导编码代理（AI Coding Agent（如 GitHub Copilot、Cursor、Windsurf 等））看的“操作手册”。已被超过[6万个开源项目采用](https://github.com/search?q=path%3AAGENTS.md+NOT+is%3Afork+NOT+is%3Aarchived&type=code)。将AGENTS.md视为代理的README：一个专门、可预测的位置，用于提供上下文和指令，帮助AI编码代理处理您的项目。

并贡献给 **Agentic AI Foundation (AAIF)** 的一种开源文档格式标准。你可以将其理解为\*\*“写给 AI 代理（AI Agents）看的 README”\*\*。 
它的主页为：[https://agents.md](https://agents.md), 开源项目地址为：[https://github.com/agentsmd/agents.md](https://github.com/agentsmd/agents.md), 

它旨在解决 AI 编码助手（如 OpenAI Codex、Cursor、GitHub Copilot 等）在处理复杂项目时上下文缺失的问题，通过标准化的格式为 AI 提供明确的“行动指南”。 AGENTS.md和CLAUDE.md和GEMINI.md的作用在各自的AI 编码开发工具（CodeX， Claude Code， Gemini CLI）的功能定位几乎完全一致，但在“行业地位”上正在发生微妙的分化。这个在文章最后会进一步展开。

以下是关于 AGENTS.md 的细节解读：

### 1\. 核心设计理念：人机分流

在软件开发中，`README.md` 是写给人看的，包含项目简介、快速上手等概括性信息。而 `AGENTS.md` 是专门写给 AI 看的，它包含了人类开发者通常默认知晓、但 AI 需要明确指令才能执行的**隐性知识**。

  * **README.md (For Humans):** 关注“这是什么项目”、“怎么跑起来”。
  * **AGENTS.md (For AI):** 关注“如何精确地修改代码”、“必须遵守哪些潜规则”、“绝对不能做的事情”。

### 2\. 标准文件结构与内容

`AGENTS.md` 是一个标准的 Markdown 文件，通常放置在项目根目录或 `.github/` 目录下。它不依赖复杂的 Schema，而是利用 LLM 强大的自然语言理解能力，通过清晰的标题和列表来传递指令。

一个典型的 `AGENTS.md` 包含以下关键板块：

  * **环境上下文 (Context):** 明确项目的具体技术栈版本（例如："Next.js 14 (App Router), Tailwind CSS, TypeScript 5.0"），避免 AI 使用过时语法。
  * **构建与测试指令 (Build & Test):** 精确的命令序列。
      * *示例：* "运行测试必须使用 `pnpm test`，提交代码前必须通过所有 lint 检查。"
  * **代码风格与规范 (Conventions):** 具体的编码偏好。
      * *示例：* "使用函数式组件而非类组件"、"变量命名强制使用驼峰式 (camelCase)"、"所有接口必须定义在 `types/` 目录下"。
  * **行为边界 (Boundaries):** **这是最重要的部分**，规定 AI 的权限。
      * *示例：* "你可以修改 `src/components` 下的文件，但**严禁**修改 `prisma/schema.prisma` 数据库定义文件，除非得到明确授权。"
  * **Git 工作流 (Workflow):** Commit 信息格式、分支命名规则等。

### 3\. AGENTS.md 文件示例

以下是一个标准的 `AGENTS.md` 文件模板，展示了它是如何指导 AI 的：

```markdown
# AGENTS.md - AI 编码助手指南

## 1. 项目概况
- 本项目是一个基于 React + Vite 的待办事项应用。
- 核心技术栈：React 18, TypeScript, Zustand (状态管理), Tailwind CSS。

## 2. 行为准则 (Boundaries)
- **允许：** 编写和重构 `src/` 目录下的 UI 组件和逻辑。
- **禁止：** 修改 `.github/workflows` 下的 CI/CD 配置。
- **注意：** 如果修改了 `package.json`，必须运行 `pnpm install` 并更新锁文件。

## 3. 编码规范
- **组件：** 所有新组件必须放在 `src/components` 下，并使用命名导出 (Named Exports)。
- **样式：** 严禁写行内样式 (style={{...}})，必须使用 Tailwind 类名。
- **测试：** 每增加一个 Utils 函数，必须在 `tests/` 目录下编写对应的单元测试。

## 4. 常用命令
- 启动开发服：`pnpm dev`
- 运行测试：`pnpm test:unit`
- 代码格式化：`pnpm format`
```

### 4\. 生态系统与 AAIF 的角色

OpenAI 将此格式捐赠给 Linux 基金会旗下的 **Agentic AI Foundation (AAIF)**，意在推动行业标准的统一。

  * **互操作性：** 无论是使用 Cursor、Devin 还是 GitHub Copilot，只要仓库里有这个文件，所有 AI Agent 都能读懂项目的“家规”，无需用户重复通过 Prompt 输入上下文。
  * **单体仓库支持：** 在 Monorepo（单体仓库）中，可以在不同子目录下放置不同的 `AGENTS.md`，AI 会根据当前编辑的文件自动读取最近的配置文件，实现更细粒度的控制。

-----

### 5. 3个相关联的主题

1.  **Model Context Protocol (MCP):** 由 Anthropic 推出并同样贡献给 AAIF 的协议，它关注 AI 如何连接外部数据源（如数据库、Slack），与 AGENTS.md（关注代码行为规范）形成互补。
2.  **Agentic Workflow (代理工作流):** 探讨如何将单一的编码任务编排成“规划-执行-检查-修正”的自动化闭环，AGENTS.md 是该闭环中的核心约束文档。
3.  **Prompt Engineering vs. Context Engineering:** AGENTS.md 代表了从单纯的提示词工程向“上下文工程”的转变，即通过固化环境上下文来降低对即时提示词的依赖。

## 6. AGENTS.md、CLAUDE.md和GEMINI.md的异同

它们在功能定位上几乎完全一致，但在“行业地位”上正在发生微妙的分化。

你可以把它们都看作是 **"AI Agent 的岗位说明书"**。它们存在的目的都是为了给 AI 编码工具提供持久化的、项目级别的上下文（Context），填补了通用大模型（Foundation Model）与具体项目细节之间的鸿沟。

以下是它们在各自生态位中的详细对比与地位解析：

### 1\. 三者地位横向对比表

| 特性 | **AGENTS.md** | **CLAUDE.md** | **GEMINI.md** |
| :--- | :--- | :--- | :--- |
| **主导机构** | **OpenAI / AAIF** (行业联盟) | **Anthropic** | **Google** |
| **原生工具** | GitHub Copilot, Cursor, OpenAI Codex | Claude Code (CLI) | Gemini CLI, Gemini Code Assist |
| **核心定位** | **通用标准 (The Standard)** | **专用配置 (Native Config)** | **专用配置 (Native Config)** |
| **互操作性** | 极高（旨在被所有工具兼容） | 中（主要服务于 Claude 生态） | 高（官方 CLI 支持读取 AGENTS.md） |
| **设计哲学** | 像 robots.txt 一样的公共协议 | 像 .eslintrc 一样的工具配置文件 | 像 Dockerfile 一样的环境构建指令 |

### 2\. 深度解析：细微的地位差异

#### A. `AGENTS.md`: 试图成为 AI 界的 "Markdown"

  * **地位：** 它正在演变成一种**跨平台的行业标准**。
  * **设计哲学：** 它不只是给某个特定工具看的，而是给所有访问该代码库的智能体（Agents）看的。它假设 Agent 具有高度的自主性。
  * **现状：** 虽然它最早由 OpenAI 贡献，但目前 GitHub Copilot 的 "Agent Mode" 已经原生支持它。Cursor 等新兴 IDE 也可以读取它。它的野心最大，试图让开发者只写一份文档，就能指挥所有的 AI（无论是 GPT-4, Claude 3.5 还是 Gemini 1.5）。
  * **趋势：** 越来越多的开源项目开始默认通过 `AGENTS.md` 来“声明”自己的代码规范，而不是为每个 AI 写不同的文件。
  * **关键特性：**
    * **边界设定 (Boundaries)：** 明确规定 AI 不能做什么（例如：“禁止修改 legacy/ 目录下的代码”）。
    * **架构意图：** 解释“为什么”代码是这样写的，而不仅仅是“怎么写”。

#### B. `CLAUDE.md`: 强大的为 CLI 优化的 "战术手册"

  * **地位：** **Claude Code CLI 的核心大脑**。
  * **设计哲学：** 它是为 Claude Code CLI 量身定制的。因为 Claude Code 是一个在终端运行的工具，它非常依赖简短、精准的指令来执行任务。
  * **现状：** 在 Claude Code 工具链中，它的权限非常高。它不仅包含规范，往往还包含针对 Claude 模型的特定 Prompt 优化技巧（Context Caching 策略等）。
  * **兼容性：** 很多开发者现在的做法是：创建一个 `AGENTS.md` 作为“真理来源”，然后通过软链接（Symlink）生成一个 `CLAUDE.md` 指向它，因为 Claude Code 默认首选读取 `CLAUDE.md`。
  * **关键特性：**
    * **常用命令 (Common Commands)：** 它通常包含一个明确的“常用命令”部分（如 Build, Test, Lint），Claude Code 会直接读取并尝试执行这些命令。
    * **Token 效率：** Anthropic 的文档建议 CLAUDE.md 保持精简，只包含高价值信息，利用 Claude 的长上下文能力但不过度浪费。
    * **错误处理：** 经常包含“如果你遇到 X 错误，请尝试 Y”的具体修复指南。

#### C. `GEMINI.md`: 灵活的 "变色龙"

  * **地位：** **Google AI 开发者生态的入口文件**。
  * **设计哲学：** 服务于 Google 庞大的开发生态（Android Studio, Firebase, Google Cloud）。它倾向于将代码上下文与云端资源连接起来。
  * **现状：** 主要用于 `gemini-cli` 和 VS Code 里的 Gemini Code Assist 插件。Google 的策略比较灵活，`gemini-cli` 的配置文件（`settings.json`）允许用户将 `contextFileName` 修改为 `AGENTS.md`。
  * **特点：** 它支持层级化加载（Hierarchical Loading），即可以读取 `~/.gemini/GEMINI.md`（全局配置）和 `./GEMINI.md`（项目配置）并进行合并，这在大型企业级项目中非常有用。
  * **关键特性：**
    * **多模态友好：** 在 Google 的愿景中，这个文件未来可能包含指向设计图（Figma 链接）或架构图的引用，利用 Gemini 的多模态能力。
    * **层级化 (Hierarchy)：** 支持更复杂的配置继承，适应大型 Monorepo（单体仓库）。
    * **强类型提示：** 在涉及 Go 或 Flutter 等 Google 强推的技术栈时，往往包含更严格的类型和风格约束。

#### 实际文件内容对比 (代码示例)
为了让你直观感受到区别，假设我们有一个 React + TypeScript 项目，下面是三个文件可能呈现的不同画风：
AGENTS.md (注重规范与架构)
```markdown
# AGENTS.md
## Project Context
User is a senior Full-Stack dev. Focus on Clean Architecture.

## Architecture
- **Frontend:** React 18, Vite. Feature-based folder structure.
- **State:** Zustand strictly. Do NOT use Redux.

## Guidelines
- Always prefer functional components.
- Use `zod` for all API response validation.
- **BOUNDARY:** Never modify the `src/core` folder without explicit user permission.
```

CLAUDE.md (注重可执行命令)
```markdown
# CLAUDE.md
## Build & Test
- Build: `npm run build`
- Test: `npm test -- --watchAll=false`
- Lint: `npm run lint`

## Code Style
- TypeScript: Strict mode enabled.
- Naming: camelCase for vars, PascalCase for components.

## Error Handling
- If you encounter "X" error, try "Y" instead.

## Troubleshooting
- If build fails on 'heap out of memory', run `export NODE_OPTIONS=--max_old_space_size=4096`.

```
GEMINI.md (注重生态集成)
```markdown
# GEMINI.md
## Integration with Google Cloud
- **Firebase:** Use Firebase Authentication for user login.
- **Cloud Firestore:** Store user data and application state.
- **Cloud Storage:** Host static assets like images.

## Documentation References
- API Specs: ./docs/openapi.yaml
- Design System: [Link to Material Design 3 guidelines]

## Conventions
- Use Go-style error handling logic where applicable.
- For UI components, strictly follow Material UI (MUI) v5 implementation patterns.

## Best Practices
- Follow Google's official style guide for React and TypeScript.
- Use Firebase's best practices for real-time data synchronization.
```



### 3\. 实际开发中的最佳实践

如果你的团队混合使用多种 AI 工具（比如有人用 Cursor，有人用 GitHub Copilot，有人用 Claude Code），建议采用 **"AGENTS.md First"** 策略：

1.  **维护一份主文件：** 在项目根目录创建详细的 `AGENTS.md`，包含所有规范、命令和架构说明。
2.  **配置特定工具：**
      * **Claude Code:** 运行 `ln -s AGENTS.md CLAUDE.md` 创建软链接。
      * **Gemini CLI:** 在 `.gemini/settings.json` 中设置 `"contextFileName": "AGENTS.md"`。
      * **GitHub Copilot:** 原生直接读取 `AGENTS.md`。
      * **Prompt 注入:** 在你的 IDE 设置（如 Cursor Rules）中，配置一条系统级 Prompt：“总是首先读取 AGENTS.md 作为你的上下文配置。”

-----

### 3个相关联的主题

1.  **Context Caching (上下文缓存):** 随着 `AGENTS.md` 文件越来越大，如何利用 Gemini 1.5 Pro 或 Claude 3.5 的长上下文缓存功能来降低 Token 成本，是进阶的工程化话题。
2.  **MCP (Model Context Protocol):** `AGENTS.md` 告诉 AI **“怎么做”** (规范)，而 MCP 告诉 AI **“去哪查”** (数据源连接)。两者结合是构建高级 AI Agent 的基石。
3.  **Hierarchical Context Injection (层级上下文注入):** 在 Monorepo（单体仓库）中，如何在根目录和子项目目录分别放置 `AGENTS.md`，实现从通用规范到特定模块规范的继承与覆盖。
4.  **CLAUDE.md 与 Claude Skills的关系：** 参看我的[claude skills的博客](https://hobbytp.github.io/zh/claude/claude_skills/)

## 7. 有创意的想法

### 7.1. 基于 AGENTS.md 的 "AI 行为单元测试"

**想法描述：** 既然 `AGENTS.md` 是给 AI 的“需求文档”，那我们就应该能测试 AI 是否遵守了它。
**具体实现：** 编写一个 CI 脚本，包含一组预设的“陷阱任务”。

  * 例如，在 `AGENTS.md` 中规定：“禁止使用 `console.log`，必须使用 `logger.info`”。
  * **测试流程：** 在 CI 中启动一个 AI Agent，给它一个“请帮我打印调试信息”的任务。
  * **断言：** 检查 AI 生成的代码。如果它写了 `console.log`，则该 AI 模型或 Prompt 策略的“合规性测试”失败。
    这能让你量化评估不同模型（如 GPT-4o vs Claude 3.5 Sonnet）在遵守你项目 `AGENTS.md` 规范时的“听话程度”。

### 7.2. AI 的“入职培训文档”自动生成器

**想法描述：** 开发一个 CI/CD 插件或 GitHub Action，名为 **"Agent Onboarding"**。
**功能：** 它可以扫描你现有的代码库，分析 Git 历史记录、代码风格（通过 ESLint/Prettier 配置）以及现有的 README，**自动生成一份初版的 `AGENTS.md`**。
**价值：** 这就像给新入职的员工自动生成一份“避坑指南”。它能自动提取出“即使没写在文档里，但大家都在遵守”的潜规则（比如大家都喜欢用 `map` 而不是 `for` 循环），让 AI 代理瞬间达到团队老员工的编码默契度。

## 参考文献
* [agents.md主页](https://agents.md), 
* [agents.md开源项目](https://github.com/agentsmd/agents.md)
* [OpenAI Codex Tutorial \#6 - Using the AGENTS.md file](https://www.youtube.com/watch?v=NlNuoH5PPl4)
*此视频是 OpenAI Codex 系列教程的一部分，详细演示了如何在实际开发中创建和使用 AGENTS.md 文件来指导 AI 编写符合项目规范的代码，非常适合希望直观了解其用法的开发者。*

