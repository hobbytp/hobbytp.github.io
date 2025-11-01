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

# 可选导入OpenAI和dotenv
try:
    import openai
except ImportError:
    openai = None

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from rich.console import Console
    from rich.json import JSON
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    load_dotenv = None

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

        # 初始化OpenAI客户端
        self.openai_client = None

        if openai:
            try:
                # 优先加载.env文件，确保.env文件的配置优先级最高
                if DOTENV_AVAILABLE:
                    load_dotenv(override=True)  # override=True 确保.env文件覆盖现有环境变量
                    print("📄 已加载 .env 文件配置")
                else:
                    print("⚠️  未找到 python-dotenv，无法加载 .env 文件")

                # 从环境变量获取配置（此时.env文件的值已经被加载）
                api_key = os.getenv('OPENAI_API_KEY')
                base_url = os.getenv('OPENAI_BASE_URL')
                model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

                # 打印API配置信息（安全显示）
                print("\n🔧 OpenAI 配置信息:")
                if api_key:
                    print(f"🔑 OPENAI_API_KEY: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
                else:
                    print("❌ OPENAI_API_KEY: 未设置")

                if base_url:
                    print(f"🌐 OPENAI_BASE_URL: {base_url}")
                else:
                    print("🌐 OPENAI_BASE_URL: 使用默认 (https://api.openai.com/v1)")

                print(f"🤖 OPENAI_MODEL: {model}")
                print()

                self.openai_model = model

                if not api_key:
                    print("⚠️ 警告: 未找到OPENAI_API_KEY环境变量")
                    print("AI增强分析功能将被禁用")
                    return

                client_kwargs = {'api_key': api_key}
                if base_url:
                    client_kwargs['base_url'] = base_url

                self.openai_client = openai.OpenAI(**client_kwargs)
                print(f"✅ OpenAI客户端初始化成功 (模型: {self.openai_model})")

            except Exception as e:
                print(f"警告: OpenAI客户端初始化失败: {e}")
                print("AI增强分析功能将被禁用")

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

    def analyze_content_quality_ai(self, content: str) -> Dict[str, Any]:
        """使用AI进行智能内容质量分析"""
        if not self.openai_client:
            return {
                'ai_analysis': None,
                'error': 'OpenAI API未配置，请设置OPENAI_API_KEY环境变量'
            }

        try:
            frontmatter = self.extract_frontmatter(content)
            body = self.extract_content_body(content)
            clean_text = self.clean_markdown(content)

            # 限制文本长度，避免API限制
            analysis_text = clean_text[:16000] + "..." if len(clean_text) > 16000 else clean_text

            prompt = f"""请对以下博客文章进行智能分析，重点关注内容质量、结构完整性、读者价值等方面。

文章标题: {frontmatter.get('title', '无标题')}
文章描述: {frontmatter.get('description', '无描述')}

文章内容:
{analysis_text}

先分析文章类型，然后以专业的角度，从以下维度进行分析（每项给出1-10分，并简要说明理由）：

1. 内容深度 (1-10分): 内容的专业深度和知识价值
2. 结构完整性 (1-10分): 文章结构是否清晰合理
3. 读者价值 (1-10分): 对读者是否有实际帮助和启发
4. 写作质量 (1-10分): 语言表达、逻辑性和可读性
5. 创新性 (1-10分): 是否有新颖的观点或见解

综合评分 (1-100分): 基于以上维度给出的总体评分

改进建议: 列出2-3个最重要的改进点

总体评价: 用一句话总结文章质量"""

            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容质量分析师，擅长分析技术博客文章的质量。请提供客观、建设性的分析。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )

            ai_response = response.choices[0].message.content

            # 解析AI响应
            analysis = self._parse_ai_analysis(ai_response)

            return {
                'ai_analysis': analysis,
                'raw_response': ai_response,
                'model': self.openai_model
            }

        except Exception as e:
            return {
                'ai_analysis': None,
                'error': f'AI分析失败: {str(e)}'
            }

    def _parse_ai_analysis(self, ai_response: str) -> Dict[str, Any]:
        """解析AI分析结果"""
        analysis = {
            'dimensions': {},
            'overall_score': 0,
            'improvement_suggestions': [],
            'overall_assessment': '',
            'confidence': 0.8  # 默认置信度
        }

        lines = ai_response.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 解析各维度评分
            for dimension in ['内容深度', '结构完整性', '读者价值', '写作质量', '创新性']:
                if dimension in line and ('分' in line or '/10' in line):
                    try:
                        # 提取数字分数
                        import re
                        score_match = re.search(r'(\d+(?:\.\d+)?)', line)
                        if score_match:
                            score = float(score_match.group(1))
                            if score <= 10:  # 确保是有效分数
                                analysis['dimensions'][dimension] = score
                    except:
                        pass

            # 解析综合评分
            if '综合评分' in line or '总体评分' in line:
                try:
                    import re
                    score_match = re.search(r'(\d+(?:\.\d+)?)', line)
                    if score_match:
                        score = float(score_match.group(1))
                        if score <= 100:  # 确保是有效分数
                            analysis['overall_score'] = score
                except:
                    pass

            # 解析改进建议
            if '改进建议' in line or any(word in line for word in ['建议', '可以', '应该', '需要']):
                if ':' in line:
                    suggestion = line.split(':', 1)[1].strip()
                    if suggestion and len(suggestion) > 5:
                        analysis['improvement_suggestions'].append(suggestion)

            # 解析总体评价
            if '总体评价' in line or '一句话总结' in line:
                if ':' in line:
                    assessment = line.split(':', 1)[1].strip()
                    if assessment:
                        analysis['overall_assessment'] = assessment

        # 计算平均维度分数作为备选综合评分
        if not analysis['overall_score'] and analysis['dimensions']:
            avg_dimension_score = sum(analysis['dimensions'].values()) / len(analysis['dimensions'])
            analysis['overall_score'] = avg_dimension_score * 10  # 转换为0-100分制

        return analysis

    def analyze_content_quality(self, content: str, enable_ai: bool = False) -> Dict[str, Any]:
        """分析内容质量（传统方法 + 可选AI增强）"""
        frontmatter = self.extract_frontmatter(content)
        body = self.extract_content_body(content)

        quality = {
            'score': 0,
            'max_score': 100,
            'checks': {},
            'issues': [],
            'strengths': [],
            'ai_enhanced': enable_ai
        }

        # AI增强分析
        if enable_ai:
            ai_analysis = self.analyze_content_quality_ai(content)
            quality['ai_analysis'] = ai_analysis

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

    def analyze_file(self, file_path: Path, enable_ai: bool = False) -> Dict[str, Any]:
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
                'quality': {},
                'ai_enhanced': enable_ai
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
            analysis['quality'] = self.analyze_content_quality(content, enable_ai)

            # 健康度分析
            analysis['health'] = self.analyze_content_health(content, file_path)

            return analysis

        except Exception as e:
            return {
                'file': str(file_path.relative_to(self.input_dir)),
                'error': str(e)
            }

    def analyze_content_health(self, content: str, file_path: Path) -> Dict[str, Any]:
        """分析内容健康度（借鉴Jimmy Song的实现）"""
        frontmatter = self.extract_frontmatter(content)
        body = self.extract_content_body(content)

        health = {
            'score': 100,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }

        # 检查必需的frontmatter字段
        required_fields = ['title', 'date', 'description']
        for field in required_fields:
            if field not in frontmatter or not frontmatter[field]:
                health['issues'].append(f'缺失必需字段: {field}')
                health['score'] -= 20

        # 检查描述长度
        description = frontmatter.get('description', '')
        if len(description) < 50:
            health['warnings'].append('描述过短，建议120-160字符')
            health['score'] -= 5
        elif len(description) > 160:
            health['warnings'].append('描述过长，可能影响SEO')
            health['score'] -= 5

        # 检查标签和分类
        tags = frontmatter.get('tags', [])
        categories = frontmatter.get('categories', [])
        if not tags and not categories:
            health['warnings'].append('缺少标签或分类，影响内容组织')
            health['score'] -= 10

        # 检查图片alt文本
        images = re.findall(r'!\[([^\]]*)\]\([^\)]*\)', body)
        missing_alt = [img for img in images if not img.strip()]
        if missing_alt:
            health['warnings'].append(f'发现{len(missing_alt)}张图片缺少alt文本')
            health['score'] -= len(missing_alt) * 2

        # 检查标题层级
        headings = re.findall(r'^(#{1,6})\s+', body, re.MULTILINE)
        heading_levels = [len(h) for h in headings]
        if heading_levels and min(heading_levels) > 1:
            health['warnings'].append('缺少一级标题(H1)')
            health['score'] -= 10

        # 检查标题层级跳跃
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i-1] + 1:
                health['warnings'].append('标题层级跳跃，可能影响可读性')
                health['score'] -= 5
                break

        # 检查内容长度
        word_count = len(re.findall(r'\b\w+\b', body))
        if word_count < 300:
            health['suggestions'].append('内容较短，建议增加更多细节')
        elif word_count > 3000:
            health['suggestions'].append('内容过长，建议考虑拆分为多篇文章')

        health['score'] = max(0, min(100, health['score']))
        return health

    def analyze_content_distribution(self, files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析内容分布（借鉴Jimmy Song的实现）"""
        distribution = {
            'by_category': {},
            'by_tag': {},
            'by_content_type': {},
            'by_date': {},
            'by_reading_time': {'short': 0, 'medium': 0, 'long': 0}
        }

        for file_data in files_data:
            if 'error' in file_data:
                continue

            frontmatter = file_data.get('frontmatter', {})

            # 按分类统计
            categories = frontmatter.get('categories', [])
            for category in categories:
                distribution['by_category'][category] = distribution['by_category'].get(category, 0) + 1

            # 按标签统计
            tags = frontmatter.get('tags', [])
            for tag in tags:
                distribution['by_tag'][tag] = distribution['by_tag'].get(tag, 0) + 1

            # 按内容类型统计（基于文件路径）
            file_path = file_data.get('file', '')
            if 'posts' in file_path or 'blog' in file_path:
                content_type = 'blog_posts'
            elif 'pages' in file_path:
                content_type = 'pages'
            elif 'docs' in file_path:
                content_type = 'documentation'
            else:
                content_type = 'other'

            distribution['by_content_type'][content_type] = distribution['by_content_type'].get(content_type, 0) + 1

            # 按日期统计
            date_str = frontmatter.get('date', '')
            if date_str:
                try:
                    # 提取年月
                    if isinstance(date_str, str) and len(date_str) >= 7:
                        year_month = date_str[:7]  # YYYY-MM
                        distribution['by_date'][year_month] = distribution['by_date'].get(year_month, 0) + 1
                except:
                    pass

            # 按阅读时间统计
            stats = file_data.get('stats', {})
            word_count = stats.get('words', 0)
            reading_time = word_count / 200  # 假设每分钟阅读200字

            if reading_time < 5:
                distribution['by_reading_time']['short'] += 1
            elif reading_time < 15:
                distribution['by_reading_time']['medium'] += 1
            else:
                distribution['by_reading_time']['long'] += 1

        return distribution

    def analyze_growth_trends(self, files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析增长趋势（借鉴Jimmy Song的实现）"""
        trends = {
            'monthly_creation': {},
            'content_velocity': [],
            'quality_trends': {},
            'word_count_trends': {}
        }

        # 收集每月创建的内容数量
        for file_data in files_data:
            if 'error' in file_data:
                continue

            frontmatter = file_data.get('frontmatter', {})
            date_str = frontmatter.get('date', '')

            if date_str and isinstance(date_str, str) and len(date_str) >= 7:
                try:
                    year_month = date_str[:7]  # YYYY-MM
                    trends['monthly_creation'][year_month] = trends['monthly_creation'].get(year_month, 0) + 1

                    # 收集质量和字数趋势
                    quality_score = file_data.get('quality', {}).get('score', 0)
                    word_count = file_data.get('stats', {}).get('words', 0)

                    if year_month not in trends['quality_trends']:
                        trends['quality_trends'][year_month] = []
                        trends['word_count_trends'][year_month] = []

                    trends['quality_trends'][year_month].append(quality_score)
                    trends['word_count_trends'][year_month].append(word_count)

                except:
                    pass

        # 计算内容创建速度（月环比增长）
        sorted_months = sorted(trends['monthly_creation'].keys())
        for i in range(1, len(sorted_months)):
            current_month = sorted_months[i]
            prev_month = sorted_months[i-1]

            current_count = trends['monthly_creation'][current_month]
            prev_count = trends['monthly_creation'].get(prev_month, 0)

            if prev_count > 0:
                velocity = {
                    'month': current_month,
                    'posts': current_count,
                    'change': current_count - prev_count,
                    'change_percent': ((current_count - prev_count) / prev_count) * 100
                }
                trends['content_velocity'].append(velocity)

        # 计算平均质量和字数趋势
        for month in trends['quality_trends']:
            if trends['quality_trends'][month]:
                trends['quality_trends'][month] = sum(trends['quality_trends'][month]) / len(trends['quality_trends'][month])

        for month in trends['word_count_trends']:
            if trends['word_count_trends'][month]:
                trends['word_count_trends'][month] = sum(trends['word_count_trends'][month]) / len(trends['word_count_trends'][month])

        return trends

    def analyze_directory(self, enable_ai: bool = False) -> Dict[str, Any]:
        """分析整个目录"""
        results = {
            'summary': {
                'total_files': 0,
                'analyzed_files': 0,
                'error_files': 0,
                'avg_quality_score': 0,
                'avg_readability': 0,
                'total_words': 0,
                'health_score': 0
            },
            'files': [],
            'quality_distribution': {},
            'readability_distribution': {},
            'top_keywords': [],
            'seo_issues': [],
            'distribution': {},
            'trends': {},
            'health_analysis': [],
            'ai_enhanced': enable_ai
        }

        all_keywords = Counter()
        quality_scores = []
        readability_scores = []
        seo_issues = []

        # 分析所有Markdown文件
        for md_file in self.input_dir.rglob('*.md'):
            results['summary']['total_files'] += 1

            analysis = self.analyze_file(md_file, enable_ai)

            if 'error' in analysis:
                results['summary']['error_files'] += 1
            else:
                results['summary']['analyzed_files'] += 1
                results['files'].append(analysis)
                results['ai_enhanced'] = enable_ai

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

        # 内容分布分析（借鉴Jimmy Song）
        results['distribution'] = self.analyze_content_distribution(results['files'])

        # 增长趋势分析（借鉴Jimmy Song）
        results['trends'] = self.analyze_growth_trends(results['files'])

        # 健康度分析汇总
        health_scores = []
        for file_data in results['files']:
            if 'health' in file_data:
                health_scores.append(file_data['health']['score'])

        if health_scores:
            results['summary']['health_score'] = round(statistics.mean(health_scores), 1)

        self.analysis_results = results
        return results

    def generate_json_data(self, output_file: str = "content-analysis-data.json", enable_ai: bool = False):
        """生成JSON格式的分析数据（供前端仪表板使用）"""
        if not self.analysis_results:
            self.analyze_directory(enable_ai)

        results = self.analysis_results

        # 清理不需要的数据，优化JSON大小
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': results['summary'],
            'distribution': results.get('distribution', {}),
            'trends': results.get('trends', {}),
            'seo_issues': results['seo_issues'],
            'top_keywords': results['top_keywords'][:20],  # 只保留前20个关键词
            'ai_enhanced': results.get('ai_enhanced', False),
            'files_count': len(results['files'])
        }

        # 保存JSON数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"📄 JSON数据已保存到: {output_file}")
        return json_data

    def generate_report(self, output_file: str = "content-analysis-report.md", enable_ai: bool = False):
        """生成分析报告"""
        if not self.analysis_results:
            self.analyze_directory(enable_ai)

        results = self.analysis_results

        ai_indicator = " 🤖 AI增强版" if results.get('ai_enhanced') else ""

        report = f"""# Hugo博客内容分析报告{ai_indicator}

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

        # 内容分布分析（借鉴Jimmy Song）
        if results.get('distribution'):
            report += "\n## 📊 内容分布分析\n\n"

            dist = results['distribution']

            # 按分类分布
            if dist['by_category']:
                report += "### 按分类分布\n\n"
                sorted_categories = sorted(dist['by_category'].items(), key=lambda x: x[1], reverse=True)
                for category, count in sorted_categories[:10]:
                    report += f"- **{category}**: {count} 篇\n"
                report += "\n"

            # 按标签分布
            if dist['by_tag']:
                report += "### 按标签分布\n\n"
                sorted_tags = sorted(dist['by_tag'].items(), key=lambda x: x[1], reverse=True)
                for tag, count in sorted_tags[:15]:
                    report += f"- **{tag}**: {count} 次\n"
                report += "\n"

            # 按阅读时间分布
            report += "### 按阅读时间分布\n\n"
            reading_dist = dist['by_reading_time']
            total = sum(reading_dist.values())
            if total > 0:
                for time_range, count in reading_dist.items():
                    percentage = (count / total) * 100
                    time_label = {'short': '短文 (<5min)', 'medium': '中等 (5-15min)', 'long': '长文 (>15min)'}[time_range]
                    report += f"- **{time_label}**: {count} 篇 ({percentage:.1f}%)\n"
            report += "\n"

        # 增长趋势分析（借鉴Jimmy Song）
        if results.get('trends'):
            report += "\n## 📈 增长趋势分析\n\n"

            trends = results['trends']

            # 月度内容创建趋势
            if trends['monthly_creation']:
                report += "### 月度内容创建趋势\n\n"
                sorted_months = sorted(trends['monthly_creation'].items())
                for month, count in sorted_months[-6:]:  # 最近6个月
                    report += f"- **{month}**: {count} 篇\n"
                report += "\n"

            # 内容创建速度
            if trends['content_velocity']:
                report += "### 内容创建速度\n\n"
                for velocity in trends['content_velocity'][-3:]:  # 最近3个月的速度
                    change_symbol = "📈" if velocity['change'] > 0 else "📉" if velocity['change'] < 0 else "➡️"
                    report += f"- **{velocity['month']}**: {velocity['posts']} 篇 {change_symbol} {velocity['change']:+d} ({velocity['change_percent']:+.1f}%)\n"
                report += "\n"

        # 内容健康度分析
        if results['summary'].get('health_score'):
            report += "\n## 🏥 内容健康度分析\n\n"

            health_score = results['summary']['health_score']
            health_level = "优秀" if health_score >= 90 else "良好" if health_score >= 75 else "一般" if health_score >= 60 else "需改进"

            report += f"- **整体健康度**: {health_score}/100 ({health_level})\n"
            report += f"- **健康文件数**: {len([f for f in results['files'] if f.get('health', {}).get('score', 0) >= 80])}/{results['summary']['analyzed_files']}\n\n"

            # 汇总常见健康问题
            all_issues = []
            all_warnings = []
            for file_data in results['files']:
                if 'health' in file_data:
                    all_issues.extend(file_data['health']['issues'])
                    all_warnings.extend(file_data['health']['warnings'])

            if all_issues:
                report += "### 常见问题\n\n"
                issue_counts = {}
                for issue in all_issues:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    report += f"- {issue} ({count} 次)\n"
                report += "\n"

            if all_warnings:
                report += "### 优化建议\n\n"
                warning_counts = {}
                for warning in all_warnings:
                    warning_counts[warning] = warning_counts.get(warning, 0) + 1
                for warning, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    report += f"- {warning} ({count} 次)\n"
                report += "\n"

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

        # AI分析结果
        if results.get('ai_enhanced'):
            report += "\n## 🤖 AI智能分析结果\n\n"

            ai_analyses = []
            for file_result in results['files']:
                if file_result.get('quality', {}).get('ai_analysis', {}).get('ai_analysis'):
                    ai_analysis = file_result['quality']['ai_analysis']['ai_analysis']
                    if ai_analysis.get('overall_score', 0) > 0:
                        ai_analyses.append({
                            'file': file_result['file'],
                            'score': ai_analysis['overall_score'],
                            'assessment': ai_analysis.get('overall_assessment', ''),
                            'dimensions': ai_analysis.get('dimensions', {})
                        })

            if ai_analyses:
                # 按AI评分排序
                ai_analyses.sort(key=lambda x: x['score'], reverse=True)

                report += "### 🎯 AI评分Top 5\n\n"
                for i, analysis in enumerate(ai_analyses[:5], 1):
                    report += f"{i}. **{Path(analysis['file']).name}**\n"
                    report += f"   - AI评分: {analysis['score']:.1f}/100\n"
                    if analysis['assessment']:
                        report += f"   - 评价: {analysis['assessment']}\n"
                    if analysis['dimensions']:
                        dims = [f"{k}:{v:.1f}" for k, v in analysis['dimensions'].items()]
                        report += f"   - 维度: {', '.join(dims)}\n"
                    report += "\n"

                # AI改进建议汇总
                all_suggestions = []
                for file_result in results['files']:
                    ai_data = file_result.get('quality', {}).get('ai_analysis', {}).get('ai_analysis', {})
                    suggestions = ai_data.get('improvement_suggestions', [])
                    all_suggestions.extend(suggestions)

                if all_suggestions:
                    report += "### 💡 AI改进建议汇总\n\n"
                    # 统计建议频率
                    from collections import Counter
                    suggestion_counts = Counter(all_suggestions)
                    for suggestion, count in suggestion_counts.most_common(5):
                        report += f"- {suggestion} ({count}次提到)\n"
                    report += "\n"

        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 分析报告已保存到: {output_file}")
        return report

def print_analysis_result(analysis: Dict[str, Any]) -> None:
    """美化输出分析结果"""
    if RICH_AVAILABLE:
        console = Console()

        # 创建标题
        title = Text("📊 内容分析结果", style="bold blue")
        console.print(Panel(title, expand=False))

        # 美化JSON输出
        json_str = json.dumps(analysis, ensure_ascii=False, indent=2)
        json_obj = JSON(json_str)
        console.print(json_obj)
    else:
        # 回退到普通JSON输出
        print(json.dumps(analysis, ensure_ascii=False, indent=2))

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
        '--json-data',
        action='store_true',
        help='生成JSON数据文件供前端仪表板使用'
    )

    parser.add_argument(
        '--json-output',
        default='content-analysis-data.json',
        help='JSON数据输出文件 (默认: content-analysis-data.json)'
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

    parser.add_argument(
        '--ai-enhance',
        action='store_true',
        help='启用AI增强分析 (需要OpenAI API密钥)'
    )

    args = parser.parse_args()

    # 如果没有指定任何选项，默认执行所有分析
    if not any([args.keywords, args.seo_check, args.readability]):
        args.all = True

    try:
        if args.analyze_single:
            # 分析单个文件 - 不需要初始化整个目录分析器
            import os
            file_path_str = args.analyze_single

            # 如果是相对路径，从项目根目录开始解析
            if not os.path.isabs(file_path_str):
                # 获取当前脚本所在目录，然后向上找到项目根目录
                script_dir = Path(__file__).parent
                project_root = script_dir.parent.parent  # tools/content-analysis -> tools -> project_root
                file_path_str = str(project_root / file_path_str)

            file_path = Path(file_path_str).resolve()
            if file_path.exists():
                # 使用文件所在目录的父目录作为content根目录
                content_root = file_path.parent.parent
                analyzer = ContentAnalyzer(str(content_root))
                analysis = analyzer.analyze_file(file_path, args.ai_enhance)
                print_analysis_result(analysis)
            else:
                print(f"文件不存在: {file_path} (原始路径: {args.analyze_single})")
        else:
            # 分析整个目录
            analyzer = ContentAnalyzer(args.input_dir)
            analyzer.analyze_directory(args.ai_enhance)

            # 根据参数生成相应格式
            if args.json_data:
                analyzer.generate_json_data(args.json_output, args.ai_enhance)
            else:
                analyzer.generate_report(args.output_file, args.ai_enhance)

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
