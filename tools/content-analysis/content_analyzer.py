#!/usr/bin/env python3
"""
Hugo Blog Content Analyzer

分析Hugo博客内容质量和SEO优化：
- 可读性评分 (Flesch-Kincaid, SMOG, Coleman-Liau)
- 关键词提取和分析
- SEO优化建议
- 内容质量评估
- 结构分析

使用方法：
python content_analyzer.py [选项]

选项：
--input-dir DIR    输入目录（默认: content/）
--output-file FILE 输出文件（默认: content-analysis-report.md）
--analyze-single FILE 分析单个文件
--keywords         启用关键词提取
--seo-check        启用SEO检查
--readability      启用可读性分析
--all             执行所有分析（默认）
"""

import os
import sys
import re
import json
import statistics
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
import math
from datetime import datetime

# 中文停用词列表
STOP_WORDS = {
    '的', '了', '和', '是', '就', '都', '而', '及', '与', '着', '或', '一个', '没有', '我们', '你们', '他们',
    '这个', '那个', '这些', '那些', '这里', '那里', '什么', '怎么', '为什么', '怎么样', '可以', '能够',
    '如果', '因为', '所以', '但是', '不过', '虽然', '但是', '而且', '因此', '然后', '就是', '就是',
    '就是说', '也就是说', '比如', '例如', '一般', '通常', '可能', '也许', '大概', '大约', '左右',
    '现在', '今天', '昨天', '明天', '时间', '时候', '目前', '最近', '已经', '还是', '还是', '还是',
    '还是', '还是', '还是', '还是', '还是', '还是', '还是', '还是', '还是', '还是', '还是', '还是'
}

