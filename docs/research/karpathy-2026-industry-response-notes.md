# Karpathy 2026：LLM Wiki 与输出理解的社区回应证据

- 核验日期与资料截止：2026-10-07。
- 范围：4 月 LLM Wiki gist、10 月 2 日输出理解帖的直接回应；不涉及编程生产力或通用 harness。
- 方法：读取作者原文、原仓库 README、GitHub 提交及评论 API；仓库证据尽量固定到提交版本。下列五项的证据日期均早于截止日。
- 日期口径：GitHub API 时间为 UTC；博客日期为页面署名日期，未推定时区。提交日期不是采用日期，仓库创建日期也不等于实现完成日期。

## 原始事件与访问边界

1. **LLM Wiki**：[Karpathy 原 gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 页面标明创建于 **2026-04-04**。这是模式说明，不能把社区实现说成 Karpathy 发布的软件。
2. **输出理解**：[原 X 帖](https://x.com/karpathy/status/2105819303471976479)。本次直接访问返回 403，未完整读取 X 原页；**2026-10-02** 的日期及 ASD-STE100、图示、HTML、3Blue1Brown 风格视频四类输出，由下列回应作者直接引用该帖的材料交叉确认。不能写成本次已直接核验原帖全部内容、回复或传播数据。

## 主张—来源—限制表

| 可用于博客的主张 | 一手来源及日期 | 具体证明了什么 | 不证明什么／归因限制 |
| --- | --- | --- | --- |
| **LLM Wiki 发布当天已有实现者直接反馈设计细节。** | **S1：Hosuke，LLMBase 作者。** [原 gist 评论][s1]；评论创建和更新均为 **2026-04-04 17:35:15 UTC**，由[单条评论 API][s1-api]核验。 | 作者明确说此前按 Karpathy 的推文尝试实现；gist 的 raw → wiki → schema 三层及 index/log 导航补足了设计。他在评论中链接自己的 LLMBase，并报告 React 界面、答案回写与模型回退的实现思路。是有身份、日期和项目链接的直接回应。 | 主要是作者自述，本次未运行项目、验证长期知识积累效果。**不能说 gist 首次催生 LLMBase**：作者自己提到更早的推文；[仓库 API][s1-repo]记录创建于 4 月 4 日 13:36:45 UTC。应写“此前受其推文启发，并在 gist 下反馈”，不推导开发耗时。 |
| **4 月模式被明确落成了后续开源参考实现。** | **S2：cobusgreyling/llm-wiki。** [初始提交 README][s2]；[提交][s2-commit]时间 **2026-07-03 09:21:39 UTC**；仓库创建于同日 09:21:40 UTC。 | 初始 README 明确称其为 Karpathy LLM Wiki 的参考实现，并直接链接原 gist；包含 raw/wiki/schema 结构、ingest/query/lint 操作和以原 gist 为输入的示例 wiki。归因来自作者文本，而非名称相似。 | 证明有后续实现，不证明 4 月即已发布；不可把它列为“4 月当天反响”。README 的 RAG 对比不是受控实验；模板、CLI 与示例也不证明企业使用、检索优势或维护成本接近零。 |
| **10 月 2 日的输出格式建议，同日被封装成四个技能并附具体样例。** | **S3：ashryaagr/karpathy-output-style。** [固定版本 README][s3]；初始提交 **2026-10-02 07:26:52 UTC**；[样例提交][s3-examples-commit] **08:43:50 UTC**；[本次核对版本][s3-commit] **08:56:24 UTC**。 | README 直接声明灵感来自该 X 帖；[扩散模型示例说明][s3-examples]列出文字、可编辑图示、交互 HTML、约 71 秒配音视频。已用 Git tree 核实 HTML、MP4、provenance 文件存在。因此证据强于仅发布提示词或宣布计划。 | 本次未播放视频、操作网页或复现实验；71 秒及测试结果来自作者文档。作者说明是未训练的玩具分布、未完整验证 STE 词典合规，也未完成 Claude 模型生成验证。它证明独立实现与产物存在，**不证明理解效果提升、官方背书或生产成熟度**。 |
| **另一个作者次日把同一输出层级写成可安装技能。** | **S4：subhams07/Output-for-Best-Understanding。** [初始 README][s4]、[初始提交][s4-commit]：**2026-10-03 10:57:40 UTC**；仓库创建于 10:57:41 UTC。 | README 明确写明基于 10 月 2 日的 Karpathy 原帖，并映射到 STE 文字、Mermaid/SVG、独立 HTML、3Blue1Brown 风格视频四种形式。可作为不同作者直接响应同一建议的第二个具体例子。 | 原候选 `explain-for-understanding-skill` 已重定向至现名，不应算成两个项目。README 自称视频功能属实验性，STE 规则是工作摘要；不能把安装指引当成已验证的跨平台可用性，也不能把作者的格式排序当成学习效果结论。 |
| **回应中出现了针对原帖附件的具体纠错，而非只有转发和实现。** | **S5：Max Nardit 作者文章。** [原文][s5]页面日期 **2026-10-04**，正文说明当天记录并检查了 10 月 2 日帖子。 | 作者报告对照 ASD-STE100 第 9 版检查附件，具体指出 approximately/ABOUT 的状态倒置、TEST 的词性问题等。可写“作者逐项质疑速查图”，并用来提出“易读的形式仍需要内容核验”。 | 这是批评作者自身核对工作的第一手记录；本次未独立逐条审计标准，应保留“作者指出／报告”的归属。不能据此判定所有简化英语、图示或视频无效，也不能认定附件由 Karpathy 本人制作或由 AI 生成。文中引用的他人实验不作为本笔记的一手实验依据。 |

## 可直接采用的表达

> 社区回应已经落到具体实现和纠错上。4 月 4 日，LLMBase 作者在原 gist 下说明自己此前已按 Karpathy 的推文尝试实现，并从详细说明中补足了三层结构和导航设计。7 月又出现直接以原 gist 为依据的参考实现。10 月 2 日的输出理解建议，则在当天和次日分别被两个作者封装成技能，其中一个仓库附有交互网页和配音视频样例；10 月 4 日，另有作者对原帖速查图进行了逐项纠错。[S1][s1] [S2][s2] [S3][s3] [S4][s4] [S5][s5]

以上支持“有可追溯的直接响应”，不支持“大规模采用”“行业已达成共识”或“理解效率得到普遍验证”。本笔记不使用 stars、浏览量、fork 数推导企业采用。

## 因果归属与并行趋势

- **明确承认受启发／基于原文**：S2 直接链接 gist；S3、S4 直接链接同一条 X 帖。可归因到具体模式或建议，不能扩大成整个技术方向的发明权。
- **早先启发与后续反馈并存**：S1 是对 gist 的直接回应，但实现尝试已受此前推文影响；不能把首次启发、仓库创建和 gist 反馈合成一个事件。
- **直接批评**：S5 针对指定帖文及附件，不属于单纯讨论同类工具的平行材料。
- **并行趋势不计入响应数**：既有的 STE 写作实践、Obsidian 工作流、HTML 可视化或讲解视频，除非作者明确建立联系，否则只能作为背景。原 gist 推荐某工具，也不等于该工具由 gist 催生。

## 复核记录与精确链接

- S1 已核对单条评论 API 的 `created_at`、`updated_at`、作者与正文；两项时间相同。当前 LLMBase README 也指向该 gist，但**没有用当前功能反推 4 月功能**。
- S2、S3、S4 已读取固定 SHA 的原始 README，并通过各仓库的[README 提交记录 S2][s2-history]、[S3][s3-history]、[S4][s4-history]核对提交时间；网页读取固定 SHA 遇到缓存缺失时改读同 SHA 的 `raw.githubusercontent.com` 内容。没有用搜索引擎的抓取日期替代发布时间。
- S3 的[固定版本文件树 API][s3-tree]显示 `examples/diffusion/webpage/diffusion.html`、`video/explainer.mp4`、`provenance.json`；[作者验证说明][s3-validation]明确保留未完成的验证项。只确认文件与作者记录，不声称本次完成端到端验证。
- S5 以作者页首日期及正文为准，无固定历史快照；这里引用的是截至核验日可见的文章。未采纳文中的流量数字、未回溯到原实验的二手结果或截止日之后的资料。

[s1]: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6079012#gistcomment-6079012
[s1-api]: https://api.github.com/gists/442a6bf555914893e9891c11519de94f/comments/6079012
[s1-repo]: https://api.github.com/repos/Hosuke/llmbase
[s2]: https://github.com/cobusgreyling/llm-wiki/blob/75294aacbfb454fe45b18d99769f1eb4a4c0934c/README.md
[s2-commit]: https://github.com/cobusgreyling/llm-wiki/commit/75294aacbfb454fe45b18d99769f1eb4a4c0934c
[s2-history]: https://api.github.com/repos/cobusgreyling/llm-wiki/commits?path=README.md&per_page=30&until=2026-10-07T23:59:59Z
[s3]: https://github.com/ashryaagr/karpathy-output-style/blob/4f6c5e974ad8a41fb2ffd628de2ed5271f0b5d88/README.md
[s3-commit]: https://github.com/ashryaagr/karpathy-output-style/commit/4f6c5e974ad8a41fb2ffd628de2ed5271f0b5d88
[s3-examples-commit]: https://github.com/ashryaagr/karpathy-output-style/commit/8b18f028114882b4f4db1023a50bb82efdd47a4b
[s3-history]: https://api.github.com/repos/ashryaagr/karpathy-output-style/commits?path=README.md&per_page=30&until=2026-10-07T23:59:59Z
[s3-examples]: https://github.com/ashryaagr/karpathy-output-style/blob/4f6c5e974ad8a41fb2ffd628de2ed5271f0b5d88/examples/diffusion/README.md
[s3-validation]: https://github.com/ashryaagr/karpathy-output-style/blob/4f6c5e974ad8a41fb2ffd628de2ed5271f0b5d88/docs/validation.md
[s3-tree]: https://api.github.com/repos/ashryaagr/karpathy-output-style/git/trees/4f6c5e974ad8a41fb2ffd628de2ed5271f0b5d88?recursive=1
[s4]: https://github.com/subhams07/Output-for-Best-Understanding/blob/7f148776d7c1c09adc69f3c89bc845475305be08/README.md
[s4-commit]: https://github.com/subhams07/Output-for-Best-Understanding/commit/7f148776d7c1c09adc69f3c89bc845475305be08
[s4-history]: https://api.github.com/repos/subhams07/Output-for-Best-Understanding/commits?path=README.md&per_page=30&until=2026-10-07T23:59:59Z
[s5]: https://max.nardit.com/articles/karpathy-understanding-llm-outputs
