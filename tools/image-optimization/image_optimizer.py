#!/usr/bin/env python3
"""
Hugo Blog Image Optimizer

自动优化Hugo博客中的图片：
- 转换为WebP格式以减少文件大小
- 生成响应式图片尺寸
- 压缩图片质量
- 保持原始文件备份

使用方法：
python image_optimizer.py [选项]

选项：
--input-dir DIR    输入目录（默认: static/images）
--output-dir DIR   输出目录（默认: static/images/optimized）
--quality QUALITY  图片质量（默认: 85）
--max-width WIDTH  最大宽度（默认: 1920）
--sizes SIZES      生成的尺寸（默认: 320,640,960,1280,1920）
--file FILE        优化单个图片文件并输出Markdown
--backup          保留原始文件备份
--dry-run         仅显示将要执行的操作，不实际执行
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
except ImportError:
    print("错误: 需要安装必要的库")
    print("请运行: pip install pillow")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageOptimizer:
    """Hugo博客图片优化器"""

    # 支持的输入格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    # 输出格式优先级
    OUTPUT_FORMATS = ['.webp', '.jpg']

    def __init__(self, input_dir: str, output_dir: str, quality: int = 85,
                 max_width: int = 1920, sizes: List[int] = None, backup: bool = True):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.max_width = max_width
        self.sizes = sizes or [320, 640, 960, 1280, 1920]
        self.backup = backup

        # 确保输入目录存在
        if not self.input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {self.input_dir}")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 创建备份目录
        if self.backup:
            self.backup_dir = self.output_dir.parent / "backup"
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def should_process_file(self, file_path: Path) -> bool:
        """判断文件是否需要处理"""
        if not file_path.is_file():
            return False

        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False

        # 跳过已经优化过的文件
        if file_path.parent.name == "optimized":
            return False

        return True

    def get_output_path(self, input_path: Path, size: int = None, format_suffix: str = None) -> Path:
        """生成输出文件路径"""
        # 获取相对路径
        rel_path = input_path.relative_to(self.input_dir)

        # 移除文件扩展名
        stem = rel_path.stem

        # 添加尺寸后缀（如果指定）
        if size:
            stem = f"{stem}_{size}w"

        # 确定输出格式
        if format_suffix:
            output_suffix = format_suffix
        else:
            # 优先使用WebP
            output_suffix = '.webp'

        # 生成输出路径
        output_path = self.output_dir / rel_path.parent / f"{stem}{output_suffix}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def optimize_image(self, input_path: Path, dry_run: bool = False) -> List[Tuple[str, str, int, int]]:
        """优化单个图片"""
        results = []
        original_file_size = input_path.stat().st_size

        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 转换为RGB模式（去除透明度）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # 获取原始尺寸
                original_width, original_height = img.size
                aspect_ratio = original_height / original_width

                logger.info(f"处理图片: {input_path} ({original_width}x{original_height})")

                # 生成不同尺寸的图片
                for size in self.sizes:
                    if size >= original_width:
                        # 如果请求的尺寸大于等于原始尺寸，使用原始尺寸
                        target_width = original_width
                        target_height = original_height
                    else:
                        target_width = size
                        target_height = int(size * aspect_ratio)

                    # 调整图片尺寸
                    resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                    # 生成WebP格式
                    output_path_webp = self.get_output_path(input_path, target_width, '.webp')

                    if dry_run:
                        logger.info(f"将生成: {output_path_webp} ({target_width}x{target_height})")
                        results.append((str(input_path), str(output_path_webp), 0, original_file_size))
                        continue

                    # 保存为WebP
                    resized_img.save(
                        output_path_webp,
                        'WEBP',
                        quality=self.quality,
                        method=6  # 更好的压缩
                    )

                    # 获取文件大小
                    file_size = output_path_webp.stat().st_size
                    results.append((str(input_path), str(output_path_webp), file_size, original_file_size))

                    logger.info(f"生成: {output_path_webp} ({target_width}x{target_height}, {file_size} bytes)")

                # 如果启用备份，备份原始文件
                if self.backup and not dry_run:
                    backup_path = self.backup_dir / input_path.relative_to(self.input_dir)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(input_path, backup_path)
                    logger.info(f"备份: {input_path} -> {backup_path}")

        except Exception as e:
            logger.error(f"处理图片失败 {input_path}: {e}")
            results.append((str(input_path), f"ERROR: {e}", 0, 0))

        return results

    def scan_and_optimize(self, dry_run: bool = False) -> List[Tuple[str, str, int, int]]:
        """扫描并优化所有图片"""
        all_files = list(self.input_dir.rglob('*'))
        image_files = [f for f in all_files if self.should_process_file(f)]

        logger.info(f"发现 {len(image_files)} 个图片文件待处理")

        results = []

        # 使用多线程处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self.optimize_image, img_file, dry_run): img_file
                for img_file in image_files
            }

            for future in as_completed(future_to_file):
                img_file = future_to_file[future]
                try:
                    file_results = future.result()
                    results.extend(file_results)
                except Exception as e:
                    logger.error(f"处理失败 {img_file}: {e}")
                    results.append((str(img_file), f"ERROR: {e}", 0, 0))

        return results

    def generate_hugo_config(self) -> str:
        """生成Hugo配置片段"""
        config_lines = [
            "# 图片优化配置",
            "[imaging]",
            "  quality = 85",
            "  resampleFilter = \"Lanczos\"",
            "",
            "# WebP格式支持",
            "[outputFormats.WebP]",
            "  baseName = \"image\"",
            "  mediaType = \"image/webp\"",
            "",
            "# 图片处理设置",
            "[params.imaging]",
            "  # 响应式图片尺寸",
            f"  sizes = {self.sizes}",
            "  # 图片质量",
            f"  quality = {self.quality}",
        ]

        return "\n".join(config_lines)

def main():
    parser = argparse.ArgumentParser(
        description="Hugo博客图片优化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        default='static/images',
        help='输入目录 (默认: static/images)'
    )

    parser.add_argument(
        '--output-dir',
        default='static/images/optimized',
        help='输出目录 (默认: static/images/optimized)'
    )

    parser.add_argument(
        '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        help='图片质量 1-100 (默认: 85)'
    )

    parser.add_argument(
        '--max-width',
        type=int,
        default=1920,
        help='最大宽度 (默认: 1920)'
    )

    parser.add_argument(
        '--sizes',
        type=int,
        nargs='+',
        default=[320, 640, 960, 1280, 1920],
        help='生成尺寸列表 (默认: 320 640 960 1280 1920)'
    )
    
    parser.add_argument(
        '--file',
        help='指定单个图片文件进行优化'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='不保留原始文件备份'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示操作，不实际执行'
    )

    parser.add_argument(
        '--generate-config',
        action='store_true',
        help='生成Hugo配置文件片段'
    )

    args = parser.parse_args()

    # 创建优化器实例
    optimizer = ImageOptimizer(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        quality=args.quality,
        max_width=args.max_width,
        sizes=args.sizes,
        backup=not args.no_backup
    )

    if args.generate_config:
        # 生成Hugo配置
        config = optimizer.generate_hugo_config()
        print("# 将以下配置添加到 config.toml:")
        print(config)
        return

    # 执行优化
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            sys.exit(1)
        
        logger.info(f"正在优化单个文件: {file_path}")
        results = optimizer.optimize_image(file_path, dry_run=args.dry_run)
        
        # 如果优化成功，输出Markdown片段
        for orig, optimized, opt_size, orig_size in results:
            if not optimized.startswith("ERROR"):
                rel_optimized = Path(optimized).relative_to(Path('../../static'))
                # 转换路径分隔符为 forward slash 供 URL 使用
                markdown_path = str(rel_optimized).replace('\\', '/')
                if not markdown_path.startswith('/'):
                    markdown_path = '/' + markdown_path
                print("\n" + "="*40)
                print("✨ 优化成功！请复制以下 Markdown 插入博客：")
                print("="*40)
                print(f"![{file_path.stem}]({markdown_path})")
                print("="*40 + "\n")
    else:
        logger.info("开始批量图片优化...")
        results = optimizer.scan_and_optimize(dry_run=args.dry_run)

    # 统计结果
    success_count = len([r for r in results if not r[1].startswith("ERROR")])
    error_count = len([r for r in results if r[1].startswith("ERROR")])
    # 计算节省的空间：原始大小之和（去重，因为一个文件可能生成多个尺寸）- 优化后大小之和
    # 在 optimize-one 场景下，通常只有一个原始文件
    processed_orig_files = {}
    total_optimized_size = 0
    for orig, optimized, opt_size, orig_size in results:
        if not optimized.startswith("ERROR"):
            processed_orig_files[orig] = orig_size
            total_optimized_size += opt_size
    
    total_original_size = sum(processed_orig_files.values())
    total_size_saved = total_original_size - total_optimized_size

    logger.info(f"优化完成: {success_count} 成功, {error_count} 失败")
    if total_size_saved > 0:
        logger.info(f"总计节省空间: {total_size_saved / 1024:.1f} KB")
    else:
        logger.info(f"总计生成大小: {total_optimized_size / 1024:.1f} KB (原始大小: {total_original_size / 1024:.1f} KB)")

    if error_count > 0:
        logger.warning("部分文件处理失败，请检查上述错误信息")

if __name__ == '__main__':
    main()
