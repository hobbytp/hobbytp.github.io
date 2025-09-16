---
title: TradingAgents 开源项目分析
date: "2025-07-03T23:03:00+08:00"
tags: ["tradingAgents", "architecture", "uml"]
categories: ["projects"]
draft: false
description: TradingAgents 开源项目分析
---
TradingAgents是一个多代理LLM金融交易框架，模拟真实交易公司的动态，通过部署各类专门的LLM驱动代理（如基本面分析师、情感分析师、新闻分析师、技术分析师、交易员及风险管理团队）协同分析市场并做出交易决策。这些代理通过动态协作讨论以定位最佳策略。框架适用于研究目的，并非提供金融建议。

- [Paper: TradingAgents: A Multi-Agent Framework for Financial Trading](https://arxiv.org/pdf/2412.20138)
- [Github: TradingAgents](https://github.com/TauricResearch/TradingAgents)

## 主要流程

TradingAgents 的工作流是基于LangGraph框架，设计为“多智能体金融交易框架”，模拟现实交易机构的操作流程。

**1. 多智能体协作架构**

- 包含不同角色的 LLM 智能体：基础面分析师、情绪分析师、新闻分析师、技术分析师、研究员（多空双方）、交易员、风险管理与投资组合经理等。
- 各智能体根据自己的职责，对市场和个股进行独立或协作分析。

**2. 工作流主要环节**

- **分析师团队**（Analyst Team）  
  - *基础面分析师*：评估公司财务数据、关键指标，挖掘内在价值与风险。  
  - *情绪分析师*：分析社交媒体与大众情绪，捕捉短期市场情绪波动。  
  - *新闻分析师*：监控全球新闻、宏观经济与重大事件。  
  - *技术分析师*：利用技术指标（如MACD、RSI等）寻找交易机会。

- **研究员团队**（Researcher Team）  
  - 由多头与空头研究员组成，围绕分析师提供的信息进行结构化辩论，平衡收益与风险。

- **交易员（Trader Agent）**  
  - 汇总分析员与研究员的报告，做出最终的交易决策，包括买卖时机与规模。

- **风险管理与投资组合经理**  
  - 持续评估持仓风险（如波动性、流动性等），调整交易策略，最终由投资组合经理批准交易方案，若通过则发送至模拟交易所执行。

**3. 自动化数据流与工具链支持**

- 各智能体通过统一接口（如 `get_simfin_cashflow`、`get_YFin_data` 等）自动拉取公司财报、行情、新闻、情绪等数据。
- 数据流自动化处理，支持回测与实盘模拟。
- 智能体可以自动调用工具链获取数据，生成报告、做出决策，并在团队内进行多轮讨论或辩论，形成最终行动方案。

**4. 可视化与决策**

- 框架中有不同流程图与结构图（如 README 里的 schema.png、analyst.png、researcher.png、trader.png、risk.png），帮助理解各角色的数据流和决策传递路径。

---

**简要流程图（摘自 README）**：

1. Analyst（四类分析师）→ 2. Researcher（辩论与整合）→ 3. Trader（决策与下单）→ 4. Risk & Portfolio Manager（风控与审批）→ 5. 交易执行

---

**总结**：  
TradingAgents 的工作流本质是“多智能体协作、分工明确、流程自动化”，通过角色分离和多轮协作，完成从分析、辩论、决策到风控和交易执行的全流程闭环。

如需了解任意环节的细节或代码实现，可进一步说明！
