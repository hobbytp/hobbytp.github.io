# 个人 AI 技术博客 🤖 | AI Tech Blog

[![部署状态](https://img.shields.io/badge/部署-成功-green)](https://hobbytp.github.io)
[![Hugo](https://img.shields.io/badge/Hugo-v0.120+-blue)](https://gohugo.io)
[![许可证](https://img.shields.io/badge/许可证-MIT-blue)](LICENSE)
[![AI Blog](https://img.shields.io/badge/AI-Blog-orange)](https://hobbytp.github.io)
[![Papers](https://img.shields.io/badge/Papers-Reviews-blue)](https://hobbytp.github.io/categories/papers)

欢迎来到我的个人 AI 技术博客！这是一个基于 Hugo 构建的静态网站，专注于分享 AI 领域的深度内容和前沿技术。涵盖机器学习、深度学习、大语言模型、多智能体系统等热门技术领域。

## 📖 博客内容

本博客涵盖以下主要领域：

> **关键词**: AI博客, 机器学习, 深度学习, 大语言模型, LLM, 论文解读, 技术分析, 开源项目, 多智能体系统, RAG, Transformer, 神经网络, 自然语言处理, NLP, 人工智能研究

### 🎯 核心内容

- **论文解读**：深度解析最新的 AI/ML 论文，从理论到实践
- **技术分析**：前沿技术深度剖析，包括大语言模型、多智能体系统等
- **开源项目**：优秀开源项目介绍与实战指南
- **行业动态**：AI 领域最新发展趋势和重要事件
- **产品评测**：商业 AI 产品深度体验与对比分析

### 🏢 重点关注

- **知名企业**：OpenAI、Google、微软、百度、阿里巴巴等
- **技术领域**：LLM、RAG、Agent、多模态、训练优化
- **开发工具**：Cursor、Claude MCP、LangChain、AutoGen 等
- **名人访谈**：行业专家观点与技术分享

## 🛠️ 技术栈

- **框架**：[Hugo](https://gohugo.io/) - 快速静态网站生成器
- **主题**：DoIt & PaperMod - 响应式设计，支持暗色模式
- **部署**：GitHub Pages - 自动化 CI/CD
- **语言支持**：中文/英文双语
- **搜索功能**：集成全文搜索
- **评论系统**：支持多种评论插件
- **链接样式**：增强的链接视觉效果，支持暗色模式

## 🚀 快速开始

### 环境要求

- Hugo Extended v0.120.0+
- Git
- Node.js (可选，用于主题开发)

### GitHub Topics 设置

为了提高仓库的搜索引擎可见性，建议添加相关标签：

```bash
# 方法1: 使用GitHub CLI
./scripts/setup-github-topics.sh

# 方法2: 使用Python脚本
pip install -r scripts/requirements.txt
export GITHUB_TOKEN=your_token
python scripts/setup-github-topics.py

# 方法3: 手动设置
# 访问 https://github.com/hobbytp/hobbytp.github.io
# 点击 About -> 添加 Topics
```

详细说明请参考：[GitHub Topics 配置指南](docs/github-topics-guide.md)

### 链接样式增强

博客采用了增强的链接样式，使链接更容易识别：

- **明显标识**: 蓝色文字 + 2px 下划线
- **悬停效果**: 背景色变化 + 圆角边框
- **外部链接**: 自动添加 "↗" 图标
- **特殊网站**: YouTube(红色)、GitHub(深色)、ArXiv(深红色)
- **暗色模式**: 自动适配浅蓝色主题
- **响应式**: 移动端优化显示

详细说明请参考：[链接样式增强指南](docs/link-styling-guide.md)

### 本地运行

```bash
# 克隆项目
git clone https://github.com/hobbytp/hobbytp.github.io.git
cd hobbytp.github.io

# 初始化子模块（主题）
git submodule update --init --recursive

# 启动开发服务器
hugo server -D --bind 0.0.0.0

# 访问 http://localhost:1313
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用 Docker
docker build -t ai-blog .
docker run -p 1313:1313 ai-blog
```

### 使用 Make 运行与构建（推荐）

为确保一致的开发体验并触发必要的验证钩子，建议通过 `make` 管理 Hugo：

```bash
# 启动开发服务器（如已在运行，先执行 make stop）
make dev

# 停止已启动的 Hugo 服务
make stop

# 生产构建（用于部署，包含最完整输出）
make build

# 查看所有可用命令
make help
```

## 📁 项目结构

```text
├── content/                 # 内容目录
│   ├── zh/                 # 中文内容
│   │   ├── papers/         # 论文解读
│   │   ├── projects/       # 项目介绍
│   │   ├── news/          # 行业动态
│   │   └── ...
│   ├── en/                # 英文内容
│   └── draft/             # 草稿文件
├── themes/                # Hugo 主题
│   ├── DoIt/             # 主主题
│   └── PaperMod/         # 备用主题
├── static/               # 静态资源
├── layouts/              # 自定义布局
├── config.toml           # 网站配置
└── docker-compose.yml    # Docker 配置
```

## ✍️ 内容创作

### 添加新文章

```bash
# 创建新的技术文章
hugo new content/zh/technologies/new-article.md

# 创建新的论文解读
hugo new content/zh/papers/paper-review.md

# 创建项目介绍
hugo new content/zh/projects/project-intro.md
```

### 文章 Front Matter 示例

```yaml
---
title: "文章标题"
date: 2024-01-15T10:00:00+08:00
draft: false
tags: ["AI", "LLM", "技术"]
categories: ["技术分析"]
author: "作者名"
description: "文章简介"
---
```

## 🌍 多语言支持

- **中文**：主要语言，包含完整内容
- **英文**：部分重要内容的英文版本
- 配置文件：`i18n/` 目录下的语言配置

## 🎨 自定义配置

### 主题配置

主要配置文件：`config.toml`

### 自定义样式

- CSS 文件：`assets/css/main.css`
- 布局文件：`layouts/` 目录

> 样式统一通过 Hugo 资源管线打包（指纹化输出），不使用外部 CSS CDN（如 Tailwind CDN）。

### 🧩 布局特性

- 左侧固定侧栏：提供分类与导航，桌面端始终可见
- 中间主内容区：文章卡片网格与正文阅读自适应宽度
- 右侧粘性目录（文章页）：自动生成目录，支持滚动联动高亮（ScrollSpy）
- 指纹化 CSS 构建：Hugo 管线统一打包，无外部样式依赖

### 搜索功能

集成了全文搜索，支持中英文内容检索。

## 📊 部署与CI/CD

- **自动部署**：推送到 main 分支自动触发 GitHub Pages 部署
- **构建状态**：可在 Actions 页面查看构建状态
- **CDN 加速**：静态资源通过 CDN 加速访问
- **架构校验**：提交前自动运行验证脚本（检测外部 CSS CDN、模板结构、CSS 体积等），保障稳定性

## 🤝 贡献指南

欢迎各种形式的贡献：

1. **内容贡献**：提交优质的技术文章或翻译
2. **错误修正**：发现错误请提交 Issue 或 PR
3. **功能建议**：通过 Issue 提出新功能建议
4. **主题优化**：改进网站设计和用户体验

### 提交流程

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 📬 联系与反馈

- **GitHub Issue**：[提交问题或建议](https://github.com/hobbytp/hobbytp.github.io/issues)
- **邮箱**：通过 GitHub Profile 联系
- **博客评论**：在相应文章下留言

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)，欢迎自由使用和分发。

## 🙏 致谢

感谢以下开源项目：

- [Hugo](https://gohugo.io/) - 静态网站生成器
- [DoIt 主题](https://github.com/HEIGE-PCloud/DoIt) - 美观的 Hugo 主题
- [PaperMod 主题](https://github.com/adityatelange/hugo-PaperMod) - 简洁的 Hugo 主题

---

**最后更新**：{{ .Date.Format "2006-01-02" }}

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！

## 🏷️ 相关标签

**GitHub Topics**: `ai-blog`, `hugo`, `machine-learning`, `deep-learning`, `llm`, `artificial-intelligence`, `paper-review`, `tech-analysis`, `open-source`, `github-pages`, `static-site`, `chinese`, `bilingual`, `rag`, `multi-agent`, `transformer`, `neural-networks`, `nlp`

**技术栈**: Hugo, PaperMod, GitHub Pages, Markdown, CSS, JavaScript

**内容分类**: 论文解读, 技术分析, 开源项目, 行业动态, 产品评测, 名人访谈

---

## Personal AI Tech Blog 🤖

[![Deployment Status](https://img.shields.io/badge/Deployment-Success-green)](https://hobbytp.github.io)
[![Hugo](https://img.shields.io/badge/Hugo-v0.120+-blue)](https://gohugo.io)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

Welcome to my personal AI tech blog! This is a Hugo-based static website focused on sharing in-depth AI content and cutting-edge technologies.

## 📖 Blog Content

This blog covers the following main areas:

### 🎯 Core Content

- **Paper Reviews**: In-depth analysis of the latest AI/ML papers, from theory to practice
- **Technical Analysis**: Deep dive into frontier technologies, including LLMs, multi-agent systems, etc.
- **Open Source Projects**: Introduction and practical guides for excellent open source projects
- **Industry Trends**: Latest developments and important events in the AI field
- **Product Reviews**: In-depth experience and comparative analysis of commercial AI products

## 🛠️ Tech Stack

- **Framework**: [Hugo](https://gohugo.io/) - Fast static site generator
- **Themes**: DoIt & PaperMod - Responsive design with dark mode support
- **Deployment**: GitHub Pages - Automated CI/CD
- **Language Support**: Chinese/English bilingual
- **Search**: Integrated full-text search
- **Comments**: Support for multiple comment plugins

### 🧩 Layout Features

- Fixed left sidebar with taxonomy/navigation
- Adaptive central content area (cards + articles)
- Sticky right-hand Table of Contents (posts) with scroll-driven highlighting
- Fingerprinted CSS bundle via Hugo pipeline (no external CSS CDN)

## 🚀 Quick Start

### Requirements

- Hugo Extended v0.120.0+
- Git
- Node.js (optional, for theme development)

### Local Development

```bash
# Clone the project
git clone https://github.com/hobbytp/hobbytp.github.io.git
cd hobbytp.github.io

# Initialize submodules (themes)
git submodule update --init --recursive

# Start development server
hugo server -D --bind 0.0.0.0

# Visit http://localhost:1313
```

## 🤝 Contributing

All forms of contributions are welcome:

1. **Content Contribution**: Submit quality technical articles or translations
2. **Error Correction**: Submit Issues or PRs when finding errors
3. **Feature Suggestions**: Propose new features through Issues
4. **Theme Optimization**: Improve website design and user experience

## 📬 Contact & Feedback

- **GitHub Issue**: [Submit questions or suggestions](https://github.com/hobbytp/hobbytp.github.io/issues)
- **Email**: Contact through GitHub Profile
- **Blog Comments**: Leave comments under relevant articles

## 📄 License

This project is licensed under the [MIT License](LICENSE), free to use and distribute.

---

**Last Updated**: {{ .Date.Format "2025-07-02" }}

## 🏷️ Related Tags

**GitHub Topics**: `ai-blog`, `hugo`, `machine-learning`, `deep-learning`, `llm`, `artificial-intelligence`, `paper-review`, `tech-analysis`, `open-source`, `github-pages`, `static-site`, `chinese`, `bilingual`, `rag`, `multi-agent`, `transformer`, `neural-networks`, `nlp`

**Tech Stack**: Hugo, PaperMod, GitHub Pages, Markdown, CSS, JavaScript

**Content Categories**: Paper Reviews, Technical Analysis, Open Source Projects, Industry News, Product Reviews, Celebrity Interviews

⭐ If this project helps you, please give it a Star for support!

