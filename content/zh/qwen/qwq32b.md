+++
title = "QwQ-32B Qwen推理大模型解读"
date = "2025-03-06T20:21:00+08:00"
draft = false
tags = ["AI", "深度思考", "QwQ-32B", "大模型", "Qwen"]
categories = ["llm", "qwen"，"large_models"]
description = "本文介绍了深度求索（DeepSeek）公司推出的新一代推理模型QwQ-32B，并对其技术原理、主要贡献、论文方法、评估结果和局限性进行了详细解读。"
+++

## 模型介绍

这是一款拥有 320 亿参数的模型，其性能可与具备 6710 亿参数（其中 370 亿被激活）的 DeepSeek-R1 媲美。这一成果突显了将强化学习应用于经过大规模预训练的强大基础模型的有效性。
QwQ32B在推理模型中集成了与 Agent 相关的能力，使其能够在使用工具的同时进行批判性思考，并根据环境反馈调整推理过程。
通过这种方式，QwQ32B 能够执行复杂的推理任务，如数学问题解决和编程挑战。
这个模型于2025年3月6日发布。

### 技术指标

- 类型：因果语言模型
- 训练阶段：训练前和训练后（监督微调和强化学习）
- 架构：具有RoPE、SwiGLU、RMSNorm和注意力QKV偏置的变压器
- 参数数：32.5B
- 参数数量（非嵌入）：31.0B
- 层数：64
- 注意头数（GQA）：Q 40个，KV 8个
- 上下文长度：完整的131,072个令牌

### 评测结果

QwQ-32B 在一系列基准测试中进行了评估，测试了数学推理、编程能力和通用能力。以下结果展示了 QwQ-32B 与其他领先模型的性能对比，包括 DeepSeek-R1-Distilled-Qwen-32B、DeepSeek-R1-Distilled-Llama-70B、o1-mini 以及原始的 DeepSeek-R1。

### 训练细节

QwQ基于Qwen2.5，在冷启动的基础上开展了大规模强化学习, 这个和DeepSeek R1的训练方式类似。
在初始阶段，我们特别针对数学和编程任务进行了 RL 训练。
与依赖传统的奖励模型（reward model）不同：

1. 通过校验生成答案的正确性来为数学问题提供反馈，
2. 通过代码执行服务器评估生成的代码是否成功通过测试用例来提供代码的反馈。
3. 随着训练轮次的推进，这两个领域中的性能均表现出持续的提升。
   1. 在第一阶段的 RL 过后，我们增加了另一个针对通用能力的 RL。
   2. 此阶段使用通用奖励模型和一些基于规则的验证器进行训练。
   3. 通过少量步骤的通用 RL，可以提升其他通用能力，同时在数学和编程任务上的性能没有显著下降。

### 代码调用

其代码已在最新的HuggingFace transformers中（v4.37）。

```python
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(
    # If the environment variable is not configured, replace with your API Key: api_key="sk-xxx"
    # How to get an API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

reasoning_content = ""
content = ""

is_answering = False

completion = client.chat.completions.create(
    model="qwq-32b",
    messages=[
        {"role": "user", "content": "Which is larger, 9.9 or 9.11?"}
    ],
    stream=True,
    # Uncomment the following line to return token usage in the last chunk
    # stream_options={
    #     "include_usage": True
    # }
)

print("\n" + "=" * 20 + "reasoning content" + "=" * 20 + "\n")

for chunk in completion:
    # If chunk.choices is empty, print usage
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
    else:
        delta = chunk.choices[0].delta
        # Print reasoning content
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
        else:
            if delta.content != "" and is_answering is False:
                print("\n" + "=" * 20 + "content" + "=" * 20 + "\n")
                is_answering = True
            # Print content
            print(delta.content, end='', flush=True)
            content += delta.content
```

### 未来工作

未来，我们将继续探索将智能体与RL集成，以实现长时推理，目标是通过推理时间扩展来释放更高的智能。
这是Qwen在大规模强化学习（RL）以增强推理能力方面的第一步。通过这一旅程，Qwen认识到预训练语言模型中尚未开发的可能性。更强大的基础模型与依托规模化计算资源的RL相结合，将会使Qwen更接近实现人工通用智能（AGI）。

### 参考链接

- Demo: <https://huggingface.co/spaces/Qwen/QwQ-32B-Demo>
- Qwen 官方文档:
  - <https://qwen.readthedocs.io/en/latest/>
- Qwen 博客
  - <https://qwenlm.github.io/zh/blog/qwq-32b/>
- 大模型访问和下载:
  - <https://modelscope.cn/models/Qwen/QwQ-32B>
  - <https://huggingface.co/Qwen/QwQ-32B>
