#!/usr/bin/env python3
"""
每日AI动态收集脚本 V3.5 (Multi-source High-SNR Pipeline)
核心特性:
- 多源高信噪比采集: 官方一手实验室 RSS + Hacker News 极客热榜 + HF Models/Daily Papers + GitHub 星速爆发榜 + Product Hunt 落地应用
- 质量评分雷达 2.0 & 语义模糊排重: 四维打分加权 + 追踪参数清洗 + 历史状态持久化
- 健壮的容灾策略: 主模型 (Gemini 2.5) 异常时自动降级到备用模型 (DashScope / OpenAI) 并支持高质量结构化脱水兜底渲染
- 动态 Prompt 注入: 根据不同内容板块自动分配专业角色 Persona
- 现代化卡片 UI: 作用域隔离样式、60秒极客速览、快速胶囊锚点导航
"""

import sys
import os
import warnings
from pathlib import Path

# 过滤第三方库 (ai_news_collector_lib 等) 内部导入旧版 SDK 触发的 FutureWarning 噪音
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

# 添加项目根目录到 Python Path 以支持包导入
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.daily_ai.main import Orchestrator


if __name__ == "__main__":
    print("============================================")
    print("🚀 Starting Daily AI Collector V3.5 (Pipeline)")
    print("============================================")
    
    try:
        orchestrator = Orchestrator()
        orchestrator.run()
        print("============================================")
        print("✅ 任务顺利完成 (V3.5)")
        print("============================================")

    except Exception as e:
        print(f"❌ 运行过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
