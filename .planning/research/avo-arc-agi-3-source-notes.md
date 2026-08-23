# NVIDIA AVO × ARC-AGI-3 一手资料研究笔记

> 研究日期：2026-08-23  
> 用途：为技术博客提供事实底稿与独特论点，不作为文章正文。  
> 来源范围：NVIDIA、ARC Prize、Anthropic 的官方页面/论文/文档，以及项目作者发布的论文与项目页。

## 结论先行

NVIDIA 公布的核心数字可以确认：AVO 配合 Claude Opus 5，在 ARC-AGI-3 的 **25 个公开演示环境（Public Demo）** 中完成 **183/183 关**，得到 **100.00 RHAE**，共使用 **6,624 次环境动作**；NVIDIA 用同模型的 VISTA 结果（7,542 次）作参照，称动作数少约 12%。

但这组结果不能被写成“AVO 清空 ARC-AGI-3”或“证明 harness 已超过模型 scaling”：

- 它只覆盖 public demo，不是 55 个 semi-private 或 55 个 fully private 环境，也不是 ARC Prize 竞赛成绩。
- ARC Prize 官方技术报告明确说，公开集仅用于展示格式，公开集成绩“强调地不是”衡量 AGI 进展的有效指标；官方榜单还刻意排除 task/domain-specific harness。
- NVIDIA 自己声明 30.16% 模型基线到 100% AVO 不是受控消融：reasoning setting、观察表示、记忆、上下文管理和评估设置都不同，无法把 69.84 个百分点归因给 AVO 的任何单一组件。
- RHAE 只计算对环境造成状态变化的动作；内部推理、只读工具调用和重试不计。因此“少 12% 动作”不等于少 12% token、时间、美元或能耗。
- “没有规则或关卡目标描述”成立；“无需任何额外指令/明确目标”不成立或至少未被证实。AVO 没有公开精确 prompt，而 ARC 官方统一 prompt 明确告诉模型目标是赢；VISTA 也公开了“用尽可能少的动作完成游戏”的任务提示。
- AVO 不是首个公开集满分系统。Tycho 的论文（2026-07-30 提交）和 VISTA 项目（2026-08-05 发布）均早于 NVIDIA 2026-08-21 的博客报告公开集 100.00。
- 截至 2026-08-23，ARC Prize Community Leaderboard 未列出 AVO，也未找到 NVIDIA 公开的 AVO scorecard URL 或完整 replay。因此 100.00/6,624 应表述为“NVIDIA 报告”，而不是“ARC Prize 已独立验证”。

最值得写的，不是“又一个满分”，而是一个更尖锐的命题：**AVO 暴露了两种完全不同的智能评价对象——产品世界需要评价完整 agent system，而 AGI 基准试图隔离模型在未知分布上的适应能力。两者都合理，却不能用同一分数互相替代。**

## 事实核验表

| 说法 | 判定 | 证据与限定 |
|---|---|---|
| AVO 在 ARC-AGI-3 上得 100% | 部分成立，需改写 | NVIDIA 报告的是 25 个 **public demo** 环境的 100.00 RHAE，不是 semi-private/private。官方技术报告把 public demo 定义为展示集。 |
| 100% 等于完成 183 关 | 成立 | NVIDIA 报告 25 个公开环境、183/183 levels、6,624 actions。注意是 183 关，不是 183 个环境。 |
| 动作效率比 VISTA 高 | 成立但不是受控对比 | 6,624 对 7,542，按总动作约少 12.17%。NVIDIA 明确说两者在 backend、观察表示、记忆和上下文管理等方面不同。 |
| Claude Opus 5 从约 30% 被 AVO 拉到 100% | 数字存在，因果未证实 | ARC Prize 的标准模型评估是 30.16%（High）；AVO 使用不同 reasoning setting 和完整 agent system。NVIDIA明确禁止将其解释为 AVO 贡献的直接测量。 |
| 无需额外指令、规则或明确目标 | 容易误导 | 只证实 agent 没收到每个游戏的规则或胜利条件描述。AVO 精确 prompt 未公开；ARC 官方统一 prompt 明说“You are playing a game. Your goal is to win”；VISTA 也有明确任务提示。 |
| 证明 agent 架构已超过模型参数规模 | 未证实 | 没有相同模型、相同 effort、相同输入表示、相同预算下逐组件 ablation，也没有参数规模变量。最多能说：模型分数不足以预测完整 agent system 的表现。 |
| 这是 ARC-AGI-3 的首次满分 | 错误 | Tycho 与 VISTA 均已更早公布公开集 100.00；NVIDIA 文章也没有声称“首次”。 |
| 100 RHAE 说明总体计算效率达到人类水平 | 错误 | RHAE 不计算内部 reasoning、read-only inspections、tool calls 或 retries；它只度量环境动作效率。 |
| ARC Prize 已独立验证 AVO 满分 | 未证实 | 当前直接证据是 NVIDIA 技术博客；ARC Community Leaderboard 未列 AVO，NVIDIA 也没有公开可直接访问的 AVO scorecard/replay。 |

