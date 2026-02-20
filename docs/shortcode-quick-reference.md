# 🚀 Shortcode 快速参考

当前已实现的 shortcodes 速查表。

---

## 已实现的 Shortcodes

### 1️⃣ `metric-grid` + `metric-card`

**用途**: 展示多个统计指标或数据卡片

**基础语法**:
```markdown
{{< metric-grid >}}
{{< metric-card label="标签" value="值" sub="说明" >}}
{{< /metric-grid >}}
```

**完整示例**:
```markdown
## 产品性能数据

{{< metric-grid >}}
{{< metric-card label="用户量" value="1M+" sub="月活跃用户" >}}
{{< metric-card label="准确率" value="98.5%" sub="识别准确度" >}}
{{< metric-card label="响应速度" value="<100ms" sub="平均延迟" >}}
{{< /metric-grid >}}
```

**参数说明**:
| 参数 | 必选 | 说明 | 示例 |
|------|------|------|------|
| label | ✅ | 指标标签 | "用户量" |
| value | ✅ | 数值或统计 | "1M+", "98.5%" |
| sub | ✅ | 副说明文字 | "月活跃用户" |

**样式特性**:
- ✨ 响应式网格（桌面3列、平板2列、手机1列）
- 🎨 深色主题适配
- 🖱️ 鼠标悬停效果（上移+阴影）
- 📱 移动设备友好

**实现文件**:
- Template: `layouts/shortcodes/metric-grid.html`
- Template: `layouts/shortcodes/metric-card.html`
- Styles: `assets/css/custom.css` (lines 1140-1170)

---

### 2️⃣ `alert`

**用途**: 显示提示、成功、警告或错误信息

**基础语法**:
```markdown
{{< alert type="info" >}}
内容
{{< /alert >}}
```

**完整示例**:
```markdown
{{< alert type="info" >}}
**注意**: 这是一条重要信息，支持 **Markdown** 格式
{{< /alert >}}

{{< alert type="success" >}}
✓ 操作成功完成
{{< /alert >}}

{{< alert type="warning" >}}
⚠️ 请注意限制条件
{{< /alert >}}

{{< alert type="danger" >}}
❌ 这是一条错误或危险警告
{{< /alert >}}
```

**参数说明**:
| 参数 | 必选 | 值 | 说明 |
|------|------|-----|------|
| type | ✅ | `info` / `success` / `warning` / `danger` | 警告类型 |

**内容支持**:
- ✅ Markdown 格式（加粗、斜体、链接、列表等）
- ✅ 多行内容
- ✅ 嵌套其他元素

**样式特性**:
- 🎨 4种不同的颜色主题
- 🔶 左边框 + 背景渐变
- 🏷️ Font Awesome 图标自动匹配
- 🌙 深色主题适配

**图标映射**:
| Type | Icon | Color |
|------|------|-------|
| info | 🔵 circle-info | #0284c7 |
| success | ✅ circle-check | #16a34a |
| warning | ⚠️ triangle-exclamation | #ea580c |
| danger | ❌ circle-xmark | #dc2626 |

**实现文件**:
- Template: `layouts/shortcodes/alert.html`
- Styles: `assets/css/custom.css` (lines 1171-1195)

---

## 🎯 使用场景速查

### 何时使用 metric-grid?

✅ **应该用**:
- 📊 产品功能对比
- 💰 成本/预算数据
- 📈 性能指标
- 🎯 成就展示
- 📉 统计数据

❌ **不应该用**:
- 单个数值展示（改用 `highlight` shortcode）
- 动态数据（需要JavaScript更新）
- 超复杂的表格对比

### 何时使用 alert?

✅ **应该用**:
- ℹ️ 重要提示
- ✅ 操作成功确认
- ⚠️ 使用限制说明
- ❌ 错误消息
- 📌 特别注意事项

❌ **不应该用**:
- 普通段落文本
- 长篇幅内容（alert 不适合大块内容）
- 需要隐藏/展开的内容（用 collapsible 代替）

---

## 📝 内容示例

### 示例1: 产品对比

```markdown
## 我们的优势

{{< metric-grid >}}
{{< metric-card label="处理速度" value="10x快" sub="比竞品更快" >}}
{{< metric-card label="成本" value="50%低" sub="更经济的方案" >}}
{{< metric-card label="可靠性" value="99.99%" sub="SLA 保证" >}}
{{< /metric-grid >}}

{{< alert type="info" >}}
这些数字基于 2024 年的第三方测试报告
{{< /alert >}}
```

