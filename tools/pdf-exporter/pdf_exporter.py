#!/usr/bin/env python3
"""
Hugo Blog PDF Exporter

将Hugo博客文章导出为PDF格式，支持离线阅读：
- 基于Playwright的HTML到PDF转换
- 保持原始样式和布局
- 支持自定义PDF样式
- 批量导出功能
- 离线阅读优化

使用方法：
python pdf_exporter.py [选项]

选项：
--input-dir DIR    输入目录（默认: content/）
--output-dir DIR   输出目录（默认: pdf-exports/）
--article PATH    导出单个文章（Markdown文件路径）
--all            导出所有文章
--serve-url URL   Hugo服务器URL（默认: http://localhost:1313）
--format FORMAT   PDF格式 (A4, Letter, 默认: A4)
--quality QUAL    图片质量 (1-100, 默认: 90)
--include-toc     包含目录
--batch-size N    批量处理大小（默认: 5）
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page, Playwright
except ImportError:
    print("错误: 需要安装playwright")
    print("请运行: pip install playwright")
    print("然后运行: playwright install chromium")
    sys.exit(1)

class HugoPDFExporter:
    """Hugo博客PDF导出器"""

    def __init__(self, serve_url: str = "http://localhost:1313",
                 output_dir: str = "pdf-exports",
                 format_type: str = "A4",
                 quality: int = 90,
                 include_toc: bool = True):
        self.serve_url = serve_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.format_type = format_type
        self.quality = quality
        self.include_toc = include_toc

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # PDF样式配置
        self.pdf_options = {
            'format': self.format_type,
            'print_background': True,
            'margin': {
                'top': '1cm',
                'right': '1cm',
                'bottom': '1cm',
                'left': '1cm'
            },
            'prefer_css_page_size': True,
        }

    async def init_browser(self, playwright: Playwright) -> Browser:
        """初始化浏览器"""
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return browser

    def get_article_url(self, md_path: Path) -> Optional[str]:
        """根据Markdown文件路径生成文章URL"""
        # 将content/zh/posts/article.md转换为/zh/posts/article/
        rel_path = md_path.relative_to(md_path.parents[2])  # 获取相对于content的路径
        url_path = str(rel_path).replace('.md', '/').replace('\\', '/')

        # 移除content/前缀
        if url_path.startswith('content/'):
            url_path = url_path[8:]  # 移除'content/'

        return urljoin(self.serve_url + '/', url_path)

    def get_pdf_path(self, md_path: Path) -> Path:
        """生成PDF文件路径"""
        rel_path = md_path.relative_to(md_path.parents[2])
        pdf_name = str(rel_path).replace('.md', '.pdf').replace('\\', '_').replace('/', '_')
        return self.output_dir / pdf_name

    async def inject_pdf_styles(self, page: Page):
        """注入PDF优化的样式"""
        pdf_css = """
        /* PDF优化样式 */
        @page {
            size: A4;
            margin: 2.5cm 2cm 2cm 2cm;
        }

        @media print {
            /* 隐藏导航栏、侧边栏和页脚 */
            .navbar, .footer, .sidebar, nav, .menu, .toc-toggle,
            .social-icons, .pagination, .comments, .share-buttons {
                display: none !important;
            }

            /* 优化文章内容布局 */
            .post-content, article, main {
                max-width: none !important;
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
            }

            /* 文章头部优化 */
            .post-header, .article-header {
                margin-bottom: 2em !important;
                border-bottom: 2px solid #333 !important;
                padding-bottom: 1em !important;
            }

            /* 标题样式优化 */
            h1 {
                font-size: 28pt !important;
                font-weight: bold !important;
                color: #1a1a1a !important;
                margin: 0 0 1em 0 !important;
                page-break-after: avoid;
                line-height: 1.2 !important;
            }

            h2 {
                font-size: 20pt !important;
                font-weight: bold !important;
                color: #2c2c2c !important;
                margin: 2em 0 0.8em 0 !important;
                page-break-after: avoid;
                border-bottom: 1px solid #ccc !important;
                padding-bottom: 0.3em !important;
            }

            h3 {
                font-size: 16pt !important;
                font-weight: bold !important;
                color: #333 !important;
                margin: 1.5em 0 0.6em 0 !important;
                page-break-after: avoid;
            }

            h4, h5, h6 {
                font-size: 14pt !important;
                font-weight: bold !important;
                color: #444 !important;
                margin: 1.2em 0 0.5em 0 !important;
                page-break-after: avoid;
            }

            /* 段落优化 */
            p {
                font-size: 12pt !important;
                line-height: 1.6 !important;
                margin: 0.8em 0 !important;
                text-align: justify !important;
                orphans: 3;
                widows: 3;
            }

            /* 列表优化 */
            ul, ol {
                margin: 1em 0 !important;
                padding-left: 1.5em !important;
            }

            li {
                font-size: 12pt !important;
                line-height: 1.5 !important;
                margin: 0.3em 0 !important;
            }

            /* 代码块优化 */
            pre {
                page-break-inside: avoid;
                background: #f8f8f8 !important;
                border: 1px solid #e0e0e0 !important;
                border-radius: 6px !important;
                padding: 1em !important;
                margin: 1.5em 0 !important;
                font-size: 10pt !important;
                line-height: 1.4 !important;
                overflow-wrap: break-word !important;
                white-space: pre-wrap !important;
            }

            code {
                background: #f5f5f5 !important;
                border: 1px solid #ddd !important;
                border-radius: 3px !important;
                padding: 0.1em 0.3em !important;
                font-size: 10pt !important;
                font-family: 'Courier New', monospace !important;
            }

            /* 引用块优化 */
            blockquote {
                background: #f9f9f9 !important;
                border-left: 4px solid #ccc !important;
                margin: 1.5em 0 !important;
                padding: 1em 1.5em !important;
                font-style: italic !important;
                page-break-inside: avoid;
            }

            /* 表格优化 */
            table {
                page-break-inside: avoid;
                width: 100% !important;
                border-collapse: collapse !important;
                margin: 1.5em 0 !important;
                font-size: 11pt !important;
            }

            th, td {
                border: 1px solid #ccc !important;
                padding: 0.5em !important;
                text-align: left !important;
            }

            th {
                background: #f0f0f0 !important;
                font-weight: bold !important;
            }

            /* 图片优化 */
            img {
                max-width: 100% !important;
                height: auto !important;
                page-break-inside: avoid;
                margin: 1em 0 !important;
                border-radius: 4px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }

            /* 链接样式优化 */
            a {
                color: #0066cc !important;
                text-decoration: underline !important;
            }

            a:visited {
                color: #551a8b !important;
            }

            /* 分页控制 */
            .page-break {
                page-break-before: always;
            }

            .no-break {
                page-break-inside: avoid;
            }

            /* 元信息优化 */
            .post-meta, .article-meta {
                font-size: 10pt !important;
                color: #666 !important;
                margin: 1em 0 2em 0 !important;
                border-top: 1px solid #eee !important;
                padding-top: 1em !important;
            }

            /* 标签优化 */
            .tags, .categories {
                margin: 1em 0 !important;
            }

            .tag, .category {
                display: inline-block !important;
                background: #f0f0f0 !important;
                color: #333 !important;
                padding: 0.2em 0.5em !important;
                margin: 0.2em 0.3em 0.2em 0 !important;
                border-radius: 3px !important;
                font-size: 9pt !important;
                text-decoration: none !important;
            }
        }

        /* 打印友好的链接样式 */
        .print-link::after {
            content: " (" attr(href) ")";
            font-size: 0.8em;
            color: #666;
            font-style: normal;
        }

        /* PDF页眉页脚 */
        @page :first {
            @top-center {
                content: "Hugo Blog - " string(title);
                font-size: 10pt;
                color: #666;
            }
        }

        @page {
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        """

        await page.add_style_tag(content=pdf_css)

    async def wait_for_content_load(self, page: Page, timeout: int = 10000):
        """等待页面内容完全加载"""
        try:
            # 等待主要内容加载
            await page.wait_for_selector('.post-content, article, main', timeout=timeout)

            # 等待图片加载
            await page.wait_for_load_state('networkidle', timeout=timeout)

            # 额外等待确保动态内容加载完成
            await asyncio.sleep(1)

        except Exception as e:
            print(f"警告: 等待内容加载时出现问题: {e}")

    async def export_single_article(self, md_path: Path, browser: Browser) -> Dict[str, Any]:
        """导出单个文章为PDF"""
        result = {
            'file': str(md_path),
            'success': False,
            'pdf_path': None,
            'error': None
        }

        try:
            article_url = self.get_article_url(md_path)
            if not article_url:
                result['error'] = '无法生成文章URL'
                return result

            print(f"📄 导出文章: {md_path.name}")
            print(f"🔗 URL: {article_url}")

            page = await browser.new_page()

            try:
                # 设置视口大小
                await page.set_viewport_size({'width': 1200, 'height': 800})

                # 导航到文章页面
                response = await page.goto(article_url, wait_until='networkidle', timeout=30000)

                if response.status != 200:
                    result['error'] = f'HTTP {response.status}: {response.url}'
                    return result

                # 等待内容加载
                await self.wait_for_content_load(page)

                # 注入PDF样式
                await self.inject_pdf_styles(page)

                # 生成PDF
                pdf_path = self.get_pdf_path(md_path)

                await page.pdf(
                    path=str(pdf_path),
                    **self.pdf_options
                )

                result['success'] = True
                result['pdf_path'] = str(pdf_path)
                result['url'] = article_url

                print(f"✅ PDF已生成: {pdf_path}")

            finally:
                await page.close()

        except Exception as e:
            result['error'] = str(e)
            print(f"❌ 导出失败: {md_path.name} - {e}")

        return result

    async def export_all_articles(self, content_dir: Path, batch_size: int = 5, limit: int = None) -> List[Dict[str, Any]]:
        """批量导出所有文章"""
        # 确保只处理content目录
        if content_dir.name != 'content':
            content_dir = content_dir / 'content'
            if not content_dir.exists():
                raise FileNotFoundError(f"Content目录不存在: {content_dir}")

        # 查找content目录下的所有Markdown文件
        md_files = list(content_dir.rglob('*.md'))

        # 过滤掉_index.md等非文章文件
        article_files = [
            f for f in md_files
            if not f.name.startswith('_') and f.name != 'search.md'
        ]

        # 应用限制
        if limit:
            article_files = article_files[:limit]

        print(f"📚 发现 {len(article_files)} 篇文章待导出{' (限制: ' + str(limit) + ')' if limit else ''}")

        async with async_playwright() as playwright:
            browser = await self.init_browser(playwright)

            try:
                results = []

                # 批量处理
                for i in range(0, len(article_files), batch_size):
                    batch = article_files[i:i+batch_size]
                    print(f"🔄 处理批次 {i//batch_size + 1}/{(len(article_files) + batch_size - 1)//batch_size}")

                    tasks = [
                        self.export_single_article(md_file, browser)
                        for md_file in batch
                    ]

                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in batch_results:
                        if isinstance(result, Exception):
                            results.append({
                                'file': 'unknown',
                                'success': False,
                                'error': str(result)
                            })
                        else:
                            results.append(result)

                    # 批次间暂停，避免服务器过载
                    if i + batch_size < len(article_files):
                        await asyncio.sleep(2)

                return results

            finally:
                await browser.close()

    def generate_export_report(self, results: List[Dict[str, Any]]) -> str:
        """生成导出报告"""
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]

        report = f"""# Hugo博客PDF导出报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 导出统计

- **总文章数**: {len(results)}
- **成功导出**: {len(successful)}
- **导出失败**: {len(failed)}
- **成功率**: {(len(successful) / len(results) * 100):.1f}%

## 📁 输出目录

PDF文件已保存到: `{self.output_dir.absolute()}`

## ✅ 成功导出的文章

"""

        for result in successful[:20]:  # 只显示前20个
            report += f"- **{Path(result['file']).name}**\n"
            report += f"  - PDF: {Path(result['pdf_path']).name}\n"
            report += f"  - URL: {result.get('url', 'N/A')}\n"

        if len(successful) > 20:
            report += f"\n... 还有 {len(successful) - 20} 篇文章成功导出\n"

        if failed:
            report += "\n## ❌ 导出失败的文章\n\n"
            for result in failed:
                report += f"- **{Path(result['file']).name}**\n"
                report += f"  - 错误: {result.get('error', '未知错误')}\n"

        report += "\n## 💡 使用建议\n\n"
        report += "- PDF文件适合离线阅读和分享\n"
        report += "- 保留了原始文章的样式和布局\n"
        report += "- 支持打印和移动设备阅读\n"
        report += f"- 图片质量: {self.quality}%\n"
        report += f"- 页面格式: {self.format_type}\n"

        return report

    def save_report(self, report: str, filename: str = "pdf-export-report.md"):
        """保存报告"""
        report_path = self.output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 导出报告已保存: {report_path}")

async def main():
    parser = argparse.ArgumentParser(
        description="Hugo博客PDF导出工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        default='content',
        help='输入目录 (默认: content)'
    )

    parser.add_argument(
        '--output-dir',
        default='pdf-exports',
        help='输出目录 (默认: pdf-exports)'
    )

    parser.add_argument(
        '--article',
        help='导出单个文章 (Markdown文件路径)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='导出所有文章'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='限制导出数量 (默认: 5)'
    )

    parser.add_argument(
        '--serve-url',
        default='http://localhost:1313',
        help='Hugo服务器URL (默认: http://localhost:1313)'
    )

    parser.add_argument(
        '--format',
        choices=['A4', 'Letter', 'Legal'],
        default='A4',
        help='PDF格式 (默认: A4)'
    )

    parser.add_argument(
        '--quality',
        type=int,
        choices=range(1, 101),
        default=90,
        help='图片质量 1-100 (默认: 90)'
    )

    parser.add_argument(
        '--include-toc',
        action='store_true',
        help='包含目录'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='批量处理大小 (默认: 5)'
    )

    args = parser.parse_args()

    if not (args.article or args.all):
        print("请指定 --article <path> 或 --all")
        sys.exit(1)

    exporter = HugoPDFExporter(
        serve_url=args.serve_url,
        output_dir=args.output_dir,
        format_type=args.format,
        quality=args.quality,
        include_toc=args.include_toc
    )

    try:
        if args.article:
            # 导出单个文章
            article_path_str = args.article

            # 如果是相对路径，从项目根目录开始解析
            if not os.path.isabs(article_path_str):
                # 获取当前脚本所在目录，然后向上找到项目根目录
                script_dir = Path(__file__).parent
                project_root = script_dir.parent.parent  # tools/pdf-exporter -> tools -> project_root
                article_path_str = str(project_root / article_path_str)

            md_path = Path(article_path_str).resolve()
            if not md_path.exists():
                print(f"文件不存在: {md_path} (原始路径: {args.article})")
                sys.exit(1)

            async with async_playwright() as playwright:
                browser = await exporter.init_browser(playwright)
                try:
                    result = await exporter.export_single_article(md_path, browser)
                    if result['success']:
                        print(f"✅ 导出成功: {result['pdf_path']}")
                    else:
                        print(f"❌ 导出失败: {result['error']}")
                finally:
                    await browser.close()

        elif args.all:
            # 导出所有文章
            content_dir = Path(args.input_dir)
            if not content_dir.exists():
                print(f"内容目录不存在: {content_dir}")
                sys.exit(1)

            print("🚀 开始批量导出PDF...")
            results = await exporter.export_all_articles(content_dir, args.batch_size, args.limit)

            # 生成报告
            report = exporter.generate_export_report(results)
            exporter.save_report(report)

            successful = sum(1 for r in results if r.get('success'))
            print(f"📊 导出完成: {successful}/{len(results)} 成功")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断导出")
    except Exception as e:
        print(f"❌ 导出过程中出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
