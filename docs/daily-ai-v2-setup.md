# 每日AI收集器 V2 - 环境配置指南

## 📋 概述

每日AI收集器 V2 是一个自动化的AI新闻聚合系统，集成了多个数据源和AI服务。

## 🔑 必需的 API Keys

### 1. GEMINI_API_KEY (必需)
用于AI内容生成和摘要。

**获取方式**:
- 访问: https://makersuite.google.com/app/apikey
- 创建 API key
- 免费额度: 每分钟 15 次请求

**设置方式**:
```bash
# 本地环境
export GEMINI_API_KEY="your_api_key_here"

# GitHub Secrets
# Repository Settings -> Secrets and variables -> Actions
# Name: GEMINI_API_KEY
# Value: your_api_key_here
```

### 2. PERPLEXITY_API_KEY (推荐)
用于实时AI新闻搜索和趋势分析。

**获取方式**:
- 访问: https://www.perplexity.ai/account/api
- 创建 API key
- 定价: $5/月 (足够日常使用)

**配额管理**:
- 每月 $5 约可进行 1000-2000 次搜索
- 每日运行 1 次，每次 3 个查询 = 90 次/月
- 预计用量: < $1/月

**设置方式**:
```bash
export PERPLEXITY_API_KEY="your_api_key_here"
```

### 3. GITHUB_TOKEN (推荐)
用于搜索 GitHub 热门 AI 项目。

**获取方式**:
- Settings -> Developer settings -> Personal access tokens
- Generate new token (classic)
- 权限: `public_repo` (读取公开仓库)

**设置方式**:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

### 4. HUGGINGFACE_API_KEY (可选)
用于搜索 Hugging Face 新模型。

**获取方式**:
- 访问: https://huggingface.co/settings/tokens
- Create new token
- Type: Read

**设置方式**:
```bash
export HUGGINGFACE_API_KEY="hf_xxxxxxxxxxxxx"
```

## 📦 依赖安装

### Python 环境要求
- Python 3.8+

### 安装依赖
```bash
cd scripts/
pip install -r requirements.txt
```

### 依赖列表
```
google-generativeai>=0.3.0  # Google Gemini SDK
openai>=1.0.0               # OpenAI SDK (fallback)
perplexityai>=0.1.0         # Perplexity SDK
PyYAML>=6.0
requests>=2.28.0
python-dateutil>=2.8.0
Pillow>=9.0.0
```

## 🚀 本地测试

### 1. 设置环境变量
创建 `.env` 文件:
```bash
# .env
GEMINI_API_KEY=your_gemini_key
PERPLEXITY_API_KEY=your_perplexity_key
GITHUB_TOKEN=your_github_token
HUGGINGFACE_API_KEY=your_hf_token
```

加载环境变量:
```bash
# Linux/Mac
source .env
export $(cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object { $var = $_.Split('='); [System.Environment]::SetEnvironmentVariable($var[0], $var[1]) }
```

### 2. 运行测试
```bash
# 测试 V2 版本
python scripts/daily_ai_collector_v2.py

# 查看生成的内容
ls content/zh/daily_ai/
cat content/zh/daily_ai/$(date +%Y-%m-%d).md
```

### 3. 诊断工具
```bash
# 运行诊断脚本
python scripts/diagnose_gemini.py
```

## ⚙️ GitHub Actions 配置

### 1. 添加 Secrets

在 GitHub 仓库中:
1. Settings -> Secrets and variables -> Actions
2. 添加以下 secrets:
   - `GEMINI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `GITHUB_TOKEN` (通常已自动提供)
   - `HUGGINGFACE_API_KEY`

### 2. 更新 Workflow 文件

编辑 `.github/workflows/daily-ai-update.yml`:

```yaml
name: Daily AI Update V2

