---
title: 每周一个MCP：FastAPI-MCP
date: "2025-04-22T15:03:00+08:00"
tags: ["mcp", "fastapi", "python"]
categories: ["projects"]
draft: false
description: FastAPI-MCP 是一个扩展 FastAPI 的工具，用于将 FastAPI 的端点暴露为具有认证功能的 Model Context Protocol (MCP) 工具。
---

## 背景

FastAPI-MCP 是一个扩展 FastAPI 的工具，以最少的设置、认证和有限的配置，将安全的 FastAPI 端点作为 MCP 工具进行公开，且所有操作都在统一的基础设施中完成。其主要特点包括：

1. 内置认证功能，兼容 FastAPI 的依赖管理。
2. 原生支持 FastAPI，而非简单的 OpenAPI -> MCP 转换器。
3. 零配置或最低配置即可使用，保留请求/响应模型的模式和端点文档（如 Swagger）。
4. 灵活部署，可与 FastAPI 应用一起部署或单独运行。
5. ASGI 通信，直接使用 FastAPI 的接口，高效的传输性能。
6. 提供主机化托管解决方案。

安装方式包括 `uv` 或 `pip`，支持直接将 MCP 服务挂载到 FastAPI。提供全面的文档、示例和进阶功能支持。适配 Python 3.10+ (推荐 3.12)。该项目开源，遵循 MIT 许可协议。

## 快速开始  

### 安装

```bash
pip install fastapi-mcp
```

### 基本使用

使用 FastAPI-MCP 最简单的方法是将 MCP 服务器直接添加到您的 FastAPI 应用程序中：

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

mcp = FastApiMCP(app)

#  默认挂载到 /mcp 路径
mcp.mount() # OR
mcp.mount_http()
```

这个自动生成的 MCP 服务器将运行在 `/mcp` 路径下。此时，任何支持 MCP 协议（SSE 或 stdio）的 AI 客户端都能自动发现并调用 /hello 接口。

### 高级定制

[中文文档](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md)
更多的使用例子，参考[Github Examples](https://github.com/tadata-org/fastapi_mcp/tree/main/examples)

* [自定义模式描述](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md#%E8%87%AA%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%BC%8F%E6%8F%8F%E8%BF%B0)
* [自定义公开的端点](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md#%E8%87%AA%E5%AE%9A%E4%B9%89%E5%85%AC%E5%BC%80%E7%9A%84%E7%AB%AF%E7%82%B9)
* [与原始 FastAPI 应用分开部署](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md#%E4%B8%8E%E5%8E%9F%E5%A7%8B-fastapi-%E5%BA%94%E7%94%A8%E5%88%86%E5%BC%80%E9%83%A8%E7%BD%B2)
* [在-mcp-服务器创建后添加端点](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md#%E5%9C%A8-mcp-%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%88%9B%E5%BB%BA%E5%90%8E%E6%B7%BB%E5%8A%A0%E7%AB%AF%E7%82%B9)
* [与 FastAPI 应用的通信](https://github.com/tadata-org/fastapi_mcp/blob/main/README_zh-CN.md#%E4%B8%8E-fastapi-%E5%BA%94%E7%94%A8%E7%9A%84%E9%80%9A%E4%BF%A1)

### 客户端接入

使用 SSE 连接到 MCP 服务器, 如果您的 MCP 客户端不支持 SSE，例如 Claude Desktop, 安装mcp-proxy后配置客户端

```json
{
  "mcpServers": {
    "my-api-mcp-proxy": {
        "command": "mcp-proxy",
        "args": ["http://127.0.0.1:8000/mcp"]
    }
  }
}
```

## 参考

* [FastAPI MCP Github](https://fastapi-mcp.tadata.com/)
* [FastAPI MCP 使用例子](https://github.com/tadata-org/fastapi_mcp/blob/main/examples/README.md)