## 一、AVO 到底是什么：不是“多写几轮 Prompt”，而是把变异算子改造成 Agent

AVO 的原始论文把它定义为 **Agentic Variation Operators**：传统演化搜索把 LLM 限制在一次性的候选生成步骤，而采样、评估、种群管理和调用顺序由固定框架决定；AVO 则让 agent 接管整个 `Vary` 操作。

论文的形式化表达是：

```text
传统：Vary(P_t) = Generate(Sample(P_t))
AVO：Vary(P_t) = Agent(P_t, K, f)
```

其中：

- `P_t` 是历史候选及评分构成的完整 lineage；
- `K` 是领域知识库；
- `f` 是可执行的评分函数；
- agent 自己决定查什么、改什么、何时测试、失败后如何修复。

这意味着 AVO 的关键不是“生成能力更强”，而是把一次模型调用改造成一个有状态的控制系统：

1. **可持久化谱系**：成功候选、分数和证据不会随上下文结束而消失。
2. **基于真实执行的闭环**：编译器、测试、profiler 或环境转移充当外部真值，不让自然语言自评成为终点。
3. **单调提交门**：内核实验中，只有通过正确性检查且不劣于当前最佳分数的版本才进入 committed lineage。
4. **停滞监控**：supervisor 检测 plateau 或重复失败循环，并改变探索方向；它不是简单地“再试一次”。
5. **内部失败不污染主线**：失败尝试保留在搜索轨迹中用于学习，但不会被提升为新的基线。

在 GPU 内核实验中，AVO 连续运行 7 天，探索 500 多个优化方向，提交 40 个版本；在 B200 上，论文报告 MHA 最多超过 cuDNN 3.5%、超过 FlashAttention-4 10.5%。这些是明确实验设置下的峰值提升，不应外推到所有 shape、硬件或 attention workload。

### 一个更准确的类比：模型是乱序执行核心，Harness 是操作系统加事务层

把 harness 叫“脚手架”容易低估它。AVO 更像：

- 模型提供局部推理与候选动作，类似 CPU 执行单元；
- memory/lineage 提供耐久状态，类似日志与存储；
- tools 把推理连接到真实世界 I/O；
- evaluator 是提交前的一致性检查；
- supervisor 是 watchdog/scheduler；
- commit gate 则像事务提交。

单次模型推理仍可能错，但系统通过“证据—状态—恢复—再执行”把局部不可靠性转化为较可靠的长程过程。这是 AVO 对 coding agent 最有价值的底层启示。

## 二、ARC-AGI-3 测的不是静态答题，而是交互中的技能获取效率

ARC-AGI-3 把测试从静态输入输出网格改成无自然语言规则的回合制环境。Agent 必须通过动作完成四类工作：

1. exploration：主动取得信息；
2. modeling：把观察转成可预测后果的世界模型；
3. goal-setting：从环境线索中发现值得追求的状态；
4. planning and execution：规划并在反馈变化时修正。

每个环境由至少六个逐步变难的 level 组成，后续关卡要求复用和组合前面学到的机制。因此，这个基准确实比“一次性猜答案”更适合观察记忆、反事实更新和长程执行。

