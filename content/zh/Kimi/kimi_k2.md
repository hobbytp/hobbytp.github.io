---
title: "Kimi-K2 简介和有意思的用法"
date: "2025-07-19T22:10:00+08:00"
draft: false
tags: ["AI", "Kimi", "Kimi-K2", "代码", "技术", "MoonshotAI"]
categories: ["large_models"]
description: "本文介绍了MoonshotAI公司Kimi-K2模型简介和相关有意思的用法。"
---

## 目录

- [目录](#目录)
- [Kimi-K2 简介](#kimi-k2-简介)
- [有意思的功能](#有意思的功能)
  - [Partial](#partial)
    - [1. **Partial Mode 的本质作用**](#1-partial-mode-的本质作用)
    - [2. **Partial Mode 的典型效果和用法**](#2-partial-mode-的典型效果和用法)
      - [场景一：结构化内容补全（如 JSON）](#场景一结构化内容补全如-json)
      - [场景二：角色扮演一致性](#场景二角色扮演一致性)
      - [场景三：多轮对话中的格式引导](#场景三多轮对话中的格式引导)
    - [3. **Partial Mode 的底层原理**](#3-partial-mode-的底层原理)
    - [4. **注意事项**](#4-注意事项)
    - [5. **脑洞大开的建议**](#5-脑洞大开的建议)
  - [自动选择合适上下文窗口（context window）模型](#自动选择合适上下文窗口context-window模型)
    - [1. 背景与需求分析](#1-背景与需求分析)
    - [2. 官方推荐方案](#2-官方推荐方案)
- [Kimi-K2 API](#kimi-k2-api)
  - [使用 Tools](#使用-tools)
- [集成到AI 辅助编程助手](#集成到ai-辅助编程助手)

## Kimi-K2 简介

Kimi-K2 是由 Moonshot AI 开发的一种最先进的大规模混合专家（MoE）语言模型，拥有1万亿参数及32亿激活参数，专为**工具使用、推理和自主问题解决**而优化，适用于知识、推理和编码任务等领域。

- Homepage: <https://www.moonshot.ai/>
- Huggingface 模型地址：<https://huggingface.co/moonshotai/Kimi-K2-Instruct>
- Github Kimi-K2: <https://github.com/moonshotai/Kimi-K2>
- Paper Link (coming soon)
- Kimi Chat: <https://www.kimi.com/>
- Kimi API: <https://platform.moonshot.ai>
  - 每百万输入令牌 0.15 美元（缓存命中）
  - 每百万输入令牌 0.60 美元（缓存未命中）
  - 每百万输出令牌 2.50 美元

**主要特点：**

- 通过Muon优化器在1万亿参数和15.5万亿Token上进行大规模训练，解决训练不稳定性问题。
- 提供基础模型（Kimi-K2-Base）和指令模型（Kimi-K2-Instruct），分别适用于细调及通用聊天。
- 强大的自主工具调用能力。

**评估性能：**

- 在多项指标如代码生成、工具使用、数学和通用任务中表现优秀，甚至在部分开源基准任务中达到全球SOTA。

**部署：**

- 提供开放兼容API，并支持多种推理引擎如vLLM和TensorRT-LLM。
- 部署示例和完整使用指南可在项目页获取。

**许可：**

- 模型权重和代码基于修改版MIT许可协议开放。

**资源及联系信息：**

- 提供技术博客、API接入、以及未来的论文链接。如有疑问，可邮件至 <support@moonshot.cn>。

这是一个强大的开源项目，旨在推进大语言模型的创新与应用。

## 有意思的功能

### Partial

在使用大型语言模型时，有时我们希望通过预先填充部分响应来引导模型的输出。在 Kimi 大型语言模型中，我们提供了“部分模式”来实现这一功能。它有助于我们控制输出格式、引导内容，并在角色扮演场景中保持更好的一致性。您只需在最后一个以助手角色发送的消息条目中添加“partial”： True 即可启用“部分模式”。

```python
from openai import OpenAI
 
client = OpenAI(
    api_key="$MOONSHOT_API_KEY",
    base_url="https://api.moonshot.ai/v1",
)
 
completion = client.chat.completions.create(
    model="moonshot-v1-32k",
    messages=[
        {
            "role": "system",
            "content": "Extract the name, size, price, and color from the product description and output them in a JSON object.",
        },
        {
            "role": "user",
            "content": "The DaMi SmartHome Mini is a compact smart home assistant available in black and silver. It costs 998 yuan and measures 256 x 128 x 128mm. It allows you to control lights, thermostats, and other connected devices via voice or app, no matter where you place it in your home.",
        },
        {
            "role": "assistant",
            "content": "{",
            "partial": True   # <<<<< 关键点
        },
    ],
    temperature=0.3,
)
 
print('{'+completion.choices[0].message.content)
```

#### 1. **Partial Mode 的本质作用**

当你在最后一个 assistant 消息中设置 `"partial": true`，**你是在告诉模型：这一条回复只是“部分内容”，后续还会继续补充**。这会引发模型在生成时的“引导”行为，具体表现为：

- **模型会以你提供的内容为“开头”，继续补全剩余内容**；
- 你可以精确控制输出的开头格式、风格，甚至是结构（比如 JSON 的左大括号、角色扮演的前缀等）；
- 这对于需要严格格式化输出、或需要模型“在某种状态下”继续生成的场景非常有用。

#### 2. **Partial Mode 的典型效果和用法**

##### 场景一：结构化内容补全（如 JSON）

假设你希望模型输出标准 JSON，但又怕它乱加前缀或格式出错。你可以这样做：

```json
{
  "role": "assistant",
  "content": "{",
  "partial": true
}
```

此时模型会以 `{` 为起点，**只补全后续 JSON 字段**，而不会再多加内容或乱改结构。你拿到的结果会更容易拼接和解析。

##### 场景二：角色扮演一致性

比如你要让模型扮演某个角色，可以这样：

```json

{
  "role": "assistant",
  "name": "Dr. Kelsier",
  "content": "",
  "partial": true
}

```

这样模型生成的回复就会以 Dr. Kelsier 的身份、风格进行，**不会自动加多余的开头**，角色一致性更好。

##### 场景三：多轮对话中的格式引导

你可以动态地在每轮对话中根据实际需要，**预填充一部分内容**，让模型在这个基础上继续生成，确保风格/格式/内容不跑偏。

#### 3. **Partial Mode 的底层原理**

- **Prompt 拼接控制**：本质上，相当于你把一段“前导文本”强制塞给模型，模型只负责“续写”。
- **防止模型自作主张**：在没有 partial 时，模型有时会自动添加解释、前缀或格式，导致输出不可控；有了 partial，模型会更“听话”地只做补全。
- **流式输出友好**：对于需要流式生成（如实时聊天、代码补全等），partial 可以让你逐步引导模型输出，提升交互体验。

#### 4. **注意事项**

- **不要和 response_format=json_object 混用**，否则模型可能混淆结构，导致输出异常。
- **API 返回内容不包含你预填的 leading_text**，你需要自己拼接完整输出。

#### 5. **脑洞大开的建议**

你可以结合 partial mode 实现以下高级玩法：

- **多 Agent 协同写作**：每个 Agent 先写一段开头，后续用 partial 让模型自动续写，形成风格统一的长文或剧本。
- **AI 自动代码补全 IDE**：你先给出部分函数头，用 partial 让模型只补全函数体，保证代码格式和风格一致。
- **多模态输出引导**：在多模态场景里，先让模型生成图片描述的开头，再 partial 续写详细内容，实现分段式内容生成。
- **AI 安全对齐**：通过 partial 预填“安全声明”或“免责声明”，让模型每次输出都带有合规性前缀，降低风险。

**总结一句话**：  
`partial: true` 让你像“牵着模型的手”一样，精准引导它的输出起点和风格，特别适合高格式化、角色扮演和多轮交互等场景，是高级工程师玩转大模型的利器！

### 自动选择合适上下文窗口（context window）模型

参考： <https://platform.moonshot.ai/docs/guide/choose-an-appropriate-kimi-model>

#### 1. 背景与需求分析

- **问题本质**：多轮对话中，历史消息不断增长，Token数可能超过当前模型的最大Token限制（如8k、32k、128k）。
- **手工方案**：提前计算Token数，选择合适的模型，但不灵活且易出错。
- **自动化目标**：根据当前对话上下文的Token数，自动选择合适的Kimi大模型，既节省成本又避免超限报错。

#### 2. 官方推荐方案

Moonshot官方已提供**moonshot-v1-auto**模型，作为“模型路由器”：

- **工作机制**：自动检测当前上下文Token数，选择8k、32k或128k模型。
- **调用方式**：与普通模型一致，仅需将model参数改为`moonshot-v1-auto`即可。
- **计费规则**：按最终实际选用的模型计费。

**代码示例**：

```python
from openai import OpenAI
 
client = OpenAI(
    api_key = "MOONSHOT_API_KEY", # Replace MOONSHOT_API_KEY with the API Key you obtained from the Kimi Open Platform
    base_url = "https://api.moonshot.ai/v1",
)
messages.append({
  "role": "user",
  "content": input, 
})
 
# We engage in a conversation with the Kimi large language model, carrying the messages along
completion = client.chat.completions.create(
        model="moonshot-v1-auto",  # <-- Note the change here, from moonshot-v1-8k to moonshot-v1-auto
        messages=messages,
        temperature=0.3,
    )
 
# Through the API, we obtain the response message (role=assistant) from the Kimi large language model
   assistant_message = completion.choices[0].message
 
   # To ensure the Kimi large language model has a complete memory, we must also add the message it returns to us to the messages list
   messages.append(assistant_message)
 
   return assistant_message.content
# Through the API, we obtain the response message (role=assistant) from the Kimi large language model
   assistant_message = completion.choices[0].message
 
   # To ensure the Kimi large language model has a complete memory, we must also add the message it returns to us to the messages list
   messages.append(assistant_message)
 
   return assistant_message.content
```

## Kimi-K2 API

它同时支持与 OpenAI 兼容和与 Anthropic 兼容的 API。
这是使用它替代 OpenAI 模型所需的全部 Python 代码。

```python
from openai import OpenAI

client = OpenAI(
    api_key="$MOONSHOT_API_KEY",
    base_url="https://api.moonshot.ai/v1",
)

completion = client.chat.completions.create(
    model="kimi-k2-0711-preview",
    messages=[
        {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conve"},
        {"role": "user", "content": "Hello, my name is Li Lei. What is 1+1?"}
    ],
    temperature = 0.3,
)

print(completion.choices[0].message.content)
```

### 使用 Tools

```python

from openai import OpenAI
 
client = OpenAI(
    api_key = "$MOONSHOT_API_KEY",
    base_url = "https://api.moonshot.ai/v1",
)
 
completion = client.chat.completions.create(
    model = "moonshot-v1-8k",
    messages = [
        {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI, who is more proficient in Chinese and English conversations. You will provide users with safe, helpful, and accurate answers. At the same time, you will reject any questions involving terrorism, racism, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
        {"role": "user", "content": "Determine whether 3214567 is a prime number through programming."}
    ],
    tools = [{
        "type": "function",
        "function": {
            "name": "CodeRunner",
            "description": "A code executor that supports running Python and JavaScript code",
            "parameters": {
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript"]
                    },
                    "code": {
                        "type": "string",
                        "description": "The code is written here"
                    }
                },
            "type": "object"
            }
        }
    }],
    temperature = 0.3,
)
 
print(completion.choices[0].message)
```

## 集成到AI 辅助编程助手

1. 集成到Cline： <https://platform.moonshot.ai/docs/guide/agent-support#using-kimi-k2-model-in-cline>
2. 集成到Roocode： <https://platform.moonshot.ai/docs/guide/agent-support#using-kimi-k2-model-in-roocode>
