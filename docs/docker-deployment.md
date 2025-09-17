# Hugo Docker 部署指南

## 目录

- [Hugo Docker 部署指南](#hugo-docker-部署指南)
  - [目录](#目录)
  - [快速开始](#快速开始)
  - [部署原理](#部署原理)
  - [前置要求](#前置要求)
  - [部署方法](#部署方法)
    - [Docker 直接部署](#docker-直接部署)
      - [基础启动命令](#基础启动命令)
      - [参数说明](#参数说明)
      - [终端适配](#终端适配)
        - [Git Bash（推荐）](#git-bash推荐)
        - [PowerShell](#powershell)
        - [CMD](#cmd)
    - [Docker Compose 部署](#docker-compose-部署)
    - [Make 工具部署](#make-工具部署)
  - [配置说明](#配置说明)
    - [端口配置](#端口配置)
    - [主题配置](#主题配置)
    - [开发模式配置](#开发模式配置)
  - [常见问题解决](#常见问题解决)
    - [1. 配置文件找不到](#1-配置文件找不到)
    - [2. 样式不更新](#2-样式不更新)
    - [3. Windows 路径问题](#3-windows-路径问题)
    - [4. 端口被占用](#4-端口被占用)
    - [5. 主题更新问题](#5-主题更新问题)
  - [开发技巧](#开发技巧)
    - [实时预览](#实时预览)
    - [生产环境测试](#生产环境测试)
    - [主题开发模式](#主题开发模式)
    - [调试技巧](#调试技巧)
  - [部署验证](#部署验证)
  - [最佳实践](#最佳实践)

## 快速开始

使用 Docker Compose 快速启动开发服务器：

```bash
docker-compose up
```

访问 `http://localhost:1313` 查看网站。

## 部署原理

Hugo 通过 Docker 容器提供隔离的运行环境：

- 容器镜像包含 Hugo 核心和所有依赖
- 通过卷(volume)挂载实现主机-容器文件同步
- 端口映射(1313:1313)实现本地访问
- 支持热重载，实时预览修改

## 前置要求

- 已安装 Docker Desktop 并确保服务正在运行
- 项目目录结构完整（含 config.toml）
- Git 子模块初始化（如使用主题）：

  ```bash
  git submodule update --init --recursive
  ```

- 确保 1313 端口未被占用（或准备使用其他端口）

## 部署方法

### Docker 直接部署

#### 基础启动命令

```bash
MSYS_NO_PATHCONV=1 docker run --rm -it \
  -v /d/Hobby/github/hobbytp.github.io:/src \
  -p 1313:1313 \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  server -D --bind=0.0.0.0
```

#### 参数说明

| 参数 | 作用 | 说明 |
|------|------|------|
| `MSYS_NO_PATHCONV=1` | 防止 Windows 路径转换 | Git Bash 专用 |
| `--rm` | 退出后自动删除容器 | 保持环境清洁 |
| `-it` | 交互式终端 | 可以使用 Ctrl+C 停止 |
| `-v` | 主机目录映射到容器 | 源代码同步 |
| `-p` | 端口映射 | 可修改为其他端口 |
| `-w` | 容器内工作目录 | 必须与卷挂载路径一致 |
| `server -D` | 启动开发服务器并显示草稿 | 开发模式 |
| `--bind` | 允许外部访问 | 默认只允许 localhost |

#### 终端适配

##### Git Bash（推荐）

```bash
MSYS_NO_PATHCONV=1 docker run --rm -it \
  -v /d/Hobby/github/hobbytp.github.io:/src \
  -p 1313:1313 \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  server -D --bind=0.0.0.0
```

##### PowerShell

```powershell
docker run --rm -it `
  -v ${PWD}:/src `
  -p 1313:1313 `
  -w /src `
  hugomods/hugo:exts-0.148.0 `
  server -D --bind=0.0.0.0
```

##### CMD

```cmd
docker run --rm -it ^
  -v %cd%:/src ^
  -p 1313:1313 ^
  -w /src ^
  hugomods/hugo:exts-0.148.0 ^
  server -D --bind=0.0.0.0
```

### Docker Compose 部署

使用 `docker-compose.yml` 文件管理部署：

```yaml
version: '3'
services:
  hugo:
    image: hugomods/hugo:exts-0.148.0
    ports:
      - "1313:1313"
    volumes:
      - .:/src
    working_dir: /src
    command: server -D --bind=0.0.0.0
```

启动命令：

```bash
docker-compose up
```

### Make 工具部署

使用 Makefile 简化部署流程：

```makefile
.PHONY: dev build clean

dev:
 docker run --rm -it \
  -v $(PWD):/src \
  -p 1313:1313 \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  server -D --bind=0.0.0.0

build:
 docker run --rm \
  -v $(PWD):/src \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  build --minify

clean:
 rm -rf public/ resources/_gen/
```

## 配置说明

### 端口配置

默认端口为 1313，可通过以下方式修改：

1. Docker 直接部署：

   ```bash
   -p 新端口:1313
   ```

2. Docker Compose：

   ```yaml
   ports:
     - "新端口:1313"
   ```

### 主题配置

1. 确保主题已正确安装：

   ```bash
   git submodule update --init --recursive
   ```

2. 更新主题：

   ```bash
   git submodule update --remote --merge
   ```

### 开发模式配置

- `-D` 参数：显示草稿内容
- `--bind=0.0.0.0`：允许外部访问
- `--disableFastRender`：禁用快速渲染（主题开发时使用）

## 常见问题解决

### 1. 配置文件找不到

症状：`Unable to locate config file`  
解决：

- 确认在项目根目录执行
- 检查路径映射是否正确
- 添加 `-w /src` 参数
- 确认 config.toml 存在且格式正确

### 2. 样式不更新

解决方案：

```bash
# 清理缓存
rm -rf public/ resources/_gen/
# 重启 Hugo 服务器
```

### 3. Windows 路径问题

解决方案：

- 使用绝对路径（如 `/d/...`）
- 添加 `MSYS_NO_PATHCONV=1` 前缀
- 确保路径中没有特殊字符

### 4. 端口被占用

症状：`port is already in use`  
解决：

```bash
# 使用其他端口，如 1314
docker run --rm -it \
  -v /d/Hobby/github/hobbytp.github.io:/src \
  -p 1314:1313 \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  server -D --bind=0.0.0.0
```

### 5. 主题更新问题

症状：主题更新后样式未生效  
解决：

```bash
# 更新主题
git submodule update --remote --merge
# 清理缓存
rm -rf public/ resources/_gen/
# 重启服务

```

## 开发技巧

### 实时预览

- 修改 Markdown 自动刷新
- CSS/JS 变更实时生效
- 配置文件修改需要重启服务

### 生产环境测试

```bash
docker run --rm \
  -v /d/Hobby/github/hobbytp.github.io:/src \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  build --minify
```

### 主题开发模式

```bash
docker run --rm -it \
  -v /d/Hobby/github/hobbytp.github.io:/src \
  -p 1313:1313 \
  -w /src \
  hugomods/hugo:exts-0.148.0 \
  server -D --disableFastRender --theme PaperMod
```

### 调试技巧

- 使用 `hugo --debug` 查看详细日志
- 检查浏览器控制台错误信息
- 验证文件权限和路径正确性

## 部署验证

1. 访问测试：
   - 默认地址：`http://localhost:1313`
   - 如修改端口：`http://localhost:端口号`

2. 功能验证：
   - 检查页面样式是否正确
   - 验证链接可以正常跳转
   - 确认图片正常显示
   - 测试标签和分类功能

3. 性能检查：
   - 页面加载速度
   - 实时预览响应时间
   - 资源加载状态

## 最佳实践

1. 使用 Docker Compose 管理部署配置
2. 保持主题更新到最新版本
3. 定期清理构建缓存
4. 使用 Makefile 简化常用命令
5. 开发时启用草稿显示
6. 生产构建时启用压缩
7. 使用版本控制管理主题

> 注意：本文档假设使用 Git Bash 作为默认终端。如使用其他终端，请参考[终端适配](#终端适配)部分。

> 文档最后更新：2024年6月
