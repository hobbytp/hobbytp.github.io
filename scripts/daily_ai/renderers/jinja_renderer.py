from typing import Dict, Any
from pathlib import Path
import jinja2

class JinjaRenderer:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染指定的 Jinja2 模板
        :param template_name: 模板文件名，例如 'default.md.j2'
        :param context: 注入模板的变量字典
        :return: 渲染后的文本
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            print(f"[ERROR] 模板渲染失败 ({template_name}): {e}")
            return f"> 模板渲染错误: {e}"
