我来详细解释如何管理和自定义 Hugo 主题。首先让我看一下你当前的自定义布局：

# 1. 主题管理

### 1.1 主题更新

```bash
# 更新主题子模块到最新版本
git submodule update --remote themes/PaperMod

# 提交更新
git add themes/PaperMod
git commit -m "Update PaperMod theme"
```

### 1.2 主题切换

1. 添加新主题：

```bash
git submodule add https://github.com/主题仓库地址 themes/新主题名
```

2. 在 `config.toml` 中修改主题：

```toml
theme = "新主题名"
```

## 2. 主题自定义

### 2.1 自定义方法优先级（从高到低）

1. `/layouts/*`: 项目根目录下的布局文件
2. `/themes/PaperMod/layouts/*`: 主题目录下的布局文件

### 2.2 常见自定义位置

1. **布局模板**：
   - `/layouts/_default/`: 默认模板
   - `/layouts/partials/`: 部分模板
   - `/layouts/index.html`: 首页模板

2. **样式文件**：
   - `/assets/css/`: 自定义 CSS
   - `/static/css/`: 静态 CSS 文件

3. **JavaScript**：
   - `/assets/js/`: 自定义 JavaScript
   - `/static/js/`: 静态 JavaScript 文件

### 2.3 自定义示例

1. **修改页面布局**：
让我看一下你的首页模板：

Read file: layouts/index.html
我看到你已经对首页做了很好的自定义，包括：

- 左侧导航栏
- 标签云
- 最新文章展示
- 分类文章展示
- 响应式布局

### 2.4 自定义最佳实践

1. **不要直接修改主题文件**
   - 正确：在根目录 `/layouts` 创建同名文件覆盖
   - 错误：修改 `/themes/PaperMod/layouts` 中的文件

2. **保持目录结构一致**
   - 要覆盖主题中的 `themes/PaperMod/layouts/partials/header.html`
   - 应创建 `/layouts/partials/header.html`

3. **CSS 自定义**
   - 创建 `/assets/css/extended.css` 添加自定义样式
   - 在 `config.toml` 中启用：

   ```toml
   [params]
     customCSS = ["css/extended.css"]
   ```

4. **部分修改**
   - 可以只覆盖需要修改的部分
   - 使用 Hugo 的 partial 模板系统

   ```html
   {{ partial "original-theme-partial" . }}
   <!-- 添加自定义内容 -->
   ```

5. **响应式设计**
   - 使用 CSS 媒体查询
   - 测试不同设备尺寸
   - 确保移动端友好

### 2.5 调试技巧

1. **Hugo 服务器模式**

```bash
hugo server -D
```

- `-D` 显示草稿内容
- 实时预览修改

2. **检查模板**

```bash
hugo --templateMetrics
```

- 显示模板使用情况
- 帮助定位性能问题

3. **调试模式**

```bash
hugo server --debug
```

- 显示详细的调试信息
- 帮助解决模板问题

### 2.6 版本控制

1. **主题更改**：
   - 在 Git 中忽略主题的修改：

   ```gitignore
   themes/PaperMod/*
   ```

   - 将自定义更改放在版本控制中

2. **文档化**：
   - 记录所有自定义修改
   - 更新 README.md
   - 说明自定义的原因和方法

需要我详细解释某个具体的自定义方面吗？或者你想了解如何实现特定的功能？
