# Hugo Blog PDF Exporter

将Hugo博客文章导出为高质量PDF，支持离线阅读和分享。

## 功能特性

- 📄 **高质量PDF**: 基于Playwright的HTML到PDF转换
- 🎨 **保持样式**: 保留原始文章的样式和布局
- 📱 **响应式优化**: 针对PDF阅读优化的布局
- 🔄 **批量导出**: 支持批量导出整个博客
- 📖 **离线阅读**: 生成适合离线阅读的PDF格式
- 🎯 **自定义样式**: 支持PDF专用样式优化

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 基本用法

### 前置条件

确保Hugo开发服务器正在运行：

```bash
make dev  # 或者 hugo server -D
```

### 1. 导出单个文章

```bash
python pdf_exporter.py --article content/zh/posts/my-article.md
```

### 2. 批量导出所有文章

```bash
python pdf_exporter.py --all
```

### 3. 自定义输出目录和格式

```bash
python pdf_exporter.py --all \
  --output-dir ./pdf-exports \
  --format A4 \
  --quality 95
```

## Make命令使用

### 导出所有文章

```bash
make export-pdf
```

### 导出单个文件

```bash
make export-pdf FILE=./content/zh/google/a2a.md
```

### 批量导出（限制数量）

```bash
python pdf_exporter.py --all --limit 3
```

## 命令行选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--input-dir DIR` | 输入目录 | `content` |
| `--output-dir DIR` | 输出目录 | `pdf-exports` |
| `--article PATH` | 导出单个文章 | - |
| `--all` | 导出所有文章 | - |
| `--serve-url URL` | Hugo服务器URL | `http://localhost:1313` |
| `--format FORMAT` | PDF格式 (A4/Letter/Legal) | `A4` |
| `--quality QUAL` | 图片质量 (1-100) | `90` |
| `--include-toc` | 包含目录 | - |
| `--batch-size N` | 批量处理大小 | `5` |

## 输出结果

### 文件结构

```
pdf-exports/
├── zh_posts_my-article.pdf
├── zh_projects_ai_tool.pdf
├── pdf-export-report.md
└── ...
```

### 导出报告示例

```
# Hugo博客PDF导出报告

生成时间: 2025-10-31 23:45:00

## 📊 导出统计

- **总文章数**: 156
- **成功导出**: 152
- **导出失败**: 4
- **成功率**: 97.4%

## 📁 输出目录

PDF文件已保存到: `pdf-exports/`

## ✅ 成功导出的文章

- **ai-trends-2025.md**
  - PDF: zh_posts_ai-trends-2025.pdf
  - URL: http://localhost:1313/zh/posts/ai-trends-2025/

- **deepseek-analysis.md**
  - PDF: zh_posts_deepseek-analysis.pdf
  - URL: http://localhost:1313/zh/posts/deepseek-analysis/
```

## PDF特性

### 样式优化

- **打印友好**: 针对A4纸张优化的边距和布局
- **导航隐藏**: 自动隐藏网站导航栏和页脚
- **内容居中**: 优化文章内容在PDF中的显示
- **分页控制**: 智能处理标题和段落的分页

### 图片处理

- **质量保持**: 高质量图片导出 (默认90%)
- **尺寸适配**: 自动适配PDF页面宽度
- **格式支持**: 支持所有Web图片格式

### 链接处理

- **外部链接**: 在PDF中保留可点击的链接
- **内部链接**: 转换为PDF内部引用
- **链接样式**: 打印友好的链接显示

## 集成到Hugo工作流

### Makefile集成

```makefile
# PDF导出
export-pdf:
    @echo "📄 导出PDF..."
    @cd tools/pdf-exporter && $(PYTHON_CMD) pdf_exporter.py --all

# 包含PDF导出的完整构建
full-publish: build export-pdf
    @echo "📚 完整发布流程完成"
```

### GitHub Actions集成

```yaml
- name: Export PDFs
  run: |
    # 启动Hugo服务器
    hugo server -D --port 1313 &
    sleep 10

    # 导出PDF
    cd tools/pdf-exporter
    python pdf_exporter.py --all --serve-url http://localhost:1313
```

## 高级用法

### 自定义PDF样式

修改 `pdf_exporter.py` 中的 `inject_pdf_styles` 方法：

```python
async def inject_pdf_styles(self, page: Page):
    custom_css = """
    @media print {
        /* 你的自定义样式 */
        .custom-header {
            font-size: 24pt;
            color: #333;
        }
    }
    """
    await page.add_style_tag(content=custom_css)
```

### 大批量导出优化

对于大型博客，建议分批处理：

```bash
# 分批导出，每批10篇文章
python pdf_exporter.py --all --batch-size 10

# 仅导出特定分类
find content/zh/posts -name "*.md" | head -20 | \
  xargs -I {} python pdf_exporter.py --article {}
```

## 故障排除

### 常见问题

1. **"连接被拒绝"**

   ```bash
   # 确保Hugo服务器正在运行
   curl http://localhost:1313
   ```

2. **"页面加载失败"**

   ```bash
   # 检查文章URL是否正确
   python pdf_exporter.py --article content/zh/posts/test.md
   ```

3. **"Playwright未安装"**

   ```bash
   playwright install chromium
   ```

4. **内存不足**

   ```bash
   # 减少批量大小
   python pdf_exporter.py --all --batch-size 3
   ```

5. **PDF质量问题**

   ```bash
   # 提高图片质量
   python pdf_exporter.py --all --quality 95
   ```

## 性能优化

- **并发处理**: 默认批量处理，避免服务器过载
- **资源缓存**: 浏览器实例复用，减少启动时间
- **智能等待**: 等待页面和资源完全加载
- **内存管理**: 分批处理，控制内存使用

## 使用场景

### 离线阅读

- 生成PDF版本供离线阅读
- 适合移动设备和Kindle等设备
- 保留文章的完整格式和链接

### 内容分享

- 分享文章的PDF版本
- 适合打印和存档
- 保持专业的出版质量

### 内容备份

- 创建博客内容的PDF备份
- 确保内容的可访问性
- 支持长期保存

## 许可证

MIT License