class ContentAnalyzer:
    """Hugo博客内容分析器"""

    def __init__(self, input_dir: str = "content"):
        self.input_dir = Path(input_dir)
        self.analysis_results = {}

        if not self.input_dir.exists():
            raise FileNotFoundError(f"内容目录不存在: {self.input_dir}")

    def extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """提取Hugo frontmatter"""
        frontmatter = {}
        lines = content.split('\n')

        if not lines[0].strip() == '---':
            return frontmatter

        # 查找frontmatter结束标记
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx == -1:
            return frontmatter

        # 解析frontmatter
        frontmatter_lines = lines[1:end_idx]
        frontmatter_text = '\n'.join(frontmatter_lines)

        # 简单解析YAML格式
        for line in frontmatter_lines:
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # 处理数组
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip('"').strip("'") for item in value[1:-1].split(',') if item.strip()]

                frontmatter[key] = value

        return frontmatter

    def extract_content_body(self, content: str) -> str:
        """提取内容主体（去除frontmatter）"""
        lines = content.split('\n')

        if not lines[0].strip() == '---':
            return content

        # 查找frontmatter结束标记
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i + 1
                break

        if end_idx == -1:
            return content

        return '\n'.join(lines[end_idx:])

    def clean_markdown(self, text: str) -> str:
        """清理Markdown标记，返回纯文本"""
        # 移除frontmatter
        text = self.extract_content_body(text)

        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]*`', '', text)

        # 移除链接
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
        text = re.sub(r'https?://[^\s]+', '', text)

        # 移除图片
        text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', '', text)

        # 移除标题标记
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

        # 移除列表标记
        text = re.sub(r'^[\s]*[-\*\+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # 移除粗体和斜体
        text = re.sub(r'\*\*([^\*]*)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]*)\*', r'\1', text)
        text = re.sub(r'_([^_]*)_', r'\1', text)

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """计算可读性分数"""
        if not text:
            return {'flesch_kincaid': 0, 'smog': 0, 'coleman_liau': 0, 'avg_score': 0}

        # 基础统计
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', text)
        chars = len(text.replace(' ', ''))

        total_sentences = len(sentences)
        total_words = len(words)
        total_chars = chars

        if total_sentences == 0 or total_words == 0:
            return {'flesch_kincaid': 0, 'smog': 0, 'coleman_liau': 0, 'avg_score': 0}

        # Flesch-Kincaid Grade Level
        avg_words_per_sentence = total_words / total_sentences
        avg_syllables_per_word = sum(self.count_syllables(word) for word in words) / total_words
        flesch_kincaid = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59

        # SMOG Index
        complex_words = sum(1 for word in words if self.count_syllables(word) >= 3)
        smog = 1.043 * math.sqrt(complex_words * (30 / total_sentences)) + 3.1291

        # Coleman-Liau Index
        avg_chars_per_word = total_chars / total_words
        avg_sentences_per_100_words = (total_sentences / total_words) * 100
        coleman_liau = 0.0588 * avg_chars_per_word - 0.296 * avg_sentences_per_100_words - 15.8

        # 计算平均分数
        avg_score = (flesch_kincaid + smog + coleman_liau) / 3

        return {
            'flesch_kincaid': round(flesch_kincaid, 2),
            'smog': round(smog, 2),
            'coleman_liau': round(coleman_liau, 2),
            'avg_score': round(avg_score, 2),
            'stats': {
                'sentences': total_sentences,
                'words': total_words,
                'chars': total_chars,
                'avg_words_per_sentence': round(avg_words_per_sentence, 1),
                'avg_chars_per_word': round(avg_chars_per_word, 1)
            }
        }

    def count_syllables(self, word: str) -> int:
        """计算单词音节数（简化版）"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"

        if word[0] in vowels:
            count += 1

        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1

        if word.endswith("e"):
            count -= 1

        if count == 0:
            count += 1

        return count

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """提取关键词"""
        # 清理文本
        clean_text = self.clean_markdown(text).lower()

        # 分词（简单按空格和标点分割）
        words = re.findall(r'\b\w+\b', clean_text)

        # 过滤停用词和短词
        filtered_words = [
            word for word in words
            if len(word) > 2 and word not in STOP_WORDS and not word.isdigit()
        ]

        # 统计词频
        word_freq = Counter(filtered_words)

        # 返回最常见的关键词
        return word_freq.most_common(top_n)

    def analyze_seo(self, content: str, filename: str) -> Dict[str, Any]:
        """分析SEO相关指标"""
        frontmatter = self.extract_frontmatter(content)
        body = self.extract_content_body(content)

        seo_analysis = {
            'title': frontmatter.get('title', ''),
            'description': frontmatter.get('description', ''),
            'slug': filename.replace('.md', ''),
            'issues': [],
            'suggestions': []
        }

        # 检查标题
        if not seo_analysis['title']:
            seo_analysis['issues'].append('缺少标题 (title)')
        elif len(seo_analysis['title']) < 30:
            seo_analysis['issues'].append('标题过短 (建议30-60字符)')
        elif len(seo_analysis['title']) > 60:
            seo_analysis['issues'].append('标题过长 (建议30-60字符)')

        # 检查描述
        if not seo_analysis['description']:
            seo_analysis['issues'].append('缺少描述 (description)')
        elif len(seo_analysis['description']) < 120:
            seo_analysis['issues'].append('描述过短 (建议120-160字符)')
        elif len(seo_analysis['description']) > 160:
            seo_analysis['issues'].append('描述过长 (建议120-160字符)')

        # 检查关键词密度
        clean_text = self.clean_markdown(body)
        words = re.findall(r'\b\w+\b', clean_text.lower())
        total_words = len(words)

        if total_words > 0:
            # 计算关键词密度
            keywords = self.extract_keywords(body, 5)
            for keyword, count in keywords:
                density = (count / total_words) * 100
                if density > 5:
                    seo_analysis['issues'].append(f'关键词"{keyword}"密度过高 ({density:.1f}%)')
                elif density < 0.5:
                    seo_analysis['suggestions'].append(f'考虑增加关键词"{keyword}"的使用')

        # 检查URL结构
        if len(seo_analysis['slug']) > 100:
            seo_analysis['issues'].append('URL过长')

        # 检查frontmatter
        if 'date' not in frontmatter:
            seo_analysis['issues'].append('缺少发布日期 (date)')
        if 'draft' not in frontmatter or frontmatter['draft']:
            seo_analysis['issues'].append('文章仍为草稿状态')

        return seo_analysis

    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """分析内容质量"""
        frontmatter = self.extract_frontmatter(content)
        body = self.extract_content_body(content)

        quality = {
            'score': 0,
            'max_score': 100,
            'checks': {},
            'issues': [],
            'strengths': []
        }

        # 检查frontmatter完整性 (20分)
        fm_score = 0
        required_fields = ['title', 'date', 'description']
        for field in required_fields:
            if field in frontmatter:
                fm_score += 7  # 20/3 ≈ 6.67

        quality['checks']['frontmatter'] = fm_score
        if fm_score >= 15:
            quality['strengths'].append('Frontmatter信息完整')
        else:
            quality['issues'].append('Frontmatter信息不完整')

        # 检查内容长度 (25分)
        clean_text = self.clean_markdown(body)
        word_count = len(re.findall(r'\b\w+\b', clean_text))

        if word_count >= 1000:
            content_score = 25
            quality['strengths'].append('内容丰富详细')
        elif word_count >= 500:
            content_score = 20
            quality['strengths'].append('内容适中')
        elif word_count >= 200:
            content_score = 15
        else:
            content_score = 5
            quality['issues'].append('内容过短')

        quality['checks']['content_length'] = content_score

        # 检查结构 (20分)
        headings = re.findall(r'^#{1,6}\s+', body, re.MULTILINE)
        lists = len(re.findall(r'^[\s]*[-\*\+]\s+', body, re.MULTILINE))
        code_blocks = len(re.findall(r'```', body))

        structure_score = min(20, len(headings) * 2 + lists + code_blocks * 3)
        quality['checks']['structure'] = structure_score

        if structure_score >= 15:
            quality['strengths'].append('结构层次清晰')
        elif structure_score < 5:
            quality['issues'].append('结构层次不足')

        # 检查可读性 (20分)
        readability = self.calculate_readability_scores(clean_text)
        avg_score = readability.get('avg_score', 0)

        if 6 <= avg_score <= 8:
            readability_score = 20
            quality['strengths'].append('可读性适中')
        elif 4 <= avg_score <= 10:
            readability_score = 15
        elif 2 <= avg_score <= 12:
            readability_score = 10
        else:
            readability_score = 5
            quality['issues'].append('可读性需要改进')

        quality['checks']['readability'] = readability_score

        # 检查关键词使用 (15分)
        keywords = self.extract_keywords(body, 3)
        if keywords and keywords[0][1] >= 3:
            keyword_score = 15
            quality['strengths'].append('关键词使用得当')
        elif keywords:
            keyword_score = 10
        else:
            keyword_score = 0
            quality['issues'].append('缺少核心关键词')

        quality['checks']['keywords'] = keyword_score

        # 计算总分
        quality['score'] = sum(quality['checks'].values())

        return quality

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = {
                'file': str(file_path.relative_to(self.input_dir)),
                'frontmatter': self.extract_frontmatter(content),
                'stats': {},
                'readability': {},
                'keywords': [],
                'seo': {},
                'quality': {}
            }

            # 基础统计
            body = self.extract_content_body(content)
            clean_text = self.clean_markdown(content)

            analysis['stats'] = {
                'total_chars': len(content),
                'body_chars': len(body),
                'clean_chars': len(clean_text),
                'words': len(re.findall(r'\b\w+\b', clean_text)),
                'sentences': len(re.split(r'[.!?]+', clean_text)),
                'paragraphs': len([p for p in body.split('\n\n') if p.strip()]),
                'headings': len(re.findall(r'^#{1,6}\s+', body, re.MULTILINE)),
                'links': len(re.findall(r'\[([^\]]*)\]\([^\)]*\)', body)),
                'images': len(re.findall(r'!\[([^\]]*)\]\([^\)]*\)', body)),
                'code_blocks': len(re.findall(r'```', body))
            }

            # 可读性分析
            analysis['readability'] = self.calculate_readability_scores(clean_text)

            # 关键词提取
            analysis['keywords'] = self.extract_keywords(content, 10)

            # SEO分析
            analysis['seo'] = self.analyze_seo(content, file_path.name)

            # 质量分析
            analysis['quality'] = self.analyze_content_quality(content)

            return analysis

        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.input_dir)),
                'error': str(e)
            }

    def analyze_directory(self) -> Dict[str, Any]:
        """分析整个目录"""
        results = {
            'summary': {
                'total_files': 0,
                'analyzed_files': 0,
                'error_files': 0,
                'avg_quality_score': 0,
                'avg_readability': 0,
                'total_words': 0
            },
            'files': [],
            'quality_distribution': {},
            'readability_distribution': {},
            'top_keywords': [],
            'seo_issues': []
        }

        all_keywords = Counter()
        quality_scores = []
        readability_scores = []
        seo_issues = []

        # 分析所有Markdown文件
        for md_file in self.input_dir.rglob('*.md'):
            results['summary']['total_files'] += 1

            analysis = self.analyze_file(md_file)

            if 'error' in analysis:
                results['summary']['error_files'] += 1
            else:
                results['summary']['analyzed_files'] += 1
                results['files'].append(analysis)

                # 收集统计数据
                quality_scores.append(analysis['quality']['score'])
                readability_scores.append(analysis['readability']['avg_score'])
                results['summary']['total_words'] += analysis['stats']['words']

                # 收集关键词
                for keyword, count in analysis['keywords']:
                    all_keywords[keyword] += count

                # 收集SEO问题
                seo_issues.extend(analysis['seo']['issues'])

        # 计算汇总统计
        if quality_scores:
            results['summary']['avg_quality_score'] = round(statistics.mean(quality_scores), 1)

        if readability_scores:
            results['summary']['avg_readability'] = round(statistics.mean(readability_scores), 1)

        # 质量分布
        for score in quality_scores:
            level = '优秀' if score >= 80 else '良好' if score >= 60 else '一般' if score >= 40 else '需改进'
            results['quality_distribution'][level] = results['quality_distribution'].get(level, 0) + 1

        # 可读性分布
        for score in readability_scores:
            level = '容易' if score <= 6 else '适中' if score <= 8 else '较难' if score <= 10 else '困难'
            results['readability_distribution'][level] = results['readability_distribution'].get(level, 0) + 1

        # 热门关键词
        results['top_keywords'] = all_keywords.most_common(20)

        # SEO问题汇总
        results['seo_issues'] = list(set(seo_issues))

        self.analysis_results = results
        return results

    def generate_report(self, output_file: str = "content-analysis-report.md"):
        """生成分析报告"""
        if not self.analysis_results:
            self.analyze_directory()

        results = self.analysis_results

        report = f"""# Hugo博客内容分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体统计

- **总文件数**: {results['summary']['total_files']}
- **成功分析**: {results['summary']['analyzed_files']}
- **分析失败**: {results['summary']['error_files']}
- **总字数**: {results['summary']['total_words']:,}
- **平均质量分数**: {results['summary']['avg_quality_score']}/100
- **平均可读性**: {results['summary']['avg_readability']}

## 📈 质量分布

"""

        for level, count in results['quality_distribution'].items():
            percentage = (count / results['summary']['analyzed_files']) * 100
            report += f"- **{level}**: {count} 篇 ({percentage:.1f}%)\n"

        report += "\n## 📖 可读性分布\n\n"

        for level, count in results['readability_distribution'].items():
            percentage = (count / results['summary']['analyzed_files']) * 100
            report += f"- **{level}**: {count} 篇 ({percentage:.1f}%)\n"

        report += "\n## 🔥 热门关键词\n\n"

        for keyword, count in results['top_keywords'][:10]:
            report += f"- **{keyword}**: {count} 次\n"

        report += "\n## ⚠️ SEO问题汇总\n\n"

        if results['seo_issues']:
            for issue in results['seo_issues']:
                report += f"- {issue}\n"
        else:
            report += "暂无明显SEO问题\n"

        report += "\n## 📋 详细文件分析\n\n"

        for file_analysis in results['files'][:5]:  # 只显示前5个文件的详细分析
            report += f"### {file_analysis['file']}\n\n"
            report += f"- **质量分数**: {file_analysis['quality']['score']}/100\n"
            report += f"- **可读性**: {file_analysis['readability']['avg_score']}\n"
            report += f"- **字数**: {file_analysis['stats']['words']}\n"

            if file_analysis['seo']['issues']:
                report += f"- **SEO问题**: {', '.join(file_analysis['seo']['issues'][:3])}\n"

            if file_analysis['keywords']:
                top_keywords = [kw for kw, _ in file_analysis['keywords'][:3]]
                report += f"- **关键词**: {', '.join(top_keywords)}\n"

            report += "\n"

        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 分析报告已保存到: {output_file}")
        return report

