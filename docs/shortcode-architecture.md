# Shortcode 系统架构

Shortcode 组件系统的完整技术架构文档。

---

## 🏗️ 系统架构图

```
Hugo Content System
│
├─ 📄 Markdown Content
│  └─ (content/zh/, content/en/)
│
├─ 🎨 Shortcodes (layouts/shortcodes/)
│  ├─ metric-grid.html      ← 响应式网格容器
│  ├─ metric-card.html      ← 单个卡片组件
│  └─ alert.html            ← 警告/提示框
│
├─ 🎭 CSS Styling (assets/css/)
│  └─ custom.css            ← 所有样式 (1140-1195 行)
│
└─ 🌐 Generated HTML (public/)
   └─ articles/             ← 编译后的网页
```

---

## 📊 数据流

```
1. 用户编写 Markdown
   ↓
   {{< metric-grid >}}
   {{< metric-card label="..." value="..." sub="..." >}}
   {{< /metric-grid >}}
   ↓
2. Hugo 处理 Shortcodes
   ↓
   metric-grid.html
   ├─ 读取 .Inner 内容
   ├─ 应用 markdownify
   └─ 包装成 <div class="metric-grid">
   ↓
   metric-card.html
   ├─ 读取参数 (.Get "label" 等)
   ├─ 构建 HTML 结构
   └─ 应用样式类名
   ↓
3. 应用样式
   ↓
   custom.css
   ├─ .metric-grid { display: grid; ... }
   ├─ .metric-card { flex-direction: column; ... }
   └─ .metric-card:hover { transform: ... }
   ↓
4. 生成最终 HTML
```

---

## 🔄 Shortcode 处理流程

### 嵌套 Shortcode 的处理顺序

```
输入 Markdown:
{{< metric-grid >}}
  {{< metric-card label="A" value="1" sub="sub" >}}
  {{< metric-card label="B" value="2" sub="sub" >}}
{{< /metric-grid >}}

处理步骤:
1. Hugo 解析最内层的 shortcode
   → metric-card.html 处理
   → 生成: <div class="metric-card">...</div>
   
2. Hugo 处理下一层
   → 内容现在是生成的 HTML
   → metric-grid.html 的 .Inner = 两个 metric-card 元素
   
3. markdownify 过滤器
   → 对字符串内容应用 Markdown 处理
   → HTML 标签被保留
   
4. 最终输出
   → <div class="metric-grid">
       <div class="metric-card">...</div>
       <div class="metric-card">...</div>
     </div>
```

---

## 💾 文件位置和责任

```
layouts/shortcodes/
├─ metric-grid.html
│  ├─ 职责: 提供网格容器和响应式布局
│  ├─ 输入: .Inner (嵌套内容)
│  ├─ 输出: <div class="metric-grid">{{ .Inner }}</div>
│  └─ 依赖: metric-card 模板
│
├─ metric-card.html
│  ├─ 职责: 渲染单个数据卡片
│  ├─ 输入: label, value, sub 参数
│  ├─ 输出: <div class="metric-card">...</div>
│  └─ 依赖: CSS 类 .metric-card
│
└─ alert.html
   ├─ 职责: 渲染不同类型的警告框
   ├─ 输入: type (info/success/warning/danger) 和内容
   ├─ 输出: <div class="alert alert-{{ type }}">...</div>
   └─ 依赖: CSS 类 .alert-*

assets/css/custom.css
├─ 行数范围: 1140-1195
├─ 职责: 提供所有 shortcode 的样式
├─ 内容:
│  ├─ .metric-grid { display: grid; ... }
│  ├─ .metric-card { ... }
│  ├─ .metric-card:hover { ... }
│  ├─ .alert { ... }
│  ├─ .alert-info { ... }
│  ├─ .alert-success { ... }
│  ├─ .alert-warning { ... }
│  └─ .alert-danger { ... }
└─ 依赖: CSS 自定义属性
```

---

## 🎨 CSS 变量系统

### 使用的 CSS 变量

