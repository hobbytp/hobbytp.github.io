# 数据摄取脚本运行策略

## 📋 概述

本文档说明 `scripts/ingest.py` 的运行时机、重复运行的安全性，以及自动化方案。

## ✅ 重复运行的安全性

### 幂等性保证

脚本已实现**幂等性**，可以安全地重复运行：

1. **确定性 ID 生成**
   - 使用 `md5(full_url + chunk_index)` 生成向量 ID
   - 相同文章和相同 chunk 位置总是生成相同的 ID
   - 即使文章内容未变，ID 也不会改变

2. **Vectorize Upsert 操作**
   - 使用 `upsert` API，相同 ID 的记录会被**自动覆盖**
   - 不会产生重复数据
   - 如果文章内容未变，重新运行不会产生新数据

3. **实际效果**
   ```bash
   # 第一次运行：上传所有数据
   uv run python scripts/ingest.py
   # 输出：上传了 1000 个向量
   
   # 立即再次运行（内容未变）：只更新元数据，不产生新数据
   uv run python scripts/ingest.py
   # 输出：上传了 1000 个向量（覆盖现有数据）
   
   # 修改一篇文章后运行：只更新该文章的向量
   # 其他文章的向量保持不变
   ```

### 何时需要运行

| 场景 | 是否需要运行 | 说明 |
|------|------------|------|
| 新写博客文章 | ✅ 需要 | 新文章需要向量化 |
| 修改已有文章 | ✅ 需要 | 修改后的内容需要重新向量化 |
| 删除文章 | ⚠️ 可选 | Vectorize 不会自动删除，需要手动清理 |
| 修改 frontmatter | ⚠️ 可选 | 如果只改标题/日期，不影响内容向量 |
| 定期全量更新 | ✅ 推荐 | 确保所有数据都是最新的 |

## 🚀 运行方式

### 方式 1: 手动运行（当前）

```bash
# 处理所有文件
uv run python scripts/ingest.py

# 处理单个文件（测试用）
uv run python scripts/ingest.py --file content/posts/new-article.md

# 处理特定目录
uv run python scripts/ingest.py --content-dir content/zh
```

### 方式 2: 使用 Makefile（推荐）

已添加到 Makefile，可以使用：

```bash
# 处理所有文件
make ingest-data

# 处理单个文件
make ingest-data FILE=content/posts/new-article.md
```

### 方式 3: Git Hook（自动化）

可以添加到 Git pre-commit hook，自动处理修改的文件：

```bash
# 安装 Git hooks（如果还没有）
bash scripts/setup_git_hooks.sh

# 然后每次提交包含 .md 文件时，会自动运行摄取脚本
```

### 方式 4: GitHub Actions（CI/CD）

可以添加到 GitHub Actions workflow，在推送时自动运行。

## 📝 自动化方案

### 方案 A: 添加到 Makefile（最简单）

已在 Makefile 中添加 `ingest-data` 命令：

```makefile
# 数据摄取
ingest-data:
	@echo "📚 开始数据摄取..."
	uv run python scripts/ingest.py $(if $(FILE),--file $(FILE),)
```

使用方式：
```bash
make ingest-data                    # 处理所有文件
make ingest-data FILE=content/posts/new-article.md  # 处理单个文件
```

### 方案 B: Git Hook（自动处理修改的文件）

创建增量更新脚本，只处理修改的文件：

```bash
# 创建 scripts/ingest-changed.sh
# 在 Git pre-commit hook 中调用
```

**优点**：
- 自动检测修改的文件
- 只处理需要更新的内容
- 节省时间和 API 调用

**缺点**：
- 需要配置 Git hooks
- 可能增加提交时间

### 方案 C: GitHub Actions（CI/CD 集成）

在 GitHub Actions workflow 中添加步骤：

```yaml
- name: Ingest blog content to Vectorize
  env:
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
  run: |
    pip install -r requirements.txt
    python scripts/ingest.py
```

**优点**：
- 完全自动化
- 在云端运行，不占用本地资源
- 可以设置定时任务

**缺点**：
- 需要配置 GitHub Secrets
- 每次推送都会运行（可能不必要）

### 方案 D: 增量更新脚本（推荐用于频繁更新）

创建一个智能脚本，只处理：
- 新文件
- 修改过的文件（基于 Git 历史）

## 🎯 推荐工作流

### 日常写作流程

1. **写新文章或修改文章**
   ```bash
   # 编辑 content/posts/my-article.md
   ```

2. **提交前运行摄取脚本**
   ```bash
   # 方式 1: 手动运行
   uv run python scripts/ingest.py
   
   # 方式 2: 使用 Makefile
   make ingest-data
   
   # 方式 3: 只处理修改的文件（如果实现了增量脚本）
   uv run python scripts/ingest-incremental.py
   ```

3. **提交代码**
   ```bash
   git add content/posts/my-article.md
   git commit -m "Add new article"
   git push
   ```

### 批量更新流程

如果需要批量更新所有内容：

```bash
# 全量更新
uv run python scripts/ingest.py

# 或使用 Makefile
make ingest-data
```

### 定期维护

建议每月运行一次全量更新，确保所有数据都是最新的：

```bash
# 可以添加到 cron 或 GitHub Actions 定时任务
uv run python scripts/ingest.py
```

## ⚠️ 注意事项

### 1. API 速率限制

- Cloudflare Workers AI 有速率限制
- 大量文件可能需要分批处理
- 脚本已实现批量处理，但仍需注意

### 2. 成本考虑

- Workers AI 和 Vectorize 都有使用限制
- 免费套餐有配额限制
- 重复运行会消耗配额（但不会产生重复数据）

### 3. 删除文章

- Vectorize 不会自动删除已删除文章的向量
- 需要手动清理或定期全量更新

### 4. 网络和代理

- 如果使用代理，确保代理设置正确
- 大量文件上传可能需要较长时间

## 🔧 故障处理

### 如果脚本中断

脚本支持断点续传（通过幂等性）：
- 重新运行脚本
- 已上传的向量会被覆盖（不会重复）
- 未上传的向量会被上传

### 如果上传失败

1. 检查错误信息
2. 确认 API Token 有效
3. 检查网络连接
4. 重新运行脚本

### 验证上传结果

```bash
# 使用测试脚本验证
uv run python scripts/test_cloudflare_auth.py

# 或使用 Wrangler 查看索引
npx wrangler vectorize list
```

## 📊 性能优化建议

1. **批量处理**：脚本已实现批量生成 embeddings
2. **增量更新**：只处理修改的文件（如果实现了增量脚本）
3. **并行处理**：可以修改脚本支持并行（注意 API 限制）
4. **缓存机制**：可以添加文件修改时间检查，跳过未修改的文件

## 🎓 最佳实践

1. **新文章**：写完后立即运行摄取脚本
2. **修改文章**：修改后运行摄取脚本
3. **定期维护**：每月运行一次全量更新
4. **使用 Makefile**：使用 `make ingest-data` 而不是直接运行 Python 脚本
5. **验证结果**：重要更新后验证上传结果

## 📚 相关文档

- [设置指南](rag-chatbot-setup.md)
- [故障排除](cloudflare-auth-troubleshooting.md)
- [PRD 文档](PRD/PRD-基于RAG的博客数字分身助手-v1.1.md)





