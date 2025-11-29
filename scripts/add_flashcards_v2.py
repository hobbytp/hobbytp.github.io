#!/usr/bin/env python3
"""
闪卡生成器 - 将 CSV 格式的 Q&A 数据转换为 Hugo shortcode 并插入博客文章
支持 AI 自动生成闪卡（Gemini / OpenRouter / OpenAI Compatible）

用法:
    # 从 CSV 文件添加闪卡
    python add_flashcards.py <博客文件路径> <CSV文件路径>
    
    # 使用 AI 自动生成闪卡
    python add_flashcards.py <博客文件路径> --generate
    python add_flashcards.py <博客文件路径> --generate --provider openrouter --model anthropic/claude-3.5-sonnet
    python add_flashcards.py <博客文件路径> --generate --provider openai --base-url http://localhost:11434/v1

环境变量:
    GEMINI_API_KEY     - Google Gemini API 密钥 (默认)
    OPENROUTER_API_KEY - OpenRouter API 密钥
    OPENAI_API_KEY     - OpenAI 兼容 API 密钥

CSV 格式要求:
    第一列: 问题 (Question)
    第二列: 答案 (Answer)
    支持带或不带表头

示例:
    python scripts/add_flashcards.py content/zh/posts/my-article.md flashcards.csv
    python scripts/add_flashcards.py content/zh/posts/my-article.md --generate
    python scripts/add_flashcards.py content/zh/posts/my-article.md --generate --count 20
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# ============================================================================
# AI Provider Implementations
# ============================================================================

def generate_with_gemini(content: str, count: int, model: str) -> List[Tuple[str, str]]:
    """使用 Google Gemini API 生成闪卡"""
    try:
        from google import genai
    except ImportError:
        print("错误: 请安装 google-genai 库: pip install google-genai")
        sys.exit(1)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误: 请设置 GEMINI_API_KEY 环境变量")
        sys.exit(1)
    
    client = genai.Client(api_key=api_key)
    
    prompt = create_qa_prompt(content, count)
    
    print(f"   使用模型: {model}")
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    
    return parse_qa_response(response.text)


def generate_with_openrouter(content: str, count: int, model: str) -> List[Tuple[str, str]]:
    """使用 OpenRouter API 生成闪卡"""
    import requests
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("错误: 请设置 OPENROUTER_API_KEY 环境变量")
        sys.exit(1)
    
    prompt = create_qa_prompt(content, count)
    
    print(f"   使用模型: {model}")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hobbytp/hobbytp.github.io",
            "X-Title": "Flashcard Generator",
        },
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
        },
        timeout=120,
    )
    
    if response.status_code != 200:
        print(f"错误: API 请求失败 ({response.status_code}): {response.text}")
        sys.exit(1)
    
    data = response.json()
    return parse_qa_response(data["choices"][0]["message"]["content"])


def generate_with_openai_compatible(
    content: str, 
    count: int, 
    model: str, 
    base_url: str
) -> List[Tuple[str, str]]:
    """使用 OpenAI 兼容 API 生成闪卡（支持 Ollama, vLLM, LocalAI 等）"""
    import requests
    
    api_key = os.getenv("OPENAI_API_KEY", "sk-no-key-required")
    
    prompt = create_qa_prompt(content, count)
    
    # 确保 base_url 以 /v1 结尾
    if not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"
    
    print(f"   使用模型: {model}")
    print(f"   API 地址: {base_url}")
    
    response = requests.post(
        url=f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
        },
        timeout=300,  # 本地模型可能较慢
    )
    
    if response.status_code != 200:
        print(f"错误: API 请求失败 ({response.status_code}): {response.text}")
        sys.exit(1)
    
    data = response.json()
    return parse_qa_response(data["choices"][0]["message"]["content"])


# ============================================================================
# Prompt and Parsing
# ============================================================================

def create_qa_prompt(content: str, count: int) -> str:
    """创建生成 Q&A 对的提示词"""
    return f"""你是一个专业的教育内容专家。请仔细阅读以下技术文章，然后生成 {count} 个高质量的问答对（闪卡），用于帮助读者复习和巩固文章中的关键知识点。

