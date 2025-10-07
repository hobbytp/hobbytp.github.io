# 每日AI动态数据收集测试指南

## 📋 概述

本目录包含了用于测试每日AI动态数据收集功能的脚本。这些脚本可以帮助您在本地验证数据收集是否正常工作。

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install requests openai pyyaml

# 或者使用requirements.txt
pip install -r requirements.txt
```

### 2. 设置API密钥

#### 方法1: 使用.env文件（推荐）

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑.env文件，填入您的API密钥
# GITHUB_TOKEN=your_github_token_here
# GEMINI_API_KEY=your_gemini_api_key_here
# HUGGINGFACE_API_KEY=your_hf_token_here
```

#### 方法2: 设置环境变量

```bash
# Linux/Mac
export GITHUB_TOKEN="your_github_token"
export GEMINI_API_KEY="your_gemini_api_key"
export HUGGINGFACE_API_KEY="your_hf_token"

# Windows
set GITHUB_TOKEN=your_github_token
set GEMINI_API_KEY=your_gemini_api_key
set HUGGINGFACE_API_KEY=your_hf_token
```

### 3. 运行测试

```bash
# 快速测试（推荐）
python scripts/run_test.py

# 或者直接运行详细测试
python scripts/test_data_collection.py
```

## 🔧 API密钥获取指南

### GitHub Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 选择权限：至少需要 `public_repo` 权限
4. 复制生成的token

### Gemini API Key
1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账户
3. 点击 "Create API Key"
4. 复制生成的API密钥

### Hugging Face Token（可选）
1. 访问 https://huggingface.co/settings/tokens
2. 登录Hugging Face账户
3. 点击 "New token"
4. 选择权限：`read` 即可
5. 复制生成的token

## 📊 测试脚本说明

### `test_data_collection.py`
主要测试脚本，包含以下测试：
- ✅ 环境变量检查
- ✅ GitHub API测试
- ✅ Hugging Face API测试
- ✅ ArXiv API测试
- ✅ AI摘要生成测试
- ✅ 完整数据收集流程测试

### `setup_test_env.py`
环境设置脚本，帮助：
- 检查Python包依赖
- 验证API密钥设置
- 创建配置文件模板

### `run_test.py`
快速测试脚本，自动：
- 加载.env文件
- 运行完整测试套件

## 📈 测试输出示例

```
🧪 每日AI动态数据收集测试
==================================================
🔧 检查环境变量...
✅ GITHUB_TOKEN: ******** (已设置)
✅ GEMINI_API_KEY: ******** (已设置)
✅ HUGGINGFACE_API_KEY: ******** (已设置)
✅ 环境变量检查完成

🔍 测试GitHub API...
🔍 搜索GitHub项目: AI machine-learning deep-learning created:>2025-10-01 language:python language:javascript
📊 GitHub API响应状态: 200
✅ 找到 15 个GitHub项目
✅ GitHub API测试成功，找到 15 个项目

🔍 测试Hugging Face API...
🔍 搜索Hugging Face模型
📊 HF API响应状态: 200
📊 获取到 50 个模型
✅ 找到 8 个最近创建的模型
✅ Hugging Face API测试成功，找到 8 个模型

🔍 测试ArXiv API...
🔍 搜索ArXiv论文: cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[202510010000 TO 202510072359]
📊 ArXiv API响应状态: 200
✅ 找到 12 篇ArXiv论文
✅ ArXiv API测试成功，找到 12 篇论文

🤖 测试AI摘要生成...
📊 数据收集统计:
   GitHub项目: 1
   HF模型: 1
   ArXiv论文: 1
🤖 开始AI生成摘要...
✅ AI摘要生成完成
✅ AI摘要生成测试成功

🚀 测试完整数据收集流程...
📊 开始收集数据...
📅 时间范围: 2025年10月06日 08:00 - 2025年10月07日 08:00
🔍 开始收集数据...
🔍 搜索GitHub项目: AI machine-learning deep-learning created:>2025-10-01 language:python language:javascript
📊 GitHub API响应状态: 200
✅ 找到 15 个GitHub项目
🔍 搜索Hugging Face模型
📊 HF API响应状态: 200
📊 获取到 50 个模型
✅ 找到 8 个最近创建的模型
🔍 搜索ArXiv论文: cat:cs.AI OR cat:cs.LG OR cat:cs.CL AND submittedDate:[202510010000 TO 202510072359]
📊 ArXiv API响应状态: 200
✅ 找到 12 篇ArXiv论文
📊 数据收集统计:
   GitHub项目: 15
   HF模型: 8
   ArXiv论文: 12
🤖 开始AI生成摘要...
✅ AI摘要生成完成
✅ 测试结果已保存到: test_daily_ai_output.md

==================================================
📊 测试结果总结:
==================================================
GitHub API: ✅ 通过
Hugging Face API: ✅ 通过
ArXiv API: ✅ 通过
AI摘要生成: ✅ 通过
完整数据收集: ✅ 通过

总计: 5/5 项测试通过
🎉 所有测试都通过了！数据收集功能正常工作。
```

## 🐛 故障排除

### 常见问题

1. **"ImportError: No module named 'requests'"**
   ```bash
   pip install requests openai pyyaml
   ```

2. **"GitHub API错误: 401"**
   - 检查GitHub token是否正确
   - 确认token有足够的权限

3. **"Gemini API错误: 403"**
   - 检查Gemini API key是否正确
   - 确认API配额是否充足

4. **"没有收集到任何数据"**
   - 检查网络连接
   - 确认API密钥权限
   - 尝试放宽时间范围

### 调试技巧

1. **查看详细日志**
   - 测试脚本会输出详细的调试信息
   - 注意API响应状态码

2. **检查网络连接**
   ```bash
   # 测试GitHub API
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/user
   
   # 测试ArXiv API
   curl "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=1"
   ```

3. **验证API密钥**
   - GitHub: 访问 https://api.github.com/user
   - Gemini: 使用API文档中的测试端点

## 📝 测试结果文件

测试完成后会生成 `test_daily_ai_output.md` 文件，包含：
- 数据收集统计
- AI生成的摘要
- 原始收集的数据（JSON格式）

这个文件可以帮助您了解数据收集的详细情况。

## 🔄 持续测试

建议定期运行测试以确保：
- API密钥仍然有效
- 数据收集功能正常
- 网络连接稳定

```bash
# 每日测试
python scripts/run_test.py

# 或添加到crontab
0 9 * * * cd /path/to/your/project && python scripts/run_test.py
```
