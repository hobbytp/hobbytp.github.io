# Update Tasks: Python 3.14 融合

## 1. Implementation

- [x] 1.1 注解与类型：
  - 在第1章与第4章加入 PEP 649/749（延迟求值与 annotationlib）说明与最小示例
  - 更新前向引用说明（3.14 起通常无需字符串化），补充跨版本建议
  - 清理/合并对 PEP 563 的历史说明，避免读者混淆

- [x] 1.2 并发：
  - 在第5章加入 PEP 734：subinterpreters、concurrent.interpreters、InterpreterPoolExecutor 概念与示例
  - 说明 PEP 779：自由线程（无 GIL）版本的官方支持状态与注意事项
  - 记录 Unix 默认 forkserver 的变化及对 multiprocessing/ProcessPoolExecutor 的影响
  - 在 asyncio 小节补充调用图/自省工具的使用要点

- [x] 1.3 高级表达式与内置：
  - 在第6章新增 t-strings（PEP 750）小节，给出 1–2 个最小示例，与 f-strings 对比
  - 在合适小节加入 map(strict=...)、memoryview 泛型、NotImplemented 布尔上下文变更等要点

- [x] 1.4 异常与诊断：
  - 在第7章加入 PEP 758（except/except* 无需括号）与 PEP 765（finally 离开控制流警告）
  - 新增"大章节：调试与可观测性"，包含外部调试接口与安全（参考 PEP 768）、REPL/CLI 可读性、faulthandler/tracemalloc/结构化日志、asyncio 自省（任务栈等）；并相应顺延后续章节编号

- [x] 1.5 标准库/平台与性能：
  - 在（顺延后的）性能/平台章节加入：PEP 784（zstandard 模块）、JIT 二进制/Android 发行/Emscripten tier 3、增量 GC 说明
  - 在总结中以 1–2 句强化"3.14 的定位与趋势"

- [x] 1.6 校验：
  - 通过 markdownlint、本地 Hugo 预览检查
  - 与版本演进表（3.14 行）一致；无内联 HTML；链接可达
