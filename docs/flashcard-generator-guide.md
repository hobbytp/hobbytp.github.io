# 闪卡生成器使用文档

闪卡生成器是一个 Python 脚本工具，可以为 Hugo 博客文章自动添加类似 NotebookLM 的知识回顾闪卡功能。支持从 CSV 文件导入或使用 AI 自动生成问答对。

## 功能特性

- ✅ **AI 自动生成** - 支持 Gemini、OpenRouter、OpenAI 兼容 API
- ✅ **CSV 导入** - 从 CSV 文件批量导入问答对
- ✅ **自动插入** - 将闪卡代码自动插入博客文章末尾
- ✅ **智能替换** - 如果文章已有闪卡，会自动替换
- ✅ **特殊字符处理** - 自动转义引号等可能导致 Hugo 解析错误的字符

## 安装依赖

```bash
# 基础依赖（CSV 模式无需额外依赖）
pip install requests

# Gemini API（推荐）
pip install google-genai
```

## 环境变量配置

根据您选择的 AI 提供商设置对应的环境变量：

```bash
# Gemini (默认提供商，推荐使用)
export GEMINI_API_KEY="your-gemini-api-key"

# OpenRouter (统一 API，支持 300+ 模型)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# OpenAI 兼容 API (如 Ollama, vLLM, LocalAI 等)
export OPENAI_API_KEY="your-api-key"  # 本地服务可不设置
```

### 获取 API Key

- **Gemini**: https://aistudio.google.com/apikey
- **OpenRouter**: https://openrouter.ai/keys
- **OpenAI**: https://platform.openai.com/api-keys

## 使用方法

### 方式一：AI 自动生成（推荐）

脚本会读取博客文章内容，调用 AI 生成问答对，并自动插入到文章末尾。

#### 基础用法

```bash
# 使用 Gemini（默认）
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate

# 指定生成数量（默认 15 个）
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate --count 20
```

#### 使用 OpenRouter

```bash
# 使用默认模型 (google/gemini-2.0-flash-001)
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --provider openrouter

# 使用 Claude 3.5 Sonnet
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --provider openrouter \
    --model anthropic/claude-3.5-sonnet

# 使用 GPT-4o
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --provider openrouter \
    --model openai/gpt-4o
```

#### 使用本地模型（Ollama）

```bash
# 使用 Ollama 本地模型
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --provider openai \
    --base-url http://localhost:11434 \
    --model llama3.1

# 使用 vLLM 或其他 OpenAI 兼容服务
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --provider openai \
    --base-url http://your-server:8000/v1 \
    --model your-model-name
```

#### 保存生成的问答对

```bash
# 生成闪卡的同时保存到 CSV 文件（方便备份或复用）
python scripts/add_flashcards.py content/zh/posts/my-article.md --generate \
    --output flashcards_backup.csv
```

### 方式二：从 CSV 文件导入

如果您已经有准备好的问答对，可以直接从 CSV 文件导入。

#### CSV 文件格式

```csv
Question,Answer
什么是强化学习？,强化学习是一种通过与环境交互来学习最优策略的机器学习方法。
GRPO 算法的优势是什么？,GRPO 不需要 Critic 模型，通过组内相对比较计算优势函数。
```

**格式要求：**
- 第一列：问题
- 第二列：答案
- 支持带或不带表头
- 使用 UTF-8 编码

#### 导入命令

