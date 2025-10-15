#!/usr/bin/env python3
"""
测试 Gemini API 连接
"""
import os
import openai

print("测试 Gemini API 连接...")
print(f"API Key 长度: {len(os.getenv('GEMINI_API_KEY', ''))}")

try:
    client = openai.OpenAI(
        api_key=os.getenv('GEMINI_API_KEY'),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    print("\n尝试调用 Gemini API...")
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "请用中文回复：你好"}],
        max_tokens=100
    )
    
    content = response.choices[0].message.content
    print(f"\n✅ API 调用成功！")
    print(f"返回内容: {content}")
    print(f"内容长度: {len(content)}")
    print(f"内容类型: {type(content)}")
    
except Exception as e:
    print(f"\n❌ API 调用失败: {e}")
    import traceback
    traceback.print_exc()
