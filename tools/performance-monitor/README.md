# Hugo Blog Performance Analyzer

分析Hugo博客的性能指标，提供优化建议。

## 功能特性

- 🕐 **构建时间分析**: 测量Hugo构建耗时
- 📊 **站点结构分析**: 统计页面数量、大小分布
- 🖼️ **图片优化检查**: 分析图片格式和大小
- 📦 **资源使用统计**: CSS/JS文件大小分析
- 📝 **性能报告生成**: 自动生成优化建议

## 安装依赖

本工具使用Python标准库，无需额外依赖。

## 基本用法

### 1. 执行完整性能分析

```bash
python performance_analyzer.py --all
```

### 2. 仅分析构建时间

```bash
python performance_analyzer.py --build-time
```

### 3. 分析站点结构

```bash
python performance_analyzer.py --analyze-site
```

### 4. 检查图片优化情况

```bash
python performance_analyzer.py --check-images
```

### 5. 生成性能报告

```bash
python performance_analyzer.py --generate-report
```

## 命令行选项

| 选项 | 描述 |
|------|------|
| `--build-time` | 分析Hugo构建时间 |
| `--analyze-site` | 分析站点结构和大小 |
| `--check-images` | 检查图片优化情况 |
| `--generate-report` | 生成性能报告 |
| `--output-dir DIR` | 输出目录 (默认: reports) |
| `--all` | 执行所有分析 (默认) |

## 输出结果

### 性能报告示例

```
# Hugo博客性能分析报告

生成时间: 2024-01-15 14:30:00

## 📊 总体统计

- **构建时间**: 12.34 秒
- **页面数量**: 568
- **站点总大小**: 53.2 MB
- **平均页面大小**: 45.6 KB

## 🖼️ 图片分析

- **图片总数**: 156
- **图片总大小**: 8.7 MB
- **WebP格式数量**: 89

### 图片格式分布
- **WEBP**: 89 个文件, 3.2 MB
- **JPG**: 45 个文件, 4.1 MB
- **PNG**: 22 个文件, 1.4 MB

## 💡 性能优化建议

- ✅ 性能表现良好，继续保持！
```

## 在Hugo工作流中使用

### 添加到Makefile

```makefile
# 性能分析
analyze-performance:
    @echo "分析Hugo性能..."
    @cd tools/performance-monitor && python performance_analyzer.py --all

# 构建后自动分析
build: hugo-build
    @$(MAKE) analyze-performance
```

### GitHub Actions集成

```yaml
- name: Performance Analysis
  run: |
    cd tools/performance-monitor
    python performance_analyzer.py --all --output-dir ../../reports
```

## 分析指标说明

### 构建时间

- **< 10秒**: 优秀
- **10-30秒**: 良好
- **30-60秒**: 需要优化
- **> 60秒**: 严重问题

### 页面大小

- **< 50KB**: 优秀 (移动端友好)
- **50-100KB**: 良好
- **100-200KB**: 可接受
- **> 200KB**: 需要优化

### 图片优化

- **WebP使用率 > 80%**: 优秀
- **WebP使用率 > 50%**: 良好
- **WebP使用率 < 50%**: 需要优化
- **大文件 > 500KB**: 建议压缩

## 故障排除

### 常见问题

1. **"public目录不存在"**

   ```bash
   # 先构建Hugo站点
   hugo --minify
   ```

2. **权限错误**

   ```bash
   # 确保reports目录有写入权限
   chmod 755 reports
   ```

3. **Hugo命令未找到**

   ```bash
   # 确保Hugo已安装并在PATH中
   which hugo
   ```

## 扩展功能

### 自定义分析脚本

```python
from performance_analyzer import HugoPerformanceAnalyzer

# 创建分析器实例
analyzer = HugoPerformanceAnalyzer()

# 执行特定分析
build_time = analyzer.measure_build_time()
site_stats = analyzer.analyze_site_structure()
image_stats = analyzer.analyze_images()

# 生成自定义报告
print(f"构建耗时: {build_time:.2f}秒")
print(f"页面数量: {site_stats.get('total_files', 0)}")
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
