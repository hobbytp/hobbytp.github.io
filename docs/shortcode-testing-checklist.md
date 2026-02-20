# Shortcode 测试检查清单

用这个清单来验证你的 shortcodes 是否工作正常。

---

## ✅ 实施前检查

- [ ] 已创建 `layouts/shortcodes/shortcode-name.html` 文件
- [ ] Shortcode 模板语法正确（`{{ .Get "param" }}`, `.Inner`, `markdownify`）
- [ ] 文件编码为 UTF-8（无 BOM）
- [ ] 没有多余的空格或换行

---

## ✅ CSS 样式检查

- [ ] 样式已添加到 `assets/css/custom.css`
- [ ] 使用了 CSS 变量（`var(--color-primary)`, `var(--article-border)` 等）
- [ ] 响应式设计已考虑（使用媒体查询）
- [ ] 深色主题兼容（使用 `[data-theme="dark"]` 选择器）
- [ ] CSS 文件总大小 < 1000 行

---

## ✅ 功能测试

### 本地开发测试

```bash
# 1. 启动开发服务器
make dev

# 2. 访问包含 shortcode 的页面
# http://localhost:1313/zh/path/to/article/

# 3. 打开浏览器控制台检查错误
# 按 F12，查看 Console 和 Network 选项卡
```

### 单个 Shortcode 测试

#### 测试项目

- [ ] **参数传递**: 所有参数都正确显示
- [ ] **内容渲染**: `.Inner` 内容被正确处理
- [ ] **Markdown 支持**: 内容中的 Markdown 格式正确转换（如果使用了 `markdownify`）
- [ ] **HTML 结构**: 生成的 HTML 结构符合预期
- [ ] **CSS 应用**: 样式类正确应用且外观符合设计

### 响应式设计测试

```markdown
在浏览器中测试不同的屏幕尺寸：

1. **桌面** (1920x1080)
   - 元素布局是否正确
   - 文字可读性如何

2. **平板** (768x1024)
   - 元素是否自适应宽度
   - 间距是否合适

3. **手机** (375x667)
   - 是否正确堆叠
   - 是否仍然可用
   - 点击目标大小是否≥44px
```

### 浏览器兼容性测试

- [ ] Chrome/Edge (最新版)
- [ ] Firefox (最新版)
- [ ] Safari (最新版)
- [ ] Mobile Chrome (最新版)
- [ ] Mobile Safari (最新版)

---

## ✅ 主题测试

### 浅色主题

1. 导航到任何包含 shortcode 的页面
2. 观察：
   - [ ] 文字可读性好
   - [ ] 背景与文字对比度充分（WCAG AA 标准）
   - [ ] 图标清晰可见
   - [ ] 边框/阴影适当

### 深色主题

1. 点击主题切换按钮或使用 CSS 变量覆盖
2. 观察：
   - [ ] 颜色自动反转
   - [ ] 背景变深，文字变亮
   - [ ] 所有元素仍然可见
   - [ ] 无硬编码的颜色冲突

**测试深色模式的 CSS**:
```css
/* 在浏览器控制台中运行 */
document.documentElement.setAttribute('data-theme', 'dark');
```

---

## ✅ 内容测试

### 参数验证

测试边界情况：

```markdown
# 1. 空参数
{{< metric-card label="" value="100" sub="测试" >}}

# 2. 长文本参数
{{< metric-card label="这是一个非常长的标签用来测试文字包装" value="很长的值" sub="非常长的说明文字用来测试是否正确处理" >}}

# 3. 特殊字符
{{< metric-card label="价格 & 成本" value="$1,000" sub="中文 & English" >}}

# 4. HTML/脚本注入（安全测试）
{{< metric-card label="<script>alert('test')</script>" value="test" sub="test" >}}
```

### 嵌套内容测试

```markdown
{{< metric-grid >}}
{{< metric-card label="卡片1" value="值1" sub="说明1" >}}
{{< metric-card label="卡片2" value="值2" sub="说明2" >}}

# 测试是否支持多行
{{< metric-card label="卡片3" value="值3" sub="说明3" >}}
{{< /metric-grid >}}
```

