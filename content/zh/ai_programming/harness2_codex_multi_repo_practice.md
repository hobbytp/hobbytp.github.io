---
title: "Harness² + CodeX 多代码库实践指南：构建企业级 AI 编程Harness与自进化体系"
date: "2026-10-21T14:30:00+08:00"
draft: false
tags: ["AI 编程", "Harness2", "CodeX", "多代码库", "Spring Boot", "Python", "Agent Harness", "Loop Engineering", "DevOps"]
categories: ["ai_programming"]
description: "本文详细记录如何将 Google Harness² 的Harness标准体系与递归自进化能力引入企业级多代码库项目（Java Spring Boot + Python + E2E 测试环境），解决跨仓库协同、上下文膨胀、危险操作拦截与经验自动沉淀等痛点，提供可直接抄作业的实操步骤与脚本源码。"
---

## 0. 前置认知：Harness² 智能体进化蓝图

在深入探讨企业级多代码库的工程落地之前，建议读者先翻阅下方这份完整的 **《Harness² 智能体进化蓝图》**。该文档系统性地梳理了智能体编程范式从早期的静态 Prompt 约束（Harness 1.0），跃迁至具备“动态技能按需加载、确定性工具总线、生命周期守卫、递归自进化反思”四维标准的 **Harness 2.0（CODEX_SURFACE）** 核心思想，帮助您建立清晰的理论底座：

{{< alert type="info" >}}
💡 **在线阅览提示**：下方已内嵌完整版《Harness² 智能体进化蓝图》PDF 文档，支持在线翻页、放大、全屏浏览以及一键下载。
{{< /alert >}}

{{< pdf src="/pdf/Harness2_Agent_Evolution_Blueprint.pdf" title="Harness² 智能体进化蓝图" height="650px" >}}

---

## 1. 背景与痛点：从单仓玩具到企业级多仓工程

在当前 AI 编程（如 CodeX、Claude Code、Antigravity 等）的普及过程中，许多开发者在单独一个小型项目（例如单体 Node.js 或单模块 Python 脚本）中能获得惊艳的体验。然而，一旦把 AI 引入企业级真实研发环境，尤其面对**多代码库（Multi-Repo）、异构技术栈（如 Java Spring Boot 与 Python 混合架构）以及长链路端到端集成测试**时，通常会迅速陷入以下几大典型困境：

1. **上下文爆炸与漂移**：多仓库代码总量动辄数百万行，直接将所有背景信息塞入 Prompt 会迅速挤爆上下文窗口（Context Window），导致模型注意力稀释、生成幻觉代码。
2. **跨仓库契约不一致**：前端/调度服务用 Python，后端核心业务用 Java，修改一个 API 很容易造成 REST DTO 字段不匹配或类型断裂。
3. **缺乏安全防护壁垒**：AI 可能会执行诸如 `git reset --hard`、`git push --force` 或误删生产配置等危险破坏性命令。
4. **验证流程割裂**：每个子仓库的构建测试命令不同（Maven/Gradle、pytest/unittest、E2E 脚本），AI 无法自动完成多层次的分级闭环验证。
5. **“从不长记性”的重复踩坑**：上一次任务调试解决的依赖冲突或环境陷阱，在下一次全新会话中会被 AI 彻底遗忘。

针对上述难题，Google 提出的 **Harness²（Harness工程 2.0 / Agent Harness）** 标准体系给出了系统性的工程化答案：**不要把 AI 仅仅当成代码补全器，而是围绕 AI 建立一套由“总控Harness + 按需专家技能 + 确定性脚本 + 生命周期守卫 + 递归自进化反思”组成的坚固底盘。**

本文将以一个真实的企业级混合架构项目（代号 **LCM**，包含多个 Java Spring Boot 核心服务、Python 任务调度服务以及独立平台 E2E 测试环境）为例，详细拆解如何将 Harness² 体系无缝嫁接到 CodeX 中，并提供可直接复制落地的实践规范。

