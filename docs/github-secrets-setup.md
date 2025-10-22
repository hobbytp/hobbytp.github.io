# GitHub Secrets 配置指南

本文档说明需要在 GitHub Repository Secrets 中配置的所有 API 密钥，以确保每日AI动态收集脚本能够正常运行。

## 必需的 Secrets

### 核心 AI 服务

- `GEMINI_API_KEY` - Google Gemini API 密钥（用于内容生成）
- `PERPLEXITY_API_KEY` - Perplexity API 密钥（用于AI新闻搜索）

### 数据源 API 密钥

- `GITHUB_TOKEN` - GitHub Personal Access Token（用于搜索开源项目）
- `HUGGINGFACE_API_KEY` - Hugging Face API 密钥（用于搜索新模型）

### ai_news_collector_lib 多源搜索 API 密钥

- `NEWS_API_KEY` - NewsAPI 密钥（新闻API）
- `TAVILY_API_KEY` - Tavily 搜索API密钥
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API 密钥
- `GOOGLE_SEARCH_ENGINE_ID` - Google Custom Search Engine ID
- `SERPER_API_KEY` - Serper 搜索API密钥
- `BRAVE_SEARCH_API_KEY` - Brave Search API密钥
- `METASOSEARCH_API_KEY` - Metasosearch API密钥

## 配置步骤

1. 进入 GitHub 仓库设置页面
2. 导航到 `Settings` > `Secrets and variables` > `Actions`
3. 点击 `New repository secret`
4. 为每个上述密钥创建对应的 Secret

## API 密钥获取指南

### Google Gemini API

- 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
- 创建新的 API 密钥

### Perplexity API

- 访问 [Perplexity API](https://www.perplexity.ai/settings/api)
- 获取 API 密钥

### GitHub Token

- 访问 GitHub Settings > Developer settings > Personal access tokens
- 创建具有 `repo` 权限的 token

### Hugging Face API

- 访问 [Hugging Face Settings](https://huggingface.co/settings/tokens)
- 创建新的 Access Token

### NewsAPI

- 访问 [NewsAPI](https://newsapi.org/register)
- 注册并获取免费 API 密钥

### Tavily

- 访问 [Tavily](https://tavily.com/)
- 注册并获取 API 密钥

### Google Custom Search

- 访问 [Google Custom Search](https://cse.google.com/)
- 创建自定义搜索引擎
- 获取 API 密钥和搜索引擎 ID

### Serper

- 访问 [Serper](https://serper.dev/)
- 注册并获取 API 密钥

### Brave Search

- 访问 [Brave Search API](https://brave.com/search/api/)
- 注册并获取 API 密钥

### Metasosearch

- 访问 [Metasosearch](https://metasosearch.com/)
- 注册并获取 API 密钥

## 注意事项

1. **免费额度限制**: 大多数API都有免费额度限制，请根据使用量选择合适的计划
2. **安全性**: 不要在代码中硬编码API密钥，始终使用环境变量
3. **监控使用量**: 定期检查API使用情况，避免超出限制
4. **备用方案**: 如果某个API不可用，脚本会自动跳过该数据源

## 验证配置

运行以下命令验证环境变量是否正确设置：

```bash
python scripts/daily_ai_collector_v2.py
```

脚本会输出每个API密钥的配置状态，确保所有必需的密钥都已正确设置。
