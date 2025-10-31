+++
title = "Cursor AI 最佳实践：提升编码效率与代码质量的权威指南"
date = "2025-04-12T21:10:00+08:00"
lastmod = "2025-05-16T22:10:00+08:00"
draft = false
tags = ["Cursor", "AI", "论文", "技术"]
categories = ["ai_programming"]
description = "Cursor AI 最佳实践：提升编码效率与代码质量的权威指南"
+++

# **Cursor AI 最佳实践：提升编码效率与代码质量的权威指南**

## **I. 引言**

Cursor 是一款以人工智能（AI）为核心、旨在显著提升开发者生产力的代码编辑器 1。它基于流行的 Visual Studio Code (VS Code) 构建，继承了其熟悉的用户界面和广泛的扩展生态系统，同时深度集成了先进的 AI 功能，以重新构想代码编写、理解、调试和协作的方式 1。本报告旨在全面梳理和分析 Cursor 的核心功能、设计理念、推荐工作流程以及社区分享的最佳实践，为开发者提供一份权威指南，以充分利用 Cursor 提升编码效率和代码质量。我们将深入探讨其各项 AI 功能，包括代码补全、自然语言交互、代码生成与编辑、调试辅助、文档处理等，并结合不同编程语言、框架和开发场景，提供具体的最佳实践建议。此外，报告还将分析 Cursor 与其他主流 AI 编码助手的异同，明确其独特的优势和最佳应用场景。

## **II. 核心概念与设计哲学**

Cursor 的核心设计理念在于将 AI 无缝融入开发者的日常工作流，使其成为一个智能的“结对编程伙伴” 2。它不仅仅是在现有编辑器上叠加 AI 功能，而是从底层架构上就以 AI 为先进行设计 6。

* **基于 VS Code 的熟悉感与扩展性：** Cursor 选择基于 VS Code 进行构建，这是一个明智的决策。这使得数百万熟悉 VS Code 的开发者能够以极低的门槛迁移过来，并能一键导入现有的扩展、主题和快捷键设置 1。这种熟悉感降低了学习曲线，让开发者可以快速上手并专注于利用 AI 功能 3。然而，这也意味着 Cursor 可能继承了 VS Code 在某些特定领域的局限性，例如对某些非官方支持的调试器（如.NET C\# 调试器）的兼容性问题 10。这种权衡使得 Cursor 在提供强大 AI 能力的同时，也需要用户了解其底层平台的特性。  
* **深度 AI 集成：** 与许多将 AI 作为插件添加的工具不同，Cursor 将 AI 能力深度集成到编辑器的每一个环节 7。从智能的代码补全（Tab）、到基于自然语言的交互式编辑（Chat、⌘K）、再到能够执行复杂任务的 Agent 模式，AI 不再是辅助，而是核心驱动力 1。这种深度集成旨在创造一种更流畅、更智能的编码体验，让开发者感觉 AI 真正理解他们的代码和意图 5。  
* **情境感知与代码库理解：** Cursor 的一个关键优势在于其理解整个代码库上下文的能力 2。它不仅仅分析当前文件，还会自动索引整个项目，理解文件结构、依赖关系和编码风格 5。这种全局视野使得 AI 能够提供更相关、更准确的建议和代码生成，尤其是在进行跨文件重构或理解复杂项目时 13。  
* **从“编写者”到“指导者”的转变：** Cursor 的设计哲学鼓励开发者转变角色，从代码的直接编写者，更多地转变为 AI 的指导者和代码的审查者 17。开发者通过自然语言描述需求、提供上下文、设置规则来引导 AI 完成任务，然后审查、修改和确认 AI 生成的结果 17。这种转变旨在将开发者从繁琐的细节中解放出来，专注于更高层次的架构设计和问题解决 18。然而，这也对开发者的指导能力和审查能力提出了新的要求，需要开发者清晰地表达意图并具备辨别 AI 输出质量的能力 19。一些事件甚至表明，Cursor 的 AI 会在生成大量代码后拒绝继续，要求用户自行理解和开发逻辑，这反映了其设计中可能包含的防止过度依赖、鼓励学习的哲学考量 21。

## **III. 快速上手**

开始使用 Cursor 非常简单直接，特别是对于已经熟悉 VS Code 的开发者。

* **下载与安装：** 访问 Cursor 官方网站（cursor.com）的下载页面 22，根据你的操作系统（macOS、Windows、Linux）选择并下载对应的最新版本安装包。安装过程与标准应用程序类似 1。Cursor 提供通用二进制文件（Universal）以及针对特定架构（如 Arm64, x64）的版本 22。  
* **初始设置：** 首次启动 Cursor 时，会有一个简单的配置向导 3。  
  * **键盘快捷键：** 你可以选择沿用 VS Code 的快捷键，或者选择其他编辑器的键位映射（如 Vim）3。对于 VS Code 用户，保留默认设置可以实现无缝过渡。  
  * **AI 交互语言：** 可以选择使用非英语语言与 AI 进行交互 3。  
  * **代码库范围索引：** 建议启用此选项，允许 AI 理解整个代码库的上下文，这是 Cursor 发挥其强大功能的关键 3。  
* **导入 VS Code 设置：** Cursor 提供了一键导入 VS Code 扩展、设置、主题和快捷键的功能 1。这极大地简化了迁移过程，让开发者可以立即在熟悉的环境中工作。  
* **免费试用与定价：** Cursor 提供免费的 Hobby 计划，包含 Pro 计划的两周试用期，无需信用卡 1。免费计划包含有限次数的代码补全和高级模型（如 GPT-4o, Claude 3.5 Sonnet）的慢速请求 24。Pro 计划（$20/月）提供无限补全、更多快速高级请求和无限慢速高级请求 24。Business 计划（$40/用户/月）则增加了团队管理、SSO 和强制隐私模式等功能 24。

## **IV. 核心 AI 功能详解**

Cursor 提供了一系列紧密集成的 AI 功能，旨在覆盖开发工作流的各个方面。

* **A. Tab 智能代码补全：**  
  * **超越传统自动补全：** Cursor 的 Tab 功能远超传统的基于语法的自动补全 5。它由先进的 AI 模型驱动，能够理解代码上下文、开发者意图甚至最近的编辑历史 1。  
  * **多行与块级建议：** 它不仅能补全当前行，还能预测并建议多行代码甚至整个函数或类的实现 1。用户反馈其建议有时“如同魔法”般精准 2。  
  * **智能重写与错误修复：** Tab 具备“智能重写”能力，可以自动修正开发者输入时的拼写错误、语法错误或不规范写法 5。这使得开发者可以更流畅地编写代码，减少因小错误中断思路的情况 1。  
  * **上下文感知与风格适应：** Tab 会学习用户的编码风格和项目中的常见模式，提供更贴合的建议 6。它还能自动处理导入（例如在 TS/Python 中）26。  
  * **光标预测：** 该功能还能预测开发者下一步可能想要编辑的位置，优化代码导航 5。  
* **B. Chat 交互式 AI 助手 (⌘L / Ctrl+L)：**  
  * **自然语言界面：** Chat 提供了一个位于侧边栏的自然语言交互界面，允许开发者通过对话方式探索、理解、编辑和管理代码 6。  
  * **核心能力：** 包括理解代码（提问、解释）、编辑代码（小调整到多文件修改）、运行命令（建议终端命令）以及执行复杂操作（通过 Agent 模式）15。  
  * **模式切换：** Chat 提供多种模式以适应不同任务 6：  
    * **Agent 模式（默认）：** 赋予 AI 更大的自主权，使其能够学习代码库并代表用户执行跨文件的复杂更改，如实现新功能、大规模重构、项目初始化等 6。Agent 模式是 Cursor 实现更高级别自动化和代码生成能力的核心，它尝试模拟一个能够独立思考和执行任务的开发者助手。  
    * **Ask 模式：** 主要用于提问和理解代码库 6。开发者可以询问关于特定代码段的问题、获取复杂函数的解释、查找代码模式或规划功能实现 6。在此模式下，AI 提出的代码更改需要用户显式点击“Apply”按钮来应用 15。  
    * **Manual 模式：** 用于进行更受控的编辑，AI 仅基于用户明确提供的上下文（如选定的代码、引用的文件）进行操作 15。  
    * **Custom 模式：** 允许用户创建符合自己特定工作流程的自定义模式 6。  
  * **上下文管理：** Chat 通过分析打开的文件、用户通过 @ 符号引用的元素以及项目结构来理解上下文 15。对于长对话，Cursor 会智能总结早期消息以保持效率 15。  
  * **即时应用：** Chat 中生成的代码块可以通过点击代码块上方的“Apply”按钮（播放按钮图标）直接应用到编辑器中 3。  
* **C. ⌘K / Ctrl+K 快捷编辑与生成：**  
  * **行内交互：** ⌘K 提供了一种快速的行内（inline）方式来编辑或生成代码，无需离开当前编辑流程 1。  
  * **编辑模式：** 选中一段代码，按下 ⌘K，然后用自然语言描述你想要进行的修改 3。例如，“将此函数重构为异步函数”或“为这段代码添加错误处理”。  
  * **生成模式：** 在没有选中任何代码的情况下按下 ⌘K，然后描述你想要生成的新代码 5。例如，“生成一个计算斐波那契数列的函数”或“创建一个 React 函数组件”。  
  * **终端集成：** 在 Cursor 的集成终端中使用 ⌘K，可以用自然语言描述需要的终端命令，AI 会将其转换为实际的命令 12。这对于不熟悉复杂命令行语法的开发者尤其有用。  
  * **快速提问：** 选中代码后，可以通过 ⌘K 的菜单选择“快速提问”来获取关于该代码段的即时解答 12。  
