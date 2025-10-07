# API密钥设置指南

## 当前状态
测试脚本运行成功，但需要设置API密钥才能进行完整测试。

## 需要设置的API密钥

### 1. GitHub Token (必需)
- **用途**: 搜索GitHub上的AI项目
- **获取地址**: https://github.com/settings/tokens
- **权限**: 至少需要 `public_repo` 权限

### 2. Gemini API Key (必需)
- **用途**: 生成AI摘要
- **获取地址**: https://makersuite.google.com/app/apikey
- **说明**: 用于调用Google Gemini API

### 3. Hugging Face Token (可选)
- **用途**: 搜索Hugging Face上的AI模型
- **获取地址**: https://huggingface.co/settings/tokens
- **权限**: `read` 权限即可

## 设置方法

### 方法1: 使用.env文件 (推荐)

1. 在项目根目录创建 `.env` 文件
2. 添加以下内容：
```
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_hf_token_here
```

### 方法2: 设置环境变量

#### Windows (PowerShell)
```powershell
$env:GITHUB_TOKEN="your_github_token"
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:HUGGINGFACE_API_KEY="your_hf_token"
```

#### Windows (CMD)
```cmd
set GITHUB_TOKEN=your_github_token
set GEMINI_API_KEY=your_gemini_api_key
set HUGGINGFACE_API_KEY=your_hf_token
```

## 测试步骤

1. 设置API密钥后，运行测试：
```bash
python scripts/basic_test.py
```

2. 如果所有测试通过，可以运行完整测试：
```bash
python scripts/test_data_collection.py
```

## 预期结果

设置API密钥后，您应该看到：
- ✅ 环境变量检查通过
- ✅ GitHub API找到项目
- ✅ ArXiv API找到论文
- ✅ AI摘要生成成功

## 故障排除

如果遇到问题：
1. 检查API密钥是否正确
2. 确认网络连接正常
3. 验证API密钥权限
4. 查看详细错误信息
