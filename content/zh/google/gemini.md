---
title: "gemini相关模型和工具"
date: 2025-01-01T00:00:00+08:00
draft: false
updated: 2025-10-09T00:00:00+08:00
tags: ["gemini", "模型", "工具"]
categories: ["large_models"]
description: "gemini相关模型和工具"
---

## gemini

## Gemini 2.5 Computer Use Model （2025-10-07）

[Gemini 2.5 Computer Use Model](https://blog.google/technology/google-deepmind/gemini-computer-use-model/)：把“看屏幕、点鼠标、填表单”这类人机操作，交给模型来做。它通过 Gemini API 提供一个 computer_use 工具，循环式执行：输入用户意图、当前界面截图与历史动作，模型产出结构化的UI指令（点击、输入、滚动、拖拽、选择下拉等），客户端执行后回传新截图与URL，直至任务完成或被安全策略中断。核心价值在两点：一是对网页/移动端UI的强鲁棒理解与低延迟控制（Browserbase基准表现领先，在线Mind2Web场景延迟更低）；二是可在登录态、复杂表单、拖拽归类等真实工作流里稳定跑通。

它解决的痛点：传统RPA/脚本在DOM变化、非结构化界面、意外弹窗下脆弱，维护成本高；而通用LLM虽能调API，却难以处理“只有UI”的末梢任务。Gemini 2.5 以视觉-推理一体的闭环，直接对屏幕做决策，显著提升容错与恢复（谷歌内测用于脆弱E2E UI测试，自动“自愈”超60%失败）。安全侧提供逐步审查服务与高风险操作确认，覆盖绕过验证码、敏感系统修改等场景。

开发者路径清晰：Google AI Studio/Vertex AI 即刻预览，参考实现支持本地 Playwright 或 Browserbase 云端沙箱。适合个人助手、工作流自动化、UI测试等场景，尤其是“无API、界面频繁变动”的长尾流程。脑洞升级：把它接入多代理协同，前台UI执行+后台检索/结构化解析分工，叠加人类在环批注数据，做自监督式恢复策略学习，冲刺真实世界自治代理。

目前主要支持浏览器，但是未来可能会支持更多UI场景。

## 相关链接

- [NotebookLM 相关链接](https://notebooklm.com/docs/getting-started/overview)
- [Gemini 2.5 Computer Use Model](https://blog.google/technology/google-deepmind/gemini-computer-use-model/)
