---
title: OpenAI Codex
date: "2025-11-30T09:10:00+08:00"
draft: false
tags: ["OpenAI", "Codex", "Rust"]
categories: ["ai_programming"]
description: "Codex是OpenAI发布的一个轻量级编码代理工具，可以在终端本地运行，同时支持与ChatGPT账户或API密钥集成。项目主要由**Rust**开发,支持MCP服务器、非交互模式、沙盒及审批规则等功能，还支持TypeScript SDK和GitHub Action等扩展使用方式。"
---

## TR;DR

Codex是OpenAI发布的一个轻量级编码代理工具，可以在终端本地运行，同时支持与ChatGPT账户或API密钥集成。它可以通过npm或Homebrew进行全局安装，并提供丰富的配置选项（如`~/.codex/config.toml`）。Codex支持MCP服务器、非交互模式、沙盒及审批规则等功能，还支持TypeScript SDK和GitHub Action等扩展使用方式。项目主要由**Rust**开发，占比96.7%。本项目基于Apache-2.0开源协议。

## CodeX主要功能

Codex 的核心思想是将编程语言视为一种特殊的自然语言，并利用强大的语言模型技术来理解和生成它。
基于 GPT-5 的最强 AI 编程代理，可自主完成从需求到代码、测试、PR 的完整开发任务，而不仅是代码补全。

**核心亮点**  
- 真正“代理”：能独立思考、规划、连续跑几小时任务。
- 并行多任务：一次开几十个代理同时干活  
- 37% 复杂任务一次成功，迭代后接近 80%  
- 支持 Python/JS/Go/Rust 等主流语言，集成 VS Code、CLI、GitHub  

**主要竞争对手**  
- GitHub Copilot（实时补全王者）  
- Claude Code（推理最强，开源社区扩展最大最强，演进最快）  
- Cursor（最丝滑全AI IDE）  
- Gemini CLI （白嫖之王）
- Devin（最“全能”但贵）  
- Amazon Q / Gemini Code Assist（企业级）  
- Codeium / Qwen Code（免费平替）
- ...

**业界评价**  
正面：生产力暴增、“7小时不喝咖啡的队友”  
负面：贵（高强度用一天几十美元）、有幻觉、代码需人工审、隐私争议  
综合评分：4.5/5，大厂/中大型团队爱用，个人/小厂常选 Cursor 或 Copilot

**未来趋势**  
2026 年预计：  
- 更便宜 API 开放  
- 实时纠错 + 多模态输入（截图→代码）  
- 与 CI/CD、Jira 全打通  
目标：让程序员只提需求和做最终审查，80% 代码由 AI 写

一句话：Codex 正在把“AI 写代码”从辅助工具升级为“可托付的远程程序员”。



## CodeX开源技术探究

可以访问https://zread.ai/openai/ 获取最新代码库的解说信息。

## CodeX 配置不同LLM

### CodeX 配置GLM4.6

配置 Codex 使用 GLM-4.6 模型，主要有两种主流且已验证可行的方法。你可以根据自己的情况选择以下任一方案。

| 配置方式 | 核心特点 | 适用场景 |
| :--- | :--- | :--- |
| **方式一：通过智谱官方平台** | 直接、稳定，需订阅GLM Coding套餐。 | 追求最佳兼容性和稳定性，愿意支付月费以获得官方服务和支持。 |
| **方式二：通过魔搭（ModelScope）社区** | 可免费试用，依赖魔搭平台的免费额度。 | 希望先免费体验，或已有魔搭社区账户的用户。 |

下面是每种方式详细的配置步骤。

### 💡 方式一：通过智谱AI官方平台配置

