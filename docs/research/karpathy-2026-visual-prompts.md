# Karpathy 2026 观点解读：章节配图与封面

目标文章：`content/zh/celebrity_insights/Andrej_Karpathy/Andrej_Karpathy_2026_recent_views.md`。

七张图均为本文分析的概念示意，不是 Karpathy 原图、测量结果或官方标准示例。第七张图的事件依据见正文原始来源；并列不代表因果关系。使用内置 imagegen，每个资产独立生成。正文图注与替代文本提供图片之外的文字解释。

保存目录：`static/images/karpathy-2026/`。

最终资产为七张 1536 × 1024 的 WebP，通过浏览器 Canvas 以 0.92 质量从生成的 PNG 转码，不缩放、不修改图形或文字。合计 813,078 字节；原始 PNG 保留于生成工具的默认目录，不重复放入站点。正文提供替代文本、解释性图注和点击查看原图的链接。

## 博客卡片封面

使用内置 imagegen 单独生成。保存为 `static/images/generated-covers/Andrej_Karpathy_2026_recent_views.webp`，1672 × 941，149,240 字节；仅以 0.92 质量转码为 WebP，不缩放、不改变构图。封面用人的审查连接大量代码与目标、证据、理解三个主题，不是 Karpathy 本人的照片或官方配图。

```text
Use case: illustration-story.
Asset type: final editorial BLOG CARD COVER for the Chinese article "代码变便宜之后：深读 Karpathy 这半年的 AI 判断".
Primary request: an elegant conceptual cover showing that AI can generate abundant code, but human judgment, evidence and understanding remain essential. This is an editorial visual, not a process diagram.
Composition: wide landscape 16:9, ideally 1536x864. Plenty of breathing room. Keep every important element and every word within the central 75% of the canvas so the image survives responsive thumbnail cropping.
Scene: a controlled stream of small blue code-document tiles enters from the left, converges through a central oversized clear teal magnifying lens with a simple teal human hand holding its handle, and emerges on the right as three carefully organized objects: an amber compass representing goals, a small verified document representing evidence, and an open book representing understanding. The metaphor is thoughtful human review and curation, not magical autonomous correctness. Make the visual readable at 320px width, with a few bold large shapes rather than many fine details. The lens and human hand are the main focal point, not a robot.
Style: refined flat editorial illustration matching an existing Chinese explainer series: warm ivory #FAF8F2 background, dark charcoal #202D3A, teal #168579, blue #4679B8, restrained amber #B87432. Crisp outlines, simple geometric forms, sophisticated whitespace, subtle paper feel, no 3D, no glowing cyberpunk effects.
Text: one large dark-charcoal headline near upper center, exactly "代码变便宜之后". One smaller subtitle exactly "KARPATHY · 2026". The image title and subject must sit comfortably inside the safe area. No other readable text; code tiles can have abstract short line marks.
Constraints: no portrait, no corporate logos, no official endorsement, no statistics, no watermark, no invented quotes, no website UI frame. One polished final cover image.
```

## 公共提示词

每次生成，将本段与对应章节提示词连接。

```text
Use case: infographic-diagram.
Asset type: one final Chinese explanatory illustration for an editorial technology blog, NOT a cover or an advertisement.
Style: restrained flat editorial diagram; warm off-white #FAF8F2 canvas, charcoal #202D3A typography, teal #168579 for human judgment, blue #4679B8 for agent execution, muted amber #B87432 for checks/uncertainty. Fine crisp strokes, simple rounded cards, generous whitespace, minimal outline icons, no textures, no gradients, no 3D, no logos or portraits.
Composition: landscape 3:2, approximately 1536x1024. Large modern Simplified Chinese sans-serif labels, all specified text rendered exactly. Main title at top left. Keep text sparse and readable at article width. All arrows must have unambiguous start and end. Never invent statistics, percentages, quotes, event dates or extra claims. Output one complete polished image, not a mockup of a screen or page. No labels outside the canvas.
```

## 01-responsibility — 执行可以委托，责任需要保留

```text
Primary request: a clear responsibility swimlane diagram. Three horizontally stacked lanes, labels on left: “人”, “Agent”, “检查”. Four chronological columns, ample spacing.
Flow: a teal card in human lane at far left “定义目标” with subtitle “约束与验收标准”; arrow diagonally down to a blue card in Agent lane “实现与修改”; arrow diagonally down/right to an amber card in checks lane “测试与证据”; arrow up/right to teal human card at far right “验收与负责”. An amber return arrow from “测试与证据” back to “实现与修改”, labeled “发现问题”. In human lane a thin teal continuous line spanning from goal definition toward acceptance, with a short unobtrusive label “持续监督”. Keep this separate from the executable task arrows.
Title verbatim: “执行可以委托，责任需要保留”.
Bottom takeaway in large text: “生成代码 ≠ 完成工程”.
No numerical data, no claim that tests alone establish correctness.
```

## 02-jagged-tasks — 拆开一个任务，才能看见能力边界

```text
Primary request: qualitative task decomposition map for one refund request. Top title “拆开一个任务，才能看见能力边界”. Under title a small centered root card “一笔退款申请”, branching to exactly three equal-width large columns.
Column 1 blue: “核对金额”, smaller “订单与规则”, bottom check label “可用计算校验”.
Column 2 amber: “检查权限”, smaller “身份与授权”, bottom check label “依赖可信系统”.
Column 3 teal: “处理例外”, smaller “政策与业务判断”, bottom check label “需要授权决策”.
Under the columns a single amber callout “同一业务，不同验证条件”.
Bottom takeaway “先拆分，再决定自主权”.
Equal card sizes; this is NOT a capability ranking, quantitative chart, or assurance of full automation. Use small relevant line icons, no axes, bars, percentages or benchmark numbers.
```