---

## 2. 总体架构：多代码库的 Harness² 拓扑设计

在多代码库环境下，我们不能把Harness散落在各个孤立的子仓库中，而是在**多代码库的父级总控目录**建立全局Harness，同时保持下属各子仓库的轻量与自治。

Harness2 能将 Codex 作为底层执行器（Substrate）的核心机制在于**执行底座抽象与文件级组件映射（Substrate Abstraction & File Mapping）**。Harness2 将智能体脚手架（Harness）解耦为 8 个可重写的独立文件组件，当通过 `--substrate cx` 参数指定 Codex 底座时，系统会自动将常驻系统提示词与护栏整合映射至 Codex 原生支持的 `AGENTS.md` 统一配置文件中，而按需调用的技能（skills）、脚本（scripts）与插件（plugins）等则保持标准目录映射；通过这种统一的文件接口适配，Harness2 的双层递归优化回路（Propose–Probe–Compose）能够在完全不改变模型神经网络权重的的前提下，直接通过动态重写 Codex 挂载的外围配置文件，无缝且精准地重构 Codex 运行时的上下文构造、工具调用与任务执行行为。而用户在编程完成一定任务后，可以通过CodeX对话来要求沉淀之前的经验到Harness来形成闭环。


### 2.1 整体拓扑图

```mermaid
flowchart TD
    subgraph Control_Layer ["顶层控制与Harness总线"]
        AGENTS["AGENTS.md (全局契约与触发索引 <8KB)"]
        HOOKS[".codex/hooks.json (生命周期守卫与危险拦截)"]
        SUB_AGENTS["sub_agents/ (架构师 & 审查员专属代理)"]
    end

    subgraph Dynamic_Skills ["按需动态技能库 (.agents/skills/)"]
        SKILL_TDD["tdd-workflow (Spring Boot / Django TDD)"]
        SKILL_CR["code-review (事务 / N+1 / 幂等性审查)"]
        SKILL_DIAG["diagnosing-bugs (Bean冲突 / 懒加载 / 序列化)"]
        SKILL_SYNC["multi-repo-sync (Java 与 Python DTO 契约)"]
        SKILL_E2E["vm-e2e (端到端集成测试规范)"]
    end

    subgraph Deterministic_Tools ["确定性执行工具 (scripts/)"]
        CHECK_WS["check_workspace.py (多仓库 Git 状态巡检)"]
        RUN_CHECKS["run_checks.py (分级验证统一入口)"]
        REFLECT["reflect_experience.py (经验沉淀自进化反思器)"]
    end

    subgraph Repositories ["业务与测试代码库群"]
        REPO_PY["python-connect (Python / Django / Celery)"]
        REPO_JAVA1["platform-lcm (Java Spring Boot 核心)"]
        REPO_JAVA2["sdwan-manager (Java 控制面)"]
        REPO_E2E["platform-support-design (VM 生命周期 E2E 框架)"]
    end

    CodeX((CodeX Agent)) <--> Control_Layer
    Control_Layer -.-> Dynamic_Skills
    Control_Layer -.-> Deterministic_Tools
    Deterministic_Tools --> Repositories
    Dynamic_Skills -.-> Repositories
```

### 2.2 目录结构清单与交付契约

