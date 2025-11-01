#!/usr/bin/env python
import os
import sys

# 添加路径
sys.path.append('tools/content-analysis')

try:
    from content_analyzer import ContentAnalyzer
    print('正在初始化ContentAnalyzer...')
    analyzer = ContentAnalyzer('./content')
    print('✅ ContentAnalyzer初始化成功')

    if analyzer.openai_client:
        print(f'✅ OpenAI客户端已配置 (模型: {analyzer.openai_model})')
        print(f'   API端点: {os.getenv("OPENAI_BASE_URL", "默认")}')
    else:
        print('⚠️  OpenAI客户端未配置')

except Exception as e:
    print(f'❌ 初始化失败: {e}')
    import traceback
    traceback.print_exc()
