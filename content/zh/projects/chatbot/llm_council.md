---
title: LLM Council
date: "2025-12-09T15:20:00+08:00"
draft: false
tags: ["llm_council", "chatbot"]
categories: ["projects"]
description: "LLM Council是一个由 Andreas Karpathy 创建的开源项目，用于将多个大语言模型（LLM）组成“理事会”，通过本地 Web 应用统一处理用户查询。"
---
## 项目总结
LLM Council 是一个由 Andreas Karpathy 创建的开源项目，用于将多个大语言模型（LLM）组成“理事会”，通过本地 Web 应用统一处理用户查询。主要特性及流程如下：

1. **功能描述**：
   - 用户输入问题，发送到多个语言模型（如 OpenAI GPT-5.1、Google Gemini 3.0 Pro 等）。
   - 阶段 1：每个模型单独给出答案，展示在“选项卡视图”中供用户比较。
   - 阶段 2：每个语言模型对其他模型的答案进行匿名审核和排名。
   - 阶段 3：理事会的“主席模型”综合所有答案，生成最终答复。

2. **技术实现**：
   - 后端使用 FastAPI（Python 3.10+）与 OpenRouter API。
   - 前端基于 React + Vite，实现用户界面和 Markdown 渲染。
   - 数据存储采用 JSON 文件。

3. **使用方法**：
   - 安装依赖（Python 和 npm）。
   - 配置 API 密钥和模型列表。
   - 通过脚本或命令启动后端和前端服务，访问本地 Web 应用。

## LLM Council 的多模型协作机制
这个系统采用三阶段民主投票式协作机制，让多个大语言模型（LLM）共同工作来回答用户问题：

### 第一阶段：独立回答（Stage 1）
并行查询：用户问题同时发送给所有理事会成员模型（默认包括 GPT-5.1、Gemini 3 Pro、Claude Sonnet 4.5、Grok 4）
技术实现：使用 query_models_parallel() 通过 asyncio.gather() 并行调用所有模型
结果收集：每个模型独立生成自己的回答，不受其他模型影响
代码位置：stage1_collect_responses() 函数

### 第二阶段：交叉评审（Stage 2）
匿名化处理：将第一阶段的所有回答标记为 "Response A"、"Response B" 等，隐藏模型身份
互相排名：每个模型再次被调用，要求评估所有匿名回答并排序
评审标准：模型需要：
单独评价每个回答的优缺点
给出明确的最终排名（FINAL RANKING）

```python
    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""
```

### 第三阶段：主席综合（Stage 3）
* 信息整合：主席模型（默认 Gemini 3 Pro）接收：
    * 所有模型的原始回答（Stage 1）
    * 所有模型的互评排名（Stage 2）
* 综合生成：主席基于集体智慧生成最终答案
* 考虑因素：
    * 各个回答的见解
    * 同行排名揭示的质量
    * 共识和分歧的模式


**核心思想**：主席不是"选出最佳答案"，而是像人类专家综述一样，从多个来源中提炼、整合、综合出一个更好的答案。这利用了大语言模型强大的信息综合能力和上下文理解能力。

```python
    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, and then ranked each other's responses.

Original Question: {user_query}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""

```

### 关键技术特点
* 并行处理：通过 asyncio 实现所有模型调用的并行化，提高响应速度
* 匿名评审：防止模型偏袒特定品牌（如 GPT 偏袒 OpenAI）
* 结构化输出：强制要求排名格式 "FINAL RANKING: 1. Response A"
* 容错机制：单个模型失败不影响整体流程
* OpenRouter 集成：统一 API 访问多家 LLM 提供商

### 工作流程总结

```text
用户问题
    ↓
[Stage 1] → GPT-5.1, Gemini, Claude, Grok 并行回答
    ↓
[Stage 2] → 每个模型评审匿名回答并排名
    ↓
[Stage 3] → 主席模型综合所有信息
    ↓
最终答案呈现给用户

```

### 关键优势
这种设计让主席模型能够：

📊 基于证据决策：不是单一模型的主观判断，而是基于多个模型的共识
🎯 纠错能力：如果某个模型出错，其他模型的排名会将其识别出来
🔄 互补整合：结合不同模型的优势（如 GPT 的逻辑、Claude 的安全性、Gemini 的创造力）
⚖️ 平衡观点：在有争议的问题上呈现多方视角


### 示例流程
假设用户问："量子纠缠是什么？"

Stage 1：

* GPT: 详细技术解释
* Claude: 通俗易懂的比喻
* Gemini: 强调实际应用
* Grok: 幽默风格解释

Stage 2：

* 大部分模型认为 GPT 最准确
* 但也认可 Claude 的可理解性
* Gemini 的应用部分被好评

Stage 3（主席）：
综合生成一个答案：

* 使用 GPT 的准确定义
* 采纳 Claude 的通俗比喻帮助理解
* 补充 Gemini 提到的应用场景
* 形成完整、准确、易懂的最终答案

## 参考
* [LLM Council](https://github.com/karpathy/llm-council)