```text
D:\Company\Codes\LCM\                   # 多代码库总根目录（工作区）
├── AGENTS.md                          # [核心指令与总Harness] 全局规范、多仓协同规则、技能自动触发索引 (<8KB)
├── .agents/
│   └── skills/                        # [按需动态技能库] 只有触发匹配时才加载对应内容
│       ├── tdd-workflow/
│       │   └── SKILL.md               # 技能1：Spring Boot + Django 测试先行与回归
│       ├── code-review/
│       │   └── SKILL.md               # 技能2：高标准代码审查（事务、空安全、N+1）
│       ├── diagnosing-bugs/
│       │   └── SKILL.md               # 技能3：跨服务调用、Bean冲突、Celery故障排查
│       ├── multi-repo-sync/
│       │   └── SKILL.md               # 技能4：跨模块依赖查找与 Python/Java REST DTO 兼容
│       └── vm-e2e/
│           └── SKILL.md               # 技能5：端到端集成测试、状态账本验证与执行入口
├── scripts/                           # [确定性辅助工具] 消除 AI 随意拼凑命令的不确定性
│   ├── check_workspace.py             # 脚本1：多代码库分支与未提交变动一键巡检
│   ├── run_checks.py                  # 脚本2：跨仓库编译/类型检查/单元测试/E2E统一分级执行器
│   └── reflect_experience.py          # 脚本3：Harness² 经验反思器（自动提炼经验写回 AGENTS.md）
├── sub_agents/                        # [独立角色代理]
│   ├── architect/
│   │   └── AGENT.md                   # 架构师角色：负责跨库接口设计与重构方案制定
│   └── reviewer/
│       └── AGENT.md                   # 审查员角色：负责质量验收与提交规范审查
├── .codex/
│   └── hooks.json                     # [生命周期钩子] 拦截危险命令 (rm -rf, git reset) + 语法格式化
├── python-connect/                    # 子仓库 A：Python 业务服务
├── platform-lcm/                      # 子仓库 B：Java Spring Boot 核心业务
├── sdwan-manager/                     # 子仓库 C：Java 集群控制服务
└── platform-support-design/           # 子仓库 D：底层 VM 生命周期端到端测试仓
```

---

## 3. 分步实施落地指南

### 第一步：编写极简全局总控Harness（`AGENTS.md`）

#### 为什么必须保持极简（<8KB）？
在 Harness² 规范中，**`AGENTS.md` 是每次交互常驻系统上下文的根指令**。如果把数万字的架构说明、测试文档全塞进 `AGENTS.md`，会严重浪费 Token 预算并干扰模型的推理能力。正确的做法是：
- `AGENTS.md` 只保留**核心原则、多仓工作区拓扑、工具契约**以及**技能自动唤醒索引表**。
- 具体的工程细节全部拆分到各个 `SKILL.md` 中，利用语义触发按需动态加载。

#### 核心代码配置示例：
在已有 `AGENTS.md` 的基础上，增量补充如下Harness声明区（保留已有业务说明）：

```markdown
# Multi-Repo Master Engineering Harness (Harness² Standard)

## 1. Workspace Topology & Repositories
- `python-connect`: Python/Django/Celery service.
- `platform-lcm`: Java Spring Boot core management service.
- `sdwan-manager`: Java cluster controller.
- `platform-support-design`: End-to-end VM lifecycle test suite and tools.

## 2. Universal Engineering Rules
- **No Direct Destructive Commands**: Never execute `git reset --hard`, `git push --force`, or unverified deletions.
- **Verification First**: Always run local verification via `scripts/run_checks.py` before completing any task.
- **Multi-Repo DTO Consistency**: When modifying API payloads, maintain backward compatibility across Java and Python.

## 3. Dynamic Skills Trigger Mapping
Read the corresponding SKILL.md ONLY when the task matches the trigger:
- When writing new features or fixing bugs, read `.agents/skills/tdd-workflow/SKILL.md`.
- When reviewing pull requests or code quality, read `.agents/skills/code-review/SKILL.md`.
- When diagnosing complex exceptions or stack traces, read `.agents/skills/diagnosing-bugs/SKILL.md`.
- When modifying cross-repo APIs or DTOs between Python and Java, read `.agents/skills/multi-repo-sync/SKILL.md`.
- When preparing or running VM lifecycle End-to-End integration tests, read `.agents/skills/vm-e2e/SKILL.md`.

## 4. Deterministic Scripts Contract
- Workspace check: `python scripts/check_workspace.py`
- Fast checks: `python scripts/run_checks.py [all|python|ecr|v2-mgr|e2e]`
- Reflection & Lesson Record: `python scripts/reflect_experience.py --category <Category> --lesson "<Lesson>"`
```

