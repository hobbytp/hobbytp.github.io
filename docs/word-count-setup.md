# 字数统计自动更新指南

本博客系统支持自动计算和更新文章的字数和阅读时间统计，避免了每次页面加载时都需要客户端计算的问题。

## 📊 工作原理

1. **构建时优先使用 front matter**: Hugo 模板优先读取 front matter 中的 `wordCount` 和 `readingTime` 字段
2. **客户端回退**: 如果 front matter 中没有数据，JavaScript 会在客户端计算
3. **自动更新**: 通过 Git pre-commit hook 在提交时自动更新统计

## 🚀 快速开始

### 1. 安装 Git Hook（推荐）

运行安装脚本：

```bash
bash scripts/setup_git_hooks.sh
```

安装后，每次提交包含 `.md` 文件的 commit 时，会自动：
- 检测变更的 Markdown 文件
- 计算中文字数和阅读时间
- 更新 front matter 中的 `wordCount` 和 `readingTime` 字段
- 自动将更新后的文件添加到暂存区

### 2. 手动更新所有文件

如果想一次性更新所有文章的统计：

```bash
# 检查所有文件（不修改）
python scripts/update_word_count.py

# 更新所有文件
python scripts/update_word_count.py --update

# 更新特定目录
python scripts/update_word_count.py --update --dir content/zh/daily_ai

# 更新特定文件
python scripts/update_word_count.py --update content/zh/projects/mcp/skill_seeker.md
```

## 📝 Front Matter 格式

更新后的文章 front matter 会自动包含：

```yaml
---
title: "文章标题"
date: 2025-11-02T20:10:00+08:00
wordCount: 1234      # 中文字符数
readingTime: 5       # 阅读时间（分钟）
---
```

## 🔧 统计规则

- **字数统计**: 统计中文字符数（包括中文标点符号）
  - `\u4e00-\u9fa5`: 中文汉字
  - `\u3000-\u303f`: CJK符号和标点
  - `\uff00-\uffef`: 全角符号

- **阅读时间**: 基于中文阅读速度 **250字/分钟**
  ```javascript
  阅读时间 = Math.ceil(字数 / 250)
  ```

## ⚡ 性能优化

使用 front matter 存储统计数据的优势：

1. **构建时已知**: Hugo 在构建时就知道了字数和阅读时间，无需客户端计算
2. **零延迟**: 页面加载时立即显示，无需等待 JavaScript 计算
3. **SEO友好**: 统计信息是静态的，搜索引擎可以索引

## 🛠️ 故障排除

### Hook 没有运行

如果 pre-commit hook 没有自动运行：

1. 检查 hook 文件是否存在且可执行：
   ```bash
   ls -l .git/hooks/pre-commit
   ```

2. 检查 Python 环境：
   ```bash
   python --version
   python -c "import yaml; print('PyYAML OK')"
   ```

3. 手动运行脚本测试：
   ```bash
   python scripts/update_word_count.py content/zh/test.md
   ```

### 跳过 Hook（紧急情况）

如果需要跳过 hook（不推荐）：

```bash
git commit --no-verify -m "紧急提交"
```

### 重新安装 Hook

```bash
bash scripts/setup_git_hooks.sh
```

## 📚 更多信息

- 脚本位置: `scripts/update_word_count.py`
- Hook 位置: `.git/hooks/pre-commit`
- 相关模板: `layouts/_default/single.html`, `layouts/_default/single-spa.html`

