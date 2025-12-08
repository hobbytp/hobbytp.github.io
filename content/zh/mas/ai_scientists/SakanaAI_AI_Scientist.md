---
title: "SakanaAI AI Scientist"
date: 2025-11-08T17:00:00+08:00
draft: true
tags: ["AI", "SakanaAI", "AI Scientist"]
categories: ["ai_scientists"]
description: "AI Scientist-v2 是一个由 SakanaAI 开发的自动化科学研究系统，其核心目标是通过代理式树搜索实现开放式科学探索。"
wordCount: 406
readingTime: 2
---

AI Scientist-v2 是一个由 SakanaAI 开发的自动化科学研究系统，其核心目标是通过代理式树搜索实现开放式科学探索。相比前代版本（AI Scientist-v1），AI Scientist-v2 不再依赖于人工模板，能够跨机器学习领域生成假设、运行实验、分析数据并撰写科学论文。它被用于生成并发表了首篇完全由 AI 撰写并通过同行评审的 workshop 论文。不过，AI Scientist-v2 更倾向探索性，成功率可能低于基于模板的 v1。

其主要特性包括：

1. **自动生成研究想法与实验方案**：利用 LLM 进行主题生成和分析，检测新颖性并生成具体研究方向。
2. **多模型支持与 API 集成**：支持 OpenAI、Gemini 和 AWS Bedrock 模型，能够进行多轮生成与改进。
3. **实验自动化与论文生成**：通过渐进式树搜索优化实验流程，并生成完整的 PDF 科学论文。
4. **兼容性与安全性警告**：推荐在受控环境（如 Docker）中运行，防止潜在风险。

安装与运行需要 CUDA 支持的 NVIDIA GPU，可通过 Conda 和 pip 配置环境。用户需提供相应模型的 API Key，并可自定义生成的主题、实验配置和论文撰写流程。

代码的主要用途包括科学研究过程中想法生成、实验数据分析与论文自动化撰写，为科学自动化提供了一种新的工具框架。

星标：1.8k，Fork：332，许可证：Apache-2.0。