---

### 第二步：建立按需触发的专家技能库（`.agents/skills/`）

技能文件（`SKILL.md`）需要具备标准的结构与操作步骤。以下是多仓实践中最关键的两个技能定义：

#### 技能 A：跨仓库 DTO 协同（`.agents/skills/multi-repo-sync/SKILL.md`）
跨语言代码库最容易发生字段命名不一致（如蛇形命名 `snake_case` 与驼峰命名 `camelCase`）、枚举值缺失等。

```markdown
---
name: multi-repo-sync
description: Cross-repository API, REST DTO, and data contract alignment between Python and Java
---

# Multi-Repo Contract Synchronization Workflow

## 1. Inspection Checklist
1. Identify the Producer and Consumer:
   - If Python produces JSON: Check Jackson deserialization annotations (`@JsonProperty`) in Java.
   - If Java produces JSON: Check serializer/pydantic models in Python.
2. Field naming conventions:
   - Ensure case mappings (`camelCase` vs `snake_case`) are explicitly declared.
3. Enum sync:
   - When adding a state in Java enum, immediately sync the Python choice enum.

## 2. Verification Protocol
1. Modify the DTO definitions in both repositories simultaneously.
2. Run unit tests in both repositories using `python scripts/run_checks.py python` and `python scripts/run_checks.py ecr`.
```

#### 技能 B：全链路端到端集成测试（`.agents/skills/vm-e2e/SKILL.md`）
在我们的项目里，`platform-support-design` 是端到端测试的总控仓。该技能直接规范了调用真实系统时的核心原则：

```markdown
---
name: vm-e2e
description: End-to-End VM lifecycle integration testing via platform-support-design tools
---

# VM Lifecycle E2E Testing Protocol

## Core Rules
1. **Never use test backdoors**: All tests must invoke the actual public APIs.
2. **HTTP 200 != Success**: Always verify against the state ledger (database & NetBox records) to confirm real VM provisioning.
3. **Platform Token Lifecycle**: Long-term reuse of existing environment tokens; do not generate transient tokens.

## Execution Procedure
- Preflight environment check:
  `python platform-support-design/tools/e2e.py check --env <profile.json>`
- Run Smoke test suite:
  `python platform-support-design/tools/e2e.py run --env <profile.json> --suite smoke`
- Cleanup test resources safely:
  `python platform-support-design/tools/e2e.py clean --env <profile.json>`
```

---

### 第三步：编写确定性工作区工具（`scripts/`）

让 AI 在终端中自由猜测、手动敲 `cd xxx && git status` 是极其低效且容易出错的。Harness² 强调使用**确定性的脚本（Deterministic Tools）**封装高频复杂动作。

#### 1. 多代码库状态巡检脚本：`scripts/check_workspace.py`
在开始任何复杂任务前，CodeX 首先运行该脚本，一眼看清所有子模块当前位于什么分支、有多少未提交的修改，避免把代码写错分支或覆盖同事的改动。

```python
#!/usr/bin/env python3
"""
scripts/check_workspace.py
Inspect git branches, working tree states, and recent commits across all sub-repos.
"""
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def check_repo(repo_dir: Path):
    if not (repo_dir / ".git").exists():
        return None
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=repo_dir, text=True
        ).strip() or "DETACHED"
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_dir, text=True
        )
        modified = staged = untracked = 0
        for line in status_out.splitlines():
            if not line:
                continue
            x, y = line[0], line[1]
            if x in "MADRC":
                staged += 1
            if y in "MADRC":
                modified += 1
            if x == "?" and y == "?":
                untracked += 1
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%h %s"], cwd=repo_dir, text=True
        ).strip()[:30]
        return {
            "name": repo_dir.name,
            "branch": branch,
            "msu": f"{modified}/{staged}/{untracked}",
            "commit": commit,
        }
    except Exception as e:
        return {"name": repo_dir.name, "branch": "ERR", "msu": "-", "commit": str(e)}

def main():
    print("=" * 80)
    print(f"{'Repository':<25} | {'Branch':<20} | {'M/S/U':<8} | {'Recent Commit'}")
    print("-" * 80)
    for item in sorted(WORKSPACE_ROOT.iterdir()):
        if item.is_dir() and (item / ".git").exists():
            info = check_repo(item)
            if info:
                print(f"{info['name']:<25} | {info['branch']:<20} | {info['msu']:<8} | {info['commit']}")
    print("=" * 80)
    print("M/S/U: Modified / Staged / Untracked files")

if __name__ == "__main__":
    main()
```

