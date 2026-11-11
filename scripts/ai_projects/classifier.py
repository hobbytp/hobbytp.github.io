#!/usr/bin/env python3
"""
开源项目智能分类器与结构化中文摘要兜底生成器。
根据仓库名称、英文描述、GitHub Topics、主要语言自动归类到 10 大领域，
并提供高质量的中文一句话定位、适用场景与局限边界。
"""

import re
from typing import Dict, List, Tuple, Any


CATEGORY_RULES: List[Tuple[str, re.Pattern]] = [
    (
        "security",
        re.compile(
            r"pyrit|garak|ai[-_ ]?safety|llm[-_ ]?security|prompt[-_ ]?injection|"
            r"red[-_ ]?team|guardrail|jailbreak|cybersecurity|pentest|vulnerability|waf|auth",
            re.I,
        ),
    ),
    (
        "eval",
        re.compile(
            r"promptfoo|ragas|deepeval|lm[-_]evaluation|llm[-_ ]?eval|ai[-_ ]?eval|"
            r"observability|langfuse|phoenix|opik|benchmark|leaderboard|oolong|evals|tracing|telemetry",
            re.I,
        ),
    ),
    (
        "skills",
        re.compile(
            r"\bmcp\b|model[-_ ]?context[-_ ]?protocol|mcp[-_ ]?server|fastmcp|fastapi[-_]?mcp|"
            r"agent[-_ ]?skills|claude[-_ ]?skills|skill[-_ ]?seeker|serena|context7|agentgateway|"
            r"ui[-_]?ux[-_]?pro|tool[-_ ]?use|function[-_ ]?calling",
            re.I,
        ),
    ),
    (
        "coding",
        re.compile(
            r"openai/codex|codex[-_ ]?cli|claude[-_ ]?code|gemini[-_ ]?cli|opencode|\baider\b|\bcursor\b|"
            r"windsurf|\bcline\b|roo[-_ ]?code|ccmanager|claudable|spec[-_]?kit|spec[-_ ]?driven|"
            r"swe[-_ ]?agent|openhands|\bdevin\b|code[-_ ]?assistant|coding[-_ ]?agent|copilot|"
            r"code[-_ ]?review|\bworktree\b|\blsp\b|\bide\b",
            re.I,
        ),
    ),
    (
        "training",
        re.compile(
            r"llama[-_]?factory|axolotl|unsloth|fine[-_ ]?tun|finetun|model[-_ ]?training|"
            r"vllm|sglang|tensorrt|llama\.cpp|gguf|ollama|mlx|flash[-_]?mla|flash[-_]?attention|"
            r"deepspeed|megatron|verl|grpo|rlhf|dpo|lora|qlora|quantiz|inference[-_ ]?engine|cuda|kernel",
            re.I,
        ),
    ),
    (
        "media",
        re.compile(
            r"comfyui|wan2|wan[-_ ]?video|code2video|visual[-_ ]?explainer|html[-_ ]?explainer|"
            r"editorial[-_ ]?diagram|diffusers|stable[-_ ]?diffusion|flux|midjourney|"
            r"text[-_ ]?to[-_ ]?(image|video|audio|speech)|image[-_ ]?generation|video[-_ ]?generation|"
            r"tts|asr|whisper|voice|audio|music|3d|blender|animation|diagram|mermaid|slide|presentation|canvas",
            re.I,
        ),
    ),
    (
        "knowledge",
        re.compile(
            r"graphiti|mem0|memevolve|zep|letta|memgpt|qdrant|milvus|weaviate|chroma|pgvector|"
            r"lightrag|graphrag|ragflow|haystack|llamaindex|knowledge[-_ ]?graph|knowledge[-_ ]?base|"
            r"retrieval[-_ ]?augmented|\brag\b|vector[-_ ]?(db|database|search)|embedding|rerank|"
            r"memory|context[-_ ]?engineering|docling|mineru|pdf|ocr|crawler|scrape|firecrawl|crawl4ai",
            re.I,
        ),
    ),
    (
        "apps",
        re.compile(
            r"trendradar|deer[-_]?flow|\bstorm\b|deep[-_ ]?research|deeptutor|open[-_ ]?notebook|"
            r"notebooklm|dify|open[-_ ]?webui|anythingllm|lobechat|cherry[-_ ]?studio|nextchat|"
            r"chatbox|jan|khoj|perplexica|search|news|digest|rss|podcast|translate|writing|"
            r"tradingagents|quant|qlib|rd[-_]?agent|finance|assistant|tutor|education",
            re.I,
        ),
    ),
    (
        "agent",
        re.compile(
            r"langgraph|langchain|smolagents|autogen|crewai|camel|ag2|mastra|pydantic[-_]?ai|"
            r"openai[-_ ]?agents|swarm|openmanus|manus|owl|nanobot|autoglm|ui[-_]?tars|browser[-_ ]?use|"
            r"playwright|computer[-_ ]?use|gui[-_ ]?agent|agent[-_ ]?reach|openenv|openevolve|"
            r"task[-_]?master|multi[-_ ]?agent|agentic|\bagent\b|workflow|orchestrat",
            re.I,
        ),
    ),
    (
        "infra",
        re.compile(
            r"proxmox|proxlb|docker|kubernetes|k8s|container|linux|ubuntu|nixos|openwrt|"
            r"network|proxy|vpn|wireguard|tailscale|cloudflare|nginx|caddy|database|postgres|"
            r"redis|sqlite|rust|golang|cli|terminal|shell|devops|monitor",
            re.I,
        ),
    ),
]