def main():
    parser = argparse.ArgumentParser(
        description="Hugo博客内容分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        default='content',
        help='输入目录 (默认: content)'
    )

    parser.add_argument(
        '--output-file',
        default='content-analysis-report.md',
        help='输出文件 (默认: content-analysis-report.md)'
    )

    parser.add_argument(
        '--analyze-single',
        help='分析单个文件'
    )

    parser.add_argument(
        '--keywords',
        action='store_true',
        help='启用关键词提取'
    )

    parser.add_argument(
        '--seo-check',
        action='store_true',
        help='启用SEO检查'
    )

    parser.add_argument(
        '--readability',
        action='store_true',
        help='启用可读性分析'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='执行所有分析 (默认)'
    )

    args = parser.parse_args()

    # 如果没有指定任何选项，默认执行所有分析
    if not any([args.keywords, args.seo_check, args.readability]):
        args.all = True

    try:
        analyzer = ContentAnalyzer(args.input_dir)

        if args.analyze_single:
            # 分析单个文件
            file_path = Path(args.analyze_single)
            if file_path.exists():
                analysis = analyzer.analyze_file(file_path)
                print(json.dumps(analysis, ensure_ascii=False, indent=2))
            else:
                print(f"文件不存在: {file_path}")
        else:
            # 分析整个目录
            analyzer.analyze_directory()
            analyzer.generate_report(args.output_file)

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
