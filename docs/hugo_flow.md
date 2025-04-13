# 项目文档：AI技术博客

## 业务目标

- 提供高质量的AI领域技术内容分享
- 建立AI技术交流平台
- 记录和传播AI领域最新发展动态

## 核心功能

- 内容发布系统：
  - 支持中英双语内容
  - 分类管理（论文/技术/项目/访谈/新闻/产品）
  - 标签系统
- 读者服务：
  - 阅读时间估算
  - 目录导航
  - 内容分享功能

- 管理功能
  - GitHub Actions自动化部署
  - 多分支开发流程

## 整体架构

```
前端展示层(Hugo) ←→ 内容层(Markdown) ←→ 部署层(GitHub Pages)
       ↑
配置层(config.toml)
```

## 数据实体

- 文章(Post)：
  - 标题/作者/发布时间
  - 分类/标签
  - 阅读时间/内容

- 分类(Category)：
  - 论文解读
  - 技术解析
  - 开源项目
  - 人物访谈
  - 行业动态
  - 产品介绍

- 用户配置：
  - 个人资料
  - 社交链接

## 业务流程

- 内容创作流程： 作者编写Markdown → 推送到dev分支 → 测试验证 → 合并到main → 自动部署
- 读者访问流程： 访问首页 → 选择分类 → 浏览文章 → 分享/反馈
- 维护流程： 问题反馈 → GitHub Issue跟踪 → 修复更新

## Hugo工作流

Hugo的前端展示工作流程如下：

1. 核心模板文件：

- layouts/_default/baseof.html：基础模板框架
- layouts/_default/single.html：单篇文章模板
- layouts/_default/list.html：列表页模板
- layouts/index.html：首页模板
layouts/index.html：首页模板

2. 模板继承机制：
   Hugo采用"模板继承"模式，baseof.html定义了整体HTML结构，其他模板通过{{ define }}块填充具体内容。例如：

```html
<!-- baseof.html -->
<html>
  <head>{{ block "head" . }}{{ end }}</head>
  <body>
    {{ block "main" . }}{{ end }}
  </body>
</html>
```

3. 内容渲染流程：
   - Hugo读取Markdown内容文件（如content/posts/example.md）
   - 根据front matter中的type选择对应模板
   - 将Markdown转换为HTML插入模板
   - 应用主题样式（PaperMod）生成最终HTML
4. 关键组件：
   - layouts/partials/：存放可复用的组件（页头、页脚等）
   - assets/css/：自定义样式表
   - themes/PaperMod/：主题默认模板和资源

5. GitHub Pages的默认路由规则：
   - 当项目同时存在index.html和README.md时，GitHub Pages会优先显示index.html

但如果Hugo构建过程中出现以下情况，会导致回退到README.md：

- index.html生成失败
- 构建输出目录错误
- 部署流程未正确覆盖原有文件