**运行效果实测输出：**


#### 分级验证统一入口：`scripts/run_checks.py`
支持轻量级单模块验证与重量级全链路验证（支持 `all`, `python`, `ecr`, `v2-mgr`, `e2e` 参数），帮助 AI 形成标准化的自检循环。

```python
#!/usr/bin/env python3
"""
scripts/run_checks.py
Unified tiered verification runner for Java, Python, and E2E testing suites.
"""
import sys
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent

def run_cmd(cmd, cwd):
    print(f"\n>>> Running: {' '.join(cmd)} in {cwd}")
    ret = subprocess.run(cmd, cwd=cwd)
    return ret.returncode == 0

def check_python():
    py_dir = WORKSPACE / "python-connect"
    return run_cmd(["pytest", "-m", "unit"], cwd=py_dir)

def check_ecr():
    ecr_dir = WORKSPACE / "platform-lcm"
    mvn_cmd = "mvn.cmd" if sys.platform == "win32" else "mvn"
    return run_cmd([mvn_cmd, "test-compile"], cwd=ecr_dir)

def check_e2e():
    e2e_runner = WORKSPACE / "platform-support-design" / "tools" / "e2e.py"
    print(f"\n>>> Preflight E2E check using runner: {e2e_runner}")
    return run_cmd([sys.executable, str(e2e_runner), "--help"], cwd=WORKSPACE)

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = {}
    if target in ("python", "all"):
        results["python"] = check_python()
    if target in ("ecr", "all"):
        results["ecr"] = check_ecr()
    if target in ("e2e", "all"):
        results["e2e"] = check_e2e()

    print("\n" + "=" * 40)
    print("Verification Summary:")
    for k, ok in results.items():
        print(f"  {k:<14}: {'PASS' if ok else 'FAIL'}")
    print("=" * 40)
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### 第四步：生命周期守卫（`.codex/hooks.json`）

通过在 `.codex/` 下声明生命周期拦截规则，在 CodeX 试图调用 Bash 命令前进行规则扫描，杜绝恶意或误操作指令；在编辑代码后自动触发格式化：

```json
{
  "version": "1.0",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool_name == 'execute_bash' && (args.command.contains('reset --hard') || args.command.contains('--force'))",
        "action": "BLOCK",
        "message": "Security Block: Destructive Git commands (reset --hard, force push) are strictly prohibited."
      },
      {
        "matcher": "tool_name == 'execute_bash' && args.command.contains('rm -rf /')",
        "action": "BLOCK",
        "message": "Security Block: High-risk recursive deletion intercepted."
      }
    ],
    "PostToolUse": [
      {
        "matcher": "tool_name == 'edit_file' && (file_path.endsWith('.java') || file_path.endsWith('.py'))",
        "action": "NOTIFY",
        "message": "Source code edited. Please ensure formatting passes and run 'python scripts/run_checks.py' for quick regression check."
      }
    ]
  }
}
```

---

### 第五步：自进化经验反思机制（Harnessing-level Recursion）

这是 Harness² 最精妙的体系之一——**递归自我进化（Reflection）**。
每次 CodeX 排查完一个环境依赖报错（比如某版本 Jackson 无法反序列化特定日期格式，或者 Celery 在 Windows 下需使用 `--pool=solo` 等），我们无需每次在会话里反复强调，而是由反思器脚本自动格式化并写入 `AGENTS.md` 的“踩坑经验库”中。

#### 经验反思脚本：`scripts/reflect_experience.py`

```python
#!/usr/bin/env python3
"""
scripts/reflect_experience.py
Append lessons learned during debugging directly into AGENTS.md.
"""
import argparse
from datetime import datetime
from pathlib import Path

