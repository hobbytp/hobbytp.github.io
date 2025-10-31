# Hugo Blog Image Optimizer

自动优化Hugo博客中的图片，提升网站性能和用户体验。

## 功能特性

- 🖼️ **多格式支持**: 支持 JPEG、PNG、GIF、BMP、TIFF 等常见格式
- 🗜️ **智能压缩**: 使用 WebP 格式大幅减少文件大小
- 📱 **响应式图片**: 自动生成多尺寸图片 (320px, 640px, 960px, 1280px, 1920px)
- 🔄 **批量处理**: 支持目录递归扫描和多线程处理
- 💾 **智能备份**: 可选保留原始文件备份
- 🎯 **Hugo集成**: 生成兼容 Hugo 的图片配置

## 安装依赖

```bash
pip install -r requirements.txt
```

## 基本用法

### 1. 优化 static/images 目录中的所有图片

```bash
python image_optimizer.py
```

### 2. 自定义输入输出目录

```bash
python image_optimizer.py --input-dir static/images --output-dir static/images/optimized
```

### 3. 调整图片质量和尺寸

```bash
python image_optimizer.py --quality 90 --sizes 480 768 1024 1440
```

### 4. 预览模式（不实际执行）

```bash
python image_optimizer.py --dry-run
```

## 命令行选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--input-dir DIR` | 输入目录 | `static/images` |
| `--output-dir DIR` | 输出目录 | `static/images/optimized` |
| `--quality QUALITY` | 图片质量 (1-100) | `85` |
| `--max-width WIDTH` | 最大宽度 | `1920` |
| `--sizes SIZES` | 生成的尺寸列表 | `320 640 960 1280 1920` |
| `--no-backup` | 不保留原始文件备份 | - |
| `--dry-run` | 仅显示操作，不实际执行 | - |
| `--generate-config` | 生成Hugo配置片段 | - |

## Hugo 配置

运行以下命令生成 Hugo 配置：

```bash
python image_optimizer.py --generate-config
```

将输出内容添加到你的 `config.toml`：

```toml
# 图片优化配置
[imaging]
  quality = 85
  resampleFilter = "Lanczos"

# WebP格式支持
[outputFormats.WebP]
  baseName = "image"
  mediaType = "image/webp"

# 图片处理设置
[params.imaging]
  # 响应式图片尺寸
  sizes = [320, 640, 960, 1280, 1920]
  # 图片质量
  quality = 85
```

## 使用示例

### 示例 1: 基本优化

```bash
# 优化所有图片，使用默认设置
python image_optimizer.py

# 输出示例：
# 2024-01-15 10:30:00 - INFO - 发现 25 个图片文件待处理
# 2024-01-15 10:30:01 - INFO - 处理图片: static/images/avatar.jpg (1200x800)
# 2024-01-15 10:30:01 - INFO - 生成: static/images/optimized/avatar_320w.webp (320x213, 12450 bytes)
# 2024-01-15 10:30:01 - INFO - 生成: static/images/optimized/avatar_640w.webp (640x427, 38750 bytes)
# ...
# 2024-01-15 10:30:05 - INFO - 优化完成: 125 成功, 0 失败
# 2024-01-15 10:30:05 - INFO - 总计节省空间: 2456.7 KB
```

### 示例 2: 自定义设置

```bash
# 高质量优化，生成更多尺寸
python image_optimizer.py \
  --quality 95 \
  --sizes 320 480 640 800 1024 1280 1600 \
  --input-dir content/posts/images \
  --output-dir static/images/posts
```

### 示例 3: 在 Hugo 构建中使用

在 `Makefile` 中添加：

```makefile
# 优化图片
optimize-images:
    @echo "优化图片..."
    @cd tools/image-optimization && python image_optimizer.py

# 构建时自动优化图片
build: optimize-images
    @echo "构建 Hugo 站点..."
    @hugo --minify
```

## 文件结构

```
static/
├── images/           # 原始图片
│   └── ...
├── images/optimized/ # 优化后的图片
│   └── avatar_320w.webp
│   └── avatar_640w.webp
│   └── ...
└── images/backup/    # 原始文件备份（如果启用）
    └── ...
```

## 性能优化建议

1. **质量设置**: WebP 格式下 85-90 的质量通常能获得最佳的压缩比
2. **尺寸选择**: 根据你的网站设计选择合适的响应式尺寸
3. **缓存策略**: 优化后的图片可以通过 CDN 缓存进一步提升性能
4. **渐进式加载**: 考虑为大图片添加 `loading="lazy"` 属性

## 故障排除

### 常见问题

1. **ImportError: No module named 'PIL'**
   ```bash
   pip install Pillow
   ```

2. **权限错误**
   ```bash
   # 确保输出目录有写入权限
   chmod 755 static/images/optimized
   ```

3. **内存不足**
   ```bash
   # 对于超大图片，可以降低质量或不生成过多尺寸
   python image_optimizer.py --quality 75 --sizes 640 1024 1440
   ```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