* **D. Agent 模式深入：**  
  * **自主任务执行：** Agent 模式的核心是其自主性 12。它被设计用来处理端到端的任务，例如根据需求文档实现一个完整的功能 6。  
  * **上下文发现：** Agent 使用定制的检索模型来理解代码库，减少了用户手动添加上下文的需求 12。它会主动寻找和分析相关文件。  
  * **命令执行：** Agent 可以自动编写并运行终端命令（默认需要用户确认），例如安装依赖包或执行构建脚本 12。  
  * **错误处理与循环：** 一个强大的特性是 Agent 能够自动检测 lint 错误或其他构建错误，并尝试应用修复，然后再次检查，形成一个“循环修复”的过程，直到错误解决 12。这极大地减少了手动调试和修复构建问题的时间。  
  * **保持用户参与：** 尽管 Agent 具有自主性，但其设计目标是让程序员始终处于掌控之中 12。它会展示计划、征求确认（特别是对于运行命令或重大更改），并提供清晰的日志 30。

这些核心功能相互协作，共同构成了 Cursor 强大的 AI 编码辅助能力，旨在覆盖从代码编写、理解到调试和重构的整个开发生命周期。

## **V. 代码生成与编辑最佳实践**

利用 Cursor 的 AI 功能进行代码生成和编辑，可以显著提高效率，但需要掌握正确的方法。

* **A. 利用 Tab 补全加速编写：**  
  * **积极采纳建议：** 养成习惯，留意 Tab 键提供的多行建议。当建议准确时，大胆按下 Tab 键接受，可以节省大量击键时间 2。  
  * **快速原型构建：** 在编写新函数或组件的骨架时，Tab 补全尤其有用。输入函数签名或类定义，Tab 通常能预测并生成基础实现或常用模式 3。  
  * **处理重复模式：** 当需要对多个相似的代码块进行相同修改时（例如，更新一系列链接的 CSS 类），Tab 的预测能力非常强大。完成第一个修改后，继续按 Tab，Cursor 可能会自动应用后续的相似修改 2。  
  * **信任智能重写：** 允许 Tab 的智能重写功能纠正小的输入错误或不规范写法，保持编码流畅性，不必过分担心打字时的完美性 5。  
* **B. 使用 Chat 进行复杂生成与修改：**  
  * **清晰描述需求（Agent/Ask 模式）：** 对于实现新功能或进行较大范围的修改，使用 Chat 的 Agent 或 Ask 模式。用自然语言清晰、具体地描述目标 15。例如，不要只说“创建登录功能”，而应说明“使用 JWT 实现用户邮箱/密码登录认证，失败时返回 401 错误”。  
  * **提供上下文（@符号）：** 使用 @ 符号引用相关的现有文件、函数或文档，为 AI 提供必要的背景信息 5。例如，“在 @services/authService.ts 中添加一个处理用户注册的函数，使其类似于 @controllers/loginController.ts 中的登录逻辑”。  
  * **分步执行（Agent 模式）：** 对于复杂任务，可以将任务分解成更小的步骤，并指导 Agent 逐一完成 20。在 Chat 中明确指示当前步骤。  
  * **审查与应用：** 在 Ask 模式下，仔细审查 AI 提供的代码建议（diff 视图），确认无误后点击“Apply”应用 15。在 Agent 模式下，虽然 AI 会自动应用更改，但仍需在关键节点（如文件创建、命令执行）进行确认，并在完成后审查整体结果 12。  
  * **利用 Checkpoint 恢复：** 如果 Chat 中的修改引入了问题，可以使用聊天记录中的“Restore Checkpoint”按钮或消息旁边的“+”按钮回滚到之前的状态 15。  
* **C. 通过 ⌘K 进行快速行内操作：**  
  * **精确编辑：** 选中需要修改的小段代码，按 ⌘K 并描述修改意图。这比手动修改更快，尤其适用于重命名变量、调整逻辑或添加简单功能 3。  
  * **快速生成片段：** 在光标处按 ⌘K，快速生成样板代码、工具函数或特定算法的实现 5。  
  * **终端命令助手：** 在终端中使用 ⌘K 生成不熟悉的或复杂的命令，提高命令行效率 12。  
  * **选择 ⌘K vs Chat：** 对于目标明确、范围局限的修改或生成，⌘K 更快捷高效 28。对于需要更广泛代码库上下文、涉及多文件或需要详细讨论的任务，Chat 更合适 28。

**通用最佳实践：**

* **明确性原则：** 无论是使用 Tab、Chat 还是 ⌘K，提供给 AI 的指令或上下文越清晰、越具体，得到的结果就越准确 19。避免模糊不清的请求。  
* **迭代优化：** 不要期望 AI 一次就能完美生成所有代码。将 AI 辅助视为一个迭代过程，生成初步代码，然后通过进一步的提示或手动修改进行细化 17。  
* **审查与验证：** 始终审查 AI 生成或修改的代码 20。利用 Cursor 的 diff 视图 3 或 Git 工具 17 进行对比。对于关键逻辑，务必手动测试或编写单元测试进行验证 20。

## **VI. 代码理解与重构最佳实践**

Cursor 的 AI 能力不仅限于生成新代码，在理解和改进现有代码方面也同样强大。

* **A. 使用 Chat (Ask 模式) 理解代码：**  
  * **提问具体问题：** 选中一段不熟悉的代码或将光标放在特定函数上，使用 Chat (⌘L) 的 Ask 模式提问 6。例如：“这段代码的作用是什么？”或“解释一下这个函数的参数和返回值”。  
  * **探索代码库：** 使用 @Codebase 或 Ctrl+Enter 让 Chat 分析整个项目并回答更宏观的问题 5。例如：“项目中哪里定义了用户认证逻辑？”或“查找所有使用了 UserService 的地方”。  
  * **获取模式示例：** 询问 Chat 如何在当前项目中实现某种设计模式或特定功能，它可以基于现有代码提供示例 6。  
  * **解释复杂逻辑：** 对于难以理解的算法或复杂的业务逻辑，可以请求 Chat 提供分步解释或简化说明 4。  
* **B. 利用 Agent/Chat 进行智能重构：**  
  * **明确重构目标：** 在 Chat 中清晰地描述重构的目标和范围 15。例如，“将这个包含多个职责的类 LargeService 重构为遵循单一职责原则的多个小类”或“将项目中的回调函数替换为 Promises/Async/Await”。  
  * **提供上下文和规则：** 使用 @ 引用需要重构的文件或目录 12。如果项目有编码规范或设计模式要求，通过项目规则 (.cursor/rules) 或在提示中明确告知 AI 29。  
  * **选择合适的模式：**  
    * **Agent 模式：** 对于涉及多个文件的大规模重构，Agent 模式是理想选择 15。它能自主分析依赖关系并进行跨文件修改。  
    * **Ask/Manual 模式：** 对于小范围或需要更精细控制的重构，可以使用 Ask 模式先进行规划和预览，或使用 Manual 模式针对特定代码片段进行重构 15。  
  * **审查 Diff 视图：** 重构操作通常涉及较多改动。在应用更改前（尤其是在 Ask 模式下）或应用更改后（Agent 模式），务必仔细审查 diff 视图，确保重构符合预期且未引入新问题 3。  
  * **结合测试：** 在进行重构前后运行单元测试或集成测试是至关重要的最佳实践 19。可以要求 Cursor Agent 在重构后运行测试并修复失败的用例 17。  
  * **利用 Cursor 的建议：** Cursor 本身也会主动建议代码改进，例如将循环转换为列表推导、简化复杂条件或移除未使用变量 14。留意这些建议并考虑采纳。  
* **C. 结合 ⌘K 进行局部优化：**  
  * 对于小块代码的优化，例如简化某个函数的逻辑、改进变量命名或提取重复代码到新函数，选中代码后使用 ⌘K 是最快的方式 3。

**核心原则：**

* **理解先于修改：** 在进行大规模重构前，务必利用 Ask 模式或手动分析，确保自己和 AI 都充分理解了现有代码的逻辑和依赖关系。  
* **小步快跑：** 尽量将大型重构任务分解为一系列较小的、可验证的步骤 20。这使得审查更容易，风险更低。  
* **验证至上：** 重构的核心目标是改进代码结构而不改变其外在行为。自动化测试是验证这一点的最可靠方法 17。

## **VII. 调试最佳实践**

调试是软件开发中不可或缺的一环，Cursor 提供多种 AI 功能来辅助开发者更快地定位和修复错误。

* **A. 利用 Agent 模式自动修复错误：**  
  * **循环修复（Loops on Errors）：** Agent 模式具备自动检测 lint 错误或构建错误并尝试修复的能力 12。当 Agent 执行任务（如代码生成或重构）时，如果遇到这类错误，它会尝试应用修复，然后重新检查，直到错误消失或它无法解决。  
  * **YOLO 模式：** 通过在设置中启用 YOLO 模式，并配置允许运行的测试和构建命令（如 npm test, tsc），可以指示 Agent 在完成代码修改后自动运行这些检查 17。如果检查失败，Agent 会尝试修复问题并再次运行检查，实现自动化的测试-修复循环 28。这对于确保代码提交前的基本质量非常有帮助。  
  * **Bug Finder 功能：** Cursor 提供了一个“Bug Finder”功能（可通过 Cmd+Shift+P 访问），它可以分析当前分支与主分支的差异，并尝试识别潜在的错误（如未处理的空值）28。虽然并非完美，但可以作为额外的检查手段。  
