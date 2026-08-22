#!/usr/bin/env python3
"""
快速诊断与验证 AI API 连接状态 (支持 Google genai, OpenAI, DashScope, SiliconFlow)
"""
import os
import sys
import warnings

# 过滤废弃告警
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")


print("="*60)
print("🤖 博客 AI 接口诊断工具 (Multi-Provider)")
print("="*60)

# 1. 检查环境变量
print("\n1. 环境变量检查:")
keys = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'DASHSCOPE_API_KEY': os.getenv('DASHSCOPE_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'SILICONFLOW_API_KEY': os.getenv('SILICONFLOW_API_KEY'),
    'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
}

for name, val in keys.items():
    if val:
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
        print(f"   ✅ {name}: 已设置 (长度: {len(val)}, 预览: {masked})")
    else:
        print(f"   ⚪ {name}: 未设置")

# 2. 测试 Google GenAI (新官方 SDK)
print("\n2. 测试 Google GenAI 官方接口 (google-genai):")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key.strip())
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='用一句话回答：1+1等于几？'
        )
        ans = response.text if hasattr(response, 'text') else str(response)
        print(f"   ✅ Google Gemini API 调用成功！")
        print(f"   回复内容: {ans.strip()[:100]}")
    except Exception as e:
        print(f"   ❌ Google Gemini API 调用失败: {e}")
        if "API key not valid" in str(e) or "INVALID_ARGUMENT" in str(e):
            print("   💡 提示: 您的 GEMINI_API_KEY 无效或已失效，请前往 Google AI Studio (https://aistudio.google.com/) 重新生成并更新到 GitHub Secrets。")
else:
    print("   ⚪ 跳过（未设置 GEMINI_API_KEY）")

# 3. 测试 DashScope (通义千问备用模型)
print("\n3. 测试 DashScope / 兼容接口:")
dashscope_key = os.getenv('DASHSCOPE_API_KEY')
if dashscope_key:
    try:
        import openai
        client = openai.OpenAI(
            api_key=dashscope_key.strip(),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": "用一句话回答：1+1等于几？"}],
            max_tokens=60
        )
        ans = response.choices[0].message.content if response.choices else ""
        print(f"   ✅ DashScope 通义千问调用成功！")
        print(f"   回复内容: {ans.strip()[:100]}")
    except Exception as e:
        print(f"   ❌ DashScope API 调用失败: {e}")
else:
    print("   ⚪ 跳过（未设置 DASHSCOPE_API_KEY）")

# 4. 测试 OpenAI / SiliconFlow
print("\n4. 测试 OpenAI / SiliconFlow 接口:")
openai_key = os.getenv('OPENAI_API_KEY')
silicon_key = os.getenv('SILICONFLOW_API_KEY')

test_key = openai_key or silicon_key
base_url = "https://api.siliconflow.cn/v1" if silicon_key and not openai_key else None

if test_key:
    try:
        import openai
        client = openai.OpenAI(api_key=test_key.strip(), base_url=base_url)
        model = "deepseek-ai/DeepSeek-V3" if silicon_key and not openai_key else "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "1+1等于几？"}],
            max_tokens=60
        )
        ans = response.choices[0].message.content if response.choices else ""
        print(f"   ✅ API 调用成功！")
        print(f"   回复内容: {ans.strip()[:100]}")
    except Exception as e:
        print(f"   ❌ API 调用失败: {e}")
else:
    print("   ⚪ 跳过（未设置 OPENAI_API_KEY 或 SILICONFLOW_API_KEY）")

print("\n" + "="*60)
print("诊断完成")
print("="*60)
