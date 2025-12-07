# 修复 Cloudflare API Token 格式问题

## 问题症状

运行 `scripts/test_cloudflare_auth.py` 时出现：
```
❌ 请求失败: HTTP 400
响应: {"success":false,"errors":[{"code":6003,"message":"Invalid request headers","error_chain":[{"code":6111,"message":"Invalid format for Authorization header"}]}]}
```

## 原因

Cloudflare API Token 格式不正确，常见问题：

1. **Token 被引号包裹** - `.env` 文件中使用了引号
2. **Token 包含换行符** - 复制粘贴时包含了换行
3. **Token 包含空白字符** - 前后有空格或中间有空格

## 解决方案

### 步骤 1: 检查 .env 文件

打开 `.env` 文件，检查 `CLOUDFLARE_API_TOKEN` 的格式：

```bash
# ❌ 错误格式 1: 使用引号
CLOUDFLARE_API_TOKEN="82d67d12...90b5"

# ❌ 错误格式 2: 包含换行符
CLOUDFLARE_API_TOKEN=82d67d12
...90b5

# ❌ 错误格式 3: 前后有空格
CLOUDFLARE_API_TOKEN= 82d67d12...90b5 

# ✅ 正确格式: 纯字符串，无引号，无空白字符
CLOUDFLARE_API_TOKEN=82d67d12...90b5
```

### 步骤 2: 修复 .env 文件

1. 打开 `.env` 文件
2. 找到 `CLOUDFLARE_API_TOKEN` 行
3. 确保格式为：
   ```
   CLOUDFLARE_API_TOKEN=your_token_here
   ```
   - 不要使用引号（除非 token 本身包含引号，这种情况很少见）
   - 不要有前后空格
   - 不要有换行符
   - Token 应该是连续的字符串

### 步骤 3: 重新获取 Token（如果需要）

如果问题仍然存在，可能需要重新生成 API Token：

1. 访问 https://dash.cloudflare.com/profile/api-tokens
2. 删除旧的 Token（如果已失效）
3. 点击 "Create Token"
4. 使用 "Edit Cloudflare Workers" 模板，或自定义权限：
   - Account: Cloudflare Workers AI:Edit
   - Account: Vectorize:Edit
5. 复制新 Token（注意：只显示一次）
6. 直接粘贴到 `.env` 文件中，不要添加引号

### 步骤 4: 验证修复

运行测试脚本：

```bash
uv run python scripts/test_cloudflare_auth.py
```

应该看到：
```
✅ 账户验证成功: Your Account Name
✅ Workers AI 可访问
✅ Vectorize 可访问
```

## 自动清理功能

代码已更新，会自动清理以下问题：
- ✅ 移除前后空白字符
- ✅ 移除引号包裹
- ✅ 移除换行符和中间空白字符

但最好在 `.env` 文件中就使用正确格式，避免潜在问题。

## 常见问题

### Q: Token 长度应该是多少？

A: Cloudflare API Token 通常是 40-50 个字符的 base64 编码字符串。如果长度异常（< 20 或 > 100），可能格式不正确。

### Q: 为什么不能使用引号？

A: 虽然某些环境变量解析器支持引号，但 Cloudflare API 期望的是纯字符串。引号会被包含在 token 中，导致认证失败。

### Q: 如何确认 Token 格式正确？

A: 运行 `scripts/test_cloudflare_auth.py`，它会：
- 显示 Token 长度
- 检查格式问题
- 测试 API 连接
- 提供详细的错误信息

## 参考

- [Cloudflare API Token 文档](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [Cloudflare Workers AI 文档](https://developers.cloudflare.com/workers-ai/)





