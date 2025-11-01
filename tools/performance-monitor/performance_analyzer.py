#!/usr/bin/env python3
"""
Hugo Blog Performance Analyzer

分析Hugo博客的性能指标：
- 构建时间统计
- 页面大小分析
- 资源使用情况
- 性能建议生成

使用方法：
python performance_analyzer.py [选项]

选项：
--build-time     分析构建时间
--analyze-site   分析站点结构和大小
--check-images   检查图片优化情况
--generate-report 生成性能报告
--output-dir DIR  输出目录（默认: reports/）
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import shutil
from datetime import datetime

class HugoPerformanceAnalyzer:
    """Hugo博客性能分析器"""

    def __init__(self, site_dir: str = ".", output_dir: str = "reports"):
        self.site_dir = Path(site_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 性能数据存储
        self.metrics = {
            'build_time': 0,
            'page_count': 0,
            'total_size': 0,
            'avg_page_size': 0,
            'largest_pages': [],
            'image_stats': {},
            'resource_stats': {}
        }

    def run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """运行命令并返回结果"""
        try:
            # 检查是否在虚拟环境中
            env = os.environ.copy()
            venv_python = None

            # 优先使用conda环境
            if 'CONDA_DEFAULT_ENV' in env:
                # conda环境已激活，使用系统hugo
                pass
            # 检查uv虚拟环境
            elif os.path.exists('.venv/bin/python'):
                venv_python = '.venv/bin/python'
            elif os.path.exists('.venv/Scripts/python.exe'):  # Windows
                venv_python = '.venv/Scripts/python.exe'

            # 如果是Python脚本，尝试使用虚拟环境
            if cmd[0] in ['python', 'python3'] and venv_python:
                cmd[0] = venv_python

            result = subprocess.run(
                cmd,
                cwd=self.site_dir,
                capture_output=capture_output,
                text=True,
                check=True,
                env=env
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {' '.join(cmd)}")
            print(f"错误信息: {e}")
            return None

    def measure_build_time(self) -> float:
        """测量Hugo构建时间"""
        print("🔧 测量Hugo构建时间...")

        start_time = time.time()

        # 清理之前的构建
        public_dir = self.site_dir / "public"
        if public_dir.exists():
            shutil.rmtree(public_dir)

        # 执行Hugo构建
        result = self.run_command(["hugo", "--minify"])

        end_time = time.time()
        build_time = end_time - start_time

        if result and result.returncode == 0:
            self.metrics['build_time'] = build_time
            print(f"✅ 构建完成: {build_time:.2f} 秒")
        else:
            print("❌ 构建失败")

        return build_time

    def analyze_site_structure(self) -> Dict[str, Any]:
        """分析站点结构和大小"""
        print("📊 分析站点结构...")

        public_dir = self.site_dir / "public"
        if not public_dir.exists():
            print("❌ public目录不存在，请先构建站点")
            return {}

        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'page_sizes': [],
            'largest_files': []
        }

        # 遍历所有文件
        for file_path in public_dir.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1

                # 获取文件大小
                size = file_path.stat().st_size
                stats['total_size'] += size

                # 分类文件类型
                suffix = file_path.suffix.lower()
                if suffix not in stats['file_types']:
                    stats['file_types'][suffix] = {'count': 0, 'size': 0}
                stats['file_types'][suffix]['count'] += 1
                stats['file_types'][suffix]['size'] += size

                # 记录页面文件大小
                if suffix in ['.html', '.htm']:
                    stats['page_sizes'].append(size)

                # 记录大文件
                if size > 1024 * 1024:  # > 1MB
                    stats['largest_files'].append({
                        'path': str(file_path.relative_to(public_dir)),
                        'size': size,
                        'size_mb': round(size / (1024 * 1024), 2)
                    })

        # 计算统计信息
        if stats['page_sizes']:
            stats['page_sizes'].sort(reverse=True)
            stats['avg_page_size'] = sum(stats['page_sizes']) / len(stats['page_sizes'])
            stats['median_page_size'] = stats['page_sizes'][len(stats['page_sizes']) // 2]
            stats['largest_pages'] = stats['page_sizes'][:5]

        # 转换大小为MB
        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)

        # 更新metrics
        self.metrics.update({
            'page_count': len(stats['page_sizes']),
            'total_size': stats['total_size'],
            'avg_page_size': stats.get('avg_page_size', 0),
            'largest_pages': stats['largest_pages']
        })

        return stats

    def analyze_images(self) -> Dict[str, Any]:
        """分析图片优化情况"""
        print("🖼️  分析图片优化情况...")

        public_dir = self.site_dir / "public"
        image_stats = {
            'total_images': 0,
            'total_size': 0,
            'formats': {},
            'unoptimized': [],
            'webp_count': 0
        }

        # 查找所有图片文件
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

        for ext in image_extensions:
            for img_path in public_dir.rglob(f'*{ext}'):
                if img_path.is_file():
                    image_stats['total_images'] += 1
                    size = img_path.stat().st_size
                    image_stats['total_size'] += size

                    # 统计格式
                    fmt = ext[1:]  # 移除点
                    if fmt not in image_stats['formats']:
                        image_stats['formats'][fmt] = {'count': 0, 'size': 0}
                    image_stats['formats'][fmt]['count'] += 1
                    image_stats['formats'][fmt]['size'] += size

                    # 检查WebP格式
                    if fmt == 'webp':
                        image_stats['webp_count'] += 1

                    # 检查大文件（可能未优化）
                    if size > 500 * 1024 and fmt in ['jpg', 'jpeg', 'png']:  # > 500KB
                        image_stats['unoptimized'].append({
                            'path': str(img_path.relative_to(public_dir)),
                            'size': size,
                            'size_mb': round(size / (1024 * 1024), 2),
                            'format': fmt
                        })

        # 转换大小
        image_stats['total_size_mb'] = round(image_stats['total_size'] / (1024 * 1024), 2)

        self.metrics['image_stats'] = image_stats
        return image_stats

    def analyze_resources(self) -> Dict[str, Any]:
        """分析资源使用情况"""
        print("📦 分析资源使用情况...")

        public_dir = self.site_dir / "public"
        resource_stats = {
            'css_files': [],
            'js_files': [],
            'total_css_size': 0,
            'total_js_size': 0
        }

        # 分析CSS文件
        for css_path in public_dir.rglob('*.css'):
            if css_path.is_file():
                size = css_path.stat().st_size
                resource_stats['css_files'].append({
                    'path': str(css_path.relative_to(public_dir)),
                    'size': size
                })
                resource_stats['total_css_size'] += size

        # 分析JS文件
        for js_path in public_dir.rglob('*.js'):
            if js_path.is_file():
                size = js_path.stat().st_size
                resource_stats['js_files'].append({
                    'path': str(js_path.relative_to(public_dir)),
                    'size': size
                })
                resource_stats['total_js_size'] += size

        # 转换大小
        resource_stats['total_css_size_kb'] = round(resource_stats['total_css_size'] / 1024, 1)
        resource_stats['total_js_size_kb'] = round(resource_stats['total_js_size'] / 1024, 1)

        self.metrics['resource_stats'] = resource_stats
        return resource_stats

    def generate_report(self) -> str:
        """生成性能报告"""
        print("📝 生成性能报告...")

        report = f"""# Hugo博客性能分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体统计

