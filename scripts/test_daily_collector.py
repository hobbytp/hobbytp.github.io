#!/usr/bin/env python3
"""
测试每日AI收集器
"""
import os
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置测试环境变量（如果没有的话）
if not os.getenv('GEMINI_API_KEY'):
    print("WARNING: GEMINI_API_KEY 未设置，测试将使用fallback模式")

if not os.getenv('GITHUB_TOKEN'):
    print("WARNING: GITHUB_TOKEN 未设置，将跳过GitHub搜索")

if not os.getenv('HUGGINGFACE_API_KEY'):
    print("WARNING: HUGGINGFACE_API_KEY 未设置，将跳过HF搜索")

print("\n" + "="*60)
print("开始测试每日AI收集器")
print("="*60 + "\n")

from daily_ai_collector import DailyAICollector

try:
    collector = DailyAICollector()
    print("\n✅ 收集器初始化成功\n")
    
    # 测试数据收集
    print("测试数据收集...")
    collected_data = {
        'github_projects': collector.search_github_trending(),
        'hf_models': collector.search_huggingface_models(),
        'arxiv_papers': collector.search_arxiv_papers()
    }
    
    print("\n数据收集结果:")
    print(f"  - GitHub项目: {len(collected_data['github_projects'])} 个")
    print(f"  - HF模型: {len(collected_data['hf_models'])} 个")
    print(f"  - ArXiv论文: {len(collected_data['arxiv_papers'])} 个")
    
    # 测试AI摘要生成
    print("\n测试AI摘要生成...")
    summary = collector.generate_ai_summary(collected_data)
    
    if summary and summary != "None":
        print(f"\n✅ 摘要生成成功，长度: {len(summary)} 字符")
        print("\n摘要预览（前500字符）:")
        print("-" * 60)
        print(summary[:500])
        print("-" * 60)
    else:
        print("\n❌ 摘要生成失败或返回None")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
