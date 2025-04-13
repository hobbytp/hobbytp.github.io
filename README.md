# 个人 AI 博客

欢迎来到我的个人 AI 博客仓库，本博客主要关注 AI 领域的论文解读、最新技术、开源项目、知名人物访谈、动态和商业产品介绍。

## 目录结构

- **content/**：存放中英文博客内容，按照主题（papers、technologies、projects、interviews、news、products）分类。
- **assets/**：存放图片和样式表。
- **layouts/**：页面模板和局部模板，包括 header、footer、SEO 模板及标签系统部分。
- **config/**：站点配置与国际化支持文件。
- **docs/**.md**：详细记录了大部分博客网站设计，和部分改进建议（如标签系统、自动化部署、SEO 优化、多语言支持等）。
- **.github/workflows/deploy.yml**：GitHub Actions 自动化部署配置。

## 分支策略

- 建议在 `dev` 分支上进行新功能和内容的开发与测试，待确认稳定后再合并到 `main` 分支。合并到 `main` 后，GitHub Actions 将自动触发部署流程.

## 用户反馈

如有疑问或建议，请点击页面底部的反馈链接，或直接在 [GitHub Issue](https://github.com/yourusername/yourrepo/issues) 提交反馈。

---

测试部署 - {{ timestamp }}
