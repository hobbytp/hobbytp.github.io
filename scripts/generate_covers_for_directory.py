#!/usr/bin/env python3
"""
Directory-specific AI Cover Image Generator for Hugo Blog
为指定目录下的博客文章批量生成AI封面图片
支持ModelScope Qwen-image API
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectoryCoverGenerator:
    """目录级AI封面生成器"""

    def __init__(self, base_content_dir: str = "content/zh"):
        self.base_content_dir = Path(base_content_dir)
        self.script_dir = Path(__file__).parent
        self.ai_generator_script = self.script_dir / "ai_cover_generator.py"

    def find_articles_in_directory(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        查找指定目录下的所有文章

        Args:
            directory: 目标目录路径（相对于content/zh）
            recursive: 是否递归查找子目录

        Returns:
            文章文件路径列表
        """
        target_dir = self.base_content_dir / directory
        if not target_dir.exists():
            logger.error(f"Directory not found: {target_dir}")
            return []

        articles = []
        pattern = "**/*.md" if recursive else "*.md"

        for file_path in target_dir.glob(pattern):
            if file_path.is_file() and file_path.name != "_index.md":
                # 检查文件是否包含front matter
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            articles.append(file_path)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")

        logger.info(f"Found {len(articles)} articles in {directory}")
        return articles

    def check_article_needs_cover(self, article_path: Path) -> bool:
        """
        检查文章是否需要生成封面

        Args:
            article_path: 文章路径

        Returns:
            是否需要生成封面
        """
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取front matter
            if not content.startswith('---'):
                return False

            parts = content.split('---', 2)
            if len(parts) < 3:
                return False

            front_matter = parts[1]

            # 检查是否已有封面图片
            has_ai_cover = 'ai_cover:' in front_matter
            has_cover_image = 'cover:' in front_matter and 'image:' in front_matter

            if has_ai_cover or has_cover_image:
                logger.info(f"Article {article_path.name} already has cover image")
                return False

            # 检查是否有title和description
            has_title = 'title:' in front_matter
            has_description = 'description:' in front_matter

            if not (has_title and has_description):
                logger.warning(f"Article {article_path.name} missing title or description")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking {article_path}: {e}")
            return False

    def generate_cover_for_article(self, article_path: Path, force: bool = False) -> bool:
        """
        为单篇文章生成封面

        Args:
            article_path: 文章路径
            force: 是否强制重新生成

        Returns:
            是否生成成功
        """
        try:
            # 构建命令
            cmd = [
                sys.executable,
                str(self.ai_generator_script),
                '--specific-file', str(article_path),
                '--workflow-mode'
            ]

            if force:
                cmd.append('--force')

            # 设置环境变量
            env = os.environ.copy()

            # 执行生成命令
            logger.info(f"Generating cover for {article_path.name}...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                logger.info(f"✅ Successfully generated cover for {article_path.name}")
                return True
            else:
                logger.error(f"❌ Failed to generate cover for {article_path.name}")
                logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout generating cover for {article_path.name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error generating cover for {article_path.name}: {e}")
            return False

    def generate_covers_for_directory(self, directory: str, recursive: bool = True,
                                    force: bool = False, dry_run: bool = False) -> Dict:
        """
        为指定目录下的所有文章生成封面

        Args:
            directory: 目标目录
            recursive: 是否递归处理子目录
            force: 是否强制重新生成已有封面
            dry_run: 是否只显示将要处理的文章而不实际生成

        Returns:
            生成结果统计
        """
        logger.info(f"🎯 Processing directory: {directory}")
        logger.info(f"Recursive: {recursive}, Force: {force}, Dry run: {dry_run}")

        # 查找文章
        articles = self.find_articles_in_directory(directory, recursive)
        if not articles:
            return {"total": 0, "processed": 0, "skipped": 0, "failed": 0}

        # 筛选需要处理的文章
        articles_to_process = []
        for article in articles:
            if force or self.check_article_needs_cover(article):
                articles_to_process.append(article)

        logger.info(f"Found {len(articles_to_process)} articles to process")

        if dry_run:
            logger.info("🔍 Dry run - Articles to be processed:")
            for article in articles_to_process:
                logger.info(f"  - {article.relative_to(self.base_content_dir)}")
            return {"total": len(articles_to_process), "processed": 0, "skipped": 0, "failed": 0}

        # 处理文章
        results = {"total": len(articles_to_process), "processed": 0, "skipped": 0, "failed": 0}

        for i, article in enumerate(articles_to_process, 1):
            logger.info(f"Processing {i}/{len(articles_to_process)}: {article.name}")

            if self.generate_cover_for_article(article, force):
                results["processed"] += 1
            else:
                results["failed"] += 1

        return results

    def list_available_directories(self) -> List[str]:
        """
        列出所有可用的目录

        Returns:
            目录列表
        """
        directories = []
        for item in self.base_content_dir.iterdir():
            if item.is_dir() and item.name not in ['.git', '__pycache__', 'draft']:
                directories.append(item.name)

        # 添加根目录文件
        root_files = list(self.base_content_dir.glob("*.md"))
        if root_files:
            directories.append("(root files)")

        return sorted(directories)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Directory-specific AI Cover Image Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 为papers目录生成封面
  python generate_covers_for_directory.py papers

  # 为deepseek目录及其子目录生成封面
  python generate_covers_for_directory.py deepseek --recursive

  # 强制重新生成已有封面
  python generate_covers_for_directory.py papers --force

  # 只查看将要处理的文章（不实际生成）
  python generate_covers_for_directory.py papers --dry-run

  # 列出所有可用目录
  python generate_covers_for_directory.py --list-directories
        """
    )

    parser.add_argument('directory', nargs='?', help='目标目录名称（相对于content/zh）')
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                       help='递归处理子目录（默认开启）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归处理子目录')
    parser.add_argument('--force', '-f', action='store_true',
                       help='强制重新生成已有封面')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='只显示将要处理的文章，不实际生成')
    parser.add_argument('--list-directories', '-l', action='store_true',
                       help='列出所有可用目录')
    parser.add_argument('--base-dir', default='content/zh',
                       help='基础内容目录（默认: content/zh）')

    args = parser.parse_args()

    # 处理参数
    if args.list_directories:
        generator = DirectoryCoverGenerator(args.base_dir)
        directories = generator.list_available_directories()
        print("📁 可用目录:")
        for directory in directories:
            print(f"  - {directory}")
        return

    if not args.directory:
        print("❌ 请指定目标目录")
        print("使用 --list-directories 查看所有可用目录")
        parser.print_help()
        return

    # 处理递归参数
    recursive = args.recursive and not args.no_recursive

    # 创建生成器
    generator = DirectoryCoverGenerator(args.base_dir)

    # 检查环境变量
    modelscope_key = os.getenv("MODELSCOPE_API_KEY")
    if not modelscope_key:
        print("⚠️  警告: 未设置 MODELSCOPE_API_KEY 环境变量")
        print("请在 .env 文件中添加: MODELSCOPE_API_KEY=your-key")

    # 生成封面
    print(f"🚀 开始为目录 '{args.directory}' 生成AI封面...")
    results = generator.generate_covers_for_directory(
        directory=args.directory,
        recursive=recursive,
        force=args.force,
        dry_run=args.dry_run
    )

    # 显示结果
    print(f"\n📊 处理完成:")
    print(f"  总计: {results['total']} 篇文章")
    print(f"  ✅ 成功: {results['processed']} 篇")
    print(f"  ❌ 失败: {results['failed']} 篇")
    print(f"  ⏭️  跳过: {results['skipped']} 篇")

    if results['failed'] > 0:
        print("\n⚠️  部分文章生成失败，请检查日志")
        return 1

    print("\n🎉 所有封面生成完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())