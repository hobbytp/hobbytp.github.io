---
title: "AI超元域 YouTube：Claude Code / CodeX / Gemini CLI / Copilot 相关视频汇总"
date: "2026-01-20T21:11:30+08:00"
draft: false
tags: ["youtube", "claude", "codex", "gemini", "copilot", "ai_programming"]
categories: ["ai_programming"]
description: "收集 @AIsuperdomain（超元域）频道中与 Claude Code、Codex/CodeX、Gemini CLI、GitHub Copilot 及相关插件/规范/增强工具有关的视频链接。"

ai_cover: "/images/generated-covers/d99672dc058a946b17d52a8527b079dc.webp"
cover:
  image: "/images/generated-covers/d99672dc058a946b17d52a8527b079dc.webp"
  alt: "AI超元域 YouTube：Claude Code / CodeX / Gemini CLI / Copilot 相关视频汇总"
  ai_generated: true
wordCount: 4628
readingTime: 12
---

## 超元域 YouTube：Claude Code / CodeX / Gemini CLI / Copilot 相关视频汇总
AI超元域是我喜欢的一个频道，这篇文章主要关注他的关于AI编程工具的视频。基于这些视频，我可以了解到Claude Code 的相关生态系统已经非常庞大且专业化。这些工具、插件、Skill 和开源项目可以清晰地分为以下 **七大类**：

### 1. 连接协议与基础设施 (Model Context Protocol - MCP)
这是目前最核心的扩展方式，被称为“颠覆性创新”，旨在解决 AI 模型与外部数据/工具连接的标准化问题。
*   **核心作用**：让 Claude Code 连接外部世界（数据库、浏览器、本地文件、API）。
*   **典型项目**：
    *   **通用连接**：**Context7**（搜索项目最新文档）、**Fetch MCP**（抓取网页内容）。
    *   **浏览器自动化**：**Browser Use**（AI 驱动的浏览器操作框架）、**Chrome DevTools MCP**（原生支持 Chrome 调试和自动化）、**Stagehand**。
    *   **代码分析与语言服务**：**Serena**（基于 LSP 协议，理解代码依赖关系而非单纯读取文本）、**Code2MCP**（将现有 GitHub 代码库自动转为 MCP 服务）。
    *   **知识库与记忆**：**Graphiti**（构建时序知识图谱，实现持久化记忆）、**LightRAG**（基于图结构的检索增强生成）。
    *   **数据库操作**：**SQLite MCP**（允许 AI 操作数据库）。
    *   **中间件**：**mcpo**（Open WebUI 推出的代理工具，将 MCP 转为 OpenAI API 格式）。

### 2. 工作流与方法论框架 (Workflow Frameworks)
这类项目不仅仅是工具，而是将软件工程的最佳实践（如敏捷开发、TDD）固化为 AI 必须遵守的流程，旨在消除随意的“Vibe Coding”。
*   **核心作用**：约束 AI 的行为，强制执行特定开发流程（如先写文档再写代码）。
*   **典型项目**：
    *   **Superpowers**：一个完整的软件开发工作流系统，强制执行 **TDD（测试驱动开发）**，包含头脑风暴、编写计划、执行计划等步骤。
    *   **Spec-Driven（规范驱动）**：**OpenSpec**、**SpecKit**、**Claude Code Spec Workflow**。这些工具要求先生成可执行的规范（Spec），再生成代码，确保“零猜想”。
    *   **敏捷开发**：**BMad-Method**（多智能体协作框架，模拟敏捷开发团队，如产品经理、架构师、QA）。
    *   **项目管理**：**Claude Code PM** (CCPM)（将 PRD 转为 GitHub Issues，支持并行开发）。

### 3. 技能与行为定义 (Agent Skills)
Skills 是“程序化知识”，告诉 AI “如何做”某事（如代码审查的具体标准），不同于 MCP（提供“做什么”的能力）。
*   **核心作用**：封装重复性指令、脚本和最佳实践，实现按需加载，节省 Token。
*   **典型项目**：
    *   **标准库**：**anthropics/skills**（官方提供的文档处理等技能）、**agentskills.io**（开放标准）。
    *   **高级技巧**：**Decision Trees（决策树）Skills**（在 Skill 中嵌入 if-else 逻辑，让 AI 自主决策使用哪个工具，例如在 Code Review 时自动选择 Gemini 或 Codex）。
    *   **特定领域**：**UI/UX Pro Max Skills**（专注于前端设计）。

