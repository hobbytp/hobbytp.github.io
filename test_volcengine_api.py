#!/usr/bin/env python3
"""测试火山引擎API"""

import os
import sys
from pathlib import Path

# 加载.env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

# 导入配置
from scripts.ai_cover_generator import ImageGenConfig, CoverImageGenerator

# 创建配置
config = ImageGenConfig(
    api_provider="volcengine",
    volcengine_access_key=os.getenv("VOLCENGINE_ACCESS_KEY", ""),
    volcengine_secret_key=os.getenv("VOLCENGINE_SECRET_KEY", ""),
    volcengine_model=os.getenv("VOLCENGINE_MODEL", "jimeng_t2i_v40"),
)

print("=" * 60)
print("火山引擎API测试")
print("=" * 60)
print(f"API Provider: {config.api_provider}")
print(f"Access Key: {config.volcengine_access_key[:20]}..." if config.volcengine_access_key else "Access Key: NOT SET")
print(f"Secret Key: {config.volcengine_secret_key[:20]}..." if config.volcengine_secret_key else "Secret Key: NOT SET")
print(f"Model: {config.volcengine_model}")
print("=" * 60)

# 测试生成
generator = CoverImageGenerator(config)

# 使用简单的测试内容
test_title = "Test Image Generation"
test_description = "This is a simple test to verify Volcengine API works correctly"
test_category = "test"

print("\n开始测试图片生成...")
print(f"Title: {test_title}")
print(f"Description: {test_description}")
print(f"Category: {test_category}")
print()

result = generator.generate_cover(test_title, test_description, test_category, force=True)

if result:
    print(f"\n✅ 成功! 图片路径: {result}")
else:
    print(f"\n❌ 失败! API调用未返回图片")

sys.exit(0 if result else 1)
