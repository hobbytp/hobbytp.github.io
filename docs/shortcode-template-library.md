# Shortcode 模板库

这个文件包含常用的 Shortcode 模板，可直接复制使用。

---

## 🎨 基础样式组件

### 1. 按钮组 (Button Group)

**文件**: `layouts/shortcodes/button-group.html`
```html
{{- /*
  按钮组件
  用法: {{< button-group >}}
         {{< button href="#" text="按钮1" style="primary" >}}
         {{< button href="#" text="按钮2" style="secondary" >}}
        {{< /button-group >}}
*/ -}}

<div class="button-group">
  {{ .Inner | markdownify }}
</div>
```

**CSS** (添加到 `assets/css/custom.css`):
```css
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.5rem 0;
}

.button-group a {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 0.25rem;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.button-group a.primary {
  background: var(--color-primary);
  color: white;
}

.button-group a.primary:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.button-group a.secondary {
  background: var(--color-secondary);
  color: var(--color-text);
  border: 1px solid var(--article-border);
}
```

---

### 2. 高亮文本框 (Highlight)

**文件**: `layouts/shortcodes/highlight.html`
```html
{{- /*
  高亮文本框
  用法: {{< highlight text="重要信息" >}}
*/ -}}

<div class="highlight-box">
  <span class="highlight-icon">💡</span>
  <span class="highlight-text">{{ .Get "text" }}</span>
</div>
```

**CSS**:
```css
.highlight-box {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(251, 191, 36, 0.1);
  padding: 0.25rem 0.75rem;
  border-left: 3px solid #fbbf24;
  border-radius: 0.25rem;
  color: var(--color-text);
}

.highlight-icon {
  font-size: 1.1em;
}
```

---

### 3. 统计框 (Stat Box)

**文件**: `layouts/shortcodes/stat-box.html`
```html
{{- /*
  单个统计框（比 metric-card 更简洁）
  用法: {{< stat-box number="42" label="项目完成" color="blue" >}}
*/ -}}

<div class="stat-box stat-box--{{ .Get "color" | default "blue" }}">
  <div class="stat-box__number">{{ .Get "number" }}</div>
  <div class="stat-box__label">{{ .Get "label" }}</div>
</div>
```

**CSS**:
```css
.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border-radius: 0.5rem;
  text-align: center;
  min-height: 120px;
}

.stat-box__number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.stat-box__label {
  font-size: 0.875rem;
  color: var(--color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-box--blue { background: rgba(59, 130, 246, 0.05); }
.stat-box--green { background: rgba(16, 185, 129, 0.05); }
.stat-box--red { background: rgba(239, 68, 68, 0.05); }
.stat-box--purple { background: rgba(139, 92, 246, 0.05); }
```

---

## 📊 信息展示组件

### 4. 对比表格 (Comparison Table)

**文件**: `layouts/shortcodes/comparison-row.html`
```html
{{- /*
  对比行（在对比表中使用）
  用法: {{< comparison-row item="方案A" pro="优势内容" con="劣势内容" >}}
*/ -}}

<tr>
  <td><strong>{{ .Get "item" }}</strong></td>
  <td><span class="comparison-pro">✓ {{ .Get "pro" }}</span></td>
  <td><span class="comparison-con">✗ {{ .Get "con" }}</span></td>
</tr>
```

**CSS**:
```css
.comparison-pro {
  color: #10b981;
  font-weight: 500;
}

.comparison-con {
  color: #ef4444;
  font-weight: 500;
}
```

---

### 5. 时间线 (Timeline)

**文件**: `layouts/shortcodes/timeline-item.html`
```html
{{- /*
  时间线项目
  用法: {{< timeline-item date="2024年1月" title="里程碑" >}}描述内容{{< /timeline-item >}}
*/ -}}

<div class="timeline-item">
  <div class="timeline-marker"></div>
  <div class="timeline-content">
    <div class="timeline-date">{{ .Get "date" }}</div>
    <h4 class="timeline-title">{{ .Get "title" }}</h4>
    <div class="timeline-text">
      {{ .Inner | markdownify }}
    </div>
  </div>
</div>
```

