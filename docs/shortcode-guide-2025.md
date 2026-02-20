# Shortcode 使用指南

## 已创建的新 Shortcodes

### 1. **metric-card** - 指标卡片

用于展示单个指标（如模型参数、性能数据等）。

**用法：**
```markdown
{{< metric-card label="标签文本" value="值" sub="子文本描述" >}}
```

**示例：**
```markdown
{{< metric-card label="MiMo-V2-Flash (Agent)" value="309B" sub="总参数量 / 激活15B" >}}
```

**参数：**
- `label` - 卡片标签（小字）
- `value` - 主要显示值（大字）
- `sub` - 子文本描述（小字）

---

### 2. **metric-grid** - 指标网格

用于组织多个 metric-card 成网格布局。

**用法：**
```markdown
{{< metric-grid >}}
{{< metric-card label="标签1" value="值1" sub="描述1" >}}
{{< metric-card label="标签2" value="值2" sub="描述2" >}}
{{< metric-card label="标签3" value="值3" sub="描述3" >}}
{{< /metric-grid >}}
```

**特点：**
- 响应式设计，自动调整列数
- 支持无限数量的卡片
- 支持鼠标悬停效果

---

### 3. **alert** - 警告/提示框

用于显示重要信息、提示或警告。

**用法：**
```markdown
{{< alert type="info" >}}
内容支持 **Markdown** 格式
{{< /alert >}}
```

**支持的类型：**
- `info` - 信息提示（蓝色）
- `success` - 成功提示（绿色）
- `warning` - 警告提示（橙色）
- `danger` - 危险提示（红色）

**示例：**
```markdown
{{< alert type="success" >}}
**核心洞察**：小米不仅关注模型参数的堆砌...
{{< /alert >}}
```

---

## CSS 样式

所有 shortcode 样式已添加到 `assets/css/custom.css`，包括：

- 响应式网格布局
- 深色主题支持
- 悬停动画效果
- Font Awesome 图标集成

---

## 实际应用示例

查看完整示例：[xiaomi_models_2025.md](../../content/zh/companies/xiaomi/xiaomi_models_2025.md)

---

## 扩展建议

如需添加更多 shortcode，可参考现有的模式：

1. 在 `layouts/shortcodes/` 创建 `.html` 文件
2. 在 `assets/css/custom.css` 添加对应样式
3. 更新此指南说明用法