### RHAE 真正计算什么

ARC-AGI-3 使用 Relative Human Action Efficiency：

```text
level_score = (human_baseline_actions / ai_actions) ^ 2
```

单关最高封顶为 1.15；后面的关卡权重更高；只有完成所有关卡才能解锁单个游戏的 100% 上限。人类基线来自第一次接触游戏的受控测试者，以每关上中位数（upper median）动作数为基准。

关键盲点是：**内部 reasoning、tool calls、只读检查与 retry 不属于 action。** 因此 RHAE 在“现实动作昂贵或危险”的机器人/运维场景很有意义，却没有衡量 agent 为减少外部动作付出的全部推理成本。

技术博客应明确区分四个效率指标：

| 指标 | AVO 公布了吗 | 含义 |
|---|---:|---|
| 环境动作数 | 是：6,624 | 对游戏状态产生影响的动作 |
| 模型 token / tool calls | 否 | 推理与检查成本 |
| wall-clock latency | 未公布完整公开集 | 用户等待时间 |
| 美元/能耗 | 否 | 商业与基础设施成本 |

## 三、NVIDIA 的 ARC 结果：哪些已知，哪些仍是黑箱

### 已知

- 基础模型：Claude Opus 5。
- 输入表示：精确的 64×64 文本网格；不向模型发送图像或 image token。
- Agent 获得可用动作，但没有每个游戏的规则或目标描述，必须由交互推断其效果。
- 设计路线：借鉴 VISTA 的直接交互思路，不显式构造 ARC 专用的可执行 world model。
- 结果：25/25 public environments，183/183 levels，100.00 RHAE，6,624 environment actions。
- 对比：VISTA + Opus 5 为 7,542 actions，AVO 少约 12%。

### 未公开或无法独立确认

- AVO 在 ARC 运行中的精确 system/user prompt。
- Opus 5 的具体 reasoning effort；文章只说与 ARC Prize 的 High baseline 不同。
- token、API 成本、总工具调用、重试次数、wall-clock 时间和运行方差。
- memory 的数据结构、写入/淘汰策略、supervisor 的触发阈值和干预 prompt。
- 多次独立重复运行的均值、方差与最差结果。
- 相同设置下逐项关闭 memory、supervisor、context recovery、文本表示等组件的 ablation。
- 可复现的 AVO ARC 源码、完整运行日志和博客中可直接访问的具体 scorecard URL。

因此，当前证据等级是 **NVIDIA 一手结果声明 + 官方基准定义**，而不是独立复现实验。

## 四、最重要的反方证据：ARC 官方并不把这种公开集 Harness 满分当作 AGI 进展

ARC-AGI-3 的数据划分是：

| 集合 | 环境数 | 官方目的 |
|---|---:|---|
| Public Demo | 25 | 展示格式和基本机制，刻意更容易 |
| Semi-Private | 55 | 测试 API 后面的 frontier models |
| Fully Private | 55 | 正式竞赛，严格保密 |

官方技术报告说，public set 不全面代表 private mechanics，并且 private set 明显更难、相对 public 刻意 OOD。报告进一步指出：

- 公开集无法排除人工调参、查看 replay、工具选择和定向优化；
- 专为 ARC-AGI-3 设计的 harness 可能提升已见任务成绩，却不改善跨领域一般能力；
- 所以官方 leaderboard 不用 harness 报告模型成绩，public 分数也不会用于官方榜单。

这与 NVIDIA 的产品工程视角并不矛盾，而是测量目标不同：

- **ARC 官方问题**：一个通用模型首次面对未见分布时，自身能多快学会？
- **NVIDIA/产品问题**：给定一个强模型，完整系统能否可靠完成长程任务？

博客最独特的判断应是：**AVO 的 100 分不是 AGI 宣言，而是一次“评价对象切换”——从 model capability 切到 system capability。**

## 五、不能从 30.16% → 100% 推导“Harness 贡献 69.84 个百分点”

ARC Prize 对 Claude Opus 5 的官方结果为 30.16%（High effort）。NVIDIA 的 AVO 为 100.00，但 NVIDIA 同时明确说明：

