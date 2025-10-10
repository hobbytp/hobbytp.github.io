---
title: "xiaohongshu-mcp"
date: 2025-10-10T14:00:00+08:00
lastmod: 2025-10-10T14:00:00+08:00
draft: false
description: "xiaohongshu-mcp 是一个开源项目，用于实现对小红书 (xiaohongshu.com) 的 Model Context Protocol (MCP) 支持，基于自动化运营小红书账号。"
tags: ["MCP", "小红书", "自动化运营"]
categories: ["projects"]
---



## 项目介绍
xiaohongshu-mcp 是一个基于Go语言的开源项目，用于实现对小红书 (xiaohongshu.com) 的 Model Context Protocol (MCP) 支持，基于自动化运营小红书账号。项目包含以下主要功能：

1. **功能支持**
   - 登录：小红书登录（二维码扫码）及检查状态，Cookie持久化存储
   - 内容发布：发布图文/视频内容，查看帖子详情（包括评论）
   - 浏览：搜索内容，获取推荐列表、帖子详情及互动数据，
   - 互动：点赞/取消点赞，收藏/取消收藏，发表评论到帖子，查看用户主页
   - MCP: 标准MCP工具接口，HTTP API接口

2. **部署及使用教程**
   - 支持通过二进制文件、源码编译或 Docker 容器进行部署，操作简单。
   - 详细步骤包括登录(获取cookie)、启动 MCP 服务(使用cookie连接小红书服务器)及验证服务状态。
   - 可连接 MCP 的 AI 客户端（如 Claude Code、Cursor、VSCode），支持标准化发布及交互。

3. **特点及实操说明**
   - 支持持续自动化运营小红书账号，避免封号风险。(cookie过期后要重新人为扫码登录)
   - 支持图文、视频发布及标签添加，有完整的流量运营策略。
   - 提供实战案例及教程，方便社区用户学习与集成。

## 技术架构

### 实现方式
- **浏览器自动化**：使用Rod框架控制Chrome浏览器
- **DOM操作**：通过CSS选择器定位页面元素
- **数据提取**：解析页面JavaScript变量（`window.__INITIAL_STATE__`）
- **模拟用户操作**：点击、输入、上传文件等

### 部署方式
- 预编译二进制文件
- Docker容器部署
- 源码编译
- 支持多平台（Windows、macOS、Linux）

## 优点

| 序号 | 优点类别 | 具体描述 |
|----|----------|----------|
| 1 | 功能完整性 | 覆盖小红书主要功能 |
| 2 | 无需官方API | 无需申请密钥与授权；可直接抓取页面全部数据 |
| 4 | 部署简单 | 多方式部署；Docker一键启动；跨平台支持 |


## 缺点和限制

### **1. 技术风险**
1.1. 页面结构依赖硬编码的CSS选择器，页面变化会导致失效。小红书界面更新会导致功能失效。需要持续维护和更新选择器
```
// 硬编码的CSS选择器，页面变化会导致失效
const (
    SelectorLikeButton    = ".interact-container .left .like-lottie"
    SelectorCollectButton = ".interact-container .left .reds-icon.collect-icon"
)
```

1.2. 数据获取依赖
依赖页面JavaScript变量，小红书改变数据存储方式会导致数据获取失败，需要跟踪页面变化并更新代码
```go
// 依赖页面JavaScript变量
result := page.MustEval(`() => {
    if (window.__INITIAL_STATE__) {
        return JSON.stringify(window.__INITIAL_STATE__);
    }
    return "";
}`).String()
```
### 2. **性能限制**

**资源消耗**: 需要启动Chrome浏览器(有头或无头（无UI）),内存占用较大,CPU使用率较高
**执行速度**: 需要等待页面加载,操作执行较慢，不适合高频操作

### 3. **安全风险**

#### **Cookie管理**
- Cookie可能过期
- 需要定期重新登录
- 登录状态可能被踢出

#### **反爬虫机制**
- 可能触发小红书的反爬虫检测
- 存在账号被封的风险
- 需要模拟真实用户行为

### 4. **功能限制**

#### **操作复杂度**
- 只能执行页面可见的操作
- 无法处理复杂的验证码
- 无法绕过某些安全机制

#### **数据准确性**
- 依赖页面渲染的数据
- 可能存在数据延迟
- 无法获取后台实时数据

## 总结

这个项目体现了浏览器自动化技术的强大能力，但也暴露了这种技术路线的固有风险。在实际使用中需要权衡功能需求和技术风险。