AGENTS_FILE = Path(__file__).resolve().parent.parent / "AGENTS.md"

def append_lesson(category: str, lesson: str):
    if not AGENTS_FILE.exists():
        print(f"Error: {AGENTS_FILE} does not exist.")
        return

    content = AGENTS_FILE.read_text(encoding="utf-8")
    header = "## 5. Lessons Learned & Troubleshooting Ledger (Auto-Reflected)"
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    record = f"- [{timestamp}] **[{category}]**: {lesson}\n"

    if header not in content:
        content += f"\n\n{header}\n{record}"
    else:
        parts = content.split(header)
        content = parts[0] + header + "\n" + record + parts[1].lstrip("\n")

    AGENTS_FILE.write_text(content, encoding="utf-8")
    print(f"Successfully recorded lesson into AGENTS.md under [{category}].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harness² Reflection Recorder")
    parser.add_argument("--category", required=True, help="Category (e.g., Java, Python, E2E, Git)")
    parser.add_argument("--lesson", required=True, help="Detailed lesson or pitfall to avoid")
    args = parser.parse_args()

    append_lesson(args.category, args.lesson)
```

**使用方式：**
当 AI 攻克难题后，开发者只需对 CodeX 说一句：
> *"请将本次修复 Celery 序列化异常的排查教训沉淀进 Harness。"* 或者
> *""请将本次调试遇到的教训沉淀到 Harness 中"。"*

CodeX 即可自发执行：
```bash
python scripts/reflect_experience.py --category Python --lesson "Celery 5.x 传输 LocalDateTime 时必须显式注册 ISO8601 json 编码器，否则报 Object of type datetime is not JSON serializable"
```
下一轮会话启动时，CodeX 就会在 `AGENTS.md` 中天然继承这条教训，实现**代码库级别的记忆延续**。

---

## 4. 端到端实战流程演示

当这套 Harness² 体系配置完成后，日常使用 CodeX 在多代码库中工作的典型闭环流程如下：

```mermaid
sequenceDiagram
    autonumber
    actor Dev as 开发者
    participant Agent as "CodeX Agent"
    participant Script as "scripts/ 工具层"
    participant Skill as ".agents/skills/"
    participant Hook as ".codex/ 守卫"

    Dev->>Agent: "在 platform-lcm 中新增 VM 取消提交接口，并让 Python 端兼容"
    Agent->>Script: 执行 check_workspace.py 获取多仓当前分支与状态
    Script-->>Agent: 确认都在 feature_ESDWAN-8051 分支
    Agent->>Skill: 自动匹配激活 multi-repo-sync 与 tdd-workflow
    Skill-->>Agent: 获取 DTO 对齐与 JUnit5 测试规范
    Agent->>Hook: 尝试提交更改并执行单元测试
    Hook-->>Agent: 验证无危险命令，提示运行回归检查
    Agent->>Script: 运行 run_checks.py ecr 与 python
    Script-->>Agent: 单元测试全绿 (PASS)
    Dev->>Agent: "将新接口在真实环境进行 Smoke 验证"
    Agent->>Skill: 自动匹配激活 vm-e2e 技能
    Agent->>Script: 运行 platform-support-design/tools/e2e.py run --suite smoke
    Script-->>Agent: E2E 验证通过
    Dev->>Agent: "提炼经验并沉淀"
    Agent->>Script: 运行 reflect_experience.py 写入 AGENTS.md