- **构建时间**: {self.metrics['build_time']:.2f} 秒
- **页面数量**: {self.metrics['page_count']}
- **站点总大小**: {self.metrics['total_size'] / (1024*1024):.2f} MB
- **平均页面大小**: {self.metrics['avg_page_size'] / 1024:.1f} KB

## 🖼️ 图片分析

- **图片总数**: {self.metrics['image_stats'].get('total_images', 0)}
- **图片总大小**: {self.metrics['image_stats'].get('total_size_mb', 0):.2f} MB
- **WebP格式数量**: {self.metrics['image_stats'].get('webp_count', 0)}

### 图片格式分布
"""

        # 添加图片格式统计
        for fmt, data in self.metrics['image_stats'].get('formats', {}).items():
            report += f"- **{fmt.upper()}**: {data['count']} 个文件, {data['size'] / (1024*1024):.2f} MB\n"

        # 添加潜在未优化的图片
        unoptimized = self.metrics['image_stats'].get('unoptimized', [])
        if unoptimized:
            report += "\n### 建议优化的图片 (>500KB)\n"
            for img in unoptimized[:5]:  # 只显示前5个
                report += f"- `{img['path']}`: {img['size_mb']:.1f} MB ({img['format'].upper()})\n"

        # 添加资源统计
        report += ".1f"".1f"        # 生成建议
        report += "\n## 💡 性能优化建议\n"

        suggestions = []

        if self.metrics['build_time'] > 30:
            suggestions.append("⚡ 构建时间较长，考虑启用Hugo缓存或减少页面数量")

        if self.metrics['avg_page_size'] > 100 * 1024:  # > 100KB
            suggestions.append("📄 平均页面大小较大，考虑压缩HTML或减少资源")

        webp_ratio = self.metrics['image_stats'].get('webp_count', 0) / max(self.metrics['image_stats'].get('total_images', 1), 1)
        if webp_ratio < 0.5:
            suggestions.append("🖼️ WebP使用率较低，建议启用图片优化")

        if not suggestions:
            suggestions.append("✅ 性能表现良好，继续保持！")

        for suggestion in suggestions:
            report += f"- {suggestion}\n"

        return report

    def save_report(self, report: str, filename: str = "performance-report.md"):
        """保存报告到文件"""
        report_path = self.output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {report_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Hugo博客性能分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--build-time',
        action='store_true',
        help='分析构建时间'
    )

    parser.add_argument(
        '--analyze-site',
        action='store_true',
        help='分析站点结构和大小'
    )

    parser.add_argument(
        '--check-images',
        action='store_true',
        help='检查图片优化情况'
    )

    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='生成性能报告'
    )

    parser.add_argument(
        '--output-dir',
        default='reports',
        help='输出目录 (默认: reports)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='执行所有分析'
    )

    args = parser.parse_args()

    # 如果没有指定任何选项，默认执行所有分析
    if not any([args.build_time, args.analyze_site, args.check_images, args.generate_report]):
        args.all = True

    analyzer = HugoPerformanceAnalyzer(output_dir=args.output_dir)

    print("🚀 开始Hugo博客性能分析...\n")

    if args.build_time or args.all:
        print("⚠️  跳过构建时间测试（Docker环境）")
        analyzer.metrics['build_time'] = 0  # 设置为0表示未测试
        print()

    if args.analyze_site or args.all:
        analyzer.analyze_site_structure()
        print()

    if args.check_images or args.all:
        analyzer.analyze_images()
        print()

    analyzer.analyze_resources()

    if args.generate_report or args.all:
        report = analyzer.generate_report()
        analyzer.save_report(report)
        print()

    print("✅ 性能分析完成！")

if __name__ == '__main__':
    main()
