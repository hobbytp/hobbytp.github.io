---
title: "DeerFlow - 字节跳动开源的Deep Research"
date: "2025-05-21T22:30:00+08:00"
draft: false
tags:  ["Deerflow","Deep Research","LangGraph","MCP"]
categories: ["projects"]
description: "DeerFlow - 字节跳动开源的Deep Research"
---


## 介绍

DeerFlow 是一个社区驱动的深度研究框架，由字节跳动开发，结合语言模型与工具（如网页搜索、爬虫、Python 执行），强调开放源码并回馈开源社区。核心功能包括：

1. **LLM 集成**：支持多层级模型集成，用于不同复杂度任务（不同节点可以使用不同的模型）；
2. **工具与搜索能力**：支持 Tavily、DuckDuckGo、Brave、Arxiv 等多种搜索引擎和高级内容提取；
3. **报告生成**：基本研究、报告编辑、PPT 生成及播客脚本制作；
4. **人机协作**：支持自然语言修改研究计划；
5. **TTS 功能**：将研究报告转为高质量的语音。
6. **前后端分离**：前端使用Next.js，后端使用FastAPI + Python LangGraph Workflow
7. **支持MCP**：支持MCP（Modal Context Protocol）协议
8.

项目采用模块化多代理架构，基于 **LangGraph** 的可视化工作流。此外，提供控制台和 Web UI 两种界面，支持 Docker 部署和配置，可快速地进行深度研究和报告生成。项目开源，遵循 MIT 许可协议，官方文档详尽，设置和使用简单易行。

## 架构

### 整体架构图

```mermaid
graph TD
    %% Frontend
    subgraph Frontend ["Frontend (Next.js)"]
        F1[Web UI Components] --> F2["useStore (store.ts)"]
        F1 --> F3["useSettingsStore (settings-store.ts)"]
        F2 --> F4["chatStream() (chatts)"]
    end

    %% Backend
    subgraph Backend ["Backend (FastAPI)"]
        B1["FastAPI App (app.py)"] --> B2["/api/chat/stream endpoint"]
        B2 --> B3["build_graph_with_memory()"]
        AgentNodes
        Tools
    end

    %% Agent Nodes
    subgraph AgentNodes ["Agent Nodes (nodes.py)"]
        AN1["coordinator_node()"] --> AN2["planner_node()"]
        AN2 --> AN3["research_team_node()"]
        AN3 --> AN4["researcher_node()"]
        AN4 --> AN3
        AN3 --> AN5["coder_node()"]
        AN5 --> AN3
        AN3 --> AN6["reporter_node()"]
    end

    %% Tools
    subgraph Tools ["Tools"]
        T1[web_search_tool]
        T2[crawl_tool]
        T3[python_repl_tool]
        T4[MCP integration]
    end

    %% Connections between subgraphs and nodes
    F4 --> B1
    B3 --> AN1
    AN4 --> T1
    AN4 --> T4
    AN4 --> T2
    AN5 --> T3
    AN6 --> T4

    %% Assuming reporter_node might interact with MCP integration or this is a general tool link
    %% Styling (Optional - Can be added if specific styling is needed)
    %% classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    %% classDef subgraphstyle fill:#ececff,stroke:#999,stroke-width:1px,color:black;
    %% class Frontend,Backend,AgentNodes,Tools subgraphstyle;
```

### 多代理工作流

## 限制

目前报告生成由Reporter完成，但是没有其他角色对其输出进行检查。
目前只支持同时运行一种Search Engine，.env里面只有一个SEARCH_API配置。

## Demo

在本地安装DeerFlow，并使用CLI 或Web UI来运行。

### Step1: Install

```bash
# Clone the repository
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow

# Install dependencies, uv will take care of the python interpreter and venv creation, and install the required packages
uv sync

# Configure .env with your API keys
# Tavily: https://app.tavily.com/home
# Brave_SEARCH: https://brave.com/search/api/
# volcengine TTS: Add your TTS credentials if you have them
cp .env.example .env

# See the 'Supported Search Engines' and 'Text-to-Speech Integration' sections below for all available options

# Configure conf.yaml for your LLM model and API keys
# Please refer to 'docs/configuration_guide.md' for more details
cp conf.yaml.example conf.yaml

# Optionally, install web UI dependencies via pnpm:
cd deer-flow/web
pnpm install
```

### Step 2: 使用一个UI来运行

Console UI

```bash
# Run the project in a bash-like shell
uv run main.py
WebUI
这个目前不是很好用
# Run both the backend and frontend servers in development mode
# On macOS/Linux
./bootstrap.sh -d

# Open your browser and visit http://localhost:3000 to explore the web UI.
```

### 问题

1.如何不同的Agent使用不同的模型？
修给下面的mapping，在config.yaml里面加模型配置信息。

```python
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",
    "planner": "basic",
    "researcher": "basic",
    "coder": "basic",
    "reporter": "basic",
    "podcast_script_writer": "basic",
    "ppt_composer": "basic",
    "prose_writer": "basic",
}
```

## 参考

-[deerflow github](https://github.com/bytedance/deer-flow)
-[deepwiki deerflow](https://deepwiki.com/bytedance/deer-flow)
