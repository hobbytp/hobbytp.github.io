
# BMAD-METHOD 和 Claude Skills 的结合

**BMAD-METHOD**（Breakthrough Method for Agile AI-Driven Development）是一种革命性的 AI 驱动敏捷开发框架，旨在通过模拟敏捷团队角色（如分析师、产品经理、架构师、开发者和测试者）来结构化软件开发过程。它使用 Markdown 文件定义 AI 代理，每个代理有特定的角色、个性（persona）和命令，支持从需求分析到代码实现的完整工作流。BMAD 强调迭代式开发、任务分解和跨代理协作，通常与大型语言模型（如 Claude）集成，以实现高效的“敏捷 AI 驱动开发”。

**Claude Skills** 是 Anthropic 的 Claude AI 的一项功能，它允许用户创建包含指令、脚本和资源的文件夹，这些资源可以动态加载以提升 Claude 在特定任务上的表现。例如，Skills 可以用于处理 Excel、遵循品牌指南或执行代码任务。Skills 是可组合的（可以堆叠使用）、可移植的（跨 Claude 应用、Claude Code 和 API 使用），并且高效（仅加载必要内容）。Claude 会根据任务自动扫描和激活相关 Skills。

## 为什么结合它们？

BMAD-METHOD 的核心是**代理协作和结构化工作流**，而 Claude Skills 提供了完美的实现机制：Skills 可以封装 BMAD 的每个代理角色（如 BMAD Master、Business Analyst、Developer），使其成为可重用、可扩展的模块。这种结合可以将 Claude Code 转变为一个完整的 BMAD 驱动开发环境，支持自动检测、内存集成和斜杠命令（slash commands），从而减少令牌消耗（token usage）70-85%，并适应从简单 bug 修复到企业级系统的项目复杂度。 这比单纯的“氛围编码”（Vibe Coding）更高效，避免了资源浪费，并将人类专业知识转化为 AI 可访问的格式。

### 如何结合使用（基于实际实现示例）

一个典型结合方式是通过 GitHub 仓库如 aj-geddes/claude-code-bmad-skills 来实现 BMAD Method v6 与 Claude Skills 的集成。 以下是步骤指南：

1. **安装 BMAD-METHOD 和 Skills**:
   - 确保你有 Claude Pro/Max/Team/Enterprise 订阅，并启用 Skills 功能（在 Claude 设置中）。
   - 克隆仓库：在终端运行：

     ```
     git clone https://github.com/aj-geddes/claude-code-bmad-skills.git
     ```

   - 自动安装（推荐）：在 Claude Code 中输入命令 `"Please install BMAD Method v6 from this repository"`，Claude 会自动检测平台并安装。
   - 手动安装（Linux/macOS/WSL）：

     ```
     cd claude-code-bmad-skills
     chmod +x install-v6.sh && ./install-v6.sh
     ```

     （Windows 使用 PowerShell 脚本 `.\install-v6.ps1`。）
   - 验证：检查 `~/.claude/skills/bmad/core/bmad-master/SKILL.md` 文件是否存在。

   安装成功后，它会在Claude Code 中显示如下信息：

```
● ✅ BMAD Method v6 Installation Complete!

  Installation Summary

  Successfully installed BMAD Method v6 with the following components:

  🎯 Core Installation

- BMad Master Skill (Core orchestrator) ✅
- 6 BMAD Method Management (BMM) Skills ✅
- 1 Builder Module (BMB) Skill ✅
- 1 Creative Intelligence (CIS) Skill ✅
- Total: 9 Specialized Skills ✅

  📁 Installation Location

- Skills: C:\Users\RayTan\.claude\skills\bmad\
- Configuration: C:\Users\RayTan\.claude\config\bmad\
- Utility Helpers: C:\Users\RayTan\.claude\config\bmad\helpers.md

  🚀 Next Steps

  1. Restart Claude Code - Skills load on startup
  2. Open your project directory in Claude Code
  3. Initialize BMAD: Run /workflow-init
  4. Check status: Run /workflow-status

  💡 Available Commands After Restart

- /workflow-init - Initialize BMAD structure
- /workflow-status - Check project status and get recommendations
- /product-brief - Phase 1: Product discovery
- /prd - Phase 2: Detailed requirements
- /tech-spec - Phase 2: Lightweight requirements
- /architecture - Phase 3: System design
- /sprint-planning - Phase 4: Sprint planning
- /dev-story - Phase 4: Story implementation
```

2. **初始化 BMAD**:
   按照上面的指示，执行下面的步骤：
   1. 进入目标项目目录。
   2. 运行claude code。
   3. 运行 `/workflow-init` 来初始化 BMAD 结构。
   4. 运行 `/workflow-status` 来查看进度和建议。

3. **创建和配置 Skills**:
   - 使用 Claude 的“skill-creator” Skill 来构建 BMAD 代理。例如，创建一个文件夹作为 Skill，包含：
     - `SKILL.md`：定义角色（如 “You are the Business Analyst”）、指令和命令。
     - YAML 配置：指定代理名称、依赖和激活逻辑。
     - 辅助文件：如 `helpers.md` 用于可重用代码段，以优化 token 使用。
   - BMAD 提供 9 个核心 Skills（如 BMad Master、Developer、UX Designer），对应 BMAD 的 8 个阶段（Analysis, Planning, Solutioning, Implementation, Builder, Creative Intelligence, UX/Advanced）。

4. **运行结合工作流**:
   - 在 Claude Code 中打开项目目录。
   - 初始化：运行 `/workflow-init` 设置 BMAD 结构（创建 `bmad-outputs/` 文件夹用于文档和内存）。
   - 执行阶段命令：
     - 分析阶段：`/product-brief` 或 `/prd` 生成产品需求文档（PRD）。
     - 规划阶段：`/sprint-planning` 或 `/create-story` 分解任务。
     - 解决方案阶段：`/architecture` 设计架构，`/solutioning-gate-check` 检查。
     - 实施阶段：`/dev-story` 开发用户故事。
     - 创意/UX：`/brainstorm`（支持 8 种 brainstorm 技术）或 `/create-ux-design`。
   - 监控：`/workflow-status` 查看进度和建议。
   - 扩展：使用 `/create-agent` 添加自定义代理（如 QA Engineer），或 `/create-workflow` 定义新工作流。

5. **高级集成**:
   - **内存和文件**：BMAD 使用 YAML 跟踪状态，Claude Skills 动态加载文件，确保上下文持久。
   - **多代理协作**：BMAD Orchestrator（主代理）协调 Skills，如 Analyst 生成简报后 handover 给 PM。
   - **API 支持**：在 Claude API 中，通过 `/v1/skills` 端点添加 BMAD Skills，支持代码执行工具。
   - **兼容工具**：支持 Cursor、Cline 等 IDE，自动生成 PRD、架构设计。

#### 好处和注意事项

- **好处**：这种结合使开发更敏捷、token 高效，并支持跨平台（Windows/Linux/macOS）。它将 Claude 从通用 AI 转变为专属软件工程师，提升输出质量。
- **注意**：Skills 涉及代码执行，使用可信来源。项目复杂度自动适应（Level 0-4），但大型项目可能需手动调整。未来更新可能包括更简单的创建流程。

如果你有具体项目需求或需要代码示例，我可以进一步指导！
