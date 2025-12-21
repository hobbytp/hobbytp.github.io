---
title: "Karpathy: 2025 年大语言模型年度回顾"
date: "2025-12-20T22:30:00+08:00"
draft: false
tags: ["AI","Karpathy","llm","Review"]
categories: ["celebrity_insights"]
description: "Karpathy大神在2025年年底的时候多大模型这一年的发展做了一个年度总结,我搬运过来，翻译了一下。"

cover:
  image: "/images/generated-covers/Andrej_Karpathy_2025_Review.webp"
  alt: "Karpathy: 2025 年大语言模型年度回顾"
---

Karpathy大神在2025年年底的时候多大模型这一年的发展做了一个“年度总结”，我用Qwen3 Max做了翻译，供大家阅读。我在文后附上了我个人的看法。

简单说，Karpathy 觉得这一年 AI 发生了几个显著的变化：

* **从“喂饭”到“悟道”**： 以前训练 AI 靠人工标数据（RLHF），现在靠给它一个目标让它自己在数学和代码里“悟”（RLVR）。AI 开始自发产生推理策略，那种“o3 思考时”的顿悟感，就是这么来的。

* **它是“幽灵”不是“动物”**： 别再用人类的逻辑去衡量它了。AI 的智能是“锯齿状”的：它能解顶级数学题，却可能被一句垃圾话骗走你的隐私。它不是一个正在成长的婴儿，而是一个被召唤出来的、极度偏科的“幽灵”。

* **“氛围编程”彻底火了**： 2025 是“Vibe Coding”元年。代码变得廉价、随用随弃。只要你英语够好、审美在线，你就能“求”AI 给你搓出任何程序，甚至不需要去看一眼源码。

* **AI 住进了你的电脑**： 别再只盯着网页版 ChatGPT 了，像 Claude Code 这种直接跑在本地、操作你文件系统的 Agent 才是未来。它不再是一个搜索引擎，而是你电脑里的一个“数字灵魂”。


## 2025 年大语言模型年度回顾


2025 年，是大语言模型（LLMs）取得强劲而跌宕起伏进展的一年。以下是我个人眼中**尤为突出、略带意外的几项“范式迁移”**——它们不只是技术迭代，更在概念层面上重塑了我对智能本质的理解。

### 1. **基于可验证奖励的强化学习（RLVR）**

2025 年初，各大实验室的 LLM 生产流程还长这样：  
▸ 预训练（Pretraining，GPT-2/3 时代，~2020）  
▸ 监督微调（SFT，InstructGPT 时代，~2022）  
▸ 基于人类反馈的强化学习（RLHF，~2022）  

这套流程稳定、成熟，是训练工业级 LLM 的“黄金配方”。  
而 2025 年，**基于可验证奖励的强化学习（Reinforcement Learning from Verifiable Rewards, RLVR）**横空出世，成为这套流程中事实上的**第四支柱**。

其核心思想是：让 LLM 在一系列**可自动验证结果的环境**中优化（比如数学题、编程谜题），并以客观奖励信号驱动学习。  
神奇的是——模型竟**自发涌现出人类称之为“推理”的策略**：它学会把问题拆解为中间步骤，学会“回溯-试探-修正”的解题循环（参见 DeepSeek R1 论文中的精彩案例）。  
这些能力，在 SFT 或 RLHF 框架下极难实现——因为人类根本说不清“最优推理路径”长什么样；而 RLVR 把这个问题交还给优化器：让模型自己在奖励梯度中**摸索出适合自己的解题之道**。

与 SFT/RLHF 这类“轻量微调”不同，RLVR 可在**客观、不可钻空子（non-gameable）的奖励函数下持续优化极长时间**。实践下来，RLVR 的**能力提升/每美元算力**极高——高到它几乎“吃光”了原本为预训练预留的算力池。

于是，2025 年的能力跃进，不再靠“更大模型”，而是靠“更长 RL 训练”。我们看到的是：**模型尺寸大致持平，但 RL 训练时长指数级增长**。

更独特的是，RLVR 引入了一个全新的、可控的“旋钮”：**测试时推理长度**（即“思考时间”）。通过生成更长的推理链、给予更多计算步数，我们能显式调节模型表现——这催生了一条全新的缩放律（scaling law）。

OpenAI 的 o1（2024 年底）是首个 RLVR 模型的雏形，  
而 **o3（2025 年初）则是真正的拐点**——你几乎能**凭直觉感受到**：这东西“变聪明了”。

