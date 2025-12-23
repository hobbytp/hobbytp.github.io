#!/usr/bin/env python3
"""
更新博客文章的字数和阅读时间统计
自动扫描content目录下的所有markdown文件，计算中文字符数并更新front matter
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# 强制 stdout 使用 utf-8 编码，防止 Windows 下打印 emoji 报错
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        pass

def count_chinese_chars(text: str) -> int:
    """统计中文字符数（包括中文标点符号）"""
    # 匹配中文字符
    # \u4e00-\u9fa5: 中文汉字
    # \u3000-\u303f: CJK符号和标点
    # \uff00-\uffef: 全角符号
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]')
    matches = chinese_pattern.findall(text)
    return len(matches)

def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """提取front matter和正文内容"""
    if not content.startswith('---'):
        return None, content
    
    # 查找第二个 ---
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    
    frontmatter = parts[1].strip()
    body = parts[2]
    
    return frontmatter, body

def parse_frontmatter(frontmatter: str) -> dict:
    """解析YAML front matter"""
    import yaml
    try:
        return yaml.safe_load(frontmatter) or {}
    except Exception as e:
        print(f"警告: 解析front matter失败: {e}")
        return {}

def update_frontmatter(frontmatter_str: str, word_count: int, reading_time: int) -> str:
    """更新front matter字符串，只添加或更新wordCount和readingTime字段，保留其他格式"""
    lines = frontmatter_str.split('\n')
    result_lines = []
    word_count_updated = False
    reading_time_updated = False
    
    # 遍历每一行，更新或跳过 wordCount 和 readingTime
    for line in lines:
        # 检查是否是 wordCount 行
        if re.match(r'^wordCount\s*:', line, re.IGNORECASE):
            result_lines.append(f'wordCount: {word_count}')
            word_count_updated = True
        # 检查是否是 readingTime 行
        elif re.match(r'^readingTime\s*:', line, re.IGNORECASE):
            result_lines.append(f'readingTime: {reading_time}')
            reading_time_updated = True
        else:
            # 保留其他所有行（包括多行字段的续行）
            result_lines.append(line)
    
    # 如果没有找到这两个字段，在末尾添加（保留最后一个空行）
    if not word_count_updated:
        # 找到最后一个非空行
        last_content_idx = len(result_lines) - 1
        while last_content_idx >= 0 and not result_lines[last_content_idx].strip():
            last_content_idx -= 1
        
        # 在最后一个内容行后插入
        result_lines.insert(last_content_idx + 1, f'wordCount: {word_count}')
    
    if not reading_time_updated:
        # 找到最后一个非空行（可能已经是 wordCount）
        last_content_idx = len(result_lines) - 1
        while last_content_idx >= 0 and not result_lines[last_content_idx].strip():
            last_content_idx -= 1
        
        # 在最后一个内容行后插入
        result_lines.insert(last_content_idx + 1, f'readingTime: {reading_time}')
    
    return '\n'.join(result_lines)

def calculate_reading_stats(text: str, reading_speed: int = 400) -> Tuple[int, int]:
    """
    计算文本的字数和阅读时间
    
    Args:
        text: 文本内容
        reading_speed: 阅读速度（字/分钟），默认400
        
    Returns:
        (word_count, reading_time)
    """
    word_count = count_chinese_chars(text)
    reading_time = max(1, (word_count + reading_speed - 1) // reading_speed)
    return word_count, reading_time

def process_markdown_file(file_path: Path, update: bool = False) -> Tuple[int, int, bool]:
    """
    处理单个markdown文件
    返回: (字数, 阅读时间, 是否已更新)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] 读取文件失败 {file_path}: {e}")
        return 0, 0, False
    
    frontmatter_str, body = extract_frontmatter(content)
    
    if frontmatter_str is None:
        # 使用字符串格式化而不是relative_to避免路径问题
        rel_path = str(file_path).replace(str(Path.cwd()), '').lstrip('\\/').replace('\\', '/')
        print(f"[WARN] 跳过（无front matter）: {rel_path}")
        return 0, 0, False
    
    # 统计字数和阅读时间
    word_count, reading_time = calculate_reading_stats(body, reading_speed=400)
    
    # 解析front matter
    fm_data = parse_frontmatter(frontmatter_str)
    
    # 检查是否需要更新
    current_word_count = fm_data.get('wordCount', 0)
    current_reading_time = fm_data.get('readingTime', 0)
    
    if not update:
        # 仅显示统计信息
        status = "[OK]" if current_word_count == word_count and current_reading_time == reading_time else "[WARN]"
        # 使用字符串格式化而不是relative_to避免路径问题
        rel_path = str(file_path).replace(str(Path.cwd()), '').lstrip('\\/').replace('\\', '/')
        print(f"{status} {rel_path}")
        print(f"   当前: {current_word_count} 字, {current_reading_time} 分钟")
        print(f"   实际: {word_count} 字, {reading_time} 分钟")
        return word_count, reading_time, False
    
    # 需要更新
    if current_word_count != word_count or current_reading_time != reading_time:
        # 更新front matter（保留原始格式）
        new_frontmatter = update_frontmatter(frontmatter_str, word_count, reading_time)
        
        # 重新组装文件内容
        new_content = f"---\n{new_frontmatter}\n---{body}"
        
        # 写回文件
        try:
            file_path.write_text(new_content, encoding='utf-8')
            # 使用字符串格式化而不是relative_to避免路径问题
            rel_path = str(file_path).replace(str(Path.cwd()), '').lstrip('\\/').replace('\\', '/')
            print(f"[UPDATED] 已更新: {rel_path} ({word_count} 字, {reading_time} 分钟)")
            return word_count, reading_time, True
        except Exception as e:
            print(f"[ERROR] 写入文件失败 {file_path}: {e}")
            return word_count, reading_time, False
    else:
        # 使用字符串格式化而不是relative_to避免路径问题
        rel_path = str(file_path).replace(str(Path.cwd()), '').lstrip('\\/').replace('\\', '/')
        print(f"[SKIP] 无需更新: {rel_path}")
        return word_count, reading_time, False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='更新博客文章的字数和阅读时间统计',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查所有文件（不修改）
  python scripts/update_word_count.py
  
  # 更新所有文件
  python scripts/update_word_count.py --update
  
  # 更新特定文件
  python scripts/update_word_count.py --update content/zh/projects/mcp/skill_seeker.md
  
  # 仅处理特定目录
  python scripts/update_word_count.py --update --dir content/zh/daily_ai
        """
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='要处理的markdown文件路径（默认：扫描content目录下所有.md文件）'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='实际更新文件（默认仅显示统计信息）'
    )
    parser.add_argument(
        '--dir',
        type=str,
        help='仅处理指定目录下的文件'
    )
    parser.add_argument(
        '--content-dir',
        type=str,
        default='content',
        help='内容目录路径（默认: content）'
    )
    
    args = parser.parse_args()
    
    # 确定要处理的文件列表
    if args.files:
        files = [Path(f) for f in args.files if f.endswith('.md')]
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"[ERROR] 目录不存在: {dir_path}")
            sys.exit(1)
        files = list(dir_path.rglob('*.md'))
    else:
        content_dir = Path(args.content_dir)
        if not content_dir.exists():
            print(f"[ERROR] 内容目录不存在: {content_dir}")
            sys.exit(1)
        files = list(content_dir.rglob('*.md'))
    
    if not files:
        print("[WARN] 未找到任何markdown文件")
        sys.exit(0)
    
    print(f"{'=' * 60}")
    if args.update:
        print(f"[UPDATE] 更新模式: 将更新 {len(files)} 个文件")
    else:
        print(f"[CHECK] 检查模式: 将检查 {len(files)} 个文件（使用 --update 实际更新）")
    print(f"{'=' * 60}\n")
    
    total_word_count = 0
    total_reading_time = 0
    updated_count = 0
    
    for file_path in sorted(files):
        word_count, reading_time, updated = process_markdown_file(file_path, args.update)
        total_word_count += word_count
        total_reading_time += reading_time
        if updated:
            updated_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"统计汇总:")
    print(f"   总文件数: {len(files)}")
    if args.update:
        print(f"   已更新: {updated_count}")
        print(f"   无需更新: {len(files) - updated_count}")
    print(f"   总字数: {total_word_count:,} 字")
    print(f"   总阅读时间: {total_reading_time} 分钟")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    try:
        import yaml
    except ImportError:
        print("[ERROR] 错误: 需要安装 PyYAML")
        print("   安装命令: pip install pyyaml")
        sys.exit(1)
    
    main()

