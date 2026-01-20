import os
import sys
import csv
import logging
import shutil
import argparse
from pathlib import Path
from PIL import Image
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 目录配置
STATIC_DIR = PROJECT_ROOT / "static"
TMP_DIR = STATIC_DIR / "tmp"
CONTENT_DIR_BASE = PROJECT_ROOT / "content" / "zh"

BACKUP_IMAGES_DIR = STATIC_DIR / "images" / "backup" / "png"
OPTIMIZED_IMAGES_DIR = STATIC_DIR / "images" / "optimized" / "png"
PDF_DIR = STATIC_DIR / "pdf"
FLASHCARDS_DIR = STATIC_DIR / "flashcards"

def ensure_dirs():
    """确保目标目录存在"""
    for d in [BACKUP_IMAGES_DIR, OPTIMIZED_IMAGES_DIR, PDF_DIR, FLASHCARDS_DIR, TMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def move_and_process_files(filename):
    """
    移动文件并返回处理后的路径信息
    :param filename: 文件名（不含后缀）
    """
    # 1. 处理 PNG
    src_png = TMP_DIR / f"{filename}.png"
    if src_png.exists():
        dst_png = BACKUP_IMAGES_DIR / f"{filename}.png"
        shutil.move(str(src_png), str(dst_png))
        logger.info(f"Moved PNG: {src_png} -> {dst_png}")
        
        # 优化 WebP
        dst_webp = OPTIMIZED_IMAGES_DIR / f"{filename}.webp"
        if not dst_webp.exists():
            try:
                with Image.open(dst_png) as img:
                    img.save(dst_webp, "WebP", quality=80)
                logger.info(f"Optimized WebP: {dst_webp}")
            except Exception as e:
                logger.error(f"Failed to convert image: {e}")
    else:
        logger.warning(f"PNG file not found in tmp: {src_png}")

    # 2. 处理 PDF
    src_pdf = TMP_DIR / f"{filename}.pdf"
    if src_pdf.exists():
        dst_pdf = PDF_DIR / f"{filename}.pdf"
        shutil.move(str(src_pdf), str(dst_pdf))
        logger.info(f"Moved PDF: {src_pdf} -> {dst_pdf}")
    else:
        logger.warning(f"PDF file not found in tmp: {src_pdf}")

    # 3. 处理 CSV/XLS
    # 优先找 CSV
    src_csv = TMP_DIR / f"{filename}.csv"
    src_xls = TMP_DIR / f"{filename}.xls"
    src_xlsx = TMP_DIR / f"{filename}.xlsx"
    
    final_flashcard_file = None

    if src_csv.exists():
        dst_csv = FLASHCARDS_DIR / f"{filename}.csv"
        shutil.move(str(src_csv), str(dst_csv))
        logger.info(f"Moved CSV: {src_csv} -> {dst_csv}")
        final_flashcard_file = dst_csv
    elif src_xls.exists():
         # 简单移动，暂不支持读取
        dst_xls = FLASHCARDS_DIR / f"{filename}.xls"
        shutil.move(str(src_xls), str(dst_xls))
        logger.info(f"Moved XLS: {src_xls} -> {dst_xls}")
        logger.warning("XLS support for generating shortcodes is limited. Please use CSV for best results.")
    elif src_xlsx.exists():
        dst_xlsx = FLASHCARDS_DIR / f"{filename}.xlsx"
        shutil.move(str(src_xlsx), str(dst_xlsx))
        logger.info(f"Moved XLSX: {src_xlsx} -> {dst_xlsx}")
        logger.warning("XLSX support for generating shortcodes is limited. Please use CSV for best results.")
    else:
        logger.warning(f"Flashcard file (csv/xls/xlsx) not found in tmp for: {filename}")
        
    return final_flashcard_file

def generate_flashcards_shortcode(flashcard_file_path):
    """
    读取 Flashcard 文件并生成 Shortcode
    目前主要支持 CSV
    """
    if not flashcard_file_path or not flashcard_file_path.exists():
        return ""

    if flashcard_file_path.suffix.lower() != '.csv':
        logger.warning(f"Skipping flashcard generation for non-CSV file: {flashcard_file_path}")
        return ""

    flashcards_content = "{{< flashcards >}}\n"
    try:
        with open(flashcard_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    question = row[0].strip()
                    answer = row[1].strip()
                    question = question.replace('"', '\\"')
                    flashcards_content += f'{{{{< flashcard q="{question}" >}}}}{answer}{{{{< /flashcard >}}}}\n'
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return ""

    flashcards_content += "{{< /flashcards >}}"
    return flashcards_content

def generate_paper_blog(filename, output_dir_name="papers"):
    """
    生成论文博客
    :param filename: 文件名（不含后缀）
    :param output_dir_name: 输出目录名称（相对于 content/zh/），默认为 papers
    """
    ensure_dirs()
    
    logger.info(f"Processing resources for {filename}...")
    move_and_process_files(filename)
    
    # 博客输出路径
    output_dir = CONTENT_DIR_BASE / output_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 准备内容
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    # 图片路径 (指向 optimized)
    image_rel_path = f"/images/optimized/png/{filename}.webp"
    pdf_rel_path = f"/pdf/{filename}.pdf"
    
    # 闪卡 Shortcode
    # 查找 flashcards 目录下的 csv
    flashcard_file = FLASHCARDS_DIR / f"{filename}.csv"
    flashcards_block = generate_flashcards_shortcode(flashcard_file)

    # Frontmatter
    frontmatter = f"""---
title: "{filename}"
date: "{date_str}"
draft: false
tags: ["paper", "research"]
categories: ["{output_dir_name}"]
description: "论文 {filename} 的详细解读与资料整理。"
cover:
  image: "{image_rel_path}"
  alt: "{filename} 示意图"
---
"""

    # 正文
    content = f"""
## 摘要

(此处添加摘要内容)

## 论文示意图

![{filename}示意图]({image_rel_path})

## 论文 PDF

{{{{< pdf src="{pdf_rel_path}" >}}}}

## 闪卡回顾

{flashcards_block}
"""

    full_content = frontmatter + content
    
    # 写入文件
    output_path = output_dir / f"{filename}.md"
    output_path.write_text(full_content, encoding='utf-8')
    logger.info(f"Blog post generated at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Hugo blog post from paper resources.")
    parser.add_argument("filename", help="Base filename (without extension)")
    parser.add_argument("--output-dir", default="papers", help="Output directory under content/zh/ (default: papers)")
    
    args = parser.parse_args()
    
    generate_paper_blog(args.filename, args.output_dir)