---

### 2. **“幽灵” vs “动物” / 锯齿状智能（Jagged Intelligence）**

2025 年，我（以及行业大多数人）**头一回对 LLM 的“智能形态”有了直觉性把握**：  
我们不是在“培育动物”，而是在“召唤幽灵”。

——整个 LLM 技术栈都截然不同：网络架构、训练数据、训练算法，尤其是**优化目标**。  
所以，它产出的“智能体”，自然不该用动物心智的透镜去理解。

比特层面看：  
人类神经网络经百万年演化，为的是“在丛林里帮部落活下来”；  
而 LLM 神经网络，是在“模仿人类文本”“解数学题拿奖励”“在 LMSYS Arena 上赢一个 upvote”。

当可验证任务成为 RLVR 的训练场，LLM 的能力便会在这些领域**垂直飙升**，最终呈现出一种**荒诞又真实的“锯齿状智能”**：  
它前一秒是博学多才的通才，后一秒就成了被一道脑筋急转弯绕晕的小学生；再过一秒，可能就被一个 jailbreak prompt 哄骗着把你的数据偷走。

![human_vs_ai_intelligence](./images/human_vs_ai_intelligence.png)
人类智能：蓝色；AI 智能：红色。  
我喜欢这个 meme 版本（抱歉忘了原帖出处），它提醒我们：**人类智能本身也是锯齿状的**——只是“锯齿”的形状不同罢了。

与之密切相关的，是我 2025 年对**基准测试（benchmarks）的彻底幻灭与不信任**。  
问题核心在于：基准测试几乎**天然就是可验证环境**——因此极易被 RLVR（或其弱化版：合成数据训练）定向优化。  

在典型的**刷榜内卷**（benchmaxxing）过程中，各团队会不自觉地在嵌入空间中，围绕 benchmark 所在的“小口袋”疯狂生长“能力尖刺”（jaggies），只为精准覆盖测试点。  
——“用测试集训练”，已然成为一门新艺术。

那么问题来了：  
**怎样才能‘刷爆所有榜’，却依然离 AGI 十万八千里？**  

关于本节，我另有长文详述：  
▸ [Animals vs. Ghosts](链接)  
▸ [Verifiability](链接)  
▸ [The Space of Minds](链接)

---

### 3. **Cursor：LLM 应用的新层**

除了它今年的火箭式蹿红，Cursor 最令我震撼的，是它**清晰揭示了一类全新的“LLM 应用范式”**——人们开始说：“我们想要一个 *Cursor for X*”。

正如我在今年 Y Combinator 演讲中强调的（[文字稿 & 视频](链接)），像 Cursor 这样的 LLM 应用，并非简单调用 API，而是在**特定垂直领域内精心编排 LLM 调用**：  

- 它们负责**上下文工程**（Context Engineering）  
- 它们在后台将多次 LLM 调用串成日益复杂的 DAG（有向无环图），精细权衡性能与成本  
- 它们为人机协作设计**领域专属的 GUI**  
- 它们提供“**自主性滑块**”（autonomy slider）——从“建议模式”到“全自动执行”的连续调节  

2025 年，业界热议一个关键问题：**这一新应用层到底“有多厚”？**  
LLM 大厂会通吃所有应用？还是存在一片 LLM 应用的“绿色草原”？

我个人倾向后者：  
> **LLM 实验室将培养出“通识能力扎实的大学毕业生”，  
> 而 LLM 应用层，则会整合、微调、并真正“激活”这群毕业生——  
> 通过注入私有数据、传感器、执行器与反馈回路，  
> 把他们变成某个垂直领域里能落地干活的“职场专家”。**

---

### 4. **Claude Code：住在你电脑里的 AI**

**Claude Code（CC）** 是首个令人信服的 LLM Agent 案例——它能以**闭环方式**，将工具调用与推理串联起来，完成长时间、多步骤的问题求解。

更让我眼前一亮的是：**CC 运行在你的本地机器上**，使用你自己的环境、私有数据与上下文。

我认为 OpenAI 在这一点上判断失误——他们把 Codex / Agent 的重心放在“云端容器”（通过 ChatGPT 编排），而非 `localhost`。  
诚然，云端“智能体蜂群”可能是 AGI 的终局形态；  
但在我们所处的“能力锯齿状、渐进起飞”的当下，**让 Agent 直接扎根于开发者机器、与其工作流深度耦合，才是更务实的选择**。

