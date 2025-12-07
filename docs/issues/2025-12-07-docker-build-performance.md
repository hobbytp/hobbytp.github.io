# Docker on Windows 构建性能优化经验 (2025-12-07)

## 问题描述

在 Windows 11 + WSL2/Git Bash 环境下，执行 `make build` (基于 Docker) 极慢，经常超时 (>60s)。
而同样的 `hugo --minify` 命令在 GitHub Actions Linux 环境下只需几秒钟。

## 根本原因

经过排查，瓶颈在于 **Docker 的文件系统挂载（Bind Mount）机制**。

1.  **原始配置**：
    `docker-compose.yml` 中的 `hugo-build` 服务仅挂载了根目录 `.:/src`。
    ```yaml
    services:
      hugo-build:
        volumes:
          - .:/src
    ```

2.  **性能杀手**：
    Hugo 构建时会生成大量静态文件（`/public` 目录，包含数千个文件）和资源文件（`/resources`）。
    由于 `.:/src` 是一个绑定挂载（Bind Mount），Docker 容器内的每一次写操作都需要同步回 Windows 宿主机的文件系统。
    在跨操作系统的文件系统（Windows NTFS <-> Linux Container）之间同步大量小文件（I/O 密集型操作）会导致极大的性能开销。

## 解决方案

使用 **匿名卷（Anonymous Volumes）** 来隔离高频写入目录，避免回写到宿主机（如果不需要在宿主机上保留这些构建产物，或者只需要最终结果）。

在 `docker-compose.yml` 中，为 `hugo-build` 服务添加对 `/src/resources` 和 `/src/public` 的挂载：

```yaml
services:
  hugo-build:
    volumes:
      - .:/src
      - /src/resources  # 匿名卷，不回写宿主机
      - /src/public     # 匿名卷，不回写宿主机
```

## 结果对比

*   **优化前**：构建耗时 > 60s（甚至触发超时），系统卡顿。
*   **优化后**：构建耗时 < 13s。

## 经验教训

1.  **I/O 敏感性**：Docker on Windows (WSL2 backend) 对跨 OS 的文件系统绑定挂载非常敏感，尤其是涉及大量小文件的读写。
2.  **构建隔离**：对于中间产物（如 `resources`）或非必须持久化到开发机源码目录的产物（如 `public`，如果是为了部署通常在 CI/CD 中生成），应尽量使用 Docker 内部卷或匿名卷。
3.  **开发 vs 生产**：开发服务 (`hugo server`) 通常使用内存缓存，对 I/O 不那么敏感，但在 Windows 上也建议对 `resources` 和 `public` 使用匿名卷以提升性能。

## 相关命令

*   `make build`: 生产构建（已优化）。
*   `make build-measure`: 测量当前构建耗时。
