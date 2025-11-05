# Daily AI Collector V3.0 - 更新日志

## 版本 3.0.0 (2025-11-05)

### 🎯 重大改进：分章节专用数据源策略

本版本实现了全新的**分章节专用数据源策略**，每个报告章节使用专门优化的数据源。

---

## 🆕 新增功能

### 1. 今日焦点专用搜索

- **方法**: `search_focus_news()`
- **数据源**: Google Search
- **特点**: 专注大模型厂商（OpenAI, Gemini, Anthropic, xAI, Meta, Qwen, DeepSeek, GLM, Kimi）
- **优势**: 更精准的新闻筛选，避免无关内容

### 2. 应用与产品专用搜索

- **方法**: `search_applications()`
- **数据源**: NewsAPI, Tavily, Google, Serper, Brave（多源并行）
- **特点**: 专门搜索AI应用和产品发布
- **优势**: 新增专用章节，覆盖更全面

---

## ⚡ 优化改进

### GitHub 搜索优化

- **改进**: 按 star 增长率排序（stars/day）
- **优势**: 发现快速获得关注的新项目
- **新增**: 计算并展示 star 增长速度

### 质量评分扩展

- **新增**: `google_focus` 评分逻辑
- **新增**: `applications` 评分逻辑
- **优化**: 针对不同数据源的专门评分策略

---

## 🔄 数据结构变更

### 新的数据收集结构

```python
collected_data = {
    'focus_news': [],       # 今日焦点（Google Search）
    'hf_models': [],        # 模型与算法（HuggingFace）
    'arxiv_papers': [],     # 学术前沿（arXiv）
    'github_projects': [],  # 工具与框架（GitHub）
    'applications': [],     # 应用与产品（多源）
}
```

### 移除的字段

- `perplexity_news` - 已移除（质量问题）
- `ai_news_lib` - 重构为 `applications`

---

## 📊 章节与数据源映射

| 章节 | 数据源 | 搜索方法 |
|------|--------|---------|
| 📰 今日焦点 | Google Search | `search_focus_news()` |
| 🧠 模型与算法 | HuggingFace | `search_huggingface_models()` |
| 📚 学术前沿 | arXiv | `search_arxiv_papers()` |
| 🛠️ 工具与框架 | GitHub | `search_github_trending()` |
| 📱 应用与产品 | 多源并行 | `search_applications()` |

---

## 📝 文件修改

### 核心文件

- `scripts/daily_ai_collector_v2.py` - 主要逻辑重构
  - 新增 `search_focus_news()` 方法
  - 新增 `search_applications()` 方法
  - 优化 `search_github_trending()` 方法
  - 扩展 `calculate_quality_score()` 方法
  - 重构 `generate_ai_summary()` 方法
  - 重写 `generate_fallback_summary()` 方法
  - 更新 `create_daily_content()` 数据收集流程

### 新增文档

- `docs/daily-ai-v3-implementation.md` - 完整实施报告
- `CHANGELOG-v3.0.md` - 本更新日志

---

## 🎯 预期效果

### 内容质量提升

- ✅ 今日焦点更聚焦大模型厂商
- ✅ 工具与框架展示 star 增长趋势
- ✅ 应用与产品独立章节，信息更丰富
- ✅ 整体内容精准度显著提高

### 性能优化

- ✅ 避免重复搜索
- ✅ 资源使用更高效
- ✅ 更快的执行速度

---

## 🔧 环境要求

### 新增必需 API

- `GOOGLE_SEARCH_API_KEY` - 用于今日焦点搜索
- `GOOGLE_SEARCH_ENGINE_ID` - Google Custom Search Engine ID

### 继续使用的 API

- `HUGGINGFACE_API_KEY` - 模型搜索
- `GITHUB_TOKEN` - GitHub 搜索
- `NEWS_API_KEY` - 应用搜索
- `TAVILY_API_KEY` - 应用搜索
- `SERPER_API_KEY` - 应用搜索
- `BRAVE_SEARCH_API_KEY` - 应用搜索

---

## ⚠️ 破坏性变更

### 数据字段变更

- `perplexity_news` 字段已移除
- `ai_news_lib` 字段已移除
- 新增 `focus_news` 字段
- 新增 `applications` 字段

### 兼容性

- ✅ 其他字段保持兼容
- ✅ API 向后兼容
- ⚠️ 如有自定义脚本依赖旧字段，需要更新

---

## 📚 使用方法

### 运行收集器

```bash
# 确保环境变量已配置
python scripts/daily_ai_collector_v2.py
```

### 测试新功能

```bash
# 测试今日焦点搜索
python -c "from scripts.daily_ai_collector_v2 import DailyAICollectorV2; c = DailyAICollectorV2(); print(len(c.search_focus_news()))"

# 测试应用搜索
python -c "from scripts.daily_ai_collector_v2 import DailyAICollectorV2; c = DailyAICollectorV2(); print(len(c.search_applications()))"
```

---

## 🐛 已知问题

无已知问题。

---

## 📋 待办事项

- [ ] 监控 Google Search API 配额
- [ ] 收集用户反馈
- [ ] 优化 star 增长率算法
- [ ] 考虑添加"行业动态"章节

---

## 🙏 致谢

感谢用户提供的宝贵建议，促成了这次重大改进！

---

**版本**: 3.0.0  
**发布日期**: 2025-11-05  
**状态**: ✅ 稳定版
