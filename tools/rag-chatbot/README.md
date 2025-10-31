# Hugo Blog RAG Chatbot

基于Retrieval-Augmented Generation的智能博客问答系统，为Hugo博客提供AI驱动的智能问答功能。

## 功能特性

- 🧠 **智能问答**: 基于博客内容进行语义搜索和智能回答
- 🔍 **向量检索**: 使用Sentence Transformers和FAISS进行高效向量搜索
- 🤖 **AI增强**: 支持OpenAI GPT集成，提供更智能的回答
- 📚 **内容索引**: 自动索引所有博客文章，支持增量更新
- 🌐 **多语言支持**: 支持中文和英文内容理解
- ⚡ **实时更新**: 支持内容更新时的索引增量更新

## 工作原理

### RAG (Retrieval-Augmented Generation) 流程

1. **文档处理**: 解析Hugo Markdown文件，提取纯文本内容
2. **文本分块**: 将长文档分割成语义相关的文本块
3. **向量嵌入**: 使用Sentence Transformers将文本转换为向量
4. **索引构建**: 使用FAISS构建向量索引，支持快速相似度搜索
5. **检索增强**: 用户查询时检索最相关的文档片段
6. **答案生成**: 基于检索结果生成准确、相关的回答

### 系统架构

```
用户查询 → 向量嵌入 → FAISS检索 → 相关文档 → AI生成 → 智能回答
                       ↓
                  博客内容索引
```

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或使用conda
conda install numpy sentence-transformers faiss-cpu beautifulsoup4 markdown
pip install openai
```

## 快速开始

### 1. 构建内容索引

```bash
# 首次构建索引
python rag_engine.py --rebuild-index

# 更新现有索引（增量）
python rag_engine.py --update-index
```

### 2. 测试问答功能

```bash
# 简单查询测试
python rag_engine.py --query "什么是深度学习？"

# 复杂问题
python rag_engine.py --query "如何使用AI进行代码生成？"
```

### 3. 查看索引统计

```bash
python rag_engine.py --stats
```

## 命令行选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--content-dir DIR` | Hugo内容目录 | `content` |
| `--index-dir DIR` | 索引存储目录 | `rag-index` |
| `--rebuild-index` | 完全重建索引 | - |
| `--update-index` | 增量更新索引 | - |
| `--query TEXT` | 执行查询 | - |
| `--serve` | 启动Web服务 | - |
| `--stats` | 显示统计信息 | - |
| `--openai-api-key KEY` | OpenAI API密钥 | 环境变量 |
| `--embedding-model MODEL` | 嵌入模型名称 | `all-MiniLM-L6-v2` |

## 配置说明

### 环境变量

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-api-key-here"
```

### 自定义配置

```python
# 在rag_engine.py中修改配置
self.chunk_size = 1000      # 文本块大小
self.chunk_overlap = 200    # 块重叠大小
self.embedding_model_name = "paraphrase-multilingual-MiniLM-L12-v2"  # 多语言模型
```

## 使用示例

### 基本查询

```bash
# 关于AI的话题
python rag_engine.py --query "AI在软件开发中的应用"

# 具体技术问题
python rag_engine.py --query "如何优化React应用的性能"

# 内容创作建议
python rag_engine.py --query "写技术博客的经验分享"
```

### 索引管理

```bash
# 查看当前索引状态
python rag_engine.py --stats

# 重建索引（添加新内容后）
python rag_engine.py --rebuild-index

# 增量更新（只处理变更内容）
python rag_engine.py --update-index
```

## 输出示例

### 查询结果

```
🔍 查询: 什么是RAG？

🤖 回答:
RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术。它通过首先从知识库中检索相关信息，然后基于这些信息生成回答，从而提供更准确、更有根据的回答。

📚 相关来源:
1. AI技术基础 (相关度: 0.823)
   /zh/ai-basics/
2. 大语言模型进阶 (相关度: 0.756)
   /zh/llm-advanced/
```

### 统计信息

```
📊 RAG索引统计信息:
- 文档块数量: 1247
- 向量维度: 384
- 总词数: 89,432
- 唯一文件数: 234
- 最后更新: 2025-11-01T00:15:30
```

## 集成到Hugo工作流

### Makefile集成

```makefile
# RAG相关目标
rag-build-index:
	@echo "🧠 构建RAG索引..."
	@cd tools/rag-chatbot && $(PYTHON_CMD) rag_engine.py --rebuild-index

rag-update-index:
	@echo "🔄 更新RAG索引..."
	@cd tools/rag-chatbot && $(PYTHON_CMD) rag_engine.py --update-index

rag-query:
	@echo "🤖 RAG查询测试..."
	@cd tools/rag-chatbot && $(PYTHON_CMD) rag_engine.py --query "$(QUERY)"

# 完整构建包含RAG
full-build: build rag-update-index
```

### 使用方法

```bash
# 构建索引
make rag-build-index

# 更新索引
make rag-update-index

# 测试查询
make rag-query QUERY="什么是机器学习？"
```

## 高级功能

### 自定义嵌入模型

```python
# 使用多语言模型
self.embedding_model_name = "paraphrase-multilingual-MiniLM-L12-v2"

# 使用更精确的模型
self.embedding_model_name = "all-mpnet-base-v2"
```

### 文本分块策略

```python
# 调整分块参数
self.chunk_size = 800       # 更小的块
self.chunk_overlap = 150    # 更少的重叠
```

### 检索优化

```python
# 调整检索参数
top_k = 10  # 返回更多候选文档
score_threshold = 0.7  # 设置相似度阈值
```

## 性能优化

- **索引压缩**: FAISS支持多种索引类型，可根据需要选择
- **批量处理**: 支持批量向量编码，提高构建速度
- **内存管理**: 流式处理大文档，避免内存溢出
- **缓存机制**: 智能检测内容变化，只重新索引变更部分

## 故障排除

### 常见问题

1. **索引构建失败**
   ```bash
   # 检查内容目录
   ls content/

   # 检查权限
   chmod +r content/
   ```

2. **查询无结果**
   ```bash
   # 重建索引
   python rag_engine.py --rebuild-index

   # 检查查询关键词
   python rag_engine.py --query "具体的技术术语"
   ```

3. **OpenAI API错误**
   ```bash
   # 检查API密钥
   export OPENAI_API_KEY="sk-..."

   # 检查网络连接
   curl -I https://api.openai.com
   ```

4. **内存不足**
   ```bash
   # 使用更小的模型
   python rag_engine.py --embedding-model "all-MiniLM-L6-v2"

   # 减少批量大小
   # 在代码中调整batch_size参数
   ```

## 技术细节

### 支持的嵌入模型

- **all-MiniLM-L6-v2**: 快速，384维，默认选择
- **all-mpnet-base-v2**: 高精度，768维，更准确但较慢
- **paraphrase-multilingual-MiniLM-L12-v2**: 多语言支持

### 向量索引

- **IndexFlatIP**: 内积索引，精确但内存占用大
- **IndexIVFFlat**: 近似索引，速度更快，内存更少
- **IndexHNSW**: 图索引，最快的近似搜索

### 相似度计算

- 使用余弦相似度 (cosine similarity)
- 支持多种距离度量：L2、IP (内积)
- 可配置相似度阈值过滤结果

## 未来扩展

- **多模态支持**: 支持图片、代码片段的检索
- **实时索引**: 自动检测内容变化并更新索引
- **对话历史**: 维护对话上下文提供更连贯的回答
- **多租户**: 支持多个博客的独立索引
- **API接口**: 提供RESTful API供第三方集成

## 许可证

MIT License


