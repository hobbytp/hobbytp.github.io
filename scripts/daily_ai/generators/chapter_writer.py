import yaml
from pathlib import Path
from typing import Dict, Any, List
from scripts.daily_ai.generators.ai_client import AIClient
from scripts.daily_ai.models import BaseItem

class ChapterWriter:
    """章节生成引擎：根据不同章节调用特定 Prompt 和大模型"""
    
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
             if hasattr(item, 'stars'):
                 context_lines.append(f"    Stars数量/增长: {item.stars} ({getattr(item, 'stars_per_day', 0):.1f}/day)")
             if hasattr(item, 'authors') and item.authors:
                 context_lines.append(f"    作者: {', '.join(getattr(item, 'authors', []))}")
             context_lines.append("")
         return "\n".join(context_lines)
         
    def write_section(self, section_name: str, items: List[BaseItem]) -> str:
         if not items:
             return ""
             
         prompt_template = self.prompts.get(section_name, {}).get("template", "请总结以下信息：\n{context}")
         context_text = self._build_context(items)
         
         prompt = prompt_template.replace("{context}", context_text)
         print(f"[INFO] 正在生成章节 '{section_name}' ({len(items)} 条内容)...")
         return self.ai.generate(prompt)
