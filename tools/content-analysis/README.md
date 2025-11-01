# Hugo Blog Content Analyzer

分析Hugo博客内容质量、SEO优化和可读性，提供详细的优化建议。

## 🚀 新功能：AI智能增强分析

现在支持大模型结合传统分析方式，对整篇文章进行深度内容分析！

## 功能特性

- 🤖 **AI智能分析**: GPT模型深度内容质量评估
- 📊 **可读性分析**: Flesch-Kincaid、SMOG、Coleman-Liau算法评分
- 🔍 **关键词提取**: 自动提取内容关键词和标签
- 🔍 **SEO优化检查**: 标题、描述、URL结构分析
- 📈 **质量评估**: 综合评分系统 (0-100分)
- 🏥 **内容健康度**: 检查元数据完整性、结构问题和优化建议
- 📊 **内容分布分析**: 按分类、标签、阅读时间分析内容分布
- 📈 **增长趋势分析**: 月度内容创建趋势和创作速度分析
- 📝 **详细报告**: Markdown格式的完整分析报告
- 🎯 **单文件分析**: 支持分析单个文件或整个目录

## 安装依赖

本工具使用Python标准库，无需额外依赖。

AI增强分析需要额外安装：

```bash
pip install openai>=1.0.0 python-dotenv>=1.0.0 rich>=13.0.0
```

rich库用于美化JSON输出，提供彩色和结构化的分析结果显示。如果未安装rich，将自动回退到标准JSON格式。

## 🚀 新功能：前端仪表板集成

### JSON数据格式

工具现在支持生成专门的JSON数据文件，供前端仪表板使用：

```json
{
  "generated_at": "2025-11-01T09:29:10.568322",
  "summary": {
    "total_files": 302,
    "analyzed_files": 302,
    "avg_quality_score": 58.0,
    "health_score": 57.2
  },
  "distribution": {
    "by_category": {...},
    "by_tag": {...},
    "by_reading_time": {...}
  },
  "trends": {
    "monthly_creation": {...},
    "content_velocity": [...]
  }
}
```

### Hugo短代码集成

创建了 `{{< content-analysis >}}` 短代码，可以在Hugo文章中嵌入分析信息：

```markdown
<!-- 内容概览 -->
{{< content-analysis type="overview" >}}

<!-- 详细统计 -->
{{< content-analysis type="stats" >}}

<!-- 创作趋势 -->
{{< content-analysis type="trends" >}}

<!-- 热门关键词 -->
{{< content-analysis type="keywords" limit="10" >}}

<!-- 内容分类 -->
{{< content-analysis type="categories" limit="5" >}}
```

### 自动化分析

设置了GitHub Actions工作流，每天自动运行内容分析：

- **定时执行**: 每天早上8点自动分析
- **手动触发**: 支持手动触发AI增强分析
- **结果提交**: 自动提交分析结果到仓库
- **状态报告**: 在Actions中显示分析摘要

## 🤖 AI增强分析设置

要使用AI增强分析功能，可以通过环境变量或`.env`文件配置：

### 方法1：环境变量

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选，自定义API端点
export OPENAI_MODEL="gpt-3.5-turbo"  # 可选，默认模型
```

### 方法2：.env文件（推荐）

在项目根目录创建`.env`文件：

```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

**注意**: `.env`文件已被加入`.gitignore`，不会被提交到版本控制中，确保API密钥安全。

支持的模型选项：

- `gpt-4`: 最准确的模型，但API费用较高
- `gpt-4-turbo-preview`: GPT-4的Turbo版本，速度更快
- `gpt-3.5-turbo` (默认): 性价比最好的选择
- `gpt-3.5-turbo-16k`: 支持更长文本的GPT-3.5版本

对于国内用户，可以配置第三方API服务：

```bash
OPENAI_BASE_URL=https://your-api-proxy.com/v1
OPENAI_API_KEY=your-proxy-api-key
```

AI分析功能包括：

- **内容深度评估**: 分析专业深度和知识价值
- **结构完整性**: 检查文章结构是否合理
- **读者价值**: 评估对读者的实际帮助
- **写作质量**: 分析语言表达和逻辑性
- **创新性**: 识别新颖观点和见解
- **个性化建议**: 基于AI理解的改进建议

## 基本用法

### 1. 基础内容分析

```bash
python content_analyzer.py
```

### 2. 🤖 AI增强内容分析

```bash
python content_analyzer.py --ai-enhance
```

### 3. 生成内容分析报告

```bash
# 基础报告
python content_analyzer.py --output-file my-report.md

# AI增强报告
python content_analyzer.py --ai-enhance --output-file ai-enhanced-report.md
```

### 4. 生成JSON数据（供前端仪表板使用）

```bash
# 生成基础JSON数据
python content_analyzer.py --json-data

# 生成AI增强JSON数据
python content_analyzer.py --json-data --ai-enhance --json-output dashboard-data.json

# Make命令生成JSON数据
make generate-json-data      # 基础JSON数据
make generate-json-data-ai   # AI增强JSON数据
```

### 5. 分析单个文件

```bash
# 基础单文件分析
python content_analyzer.py --analyze-single content/zh/posts/my-article.md

# 🤖 AI增强单文件分析
python content_analyzer.py --analyze-single content/zh/posts/my-article.md --ai-enhance

# 生成单文件分析报告
python content_analyzer.py --analyze-single content/zh/posts/my-article.md --ai-enhance --output-file single-file-report.md
```

### 5. Make命令使用

```bash
# 分析整个目录
make analyze-content
make analyze-content-ai

# 生成JSON数据（前端仪表板）
make generate-json-data      # 基础JSON数据
make generate-json-data-ai   # AI增强JSON数据

# 分析单个文件
make analyze-content FILE=./content/zh/google/a2a.md
make analyze-content-ai FILE=./content/zh/google/a2a.md
```

### 6. 仅执行特定分析

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