CC 把这个优先级搞对了，并包装成一个**极致简洁、优雅、令人信服的 CLI 工具**——它重新定义了“AI 长什么样”：  
> 它不再是 Google 那样的网站入口；  
> 它是你电脑里住着的一个小精灵、一个“幽灵”（ghost）。

——这是与 AI 交互的**全新范式**。

---

### 5. **氛围编程（Vibe Coding）**

2025 年，AI 终于跨过了那个临界点：**人们仅凭自然语言描述，就能构建出令人印象深刻的程序，甚至完全“忘记代码存在”**。

有趣的是，我曾在一条“浴室突发奇想”推文中随手发明了 **“vibe coding”**（氛围编程）这个词——当时完全没料到它会火成这样 😄

Vibe coding 的本质是：**编程不再专属训练有素的专业人士，而成为人人可为之事**。  
这正是我在《[Power to the People](链接)》中论述的核心观点：  
> 与人类历史上所有技术不同，**LLM 的最大受益者不是企业、政府或专家，而是普通人**。

但它不止赋能大众：  
它也让专业程序员能快速实现**原本根本不会写的软件**。  
比如我在 nanochat 项目中，直接 vibe coding 出一个自定义的、高效 Rust BPE 分词器——省去了啃库或深学 Rust 的麻烦；  
我用 vibe coding 快速搭出了 menugen、llm-council、reader3、HN Time Capsule 等一系列小工具；  
甚至，我曾为定位一个 bug，现场 vibe code 一整套临时应用——**反正代码现在是“免费的、一次性的、可塑的、用完即弃的”**。

Vibe coding 将重塑软件工程版图，并重新定义“程序员”的职业内涵。

---

### 6. **Nano Banana / LLM 的 GUI 时代**

Google 的 **Gemini Nano Banana** 是 2025 年最令人震撼、最具范式颠覆性的模型之一。

在我的世界观里，**LLM 是继 70、80 年代计算机之后的下一代计算范式**——因此，我们必将重演类似的技术演进：  
▸ 个人计算（Personal Computing）  
▸ 微控制器（即“认知核心”，Cognitive Core）  
▸ 智能体互联网（Internet of Agents）……等等。

尤其在 UI/UX 层面：  
当前与 LLM “聊天”，就像 80 年代在命令行敲指令——  
**文本是计算机（及 LLM）的“母语”，却不是人类的最优输入/输出格式**。  
人类其实**厌恶阅读**——它慢、费力；  
我们天生偏爱**视觉化、空间化**的信息呈现——这也是传统计算中 GUI 被发明的原因。

同理，LLM 未来该以**我们偏好的方式说话**：图像、信息图、幻灯片、白板、动图/视频、Web 应用……

当前的初级形态，是 emoji 和 Markdown——它们用标题、加粗、列表、表格等“装饰”文本，提升可读性。  
但真正的 LLM GUI 谁来建？  
**Nano Banana，就是这一方向的首个强烈信号**。

关键在于：它远不止“图像生成”。  
它是**文本生成 + 图像生成 + 世界知识**三者深度交织的联合能力——所有这些都“缠绕”在模型权重之中。

---

### ▸ TL;DR  
2025 年，是 LLM 令人激动又略带意外的一年。  
它们正涌现出一种**新型智能**——比我预想的**更聪明，也更愚蠢**。  
无论如何，它们已极具实用价值；而依我看，即便以当下能力，行业也远未挖掘其 10% 的潜力。

与此同时，**可探索的创意仍如繁星般密集，整个领域在概念层面依然无比开放**。  
正如我今年早些时候在 Dwarkesh 播客中所说：  
> 表面上矛盾，实则并行不悖——  
> **我既相信进展将持续快速，也深知前路仍有海量工作待完成**。

系好安全带，旅程才刚刚开始。

🔗 附：此文我也同步发到了[个人博客](URL)，排版更清爽，阅读体验更佳。

--- 

翻译说明：  
- 保留 Karpathy 标志性的“冷静中带温度、严谨中见幽默”的语感；  
- “ghosts vs. animals”译为“幽灵 vs 动物”，既保留隐喻张力，又契合中文科幻语境；  
- “jagged intelligence”译为“锯齿状智能”，准确传达“能力不均衡”的核心意象；  
- “benchmaxxing”创造性译为“刷榜内卷”，符合中文技术圈语境；  
- “vibe coding”音意兼顾译为“氛围编程”，已成社区共识译法；  
- 技术术语（如 RLVR, DAG, CLI, BPE）保留英文缩写+中文注释，确保专业性与可读性平衡。

