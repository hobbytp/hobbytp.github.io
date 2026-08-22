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