- reasoning setting 不同；
- agent backend 不同；
- observation representation 不同；
- memory/context management 不同；
- evaluation setup 不同。

这不是受控 ablation，所以只能支持：

> 同一个模型名称，在不同完整系统中可能表现悬殊；model-only score 不能完整预测 agent-system score。

它不能支持：

> memory 单独贡献了多少；supervisor 单独贡献了多少；harness 比换更大的模型更有效；模型参数不再重要。

Anthropic 官方资料还显示，Opus 5 本身就是针对 agentic/long-horizon 任务显著增强的模型，拥有 1M context、默认 thinking、可调 effort，并强化工具循环和自我验证。AVO 的成功应理解为 **强模型 × 强系统的乘法效应**，而不是 harness 对模型能力的替代。

## 六、对行业与 AI 深度使用者的影响

### 1. Agent 竞争的护城河从模型 API 转向“轨迹资产”

当不同团队都能调用同一 frontier model，差异化来自：

- 哪些证据被写入 durable memory；
- 如何从失败轨迹提炼下一步实验；
- 哪些工具能产生可信反馈；
- 何时 checkpoint、rollback 或换方向；
- 如何量化停滞与重复劳动。

这些运行轨迹、状态 schema、验证器与工具适配器会成为比 prompt 模板更难复制的资产。

### 2. “更长上下文”不等于“更好的记忆”

上下文窗口只是可读取历史的容量；可靠记忆还需要选择、验证、版本化与恢复。把所有历史塞进上下文，会混合过期假设、失败方案和正确结论。AVO 的 lineage/commit 思路更接近证据化记忆：只有通过 gate 的状态才成为后续工作的稳定基线。

### 3. Agent eval 必须从单分数升级为二维预算

ARC 的环境动作预算适合衡量探索风险，但生产系统还必须同时报告：

- 外部动作与副作用；
- token 和模型调用；
- wall-clock；
- 工具/计算费用；
- 成功率与运行方差；
- 人工介入次数；
- 恢复后是否保持正确状态。

否则一个系统可能“少按了几次按钮”，却用数十倍 token 和时间完成任务。

### 4. 对 coding agent，核心能力从“生成补丁”转向“维持可验证进展”

可直接借鉴的最小 AVO 化设计：

```text
任务契约
  ↓
证据/假设/未决问题账本
  ↓
选择下一项最有信息量的实验
  ↓
编辑 → 测试/benchmark → 解释结果
  ↓
通过 gate 才 checkpoint
  ↓
停滞 watchdog：换假设、回到旧 checkpoint 或请求人工判断
```

建议具体实现：

- 将“已验证事实、当前假设、反证、下一实验”分栏保存，避免摘要把猜测固化成事实。
- 每个 checkpoint 绑定测试输出、benchmark、环境版本和模型配置。
- supervisor 只负责检测停滞和提出分支，不拥有绕过测试或扩大权限的能力。
- context rollover 时生成可审计的 continuation state，并从外部证据恢复，而不是只相信模型摘要。
- 用同一模型做 harness component ablation，至少比较 `memory on/off`、`supervisor on/off`、`resume on/off`。

### 5. 长程自治也放大安全风险

AVO 式 persistence 与 supervisor 会让错误同样产生复利：被污染的记忆可能跨上下文存活，错误 evaluator 可能持续奖励危险行为，supervisor 可能把“没进展”误判为“需要更大权限”。生产应用需要：

- 工具最小权限和沙箱；
- 不可逆动作的人类审批；
- memory 来源与版本追踪；
- evaluator 与执行器分权；
- 明确的预算和停机条件；
- 可回放、可审计的动作链。

## 七、建议文章采用的独特论点

### 主论点：AVO 的真正突破不是 100 分，而是把“智能”从瞬时回答改写成可积累的系统状态

模型参数扩大主要提高单次推理分布；AVO 的系统设计提高跨时间保存、纠错和复用有效推理的概率。它优化的不是某个 token，而是整个轨迹的状态转移。

### 反直觉论点一：这次结果同时证明了 Harness 的价值，也证明了公开基准容易被 Harness 改写