```

1. **第一步（感知现状）**：CodeX 自动运行 `check_workspace.py`，确认所有涉及的仓库处于同一个特性分支 `feature_ESDWAN-8051`，防止误写错分支。
2. **第二步（按需加载技能）**：由于涉及跨仓库与新接口开发，CodeX 自动索引读取 `.agents/skills/multi-repo-sync/SKILL.md` 和 `tdd-workflow/SKILL.md`，严格遵照 DTO 字段对齐规范和测试先行原则。
3. **第三步（分级快速验证）**：开发完成后，CodeX 运行 `python scripts/run_checks.py all` 确保 Java 编译通过、Python 单测无回归。
4. **第四步（真实环境集成）**：针对涉及虚拟机生命周期的操作，CodeX 调用 `vm-e2e` 技能，通过 `platform-support-design/tools/e2e.py` 执行端到端环境检查与 Smoke 冒烟套件。
5. **第五步（经验沉淀）**：任务结束前，自动反思本次修改注意点，写入全局 `AGENTS.md`，完成自进化闭环。

---

## 5. 多代码库 AI Harness工程的避坑指南

在实际把这套方案应用到您自己的多仓项目时，建议牢记以下四项经验法则：

1. **坚持 AGENTS.md 尺寸极简法则**：
   - 始终确保根目录 `AGENTS.md` 小于 8KB（通常在 100~150 行以内）。
   - 将所有业务细节、长篇架构文档、数据库字典下沉为 `.agents/skills/xxx/SKILL.md`。只有当用户提问命中触发词时，才通知 Agent 进目录去读。
2. **确定性脚本大于自由发散提示词**：
   - 如果某个操作流程（如仓库巡检、打包测试、日志收集）可以用 Python 或 Shell 稳定执行，**务必写成脚本**，然后让 AI 去调用脚本，绝不要让 AI 在终端里每次凭空拼接一长串 `find`、`grep` 和 `git` 命令。
3. **分级测试隔离策略**：
   - 区分“轻量单元测试”与“全链路 E2E 测试”。在代码编写过程中，只要求 AI 频繁运行单测；仅在明确集成验收阶段，才激活重量级的 E2E 测试运行器，节约开发周期。
4. **守护 Git 洁净度**：
   - 坚决通过生命周期钩子禁止硬重置（`git reset --hard`）和强推（`push --force`），在多仓库并行修改时，代码版本安全是第一准则。

---

## 6. 进阶探索与未来演进：Harness² 原生自动化调度闭环

虽然本文落地的高性价比Harness体系已经足以支撑绝大部分日常研发场景，但在 Google Harness² 的完整设计蓝图中，除了上述“Harness资产结构（Harnessing）”外，还包含了一项尚未在本次第一阶段实践中强行启用的高阶机制——**无人值守的自动化算法流水线（Task-level Recursion）**。

理解这一机制的运行原理、技术取舍以及未来演进路径，有助于我们在面临更大规模自动化研发任务时做出科学决策。

### 6.1 Task-level Recursion 的运作机制

在 Harness² 理论体系中，实际上划分了两个层次的递归循环：
1. **Harness级自进化（Harnessing-level Recursion）**：即本文在第三步第 5 小节落地的形态——通过经验反思脚本，将排错踩坑教训自动提炼并沉淀回 `AGENTS.md`，使Harness底盘越用越聪明；
2. **任务级递归流水线（Task-level Recursion）**：原生 Harness² 提供的一套面向特定需求或缺陷修复的全自动调度闭环，其运作拓扑如下：

```mermaid
flowchart TD
    INPUT["用户任务输入 (Task / Issue / Bug)"] --> PROPOSER["Harness Editor (Proposer)<br/>针对该任务自动生成 2~4 个候选提示词与测试脚本"]
    PROPOSER --> PROBING["Parallel Probing (并发试跑探索)<br/>并行启动 4 个独立的 Codex 进程沙箱分别试跑任务"]
    PROBING --> COMPOSER["Harness Composer (轨迹对比与合成)<br/>比较 4 个执行轨迹与验证结果，合成出最优解代码"]
    COMPOSER --> OUTPUT["最终交付代码 / 候选 Pull Request"]