要求：
1. 问题应该涵盖文章的核心概念、关键技术、重要结论
2. 问题应该清晰具体，避免模糊或过于宽泛
3. 答案应该简洁准确，通常 1-3 句话即可
4. 避免问题中包含英文双引号 "，如需引用请使用中文书名号『』
5. 答案可以使用 Markdown 格式（如 **加粗**、$公式$）

请严格按照以下 JSON 格式输出，不要包含其他内容：

```json
[
  {{"question": "问题1", "answer": "答案1"}},
  {{"question": "问题2", "answer": "答案2"}}
]
```

---

文章内容：

{content}

---

请生成 {count} 个问答对："""


def parse_qa_response(response_text: str) -> List[Tuple[str, str]]:
    """解析 AI 返回的 JSON 格式 Q&A 数据"""
    # 尝试提取 JSON 块
    json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response_text)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试直接解析
        json_str = response_text.strip()
    
    try:
        data = json.loads(json_str)
        qa_pairs = []
        for item in data:
            question = item.get("question", "").strip()
            answer = item.get("answer", "").strip()
            if question and answer:
                qa_pairs.append((question, answer))
        return qa_pairs
    except json.JSONDecodeError as e:
        print(f"警告: JSON 解析失败: {e}")
        print(f"原始响应: {response_text[:500]}...")
        return []


# ============================================================================
# CSV and Shortcode Generation
# ============================================================================

def read_csv(csv_path: str) -> List[Tuple[str, str]]:
    """读取 CSV 文件，返回 (问题, 答案) 列表"""
    qa_pairs = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # 尝试检测是否有表头
        sample = f.read(1024)
        f.seek(0)
        
        # 使用 csv.Sniffer 检测格式
        try:
            dialect = csv.Sniffer().sniff(sample)
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            dialect = csv.excel
            has_header = False
        
        reader = csv.reader(f, dialect)
        
        # 跳过表头（如果有）
        if has_header:
            next(reader)
        
        for row in reader:
            if len(row) >= 2:
                question = row[0].strip()
                answer = row[1].strip()
                if question and answer:
                    qa_pairs.append((question, answer))
    
    return qa_pairs


def escape_shortcode_param(text: str) -> str:
    """
    转义 shortcode 参数中的特殊字符
    - 将英文双引号替换为中文引号或转义
    - 将中文引号替换为书名号（避免 Hugo 解析问题）
    """
    # 替换英文双引号为中文单引号
    text = text.replace('"', "'")
    # 替换中文双引号为书名号
    text = text.replace('"', '『').replace('"', '』')
    text = text.replace('「', '『').replace('」', '』')
    return text


def generate_flashcards_shortcode(qa_pairs: List[Tuple[str, str]]) -> str:
    """生成 Hugo flashcards shortcode 代码"""
    lines = ['{{< flashcards >}}', '']
    
    for question, answer in qa_pairs:
        # 转义问题中的特殊字符
        safe_question = escape_shortcode_param(question)
        
        lines.append(f'{{{{< flashcard q="{safe_question}" >}}}}')
        lines.append(answer)
        lines.append('{{< /flashcard >}}')
        lines.append('')
    
    lines.append('{{< /flashcards >}}')
    
    return '\n'.join(lines)


def extract_blog_content(blog_path: str) -> str:
    """提取博客文章内容（去除 front matter 和已有闪卡）"""
    content = Path(blog_path).read_text(encoding='utf-8')
    
    # 移除 front matter
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
            content = content[end_idx + 3:].strip()
    
    # 移除已有闪卡
    content = re.sub(
        r'\{\{<\s*flashcards\s*>\}\}.*?\{\{<\s*/flashcards\s*>\}\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    return content.strip()


def insert_flashcards_to_blog(blog_path: str, flashcards_code: str) -> bool:
    """将闪卡代码插入博客文章末尾"""
    blog_file = Path(blog_path)
    
    if not blog_file.exists():
        print(f"错误: 博客文件不存在: {blog_path}")
        return False
    
    content = blog_file.read_text(encoding='utf-8')
    
    # 检查是否已有闪卡
    if '{{< flashcards >}}' in content:
        print("警告: 该博客已包含闪卡，将替换现有闪卡...")
        # 移除现有闪卡
        content = re.sub(
            r'\n*---\s*\n*\{\{<\s*flashcards\s*>\}\}.*?\{\{<\s*/flashcards\s*>\}\}\s*$',
            '',
            content,
            flags=re.DOTALL
        )
        content = content.rstrip()
    
    # 添加分隔线和闪卡
    new_content = content.rstrip() + '\n\n---\n\n' + flashcards_code + '\n'
    
    blog_file.write_text(new_content, encoding='utf-8')
    return True


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='为 Hugo 博客添加闪卡功能',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('blog_path', help='博客文件路径')
    parser.add_argument('csv_path', nargs='?', help='CSV 文件路径（与 --generate 互斥）')
    
    parser.add_argument('--generate', '-g', action='store_true',
                        help='使用 AI 自动生成闪卡')
    parser.add_argument('--provider', '-p', 
                        choices=['gemini', 'openrouter', 'openai'],
                        default='gemini',
                        help='AI 提供商 (默认: gemini)')
    parser.add_argument('--model', '-m',
                        help='模型名称 (默认根据 provider 自动选择)')
    parser.add_argument('--base-url',
                        help='OpenAI 兼容 API 的基础 URL (仅用于 --provider openai)')
    parser.add_argument('--count', '-c', type=int, default=15,
                        help='生成的闪卡数量 (默认: 15)')
    parser.add_argument('--output', '-o',
                        help='输出 CSV 文件路径（保存生成的 Q&A 对）')
    
    args = parser.parse_args()
    
    # 检查博客文件存在
    if not Path(args.blog_path).exists():
        print(f"错误: 博客文件不存在: {args.blog_path}")
        sys.exit(1)
    
    # 确定使用 CSV 还是 AI 生成
    if args.generate:
        # AI 生成模式
        print(f"🤖 使用 AI 生成闪卡 (provider: {args.provider})")
        
        # 提取博客内容
        print(f"📖 读取博客内容: {args.blog_path}")
        blog_content = extract_blog_content(args.blog_path)
        
        if len(blog_content) < 100:
            print("警告: 博客内容过短，可能无法生成有效的闪卡")
        
        # 设置默认模型
        default_models = {
            'gemini': 'gemini-2.0-flash',
            'openrouter': 'google/gemini-2.0-flash-001',
            'openai': 'gpt-4o-mini',
        }
        model = args.model or default_models.get(args.provider, 'gemini-2.0-flash')
        
        # 调用相应的 API
        print(f"🔧 正在生成 {args.count} 个问答对...")
        
        if args.provider == 'gemini':
            qa_pairs = generate_with_gemini(blog_content, args.count, model)
        elif args.provider == 'openrouter':
            qa_pairs = generate_with_openrouter(blog_content, args.count, model)
        elif args.provider == 'openai':
            base_url = args.base_url or "https://api.openai.com"
            qa_pairs = generate_with_openai_compatible(blog_content, args.count, model, base_url)
        else:
            print(f"错误: 未知的 provider: {args.provider}")
            sys.exit(1)
        
        if not qa_pairs:
            print("错误: AI 未能生成有效的问答对")
            sys.exit(1)
        
        print(f"   成功生成 {len(qa_pairs)} 个问答对")
        
        # 可选：保存到 CSV
        if args.output:
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Question', 'Answer'])
                for q, a in qa_pairs:
                    writer.writerow([q, a])
            print(f"💾 已保存到 CSV: {args.output}")
    
    elif args.csv_path:
        # CSV 文件模式
        if not Path(args.csv_path).exists():
            print(f"错误: CSV 文件不存在: {args.csv_path}")
            sys.exit(1)
        
        print(f"📖 读取 CSV 文件: {args.csv_path}")
        qa_pairs = read_csv(args.csv_path)
        
        if not qa_pairs:
            print("错误: CSV 文件中没有有效的问答对")
            sys.exit(1)
        
        print(f"   找到 {len(qa_pairs)} 个问答对")
    
    else:
        parser.print_help()
        print("\n错误: 请提供 CSV 文件路径或使用 --generate 参数")
        sys.exit(1)
    
    # 生成 shortcode
    print("🔧 生成闪卡代码...")
    flashcards_code = generate_flashcards_shortcode(qa_pairs)
    
    # 插入博客
    print(f"📝 插入闪卡到博客: {args.blog_path}")
    if insert_flashcards_to_blog(args.blog_path, flashcards_code):
        print("✅ 完成！闪卡已成功添加到博客末尾")
        print(f"   共添加 {len(qa_pairs)} 张闪卡")
    else:
        print("❌ 添加失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
