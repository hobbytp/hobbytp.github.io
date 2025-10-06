# 每日AI动态功能设置指南

## 功能概述

每日AI动态功能通过GitHub Action自动收集和发布AI领域的最新动态，包括：

- 🤖 **新模型发布** - 大模型、小模型、专业模型
- 🛠️ **新框架工具** - 开发框架、工具库、平台  
- 📱 **新应用产品** - 商业产品、开源应用
- 📋 **新标准规范** - 行业标准、技术规范
- 🔬 **新开源项目** - GitHub热门项目
- 📄 **新论文发布** - 重要学术论文
- 🎤 **科技访谈** - 技术领袖访谈、播客
- 📊 **技术报告** - 行业报告、白皮书
- 🏛️ **论坛会议** - 技术会议、研讨会
- 📈 **行业趋势** - 市场动态、投资消息

## 设置步骤

### 1. 配置GitHub Secrets

在GitHub仓库的Settings > Secrets and variables > Actions中添加以下secrets：

#### 必需配置

- `OPENAI_API_KEY`: OpenAI API密钥，用于AI内容生成
- `GITHUB_TOKEN`: GitHub Personal Access Token，用于搜索GitHub项目

#### 可选配置

- `HUGGINGFACE_API_KEY`: Hugging Face API密钥，用于搜索新模型

### 2. 获取API密钥

#### OpenAI API密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 登录并进入API Keys页面
3. 创建新的API密钥
4. 复制密钥并添加到GitHub Secrets

#### GitHub Personal Access Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 生成新的token，选择以下权限：
   - `repo` (完整仓库访问)
   - `public_repo` (公开仓库访问)
3. 复制token并添加到GitHub Secrets

#### Hugging Face API密钥 (可选)

1. 访问 [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens)
2. 创建新的token
3. 复制token并添加到GitHub Secrets

### 3. 测试功能

在本地测试收集器功能：

```bash
# 设置环境变量
export OPENAI_API_KEY="your_openai_api_key"
export GITHUB_TOKEN="your_github_token"
export HUGGINGFACE_API_KEY="your_hf_token"  # 可选

# 运行测试
python scripts/test_daily_ai.py
```

### 4. 手动触发

GitHub Action支持手动触发：

1. 进入GitHub仓库的Actions页面
2. 选择"每日AI动态更新"工作流
3. 点击"Run workflow"按钮
4. 选择分支并点击"Run workflow"

## 工作流程

### 自动运行时间

- **触发时间**: 每天北京时间早上8点 (UTC 00:00)
- **时间范围**: 收集前一天早上8点到当天早上8点的动态

### 数据源

1. **GitHub**: 搜索过去24小时创建的AI相关项目
2. **Hugging Face**: 搜索新发布的模型
3. **ArXiv**: 搜索最新提交的AI论文
4. **AI生成**: 使用GPT-4生成结构化摘要

### 内容生成

1. 收集各数据源的信息
2. 使用AI生成结构化的每日动态报告
3. 自动创建Markdown文件并提交到仓库
4. 更新博客内容

## 文件结构

```
content/zh/daily_ai/
├── _index.md              # 每日AI首页
├── 2025-01-01.md         # 每日动态文件
├── 2025-01-02.md
└── ...

scripts/
├── daily_ai_collector.py  # 主要收集脚本
├── test_daily_ai.py      # 测试脚本
└── daily_ai_template.md  # 内容模板

.github/workflows/
└── daily-ai-update.yml   # GitHub Action工作流
```

## 自定义配置

### 修改收集时间

编辑 `.github/workflows/daily-ai-update.yml` 中的cron表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天UTC 00:00 (北京时间8点)
```

### 添加新的数据源

编辑 `scripts/daily_ai_collector.py`，添加新的搜索方法：

```python
def search_new_source(self) -> List[Dict]:
    """搜索新的数据源"""
    # 实现搜索逻辑
    pass
```

### 修改内容格式

编辑 `scripts/daily_ai_template.md` 来调整内容模板。

## 故障排除

### 常见问题

1. **GitHub Action失败**
   - 检查Secrets是否正确设置
   - 查看Action日志中的错误信息
   - 确保API密钥有效且有足够权限

2. **内容生成失败**
   - 检查OpenAI API密钥是否有效
   - 确认API配额是否充足
   - 查看错误日志

3. **数据收集为空**
   - 检查网络连接
   - 确认API密钥权限
   - 查看各数据源的API状态

### 调试方法

1. **本地测试**

   ```bash
   python scripts/test_daily_ai.py
   ```

2. **查看GitHub Action日志**
   - 进入Actions页面
   - 点击失败的workflow
   - 查看详细日志

3. **手动运行脚本**

   ```bash
   python scripts/daily_ai_collector.py
   ```

## 贡献

欢迎提交Issue和Pull Request来改进这个功能！

- 报告bug: 创建Issue描述问题
- 提出新功能: 创建Issue描述需求
- 提交代码: Fork仓库并创建Pull Request