### 示例2: API 文档

```markdown
## API 配额

{{< metric-grid >}}
{{< metric-card label="请求限制" value="10K/min" sub="免费版本" >}}
{{< metric-card label="响应时间" value="<200ms" sub="P99延迟" >}}
{{< metric-card label="可用性" value="99.95%" sub="月度保证" >}}
{{< /metric-grid >}}

{{< alert type="warning" >}}
**限制提升**: 高级用户可申请提升限额。[联系我们](mailto:support@example.com)
{{< /alert >}}

{{< alert type="danger" >}}
**重要**: API 密钥不要在客户端代码中暴露！
{{< /alert >}}
```

### 示例3: 技术文章

```markdown
## 性能提升成果

{{< metric-grid >}}
{{< metric-card label="内存占用" value="↓40%" sub="从 500MB 到 300MB" >}}
{{< metric-card label="加载时间" value="↓60%" sub="从 2s 到 800ms" >}}
{{< metric-card label="并发能力" value="↑300%" sub="从 100 到 300 并发" >}}
{{< /metric-grid >}}

{{< alert type="success" >}}
优化已在生产环境验证，所有用户自动受益
{{< /alert >}}

{{< alert type="info" >}}
详见 [性能优化报告](/reports/performance-2024/)
{{< /alert >}}
```

---

## 🔧 常见操作

### 修改 Shortcode 样式

编辑 `assets/css/custom.css`，找到相应的 CSS 块：

**Metric Card 样式**:
```css
.metric-card {
  /* 修改这里 */
  padding: 1.25rem;  /* 间距 */
  border: 1px solid var(--article-border);  /* 边框 */
}

.metric-card:hover {
  /* 修改悬停效果 */
  transform: translateY(-2px);
}
```

**Alert 样式**:
```css
.alert-info {
  /* 修改这里 */
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.05), rgba(0, 0, 0, 0));
  border-left-color: #0284c7;
}
```

### 添加新的 Alert 类型

1. 在 shortcode 中添加图标映射
2. 在 CSS 中添加新的 `.alert-type` 样式
3. 在文档中记录新类型

### 修改 Grid 列数

在 `assets/css/custom.css` 中修改 `grid-template-columns`:

```css
.metric-grid {
  /* 改为2列 */
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  
  /* 改为4列 */
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}
```

---

## ⚡ 快速技巧

### 📍 Markdown 在 Alert 中工作

```markdown
{{< alert type="info" >}}
# 标题也可以用

- **加粗**
- *斜体*  
- [链接](https://example.com)
- `代码`
{{< /alert >}}
```

### 🎨 组合使用

```markdown
{{< alert type="success" >}}
## 项目成果

{{< metric-grid >}}
{{< metric-card label="完成度" value="100%" sub="all tasks done" >}}
{{< metric-card label="质量分" value="A+" sub="code review" >}}
{{< /metric-grid >}}
{{< /alert >}}
```

### 📱 移动优化

Grid 会自动调整列数，无需做额外工作：
- 桌面 (>960px): 自动计算列数
- 平板 (600px-960px): 根据容器宽度调整
- 手机 (<600px): 自动堆叠为单列

### 🌙 深色主题

所有 shortcodes 自动适配深色主题，因为使用了 CSS 变量：
```css
color: var(--color-text);  /* 自动切换 */
background: var(--color-bg);  /* 自动切换 */
```

---

## 📚 完整文档

- **使用指南**: [shortcode-guide-2025.md](shortcode-guide-2025.md)
- **最佳实践**: [shortcode-best-practices.md](shortcode-best-practices.md)
- **测试清单**: [shortcode-testing-checklist.md](shortcode-testing-checklist.md)
- **模板库**: [shortcode-template-library.md](shortcode-template-library.md)

---

## 🆘 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| Shortcode 显示为原始文本 | Hugo 未找到模板 | 检查文件名和路径 |
| 样式不应用 | CSS 未编译 | 重启 Hugo 开发服务器 |
| 布局混乱 | CSS 冲突 | 清除浏览器缓存 |
| 内容未处理 | 缺少 `markdownify` | 查看 shortcode 实现 |

**更多帮助**: 查看[测试清单](shortcode-testing-checklist.md)中的调试部分

---

**最后更新**: 2025-12-19  
**快速导航**: [首页](../README.md) | [Hugo 配置](../config/_default/) | [所有文档](index.md)