* **B. 使用 Chat 进行错误分析与修复建议：**  
  * **解释错误信息：** 将代码中的错误信息或堆栈跟踪（stack trace）复制粘贴到 Chat 中（Ask 模式），请求 AI 解释错误原因并提供可能的解决方案 9。  
  * **代码审查式调试：** 选中包含可疑错误的代码段，使用 Chat 提问：“这段代码中是否存在潜在的 bug？”或“为什么这段代码会抛出 X 异常？” 12。  
  * **引用相关上下文：** 使用 @ 符号引用与错误相关的其他文件或函数，为 AI 提供更全面的诊断背景 12。  
  * **讨论修复策略：** 在 Ask 模式下与 AI 讨论不同的修复方案，评估其优缺点，然后再决定如何修改代码 15。  
* **C. 结合 ⌘K 进行快速修复：**  
  * **行内错误修正：** 对于明显的、局部的错误，可以直接选中错误代码，按 ⌘K，然后指示 AI “修复此处的空指针异常”或“添加缺失的 await 关键字” 12。  
* **D. 调试工作流：日志分析循环：**  
  * **第一步：让 AI 注入日志：** 当遇到难以定位的 bug 时，指示 Cursor（通过 Chat 或 ⌘K）在关键逻辑点添加详细的日志记录语句 17。  
  * **第二步：运行并收集日志：** 执行代码，复现 bug，并收集相关的日志输出 28。  
  * **第三步：将日志反馈给 AI：** 将收集到的日志粘贴到 Chat 中，并询问 AI：“根据这些日志，问题可能出在哪里？如何修复？” 28。  
  * **第四步：迭代与修复：** AI 会分析日志并提供更精确的诊断和修复建议。根据建议修改代码，或要求 AI 添加更具体的日志，重复此过程直至问题解决 28。这个工作流被社区用户证明是解决复杂问题的有效方法 37。

**注意事项：**

* **谨慎对待 AI 的修复：** AI 的修复建议并非总是完美的，有时甚至可能引入新的问题 20。务必理解 AI 的修复逻辑，并在应用后进行充分测试。  
* **明确错误描述：** 向 AI 描述 bug 时，提供清晰的复现步骤、预期行为和实际行为，有助于 AI 更快地理解问题。  
* **传统调试工具的补充：** AI 调试功能应视为对传统调试工具（如断点、单步执行）的补充，而非完全替代。对于复杂的运行时问题，结合使用效果更佳。

## **VIII. 文档与注释最佳实践**

良好的文档和注释对于代码的可维护性和团队协作至关重要。Cursor 可以有效辅助完成这些任务。

* **A. 利用 Chat/Agent 生成文档和注释：**  
  * **生成函数/类文档：** 选中一个函数或类，使用 Chat (Ask/Agent 模式) 或 ⌘K 指示 AI “为这个函数生成 JSDoc/DocString 文档”或“解释这个类的作用并生成注释” 3。  
  * **生成 README 文件：** 在 Chat (Agent 模式) 中，可以要求 AI 分析整个代码库并生成项目的 README.md 文件，包含项目介绍、安装指南、使用方法等 2。  
  * **批量添加注释：** 对于缺少注释的旧代码，可以使用 Agent 模式要求 AI 遍历指定文件或目录，并为公共函数和复杂逻辑块添加注释 6。  
  * **遵循规范：** 如果项目有特定的文档或注释规范（例如，遵循某种 DocString 格式），可以通过项目规则 (.cursor/rules) 或在提示中明确告知 AI 3。例如，可以设定规则“所有 Python 函数必须包含符合 Google 风格的 DocString，包含参数、返回值和异常说明” 33。  
* **B. 使用 @Docs 和 @Web 引用外部文档：**  
  * **引用库文档 (@Docs)：** 在 Chat 或 ⌘K 中提问或生成代码时，可以使用 @Docs 引用 Cursor 预先索引的流行库文档（如 React, Vue, Angular 等）12。例如，“@Docs react 如何使用 useEffect hook？”  
  * **添加自定义文档 (@Docs \-\> Add new doc)：** 对于项目中使用的私有库、内部框架或 Cursor 未预索引的第三方库，可以通过 @Docs \-\> Add new doc 功能添加其文档 URL 3。Cursor 会抓取并索引这些文档，之后就可以像使用预置文档一样通过 @Docs YourDocName 来引用 39。这对于确保 AI 基于准确、最新的 API 信息生成代码至关重要 9。可以在 Cursor 设置中管理已添加的自定义文档 3。  
  * **引用网页 (@Web)：** 当需要获取最新的信息、教程或特定问题的解决方案时，可以使用 @Web 让 AI 根据当前上下文进行网络搜索，并将搜索结果作为额外信息 3。例如，“@Web 查找最新的关于在 Next.js 14 中进行身份验证的最佳实践”。这有助于 AI 获取其训练数据可能不包含的最新知识 29。  
  * **粘贴链接 (@Link)：** 可以直接粘贴 URL，并在前面加上 @，让 Cursor 将该网页内容纳入上下文 5。  
* **C. 改进现有注释和文档：**  
  * **审查和重写：** 可以要求 Chat 或 Agent 审查现有的注释或文档，检查其准确性、清晰度，并根据代码的最新更改进行更新或重写。  
  * **统一风格：** 如果项目中的注释风格不一致，可以要求 AI 按照指定的规范统一修改。

**最佳实践要点：**

* **文档与代码同步：** 利用 AI 辅助生成和更新文档，有助于保持文档与代码的同步，减少文档过时的问题。  
* **提供准确的上下文：** 通过 @Docs 添加和引用准确的库文档，是确保 AI 生成符合 API 要求的代码的关键。  
* **利用网络资源：** @Web 是获取最新信息和解决特定问题的强大工具，尤其适用于快速发展的技术领域。  
* **规则驱动一致性：** 使用 .cursor/rules 来定义文档和注释标准，确保 AI 生成的内容符合项目规范。

## **IX. 上下文管理：让 AI 更懂你的代码**

有效管理提供给 AI 的上下文，是决定 Cursor 辅助效果好坏的关键因素。过多无关或过少相关的上下文都会影响 AI 的判断和生成质量 17。

* **A. 理解和使用 @ 符号：**  
  * **核心机制：** @ 符号是 Cursor 中手动指定上下文的主要方式 5。在 Chat、⌘K 等输入框中输入 @ 会弹出菜单，列出可引用的上下文类型 38。  
  * **常用 @ 符号及其用途** 38**：**  
    * @Files: 引用项目中的特定文件。适用于需要 AI 理解某个完整文件内容时。  
    * @Folders: 引用整个文件夹。用于需要 AI 了解某个模块或目录下多个文件交互时。  
    * @Code: 引用代码库中特定的代码片段或符号（如函数、类）。非常适合针对具体代码块提问或修改。  
    * @Docs: 引用预置或自定义的库/框架文档。生成特定库的代码或理解其用法时必不可少 35。  
    * @Web: 引用网络搜索结果。获取最新信息或外部知识时使用 12。  
    * @Git: 引用 Git 历史、提交或差异。在 Chat 中分析代码变更历史或进行相关操作时有用。  
    * @Codebase: 让 Cursor 在整个代码库中搜索相关上下文。适用于问题涉及范围较广或不确定具体文件时 5。  
    * @Recent Changes: 引用最近的代码修改。  
    * @Lint Errors: 在 Chat 中引用 Lint 错误。  
    * @Definitions: 在 ⌘K 中引用附近代码的定义。  
    * @Notepads: 引用预存的笔记或模板 29。  
    * @Cursor Rules: 引用项目或全局规则文件。  
  * **其他符号：** \#Files 用于添加文件到上下文但不创建显式引用；/command (如 /Reference Open Editors) 用于快速添加当前打开的文件 38。  
  * **最佳实践：**  
    * **精确性优先：** 尽量使用最具体的 @ 符号来提供最相关的上下文 17。例如，如果只需要一个函数的上下文，使用 @Code FunctionName 比 @Files FilePath.ts 更好。  
    * **引用相似代码：** 在请求生成新代码时，引用一个结构或风格相似的现有文件或组件 (@Files 或 @Code)，可以显著提高生成代码的质量和一致性 20。  
    * **平衡上下文量：** 避免一次性提供过多无关的文件或过于宽泛的 @Codebase 请求，这可能导致 AI 混淆或响应缓慢 17。同时也要确保提供了足够的信息让 AI 理解任务 17。  
