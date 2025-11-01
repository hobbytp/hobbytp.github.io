Exa MCP Server 是一个由 Exa Labs 开发的开源工具，主要用于为 AI 助手（如 Claude）提供高效的代码搜索与网络搜索服务。其核心功能包括：

1. **代码上下文搜索**：快速检索代码片段、API 用法和最佳实践，从 GitHub 库及其他资源中提供相关代码参考。
2. **实时网络搜索与爬取**：支持实时爬取网页内容（如 URL、文章、PDF 等），并优化搜索结果。
3. **其他工具**：包括公司信息爬取、LinkedIn 搜索、深度研究等功能。
4. **多种集成方式**：支持通过 Smithery、Claude Desktop、Codex、Claude Code 插件等平台进行配置与集成。
5. **简单配置**：通过 API 密钥及多种工具参数选择，用户可自定义启用功能模块。

项目支持远程或本地部署，核心搜索功能由 Exa 的搜索引擎驱动，适合开发者和研究者使用。技术栈以 TypeScript 为主，采用 MIT 开源协议，目前拥有 3.1k Star 和 231 Fork，可通过 NPM 或源码直接安装使用。


## 用法

```bash
"What's the current rate limit for the GitHub API?"
```
它会自动回复
```bash
GitHub API Rate Limits (May 2025)

Unauthenticated requests: 60 per hour.
Authenticated requests: 5,000 per hour.
Source: Official GitHub API docs.

```

## 参考

https://github.com/exa-labs/exa-mcp-server