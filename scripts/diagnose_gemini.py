#!/usr/bin/env python3
"""
快速诊断 Gemini API 问题
"""
import os
import sys

print("="*60)
print("Gemini API 诊断工具")
print("="*60)

# 1. 检查环境变量
print("\n1. 环境变量检查:")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"   ✅ GEMINI_API_KEY: 已设置 (长度: {len(gemini_key)})")
else:
    print("   ❌ GEMINI_API_KEY: 未设置")
    sys.exit(1)

# 2. 检查库安装
print("\n2. 库安装检查:")
try:
    import google.generativeai as genai
    print(f"   ✅ google-generativeai: {genai.__version__}")
    has_genai = True
except ImportError as e:
    print(f"   ❌ google-generativeai: 未安装 ({e})")
    has_genai = False

try:
    import openai
    print(f"   ✅ openai: {openai.__version__}")
    has_openai = True
except ImportError as e:
    print(f"   ❌ openai: 未安装 ({e})")
    has_openai = False

# 3. 测试 Google SDK（如果可用）
if has_genai:
    print("\n3. 测试 Google SDK:")
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content("用中文回复：你好，请说一句话")
        print(f"   ✅ API 调用成功")
        print(f"   响应类型: {type(response)}")
        print(f"   响应内容: {response.text[:100] if hasattr(response, 'text') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()

# 4. 测试 OpenAI 兼容接口（如果 Google SDK 不可用）
if has_openai and not has_genai:
    print("\n4. 测试 OpenAI 兼容接口:")
    try:
        client = openai.OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[{"role": "user", "content": "用中文回复：你好，请说一句话"}],
            max_tokens=100
        )
        print(f"   ✅ API 调用成功")
        print(f"   响应类型: {type(response)}")
        print(f"   Choices: {len(response.choices)}")
        if response.choices:
            print(f"   内容: {response.choices[0].message.content}")
            print(f"   Finish reason: {response.choices[0].finish_reason}")
    except Exception as e:
        print(f"   ❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("诊断完成")
print("="*60)