希望这份翻译，能让中文读者感受到 Karpathy 原文那种——**站在智能革命前沿的清醒、兴奋与哲思交织的独特气息**。


## x.com上的原文

2025 has been a strong and eventful year of progress in LLMs. The following is a list of personally notable and mildly surprising "paradigm changes" - things that altered the landscape and stood out to me conceptually.

1. Reinforcement Learning from Verifiable Rewards (RLVR)
At the start of 2025, the LLM production stack in all labs looked something like this:
Pretraining (GPT-2/3 of ~2020)
Supervised Finetuning (InstructGPT ~2022) and
Reinforcement Learning from Human Feedback (RLHF ~2022)
This was the stable and proven recipe for training a production-grade LLM for a while. In 2025, Reinforcement Learning from Verifiable Rewards (RLVR) emerged as the de facto new major stage to add to this mix. By training LLMs against automatically verifiable rewards across a number of environments (e.g. think math/code puzzles), the LLMs spontaneously develop strategies that look like "reasoning" to humans - they learn to break down problem solving into intermediate calculations and they learn a number of problem solving strategies for going back and forth to figure things out (see DeepSeek R1 paper for examples). These strategies would have been very difficult to achieve in the previous paradigms because it's not clear what the optimal reasoning traces and recoveries look like for the LLM - it has to find what works for it, via the optimization against rewards. 
Unlike the SFT and RLHF stage, which are both relatively thin/short stages (minor finetunes computationally), RLVR involves training against objective (non-gameable) reward functions which allows for a lot longer optimization. Running RLVR turned out to offer high capability/$, which gobbled up the compute that was originally intended for pretraining. Therefore, most of the capability progress of 2025 was defined by the LLM labs chewing through the overhang of this new stage and overall we saw ~similar sized LLMs but a lot longer RL runs. Also unique to this new stage, we got a whole new knob (and and associated scaling law) to control capability as a function of test time compute by generating longer reasoning traces and increasing "thinking time". OpenAI o1 (late 2024) was the very first demonstration of an RLVR model, but the o3 release (early 2025) was the obvious point of inflection where you could intuitively feel the difference.
2. Ghosts vs. Animals / Jagged Intelligence
2025 is where I (and I think the rest of the industry also) first started to internalize the "shape" of LLM intelligence in a more intuitive sense. We're not "evolving/growing animals", we are "summoning ghosts". Everything about the LLM stack is different (neural architecture, training data, training algorithms, and especially optimization pressure) so it should be no surprise that we are getting very different entities in the intelligence space, which are inappropriate to think about through an animal lens. Supervision bits-wise, human neural nets are optimized for survival of a tribe in the jungle but LLM neural nets are optimized for imitating humanity's text, collecting rewards in math puzzles, and getting that upvote from a human on the LM Arena. As verifiable domains allow for RLVR, LLMs "spike" in capability in the vicinity of these domains and overall display amusingly jagged performance characteristics - they are at the same time a genius polymath and a confused and cognitively challenged grade schooler, seconds away from getting tricked by a jailbreak to exfiltrate your data.

