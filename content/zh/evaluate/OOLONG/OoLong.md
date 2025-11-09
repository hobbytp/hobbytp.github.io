---
title: "Oolong"
date: 2025-11-09T00:00:00+08:00
draft: false
updated: 2025-11-09T00:00:00+08:00
tags: ["oolong", "long context", "evaluation"]
categories: ["evaluation"]
description: "Oolong 是一个针对长上下文模型的挑战性聚合基准测试项目，包括相关代码和评估脚本（完整版本即将发布）。其目标是评估模型的长上下文推理和聚合能力。"
---

Oolong 是一个针对长上下文模型的挑战性聚合基准测试项目，包括相关代码和评估脚本（完整版本即将发布）。其目标是评估模型的长上下文推理和聚合能力。

*2025-11-09: Leaderboard:*

| Rank | Model | OOLONG-synth | OOLONG-real | Overall |
|------|-------|--------------|-------------|---------|
| 1 | GPT-5 | 70.75 | 47.00 | 58.88 |
| 2 | Gemini-2.5-Pro | 55.29 | 52.95 | 54.12 |
| 3 | o3 | 62.37 | 36.71 | 49.54 |
| 4 | GPT-5-mini | 63.68 | 34.55 | 49.11 |
| 5 | Claude-Sonnet-4 | 58.18 | 36.75 | 47.47 |
| 6 | o4-mini | 56.74 | 27.13 | 41.94 |
| 7 | GPT-5-nano | 50.73 | 31.05 | 40.89 |
| 8 | Deepseek-R1 | 13.11 | 32.00 | 22.55 |
| 9 | Llama-4-Maverick | 16.37 | 2.07 | 9.22 |

主要功能：

1. 提供合成和真实数据集的推理脚本，支持批量处理和动态上下文窗口分配。
2. 支持设置输入样本最大/最小长度，并通过模型推断参数。
3. 相关资源包括脚本、数据集构建代码、模型输出集和分析脚本。

运行方式：

1. 安装依赖：`pip install -r requirements.txt`
2. 配置 API 密钥：`export LITELLM_API_KEY="sk-[your key]"`
3. 执行推理脚本：`python src/eval/eval_script_batched.py --model [modelname] --dataset [synth or real]`

当前状态：
项目仍在开发中，进一步的功能及详细内容将陆续发布。

许可证：MIT  

## 参考文献

* [Paper: OOLONG: Evaluating Long Context Reasoning and Aggregation Capabilities](https://arxiv.org/pdf/2511.02817)
* [DataSet](https://huggingface.co/oolongbench)
* [Github](https://github.com/abertsch72/oolong)
* [Leaderboard](https://oolongbench.github.io/)