```

```text
[用户任务输入]
     │
     ▼
[Harness Editor (Proposer)]  ──自动针对该任务生成 2~4 个候选提示词/测试脚本
     │
     ▼
[Parallel Probing]           ──并行启动 4 个独立的 Codex 进程分别试跑该任务
     │
     ▼
[Harness Composer]           ──比较 4 个执行轨迹，合成出最终的最优代码
```

### 6.2 为什么在现阶段人机协同中暂未引入该调度器？

在本次的多代码库企业落地实践中，我们选择先建立扎实的Harness工程基底，而暂缓启动 Harness² 原生调度器，主要出于以下两点技术考量：

1. **交互形态与响应诉求不同（实时协作 vs 离线批处理）**：
   - **日常人机协同（Pair-Programming）**：开发者在终端或 IDE 中与 CodeX 紧密结对，需要的是**即时响应、低延迟、全过程可观测可审查**的开发体验。
   - **Propose-Probe 闭环**：本质上是一种**离线批处理模式（Batch Sweep）**。每解决一个需求，调度器背后都需要调用 LLM 启动 4 个以上的并行会话进行对比探索，Token 消耗和执行耗时呈数倍增加（更适合学术基准刷榜或夜间无人值守任务）。
2. **操作系统与运行时环境依赖**：
   - Harness² 的调度引擎和 Bridge 深度依赖 POSIX/Linux 环境与后台 LiteLLM 服务；
   - 在 Windows 本地直接驱动多实例并行沙箱与容器隔离相对繁琐，容易将过多精力消耗在底座环境虚拟化上，违背了“务实快速落地”的初衷。

### 6.3 未来适用场景与平滑演进路径

尽管当前暂未开启调度器，但这套多代码库Harness已经为后续升级预留了极佳的接口。当出现以下业务场景时，引入该调度闭环将展现出极高价值：

- **典型场景：夜间无人值守与批量缺陷修复**：
  例如版本发布前有 20 个低危 Jira 缺陷积压，我们可以在夜间将其输入自动化队列，由 AI 自动并发探索修复，并在后台自动执行跨库单元测试与 E2E 验证，次日清晨直接输出对比择优后的修复报告与 Pull Request。
- **推荐部署路径**：
  后续无需改造现有的业务代码仓，我们可以在 **WSL2**（Windows Subsystem for Linux）或独立 Linux 服务器中把 `harness2` 框架的自动化调度器部署运行起来，将既有的多代码库根目录（如 `LCM`）直接作为评测目标（Target），即可实现从“人机结对”到“全自动 Propose-Probe-Compose 调度”的无缝对接。

---

## 7. 总结与后续落地建议

将 Google Harness² 的设计理念落地到多代码库项目，本质上是将 AI 辅助编程从**“随机碰运气的 Prompt 问答”**转变为**“规范受控的系统工程（Harness Engineering）”**。

综合本次实践，我们为企业级多代码库项目引入 AI 编程提供分阶段的落地建议：

1. **立足当下（日常人机协同）**：
   **目前搭建的Harness体系（极简总控 + 按需动态技能 + 确定性脚本 + 生命周期守卫 + 经验反思）已经完全足够且是当前最高效的落地形态。** 开发者在终端与 IDE 中可以直接享受多仓库协同、TDD 测试驱动、E2E 测试唤醒与安全拦截能力。
2. **面向未来（批量自动化与离线自治）**：
   当日常工程规范与验证工具链足够稳固、且面临大规模离线批量任务时，可以通过 WSL2 平滑接入 Harness² 原生的任务级自动化调度闭环（Task-level Recursion），构建全自动的 Propose-Probe-Compose 智能体集群。

希望本文的拓扑架构、实施细节与演进思考，能为正在探索大中型异构项目 AI 编程工程化的团队提供实用、可靠的参考样板！