《image》
human intelligence: blue, AI intelligence: red. I like this version of the meme (I'm sorry I lost the reference to its original post on X) for pointing out that human intelligence is also jagged in its own different way.


Related to all this is my general apathy and loss of trust in benchmarks in 2025. The core issue is that benchmarks are almost by construction verifiable environments and are therefore immediately susceptible to RLVR and weaker forms of it via synthetic data generation. In the typical benchmaxxing process, teams in LLM labs inevitably construct environments adjacent to little pockets of the embedding space occupied by benchmarks and grow jaggies to cover them. Training on the test set is a new art form.
What does it look like to crush all the benchmarks but still not get AGI?
I have written a lot more on the topic of this section here:
Animals vs. Ghosts
Verifiability
The Space of Minds
3. Cursor / new layer of LLM apps
What I find most notable about Cursor (other than its meteoric rise this year) is that it convincingly revealed a new layer of an "LLM app" - people started to talk about "Cursor for X". As I highlighted in my Y Combinator talk this year (transcript and video), LLM apps like Cursor bundle and orchestrate LLM calls for specific verticals:
They do the "context engineering"
They orchestrate multiple LLM calls under the hood strung into increasingly more complex DAGs, carefully balancing performance and cost tradeoffs.
They provide an application-specific GUI for the human in the loop
They offer an "autonomy slider"
A lot of chatter has been spent in 2025 on how "thick" this new app layer is. Will the LLM labs capture all applications or are there green pastures for LLM apps? Personally I suspect that LLM labs will trend to graduate the generally capable college student, but LLM apps will organize, finetune and actually animate teams of them into deployed professionals in specific verticals by supplying private data, sensors and actuators and feedback loops.
4. Claude Code / AI that lives on your computer
Claude Code (CC) emerged as the first convincing demonstration of what an LLM Agent looks like - something that in a loopy way strings together tool use and reasoning for extended problem solving. In addition, CC is notable to me in that it runs on your computer and with your private environment, data and context. I think OpenAI got this wrong because I think they focused their codex / agent efforts on cloud deployments in containers orchestrated from ChatGPT instead of `localhost`. And while agent swarms running in the cloud feels like the "AGI endgame", we live in an intermediate and slow enough takeoff world of jagged capabilities that it makes more sense to simply run the agents on the computer, hand in hand with developers and their specific setup. CC got this order of precedence correct and packaged it into a beautiful, minimal, compelling CLI form factor that changed what AI looks like - it's not just a website you go to like Google, it's a little spirit/ghost that "lives" on your computer. This is a new, distinct paradigm of interaction with an AI.
5. Vibe coding
2025 is the year that AI crossed a capability threshold necessary to build all kinds of impressive programs simply via English, forgetting that the code even exists. Amusingly, I coined the term "vibe coding" in this shower of thoughts tweet totally oblivious to how far it would go :). With vibe coding, programming is not strictly reserved for highly trained professionals, it is something anyone can do. In this capacity, it is yet another example of what I wrote about in Power to the people: How LLMs flip the script on technology diffusion, on how (in sharp contrast to all other technology so far) regular people benefit a lot more from LLMs compared to professionals, corporations and governments. But not only does vibe coding empower regular people to approach programming, it empowers trained professionals to write a lot more (vibe coded) software that would otherwise never be written. In nanochat, I vibe coded my own custom highly efficient BPE tokenizer in Rust instead of having to adopt existing libraries or learn Rust at that level. I vibe coded many projects this year as quick app demos of something I wanted to exist (e.g. see menugen, llm-council, reader3, HN time capsule). And I've vibe coded entire ephemeral apps just to find a single bug because why not - code is suddenly free, ephemeral, malleable, discardable after single use. Vibe coding will terraform software and alter job descriptions.
6. Nano banana / LLM GUI
Google Gemini Nano banana is one of the most incredible, paradigm-shifting models of 2025. In my world view, LLMs are the next major computing paradigm similar to computers of the 1970s, 80s, etc. Therefore, we are going to see similar kinds of innovations for fundamentally similar kinds of reasons. We're going to see equivalents of personal computing, of microcontrollers (cognitive core), or internet (of agents), etc etc. In particular, in terms of the UIUX, "chatting" with LLMs is a bit like issuing commands to a computer console in the 1980s. Text is the raw/favored data representation for computers (and LLMs), but it is not the favored format for people, especially at the input. People actually dislike reading text - it is slow and effortful. Instead, people love to consume information visually and spatially and this is why the GUI has been invented in traditional computing. In the same way, LLMs should speak to us in our favored format - in images, infographics, slides, whiteboards, animations/videos, web apps, etc. The early and present version of this of course are things like emoji and Markdown, which are ways to "dress up" and lay out text visually for easier consumption with titles, bold, italics, lists, tables, etc. But who is actually going to build the LLM GUI? In this world view, nano banana is a first early hint of what that might look like. And importantly, one notable aspect of it is that it's not just about the image generation itself, it's about the joint capability coming from text generation, image generation and world knowledge, all tangled up in the model weights.
---
TLDR. 2025 was an exciting and mildly surprising year of LLMs. LLMs are emerging as a new kind of intelligence, simultaneously a lot smarter than I expected and a lot dumber than I expected. In any case they are extremely useful and I don't think the industry has realized anywhere near 10% of their potential even at present capability. Meanwhile, there are so many ideas to try and conceptually the field feels wide open. And as I mentioned on my Dwarkesh pod earlier this year, I simultaneously (and on the surface paradoxically) believe that we will both see rapid and continued progress *and* that yet there is a lot of work to be done. Strap in.
URL: I cross-posted this article to my blog, which I think looks and feels a bit better and less clunky.


## 参考文献

* [Karpathy Blog](https://karpathy.bearblog.dev/year-in-review-2025/)