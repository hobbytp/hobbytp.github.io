# AI 封面图片生成指南

本文档详细介绍了如何使用 `scripts/ai_cover_generator.py` 脚本为博客文章自动生成高质量的 AI 封面图片。

## 🌟 支持的服务提供商 (按推荐优先级)

脚本支持多种 AI 图片生成服务，您可以根据需求选择最适合的一种。

### 1. 火山方舟 (Volcengine Ark) - **推荐** 🥇
使用火山引擎方舟平台 (Ark) 的 API，支持最新的 **Doubao Seedream** 模型。
*   **优点**: 接口标准 (OpenAI 兼容)，配置简单 (仅需 API Key)，模型效果极佳 (Seedream 4.0)，适合个人开发者。
*   **模型**: `doubao-seedream-4-0-250828` (默认), `doubao-seedream-3-0-t2i` 等。

### 2. ModelScope (魔搭社区) - **备选** 🥈
使用阿里达摩院 ModelScope 的 API，支持 **Qwen-Image** 模型。
*   **优点**: 开源社区支持，Qwen-Image 模型对中文理解能力强。
*   **模型**: `Qwen/Qwen-Image`。

### 3. 火山引擎视觉智能 (Volcengine Visual) - **传统** 🥉
使用火山引擎视觉智能接口 (Visual API)，支持 **即梦 (Jimeng)** 模型。
*   **优点**: 企业级接口，功能丰富。
*   **缺点**: 鉴权复杂 (需 AK/SK 签名)，配置繁琐。
*   **模型**: `jimeng_t2i_v40`。

---

## ⚙️ 配置指南

请在项目根目录的 `.env` 文件中进行配置。

### 通用配置
```dotenv
# 指定使用的图片生成服务: ark (推荐) | modelscope | volcengine
TEXT2IMAGE_PROVIDER=ark
```

### 1. 配置火山方舟 (Ark) [推荐]
获取 Key: [火山引擎控制台 - API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)
模型接入点: [火山引擎控制台 - 在线推理](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint)

```dotenv
# 必填
ARK_API_KEY=your_ark_api_key_here
# 选填 (默认如下)
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seedream-4-0-250828
```

### 2. 配置 ModelScope
获取 Key: [ModelScope 个人中心](https://modelscope.cn/my/myaccesstoken)

```dotenv
# 必填
MODELSCOPE_API_KEY=your_modelscope_token_here
# 选填
MODELSCOPE_MODEL=Qwen/Qwen-Image
```

### 3. 配置火山引擎视觉智能 (Visual)
获取 Key: [火山引擎 IAM](https://console.volcengine.com/iam/identitymanage/user/)

```dotenv
# 必填 (注意：不是 ARK_API_KEY)
VOLCENGINE_ACCESS_KEY=AKLT...
VOLCENGINE_SECRET_KEY=...
# 选填
VOLCENGINE_MODEL=jimeng_t2i_v40
```

---

## 💻 使用方法

### 命令行运行

在本地运行脚本进行测试或批量生成。

```bash
# 进入脚本目录
cd scripts

# 1. 自动扫描并为没有封面的文章生成 (默认模式)
python ai_cover_generator.py

# 2. 强制重新生成所有封面 (慎用)
python ai_cover_generator.py --force

# 3. 为特定文件生成封面
python ai_cover_generator.py --specific-file "../content/zh/posts/my-article.md"

# 4. 限制处理数量 (例如只处理前 5 个)
python ai_cover_generator.py --limit 5
```

### GitHub Actions 自动运行

项目配置了 `.github/workflows/generate-blog-images.yml` 工作流，支持：
1.  **Push 触发**: 当提交新的 Markdown 文章时，自动检测并生成封面。
2.  **手动触发**: 在 GitHub Actions 页面手动运行，可选择服务商和生成目标。

---

## 📚 API 参考文档

更多关于各模型 API 的详细参数和说明，请参考以下文档：

*   **Doubao Seedream (Ark)**: [docs/ai-cover-doubao-v4-api-doc.md](../docs/ai-cover-doubao-v4-api-doc.md)
*   **Qwen-Image (ModelScope)**: [docs/ai-cover-modelscope-qwen-image-api.md](../docs/ai-cover-modelscope-qwen-image-api.md)
*   **Jimeng (Volcengine Visual)**: [docs/ai-cover-jimeng-api-doc.md](../docs/ai-cover-jimeng-api-doc.md)