CATEGORY_META: Dict[str, Dict[str, Any]] = {
    "agent": {
        "name": "Agent 与多智能体",
        "default_tags": ["智能体", "工作流编排", "自主执行"],
        "good_for": [
            "构建多步骤自主规划、工具调用与状态流转的 AI 智能体系统",
            "探索多智能体协同分工、环境交互与复杂任务拆解",
        ],
        "not_for": [
            "单次 Prompt 调用即可解决的简单文本生成任务",
        ],
    },
    "coding": {
        "name": "AI 编程与终端",
        "default_tags": ["AI编程", "研发效能", "终端工具"],
        "good_for": [
            "提升日常代码编写、重构、跨文件检索与自动化测试闭环效率",
            "规范化管理 AI 编码代理会话、上下文线束与工程契约",
        ],
        "not_for": [
            "非软件工程或完全不涉及代码/终端的环境",
        ],
    },
    "skills": {
        "name": "Skills 与 MCP 协议",
        "default_tags": ["MCP", "Agent Skills", "工具扩展"],
        "good_for": [
            "为 Claude Code、Codex、Cursor 等代理接入标准化外部工具与专业领域技能",
            "扩展大模型访问本地符号、实时文档、浏览器或第三方服务的能力",
        ],
        "not_for": [
            "不支持 MCP 或函数调用的纯文本对话场景",
        ],
    },
    "knowledge": {
        "name": "知识、记忆与 RAG",
        "default_tags": ["知识库", "RAG", "Agent记忆"],
        "good_for": [
            "构建企业或个人知识库、文档解析管线与高准确率检索增强生成（RAG）",
            "为长周期运行的 Agent 提供跨会话长期记忆与知识图谱关系推理",
        ],
        "not_for": [
            "无需外部知识注入或状态持久化的无状态轻量应用",
        ],
    },
    "apps": {
        "name": "深度研究与信息应用",
        "default_tags": ["深度研究", "信息聚合", "AI应用"],
        "good_for": [
            "自动化情报收集、热点监控、多视角文献深挖（Deep Research）与交互式学习",
            "开箱即用提升个人研究、信息过滤与分析决策效率",
        ],
        "not_for": [
            "需要底层算子级定制或毫秒级实时响应的嵌入式场景",
        ],
    },
    "media": {
        "name": "视觉解释与多模态创作",
        "default_tags": ["多模态", "视觉生成", "可视化"],
        "good_for": [
            "将复杂技术逻辑转化为直观图解、交互式页面或演示视频",
            "搭建可复现的图像、视频、语音多模态生成与编辑流水线",
        ],
        "not_for": [
            "纯后端数据批处理或无视觉展示需求的场景",
        ],
    },
    "training": {
        "name": "模型训练与推理加速",
        "default_tags": ["模型微调", "推理优化", "大模型底座"],
        "good_for": [
            "垂直领域模型微调（SFT/DPO/RL）、量化压缩与高吞吐低延迟推理部署",
            "优化本地或服务端 GPU 算力利用率与模型服务成本",
        ],
        "not_for": [
            "仅通过商业 API 调用且无自建模型训练/部署需求的团队",
        ],
    },
    "eval": {
        "name": "评测与可观测性",
        "default_tags": ["系统评测", "可观测性", "基准测试"],
        "good_for": [
            "对 Prompt、RAG 与 Agent 管线进行定量回归评测与模型横评",
            "追踪生产环境 LLM 调用链路、延迟、Token 成本与异常输出",
        ],
        "not_for": [
            "一次性原型验证且无需持续迭代质量门禁的场景",
        ],
    },
    "security": {
        "name": "安全与红队治理",
        "default_tags": ["AI安全", "红队测试", "风险治理"],
        "good_for": [
            "检测与防御提示词注入、越狱攻击、敏感数据泄露与越权工具调用",
            "满足企业级 AI 应用上线前的安全红队评估与合规审计",
        ],
        "not_for": [
            "完全封闭、输入可信且无外部交互的离线实验脚本",
        ],
    },
    "infra": {
        "name": "系统与基础设施",
        "default_tags": ["基础设施", "云原生", "系统工具"],
        "good_for": [
            "搭建虚拟化实验环境、容器编排、网络服务与高效开发者工具链",
            "支撑 AI 研发与自托管服务的底层计算和运维自动化",
        ],
        "not_for": [
            "纯上层业务逻辑开发且不涉及环境运维的场景",
        ],
    },
}


