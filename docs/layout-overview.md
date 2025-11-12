# 布局总览 (Layout Overview)

**最后更新:** 2025-11-12  
**状态:** ✅ 稳定 / 可扩展  

本文件描述当前 Hugo + PaperMod 驱动的站点布局策略：左侧固定侧栏、中央主内容区域、右侧粘性目录 (TOC) 与滚动高亮（ScrollSpy）。旨在帮助后续维护、移动端优化与增强迭代。

---
## 1. 整体结构概念

```
.main-container
├─ <aside class="sidebar">        # 固定左侧导航/分类
├─ <div class="main-content-with-sidebar">  # 文章列表或正文 + (文章页) TOC 容器
    ├─ 列表页: .article-grid (卡片布局)
    └─ 文章页: .post-layout (正文 + .toc-sidebar)
```

- 左侧侧栏固定宽度（约 260px），通过主内容的 `padding-left` 让布局自然留出空间。
- 文章页右侧 TOC 使用 `position: sticky; top: <offset>;`，在滚动时保持可见。
- 不使用外部 CSS 框架 CDN，所有样式通过 Hugo 管线构建指纹化 bundle。

---
## 2. Sidebar (左侧侧栏)

功能：导航、分类入口、可扩展标签或搜索入口。  
实现要点：
- 模板：`layouts/partials/sidebar.html`
- 插入位置：`_default/list.html` 与 `_default/single.html` 在 `.main-container` 下作为第一个子元素。
- 不与主内容发生嵌套（避免宽度塌缩）。

未来改进：移动端折叠（drawer / overlay）、分类动态筛选、搜索联动。

---
## 3. 主内容区域

列表页：
- 容器：`.article-grid` → 基于 CSS Grid / 自适应列（后续可扩展 `grid-template-columns: repeat(auto-fit,minmax(...))`）。

文章页：
- 容器：`.post-layout` → 两列：正文 + TOC。
- 正文：标准 PaperMod 渲染；支持标题层级生成 TOC。

---
## 4. TOC 粘性与滚动高亮 (ScrollSpy)

### 4.1 TOC 结构
- 容器：`.toc-sidebar`
- 内容来源：Hugo 的 `TableOfContents` 或自定义生成（未来可扩展层级过滤、最小深度）。

### 4.2 粘性定位
```css
.toc-sidebar { position: sticky; top: 90px; max-height: calc(100vh - 120px); overflow:auto; }
```
> `top` 具体值根据 Header 隐藏情况调整。

### 4.3 滚动高亮策略
- 优先使用 `IntersectionObserver`（性能好，避免频繁 `scroll` 监听）
- 观察正文中 `h2/h3/...` 节点进入视窗时更新 TOC 链接的 `active` / `aria-current="true"`

伪代码：
```js
const headings = document.querySelectorAll(".post-content h2, .post-content h3");
const map = new Map();
headings.forEach(h => map.set(h.id, document.querySelector(`.toc-sidebar a[href="#${h.id}"]`)));
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      map.forEach(a => a.classList.remove('active'));
      const link = map.get(e.target.id);
      if (link) { link.classList.add('active'); link.setAttribute('aria-current','true'); }
    }
  });
}, { rootMargin: '0px 0px -60% 0px', threshold: 0.1 });
headings.forEach(h => observer.observe(h));
```

### 4.4 高亮样式建议
```css
.toc-sidebar a.active {
  font-weight: 600;
  color: var(--primary);
  border-left: 3px solid var(--primary);
  padding-left: 6px;
  background: rgba(0,0,0,0.04);
}
```

---
## 5. CSS 管线与限制

- 构建来源：`assets/css/main.css` + `assets/css/extended/*.css` + `assets/css/custom.css`
- 指纹输出：`bundle.min.<hash>.css`
- 限制：`custom.css` 最大 1000 行（当前 ~745 行，建议逐步拆分为 `layout.css` / `components.css` / `utilities.css`）
- 禁止：Tailwind CDN、`:contains()` 等不兼容选择器、多余实验性全局覆盖。

---
## 6. 可访问性 (A11y)

- TOC 当前高亮应加 `aria-current="true"`
- 后续可为侧栏导航增加 `aria-label="Primary"`
- 标题层级建议保持语义连续（不跳过 h2 -> h4）

---
## 7. 移动端后续路线 (Roadmap)

| 目标 | 描述 | 优先级 |
|------|------|--------|
| Sidebar 折叠 | 宽度 < 768px 时隐藏为按钮 + Drawer | 高 |
| TOC 折叠 | 移动端收缩为 `details` / 点击展开 | 中 |
| 性能微调 | 减少不必要的观察节点，延迟初始化 | 中 |
| 样式拆分 | `custom.css` 模块化 | 中 |
| 动效最小化 | 避免滚动时多余 box-shadow/渐变 | 低 |

---
## 8. 常见问题 (FAQ)

**Q: 为什么不用 Tailwind?**  
A: 现阶段 PaperMod 原生样式 + 定制 CSS 足够；CDN + 预处理冲突会带来维护与覆盖复杂性。

**Q: 为什么不用全局 JS 框架?**  
A: 当前交互简单，原生 JS 足够；减少包负担。

**Q: TOC 未生成?**  
A: 检查文章标题层级是否正确，或确保模板使用 Hugo 的 `.TableOfContents`。

---
## 9. 变更记录（布局相关新增）
- v2.1: 引入左侧固定侧栏 + 右侧粘性 TOC + ScrollSpy；移除 Tailwind CDN；修复重复 `<aside>` 导致内容宽度塌缩。

---
**维护建议**：布局是“阅读体验”的基础层，不要在未验证宽度/滚动/可访问性之前做激进替换；增量演进，保留可回滚点。
