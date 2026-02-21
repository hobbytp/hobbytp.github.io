#!/usr/bin/env python3
"""
每日AI动态收集脚本 V3.0 (Architectural Redesign)
核心特性:
- MVC 架构解耦: 模型、获取、处理、生成、渲染完全分离
- 健壮的容灾策略: 主模型 (Gemini) 异常时自动降级到备用模型 (DashScope Qwen Max)
- 动态 Prompt 注入: 根据不同内容板块自动分配不同的人设 Persona
- 模板化输出: 基于 Jinja2 模板，彻底剥离 HTML/MD 硬编码
- 多源去重与智能评分: ArXiv, GitHub, HuggingFace 多维数据融合
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python Path 以支持包导入
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.daily_ai.main import Orchestrator

if __name__ == "__main__":
    print("============================================")
    print("🚀 Starting Daily AI Collector V3.0 (Pipeline)")
    print("============================================")
    
    try:
        orchestrator = Orchestrator()
        orchestrator.run()
        print("============================================")
        print("✅ 任务顺利完成 (V3.0)")
        print("============================================")
    except Exception as e:
        print(f"❌ 运行过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