```css
/* 颜色系统 */
--color-primary      /* 主要强调色 */
--color-secondary    /* 次要强调色 */
--color-text         /* 文本颜色 */
--color-bg           /* 背景颜色 */
--color-heading      /* 标题颜色 */
--article-border     /* 边框颜色 */

/* 深色主题覆盖 */
[data-theme="dark"] {
  --color-text: #e0e0e0;
  --color-bg: #1e1e1e;
  --article-border: rgba(255, 255, 255, 0.1);
}
```

### 变量继承链

```
全局 CSS 变量 (在主题中定义)
  ↓
PaperMod 主题默认值
  ↓
custom.css 中的组件样式
  ↓
具体的 shortcode 样式覆盖
```

---

## 📱 响应式设计架构

```
Metric Grid 响应式策略:

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

自动适配:
Desktop (>960px):    3 列 (网格自动计算)
          ↓
          [Card]  [Card]  [Card]

Tablet (600-960px):  2 列
          ↓
          [Card]  [Card]
          [Card]

Mobile (<600px):     1 列 (auto-fit 单列堆叠)
          ↓
          [Card]
          [Card]
          [Card]
```

### 关键特性

- **auto-fit**: 列数自动调整，无需媒体查询
- **minmax()**: 最小宽度 220px，最大 1fr（均分）
- **gap**: 一致的间距
- **flex 备选**: 旧浏览器退化为竖向堆叠

---

## 🔌 参数传递机制

### Shortcode 参数处理

```
用户 Markdown:
{{< metric-card label="用户量" value="1M+" sub="月活跃用户" >}}
       ↓
Hugo 解析参数
       ↓
metric-card.html 中:
{{ .Get "label" }}    → "用户量"
{{ .Get "value" }}    → "1M+"
{{ .Get "sub" }}      → "月活跃用户"
       ↓
生成 HTML
<div class="metric-card">
  <div class="metric-label">用户量</div>
  <div class="metric-value">1M+</div>
  <div class="metric-sub">月活跃用户</div>
</div>
```

### 参数验证

```
Alert Shortcode 的参数验证:

{{< alert type="info" >}}
       ↓
Hugo 获取 type 参数
       ↓
alert.html 中:
{{ $type := .Get "type" }}
       ↓
条件判断:
{{ if eq $type "info" }}
  {{ $icon := "fa-circle-info" }}
{{ else if eq $type "success" }}
  {{ $icon := "fa-circle-check" }}
...

生成对应的 icon 和样式类
```

---

## 🔐 安全考虑

### 输入处理

```
两层安全处理:

1. Hugo 的原生处理
   - 自动 HTML 转义（除非明确允许）
   - 参数值自动清理

2. Shortcode 中的处理
   .Inner | markdownify
   ↓
   - 允许 Markdown 处理
   - 但 HTML 标签被清理或转义
   - 脚本标签会被移除

示例:
输入: <script>alert('xss')</script>
输出: &lt;script&gt;alert('xss')&lt;/script&gt;
```

### 推荐实践

```
✅ 安全的:
{{< alert type="info" >}}
**用户输入**: {{ .Params.user_input | safeHTML }}
{{< /alert >}}

❌ 不安全的:
{{ .Params.user_input }}  <!-- 信任用户输入 -->
```

---

## 🚀 渲染优化

### Hugo 编译优化

```
开发模式 (make dev):
- 不缩小 CSS
- 快速编译
- 包含草稿内容
- 启用 livereload

生产模式 (make build):
- 最小化 CSS/HTML/JS
- 指纹识别资源
- 移除源映射
- 启用缓存控制
```

### 加载性能

```
资源加载顺序:

HTML 页面加载
  ↓
解析 <link rel="stylesheet" href="style.css">
  ↓
下载和解析 custom.css (包含 shortcode 样式)
  ↓
应用样式到 metric-card, alert 等元素
  ↓
渲染完成
```

---

## 🧩 扩展性设计

### 添加新 Shortcode 的最小步骤

```
1. 创建 layouts/shortcodes/new-component.html
   {{- /* 模板代码 */ -}}
   
2. 添加样式到 assets/css/custom.css
   .new-component { /* 样式 */ }
   
3. 测试: make dev
   
4. 使用: {{< new-component param="value" >}}

完整架构会自动处理:
✅ 参数传递
✅ 内容处理
✅ 样式应用
✅ 主题适配
```