这是最直接的方式，能获得较好的体验。以下是具体步骤,也可参考[官方文档](https://docs.bigmodel.cn/cn/coding-plan/tool/others)

1.  **获取GLM-4.6 API Key**
    *   访问**智谱AI开放平台**（bigmodel.cn），注册并登录账号。
    *   在平台中订阅 **GLM Coding Plan** 套餐（例如20元/月的Lite版即可体验），之后在用户中心创建并复制你的API Key。请务必妥善保存此Key，因为它通常只显示一次。

2.  **设置环境变量**
    *   将上一步获取的API Key设置为系统的环境变量，变量名建议为 `GLM_API_KEY`。
    *   **Windows系统**：在命令提示符（CMD）中执行 `setx GLM_API_KEY "你的API Key"`，然后重启终端。
    *   **macOS/Ubuntu系统**：将 `export GLM_API_KEY="你的API Key"` 这行命令添加到 `~/.zshrc` 或 `~/.bashrc` 文件末尾，然后运行 `source ~/.zshrc` 使配置生效。

3.  **修改Codex配置文件**
    *   找到Codex的配置文件，通常位于 `~/.codex/config.toml`（Windows系统在 `C:\Users\你的用户名\.codex\config.toml`）。
    *   用文本编辑器打开该文件，并写入以下配置内容：
    ```toml
    # 指定默认使用的模型提供商和模型
    model_provider = "glm"
    model = "glm-4.6"

    # 定义名为"glm"的模型提供商
    [model_providers.glm]
    name = "zai"  # 在Codex界面中显示的名称
    base_url = "https://open.bigmodel.cn/api/coding/paas/v4"  # GLM Coding套餐专用接口
    env_key = "GLM_API_KEY"  # 对应之前设置的环境变量名
    ```

完成以上步骤后，重新启动Codex，它就会使用GLM-4.6模型为你服务了。

### 🔧 方式二：通过魔搭（ModelScope）社区配置

如果你希望先免费体验，可以通过魔搭社区接入。

1.  **获取魔搭API Key**
    *   访问**魔搭社区（modelscope.cn）**，注册并登录账号。
    *   进入账号设置，在“访问令牌” section 创建一个新的API Key。魔搭社区为新用户提供一定的免费调用额度。

2.  **设置环境变量**
    *   将复制的API Key设置为环境变量，变量名建议为 `MODELSCOPE_API_KEY`。设置方法同方式一的步骤2。

3.  **修改Codex配置文件**
    *   打开Codex的配置文件 `config.toml`，写入以下配置：
    ```toml
    model_provider = "modelscope"
    model = "ZhipuAI/GLM-4.6"

    [model_providers.modelscope]
    name = "modelscope"
    base_url = "https://api-inference.modelscope.cn/v1"  # 魔搭社区的API地址
    env_key = "MODELSCOPE_API_KEY"  # 对应设置的环境变量名
    ```

配置完成后，同样需要重启Codex。

### ⚠️ 注意事项与技巧

*   **验证配置**：启动Codex后，你可以通过输入 `/status` 命令或直接询问模型“你是谁？”来确认当前使用的模型是否为GLM-4.6。注意它会回“我是CodeX”，但是只要回复了，就说明大模型配置成功。
*   **文件修改工具**：有用户反馈，使用自定义模型时，Codex可能倾向于使用效率较低的Shell工具来修改文件。如果遇到此问题，可以在对话中明确指示它使用自带的 `apply_patch` 工具，这通常更可靠。
*   **速率限制**：如果通过魔搭社区等平台使用，请注意免费额度通常有速率限制（RPM），高频调用可能被限制。付费套餐通常会有更宽松的限制和更稳定的服务。

希望这份详细的指南能帮助你顺利完成配置！如果你在某个具体步骤遇到问题，可以告诉我你的操作系统和遇到的错误提示，我可以提供更具体的帮助。

##  参考

* [CodeX 官方Developer Doc](https://developers.openai.com/codex)
* [Codex](http://openai.com/codex)
* [Codex Github](https://github.com/openai/codex)]
* [GLM4.6 集成其他AI IDE](https://docs.bigmodel.cn/cn/coding-plan/tool/others)
