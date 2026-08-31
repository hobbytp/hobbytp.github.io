


## github copilot - creat-agent

`/create-agent` 是 VS Code 里 GitHub Copilot 的一个快捷命令，用来在 **Agent mode** 里生成可复用的自定义 agent，而不是直接执行一次性任务。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
你只要描述想要的角色，例如“安全审查 agent”或“架构规划 agent”，Copilot 会继续追问细节，然后帮你产出一个 `.agent.md` 文件。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

### 使用步骤

1. 先打开 VS Code 的 GitHub Copilot Chat，并切到 **Agent mode**，因为 `/create-agent` 是在 Agent mode chat 中使用的命令。 [code.visualstudio](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)
2. 在输入框里键入 `/create-agent`，后面接你希望的角色描述，例如“一个只做只读分析的系统设计 agent”。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
3. Copilot 会提出澄清问题，随后自动生成带有 frontmatter 和说明文本的 `.agent.md` 文件，你保存后就能在 agents 下拉列表里直接切换使用它。 [docs.github](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)

### 生成内容

这个 `.agent.md` 文件本质上是一个自定义 agent 配置，通常会包含 `name`、`description`、`tools`、`model`、`target` 等字段，以及正文里的行为说明。 [docs.github](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
如果你把它建在工作区里，默认会放到 `.github/agents` 目录；如果建在用户级别，就可以跨多个工作区复用。 [docs.github](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
之后你还可以继续手改这个文件，或者在 VS Code 里用 **Configure Tools...** 来调整它能用哪些工具、是否指定模型。 [docs.github](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)

### 适合怎么用

这个功能特别适合把你常做的工作流固化下来，比如“代码安全审查”“方案规划”“测试生成”“只读排障分析”这类角色。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
VS Code 官方文档给的例子就是：你可以输入“a security review agent”，让系统生成一个带合适工具和指令的专用 agent。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
如果你刚做完一段多轮对话，也可以让 Copilot“把这类任务做成一个 agent”，把当前工作流沉淀成可复用配置。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

### 实战建议

如果你的目标是“先分析再实施”，建议把 agent 的 `tools` 限制成只读工具，这样更安全，也更容易让规划类输出保持稳定。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
等你确认方案后，再切到另一个允许编辑代码的 agent，这也是 VS Code 自定义 agents 设计出来的典型用法。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
另外，这套功能本质上就是以前的 custom chat modes 演进而来，所以如果你见过旧的 `.chatmode.md`，现在对应的是 `.agent.md`。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

一个最实用的中文提示词示例是：`/create-agent 帮我创建一个“AI系统架构师”agent，擅长需求拆解、模块边界设计、接口定义、技术选型，只读分析优先，除非我明确要求否则不要改代码。` 这种描述方式更容易让它生成符合你工作习惯的 agent 配置。 [code.visualstudio](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
要不要我接着给你写一个适合“AI 软件/系统架构设计”的 `architect.agent.md` 模板？



## 

npm install -g @githubnext/github-copilot-cli

copilot auth login