### 接口兼容性

```
所有 shortcodes 遵循统一接口:

模板 API:
{{< shortcode-name param1="value" param2="value" >}}
  可选的嵌套内容
{{< /shortcode-name >}}

可用的 Hugo 函数:
- .Get "paramName"        获取参数
- .Inner                   获取内部内容
- .Inner | markdownify    处理 Markdown
- .Get "default" "fallback" 带默认值
```

---

## 📈 性能指标

### 典型性能数据

```
单页面渲染:

- Hugo 构建时间: ~200-500ms
- CSS 编译: ~100-200ms
- 页面加载: ~800ms (首次) / ~200ms (缓存)
- FCP (First Contentful Paint): <1.8s
- LCP (Largest Contentful Paint): <2.5s

3 个 metric-card 的内存占用: ~5KB HTML + 2KB CSS
```

### 优化建议

```
✅ 已优化的:
- CSS 变量减少重复代码
- Grid 布局比 flex 更高效
- 无 JavaScript 依赖
- 最小化 HTML 标签

🔄 可优化的:
- 考虑 CSS-in-JS (如果添加更多动态样式)
- 预加载关键字体
- 延迟加载非关键 CSS
```

---

## 🔍 调试路径

### 排查 Shortcode 问题

```
问题: Shortcode 不渲染

检查清单:
1. 文件位置: layouts/shortcodes/*.html ✓
2. 文件名: 使用 kebab-case (my-component) ✓
3. Hugo 服务器: 已重启? ✓
4. 文件编码: UTF-8 无 BOM ✓
5. 语法: {{< name >}}...{{< /name >}} ✓

调试步骤:
make clean
make dev
# 查看终端输出，找 ERROR
# 在浏览器打开 http://localhost:1313
# 按 F12 查看 HTML 源代码
```

### 排查样式问题

```
问题: Shortcode HTML 正确，但样式不显示

检查清单:
1. CSS 在 custom.css 中? ✓
2. 类名拼写正确? ✓
3. Hugo 重新编译 CSS? make clean && make dev ✓
4. 浏览器缓存: Ctrl+Shift+R ✓
5. CSS 优先级: 是否被其他样式覆盖? ✓

调试步骤:
1. 打开 DevTools → Elements
2. 选择 shortcode 元素
3. 查看 Styles 面板
4. 搜索应该应用的 CSS 类
5. 检查是否被斜划线标记 (被覆盖)
```

---

## 📚 相关文档

| 文档 | 用途 | 读者 |
|------|------|------|
| [快速参考](shortcode-quick-reference.md) | 日常使用速查 | 内容创作者 |
| [最佳实践](shortcode-best-practices.md) | 设计指南 | 开发者 |
| [使用指南](shortcode-guide-2025.md) | 详细用法 | 初学者 |
| [测试清单](shortcode-testing-checklist.md) | 验证步骤 | QA/开发者 |
| [模板库](shortcode-template-library.md) | 代码模板 | 开发者 |
| **本文档** | 技术架构 | 架构师/高级开发者 |

---

## 🎓 学习路径

### 初级 (内容创作者)

1. 阅读 [快速参考](shortcode-quick-reference.md)
2. 复制粘贴例子到你的文章
3. 运行 `make dev` 预览
4. 完成！

### 中级 (博客维护者)

1. 理解 [最佳实践](shortcode-best-practices.md)
2. 学习如何修改样式
3. 阅读 [测试清单](shortcode-testing-checklist.md)
4. 验证你的更改

### 高级 (主题开发者)

1. 深入研究本架构文档
2. 查看 [模板库](shortcode-template-library.md)
3. 创建新的 shortcode
4. 扩展系统功能

---

## ✅ 检查清单

这个架构被认为是完整的，当:

- [ ] 所有文件在正确的位置
- [ ] Shortcodes 能正确渲染
- [ ] CSS 正确应用
- [ ] 主题切换工作正常
- [ ] 响应式设计工作正常
- [ ] 文档完整
- [ ] 测试通过

---

**最后更新**: 2025-12-19  
**架构版本**: v1.0  
**维护者**: Hugo Blog Team