TOPIC_TRANSLATIONS: Dict[str, str] = {
    "agent": "智能体",
    "agents": "智能体",
    "ai-agent": "AI智能体",
    "ai-agents": "AI智能体",
    "multi-agent": "多智能体",
    "multi-agent-systems": "多智能体",
    "mcp": "MCP协议",
    "mcp-server": "MCP服务",
    "model-context-protocol": "MCP协议",
    "rag": "RAG检索",
    "knowledge-graph": "知识图谱",
    "memory": "长期记忆",
    "vector-database": "向量数据库",
    "llm": "大语言模型",
    "llms": "大语言模型",
    "deep-research": "深度研究",
    "code-generation": "代码生成",
    "coding-assistant": "编程助手",
    "claude-code": "Claude-Code",
    "codex": "Codex",
    "fine-tuning": "模型微调",
    "reinforcement-learning": "强化学习",
    "inference": "推理加速",
    "quantization": "模型量化",
    "text-to-video": "视频生成",
    "text-to-image": "图像生成",
    "comfyui": "ComfyUI",
    "visualization": "可视化",
    "evaluation": "模型评测",
    "benchmark": "基准测试",
    "observability": "可观测性",
    "red-teaming": "红队测试",
    "security": "安全防护",
    "workflow": "工作流",
    "automation": "自动化",
    "browser-use": "浏览器自动化",
    "ocr": "文档解析",
    "pdf": "PDF处理",
    "proxmox": "Proxmox虚拟化",
    "docker": "容器化",
}


def classify_repository(
    full_name: str,
    description: str,
    topics: List[str],
    language: str = "",
) -> str:
    """根据仓库全名、描述、Topics 自动判定所属分类 ID。"""
    text = f"{full_name} {description or ''} {' '.join(topics or [])} {language or ''}"
    for cat_id, pattern in CATEGORY_RULES:
        if pattern.search(text):
            return cat_id
    return "agent" if "ai" in text.lower() or "llm" in text.lower() else "infra"


def extract_chinese_tags(
    cat_id: str,
    topics: List[str],
    language: str = "",
    max_tags: int = 4,
) -> List[str]:
    """从 topics 和分类中提取紧凑可读的中文/技术标签。"""
    tags: List[str] = []
    for t in topics or []:
        t_low = t.lower().strip()
        if t_low in TOPIC_TRANSLATIONS:
            zh = TOPIC_TRANSLATIONS[t_low]
            if zh not in tags:
                tags.append(zh)
        elif len(t) <= 14 and t not in tags and t_low not in ("ai", "python", "typescript", "javascript"):
            tags.append(t)
        if len(tags) >= max_tags:
            break

    defaults = CATEGORY_META.get(cat_id, CATEGORY_META["agent"])["default_tags"]
    for d in defaults:
        if len(tags) >= max_tags:
            break
        if d not in tags:
            tags.append(d)

    if language and language not in tags and len(tags) < max_tags:
        tags.append(language)

    return tags[:max_tags]


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fa5]", text or ""))


def build_heuristic_summary(
    full_name: str,
    description: str,
    cat_id: str,
    topics: List[str],
    language: str = "",
) -> Dict[str, Any]:
    """
    当项目尚未配置人工覆盖且无缓存 LLM 摘要时，
    基于描述、分类和标签生成结构化中文说明，确保每个项目页内容翔实可读。
    """
    cat_info = CATEGORY_META.get(cat_id, CATEGORY_META["agent"])
    cat_name = cat_info["name"]
    desc_clean = (description or "").strip()
    repo_name = full_name.split("/")[-1]

    if desc_clean and _has_cjk(desc_clean):
        summary_zh = desc_clean[:110]
    elif desc_clean:
        lang_prefix = f"基于 {language} 构建的" if language else "开源"
        tags_preview = "、".join(extract_chinese_tags(cat_id, topics, language, max_tags=2))
        summary_zh = f"【{cat_name}】{lang_prefix}{tags_preview}项目：{desc_clean[:120]}"
    else:
        summary_zh = f"{repo_name}：面向{cat_name}领域的开源工具与技术实现。"

    return {
        "summary_zh": summary_zh,
        "good_for": list(cat_info["good_for"]),
        "not_for": list(cat_info["not_for"]),
        "source": "heuristic",
    }
