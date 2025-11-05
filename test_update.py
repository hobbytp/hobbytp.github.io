#!/usr/bin/env python3
"""测试更新逻辑"""
import re
from pathlib import Path

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

# 测试
test_fm = """title: 每周一个MCP：Skill Seekers
date: "2025-11-02T20:10:00+08:00"
draft: false
tags: ["mcp", "skills_seeker", "coding_assistant"]
categories: ["ai_programming","projects"]
description: Skill Seekers 是一个自动化工具，可以将文档网站、GitHub 仓库和 PDF 文件快速转换为 Claude Skills，通过自动化冲突检测和AI增强技术，大幅减少手工整理和理解文档所需的时间（20-40 分钟内生成生产就绪的Claude技能）。"""

print("Original:")
print(test_fm)
print("\n" + "="*60 + "\n")

updated = update_frontmatter(test_fm, 6867, 28)
print("Updated:")
print(updated)
print("\n" + "="*60 + "\n")

# 验证格式保持不变
original_lines = test_fm.split('\n')
updated_lines = updated.split('\n')

print("Format check:")
for i, (orig, upd) in enumerate(zip(original_lines, updated_lines[:len(original_lines)])):
    if orig != upd and not (upd.startswith('wordCount:') or upd.startswith('readingTime:')):
        print(f"Line {i+1} changed: {orig} -> {upd}")
    elif orig == upd:
        print(f"Line {i+1} OK: {orig}")