on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 00:00 (北京时间 08:00)
  workflow_dispatch:  # 支持手动触发

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd scripts
          pip install -r requirements.txt
      
      - name: Run diagnostic
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
        run: |
          python scripts/diagnose_gemini.py || true
      
      - name: Collect daily AI news V2
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          HUGGINGFACE_API_KEY: ${{ secrets.HUGGINGFACE_API_KEY }}
        run: |
          python scripts/daily_ai_collector_v2.py
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add content/zh/daily_ai/
          git diff --staged --quiet || git commit -m "chore: update daily AI news [automated]"
          git push
```

## 🔄 从 V1 迁移到 V2

### 主要改进

1. **时间窗口缩短**: 7天 -> 48小时
2. **新增 Perplexity**: 实时新闻搜索
3. **智能去重**: 避免重复报道
4. **质量评分**: 自动排序高质量内容
5. **新分类体系**: 6个分类（原10个）
6. **改进格式**: 热度标识、评分、快速导航

### 迁移步骤

1. **安装新依赖**:
   ```bash
   pip install perplexityai
   ```

2. **添加新的 API key**:
   ```bash
   export PERPLEXITY_API_KEY="your_key"
   ```

3. **更新脚本引用**:
   ```bash
   # 从
   python scripts/daily_ai_collector.py
   
   # 改为
   python scripts/daily_ai_collector_v2.py
   ```

4. **测试运行**:
   ```bash
   python scripts/daily_ai_collector_v2.py
   ```

5. **检查输出**:
   - 查看新的分类体系
   - 确认 Perplexity 数据获取成功
   - 验证去重功能

## 📊 使用统计

### API 调用频率（每日）

| API | 调用次数 | 月度配额 | 预计费用 |
|-----|---------|---------|---------|
| Gemini | 1-2 | 免费 | $0 |
| Perplexity | 3-5 | $5/月 | < $0.5 |
| GitHub | 5-10 | 5000次/小时 | $0 |
| Hugging Face | 1-2 | 无限 | $0 |
| ArXiv | 1-2 | 无限 | $0 |

**总计**: < $0.5/月

### 数据量统计（每日）

- GitHub 项目: 5-10 个
- Hugging Face 模型: 0-5 个
- ArXiv 论文: 3-10 篇
- Perplexity 新闻: 3-10 条

**总计**: 15-30 条动态/天

## 🐛 故障排查

### 问题 1: Perplexity SDK 导入失败

**症状**:
```
⚠️ perplexity 库导入失败
```

**解决方案**:
```bash
pip install perplexityai
```

### 问题 2: Perplexity API 返回空结果

**可能原因**:
- API key 未设置
- 配额用完
- 查询语法错误

**解决方案**:
1. 检查 API key: `echo $PERPLEXITY_API_KEY`
2. 登录 Perplexity 查看配额
3. 查看错误日志

### 问题 3: 数据去重过度

**症状**:
每日收集的内容很少或为空。

**原因**:
历史数据中已包含类似内容。

**解决方案**:
调整 `load_history_items` 的 `days_back` 参数:
```python
# 从 7 天减少到 3 天
self.seen_urls = self.load_history_items(days_back=3)
```

### 问题 4: AI 摘要质量差

**原因**:
- 收集的数据不足
- Gemini API 返回了简短内容

**解决方案**:
1. 确保至少有 5 条以上数据
2. 检查 `max_tokens` 设置（建议 3000+）
3. 调整 prompt 更加具体

## 📞 支持

如有问题，请：
1. 查看日志输出
2. 运行诊断脚本: `python scripts/diagnose_gemini.py`
3. 提交 Issue: https://github.com/hobbytp/hobbytp.github.io/issues

## 📝 更新日志

### V2.0 (2025-01-15)
- ✨ 新增 Perplexity API 集成
- ⚡ 缩短时间窗口至 48 小时
- 🎯 实现智能去重
- 📊 添加内容质量评分
- 🔄 重构分类体系（6个分类）
- 💎 改进展现格式
- 📈 优化数据源权重

### V1.0 (2024-10-01)
- 初始版本
- 支持 GitHub、Hugging Face、ArXiv
- 基础 Gemini 摘要生成
