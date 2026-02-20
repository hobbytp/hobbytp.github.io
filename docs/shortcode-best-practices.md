# Shortcode 最佳实践指南

## 📚 何时使用 Shortcodes

### ✅ 应该使用 Shortcode
- **重复元素**：相同样式/结构出现多次
- **复杂布局**：HTML直接写入Markdown会很混乱
- **交互元素**：需要特定的JavaScript或CSS
- **样式化内容**：表格、网格、卡片等

### ❌ 不应该使用 Shortcode
- **简单文本**：普通段落用 Markdown
- **单次使用**：只出现一次的特殊元素考虑 HTML
- **模板通用性差**：非常特殊的一次性样式

---

## 🎨 现有 Shortcodes 使用场景

### `metric-grid` + `metric-card`

**最佳场景：**
- 💰 产品功能对比
- 📊 性能数据展示
- 🎯 目标与成果展示
- 📈 统计数据可视化

**示例用途：**
```markdown
## 我们的成果

{{< metric-grid >}}
{{< metric-card label="用户量" value="1M+" sub="月活跃用户" >}}
{{< metric-card label="准确率" value="98.5%" sub="AI识别准确率" >}}
{{< metric-card label="响应" value="<100ms" sub="平均延迟" >}}
{{< /metric-grid >}}
```

---

### `alert`

**最佳场景：**
- ℹ️ 重要信息提示
- ✅ 操作成功确认
- ⚠️ 警告和注意事项
- ❌ 错误和失败提示

**使用示例：**

```markdown
## API 使用说明

这是一个基础介绍。

{{< alert type="info" >}}
**注意**：API 密钥需要妥善保管，不要提交到版本控制系统
{{< /alert >}}

配置文件示例：

{{< alert type="success" >}}
配置完成！现在可以开始使用 API 了
{{< /alert >}}

{{< alert type="warning" >}}
**重要**：某些功能在免费版本中有调用限制
{{< /alert >}}

{{< alert type="danger" >}}
**不要**：直接在客户端代码中暴露 API 密钥
{{< /alert >}}
```

---

## 💡 实用技巧

### 1. 在 Alert 中使用 Markdown

所有 `alert` 的内容都支持 Markdown 格式：

```markdown
{{< alert type="info" >}}
这个提示包含 **加粗文本**、*斜体* 和 [链接](https://example.com)

- 还可以包含列表
- 多个项目
- 很方便
{{< /alert >}}
```

### 2. Metric Grid 的响应式行为

Grid 会根据屏幕大小自动调整：
- **桌面** (>960px): 3列
- **平板** (600px-960px): 2列  
- **手机** (<600px): 1列（堆叠）

### 3. 嵌套和组合

可以组合多个 shortcode：

```markdown
{{< alert type="success" >}}
### 关键成果

{{< metric-grid >}}
{{< metric-card label="完成度" value="100%" sub="项目进度" >}}
{{< metric-card label="质量分" value="A+" sub="代码审查结果" >}}
{{< /metric-grid >}}
{{< /alert >}}
```

---

## 🔧 常见问题

### Q: Shortcode 中能否使用 HTML？
**A:** 可以在 shortcode 的 `.Inner` 内容中包含 HTML，例如：
```markdown
{{< alert type="info" >}}
<div style="color: red;">自定义HTML</div>
{{< /alert >}}
```
但不建议这样做，优先使用 Markdown。

### Q: 如何自定义 Shortcode 样式？
**A:** 编辑 `assets/css/custom.css`，找到对应的 CSS 类。所有样式都遵循变量系统：
```css
.metric-card {
  background: var(--color-bg);  /* 自动适应浅色/深色主题 */
  color: var(--color-text);
}
```

### Q: Shortcode 参数中是否支持特殊字符？
**A:** 如需传递包含特殊字符的内容，使用带引号的字符串：
```markdown
{{< metric-card label="用户数（全球）" value="1M+" sub="Total active users" >}}
```

### Q: 如何在 shortcode 中使用变量？
**A:** Shortcodes 不支持动态变量。如需动态内容，建议在主题模板中实现。

---

## 📝 创建新 Shortcode 的步骤

### 1. 创建 HTML 文件

`layouts/shortcodes/my-shortcode.html`:
```html
{{- /*
  我的自定义 Shortcode
  用法: {{< my-shortcode param="value" >}}内容{{< /my-shortcode >}}
*/ -}}

<div class="my-shortcode">
  <h3>{{ .Get "param" }}</h3>
  {{ .Inner | markdownify }}
</div>
```

### 2. 添加 CSS 样式

在 `assets/css/custom.css` 添加：
```css
.my-shortcode {
  padding: 1rem;
  border: 1px solid var(--article-border);
  border-radius: 0.5rem;
}
```

### 3. 编写文档

在 `docs/shortcode-guide-2025.md` 中添加：
- 用法说明
- 参数文档
- 使用示例

### 4. 测试

```bash
# 本地测试
make dev
# 在 http://localhost:1313 上验证
```

---

## 🎯 建议的新 Shortcodes

基于你的博客内容，这些 shortcodes 可能很有用：

### 1. `timeline` - 时间线
```markdown
{{< timeline >}}
{{< timeline-item date="2024-01" title="发布 v1.0" >}}
首个稳定版本发布
{{< /timeline-item >}}
{{< /timeline >}}
```

### 2. `comparison` - 对比表格
```markdown
{{< comparison >}}
{{< comparison-item name="方案A" pros="成本低" cons="速度慢" >}}
{{< /comparison >}}
```

### 3. `code-tabs` - 代码选项卡
```markdown
{{< code-tabs >}}
{{< code-tab lang="python" >}}
# Python 代码
{{< /code-tab >}}
{{< code-tab lang="javascript" >}}
// JavaScript 代码
{{< /code-tab >}}
{{< /code-tabs >}}
```

### 4. `definition` - 术语定义
```markdown
{{< definition term="API" >}}
应用程序编程接口...
{{< /definition >}}
```

---

## ✨ 最佳实践总结

1. **保持简洁**：Shortcode 应该做一件事，并做好
2. **支持 Markdown**：使用 `markdownify` 过滤器处理内容
3. **遵循主题**：使用 CSS 变量确保主题一致性
4. **文档完整**：每个 shortcode 都要有清晰的文档
5. **易于扩展**：参数化设计，支持多种用途
6. **测试充分**：不同屏幕尺寸和主题下测试

---

**最后更新**: 2025-12-19  
**维护者**: Hugo Blog Team

