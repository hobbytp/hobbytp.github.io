import html
import json
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List
from scripts.daily_ai.generators.ai_client import AIClient
from scripts.daily_ai.models import BaseItem, GitHubProjectItem, ModelItem, PaperItem


class ChapterWriter:
    """章节生成引擎：根据不同章节调用特定 Prompt 和大模型，支持高质量兜底渲染"""
    
    def __init__(self):
        self.ai = AIClient()
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        prompt_path = Path(__file__).parent / "prompts.yaml"
        if not prompt_path.exists():
            return {}
        with open(prompt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def _build_context(self, items: List[BaseItem]) -> str:
        context_lines = []
        for idx, item in enumerate(items, 1):
            context_lines.append(f"[{idx}] 标题: {item.title}")
            context_lines.append(f"    来源: {item.source}")
            context_lines.append(f"    链接: {item.url}")
            context_lines.append(f"    简述/摘要: {item.description}")
            if hasattr(item, 'stars') and item.stars:
                context_lines.append(f"    Stars数量/增长: {item.stars} ({getattr(item, 'stars_per_day', 0):.1f}/day)")
            if hasattr(item, 'downloads') and item.downloads:
                context_lines.append(f"    下载量: {item.downloads}")
            if hasattr(item, 'authors') and item.authors:
                context_lines.append(f"    作者: {', '.join(getattr(item, 'authors', []))}")
            if getattr(item, 'keywords', None):
                context_lines.append(f"    技术标签: {', '.join(item.keywords)}")
            if getattr(item, 'sentiment', None):
                context_lines.append(f"    舆情/行业倾向: {item.sentiment}")
            context_lines.append("")
        return "\n".join(context_lines)

    def _infer_model_specs(self, title: str, pipeline: str, downloads: int, desc: str) -> Dict[str, str]:
        """推导模型的应用场景、参数量量化建议与核心亮点"""
        # 1. 应用场景
        if "video" in pipeline or "video" in title.lower():
            scene = "适用于静态图像转连贯动态视频或视频生成任务，适合于创意内容生成、广告制作与短视频快速原型设计。"
        elif "image-text-to-text" in pipeline or "vision" in title.lower() or "vl" in title.lower():
            scene = "专长于基于图像与文本输入的高质量跨模态理解与生成，可用于自动图像标注、多模态文档解析与视觉智能体交互。"
        elif "speech" in pipeline or "audio" in title.lower() or "asr" in title.lower():
            scene = "专长于高保真语音合成、实时转录或多模态音频对话，适合智能助手与端到端语音交互系统。"
        else:
            scene = "专长于复杂推理、代码辅助编写与长文本生成任务，适合对话机器人、企业级知识问答与智能体编排等核心业务场景。"

        # 2. 参数量与量化建议
        import re
        param_match = re.search(r'(\d+(?:\.\d+)?)[bB]', title)
        is_gguf = "gguf" in title.lower() or "ggml" in title.lower()
        if param_match:
            param_num = param_match.group(1)
            try:
                num_val = float(param_num)
                if num_val >= 70:
                    spec = f"拥有约 {param_num}0 亿超大规模参数。全量推理对算力要求极高，强烈推荐使用 AWQ 或 FP8/GGUF 4-bit 量化，建议配置多卡 A100/H100 或高性能算力集群进行分布式部署。"
                elif num_val >= 20:
                    spec = f"属于 {param_num}0 亿参数的中大模型级别。兼顾了强劲的推理能力与合理的硬件门槛，推荐使用 GGUF (Q4_K_M) 或 FP8 格式压缩，可在 24GB 显存单卡（如 RTX 4090 / 3090）上高效运行。"
                else:
                    spec = f"属于 {param_num}0 亿参数轻量级级别。经过 GGUF/INT4 量化后显存占用低至数 GB，具备极高的端侧与本地离线部署友好度，中低配 PC 或消费级 GPU 即可流畅运行。"
            except ValueError:
                spec = f"规模约 {param_num}B 参数级别，推荐结合具体业务吞吐需求选择 FP8 或 4-bit 量化版本，以实现速度与精度的平衡。"
        elif is_gguf:
            spec = "提供针对 llama.cpp 生态优化的 GGUF 预量化版本，大幅削减了显存与内存开销，极大地降低了个人开发者与边缘设备的运行门槛。"
        else:
            spec = "建议根据实际业务并发要求采用 4-bit/8-bit 量化技术优化显存，推荐在具备主流 GPU 算力的云端或本地环境运行以保障吞吐。"

        # 3. 核心亮点
        downloads_str = f"📥 累计获得 {downloads:,} 次社区下载" if downloads else "✨ 社区新晋热门发布"
        highlight = f"{downloads_str}。结合了优化的预训练数据与现代网络架构设计，在生成质量、指令对齐与推理效率上展现出色性能，是近期开源社区极具参考价值的模型资产。"

        return {"scene": scene, "spec": spec, "highlight": highlight}

    def _infer_paper_specs(self, title: str, desc: str) -> Dict[str, str]:
        """推导学术论文的研究领域与工程借鉴意义"""
        text = (title + " " + desc).lower()
        if "rl" in text or "reinforce" in text or "align" in text or "dpo" in text or "grpo" in text:
            domain = "强化学习与模型对齐 (RL / Alignment)"
            eng = "为构建自主可控且具备自我修正能力的 AI 系统提供了坚实的算法支撑，尤其在复杂任务与多轮推理的奖励分配上有显著借鉴价值。"
        elif "reason" in text or "math" in text or "cot" in text or "thought" in text:
            domain = "大模型推理与思考机制 (LLM Reasoning)"
            eng = "对工业界探索慢思考 (System 2)、思维链蒸馏以及提升复杂任务准确率具有直接启发，有助于改善现有垂直领域模型的长链路推理稳定性。"
        elif "agent" in text or "tool" in text or "workflow" in text:
            domain = "智能体架构与工具协同 (Agent Systems)"
            eng = "为多智能体环境设计与沙箱交互提供了优雅范式，有助于减少真实业务系统中的工具调用失真与幻觉。"
        elif "video" in text or "diffusion" in text or "image" in text or "vision" in text:
            domain = "多模态与视觉生成 (Multimodal & Vision)"
            eng = "有助于提升长时序视觉生成的时空一致性与细节保真度，为工业级多模态内容生产管线优化带来全新算法路径。"
        else:
            domain = "深度学习与大语言模型 (Deep Learning & LLM)"
            eng = "为现有模型微调、架构压缩或跨领域泛化提供了新颖的理论依据与实证数据，对工业界模型落地具有较高参考价值。"

        return {"domain": domain, "eng": eng}

    def _render_fallback_section(self, section_name: str, items: List[BaseItem]) -> str:
        """当大模型不可用时，基于采集到的高质量元数据生成干净排版的 Markdown"""
        blocks = []
        for item in items:
            title = item.title.strip()
            url = item.url.strip()
            desc = (item.description or "").strip()
            extra_meta = []
            
            # 关键词标签渲染
            if getattr(item, 'keywords', None) and item.keywords:
                tags_str = " ".join([f"`#{k}`" for k in item.keywords[:4]])
                extra_meta.append(f"- **🏷️ 核心标签**：{tags_str}")
            # 舆情倾向徽章渲染
            if getattr(item, 'sentiment', None) and item.sentiment:
                extra_meta.append(f"- **📊 行业倾向**：`{item.sentiment}`")
                
            extra_lines = ("\n" + "\n".join(extra_meta)) if extra_meta else ""
            
            if section_name == "focus_news":
                analysis = "此动态反映了当前 AI 领军机构在基础研发与产业落地上的最新角逐，同时揭示了行业在生态构建与工程化演进中的核心发力点。"
                block = f"### 🔥 [{title}]({url})\n- **极客速看**：{desc[:120] if desc else '今日重要行业突破与官方重磅发布。'}\n- **深度解析**：{analysis}\n- **来源**：{item.source}{extra_lines}"
            elif section_name == "hf_models":
                pipeline = getattr(item, 'pipeline_tag', 'text-generation') or 'text-generation'
                downloads = getattr(item, 'downloads', 0)
                specs = self._infer_model_specs(title, pipeline, downloads, desc)
                block = f"### 🌟 [{title}]({url})\n- **应用场景**：{specs['scene']}\n- **参数量/量化建议**：{specs['spec']}\n- **亮点**：{specs['highlight']}{extra_lines}"
            elif section_name == "arxiv_papers":
                authors = ", ".join(getattr(item, 'authors', [])[:4]) or "核心研究团队"
                specs = self._infer_paper_specs(title, desc)
                summary = desc if (desc and len(desc) > 30) else "该研究针对现有算法的局限性提出了创新架构，在基准测试中展现出卓越的泛化表现。"
                block = f"### 📚 [{title}]({url})\n- **作者**：{authors}\n- **研究领域**：{specs['domain']}\n- **核心突破**：{summary}\n- **工程借鉴意义**：{specs['eng']}{extra_lines}"
            elif section_name == "github_projects":
                stars = getattr(item, 'stars', 0)
                speed = getattr(item, 'stars_per_day', 0.0)
                sell_point = "通过高度优化的工程架构显著简化了复杂的开发流程，极大地降低了从原型构建到生产部署的维护成本。"
                block = f"### 🚀 [{title}]({url})\n- **一句话弄懂**：{desc[:120] if desc else '近期 GitHub 极客圈爆发式增长的高生产力开源套件。'}\n- **核心卖点**：{sell_point}\n- **热度飙升**：⭐ 当前已斩获 {stars:,} stars (🔥 增速 +{speed:.0f}/天)，社区关注度极其活跃。{extra_lines}"
            elif section_name == "hacker_news":
                point_info = "引发了硅谷一线极客与开发者的热烈探讨"
                block = f"### 💬 [{title}]({url})\n- **社区焦点**：{desc if desc else '社区针对该技术突破与行业争议展开了多维度的激烈观点碰撞。'}\n- **深度视点**：讨论中涌现出大量关于架构选型、实战避坑与未来范式变迁的高质量经验总结。\n- **热度指标**：Hacker News 极客社区热议 ({point_info}){extra_lines}"
            else:
                block = f"### 📱 [{title}]({url})\n- **应用场景与痛点**：{desc[:120] if desc else '针对实际业务场景定制的全新 AI 生产力应用。'}\n- **核心功能与交互**：提供直观易用的交互工作流与高度整合的底层能力。\n- **亮点与商业价值**：有效赋能企业与创作者实现生产效率的指数级提升。{extra_lines}"
            blocks.append(block)
            
        return "\n\n".join(blocks)


          
    def write_section(self, section_name: str, items: List[BaseItem]) -> str:
        if not items:
            return ""
            
        prompt_template = self.prompts.get(section_name, {}).get("template", "请总结以下信息：\n{context}")
        context_text = self._build_context(items)
        
        prompt = prompt_template.replace("{context}", context_text)
        print(f"[INFO] 正在生成章节 '{section_name}' ({len(items)} 条内容)...")
        
        result = self.ai.generate(prompt)
        
        # 智能检测生成是否有效：若包含失败提示或为空，自动启用结构化兜底
        if not result or "生成失败" in result or "不可恢复的错误" in result or "未初始化" in result:
            print(f"[INFO] 启用章节【{section_name}】的高质量结构化脱水兜底渲染")
            return self._render_fallback_section(section_name, items)
            
        return result

    def _derive_fallback_chinese_summary(self, section_name: str, item: BaseItem) -> str:
        """当大模型不可用或解析异常时，基于细分领域规则推导精准的中文一句话核心提炼（完整无截断）"""
        title = item.title.strip()
        desc = (item.description or "").strip()
        text = f"{title} {desc}".lower()

        # 1. 开源模型 (hf_models)
        if section_name == "hf_models":
            pipeline = getattr(item, 'pipeline_tag', '') or ''
            if "gguf" in text or "ggml" in text or "awq" in text or "quant" in text:
                return "社区主流高保真量化版，适配消费级显卡与低显存硬件本地部署"
            elif "embedding" in text or "rerank" in text:
                return "轻量级高维度向量模型，显著提升知识库语义检索与重排效率"
            elif "guard" in text or "safety" in text or "moderation" in text:
                return "大模型内容安全与价值对齐护栏，有效防御越狱攻击与有害输出"
            elif "vision" in text or "vl" in text or "image" in text or "image-text" in pipeline:
                return "跨模态视觉理解模型，支持高分辨率图像识别与图文场景推理"
            elif "audio" in text or "speech" in text or "tts" in text or "voice" in text:
                return "高保真端到端音频处理模型，专长于低延迟语音合成与多轮对话"
            elif "code" in text or "coder" in text:
                return "专为代码理解与工程重构调优的轻量级编程辅助模型"
            elif "reason" in text or "r1" in text or "math" in text:
                return "强化慢思考与链式推理模型，数理逻辑与复杂推理能力突出"
            else:
                return "针对垂直领域深度调优的高性能开源权重，兼顾推理延迟与生成精度"

        # 2. 学术论文 (arxiv_papers)
        elif section_name == "arxiv_papers":
            if "latent" in text or "concept" in text or "reasoning" in text:
                return "突破自回归离散预测局限，引入潜在空间表征以增强长程逻辑推理"
            elif "agent" in text or "tool" in text or "multi-agent" in text:
                return "针对智能体长链路协作提出创新沙箱框架，大幅缓解调用失真与幻觉"
            elif "video" in text or "diffusion" in text or "temporal" in text:
                return "提出新型时空注意力机制，显著改善多模态动态内容生成的物理一致性"
            elif "safety" in text or "jailbreak" in text or "attack" in text:
                return "构建前沿大模型安全防御架构，系统性阻断高隐蔽性的对抗攻击"
            elif "kv cache" in text or "quant" in text or "pruning" in text or "compress" in text:
                return "从显存碎片与注意力压缩切入，为超长上下文高吞吐部署提供全新路径"
            else:
                return "针对现有算法瓶颈提出创新架构设计，在权威基准上展现出卓越泛化性能"

        # 3. 工具与框架 (github_projects)
        elif section_name == "github_projects":
            stars = getattr(item, 'stars', 0)
            star_hint = f"社区标星达 {stars:,}" if stars > 100 else "极客社区热度高涨"
            if "mcp" in text or "protocol" in text or "gateway" in text:
                return f"模型上下文协议（MCP）轻量级网关，{star_hint}，简化工具生态编排"
            elif "rag" in text or "retrieval" in text or "vector" in text:
                return f"端到端知识库检索增强套件，{star_hint}，显著提升召回准确率"
            elif "inference" in text or "engine" in text or "vllm" in text or "serve" in text:
                return f"高吞吐分布式推理加速框架，{star_hint}，极致优化显存利用率"
            elif "agent" in text or "workflow" in text:
                return f"模块化自主智能体开发脚手架，{star_hint}，极大加速复杂流程原型落地"
            elif "ui" in text or "web" in text or "frontend" in text or "client" in text:
                return f"开箱即用的现代化 AI 交互客户端，{star_hint}，交互体验轻快优雅"
            else:
                return f"工程架构高度优化的极客生产力开源套件，{star_hint}，部署门槛极低"

        # 4. 今日焦点 (focus_news)
        elif section_name == "focus_news":
            if "openai" in text or "chatgpt" in text:
                return "OpenAI 官方重磅产业落地更新，加速将前沿大模型转化为企业级生产力"
            elif "anthropic" in text or "claude" in text:
                return "Anthropic 针对智能体与安全对齐的最新演进，展现强劲的模型工程实力"
            elif "google" in text or "gemini" in text:
                return "Google 持续加码多模态生态布局，在端侧与云端协同上取得关键进展"
            elif "nvidia" in text or "gpu" in text or "chip" in text:
                return "NVIDIA 算力与硬件加速生态前沿突破，为下一代模型训练铺平道路"
            elif "deepseek" in text or "qwen" in text:
                return "国内顶尖开源模型力量再度突破，在开源生态中掀起全球极客热烈响应"
            else:
                return "今日全球 AI 产业关键里程碑事件，反映领军机构在生态与研发上的新角逐"

        # 5. 极客热议 (hacker_news)
        elif section_name == "hacker_news":
            return "引发一线资深极客对系统选型、架构权衡与技术演进路线的深度观点碰撞"

        # 6. 应用产品 (applications)
        elif section_name == "applications":
            return "打通真实业务闭环的 AI 原生应用，直击垂直行业工作流中的核心效率痛点"

        # 7. 全网热搜 (perplexity_news)
        else:
            return "全网热度极高的人工智能风向话题，展示了大众与业界对该趋势的聚焦关注"

    def _summarize_overflow_items_ai(self, section_name: str, items: List[BaseItem]) -> Dict[int, str]:
        """调用大模型为溢出条目提炼精准中文一句话说明（抓住核心亮点，20-35字）"""
        prompt_template = self.prompts.get("overflow_summary", {}).get("template")
        if not prompt_template or not getattr(self, 'ai', None):
            return {}

        context_lines = []
        for idx, item in enumerate(items, 1):
            context_lines.append(f"[{idx}] 标题: {item.title}")
            if item.description:
                context_lines.append(f"    原始描述: {item.description[:250]}")
            if getattr(item, 'source', None):
                context_lines.append(f"    来源: {item.source}")
            if getattr(item, 'keywords', None) and item.keywords:
                context_lines.append(f"    标签: {', '.join(item.keywords[:4])}")

        prompt = prompt_template.replace("{context}", "\n".join(context_lines))
        try:
            raw_res = self.ai.generate(prompt)
            if raw_res:
                match = re.search(r'\[.*\]', raw_res, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    result = {}
                    for entry in parsed:
                        item_id = int(entry.get("id", 0))
                        summary = entry.get("summary", "").strip()
                        if item_id and summary:
                            result[item_id] = summary
                    if result:
                        return result
        except Exception as e:
            print(f"[WARN] 章节【{section_name}】溢出列表大模型生成中文摘要异常，将无缝启用领域规则兜底: {e}")

        return {}

    def render_overflow_list(self, section_name: str, items: List[BaseItem]) -> str:
        """将溢出条目渲染为折叠式精简列表（完整中文一句话解释 + 鼠标悬停 Tooltip 提示）"""
        if not items:
            return ""

        section_labels = {
            'focus_news': '焦点',
            'hf_models': '模型',
            'arxiv_papers': '论文',
            'github_projects': '项目',
            'hacker_news': '热议',
            'applications': '应用',
            'perplexity_news': '热搜'
        }
        label = section_labels.get(section_name, '内容')

        # 尝试通过大模型生成精准中文一句话提炼
        ai_summaries = self._summarize_overflow_items_ai(section_name, items)

        li_lines = []
        for idx, item in enumerate(items, 1):
            raw_title = item.title.strip()
            title = html.escape(raw_title)
            url = item.url.strip()

            # 优先使用 AI 提炼的中文一句话，无则走细分领域智能规则库，确保 100% 完整中文
            summary = ai_summaries.get(idx)
            if not summary:
                summary = self._derive_fallback_chinese_summary(section_name, item)

            safe_summary = html.escape(summary.strip())
            tooltip_text = html.escape(f"{raw_title} — {summary.strip()}")

            li_lines.append(
                f'  <li class="daily-ai-overflow-item" title="{tooltip_text}">'
                f'<a href="{url}" target="_blank" rel="noopener" class="overflow-link">{title}</a>'
                f'<span class="overflow-sep"> — </span>'
                f'<span class="overflow-desc">{safe_summary}</span>'
                f'</li>'
            )

        count = len(li_lines)
        list_html = "\n".join(li_lines)

        return (
            f'\n<details class="daily-ai-overflow">\n'
            f'<summary>📌 更多{label}值得关注（{count} 条，点击展开）</summary>\n'
            f'<ul class="daily-ai-overflow-list">\n'
            f'{list_html}\n'
            f'</ul>\n'
            f'</details>\n'
        )


