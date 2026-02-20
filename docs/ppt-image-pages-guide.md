# 在 Hugo（PaperMod）里展示 PPT（每页图片）最佳方案

你更在意“最清晰的细节”，推荐：**图片讲义模式（方案 A）+ WebP + 两档清晰度 srcset + 点击打开高清图**。

本项目已新增 shortcode：`ppt-pages`（文件：`layouts/shortcodes/ppt-pages.html`）。

---

## 1. 推荐目录结构（Page Bundle）

把一篇文章做成 Page Bundle，图片放在同目录的 `ppt/` 下：

```
content/zh/posts/my-ppt/index.md
content/zh/posts/my-ppt/ppt/001.webp
content/zh/posts/my-ppt/ppt/002.webp
...
content/zh/posts/my-ppt/ppt/015.webp
```

说明：
- 必须是 `index.md`（Page Bundle），这样 `.Page.Resources.Match` 才能找到图片。
- 文件名建议 `001.webp` 这种，确保排序稳定。

---

## 2. 文章里怎么写

在 `index.md` 正文中插入：

```md
## PPT 讲义（图片）

{{< ppt-pages dir="ppt" >}}
```

默认参数（清晰优先）：
- `w1=1800`（文章内常规显示）
- `w2=3000`（点击打开高清图 & srcset 高分辨率）
- `q=95`（webp 质量）
- `caption=true`

如果你希望更“极致清晰”，可以提高到：

```md
{{< ppt-pages dir="ppt" w1="2200" w2="3600" q="96" >}}
```

---

## 3. 为什么这样做最适合“清晰优先”

- 页面内默认加载 `w1` 尺寸：清晰且不会过重。
- `srcset` + `sizes`：高 DPI 设备会自动拿更清晰的资源。
- 点击图片会打开 `w2` 高清版本：看细节时不糊。
- `loading="lazy"`：不会一次性把 15 页全拉下来。

---

## 4. PNG 转 WebP：怎么选参数（清晰优先）

建议策略：
- 先用 **WebP 有损（q 92~96）**，一般对 PPT 文本/线条也很干净。
- 如果出现“文字边缘发糊/色带”，尝试：
  - 把 `q` 提到 `96~98`
  - 或改用 **WebP 无损**（体积会大很多，不一定划算）

实践建议：
- 你 15 页、PDF 20MB：通常导出为 WebP 后，总体积有机会显著下降，同时保持足够清晰。

---

## 5. PDF 作为备选/补充（强烈建议）

虽然你更在意清晰，但如果你也在意“可搜索/可复制”，建议：

- 页面顶部放 PDF：

```md
{{< pdf src="/pdf/my-ppt.pdf" title="演示文稿" height="800px" >}}
```

- 下面再放图片讲义：

```md
{{< ppt-pages dir="ppt" >}}
```

这样：
- 想看细节：看图片/点开高清。
- 想检索：用 PDF。

---

## 6. 常见问题

### Q1：为什么 shortcode 提示找不到图片？
- 你需要把文章做成 Page Bundle：`index.md` + 同目录图片。
- 图片必须放在 `dir` 指定目录里（默认 `ppt/`）。

### Q2：我图片不是 webp，是 png/jpg 可以吗？
可以。shortcode 会匹配 `webp/png/jpg/jpeg`。

### Q3：如何隐藏“第 N 页”标题？

```md
{{< ppt-pages dir="ppt" caption="false" >}}
```

---

## 7. 建议你现在就这么做（最短路径）

1) 把 PDF 的 15 页导出为 `001.webp~015.webp`，放进 `content/zh/posts/<slug>/ppt/`
2) 正文插入 `{{< ppt-pages dir="ppt" >}}`
3) `make dev` 预览，手机/桌面都看看
4) 如觉得不够清晰：改 `w1/w2/q` 参数