---

## ✅ 性能测试

### 页面加载性能

```bash
# 使用 Hugo 的构建统计
make build

# 检查输出中是否有错误或警告
# 应该看到类似的信息：
# total in 1234 ms
```

### CSS 文件大小

```bash
# 检查编译后的 CSS 大小
ls -lh public/assets/css/

# 应该 < 100KB（未压缩）
# < 20KB（gzip）
```

### 渲染性能

1. 打开包含多个 shortcode 的页面
2. 打开 DevTools → Performance 标签
3. 记录一段页面交互
4. 检查：
   - [ ] FCP (First Contentful Paint) < 1.8s
   - [ ] LCP (Largest Contentful Paint) < 2.5s
   - [ ] CLS (Cumulative Layout Shift) < 0.1
   - [ ] 无 "long tasks"（超过 50ms）

---

## ✅ 文档检查

- [ ] shortcode 在 `docs/shortcode-guide-2025.md` 中有文档
- [ ] 包含清晰的用法说明
- [ ] 有工作的代码示例
- [ ] 参数都有说明
- [ ] 说明了参数是否必选/可选

---

## ✅ 构建验证

### Hugo 构建成功

```bash
# 清除缓存并重新构建
make clean
make build

# 应该没有错误（虽然可能有警告）
# 输出应该包含: "Total in XXms"
```

### 部署前检查

```bash
# 1. 删除 public 文件夹
rm -rf public/

# 2. 进行完整构建
hugo --minify --configDir=config

# 3. 检查生成的 HTML
grep -r "shortcode" public/ | head -10
# 应该看不到 shortcode 标记，只有生成的 HTML

# 4. 验证 CSS 加载
grep -r "metric-card" public/ | grep -i ".css"
# 应该显示 CSS 类在编译的 CSS 文件中
```

---

## 🐛 调试技巧

### 查看 Shortcode 原始输出

在浏览器控制台中检查 HTML：

```javascript
// 查找所有 metric-card 元素
document.querySelectorAll('.metric-card').forEach(el => {
  console.log(el.outerHTML);
});
```

### Shortcode 不渲染

**症状**: 页面显示 `{{< metric-card ... >}}` 的原始文本

**检查清单**:
1. 检查文件是否在 `layouts/shortcodes/` 目录中
2. 文件名是否正确（无大小写问题）
3. 是否重启了 Hugo 开发服务器
4. 文件编码是否为 UTF-8

### CSS 不应用

**症状**: HTML 结构正确，但没有样式

**检查清单**:
1. CSS 类名是否拼写正确
2. CSS 是否添加到了 `assets/css/custom.css` 中
3. Hugo 是否重新编译了 CSS
4. 浏览器缓存是否清除（Ctrl+Shift+R）

### 响应式不工作

**症状**: 在手机上看不到媒体查询效果

**检查清单**:
1. 是否使用了 `@media` 查询
2. 视口元标签是否正确
3. 是否在移动设备上实际测试（不仅仅是浏览器缩放）

---

## 📋 测试用例模板

复制这个模板创建新的测试：

```markdown
## 测试: [Shortcode名称] - [功能描述]

**目标**: 验证 [具体功能]

**前置条件**:
- 已启动 Hugo 开发服务器
- 已打开 http://localhost:1313

**测试步骤**:
1. [第一步]
2. [第二步]
3. [验证步骤]

**预期结果**:
- [ ] [验证点1]
- [ ] [验证点2]
- [ ] [验证点3]

**实际结果**:
[记录你看到的情况]

**通过/失败**: ☐ 通过 ☐ 失败

**备注**:
[任何额外的观察或问题]
```

---

## 🔄 持续验证

每次编辑 shortcode 或 CSS 时：

1. ✅ 运行 `make dev`
2. ✅ 访问测试页面
3. ✅ 按 F12 检查控制台是否有错误
4. ✅ 验证桌面/平板/手机视图
5. ✅ 测试浅色和深色主题
6. ✅ 运行 `make build` 验证生产构建
7. ✅ 提交前检查本清单

---

**最后更新**: 2025-12-19  
**维护者**: Hugo Blog Team

