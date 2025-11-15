# 🎯 目录级AI封面生成器使用指南

这个工具允许你为指定目录下的博客文章批量生成AI封面图片，使用ModelScope Qwen-image API。

## 🚀 快速开始

### 1. 环境配置

首先确保你配置了必要的API密钥：

```bash
# 在项目根目录的 .env 文件中添加
MODELSCOPE_API_KEY="your-modelscope-api-key"
# 或者使用OpenAI
OPENAI_API_KEY="your-openai-api-key"
TEXT2IMAGE_PROVIDER="modelscope"  # 或 "openai"
```

### 2. 基本使用

#### 查看所有可用目录

```bash
# 使用脚本查看
python scripts/generate_covers_for_directory.py --list-directories

# 或使用Make命令
make generate-covers-for-directory  # 会显示可用目录
```

#### 为指定目录生成封面

```bash
# 使用脚本（推荐）
python scripts/generate_covers_for_directory.py papers

# 使用Make命令（便捷）
make generate-covers-for-directory DIRECTORY=papers
```

## 📋 详细使用说明

### 脚本命令选项

```bash
python scripts/generate_covers_for_directory.py [目录名] [选项]
```

**参数说明：**

- `directory`: 目标目录名称（相对于 `content/zh`）
- `--recursive, -r`: 递归处理子目录（默认开启）
- `--no-recursive`: 不递归处理子目录
- `--force, -f`: 强制重新生成已有封面
- `--dry-run, -d`: 只显示将要处理的文章，不实际生成
- `--list-directories, -l`: 列出所有可用目录
- `--base-dir`: 基础内容目录（默认: content/zh）

### 使用示例

#### 示例1: 为papers目录生成封面

```bash
# 基本用法
python scripts/generate_covers_for_directory.py papers

# 使用Make命令
make generate-covers-for-directory DIRECTORY=papers
```

#### 示例2: 递归处理目录

```bash
# papers目录及其子目录
python scripts/generate_covers_for_directory.py papers --recursive

# 仅处理papers目录，不包含子目录
python scripts/generate_covers_for_directory.py papers --no-recursive
```

#### 示例3: 强制重新生成

```bash
# 强制重新生成已有封面
python scripts/generate_covers_for_directory.py papers --force

# 对应的Make命令
make generate-covers-for-directory DIRECTORY=papers FORCE=true
```

#### 示例4: 预览模式

```bash
# 查看将要处理的文章，不实际生成
python scripts/generate_covers_for_directory.py papers --dry-run

# Make命令
make generate-covers-for-directory DIRECTORY=papers DRY_RUN=true
```

#### 示例5: 处理单篇文章

```bash
# 使用原始AI封面生成脚本
python scripts/ai_cover_generator.py --specific-file content/zh/papers/voyager.md
```

## 🎨 支持的目录

以下目录可以批量生成AI封面：

### 论文类目录

- `papers` - 论文解读和学术文章
- `technologies` - 技术深度分析
- `projects` - 开源项目介绍

### 公司/组织目录

- `deepseek` - DeepSeek相关文章
- `openai` - OpenAI相关文章
- `anthropic` - Claude相关文章
- `google` - Google AI相关文章
- `apple` - Apple AI相关文章
- `microsoft` - Microsoft AI相关文章
- `bytedancing` - 字节跳动相关文章
- `baidu` - 百度AI相关文章
- `huawei` - 华为AI相关文章
- `tencent` - 腾讯AI相关文章

### 技术主题目录

- `large_models` - 大语言模型
- `mas` - 多智能体系统
- `context_engineering` - 上下文工程
- `ai_programming` - AI编程
- `training` - 模型训练
- `agi` - 通用人工智能
- `celebrity_insights` - 名人见解
- `my_insights` - 个人见解

### 其他目录

- `tools` - 工具介绍
- `products` - 产品分析
- `news` - 新闻资讯
- `daily_ai` - 每日AI动态

## 🔧 高级功能

### 条件检查

脚本会自动检查文章是否满足生成封面的条件：

1. **必须有front matter** - 文件必须以 `---` 开头
2. **必须有标题和描述** - 包含 `title:` 和 `description:` 字段
3. **不能已有封面** - 没有现有的 `ai_cover:` 或 `cover.image:` 字段

### 生成逻辑

1. **内容哈希** - 基于标题和描述生成唯一哈希
2. **缓存机制** - 相同内容的文章会复用已生成的封面
3. **路径规范** - 生成的封面保存在 `static/images/generated-covers/` 目录
4. **格式转换** - 自动转换为WebP格式，优化加载速度

### 错误处理

- **API超时** - 单篇文章生成超时为5分钟
- **网络错误** - 自动重试机制
- **格式错误** - 跳过front matter不完整的文章
- **权限错误** - 检查API密钥配置

## ⚠️ 注意事项

### API使用限制

- ModelScope API有调用频率限制
- 建议批量处理时控制数量（如 `--limit 10`）
- 避免短时间内大量调用

### 图片质量

- 生成的图片基于文章标题和描述
- 质量取决于内容描述的详细程度
- 建议为文章提供清晰、具体的描述

### 存储空间

- 每张WebP图片约100-500KB
- 大量生成会占用存储空间
- 可通过 `--force` 参数重新生成替换旧图片

## 🐛 故障排除

### 常见问题

#### Q: 提示"Directory not found"

```bash
# 检查目录名称是否正确
python scripts/generate_covers_for_directory.py --list-directories
```

#### Q: 提示"请配置API密钥"

```bash
# 检查.env文件配置
cat .env | grep MODELSCOPE_API_KEY
```

#### Q: 某篇文章生成失败

```bash
# 检查文章front matter是否完整
head -20 content/zh/papers/some-article.md
```

#### Q: 生成的封面质量不好

```bash
# 强制重新生成
python scripts/generate_covers_for_directory.py papers --force
```

### 日志查看

脚本运行时会显示详细日志，包括：

- 处理进度
- 成功/失败统计
- 错误信息和建议

### 手动干预

如果自动生成效果不理想，可以：

1. 手动编辑文章的 `description` 字段
2. 使用 `--force` 重新生成
3. 手动替换封面图片

## 📈 性能优化

### 批量处理建议

1. **分批处理** - 大目录建议分批处理，避免API限流
2. **预览模式** - 先使用 `--dry-run` 查看待处理文章
3. **缓存利用** - 相似内容的文章会自动复用封面

### 资源管理

1. **并发控制** - 脚本按顺序处理，避免并发冲突
2. **超时处理** - 单篇文章超时后继续处理下一篇
3. **断点续传** - 已生成的文章会被跳过

## 🔗 相关文件

- `scripts/ai_cover_generator.py` - 基础AI封面生成脚本
- `scripts/generate_covers_for_directory.py` - 目录批量生成脚本
- `layouts/partials/cover-image.html` - 封面显示模板
- `static/images/generated-covers/` - 生成的封面存储目录
- `cache/image-generation/generation_cache.json` - 生成缓存文件

## 📞 获取帮助

```bash
# 显示完整帮助
python scripts/generate_covers_for_directory.py --help

# 查看Make命令帮助
make help
```