* **B. 配置 AI 规则 (Project Rules vs. Global Rules)：**  
  * **目的：** 规则用于向 AI 提供持久化的指令，指导其行为、强制执行编码标准、定义项目约定等，避免在每次提示中重复说明 3。  
  * **Project Rules (.cursor/rules 目录) \- 推荐方式** 34**：**  
    * **特性：** 存储在项目内部（通常在 .cursor/rules 目录下），因此可以纳入版本控制 34。支持使用 gitignore 风格的模式匹配来指定规则适用的文件或文件夹 34，提供非常精细的控制。可以包含语义描述，解释规则的应用场景 34。当 AI 处理与模式匹配的文件相关的任务时，这些规则会自动被加载 34。允许在规则文件中使用 @file 引用项目内的其他文件（如风格指南文档）34。  
    * **适用场景：** 定义项目特定的编码规范（如命名约定、代码风格）、框架使用约定（如 Next.js 29 或 Angular 23 的最佳实践）、架构模式、禁止使用的模式（如避免占位符注释 20）等 29。  
    * **创建：** 可通过命令面板 (Cmd+Shift+P \> New Cursor Rule) 创建 34。  
  * **Global Rules (Cursor 设置)：**  
    * **特性：** 在 Cursor 的设置界面 (General \> Rules for AI) 中配置，应用于所有项目 9。  
    * **适用场景：** 设置通用的个人偏好，如默认的注释语言、期望的 AI 回复简洁度、全局遵循的基本编码原则等 34。  
  * **.cursorrules (项目根文件) \- 旧版：**  
    * **状态：** 为了向后兼容而保留，但官方推荐迁移到新的 .cursor/rules 目录结构，该文件未来可能被移除 29。  
  * **使用技巧：**  
    * **从小处着手：** 规则文件不必一开始就非常复杂。从解决最常见的问题或定义最核心的规范开始，随着使用过程逐步补充和完善 17。  
    * **利用 AI 优化规则：** 可以让 Cursor Agent 在编码会话结束后，根据交互情况“自我改进”规则文件 37。  
    * **规则的演进：** 从单一的 .cursorrules 文件演进到支持目录结构、模式匹配和 @file 引用的 .cursor/rules 系统，这反映了 Cursor 上下文管理能力的成熟。随着 AI 在开发中扮演更核心的角色以及项目复杂度的增加，对 AI 进行更细粒度、结构化和可维护的指导变得越来越重要，新的规则系统正是为了满足这种需求而设计的 29。  
* **C. 管理代码库索引：**  
  * **自动索引：** Cursor 在打开项目时会自动索引代码库，以便 AI 能够理解项目结构和内容 1。  
  * **忽略文件 (.cursorignore)：** 类似于 .gitignore，可以在项目根目录创建 .cursorignore 文件，指定不希望被 AI 索引的文件或目录（例如，构建产物、大型数据文件）5。  
  * **手动重新同步：** 在频繁添加、删除或重命名文件后，AI 的索引可能会过时，导致它引用不存在的文件或给出错误的建议 17。这时需要手动触发重新同步。可以通过 Cursor Settings \> Features \> Codebase Index \> Resync Index 或类似路径（具体路径可能随版本变化）来更新索引 41。保持索引的最新状态对于获取准确的 AI 辅助至关重要。

通过熟练运用 @ 符号、精心配置 AI 规则以及适时管理代码库索引，开发者可以极大地提升 Cursor AI 理解代码上下文的准确性，从而获得更高质量的辅助。

### 如何添加 @Docs 引用

下面以添加LangGraph的doc为例，介绍如何添加@Docs引用。

1. **获取LangGraph的doc**

```bash
# 进入LangGraph的docs目录，github.com/LangChain-AI/langgraph,导出所有doc到一个Markdown文件。

cd docs/docs
find . -name "*.md" -type f -print0 | xargs -0 cat > ../LangGraphDoc.md
```

2. **导入个人公开gist**

在<https://gist.github.com/>页面里填入下面信息：

```
“Description”： LangGraph Document
“FileName”：LangGraphDoc.md
把LangGraphDoc.md文件拖到页面里，点击“Add File”。
点击 “Create Public gist”会生成<https://gist.github.com/hobbytp/><gist_id>，
所有我的创建的gist可以在<https://gist.github.com/hobbytp>找到。
```

3. **在Cursor Settings中添加全局@Docs引用**
进入cursor settings=》Features，拉到最下面，添加@Docs引用。

```
# 在Cursor中添加@Docs引用
@Docs https://gist.github.com/hobbytp/<gist_id>
```

4. **在Cursor中使用@Docs引用**
这个其实在chat里面会自动查找@Docs引用的，不需要手动添加。
当然也可以在chat中添加@Docs引用。

```
# 在Cursor中使用@Docs引用
@Docs https://gist.github.com/hobbytp/<gist_id>
```

## **X. 高级工作流与社区洞见**

随着开发者对 Cursor 的深入使用，社区中涌现出许多高级工作流和实用技巧，旨在克服 AI 限制、管理复杂任务并进一步提升效率。

* **A. 推荐的开发工作流：**  
  * **Markdown 驱动的自主循环：** 一种创新的工作流利用两个核心 Markdown 文件来指导 AI Agent 30。project\_config.md 作为项目的“宪法”，存储长期不变的上下文（目标、技术栈、核心规则）。workflow\_state.md 则作为动态的“大脑”，包含当前状态、执行计划、详细的嵌入式规则和操作日志 30。AI 在这个循环中读取状态、解释规则、执行动作（编码、运行测试）、更新状态，从而实现更自主的任务处理，减少了持续提示的需求 30。  
  * **敏捷 AI 驱动开发 (AIADD)：** 针对复杂应用，此方法建议先使用外部的强大推理模型（如 Gemini、GPT-4o，可能通过 API 或 Web 界面，成本较低）进行深入的需求分析和架构设计，产出详细的规划文档或“制品” 44。然后，将这些精心设计的制品作为输入，在 Cursor 中指导 Agent 进行更精确、更细粒度的代码实现 44。这种分层方法旨在解决 Agent 在长期任务中可能出现的意图漂移和上下文丢失问题。  
  * **AI 辅助的测试驱动开发 (TDD)：** 这是一个被广泛推荐的实践 17。明确指示 Cursor 首先编写单元测试来定义预期行为，然后编写实现代码，接着运行测试，并根据测试失败信息迭代修改代码，直到所有测试通过 17。这种方法利用测试作为清晰、可执行的需求规约，能有效提高 AI 生成代码的可靠性和正确性。  
  * **YOLO 模式自动化流程：** 启用 YOLO 模式并配置好允许执行的测试和构建命令后，开发者可以让 Agent 在修改代码后自动运行这些检查 17。Agent 会自动修复检测到的错误（如 lint 错误、类型错误）并重新运行检查，直至成功 28。这特别适用于代码提交前的自动化清理和验证阶段。  
  * **日志分析调试循环：** 如前文调试部分所述，通过“AI 添加日志 \-\> 运行代码收集日志 \-\> 将日志反馈给 AI 分析 \-\> AI 提供修复建议 \-\> 重复”的循环，可以有效解决难以追踪的 bug 17。  
  * **结构化重构流程：** 对于大型重构，建议先备份原始文件 36。然后指导 Agent 基于规则和提示进行重构。利用 AI 生成的测试脚本（如 Puppeteer 脚本）在重构前后验证功能一致性 36。完成后仔细比对，甚至可以要求 Agent 删除原文件并根据重构逻辑重新生成 36。  
  * **规划先行：** 对于复杂任务，先使用推理能力更强的模型（如 Claude 3 Opus (o1), o3-mini，可能通过 Cursor 的模型选择或外部工具）生成详细的执行计划（如 PLAN.md 或 steps.md 文件）17。然后将这个计划提供给 Cursor 的 Agent（如 Claude 3.5 Sonnet）来执行具体的编码实现 17。这利用了不同模型在规划和执行上的优势互补。  