### 4. 客户端与交互界面 (Clients & GUIs)
除了官方的 CLI，社区开发了多种替代客户端或 GUI 包装器，以此降低使用门槛或规避封号风险。
*   **核心作用**：提供更友好的交互界面，或作为开源替代品。
*   **典型项目**：
    *   **OpenCode**：Claude Code 的开源替代品，支持多模型切换（如 DeepSeek, Gemini），解决封号问题，支持 LSP。
    *   **Claudia**：专为 Claude Code 打造的可视化 GUI 界面，告别命令行操作。
    *   **IDE 集成**：**Cline** (原 Claude Dev)、**Roo Cline** (Cline 的分支，支持多语言和更多配置)、**Windsurf**、**Antigravity IDE**。这些插件允许在 IDE 内部运行类似 Claude Code 的智能体。
    *   **其他 CLI**：**Gemini CLI**、**OpenAI Codex CLI**、**GitHub Copilot CLI**。

### 5. 多智能体与协作编排 (Multi-Agent Orchestration)
利用多个 AI 模型或智能体分工合作，解决单一模型能力不足或成本过高的问题。
*   **核心作用**：根据任务难度动态调度不同模型（如用 Gemini Pro 做长文档分析，用 o3 做逻辑推理）。
*   **典型项目**：
    *   **Oh My OpenCode (OMO)**：OpenCode 的最强插件，内置 **Sisyphus** 智能体指挥多 AI 协作，实现“一人抵一个开发团队”。
    *   **Zen MCP**：允许 Claude 协调调用 Gemini 2.5、OpenAI o3 等模型，实现多模型协作开发。
    *   **Sub-agents**：Claude Code 原生功能，创建独立的子智能体处理特定任务，防止上下文污染。
    *   **框架集成**：**AutoGen**、**LangFlow**、**Smolagents**（通过 MCP 与 Claude Code 集成）。

### 6. 配置与上下文工程 (Configuration & Context Engineering)
通过预定义文件来控制 AI 的行为和项目认知。
*   **核心作用**：让 AI “开箱即用”地理解项目架构和规则。
*   **典型项目**：
    *   **SuperClaude**：一个配置框架，提供 19 个专业命令和 9 个预定义角色（如架构师、前端专家）。
    *   **Context Engineering**：从提示词工程升级为上下文工程，通过 `.clinerules`、`CLAUDE.md` 或 `agent.md` 文件定义项目结构和编码规范。
    *   **Output Styles**：Claude Code 的新功能，通过修改系统提示词将 Claude 变成不同类型的智能体（如教学模式）。

### 7. 自动化与循环控制 (Automation & Loop Control)
解决 AI 完成任务后“过早退出”的问题，强制其进行自我修正和迭代。
*   **核心作用**：将 Claude Code 变成“永不停歇”的开发机器。
*   **典型项目**：
    *   **Ralph Wiggum**：一个插件，拦截 Claude Code 的退出信号，强制其继续迭代，直到满足通过条件（如测试通过），特别适合修复 Bug。


## 附录    
频道主页：https://www.youtube.com/@AIsuperdomain

生成时间：2026-01-20 21:11:30 +0800

筛选说明：优先收录标题明确包含 Claude Code / Codex(CodeX) / Gemini CLI / Copilot 的视频；并补充收录与这些工具强相关的 MCP、Cursor、Cline、Windsurf、OpenSpec/Spec-driven、Superpowers、OpenCode、Agent Skills/Antigravity 等工作流/插件/规范类视频。


共抓取到 245 条频道视频列表记录，命中 65 条。

