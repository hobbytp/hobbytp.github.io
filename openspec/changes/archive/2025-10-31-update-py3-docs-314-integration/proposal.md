# Update: Python 3.14 内容融入 python3.md（无独立章节）

## Why

python3.md 目前已包含 3.13 内容，且新增了 3.14 行，但还未将 3.14 的关键变化融入现有章节。为保持技术文档的时效性与体系化，需要在不新增“3.14 独立章节”的前提下，将 3.14 的语言/标准库/并发/调试改动融入对应主题章节。

## What Changes

- 不创建“Python 3.14 独立版本章节”，而是将新增内容分布式整合到既有主题章节；同时按照你的反馈，新增一个“大章节：调试与可观测性”，集中承载外部调试接口、REPL/CLI 可读性与 asyncio 自省等内容：
  - 注解与类型（第1章、第4章）：PEP 649/749（延迟求值与 annotationlib）、前向引用不再需要字符串、跨版本提示
  - 并发（第5章）：PEP 734（subinterpreters 与 concurrent.interpreters/InterpreterPoolExecutor）、PEP 779（无GIL自由线程版本官方支持）、Unix 默认 forkserver 行为调整、asyncio 调用图/自省能力
  - 高级表达式（第6章）：PEP 750 模板字符串字面量（t-strings），以及内置/语法微调如 map(strict=...)、memoryview 泛型、NotImplemented 布尔上下文报错
  - 异常（第7章）：PEP 758（except/except* 无需括号）、PEP 765（finally 离开控制流警告）、错误消息改进
  - 调试与可观测性（新增大章节）：外部调试接口与安全性（参考 PEP 768）、REPL/CLI 可读性、`faulthandler`/`tracemalloc`/结构化日志、asyncio 自省（任务栈等）
  - 标准库/平台与性能（后移一章）：PEP 784 zstandard 模块、新平台与构建（JIT 二进制、Android 发行、Emscripten tier 3）、增量 GC 说明
- 在版本演进表中保留已添加的 3.14 行；为每处新增内容提供最小可运行示例或简短对比片段。
- 风格保持与相邻段落一致，不引入内联 HTML；必要时补充参考链接（官方 What’s New 与 PEP）。

## Impact

- 受影响文件：content/zh/technologies/python3.md（主文档）
- 受影响章节：第1、4、5、6、7章 + 新增“调试与可观测性”大章节（导致后续章节顺延重编号），以及性能/平台相关处
- 质量保障：通过 markdownlint、本地 Hugo 预览验证；不改变站点构建与主题结构。
