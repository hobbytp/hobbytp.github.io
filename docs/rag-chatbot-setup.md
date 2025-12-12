# RAG 博客数字分身助手 - 设置指南

## 📋 概述

本指南将帮助您设置和运行基于 Cloudflare Workers AI 和 Vectorize 的 RAG 聊天助手。

## 🔑 环境变量配置

### 必需的环境变量

> **重要**: Cloudflare 已弃用 `CF_` 前缀的环境变量，请使用 `CLOUDFLARE_` 前缀。  
> 参考文档: https://developers.cloudflare.com/workers/wrangler/system-environment-variables/

1. **CLOUDFLARE_ACCOUNT_ID** - Cloudflare 账户ID
   - 获取方式：登录 Cloudflare Dashboard，在右侧栏可以看到 Account ID
   - 或在 URL 中查看：`https://dash.cloudflare.com/{ACCOUNT_ID}/...`

2. **CLOUDFLARE_API_TOKEN** - Cloudflare API Token
   - 获取方式：
     1. 访问 https://dash.cloudflare.com/profile/api-tokens
     2. 点击 "Create Token"
     3. 使用 "Edit Cloudflare Workers" 模板，或自定义权限：
        - Account: Cloudflare Workers AI:Edit
        - Account: Vectorize:Edit
     4. 复制生成的 Token

3. **CLOUDFLARE_VECTORIZE_INDEX_NAME** (可选) - Vectorize 索引名称
   - 默认值：`blog-index`
   - 如果使用其他名称，请设置此变量

### 设置方法

#### Windows (Git Bash)
```bash
export CLOUDFLARE_ACCOUNT_ID="your_account_id_here"
export CLOUDFLARE_API_TOKEN="your_api_token_here"
export CLOUDFLARE_VECTORIZE_INDEX_NAME="blog-index"  # 可选
```

#### Windows (PowerShell)
```powershell
$env:CLOUDFLARE_ACCOUNT_ID="your_account_id_here"
$env:CLOUDFLARE_API_TOKEN="your_api_token_here"
$env:CLOUDFLARE_VECTORIZE_INDEX_NAME="blog-index"  # 可选
```

#### 使用 .env 文件（推荐）
在项目根目录创建 `.env` 文件：
```
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_VECTORIZE_INDEX_NAME=blog-index
```

## 📦 安装依赖

### Python 依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或使用 uv（推荐）
uv pip install -r requirements.txt
```

### Node.js 依赖（用于 Cloudflare Pages Functions）

无需额外依赖，Cloudflare Pages Functions 使用原生 JavaScript。

## 🚀 使用步骤

### 步骤 1: 创建 Vectorize 索引

在 Cloudflare Dashboard 中创建 Vectorize 索引：

1. 访问 https://dash.cloudflare.com
2. 选择您的账户
3. 进入 "Workers & Pages" -> "Vectorize"
4. 点击 "Create Index"
5. 配置：
   - **Index Name**: `blog-index` (或您自定义的名称)
   - **Dimensions**: `768` (bge-base-en-v1.5 模型的向量维度)
   - **Metric**: `cosine` (推荐) 或 `euclidean`
6. 点击 "Create"

### 步骤 2: 数据摄取（自动化）

推荐使用 GitHub Actions 自动处理。每次推送到 main 分支时，如果内容有更新，系统会自动更新向量数据库。

您也可以手动运行脚本：

```bash
# 处理所有 Markdown 文件（增量更新）
python scripts/ingest.py

# 强制重新处理所有文件
python scripts/ingest.py --force
```

**注意**：脚本会在本地生成 `.ingest_state.json` 文件，用于记录已处理文件的状态。建议将此文件提交到 Git，以实现多人协作和 CI/CD 状态同步。

### 步骤 3: 配置 Cloudflare Pages

#### 3.1 创建 wrangler.toml（可选，用于本地开发）

在项目根目录创建 `wrangler.toml`：

```toml
name = "blog-digital-twin"
pages_build_output_dir = "public"
compatibility_date = "2024-04-01"

[[vectorize]]
binding = "VECTOR_INDEX"
index_name = "blog-index"

[ai]
binding = "AI"
```

#### 3.2 在 Cloudflare Pages 中配置 Bindings

1. 访问您的 Cloudflare Pages 项目
2. 进入 "Settings" -> "Functions"
3. 配置以下 Bindings：

   **AI Binding:**
   - Binding name: `AI`
   - Type: Workers AI

   **Vectorize Binding:**
   - Binding name: `VECTOR_INDEX`
   - Type: Vectorize
   - Index: `blog-index` (或您创建的索引名称)

#### 3.3 部署

```bash
# 使用 Wrangler CLI 部署（需要先安装）
npm install -g wrangler
wrangler pages deploy public

# 或通过 GitHub 自动部署（推荐）
# 推送代码到 GitHub，Cloudflare Pages 会自动构建和部署
```

### 步骤 4: 测试 API

部署后，测试聊天 API：

```bash
curl -X POST https://your-site.pages.dev/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你对 Kubernetes 怎么看？",
    "history": []
  }'
```

预期响应：
```json
{
  "response": "根据我的博客文章，Kubernetes 是一个...",
  "references": [
    {
      "title": "K8s 学习笔记",
      "url": "/zh/posts/k8s-article/"
    }
  ]
}
```

## 🔧 故障排除

### 问题 1: "无法解析embedding响应格式"

**原因**: Cloudflare Workers AI API 响应格式可能因模型而异。

**解决**: 检查 `scripts/ingest.py` 中的 `generate_embeddings` 方法，根据实际响应格式调整解析逻辑。

### 问题 2: "上传到Vectorize失败"

**原因**: 
- API Token 权限不足
- 索引名称不匹配
- 向量维度不匹配

**解决**:
1. 确认 API Token 有 Vectorize:Edit 权限
2. 检查索引名称是否正确
3. 确认向量维度为 768（bge-base-en-v1.5）

### 问题 3: "生成查询向量失败"

**原因**: Workers AI Binding 未正确配置。

**解决**: 在 Cloudflare Pages 设置中确认 AI Binding 已正确配置。

### 问题 4: 幂等性问题

**原因**: 如果重新运行摄取脚本，可能会产生重复数据。

**解决**: 脚本已实现幂等性：
- 使用确定性ID生成（md5(url + chunk_index)）
- Vectorize 的 upsert 操作会自动覆盖相同ID的记录
- 如果文章内容未变，重新运行不会产生重复

## 📊 性能优化建议

1. **批量处理**: 脚本已支持批量生成 embeddings，减少 API 调用次数
2. **增量更新**: 可以修改脚本，只处理修改过的文件（基于文件修改时间）
3. **并行处理**: 对于大量文件，可以考虑并行处理（注意 API 速率限制）

## 🔗 相关文档

- [Cloudflare Workers AI 文档](https://developers.cloudflare.com/workers-ai/)
- [Cloudflare Vectorize 文档](https://developers.cloudflare.com/vectorize/)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/platform/functions/)

## 📝 下一步

完成数据摄取和 API 部署后，可以继续开发：
- Module C: 前端 UI 组件 (`layouts/partials/chatbox.html`)
- 样式文件 (`assets/css/chat.css`)

详见 PRD 文档：`docs/PRD/PRD-基于RAG的博客数字分身助手-v1.1.md`