## 03-value-layers — 应用变薄，不等于服务消失

```text
Primary request: before/after conceptual product value layers, distinctly marked inference. Two columns labeled “更容易重建” and “仍需持续经营”. Left shows a thin outlined stack of three slim layers with exact labels “界面”, “生成”, “流程拼接”. Right shows a solid thicker stack of three large layers with exact labels “权威数据与状态”, “交易与可靠履约”, “用户关系与责任”. Above the left stack a blue simple model icon with text “模型能力”; a small downward arrow to the left stack signals some surface functionality is absorbed. Between the stacks use a subtle right-pointing arrow labeled “重新评估价值”, NOT a measured quantity or guaranteed causal law.
Title verbatim “应用变薄，不等于服务消失”.
Bottom takeaway “从一次生成，到长期可信的服务”.
Small amber tag “作者推断”.
No thickness scale, no financial figures, no implication that every app or all UI will disappear.
```

## 04-wiki-loop — 知识库的价值，在持续维护

```text
Primary request: a closed knowledge-maintenance loop with original sources clearly separated from derived summaries.
Title “知识库的价值，在持续维护”.
Four large cards arranged clockwise in a roomy 2x2 layout: top left dark outlined source folder “原始资料”, subtitle “保留出处”; top right blue linked-document icon “关联整理”, subtitle “生成 Wiki”; bottom right teal question icon “查询与使用”, subtitle “让人检查”; bottom left amber magnifier “发现冲突”, subtitle “回查证据”.
Directional arrows exactly: 原始资料 → 关联整理 → 查询与使用 → 发现冲突 → 原始资料. Label the final return arrow “回查，不改写原始资料”. Show a second thin amber dashed path from 发现冲突 to 关联整理 labeled “修订派生页面”, routed through the empty center without covering text or nodes.
Center small concise text “持续维护”.
Bottom takeaway “页面更多 ≠ 证据更多”.
The original source is never presented as AI-generated or rewritten. No fabricated metrics.
```

## 05-understanding — 让同一条规则，更容易检查

```text
Primary request: 4-panel explanatory comparison, large text, no realistic tiny interface screenshot.
Title “让同一条规则，更容易检查”.
Subtitle “约定：首次执行失败后，最多重试 3 次”.
2x2 equal panels:
top left neutral “含混表达”, with quotation “它没成功就再试，三次不行就停。” and subtle question-mark icon.
top right teal “明确表达”, with quotation split across lines “首次执行失败后，最多重试 3 次。仍失败则停止。” and small caption “对象明确 · 术语一致”.
bottom left blue “关系图”, containing a simple fork: “执行” points to “成功？”; one outgoing branch labeled “是” goes to “结束”, other labeled “否” goes to “检查重试上限”. Do NOT invent a wrong retry loop; this is a partial decision structure only.
bottom right amber “交互示意”, show three clearly numbered small retry chips “1”, “2”, “3” and a final red outlined state “仍失败 → 停止”. Small label “改变输入，观察结果”.
Footer exact: “借鉴受控语言原则，不等于符合 ASD-STE100”.
No percentage scores or claim the Chinese sentences comply with the English standard. No video-superiority implication.
```

## 06-learning-loops — 交付循环之外，还要保留学习循环

```text
Primary request: compare a short delivery workflow and a deliberate human-learning loop without empirical charting.
Title “交付循环之外，还要保留学习循环”.
Top third a horizontal blue flow labeled “完成眼前任务”: three cards “提出需求” → “Agent 交付” → “人工确认”. Next to final card a small amber outlined callout “确认 ≠ 理解”.
Bottom two-thirds a larger teal loop labeled “形成下一次判断”: four clockwise nodes arranged as a wide diamond or rounded square, “先做预测” → “运行验证” → “解释差异” → “修正认识” → “先做预测”. All four arrows correct and legible. In center small human outline icon and “主动参与”.
Bottom takeaway “保留预测、反例与解释的机会”.
No data, no claim AI necessarily causes long-term skill decline. Equal visual dignity for both workflows; delivery is necessary but not sufficient for learning.
```

## 07-evidence — 行业反响，要按证据类型阅读

```text
Primary request: dated evidence map, NOT a causal network. Three equal vertical columns with sparse cards sorted chronologically within each. Title “行业反响，要按证据类型阅读”.
Column 1 neutral header “背景研究与实践”, two cards: “2026.01” + “AI 辅助学习研究”; “2026.02” + “工程实践指南”.
Column 2 blue header “同期行业实践”, two cards: “2026.04.08” + “Managed Agents”; “2026.06.11” + “Stripe Projects”.
Column 3 teal header “可追溯的直接回应”, three cards: “2026.04.04” + “LLMBase 评论”; “2026.10.02” + “Output Style 实现”; “2026.10.04” + “公开纠错”.
Use dates and neutral document/tool icons, no corporate logos. No arrows between columns or events; no implied influence from earlier to later. Do not invent view counts, adoption sizes or valuations.
Bottom large takeaway “时间先后 ≠ 因果关系”.
Small footer “个别案例，不代表全行业效果”.
```