* **B. 来自用户社区的技巧与窍门 (论坛, Reddit)：**  
  * **上下文管理技巧：**  
    * **频繁重置会话：** 对于多步骤任务，为每个主要步骤开启新的 Chat 会话，以防止上下文混乱或规则失效 37。  
    * **上下文标记：** 要求 AI 在回复中包含特定标记（如随机动物表情符号 🦊），如果标记消失，则表明 AI 可能已丢失上下文 37。  
    * **状态文件：** 使用 memory.md, steps.md, spec.md 等文件，并在规则中引用它们，让 AI 记录进度和遵循规划 37。  
    * **引用相似代码：** 这是提高风格一致性的关键，使用 @ 明确指向现有代码 20。  
    * **项目结构文件：** 创建 project\_structure.md（包含 tree 命令输出），让 Agent 了解目录结构，避免在错误位置创建文件 37。  
    * **聚焦上下文：** 关闭不相关的编辑器标签页，使用 /Reference Open Editors 命令快速添加当前所需文件的上下文 41。  
    * **Notepads 复用：** 将常用的提示、文件引用、配置说明等存入 Notepads (@Notepads)，方便快速调用，避免重复输入 29。  
  * **提示与规则工程：**  
    * **规则自优化：** 让 Agent 在编码会话后分析交互，并建议改进 .cursor/rules 文件 37。  
    * **规则迭代：** 从简单的规则开始，根据遇到的问题逐步添加 17。  
    * **防错规则：** 加入明确规则以避免 AI 的常见错误，如生成占位符注释 (// rest of the processing...) 20。  
    * **强制最佳实践：** 使用规则强制要求生成文档、类型提示、单元测试等 42。  
    * **详细需求：** 提供详细的需求规格说明文件 (spec.md) 37。  
  * **调试技巧：**  
    * **日志驱动：** 主动要求 AI 添加大量调试日志，并将日志结果反馈给 AI 进行分析，这通常比仅描述问题更有效 17。  
  * **验证策略：**  
    * **单元测试优先：** 依赖 AI 生成的单元测试进行功能验证 33。  
    * **人工审查关键代码：** 对于认证、支付、安全等核心模块，必须进行逐行的人工审查 20。  
    * **小步验证：** 保持 AI 的修改范围较小，并频繁进行实时测试 20。  
  * **工作流习惯：**  
    * **人机协作：** 在精力充沛时手动规划复杂功能，将 AI 用于具体的实现和重复性任务 20。  
    * **版本控制：** 严格使用 Git 进行版本控制。推荐使用 GitHub Desktop 等可视化工具审查 AI 产生的大量变更，比命令行 diff 或 git add \-p 更直观 17。  
    * **适时脱离：** 定期尝试不使用 AI 编码，有助于保持独立思考能力，并更好地判断何时适合使用 AI 20。  
* **C. 处理复杂任务和大型项目：**  
  * **任务分解：** 核心策略是将复杂任务分解为更小、更易于管理和验证的子任务 19。  
  * **结构化上下文：** 必须依赖结构化的上下文管理方法，包括精细的规则 (.cursor/rules)、精确的 @ 引用、以及规划/状态文件（如 PLAN.md, workflow\_state.md）17。  
  * **谨慎使用 Agent：** Agent 模式虽然强大，但在大型项目中执行复杂的多文件操作时，需要周密的计划、清晰的指令和严格的审查 13。  
  * **人机交互迭代：** 即使有 AI 辅助，复杂任务（如大型框架升级）往往仍需要大量的人工干预、指导和迭代 45。  
  * **社区智慧的体现：** 观察社区中涌现的各种高级工作流，可以发现一个共同模式：高级用户倾向于在 Cursor 的核心功能之上构建额外的“脚手架”（如规划文件、状态管理文件、复杂的规则集）。这表明，要让 AI 在大型或复杂项目中可靠地工作，开发者需要主动创建和维护这些元结构来弥补 AI 在长期记忆、复杂推理和上下文维持方面的固有局限性，从而更有效地引导 AI 17。

## **XI. 与语言、框架和环境的集成**

Cursor 作为 VS Code 的一个分支，继承了其广泛的语言支持能力，但针对特定技术栈和开发环境，仍有一些最佳实践和注意事项。

* **A. 通用语言支持与最佳实践：**  
  * **广泛兼容性：** Cursor 支持 VS Code 支持的大多数编程语言 5。其 AI 功能基于通用的 LLMs（如 GPT-4o, Claude 3.5 Sonnet）3，因此理论上可以为任何语言生成代码，尽管在流行语言（如 Python, JavaScript, TypeScript, Java）上表现通常更优 3。  
  * **通用最佳实践：**  
    * **利用强类型语言：** 使用 TypeScript (而非 JavaScript) 或其他强类型语言，因为类型信息为 AI 提供了重要的上下文线索，有助于生成更准确、更安全的代码 17。  
    * **安装语言扩展：** 利用 VS Code 庞大的扩展市场。安装特定语言的官方或流行扩展（如语法高亮、LSP、调试器），Cursor 可以导入并使用它们 2。  
    * **定义语言规则：** 在 .cursor/rules 中为项目使用的语言设定代码风格、命名约定和最佳实践规则，以指导 AI 生成符合规范的代码 23。例如，强制 Python 使用类型提示 3。  
* **B. 特定技术栈考量：**  
  * **Java / Spring Boot：**  
    * **环境配置：** Cursor 不自带 JDK，需要开发者手动安装并配置好 JAVA\_HOME 环境变量 35。  
    * **扩展安装：** 强烈建议安装 Extension Pack for Java、Gradle for Java / Maven for Java 以及 Spring Boot Extension Pack 等关键扩展 35。  
    * **Cursor 应用：** 利用 Tab 补全生成 Java 样板代码（构造函数、getter/setter、equals/hashCode）35；使用 Chat 解释复杂的 Java 异常堆栈跟踪 35；使用 Agent 模式进行代码现代化重构（如匿名类转 Lambda）或实现设计模式 35；通过 @Docs 添加 Spring Boot 或其他库的文档，辅助生成框架特定代码 35。  
  * **Python：**  
    * **强项：** Cursor 对 Python 的支持非常成熟，广泛应用于数据科学、机器学习脚本和 Web 开发（Flask, Django）等领域 3。  
    * **实践：** 使用规则强制类型提示 3；利用 AI 生成测试用例和文档字符串。  
  * **JavaScript / TypeScript：**  
    * **核心支持：** 作为 Web 开发的主流语言，JS/TS 得到 Cursor 的良好支持 3。  
    * **实践：** 优先使用 TypeScript 以获得更好的类型上下文 17；利用规则强制执行 TS 最佳实践和代码风格 29。  
  * **前端框架 (React / Angular / Vue)：**  
    * **基础：** 主要通过其强大的 JS/TS 支持来辅助这些框架的开发。  
    * **框架规则：** 使用 .cursor/rules 定义特定框架的最佳实践和编码约定（例如 Next.js 29 或 Angular 23）。  
    * **文档引用：** 通过 @Docs 引用框架官方文档至关重要 35。  
    * **迁移辅助：** Cursor Agent 可以辅助进行框架版本迁移（如 Vue 2 到 Vue 3），但这通常是复杂任务，需要详细规划、分步执行和大量人工指导与验证 45。AI 可能难以完全自主处理所有迁移细节（如 Vuex 到 Pinia 的 API 差异）45。  
    * **潜在问题：** 有用户报告 AI 可能生成基于旧版本框架（如 Angular）的代码 46。这强调了提供最新文档 (@Docs) 和清晰示例 (@Code) 作为上下文的重要性，以引导 AI 使用最新特性。  
    * **结合 UI 工具：** 可以考虑使用 v0.dev 等 AI UI 生成工具创建界面，然后将生成的代码（通常基于 React/Next.js 和 shadcn/ui）导入 Cursor，利用 Cursor 编写后端逻辑和交互功能 47。  
  * **.NET / C\#：**  
    * **可用性：** 社区中有用户在.NET 项目中使用 Cursor 10。Cursor 本身支持 C\# 语法和代码生成 13。  
    * **调试限制：** 最大的痛点在于调试。由于 Cursor 是 VS Code 的分支，而微软限制其官方 C\# 调试器只能在 Visual Studio 或官方 VS Code 中运行，因此 Cursor 无法提供与 Visual Studio 或 VS Code 相同的原生.NET 调试体验 10。这可能需要开发者依赖其他调试方法或在必要时切换回 VS/VS Code 进行调试。相比之下，GitHub Copilot 在 VS Code 中的调试集成可能更顺畅 11。  
* **C. 移动开发 (iOS / Android) 考量：**  
  * **跨平台框架：** Cursor 可以很好地支持基于 JS/TS 的跨平台框架，如 React Native 或基于 Dart 的 Flutter，利用其相应的语言支持和 VS Code 扩展。64 提到了 Cursor AI 在跨平台开发中提高代码复用和效率的潜力。  
  * **原生 iOS (Swift / Xcode)：**  
    * **可行性：** 开发者确实在使用 Cursor 编写 Swift 代码并编辑 Xcode 项目文件 49。它可以用于代码生成、重构、本地化 49、编写测试 49 等任务。  
    * **工作流摩擦：** 主要挑战在于 Cursor 无法完全替代 Xcode 的构建、签名、模拟器/真机部署和原生调试流程 49。开发者需要频繁在 Cursor 和 Xcode 之间切换 49。设置过程也可能比 Web 开发更繁琐 49。  
    * **定位：** Cursor 在 iOS 开发中更像一个强大的代码编辑和生成辅助工具，而非完整的 IDE 替代品 49。适合处理编码密集型任务，但最终的构建和调试仍需依赖 Xcode。  
  * **原生 Android (Kotlin / Java)：**  
    * **类似原理：** 与 iOS 类似，需要手动配置好 JDK 35 和相关的 Android SDK 及 VS Code 扩展。可以使用 Cursor 进行 Kotlin/Java 代码的编写、重构和 AI 辅助。  
    * **工具链依赖：** 同样地，构建、打包 (APK/AAB)、模拟器/设备部署和深度调试很可能仍需依赖 Android Studio 或 Gradle 命令行工具。  
  * **初学者应用：** 对于编程经验很少的初学者，使用 Cursor 从零开始构建移动应用是可能的，但挑战很大 50。这需要大量的提示工程、规则设置、学习版本控制 (Git) 等基础知识，并且需要有耐心处理 AI 的错误和不一致性 50。AI 更像一个需要不断指导的初级助手 49。  
  * **核心价值与局限：** Cursor 对移动开发的价值主要体现在其 AI 驱动的代码编辑、重构和生成能力上，可以加速开发过程中的编码环节。然而，它作为 VS Code 分支的性质，决定了它与原生移动开发工具链（Xcode, Android Studio）之间存在固有的集成摩擦，特别是在构建、调试和部署这些平台强相关的环节。因此，在原生移动开发中，Cursor 更适合作为 Xcode 或 Android Studio 的补充工具，而非完全替代品 49。

## **XII. 对比分析：Cursor 与其他 AI 编码助手**

为了更好地理解 Cursor 的定位和优势，有必要将其与市场上其他主流的 AI 编码助手进行比较。

* **A. 功能特性对比矩阵：**  
  下表总结了 Cursor 与几款主要竞品（GitHub Copilot, Tabnine, Codeium, Amazon CodeWhisperer）在关键功能上的对比（基于 2024-2025 年信息）：

| 功能 | Cursor | GitHub Copilot | Tabnine | Codeium | Amazon CodeWhisperer |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **核心形态** | 独立编辑器 (VS Code Fork) 1 | IDE 扩展 52 | IDE 扩展 54 | IDE 扩展 55 | IDE 扩展 54 |
| **代码补全** | 强（多行、块级、智能重写）12 | 强（行级为主，有建议选项）26 | 强（上下文感知，可本地运行）54 | 强（上下文感知）55 | 强（优化 AWS API）54 |
| **Chat 交互** | 是（上下文感知，支持 @, 图像）12 | 是（集成 GitHub 知识库）53 | 是（部分计划）59 | 是（免费，代码库上下文）57 | 是 54 |
| **Agent/多文件编辑** | 是（Agent 模式，Composer）12 | 是（Edits 模式，仍在发展中）11 | 否 | 否 | 否 |
| **代码库上下文** | 强（自动索引，@Codebase）12 | 中等（@workspace，可能较慢）26 | 中等（依赖本地/云端模型）56 | 中等 55 | 弱（主要关注当前文件/AWS 上下文）54 |
| **上下文控制 (@/规则)** | 非常灵活 (@ 符号丰富, .cursor/rules) 5 | 有限（@workspace, \#editor 等）60 | 有限（主要通过模型训练）8 | 有限 | 有限 |
| **终端 AI** | 是 (⌘K) 12 | 是 (GitHub Copilot CLI) 53 | 否 | 否 | 否 |
| **调试辅助** | 中等（Agent 错误修复, Chat 分析）12 | 中等（Chat 分析，部分语言集成好）7 | 弱 | 弱 | 弱（有安全扫描）8 |
| **文档引用** | 强 (@Docs, @Web, 自定义文档) 12 | 中等（Chat 可查询） | 弱 | 弱 | 弱 |
| **语言支持** | 广泛 (VS Code 基础) 5 | 广泛 (多语言训练) 56 | 非常广泛 (\>40-80 种) 8 | 广泛 (\>70 种) 55 | 广泛 8 |
| **IDE 集成** | 自身即 IDE (VS Code Fork) 1 | 强 (VS Code, JetBrains, VS, Vim) 53 | 强 (VS Code, JetBrains, Sublime 等) 54 | 强 (主流 IDEs) 57 | 中等 (主要 AWS Cloud9, VS Code, JetBrains) 54 |
| **隐私选项** | 好（隐私模式，SOC2 认证，Business 可强制）2 | 中等（依赖 GitHub/MS 策略，有企业版）16 | 最好（可本地运行模型，私有代码训练）8 | 中等（提供企业自托管选项） | 中等（AWS 生态内）8 |
| **定价 (Pro/付费)** | $20/月 (Pro) 24 | $10/月 (Individual) 16 | $12/月 (Pro) 8 | 付费版 ($12/月起) | 付费版 (Pro) |
| **免费版** | 是（有限请求）24 | 否（有试用）16 | 是（基础功能）54 | 是（功能较全）57 | 是（个人免费）8 |
| **关键差异** | 深度 AI 集成 IDE, Agent 模式, 灵活上下文控制, VS Code 体验 | GitHub 生态集成, 企业稳定, Copilot Chat 跨平台 | 隐私优先 (本地模型), 团队模型训练 | 强大的免费版, 自研模型 | AWS 生态优化, 安全扫描 |

* **B. 性能与速度考量：**  
  * **交互速度：** 社区普遍反馈 Cursor 的核心 AI 交互（如 Tab 补全、Agent 执行）在感知上比 GitHub Copilot 更快、更流畅 11。对于需要频繁与 AI 交互的开发者来说，这种速度差异可能显著影响体验 11。  
  * **资源消耗：** Cursor 作为独立应用，可能比 Copilot 插件消耗更多的内存 52。对于资源受限的环境，这可能是一个考虑因素。  
  * **模型稳定性：** 有用户指出，Cursor 使用的模型（如 Claude Sonnet）有时表现可能不如 Copilot 使用的模型（如 GPT-3.5/4）稳定和一致 11。Copilot 的模型可能在不同请求间提供更可预测的结果。  
  * **特定任务性能：** Copilot 由于运行在原生 VS Code 环境中，可能在利用 GPU 加速的图形密集型项目（如 WebGL）中表现更好 52。  
  * **速率限制：** Copilot 有明确的速率限制，达到后可能无法使用 11。Cursor Pro 计划在用完“快速”高级模型请求后，提供无限量的“慢速”请求，这被一些用户视为更灵活或 фактически 无限 11。  
  * **性能权衡：** 性能对比并非单一维度。Cursor 在交互延迟上通常占优，但在资源消耗和模型稳定性上可能存在劣势。Copilot 则可能在稳定性和特定场景（如图形、企业集成）下表现更好，但核心交互速度可能较慢。开发者需要根据自己的工作负载和优先级进行权衡 11。  
* **C. 优劣势与理想用例分析：**  
  * **Cursor 优势：**  
    * **深度集成与 VS Code 体验：** 提供原生、无缝的 AI 功能，同时保持 VS Code 的熟悉感和扩展性 1。  
    * **强大的代码编辑/生成能力：** Tab 补全和 Agent 模式在多行编辑、代码块生成和重构方面表现突出 12。  
    * **灵活的上下文控制：** 通过丰富的 @ 符号和强大的 .cursor/rules 系统，可以精确地向 AI 提供上下文 5。  
    * **模型选择（付费版）：** Pro 和 Business 用户可以选择不同的底层 AI 模型 24。  
    * **Agent 模式成熟度：** 其 Agent 模式相对 Copilot 的 Edits 模式，目前被认为更成熟、更可靠 26。  
    * **适合新项目：** 对于从零开始的项目，Cursor 的快速原型和代码生成能力优势明显 52。  
  * **Cursor 劣势：**  
    * **需要引导：** 对于复杂任务，仍需用户提供清晰的提示和结构化的上下文管理 19。  
    * **潜在不稳定性：** 模型表现可能存在波动 11，资源消耗相对较高 52。  
    * **特定栈限制：** 如.NET 调试受限 10。  
    * **学习曲线：** 要充分发挥高级功能（如规则、Agent 工作流），需要一定的学习和实践 13。  
    * **快捷键冲突：** 覆盖部分 VS Code 默认快捷键可能 gây phiền toái 11。  
  * **Cursor 理想用例：**  
    * 习惯 VS Code 并寻求更深度 AI 集成的开发者。  
    * 需要进行大量 AI 驱动的代码生成、重构或复杂任务处理的项目。  
    * 愿意投入时间学习和配置高级功能（如规则、Agent）以最大化效率的用户。  
    * 初创公司或独立开发者，优先考虑前沿 AI 能力和开发速度 52。  
  * **竞品亮点：**  
    * **GitHub Copilot:** 强大的 GitHub 和微软生态系统集成 52，对企业用户和大型遗留项目（尤其.NET/Java）可能更友好 52，模型表现更稳定 11，用户界面更简洁 16。  
    * **Tabnine:** 高度重视隐私，提供本地模型部署和基于团队代码的训练 8。  
    * **Codeium:** 提供功能非常全面的免费版本 57，使用自研模型 55。  
    * **Amazon CodeWhisperer:** 针对 AWS 服务进行了特别优化，适合重度 AWS 用户 8。  
* **D. 定价比较：**  
  * **Cursor:** 提供免费版（有限制），Pro 版 $20/月，Business 版 $40/用户/月 5。可能因超出快速请求限制或使用 API Key 产生额外费用 11。  
  * **GitHub Copilot:** 无免费版（仅试用），个人版 $10/月，商业版 $19/用户/月，企业版 $39/用户/月 16。成本相对固定可预测 11。  
  * **Tabnine:** 提供免费版，Pro 版 $12/用户/月 8。  
  * **Codeium:** 以其慷慨的免费版著称 57。  
  * **Amazon CodeWhisperer:** 提供免费版 8。

选择哪个工具取决于开发者的具体需求、项目类型、预算以及对隐私、集成和特定功能的偏好。Cursor 以其深度集成、强大的编辑能力和灵活的上下文控制脱颖而出，尤其适合追求极致 AI 辅助效率的 VS Code 用户。

## **XIII. 结论：通过最佳实践最大化 Cursor 价值**

Cursor AI 作为一款深度集成人工智能的代码编辑器，为开发者提供了前所未有的编码助力。然而，要充分释放其潜力，避免潜在的陷阱，遵循一系列最佳实践至关重要。

* **A. 关键实践总结：**  
  * **掌握核心功能：** 熟练运用 Tab 智能补全、Chat 的不同模式（Agent/Ask/Manual）以及 ⌘K 快捷编辑，理解各自的适用场景。  
  * **精通提示工程：** 提供清晰、具体、上下文丰富的提示是获取高质量 AI 输出的基础。学会分解复杂任务。  
  * **善用 Agent 模式：** 对于自动化任务、多文件操作和 TDD 流程，Agent 模式非常强大，但务必结合周密的规划和严格的审查。  
  * **拥抱 AI 辅助调试：** 利用 Agent 的错误修复循环、Chat 的错误分析能力以及日志分析工作流，加速问题定位和解决。  
  * **整合文档资源：** 通过 @Docs（包括自定义文档）和 @Web 将相关文档和最新信息融入开发流程，提高代码准确性。  
  * **主动管理上下文：** 战略性地使用 @ 符号，精心配置 .cursor/rules，并保持代码库索引更新，确保 AI 获得恰当的信息。  
  * **借鉴社区智慧：** 探索并尝试社区分享的高级工作流（如 Markdown 驱动、AIADD、规划先行），以应对复杂项目挑战。  
  * **验证与监督：** 永远不要盲目信任 AI 的输出。进行代码审查，利用自动化测试，特别是对关键和敏感代码进行人工校验。  
* **B. AI 在开发中角色的演变：**  
  * **从编写到指导：** Cursor 等工具正推动开发者角色发生转变，从逐行编写代码，更多地转向需求描述、AI 指导、结果审查和系统设计 7。这要求开发者具备更强的沟通、抽象和批判性思维能力。  
  * **挑战与反思：** AI 的广泛应用也带来了新的挑战和思考。过度依赖可能导致开发者基础技能下降或对底层逻辑理解不足（所谓的“vibe coding”风险）21。AI 工具本身也可能存在偏见、不一致性或产生看似正确实则错误的“幻觉” 31。因此，保持人类的监督、判断和对基础知识的掌握仍然至关重要 20。Cursor AI 自身拒绝继续生成代码并要求用户自行理解的事件，也引发了关于 AI 在编程中应扮演何种角色的哲学讨论 21。  
  * **未来展望：** AI 编码助手技术仍在快速发展。我们可以期待更强的推理能力、更无缝的集成、更智能的上下文理解以及新的协作模式（如 MCP 服务器标准 63）。Cursor 以其快速迭代和深度集成的特性，有望继续在这一浪潮中保持领先地位 2。对于开发者而言，持续学习、适应变化，并将这些强大的 AI 工具视为提升创造力和效率的杠杆，将是未来成功的关键。

总之，Cursor AI 提供了一套强大的工具集，通过遵循本文概述的最佳实践，开发者可以显著提升编码效率和代码质量，更专注于创造性的软件工程任务。但同时，也应保持审慎，理解 AI 的局限性，并不断提升自身的指导和判断能力，以在人机协作的新范式中游刃有余。

#### **引用的著作**

1. Cursor – Welcome to Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/get-started/welcome](https://docs.cursor.com/get-started/welcome)  
2. Cursor \- The AI Code Editor, 访问时间为 四月 11, 2025， [https://www.cursor.com/](https://www.cursor.com/)  
3. Cursor AI: A Guide With 10 Practical Examples \- DataCamp, 访问时间为 四月 11, 2025， [https://www.datacamp.com/tutorial/cursor-ai-code-editor](https://www.datacamp.com/tutorial/cursor-ai-code-editor)  
4. Cursor AI: Your New AI-Powered Coding Assistant \- Dirox, 访问时间为 四月 11, 2025， [https://dirox.com/post/cursor-ai-your-new-ai-powered-coding-assistant](https://dirox.com/post/cursor-ai-your-new-ai-powered-coding-assistant)  
5. The Ultimate Introduction to Cursor for Developers \- Builder.io, 访问时间为 四月 11, 2025， [https://www.builder.io/blog/cursor-ai-for-developers](https://www.builder.io/blog/cursor-ai-for-developers)  
6. Introduction \- Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/get-started/introduction](https://docs.cursor.com/get-started/introduction)  
7. Why Cursor.ai is the Future of Code Editing and a Superior Alternative to Visual Studio, 访问时间为 四月 11, 2025， [https://medium.com/@saharshgpt5/why-cursor-ai-is-the-future-of-code-editing-and-a-superior-alternative-to-visual-studio-b7cf165e1ef1](https://medium.com/@saharshgpt5/why-cursor-ai-is-the-future-of-code-editing-and-a-superior-alternative-to-visual-studio-b7cf165e1ef1)  
8. What is the Best and Most Advanced AI Code Assistant? \- BytePlus, 访问时间为 四月 11, 2025， [https://www.byteplus.com/en/topic/386625](https://www.byteplus.com/en/topic/386625)  
9. Cursor: AI IDE Transforming Software Development | by Alberto Basalo \- Medium, 访问时间为 四月 11, 2025， [https://albertobasalo.medium.com/cursor-ai-ide-transforming-software-development-6eeb049c43eb](https://albertobasalo.medium.com/cursor-ai-ide-transforming-software-development-6eeb049c43eb)  
10. Cursor AI with .NET? : r/dotnet \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/dotnet/comments/1fihmz0/cursor\_ai\_with\_net/](https://www.reddit.com/r/dotnet/comments/1fihmz0/cursor_ai_with_net/)  
11. GitHub Copilot vs Cursor in 2025: Why I'm paying half price for the same features \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/GithubCopilot/comments/1jnboan/github\_copilot\_vs\_cursor\_in\_2025\_why\_im\_paying/](https://www.reddit.com/r/GithubCopilot/comments/1jnboan/github_copilot_vs_cursor_in_2025_why_im_paying/)  
12. Features | Cursor \- The AI Code Editor, 访问时间为 四月 11, 2025， [https://www.cursor.com/features](https://www.cursor.com/features)  
13. Cursor AI vs Copilot: A Detailed Analysis \- Codoid, 访问时间为 四月 11, 2025， [https://codoid.com/ai/cursorai-vs-copilot-a-detailed-analysis/](https://codoid.com/ai/cursorai-vs-copilot-a-detailed-analysis/)  
14. Cursor AI: The AI-powered code editor changing the game \- Daily.dev, 访问时间为 四月 11, 2025， [https://daily.dev/blog/cursor-ai-everything-you-should-know-about-the-new-ai-code-editor-in-one-place](https://daily.dev/blog/cursor-ai-everything-you-should-know-about-the-new-ai-code-editor-in-one-place)  
15. Overview \- Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/chat/overview](https://docs.cursor.com/chat/overview)  
16. Cursor vs Copilot: Which is A Better AI-Powered Coding Tool? | Relia Software, 访问时间为 四月 11, 2025， [https://reliasoftware.com/blog/cursor-vs-copilot](https://reliasoftware.com/blog/cursor-vs-copilot)  
17. Cursor: An AI Dev Starter Guide \- kvz.io, 访问时间为 四月 11, 2025， [https://kvz.io/blog/cursor.html](https://kvz.io/blog/cursor.html)  
18. AI Impact on Java Developers : CURSOR AI Powered Code Editor | Best Practices & Real Examples \- YouTube, 访问时间为 四月 11, 2025， [https://m.youtube.com/watch?v=nALwdilg1Jg](https://m.youtube.com/watch?v=nALwdilg1Jg)  
19. The Ultimate Guide to AI-Powered Development with Cursor: From Chaos to Clean Code, 访问时间为 四月 11, 2025， [https://medium.com/@vrknetha/the-ultimate-guide-to-ai-powered-development-with-cursor-from-chaos-to-clean-code-fc679973bbc4](https://medium.com/@vrknetha/the-ultimate-guide-to-ai-powered-development-with-cursor-from-chaos-to-clean-code-fc679973bbc4)  
20. My Cursor AI Workflow That Actually Works : r/ChatGPTCoding \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/ChatGPTCoding/comments/1jiyzro/my\_cursor\_ai\_workflow\_that\_actually\_works/](https://www.reddit.com/r/ChatGPTCoding/comments/1jiyzro/my_cursor_ai_workflow_that_actually_works/)  
21. After 800 lines, AI-powered Cursor AI halts, tells user 'can't generate code, develop the logic yourself to ensure...' \- Business Today, 访问时间为 四月 11, 2025， [https://www.businesstoday.in/technology/artificial-intelligence/story/after-800-lines-ai-powered-cursor-ai-halts-tells-user-cant-generate-code-develop-the-logic-yourself-to-ensure-471223-2025-04-08](https://www.businesstoday.in/technology/artificial-intelligence/story/after-800-lines-ai-powered-cursor-ai-halts-tells-user-cant-generate-code-develop-the-logic-yourself-to-ensure-471223-2025-04-08)  
22. Downloads | Cursor \- The AI Code Editor, 访问时间为 四月 11, 2025， [https://www.cursor.com/downloads](https://www.cursor.com/downloads)  
23. Cursor AI Took My Job… or Did It? Angular Dev Edition \- Brian Treese, 访问时间为 四月 11, 2025， [https://briantree.se/cursor-ai-for-better-angular-development/](https://briantree.se/cursor-ai-for-better-angular-development/)  
24. Pricing | Cursor \- The AI Code Editor, 访问时间为 四月 11, 2025， [https://www.cursor.com/pricing](https://www.cursor.com/pricing)  
25. Top Features of Cursor AI \- APPWRK, 访问时间为 四月 11, 2025， [https://appwrk.com/cursor-ai-features](https://appwrk.com/cursor-ai-features)  
26. Cursor vs GitHub Copilot: Which AI Coding Assistant is better? \- Builder.io, 访问时间为 四月 11, 2025， [https://www.builder.io/blog/cursor-vs-github-copilot](https://www.builder.io/blog/cursor-vs-github-copilot)  
27. Understanding Cursor's AI feature \- Discussion, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/understanding-cursors-ai-feature/7204](https://forum.cursor.com/t/understanding-cursors-ai-feature/7204)  
28. How I use Cursor (+ my best tips) \- Builder.io, 访问时间为 四月 11, 2025， [https://www.builder.io/blog/cursor-tips](https://www.builder.io/blog/cursor-tips)  
29. Cursor AI: 5 Advanced Features You're Not Using \- Builder.io, 访问时间为 四月 11, 2025， [https://www.builder.io/blog/cursor-advanced-features](https://www.builder.io/blog/cursor-advanced-features)  
30. \[Guide\] A Simpler, More Autonomous AI Workflow for Cursor ..., 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688](https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688)  
31. Cursor advices : r/ChatGPTCoding \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/ChatGPTCoding/comments/1jovoed/cursor\_advices/](https://www.reddit.com/r/ChatGPTCoding/comments/1jovoed/cursor_advices/)  
32. My Cursor AI Workflow That Actually Works | N's Blog, 访问时间为 四月 11, 2025， [https://nmn.gl/blog/cursor-guide](https://nmn.gl/blog/cursor-guide)  
33. Curious to know what are your hacks or workflows to get the best out ..., 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/curious-to-know-what-are-your-hacks-or-workflows-to-get-the-best-out-of-cursor/10808](https://forum.cursor.com/t/curious-to-know-what-are-your-hacks-or-workflows-to-get-the-best-out-of-cursor/10808)  
34. Rules for AI \- Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/context/rules-for-ai](https://docs.cursor.com/context/rules-for-ai)  
35. Java \- Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/guides/languages/java](https://docs.cursor.com/guides/languages/java)  
36. Advice for refactoring/workflows? : r/cursor \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/cursor/comments/1j6fyaf/advice\_for\_refactoringworkflows/](https://www.reddit.com/r/cursor/comments/1j6fyaf/advice_for_refactoringworkflows/)  
37. Maximizing Cursor AI – What's Your Best Workflow Hack? \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/cursor/comments/1ipqiyg/maximizing\_cursor\_ai\_whats\_your\_best\_workflow\_hack/](https://www.reddit.com/r/cursor/comments/1ipqiyg/maximizing_cursor_ai_whats_your_best_workflow_hack/)  
38. Overview \- Cursor, 访问时间为 四月 11, 2025， [https://docs.cursor.com/context/@-symbols/overview](https://docs.cursor.com/context/@-symbols/overview)  
39. Cursor – @Docs, 访问时间为 四月 11, 2025， [https://docs.cursor.com/context/@-symbols/@-docs](https://docs.cursor.com/context/@-symbols/@-docs)  
40. How To Setup Cursor To Index & Learn About Your Docs \#cursor \#ai \#code \#ide \- YouTube, 访问时间为 四月 11, 2025， [https://www.youtube.com/watch?v=T2uy3DejQYs](https://www.youtube.com/watch?v=T2uy3DejQYs)  
41. How to Use Cursor More Efficiently\! : r/ChatGPTCoding \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/ChatGPTCoding/comments/1hu276s/how\_to\_use\_cursor\_more\_efficiently/](https://www.reddit.com/r/ChatGPTCoding/comments/1hu276s/how_to_use_cursor_more_efficiently/)  
42. Share your "Rules for AI" \- Discussion \- Cursor \- Community Forum, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/share-your-rules-for-ai/2377](https://forum.cursor.com/t/share-your-rules-for-ai/2377)  
43. \[Guide\] A Simpler, More Autonomous AI Workflow for Cursor \- \#16 by Jarrodsz \- Showcase, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688/16](https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688/16)  
44. Introducing the Agile-AI Workflow (AIADD): A New Way to Build Complex Apps with Cursor, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/introducing-the-agile-ai-workflow-aiadd-a-new-way-to-build-complex-apps-with-cursor/76415](https://forum.cursor.com/t/introducing-the-agile-ai-workflow-aiadd-a-new-way-to-build-complex-apps-with-cursor/76415)  
45. Use Cursor to upgrade a 5-year-old Vue 2 project to Vue 3\. \- Feedback \- Cursor Forum, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/use-cursor-to-upgrade-a-5-year-old-vue-2-project-to-vue-3/52355](https://forum.cursor.com/t/use-cursor-to-upgrade-a-5-year-old-vue-2-project-to-vue-3/52355)  
46. Angular 19: Cursor.ai / Windsurf / ChatGPT / Claude? \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/angular/comments/1j3ucaa/angular\_19\_cursorai\_windsurf\_chatgpt\_claude/](https://www.reddit.com/r/angular/comments/1j3ucaa/angular_19_cursorai_windsurf_chatgpt_claude/)  
47. Best Cursor Workflow that no one talks about... \- YouTube, 访问时间为 四月 11, 2025， [https://www.youtube.com/watch?v=2PjmPU07KNs](https://www.youtube.com/watch?v=2PjmPU07KNs)  
48. Building an app with AI: V0 \+ Cursor AI \- WeAreBrain, 访问时间为 四月 11, 2025， [https://wearebrain.com/blog/building-an-app-with-ai-v0-cursor-ai/](https://wearebrain.com/blog/building-an-app-with-ai-v0-cursor-ai/)  
49. Has anyone started to use Cursor and AI to help with development work? \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/iOSProgramming/comments/1i6eaq8/has\_anyone\_started\_to\_use\_cursor\_and\_ai\_to\_help/](https://www.reddit.com/r/iOSProgramming/comments/1i6eaq8/has_anyone_started_to_use_cursor_and_ai_to_help/)  
50. Update on developing an iOS app with cursor ai (January 27 \- 2025\) : r/swift \- Reddit, 访问时间为 四月 11, 2025， [https://www.reddit.com/r/swift/comments/1ibbd48/update\_on\_developing\_an\_ios\_app\_with\_cursor\_ai/](https://www.reddit.com/r/swift/comments/1ibbd48/update_on_developing_an_ios_app_with_cursor_ai/)  
51. I want to develop an app, such as for Android or iOS. How can I use Cursor to develop it?, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/i-want-to-develop-an-app-such-as-for-android-or-ios-how-can-i-use-cursor-to-develop-it/40777](https://forum.cursor.com/t/i-want-to-develop-an-app-such-as-for-android-or-ios-how-can-i-use-cursor-to-develop-it/40777)  
52. Cursor AI vs. GitHub Copilot: Which One Wins? | by Cos | Feb, 2025 \- Medium, 访问时间为 四月 11, 2025， [https://cosminnovac.medium.com/cursor-ai-vs-github-copilot-which-one-wins-45ba5828741f](https://cosminnovac.medium.com/cursor-ai-vs-github-copilot-which-one-wins-45ba5828741f)  
53. Cursor vs Windsurf vs GitHub Copilot \- Builder.io, 访问时间为 四月 11, 2025， [https://www.builder.io/blog/cursor-vs-windsurf-vs-github-copilot](https://www.builder.io/blog/cursor-vs-windsurf-vs-github-copilot)  
54. Comparison of AI-assisted coding assistants and IDEs | Groupe Castelis, 访问时间为 四月 11, 2025， [https://www.castelis.com/en/news/custom-development/comparison-of-ai-assisted-coding-assistants-and-ides/](https://www.castelis.com/en/news/custom-development/comparison-of-ai-assisted-coding-assistants-and-ides/)  
55. Compare \- Sourcegraph, 访问时间为 四月 11, 2025， [https://sourcegraph.com/compare](https://sourcegraph.com/compare)  
56. 17 Best AI-Powered Coding Assistant Tools in 2025 \- Spacelift, 访问时间为 四月 11, 2025， [https://spacelift.io/blog/ai-coding-assistant-tools](https://spacelift.io/blog/ai-coding-assistant-tools)  
57. Cursor AI Editor — Is It Actually Useful? \- DEV Community, 访问时间为 四月 11, 2025， [https://dev.to/best\_codes/cursor-ai-editor-is-it-actually-useful-16mj](https://dev.to/best_codes/cursor-ai-editor-is-it-actually-useful-16mj)  
58. Cursor vs GitHub Copilot \- Which One Is Better for Engineers? \- Zencoder, 访问时间为 四月 11, 2025， [https://zencoder.ai/blog/cursor-vs-copilot](https://zencoder.ai/blog/cursor-vs-copilot)  
59. Compare Cursor vs. GitHub Copilot vs. Tabnine in 2025 \- Slashdot, 访问时间为 四月 11, 2025， [https://slashdot.org/software/comparison/Cursor-vs-GitHub-Copilot-vs-Tabnine/](https://slashdot.org/software/comparison/Cursor-vs-GitHub-Copilot-vs-Tabnine/)  
60. Anyone else trying different things but Cursor still is the best?, 访问时间为 四月 11, 2025， [https://forum.cursor.com/t/anyone-else-trying-different-things-but-cursor-still-is-the-best/2310](https://forum.cursor.com/t/anyone-else-trying-different-things-but-cursor-still-is-the-best/2310)  
61. Compare Codeium vs. Cursor in 2025 \- Slashdot, 访问时间为 四月 11, 2025， [https://slashdot.org/software/comparison/Codeium-vs-Cursor/](https://slashdot.org/software/comparison/Codeium-vs-Cursor/)  
62. Design Engineering with Cursor AI for Product Designers \- \#UXLivestream and Q\&A, 访问时间为 四月 11, 2025， [https://www.youtube.com/watch?v=oy8QSO0U1D0](https://www.youtube.com/watch?v=oy8QSO0U1D0)  
63. Cursor AI Tutorial for Beginners \[2025 Edition\] \- YouTube, 访问时间为 四月 11, 2025， [https://www.youtube.com/watch?v=3289vhOUdKA](https://www.youtube.com/watch?v=3289vhOUdKA)  
64. Using Cursor AI for Cross-Platform Mobile App Development \- Slashdev, 访问时间为 四月 11, 2025， [https://slashdev.io/-using-cursor-ai-for-cross-platform-mobile-app-development](https://slashdev.io/-using-cursor-ai-for-cross-platform-mobile-app-development)
