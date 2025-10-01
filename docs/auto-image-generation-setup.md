# 自动博客图片生成设置指南

## 概述

这个功能使用GitHub Actions + Gemini API自动为博客生成封面图片。使用 [Gemini 2.5 Flash Image Preview](https://ai.google.dev/gemini-api/docs/image-generation) 模型进行高质量的图片生成。

## 功能特性

- ✅ 新增博客时自动生成图片
- ✅ 历史博客定时补图（每天5个，每小时不超过1个）
- ✅ 智能提示词生成（基于博客内容）
- ✅ 现代简约科技风格，蓝色主题
- ✅ 使用Gemini 2.5 Flash Image Preview模型
- ✅ 高质量AI生成图片
- ✅ 自动图片处理和优化

## 设置步骤

### 1. 设置GitHub Secrets

1. 进入你的GitHub仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下密钥：

```
Name: GEMINI_API_KEY
Value: 你的Gemini API密钥
```

### 2. 验证设置

设置完成后，你可以：

1. **手动触发新博客图片生成**：
   - 进入 `Actions` 标签页
   - 选择 `Generate Blog Images` 工作流
   - 点击 `Run workflow`

2. **手动触发历史博客补图**：
   - 进入 `Actions` 标签页
   - 选择 `Backfill Blog Images` 工作流
   - 点击 `Run workflow`

### 3. 图片规格

- **尺寸**: 1200x630px
- **格式**: PNG
- **存储路径**: `static/images/articles/`
- **命名规则**: `{分类名}-{博客文件名}.png`

### 4. 触发条件

#### 新增博客触发

- 当有新的`.md`文件提交到`content/`目录时自动触发
- 立即生成对应图片

#### 历史博客补图

- 每天UTC 2点（北京时间10点）自动执行
- 每天最多处理5个博客
- 每小时最多处理1个博客

## 配置说明

### 图片风格

- 现代简约，科技感
- 蓝色渐变主题
- 不包含文字，纯视觉设计
- 根据博客分类调整风格元素

### 分类风格映射

- `ai`: AI电路图案，神经网络可视化
- `projects`: 代码元素，开发工具
- `papers`: 学术图表，研究符号
- `technologies`: 技术基础设施，云计算
- `tools`: 工具图标，界面元素

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查GitHub Secrets中的`GEMINI_API_KEY`是否正确设置
   - 确认API密钥有效且有足够额度

2. **图片生成失败**
   - 查看GitHub Actions日志
   - 检查网络连接和API限制

3. **速率限制**
   - 系统会自动检查每日/每小时限制
   - 超出限制时会跳过处理

### 日志查看

1. 进入 `Actions` 标签页
2. 点击对应的工作流运行记录
3. 查看详细的执行日志

## 成本控制

- 使用Gemini API的免费额度
- 每天最多5个图片生成
- 每小时最多1个图片生成
- 自动跳过已有图片的博客

## 手动操作

如果需要为特定博客重新生成图片：

1. 删除 `static/images/articles/` 目录下对应的图片文件
2. 手动触发 `Backfill Blog Images` 工作流
3. 系统会自动检测并重新生成图片
