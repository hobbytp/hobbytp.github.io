# Hugo Blog Content Analyzer

分析Hugo博客内容质量、SEO优化和可读性，提供详细的优化建议。

## 功能特性

- 📊 **可读性分析**: Flesch-Kincaid、SMOG、Coleman-Liau算法评分
- 🔍 **关键词提取**: 自动提取内容关键词和标签
- 🔍 **SEO优化检查**: 标题、描述、URL结构分析
- 📈 **质量评估**: 综合评分系统 (0-100分)
- 📝 **详细报告**: Markdown格式的完整分析报告
- 🎯 **单文件分析**: 支持分析单个文件或整个目录

## 安装依赖

本工具使用Python标准库，无需额外依赖。

## 基本用法

### 1. 分析整个content目录

```bash
python content_analyzer.py
```

### 2. 生成内容分析报告

```bash
python content_analyzer.py --output-file my-report.md
```

### 3. 分析单个文件

```bash
python content_analyzer.py --analyze-single content/zh/posts/my-article.md
```

### 4. 仅执行关键词分析

```bash
python content_analyzer.py --keywords
```

## 命令行选项

| 选项 | 描述 |
|------|------|
| `--input-dir DIR` | 输入目录 (默认: content) |
| `--output-file FILE` | 输出文件 (默认: content-analysis-report.md) |
| `--analyze-single FILE` | 分析单个文件 |
| `--keywords` | 仅执行关键词提取 |
| `--seo-check` | 仅执行SEO检查 |
| `--readability` | 仅执行可读性分析 |
| `--all` | 执行所有分析 (默认) |

## 分析指标

### 可读性评分

基于三种经典算法计算可读性：

- **Flesch-Kincaid**: 适合英语，考虑单词长度和句子长度
- **SMOG**: 适合长文本，考虑复杂单词比例
- **Coleman-Liau**: 基于字符统计，不依赖音节分析

评分标准：
- **0-6**: 容易阅读 (小学水平)
- **6-8**: 适中难度 (中学水平)
- **8-10**: 较难阅读 (高中水平)
- **10+**: 困难阅读 (大学水平以上)

### 质量评估 (100分制)

#### Frontmatter完整性 (20分)
- 标题、日期、描述等字段完整性

#### 内容长度 (25分)
- 200字以下: 5分
- 500字以上: 15分
- 1000字以上: 25分

#### 结构层次 (20分)
- 标题数量、列表、代码块等

#### 可读性 (20分)
- 基于可读性算法的评分

#### 关键词使用 (15分)
- 核心关键词的密度和分布

### SEO检查

- **标题长度**: 30-60字符
- **描述长度**: 120-160字符
- **关键词密度**: 0.5%-5%
- **URL结构**: 不超过100字符

## 输出示例

### 总体统计报告

```
# Hugo博客内容分析报告

生成时间: 2025-10-31 23:30:00

## 📊 总体统计

- **总文件数**: 156
- **成功分析**: 152
- **分析失败**: 4
- **总字数**: 245,680
- **平均质量分数**: 78.5/100
- **平均可读性**: 7.2

## 📈 质量分布

- **优秀**: 45 篇 (29.6%)
- **良好**: 67 篇 (44.1%)
- **一般**: 32 篇 (21.1%)
- **需改进**: 8 篇 (5.3%)

## 📖 可读性分布

- **容易**: 23 篇 (15.1%)
- **适中**: 89 篇 (58.6%)
- **较难**: 35 篇 (23.0%)
- **困难**: 5 篇 (3.3%)

## 🔥 热门关键词

- **AI**: 1247 次
- **机器学习**: 892 次
- **深度学习**: 756 次
- **模型**: 645 次
- **数据**: 534 次

## ⚠️ SEO问题汇总

- 缺少描述 (description)
- 标题过短 (建议30-60字符)
- 关键词密度过高
```

### 单文件详细分析

```json
{
  "file": "zh/posts/ai-trends-2025.md",
  "frontmatter": {
    "title": "2025年AI发展趋势分析",
    "date": "2025-01-15",
    "description": "深度分析2025年人工智能领域的关键发展趋势...",
    "tags": ["AI", "趋势", "预测"]
  },
  "stats": {
    "total_chars": 15420,
    "words": 2158,
    "sentences": 142,
    "headings": 8,
    "links": 15,
    "images": 3,
    "code_blocks": 2
  },
  "readability": {
    "flesch_kincaid": 8.5,
    "smog": 7.8,
    "coleman_liau": 9.2,
    "avg_score": 8.5
  },
  "keywords": [
    ["AI", 45],
    ["趋势", 23],
    ["发展", 18],
    ["技术", 15]
  ],
  "seo": {
    "issues": [],
    "suggestions": ["考虑增加关键词'预测'的使用"]
  },
  "quality": {
    "score": 92,
    "issues": [],
    "strengths": [
      "Frontmatter信息完整",
      "内容丰富详细",
      "结构层次清晰",
      "可读性适中",
      "关键词使用得当"
    ]
  }
}
```

## 集成到Hugo工作流

### Makefile集成

```makefile
# 内容分析
analyze-content:
    @echo "📊 分析内容质量..."
    @cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py

# 构建前自动分析
pre-build: analyze-content

# 完整工作流
build: pre-build hugo-build post-build
```

### GitHub Actions集成

```yaml
- name: Content Analysis
  run: |
    cd tools/content-analysis
    python content_analyzer.py --output-file ../../reports/content-analysis.md
```

## 算法说明

### 可读性算法

1. **Flesch-Kincaid Grade Level**
   ```
   FKGL = 0.39 × (words/sentences) + 11.8 × (syllables/words) - 15.59
   ```

2. **SMOG Index**
   ```
   SMOG = 1.043 × √(complex_words × 30/sentences) + 3.1291
   ```

3. **Coleman-Liau Index**
   ```
   CLI = 0.0588 × L - 0.296 × S - 15.8
   ```
   其中 L = 平均每100字的字符数，S = 平均每100字的句子数

### 关键词提取

1. **文本预处理**: 移除Markdown标记、代码块、链接等
2. **分词**: 按空格和标点分割
3. **过滤**: 移除停用词、数字、短词
4. **统计**: 计算词频
5. **排序**: 按频率降序排列

## 自定义配置

### 修改停用词

```python
# 在content_analyzer.py中修改
STOP_WORDS = {
    '的', '了', '和', '是',  # 添加更多停用词
    # ...
}
```

### 添加新的SEO检查

```python
def custom_seo_check(self, content: str) -> List[str]:
    """自定义SEO检查"""
    issues = []
    # 添加你的检查逻辑
    return issues
```

## 故障排除

### 常见问题

1. **编码错误**
   ```bash
   # 确保文件使用UTF-8编码
   file content/zh/posts/article.md
   ```

2. **分析失败**
   ```bash
   # 检查文件权限
   ls -la content/zh/posts/article.md
   ```

3. **报告生成失败**
   ```bash
   # 确保输出目录存在
   mkdir -p reports
   ```

## 性能优化

- **大目录优化**: 对于大量文件，使用`--analyze-single`逐个分析
- **内存优化**: 工具使用流式处理，避免加载大文件到内存
- **缓存**: 考虑为重复分析添加缓存机制

## 贡献

欢迎提交Issue和Pull Request来改进分析算法和功能！

## 许可证

MIT License
