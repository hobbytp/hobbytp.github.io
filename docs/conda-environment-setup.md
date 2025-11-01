# 开发环境配置说明

## 🐍 Conda 环境

本项目使用 conda 环境 `news_collector` 来管理 Python 依赖。

### 环境信息

- **环境名称**: `news_collector`
- **Python 版本**: 3.12
- **位置**: `D:\hobby\tools\miniconda3\envs\news_collector`

### 激活环境

```bash
# Windows
conda activate news_collector

# 或使用 conda run（无需激活）
conda run -n news_collector python <script.py>
```

### 已安装的包

```bash
# 查看已安装的包
conda run -n news_collector pip list

# 关键依赖
google-generativeai==0.3.0+
openai==1.0.0+
perplexityai==0.16.0
PyYAML==6.0+
requests==2.28.0+
python-dateutil==2.8.0+
Pillow==9.0.0+
```

### 安装新依赖

```bash
# 在 news_collector 环境中安装
conda run -n news_collector pip install <package-name>

# 或激活后安装
conda activate news_collector
pip install <package-name>
```

## 🚀 运行脚本

### 方式 1: conda run（推荐）

```bash
# 无需激活环境，直接运行
conda run -n news_collector python scripts/daily_ai_collector_v2.py
```

### 方式 2: 激活后运行

```bash
# 激活环境
conda activate news_collector

# 运行脚本
python scripts/daily_ai_collector_v2.py
```

### 方式 3: 在 VS Code 中

1. 打开命令面板 (Ctrl+Shift+P)
2. 选择 "Python: Select Interpreter"
3. 选择 `news_collector` 环境
4. 直接运行脚本

## 📝 环境变量

### 本地开发

在项目根目录创建 `.env` 文件：

```bash
# .env
GEMINI_API_KEY=your_gemini_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
GITHUB_TOKEN=your_github_token_here
HUGGINGFACE_API_KEY=your_hf_token_here
```

### 加载环境变量

```bash
# Linux/Mac
export $(cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object {
    $var = $_.Split('=')
    [System.Environment]::SetEnvironmentVariable($var[0], $var[1])
}

# 或在 conda 环境中设置
conda env config vars set GEMINI_API_KEY=xxx
conda activate news_collector  # 重新激活生效
```

## 🔧 常用命令

### 环境管理

```bash
# 查看所有环境
conda env list

# 查看当前环境
conda info --envs

# 导出环境配置
conda env export > environment.yml

# 从配置创建环境
conda env create -f environment.yml
```

### 依赖管理

```bash
# 更新 requirements.txt
pip freeze > scripts/requirements.txt

# 从 requirements.txt 安装
pip install -r scripts/requirements.txt
```

### 测试运行

```bash
# 测试 V2 收集器
conda run -n news_collector python scripts/daily_ai_collector_v2.py

# 测试诊断脚本
conda run -n news_collector python scripts/diagnose_gemini.py

# 查看生成的文件
ls -lt content/zh/daily_ai/ | head -5
```

## 🐛 故障排查

### 问题 1: conda 命令不可用

**解决方案**:
```bash
# 初始化 conda
conda init bash  # 或 conda init powershell

# 重启终端
```

### 问题 2: 环境找不到

**解决方案**:
```bash
# 检查环境是否存在
conda env list

# 如果不存在，创建环境
conda create -n news_collector python=3.12
conda activate news_collector
pip install -r scripts/requirements.txt
```

### 问题 3: 包导入失败

**解决方案**:
```bash
# 确认在正确的环境中
conda info --envs

# 重新安装依赖
conda run -n news_collector pip install -r scripts/requirements.txt
```

### 问题 4: 环境变量未生效

**解决方案**:
```bash
# 检查环境变量
conda run -n news_collector python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# 临时设置（当前会话）
export GEMINI_API_KEY=xxx

# 永久设置（conda 环境）
conda activate news_collector
conda env config vars set GEMINI_API_KEY=xxx
conda activate news_collector  # 重新激活
```

## 📚 最佳实践

1. **始终在 conda 环境中运行**
   - 使用 `conda run -n news_collector` 或先激活环境
   - 避免污染全局 Python 环境

2. **及时更新依赖**
   - 定期运行 `pip list --outdated` 检查更新
   - 更新后测试确保兼容性

3. **保持环境配置同步**
   - 更新依赖后及时更新 `requirements.txt`
   - 考虑导出 `environment.yml` 用于完整环境复现

4. **使用 .env 文件管理密钥**
   - 不要提交 `.env` 到 Git
   - 确保 `.gitignore` 包含 `.env`

## 🔗 相关文档

- [Conda 官方文档](https://docs.conda.io/)
- [项目 Requirements](../scripts/requirements.txt)
- [API 配置指南](./daily-ai-v2-setup.md)
- [快速开始](./DAILY_AI_V2_QUICKSTART.md)

---

**更新日期**: 2025-10-15  
**环境版本**: news_collector (Python 3.12)