如果评价对象是产品，100 分说明系统工程非常有价值；如果评价对象是未知分布上的一般智能，公开集 harness 满分恰恰提醒我们不能把 public benchmark 当作终点。

### 反直觉论点二：AVO 的优势更像“减少重复探索”，而不一定是“更聪明”

NVIDIA 推测持久记忆减少了重复探索，但没有隔离该变量。即使未来 ablation 证实这一点，它说明的也是信息保存效率提高，而不是底层模型获得了新的抽象推理能力。

### 反直觉论点三：Agentic scaling 与 parameter scaling 是正交轴，不是替代关系

更强模型提高每一步的决策质量；更强 harness 提高错误恢复、证据积累和长期一致性。当前证据支持乘法关系，不支持“谁已经超过谁”。

### 可以使用的标题方向

1. **《AVO 满分之后：当 Harness 成为 AI 的操作系统，我们究竟在测模型还是系统？》**
2. **《从 30% 到 100% 不是一条因果曲线：拆解 NVIDIA AVO 的成绩、盲点与真正价值》**
3. **《模型负责聪明一秒，Harness 负责把这一秒保存七天》**
4. **《ARC-AGI-3 公共集满分的悖论：Agent 工程越成功，AGI 基准越需要隐藏》**

## 一手来源

1. [NVIDIA Technical Blog — NVIDIA AVO Reaches 100% on ARC-AGI-3](https://developer.nvidia.com/blog/nvidia-avo-reaches-100-on-arc-agi-3-demonstrating-a-frontier-level-general-purpose-architecture-for-long-horizon-autonomous-agents/)（2026-08-21；AVO 架构、6,624 actions、公开集范围、非受控对比声明）
2. [AVO: Agentic Variation Operators for Autonomous Evolutionary Search — arXiv HTML](https://arxiv.org/html/2603.24517v1)（AVO 的形式化、lineage、commit gate、supervisor、GPU 实验）
3. [ARC-AGI-3 Technical Report — ARC Prize Foundation PDF](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)（数据集划分、公开集限制、官方榜单政策、统一 prompt）
4. [ARC-AGI-3 Scoring Methodology — 官方文档](https://docs.arcprize.org/methodology)（RHAE 公式、动作定义、权重和封顶）
5. [Claude Opus 5 — ARC Prize 官方模型结果](https://arcprize.org/results/anthropic-claude-opus-5)（High effort 30.16%）
6. [Anthropic — Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)（模型发布与 agentic/long-horizon 能力声明）
7. [Anthropic Platform Docs — What’s new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5)（1M context、effort、thinking、tooling 行为）
8. [VISTA 官方项目页](https://vista-research.github.io/)（公开 prompt、7,542 actions、只计算环境动作）
9. [Tycho 论文](https://arxiv.org/abs/2607.28287) 与 [官方 GitHub](https://github.com/NIMI-research/Tycho/)（更早的公开集 100.00 结果与可复现 artifacts）
10. [Tycho 的 ARC Prize scorecard](https://arcprize.org/scorecards/08b98aa0-5df0-42c0-b501-856f553a21e9)（交叉确认公开集 25 environments / 183 levels；该链接不是 AVO 的 scorecard）

## 写作时应避免的句式

- 避免：“AVO 在 ARC-AGI-3 上取得满分。”  
  改为：“AVO 在 ARC-AGI-3 的 25 个公开演示环境上取得 100.00 RHAE。”
- 避免：“没有任何指令和目标。”  
  改为：“没有每个游戏的规则与胜利条件描述；精确 AVO prompt 未公开。”
- 避免：“AVO 将 Opus 5 从 30% 提升到 100%。”  
  改为：“同一模型家族在两种不可直接比较的系统设置中分别报告约 30% 和 100%。”
- 避免：“动作减少 12%，所以成本下降 12%。”  
  改为：“计分环境动作减少约 12%；token、时间和美元成本未披露。”
- 避免：“证明 harness 比模型 scaling 更重要。”  
  改为：“证明 model-only 评估不足以描述完整 agent system；两种 scaling 的相对贡献仍需受控实验。”