| 日期 | 标题 | 关键词 | 链接 |
| --- | --- | --- | --- |
| 2026-01-17 | 🚀Agent Skills决策树高级技巧！让Antigravity和Claude Code减少80%手动干预，AI编程助手终于能自主决策了！Codex CLI+Gemini CLI实现智能化代码审查 | Claude Code, Claude, Codex/CodeX, Gemini CLI, Gemini, Agent Skills/Antigravity | https://www.youtube.com/watch?v=Qydk2wlh4YI |
| 2026-01-15 | 🚀2026年Skills元年正式开启！谷歌Antigravity支持Agent Skills，彻底改写传统AI编程！保姆级教程从安装到创建到调用！UI UX Pro Max Skills实测效果超预期 | Agent Skills/Antigravity | https://www.youtube.com/watch?v=KD2D59_XGd8 |
| 2026-01-11 | 🚀告别Vibe Coding！用Superpowers让Claude Code写出工程级代码，一次通过零报错！遵循TDD最佳实践！支持Codex和OpenCode！从需求澄清到代码审查 | Claude Code, Claude, Codex/CodeX, Superpowers, OpenCode | https://www.youtube.com/watch?v=TMmq9Wx1AIQ |
| 2026-01-09 | 🚀开发者福音！一人抵一个开发团队！OpenCode最强插件Oh My Opencode实测：Sisyphus智能体指挥多AI协作，复杂项目开发效率倍增！全程零干预！指挥大模型疯狂干活 | OpenCode | https://www.youtube.com/watch?v=twFjLiy2Pmc |
| 2026-01-07 | 🚀开源界的Claude Code来了！生产力核弹opencode深度使用体验，LSP完整支持，Token消耗一目了然，程序员福音！支持Antigravity IDE！结合OpenSpec规格驱动开发！ | Claude Code, Claude, Agent Skills/Antigravity, OpenCode, OpenSpec/Spec-driven | https://www.youtube.com/watch?v=_h2MGwJO1Yc |
| 2026-01-05 | 🚀Claude Code创始人Boris亲自揭秘：他的设置竟然如此简单！开箱即用才是最强工作流，复利工程思维让效率翻倍！Opus 4.5计划模式+iTerm2+斜杠命令+GitHub Actions | Claude Code, Claude | https://www.youtube.com/watch?v=Xm-n4m7IaZk |
| 2026-01-03 | ⚡开发者神器来了！Anthropic官方Ralph Wiggum插件深度实测：让Claude Code变身永不停歇的全自动开发机器！告别手动调试！iOS原生应用20轮优化后效果惊人！Bug修复全自动 | Claude Code, Claude | https://www.youtube.com/watch?v=T8nQSFXvoLA |
| 2025-12-25 | 🚀告别Cursor繁琐代码，Readdy AI一句话生成精美网站，自动部署上线，还能24小时智能接待客户！实测从零到上线只需5分钟！@ReaddyAI | Cursor | https://www.youtube.com/watch?v=bVQ95AUqMUw |
| 2025-12-20 | 🚀开发者必看！Codex新增Agent Skills！GPT-5.2-Codex三大编程任务实测，结果出乎意料！实战开发iOS App，它真的能取代程序员吗？到底是“生产力核弹”还是“又慢又贵”？ | Codex/CodeX, Agent Skills/Antigravity | https://www.youtube.com/watch?v=p05Dt9jBouk |
| 2025-12-19 | 🚀丢掉playwright吧！Claude Code原生支持Chrome浏览器！全自动调用Chrome开发React组件、自动发现Bug、自动修复，自动化测试API接口！全自动化开发流程实测！#ai | Claude Code, Claude | https://www.youtube.com/watch?v=wVS-J7lRLlg |
| 2025-12-14 | 🚀用Antigravity IDE跑Claude Opus 4.5：速度比Codex+GPT-5.2快太多？谷歌Antigravity保姆级教程，Pro账户额度超充足，再也不怕Claude封号 | Claude, Codex/CodeX, Agent Skills/Antigravity | https://www.youtube.com/watch?v=vz0-W3BwFQU |
| 2025-12-12 | 🚀开发者必看！GPT-5.2深度实测！基准测试碾压Claude Opus 4.5？Codex实测揭秘其真实编程水平，请不要继续吹捧了！ | Claude, Codex/CodeX | https://www.youtube.com/watch?v=Y2n1HbXXP2c |
| 2025-11-19 | 🚀开发者必看！深度测评谷歌Gemini 3 Pro + Antigravity IDE！对比Claude Sonnet 4.5前端编程巅峰对决！模型能力是否被高估了？ | Claude, Gemini, Agent Skills/Antigravity | https://www.youtube.com/watch?v=ob88sANtez8 |
| 2025-11-18 | 🚀告别 Cursor！这个 AI 一键生成完整应用和游戏，Lumi.new 深度实战 | Cursor | https://www.youtube.com/watch?v=S4kd_ZG5DTQ |
| 2025-11-09 | 🚀Kimi K2 Thinking深度测评！支持Claude Code，能否平替Claude Sonnet 4.5？完整实测编程、写作、全栈开发能力！首个原生"Thinking Agent"究竟有多强 | Claude Code, Claude | https://www.youtube.com/watch?v=Nd3ZJz7Suq4 |
| 2025-10-17 | 🚀开发者福音！现有项目用AI迭代？OpenSpec规范驱动开发！让AI按规范写代码，真正做到零失误！支持Cursor、Claude Code、Codex！比SpecKit更强大！三分钟为iOS新增功能 | Claude Code, Claude, Codex/CodeX, Cursor, OpenSpec/Spec-driven | https://www.youtube.com/watch?v=ANjiJQQIBo0 |
| 2025-10-11 | 🚀神器降临！Claude Code插件功能正式上线，全球开发者共享最佳实践，一键安装最强工作流，效率爆表！ | Claude Code, Claude | https://www.youtube.com/watch?v=4rkgX8W6obk |
| 2025-10-06 | 程序员福利！GitHub最火的Spec Kit项目深度解析：只需7条命令就能实现规格驱动开发，告别繁琐的PRD文档，让规范直接生成代码！支持Claude Code！ | Claude Code, Claude | https://www.youtube.com/watch?v=PtIGaAPzCR0 |
| 2025-09-28 | 🚀保姆级教程！Chrome DevTools MCP横空出世：无需I配置大模型AP，一键让所有AI编程助手具备超强浏览器自动化能力，支持Cursor、Claude Code、Codex CLI等 | Claude Code, Claude, Codex/CodeX, Cursor, Chrome DevTools | https://www.youtube.com/watch?v=dlV5nbpCyR0 |
| 2025-09-26 | 🚀保姆级教程！GitHub Copilot CLI横空出世，支持MCP扩展+自动PR创建，让AI编程效率提升1000%，开发者必看！开发完整应用实战演示！支持GPT-5和Claude Sonnet 4 | Claude, GitHub Copilot | https://www.youtube.com/watch?v=x_uGDL5co2k |
| 2025-09-18 | 🚀Claude in Xcode超越Claude Code颠覆Apple移动端开发！三分钟实现原生开发iOS App！Claude Sonnet 4深度集成Xcode，实时代码生成+智能调试，效率倍增 | Claude Code, Claude | https://www.youtube.com/watch?v=x5LlLweitHc |
| 2025-09-16 | 🚀GPT‑5-Codex深度测评！支持Cursor！连续编程7小时不掉线，5分钟开发完整应用，彻底颠覆传统编程方式！终端命令行+IDE+云端三端通用！GitHub PR一键审查修复，效率暴涨1000% | Codex/CodeX, Cursor | https://www.youtube.com/watch?v=JHNdpjjrphA |
| 2025-09-02 | 🚀Claude Code PM 彻底颠覆传统编程开发！轻松实现并行开发！支持Spec-driven规范驱动开发！让GitHub Issues秒变独立分支的神器！开发效率提升300%！头脑风暴生成PRD | Claude Code, Claude, OpenSpec/Spec-driven | https://www.youtube.com/watch?v=5hmeTZdRt6Y |
| 2025-08-28 | 🚀颠覆Vibe Coding！超越Kiro！支持Cursor！Claude Code Spec Workflow为Claude Code完美复现Kiro的Spec-Driven规范驱动开发！效率倍增！ | Claude Code, Claude, Cursor, OpenSpec/Spec-driven | https://www.youtube.com/watch?v=ruAy8oBR5lA |
| 2025-08-16 | 🚀突破性创新！Claude Code新增Output Styles功能彻底颠覆编程方式，实现Claude Code与Gemini CLI双AI协作，代码质量倍增！Learning模式支持编写代码边学习 | Claude Code, Claude, Gemini CLI, Gemini | https://www.youtube.com/watch?v=bRcuzPiX2iQ |
| 2025-08-08 | 🚀Cursor CLI+GPT-5保姆级教程+编程能力测评！Cursor CLI零成本免费使用GPT-5！Claude Code的劲敌来了！从安装到实战演示，轻松开发AI智能体，颠覆传统开发效率翻倍！ | Claude Code, Claude, Cursor | https://www.youtube.com/watch?v=KE1gD-02BUk |
| 2025-07-29 | 🚀彻底颠覆传统开发！Claude Code再添利器！BMad-Method多智能体协作框架轻松打造敏捷AI驱动开发工作流！自动生成PRD文档、架构设计！支持Cursor、Cline、windsurf等 | Claude Code, Claude, Cursor, Cline, Windsurf | https://www.youtube.com/watch?v=ak9kOecZGRc |
| 2025-07-25 | 🚀Claude Code重磅推出Sub agents功能！轻松实现任务专业化和模块化！三分钟完美复现Kiro工作流，规范驱动开发时代正式到来！从Vibe Coding到spec-driven软件开发！ | Claude Code, Claude, OpenSpec/Spec-driven | https://www.youtube.com/watch?v=GjlkRcNNONo |
| 2025-07-15 | 🚀彻底改写Claude Code编程方式！从提示词工程到上下文工程！AI编程能力提升百倍！从需求分析到代码生成全自动化！保姆级实战教程！支持Windows！零基础用Claude Code开发AI智能体 | Claude Code, Claude | https://www.youtube.com/watch?v=oEZ7aN7jOEI |
| 2025-07-10 | 🚀当Cursor和Claude code拥有了记忆！编程能力倍增！Graphiti MCP Server让AI编程助手实现持久超强记忆！时序知识图谱让你的代码规范、Bug修复历史永久保存，开发效率倍增 | Claude Code, Claude, Cursor, MCP, Graphiti | https://www.youtube.com/watch?v=oQmJR7G0QlU |
| 2025-07-05 | 🚀 SuperClaude让Claude Code编程能力暴增300%！小白秒变顶尖程序员！19个专业命令+9大预定义角色，零编程经验也能开发复杂项目，完全碾压Cursor等AI编程工具！颠覆传统编程 | Claude Code, Claude, Cursor | https://www.youtube.com/watch?v=bMO13RNjvBk |
| 2025-07-02 | 🚀Claudia让你丢掉Cursor告别命令行！Claude Code终于有GUI了！专为Claude Code打造最强可视化界面保姆级教程！可视化项目管理、智能体创建、记忆文件配置，AI编程如此简单 | Claude Code, Claude, Cursor | https://www.youtube.com/watch?v=WIwW7V56wxE |
| 2025-06-26 | 🚀保姆级教程！Google震撼发布Gemini CLI！100万TOKEN超长上下文远超Claude Code，支持MCP Server扩展，开发者的终极AI！Context7+Task Master | Claude Code, Claude, Gemini CLI, Gemini, Task Master/Context7 | https://www.youtube.com/watch?v=v41xKxZmygU |
| 2025-06-21 | 🚀Cursor+Serena最佳组合告别AI编程工具短板！支持Claude Code、windsurf、Cline！让AI编程不再是简单读取代码而是智能分析依赖关系，让复杂开源项目二次开发效率提升十倍 | Claude Code, Claude, Cursor, Cline, Windsurf, Serena | https://www.youtube.com/watch?v=DZ-gLebVnmg |
| 2025-06-15 | 🚀告别Cursor的限制！Augment编程神器震撼登场：200K超长上下文+全自动代码生成，结合Context7轻松开发游戏！支持万行代码分析+自动bug修复+跨文件依赖识别，三分钟自动开发复杂项目 | Cursor, Task Master/Context7 | https://www.youtube.com/watch?v=DbM3QZy5I6E |
| 2025-06-13 | 🚀颠覆传统编程！Claude Code+Zen MCP实现多AI协作开发！效率提升20倍！Claude+Gemini 2.5+O3打造专业编程开发团队自动调用最适合的AI进行编码，开发效率提升20倍！ | Claude Code, Claude, Gemini | https://www.youtube.com/watch?v=2WgICfNzgZY |
| 2025-06-02 | 🚀Kilo Code横空出世：完美融合Cline和Roo Code所有优势，彻底解决卡死bug，支持5种智能模式，20美金免费额度，自动触发上下文压缩、智能任务分解、实时代码解释，编程效率提升300% | Cline | https://www.youtube.com/watch?v=sUCsitU7hmE |
| 2025-05-26 | Cursor+Claude Code+Claude 4终极组合！仅用10分钟为开源项目Magentic-UI完美集成JWT用户认证系统，编程效率提升300%，告别传统开发模式！小白也能轻松开发商业项目 | Claude Code, Claude, Cursor | https://www.youtube.com/watch?v=SK9JBDyHqiI |
| 2025-05-21 | 🚀谷歌Jules彻底颠覆传统AI编程！超越OpenAI Codex和Manus与Coze！Jules深度实测，完美GitHub集成，自动代码分析与重构，从复杂项目到功能增强一步到位，小白也能轻松编程 | Codex/CodeX | https://www.youtube.com/watch?v=_OGUP_geTsA |
| 2025-05-19 | 🚀Windsurf研发SWE-1大模型编程能力超越DeepSeek V3！开发者福音！SWE-1系列模型独家评测：不限次数免费使用，从项目分析到MCP服务器开发的全流程实战教程，让小白也能轻松开发软件 | Windsurf | https://www.youtube.com/watch?v=-rHM4TbfdGA |
| 2025-04-26 | 🚀AutoGen重大更新！新增McpWorkbench完美支持MCP Server！支持将Agent和Team封装为工具！开启模块化智能体编程！实战教程：从零开始构建旅游规划智能体和进销存智能客服系统 |  | https://www.youtube.com/watch?v=1ZxzPpa5Ysc |
| 2025-04-25 | 🔥超越cursor！Cline+Context7 MCP文档搜索功能高级用法！自定义指令+.clinerules轻松开启vibe coding！零代码构建AutoGen智能体与Next.js应用 | Cursor, Cline, Task Master/Context7 | https://www.youtube.com/watch?v=HdYT915bcfY |
| 2025-04-17 | 🚀OpenAI首发轻量级AI编程智能体-OpenAI Codex CLI，编程能力能否超越cursor？Codex编程智能体实战，打破编程瓶颈，自动化开发，轻松构建3D城市模拟与任务管理系统的实战教程 | Codex/CodeX, Cursor | https://www.youtube.com/watch?v=Qcyycy4aYgY |
| 2025-04-15 | 🚀多维度测评OpenAI最新GPT-4.1模型！百万token上下文窗口！编程能力和指令遵循能力大幅提升！Cline+GPT-4.1十分钟零代码开发macOS原生应用！只消耗0.5刀！更低成本更强效果 | Cline | https://www.youtube.com/watch?v=W2YnjNhbiUM |
| 2025-04-10 | 🚀颠覆传统智能体！ADK谷歌最强AI智能体发布！支持MCP与ollama！Agent Development Kit详细教程！超越AutoGen和LangChain!轻松打造多智能体系统！自带UI界面 |  | https://www.youtube.com/watch?v=z7aGIvVyo_I |
| 2025-04-03 | 🚀颠覆MCP！Open WebUI新技术mcpo横空出世！支持ollama！轻松支持各种MCP Server！Cline+Claude3.7轻松开发论文检索MCP Server！3分钟本地部署mcpo | Claude, Cline | https://www.youtube.com/watch?v=AAiG_j4Lx4c |
| 2025-03-31 | 🚀超越cursor！Roo Code+Gemini 2.5 Pro为OpenAI Agents SDK开发工作流UI！轻松拖动组件即可搭建工作流！小白也能化身软件工程师！超越dify和langflow | Gemini, Cursor | https://www.youtube.com/watch?v=KQULGx6wjco |
| 2025-03-25 | 🚀DeepSeek 6850亿参数开源大模型！DeepSeek-V3-0324全方位测评！编程能力、文档分析、复杂推理能力、Text-to-SQL能力！Cline+DeepSeek轻松开发城市模拟游戏 | Cline | https://www.youtube.com/watch?v=28x0s0rv-mw |
| 2025-03-23 | 🚀Cursor降低智商！WindSurf零代码开发MCP Server！五分钟轻松实现LightRAG+MCP为Claude和AutoGen挂载知识库！增强Claude和AutoGen的知识库检索能力 | Claude, Cursor, Windsurf | https://www.youtube.com/watch?v=KGZ_zM6Xi-U |
| 2025-03-16 | 实战详解MCP，从入门到开发！小白也能看懂！MCP推动AI智能体大爆发！Cline+Claude3.7打造论文搜索MCP Server！集成到AutoGen+smolagents智能体框架！AGI到来 | Claude, Cline | https://www.youtube.com/watch?v=vYm0brFoMwA |
| 2025-03-08 | 3分钟复刻Manus智能体！AutoGen+MCP Server+Cline构建最强AI智能体，支持ollama！轻松实现网络搜索+文件操作的AI Agent！不花一分钱也能拥有强大AI智能体！#ai | Cline, MCP | https://www.youtube.com/watch?v=szTXELuaJos |
| 2025-02-22 | 🚀用MCP为AutoGen开挂接入各种工具和框架！Cline零代码开发MCP Server实现接入LangFlow进行文档问答！利用MCP Server突破平台限制，从环境配置到功能实现，让AI更智能 | Cline | https://www.youtube.com/watch?v=RxR3x_Uyq4c |
| 2025-02-05 | 取代ChatGPT Operator！支持DeepSeek+Web UI！Browser Use最强AI驱动的浏览器自动化框架，支持Roo Code轻松实现MCP Server集成到Claude桌面版 | Claude | https://www.youtube.com/watch?v=jsd8TpzicRQ |
| 2025-01-29 | 阿里千问系列最强大模型-Qwen2.5-Max震撼发布！在线测评+API调用！Cline编程+AutoGen智能体！轻松实现任务计划AI Agents！官方基准测试得分超越DeepSeek v3！ | Cline | https://www.youtube.com/watch?v=vLVV6_Wiyps |
| 2025-01-08 | 告别Token消耗！用Roo Cline开发项目专属MCP Server，让AI编程不再烧钱，Claude app化身编程IDE，一次配置永久省钱！最强编程AI智能体！Roo Cline超越Cline | Claude, Cline | https://www.youtube.com/watch?v=kFwE4hHbkT0 |
| 2025-01-07 | 告别Cursor和WindSurf！最强AI编程插件Cline3.1重磅升级：智能版本管理+任务跟踪系统，让你的代码管理更高效，一键修复Bug，从项目分析到代码优化，打造完美跨平台应用的终极指南 | Cursor, Cline, Windsurf | https://www.youtube.com/watch?v=Sag2p28WYnQ |
| 2024-12-14 | 超越Windsurf+Cursor！重磅更新！Cline+Gemini 2.0轻松实现零代码开发MCP Server！打造最强Claude AI Agent！LangFlow为Claude实现RAG！ | Claude, Gemini, Cursor, Cline, Windsurf | https://www.youtube.com/watch?v=7BFMY0yuRAY |
| 2024-12-08 | Llama-3.3-70B震撼登场！70b参数128k上下文性能接近gpt4！最强开源大模型，支持简体中文和繁体中文！Cline+Aider实现全自动编程！AutoGen实现最强AI智能体！#llm | Cline | https://www.youtube.com/watch?v=MRRFyl5d958 |
| 2024-11-26 | Claude颠覆性创新！MCP模型上下文协议！轻松为Claude加入搜索引擎、网页抓取、Text to SQL、文件管理、GitHub操作等功能！Model Context Protocol为AI开挂 | Claude | https://www.youtube.com/watch?v=KbgDABTSV9I |
| 2024-11-13 | 最强开源编程大模型Qwen2.5-coder-32B-instruct！部署安装Bolt.new和Cline+Qwen2.5-coder多维度测试，能否达到Claude3.5-sonnet的编程能力？ | Claude, Cline | https://www.youtube.com/watch?v=RtBL5dNw1NY |
| 2024-11-10 | 超越Cursor颠覆传统编程！最强编程AI智能体框架OpenHands全方位测评实现零代码编程开发！支持ollama支持xAI的Grok模型！支持代码优化、项目分析、自动化测试，轻松构建完整应用 | Cursor | https://www.youtube.com/watch?v=Wd_PIbtbH3Q |
| 2024-10-24 | Claude-3.5-sonnet new+Cline+Continue打造最强编程智能体！玩转全自动编程,开发各种复杂应用，轻松修改代码、优化代码、添加注,小白也能开发各种app！#claude | Claude, Cline | https://www.youtube.com/watch?v=TsTR-b-ZCQo |
| 2024-10-11 | 最强编程AI智能体Claude Dev重大更新，改名为Cline！支持通过手稿生成UI，从零打造模仿ChatGPT的chatbot！人人都是全栈工程师！Cline+VS Code实现零代码编程开发 | Claude, Cline | https://www.youtube.com/watch?v=7Y8Q5IcOey8 |
| 2024-09-05 | 颠覆传统编程，超越Cursor！Claude Dev最强编程AI智能体！支持ollama和GitHub models！一条prompt实现全自动游戏开发！#cursor #aiagents #aigc | Claude, Cursor | https://www.youtube.com/watch?v=n18L9VFhNDo |
| 2024-08-09 | 零代码开发app！Claude Dev全自动写代码开发聊天机器人！超越Copilot！小白也能三分钟开发游戏！最强编程AI智能体! #claude3 #aiagents #aiprogramming | Claude, GitHub Copilot | https://www.youtube.com/watch?v=Us6LQzKmgfs |