```bash
python scripts/add_flashcards.py content/zh/posts/my-article.md my_flashcards.csv
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `blog_path` | - | 博客文件路径（必填） | - |
| `csv_path` | - | CSV 文件路径（与 --generate 互斥） | - |
| `--generate` | `-g` | 使用 AI 自动生成闪卡 | False |
| `--provider` | `-p` | AI 提供商: gemini/openrouter/openai | gemini |
| `--model` | `-m` | 模型名称 | 根据 provider 自动选择 |
| `--base-url` | - | OpenAI 兼容 API 的基础 URL | https://api.openai.com |
| `--count` | `-c` | 生成的闪卡数量 | 15 |
| `--output` | `-o` | 保存生成的 Q&A 到 CSV 文件 | - |

## 支持的 AI 提供商

| Provider | 环境变量 | 默认模型 | 说明 |
|----------|---------|---------|------|
| `gemini` | `GEMINI_API_KEY` | `gemini-2.0-flash` | Google Gemini，速度快，免费额度大 |
| `openrouter` | `OPENROUTER_API_KEY` | `google/gemini-2.0-flash-001` | 统一 API，支持 300+ 模型 |
| `openai` | `OPENAI_API_KEY` | `gpt-4o-mini` | OpenAI 兼容 API |

## 推荐模型

### OpenRouter 模型推荐

| 用途 | 模型 ID | 说明 |
|------|---------|------|
| 性价比首选 | `google/gemini-2.0-flash-001` | 快速便宜，质量不错 |
| 高质量输出 | `anthropic/claude-3.5-sonnet` | 输出质量最好 |
| 最强性能 | `openai/gpt-4o` | 最强但价格较高 |
| 开源模型 | `meta-llama/llama-3.1-70b-instruct` | 开源大模型 |
| 中文优化 | `deepseek/deepseek-chat` | DeepSeek 模型，中文表现好 |

### 本地模型推荐（Ollama）

```bash
# 安装 Ollama 后拉取模型
ollama pull llama3.1
ollama pull qwen2.5:14b
ollama pull deepseek-coder-v2
```

## 闪卡 Shortcode 语法

如果您想手动编写闪卡，可以在文章末尾使用以下格式：

```markdown
---

{{< flashcards >}}

{{< flashcard q="问题内容" >}}
答案内容，支持 **Markdown** 语法和 $数学公式$
{{< /flashcard >}}

{{< flashcard q="另一个问题" >}}
另一个答案
{{< /flashcard >}}

{{< /flashcards >}}
```

### 注意事项

1. **问题中避免使用英文双引号** `"` - 会导致 Hugo 解析错误
2. **如需引用，使用中文书名号** `『』` 或单引号 `'`
3. **答案支持完整 Markdown 语法**，包括代码块、公式等

## 闪卡前端功能

生成的闪卡在博客页面上具有以下交互功能：

- 📚 **折叠展开** - 默认折叠，点击标题展开
- 🔄 **卡片翻转** - 点击卡片查看答案
- ⬅️➡️ **导航切换** - 按钮或键盘方向键切换卡片
- 🔀 **随机顺序** - 打乱卡片顺序，增强复习效果
- 📊 **进度显示** - 实时显示当前卡片编号
- ⌨️ **键盘支持** - Space 翻转，← → 切换
- 📱 **响应式设计** - 移动端友好

## 故障排除

### 常见错误

1. **`请设置 GEMINI_API_KEY 环境变量`**
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

2. **`请安装 google-genai 库`**
   ```bash
   pip install google-genai
   ```

3. **`API 请求失败 (401)`**
   - 检查 API Key 是否正确
   - 检查 API Key 是否过期

4. **`JSON 解析失败`**
   - 尝试使用不同的模型
   - 减少生成数量 `--count 10`

5. **Hugo 构建报错 `Cannot mix named and positional parameters`**
   - 问题中包含了未转义的引号
   - 手动将 `"..."` 替换为 `『...』`

## 示例

### 完整工作流程

```bash
# 1. 设置环境变量
export GEMINI_API_KEY="your-api-key"

# 2. 为文章生成闪卡
python scripts/add_flashcards.py \
    content/zh/deepseek/deepseekmath_v2.md \
    --generate \
    --count 20

# 3. 启动 Hugo 预览
make dev

# 4. 访问 http://localhost:1313 查看效果
```

### 批量处理多篇文章

```bash
# 使用 shell 循环
for file in content/zh/posts/*.md; do
    echo "Processing: $file"
    python scripts/add_flashcards.py "$file" --generate --count 10
done
```

## 相关文件

- `scripts/add_flashcards.py` - 闪卡生成脚本
- `scripts/flashcards_template.csv` - CSV 模板文件
- `layouts/shortcodes/flashcards.html` - 闪卡容器组件
- `layouts/shortcodes/flashcard.html` - 单张闪卡组件

## 更新日志

- **2025-11-29**: 初始版本
  - 支持 Gemini、OpenRouter、OpenAI 兼容 API
  - 支持 CSV 文件导入
  - 自动转义特殊字符
