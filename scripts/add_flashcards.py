#!/usr/bin/env python3
"""
闪卡生成器 - 将 CSV 格式的 Q&A 数据转换为 Hugo shortcode 并插入博客文章

用法:
    python add_flashcards.py <博客文件路径> <CSV文件路径>
    python add_flashcards.py <博客文件路径> --generate  # 使用 AI 自动生成闪卡

CSV 格式要求:
    第一列: 问题 (Question)
    第二列: 答案 (Answer)
    支持带或不带表头

示例:
    python scripts/add_flashcards.py content/zh/posts/my-article.md flashcards.csv
"""

import csv
import sys
import re
from pathlib import Path
from typing import List, Tuple


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


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\n用法: python add_flashcards.py <博客文件路径> <CSV文件路径>")
        sys.exit(1)
    
    blog_path = sys.argv[1]
    csv_path = sys.argv[2]
    
    # 检查文件存在
    if not Path(blog_path).exists():
        print(f"错误: 博客文件不存在: {blog_path}")
        sys.exit(1)
    
    if not Path(csv_path).exists():
        print(f"错误: CSV 文件不存在: {csv_path}")
        sys.exit(1)
    
    # 读取 CSV
    print(f"📖 读取 CSV 文件: {csv_path}")
    qa_pairs = read_csv(csv_path)
    
    if not qa_pairs:
        print("错误: CSV 文件中没有有效的问答对")
        sys.exit(1)
    
    print(f"   找到 {len(qa_pairs)} 个问答对")
    
    # 生成 shortcode
    print("🔧 生成闪卡代码...")
    flashcards_code = generate_flashcards_shortcode(qa_pairs)
    
    # 插入博客
    print(f"📝 插入闪卡到博客: {blog_path}")
    if insert_flashcards_to_blog(blog_path, flashcards_code):
        print("✅ 完成！闪卡已成功添加到博客末尾")
        print(f"   共添加 {len(qa_pairs)} 张闪卡")
    else:
        print("❌ 添加失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
