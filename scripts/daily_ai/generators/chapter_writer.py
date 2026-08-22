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
                block = f"### 🔥 [{title}]({url})\n- **⚡ 极客速看**：{desc[:120] if desc else '今日重要行业发布'}\n- **🏷️ 信源**：{item.source}{extra_lines}"
            elif section_name == "hf_models":
                pipeline = getattr(item, 'pipeline_tag', 'text-generation') or 'text-generation'
                downloads = getattr(item, 'downloads', 0)
                block = f"### 🌟 [{title}]({url})\n- **🎯 任务类型**：`{pipeline}`\n- **✨ 社区热度**：📥 {downloads:,} 次下载\n- **🔗 快速通道**：[前往 Hugging Face 模型卡片]({url}){extra_lines}"
            elif section_name == "arxiv_papers":
                authors = ", ".join(getattr(item, 'authors', [])[:4]) or "研究团队"
                block = f"### 📚 [{title}]({url})\n- **👥 作者与机构**：{authors}\n- **🔬 核心摘要**：{desc[:200]}...\n- **📄 论文直达**：[查看原文/PDF]({url}){extra_lines}"
            elif section_name == "github_projects":
                stars = getattr(item, 'stars', 0)
                speed = getattr(item, 'stars_per_day', 0.0)
                block = f"### 🚀 [{title}]({url})\n- **⚡ 项目定位**：{desc[:150]}\n- **📈 社区热度**：⭐ {stars:,} stars (🔥 +{speed:.0f}/天)\n- **📦 开源仓库**：[GitHub 代码库]({url}){extra_lines}"
            elif section_name == "hacker_news":
                block = f"### 💬 [{title}]({url})\n- **🔥 社区讨论**：{desc}\n- **🏷️ 来源**：Hacker News 极客社区{extra_lines}"
            else:
                block = f"### 📱 [{title}]({url})\n- **💡 简述**：{desc[:150]}\n- **🏷️ 来源**：{item.source}{extra_lines}"
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
