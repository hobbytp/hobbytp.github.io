#!/usr/bin/env python3
"""
测试环境变量加载
"""

import os
from pathlib import Path

# 加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("使用python-dotenv加载环境变量")
except ImportError:
    print("python-dotenv未安装，使用手动方式加载.env文件")
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")
        print("已手动加载.env文件")
    else:
        print(".env文件不存在")

# 测试关键环境变量
print(f"TEXT2IMAGE_PROVIDER: {os.getenv('TEXT2IMAGE_PROVIDER')}")
api_key_preview = os.getenv('MODELSCOPE_API_KEY')
if api_key_preview:
    print(f"MODELSCOPE_API_KEY: {api_key_preview[:20]}...")
else:
    print("MODELSCOPE_API_KEY: Not set")

# 测试ModelScope API调用
import requests
import json

api_key = os.getenv("MODELSCOPE_API_KEY")
if api_key:
    print(f"API密钥已加载，长度: {len(api_key)}")

    # 测试API连接
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api-inference.modelscope.cn/v1/images/generations",
            headers={**headers, "X-ModelScope-Async-Mode": "true"},
            data=json.dumps({
                "model": "Qwen/Qwen-Image",
                "prompt": "A golden cat"
            }, ensure_ascii=False).encode('utf-8'),
            timeout=10
        )

        if response.status_code == 200:
            print("✅ ModelScope API连接成功")
            task_data = response.json()
            print(f"任务ID: {task_data.get('task_id', 'N/A')}")
        else:
            print(f"❌ API连接失败: {response.status_code}")
            print(f"响应: {response.text}")

    except Exception as e:
        print(f"❌ API测试异常: {e}")
else:
    print("❌ MODELSCOPE_API_KEY未找到")

print("环境变量测试完成")