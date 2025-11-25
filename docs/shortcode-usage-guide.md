# Hugo Shortcode 使用指南

**最后更新:** 2025-11-25  
**状态:** ✅ 可用

本文档介绍博客中可用的自定义 Hugo Shortcode，帮助作者在文章中嵌入各种媒体和交互组件。

---

## 1. PDF 文档嵌入

### 1.1 功能说明

`pdf` shortcode 允许在文章中嵌入 PDF 文档查看器，支持以下特性：

- ✅ 本地 PDF 文件和远程 URL
- ✅ Google Docs 嵌入模式
- ✅ 自定义高度
- ✅ 全屏查看模式
- ✅ 下载按钮（本地文件）
- ✅ 响应式设计
- ✅ 暗色/亮色模式适配

### 1.2 基本用法

**嵌入本地 PDF 文件：**

```markdown
{{</* pdf src="/pdf/my-document.pdf" */>}}
```

> 📁 本地 PDF 文件需放置在 `static/pdf/` 目录下

**嵌入远程 PDF 文件：**

```markdown
{{</* pdf src="https://example.com/document.pdf" */>}}
```

**嵌入 Google Docs 文档：**

```markdown
{{</* pdf src="https://docs.google.com/document/d/xxx/edit" type="google" */>}}
```

### 1.3 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `src` | string | **必填** | PDF 文件路径或 URL |
| `title` | string | "PDF Document" | 文档标题，显示在查看器上方 |
| `height` | string | "600px" | 查看器高度，支持 px、vh 等单位 |
| `type` | string | - | 设为 `"google"` 可嵌入 Google Docs |

### 1.4 完整示例

**带标题和自定义高度：**

```markdown
{{</* pdf src="/pdf/research-paper.pdf" title="研究论文" height="800px" */>}}
```

**嵌入 Google Slides：**

```markdown
{{</* pdf src="https://docs.google.com/presentation/d/xxx/edit" type="google" title="演示文稿" */>}}
```

### 1.5 文件放置

本地 PDF 文件需要放在 `static/` 目录下，建议的目录结构：

```
static/
└── pdf/
    ├── research-paper.pdf
    ├── presentation.pdf
    └── report-2025.pdf
```

在 shortcode 中使用时，路径从根目录开始：

```markdown
{{</* pdf src="/pdf/research-paper.pdf" */>}}
```

### 1.6 注意事项

1. **跨域限制**：某些远程 PDF 可能因 CORS 限制无法加载，建议下载到本地使用
2. **文件大小**：大型 PDF 文件会影响页面加载速度，建议压缩后使用
3. **移动端**：查看器在移动设备上会自动适配宽度
4. **Google Docs**：使用 `type="google"` 时，确保文档设置为"任何人都可以查看"

---

## 2. 更多 Shortcode（待添加）

后续可在此文档中添加其他自定义 shortcode 的使用说明。

---

## 附录：Shortcode 文件位置

所有自定义 shortcode 模板位于：

```
layouts/shortcodes/
├── pdf.html          # PDF 查看器
└── ...               # 其他 shortcode
```