**CSS**:
```css
.timeline-item {
  display: flex;
  margin-bottom: 2rem;
  position: relative;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  background: var(--color-primary);
  border-radius: 50%;
  margin-top: 0.5rem;
  margin-right: 1.5rem;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 24px;
  width: 2px;
  height: calc(100% + 1rem);
  background: var(--article-border);
}

.timeline-content {
  flex: 1;
}

.timeline-date {
  font-size: 0.875rem;
  color: var(--color-secondary);
  font-weight: 500;
}

.timeline-title {
  margin: 0.25rem 0 0.5rem;
  color: var(--color-heading);
}

.timeline-text {
  color: var(--color-text);
  line-height: 1.6;
}
```

---

## 💻 代码展示组件

### 6. 代码选项卡 (Code Tabs)

**文件**: `layouts/shortcodes/code-tabs.html`
```html
{{- /*
  代码选项卡容器
  用法: {{< code-tabs >}}
         {{< code-tab lang="python" >}}code{{< /code-tab >}}
         {{< code-tab lang="js" >}}code{{< /code-tab >}}
        {{< /code-tabs >}}
*/ -}}

<div class="code-tabs">
  {{ .Inner | markdownify }}
</div>
```

**文件**: `layouts/shortcodes/code-tab.html`
```html
{{- /*
  单个代码标签
*/ -}}
<div class="code-tab code-tab--{{ .Get "lang" }}">
  <div class="code-tab__label">{{ .Get "lang" | upper }}</div>
  <pre><code>{{ .Inner }}</code></pre>
</div>
```

**CSS**:
```css
.code-tabs {
  position: relative;
  margin: 1.5rem 0;
  border: 1px solid var(--article-border);
  border-radius: 0.5rem;
  overflow: hidden;
}

.code-tab {
  display: none;
}

.code-tab:first-child {
  display: block;
}

.code-tab__label {
  background: var(--color-secondary);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.code-tab pre {
  margin: 0;
  overflow-x: auto;
}

.code-tab code {
  background: var(--color-bg);
  padding: 1rem;
  display: block;
  font-family: monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}
```

---

## 📝 表单和交互组件

### 7. 可折叠内容 (Collapsible)

**文件**: `layouts/shortcodes/collapsible.html`
```html
{{- /*
  可折叠内容块
  用法: {{< collapsible title="点击查看更多" >}}内容{{< /collapsible >}}
*/ -}}

<details class="collapsible">
  <summary class="collapsible__summary">
    <span>{{ .Get "title" }}</span>
    <span class="collapsible__icon">▼</span>
  </summary>
  <div class="collapsible__content">
    {{ .Inner | markdownify }}
  </div>
</details>
```

**CSS**:
```css
.collapsible {
  margin: 1rem 0;
  border: 1px solid var(--article-border);
  border-radius: 0.25rem;
  overflow: hidden;
}

.collapsible__summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--color-secondary);
  cursor: pointer;
  user-select: none;
}

.collapsible__summary:hover {
  background: rgba(var(--color-secondary-rgb), 0.8);
}

.collapsible__icon {
  display: inline-block;
  transition: transform 0.3s ease;
}

.collapsible[open] .collapsible__icon {
  transform: rotate(180deg);
}

.collapsible__content {
  padding: 1rem;
  background: var(--color-bg);
  border-top: 1px solid var(--article-border);
}
```

---

## 🎯 快速参考

| 组件 | 难度 | 维护成本 | 建议度 |
|------|------|---------|-------|
| button-group | ⭐ 简单 | 低 | ⭐⭐⭐⭐⭐ |
| highlight | ⭐ 简单 | 低 | ⭐⭐⭐⭐ |
| stat-box | ⭐ 简单 | 低 | ⭐⭐⭐⭐⭐ |
| comparison-row | ⭐⭐ 中等 | 中 | ⭐⭐⭐⭐ |
| timeline | ⭐⭐ 中等 | 中 | ⭐⭐⭐⭐ |
| code-tabs | ⭐⭐⭐ 复杂 | 高 | ⭐⭐⭐ |
| collapsible | ⭐⭐ 中等 | 低 | ⭐⭐⭐⭐ |

---

**提示**: 从简单的开始实施，逐步添加复杂组件。每个新的 shortcode 都需要在文档中添加说明和示例。

