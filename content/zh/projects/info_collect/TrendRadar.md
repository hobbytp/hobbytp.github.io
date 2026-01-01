---
title: "TrendRadar - 多平台热点聚合和AI智能分析"
date: 2025-12-05T00:00:00+08:00
lastmod: 2026-01-01T16:00:00+08:00
draft: false
tags: ["TrendRadar", "热点聚合", "AI智能分析"]
categories: ["projects"]
description: "TrendRadar 是一个用于多平台热点聚合和AI智能分析的开源项目，主要功能包括热点新闻监控、智能筛选及推送，同时支持基于MCP协议的深度分析。"
wordCount: 2029
readingTime: 6
---


## TrendRadar

TrendRadar ([github](https://github.com/sansan0/TrendRadar), 38k stars （截止2025-12）) 是一个用于多平台热点聚合和AI智能分析的开源项目，主要功能包括热点新闻监控、智能筛选及推送，同时支持基于MCP协议的深度分析。核心特点：

1. **功能概述**：
   - 聚合35个平台热点（知乎、抖音、B站、华尔街见闻等）。
   - 提供全网热点汇总（每日、当前榜单、增量监控三种模式）。
   - 智能推送：可按关键词筛选热点，并设定时间窗口。
   - 热点趋势分析：实时追踪新闻热度变化，支持跨平台对比。

2. **AI增强**：
   - AI对话分析功能，支持自然语言提问，进行热点趋势追踪、情感分析、相关检索等。
   - 提供本地测试数据，可利用Docker部署MCP服务支持AI使用。

3. **多渠道推送**：
   - 支持飞书、钉钉、企业微信、Telegram、Slack、邮件、Bark 等推送方式。
   - 管理多账号推送功能，适用于多种场景。

4. **便捷部署**：
   - 推荐使用Docker部署，30秒网页生成，1分钟手机通知，无需编程基础。
   - 项目遵循“Use this template”，避免 Fork。

5. **适用人群**：
   - 企业管理者、自媒体人、投资者和普通用户，用于品牌舆情监控、行业动态追踪及时事热点查看。

6. **更新特色**：
   - 新增多账号推送支持、全局过滤关键词、内容顺序配置等功能。
   - 文档优化，提供详细配置教程。

项目提供用户友好的设置选择，可快速高效地追踪和分析热点资讯，同时利用AI工具深度挖掘新闻数据。

## TrendRadar 源码分析

### **架构深度评价**

#### **1. 架构优势**

- **极致轻量与灵活部署**: 同时支持 GitHub Actions (无状态)、Docker (容器化) 和本地运行，通过 `StorageManager` 智能切换 SQLite/S3 存储，极大降低了使用门槛。
- **模块化核心设计**: 核心模块职责边界清晰 (Crawler, Core, Storage, Notification)，新增推送渠道符合开闭原则。
- **前瞻性 AI 融合**: 原生支持 MCP 协议，将传统爬虫转化为 AI Agent 的感知工具，提供自然语言日期解析和趋势分析等高级语义能力。

#### **2. 可扩展性**
- **数据源扩展**: 通用的 `DataFetcher` 接口和 RSS 模块设计证明了对异构数据源的良好兼容性。
- **AI 能力扩展**: FastMCP 2.0 架构使得新增 NLP 工具（如情感分析、摘要生成）非常便捷。

#### **3. 改进方向**
- **并发性能**: `DataFetcher` 目前采用串行抓取，面对大量数据源时 IO 阻塞将成为瓶颈，建议引入异步并发。
- **职责解耦**: `NewsAnalyzer` 类承担了过多编排职责，建议未来拆分为更细粒度的 Pipeline 模式。
- **配置管理**: `config.yaml` 日益庞大，建议引入强类型配置验证 (如 Pydantic) 以减少运行时错误。

---

本文档使用 UML 标准从多角度描述 TrendRadar 的架构设计，包括系统概览、核心组件、数据流、类结构等。

---

### 目录

1. [系统概览](#1-系统概览)
2. [核心功能与创新点](#2-核心功能与创新点)
3. [系统架构图](#3-系统架构图)
4. [组件架构](#4-组件架构)
5. [类图](#5-类图)
6. [时序图](#6-时序图)
7. [数据流图](#7-数据流图)
8. [部署架构](#8-部署架构)
9. [MCP 服务架构](#9-mcp-服务架构)

---

### 1. 系统概览

TrendRadar 是一个**轻量级热点新闻聚合与分析系统**，支持：

- 🔥 **全网热点聚合**：11+ 主流平台热榜数据抓取
- 📰 **RSS 订阅**：支持 RSS/Atom 订阅源
- 🤖 **AI 智能分析**：基于 MCP 协议的 17 种分析工具
- 📱 **多渠道推送**：飞书、钉钉、企业微信、Telegram、Slack、Email 等
- 🌐 **多环境部署**：GitHub Actions、Docker、本地运行

#### 1.2 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| 存储 | SQLite (本地) / S3 兼容存储 (远程) |
| MCP 服务 | FastMCP 2.0 |
| 部署 | Docker / GitHub Actions |

---

### 2. 核心功能与创新点

#### 2.1 核心功能

```mermaid
mindmap
  root((TrendRadar))
    数据采集
      热榜爬虫
        11+平台支持
        自动重试机制
        代理支持
      RSS订阅
        Atom/RSS解析
        按关键词分组
    智能分析
      关键词匹配
        必须词/过滤词
        词组化管理
      权重算法
        排名权重
        频率权重
        热度权重
    推送通知
      多渠道支持
        飞书/钉钉
        企业微信
        Telegram
        Slack/Email
      智能策略
        增量模式
        当日汇总
        时间窗口
    AI分析
      MCP协议
      17种工具
      自然语言交互
```

#### 2.2 核心创新点

| 创新点 | 描述 |
|--------|------|
| **统一存储抽象** | `StorageBackend` 抽象层支持本地 SQLite 和远程 S3，无缝切换 |
| **智能推送策略** | 三种模式（daily/current/incremental）+ 时间窗口控制 |
| **权重排序算法** | 基于排名、频率、热度的综合权重计算 |
| **MCP AI 分析** | 基于 Model Context Protocol 的 AI 分析能力，支持多客户端 |
| **多账号推送** | 所有渠道支持多账号配置，用 `;` 分隔 |

---

### 3. 系统架构图

#### 3.1 高层架构

```mermaid
graph TB
    subgraph External["外部系统"]
        API["NewsNow API"]
        RSS["RSS/Atom 源"]
        S3["S3 兼容存储"]
    end

    subgraph TrendRadar["TrendRadar 核心"]
        subgraph Crawler["数据采集层"]
            DF["DataFetcher"]
            RF["RSSFetcher"]
        end

        subgraph Core["核心处理层"]
            NA["NewsAnalyzer"]
            AN["Analyzer"]
            FQ["Frequency"]
        end

        subgraph Storage["存储层"]
            SM["StorageManager"]
            LS["LocalStorage"]
            RS["RemoteStorage"]
        end

        subgraph Notification["通知层"]
            ND["NotificationDispatcher"]
            SP["Splitter"]
            SD["Senders"]
        end

        subgraph Report["报告层"]
            RG["ReportGenerator"]
            HG["HTMLGenerator"]
        end
    end

    subgraph MCP["MCP AI 服务"]
        MS["MCP Server"]
        DQ["DataQuery"]
        AT["Analytics"]
        SS["SearchTools"]
    end

    subgraph Channels["推送渠道"]
        FS["飞书"]
        DT["钉钉"]
        WW["企业微信"]
        TG["Telegram"]
        SL["Slack"]
        EM["Email"]
    end

    API --> DF
    RSS --> RF
    DF --> NA
    RF --> NA
    NA --> AN
    NA --> FQ
    NA --> SM
    SM --> LS
    SM --> RS
    RS <--> S3
    NA --> ND
    ND --> SP
    SP --> SD
    SD --> Channels
    NA --> RG
    RG --> HG
    SM --> MS
    MS --> DQ
    MS --> AT
    MS --> SS
```

#### 3.2 模块结构

```mermaid
graph LR
    subgraph trendradar["trendradar 包"]
        main["__main__.py<br/>主入口"]
        context["context.py<br/>应用上下文"]
        
        subgraph core["core/"]
            analyzer["analyzer.py"]
            config["config.py"]
            data["data.py"]
            frequency["frequency.py"]
            loader["loader.py"]
        end
        
        subgraph crawler["crawler/"]
            fetcher["fetcher.py"]
            rss_pkg["rss/"]
        end
        
        subgraph storage["storage/"]
            base["base.py"]
            manager["manager.py"]
            local["local.py"]
            remote["remote.py"]
        end
        
        subgraph notification["notification/"]
            dispatcher["dispatcher.py"]
            senders["senders.py"]
            splitter["splitter.py"]
            renderer["renderer.py"]
        end
        
        subgraph report["report/"]
            generator["generator.py"]
            html["html.py"]
            formatter["formatter.py"]
        end
    end
    
    subgraph mcp_server["mcp_server 包"]
        server["server.py"]
        
        subgraph tools["tools/"]
            analytics["analytics.py"]
            data_query["data_query.py"]
            search_tools["search_tools.py"]
        end
        
        subgraph services["services/"]
            data_service["data_service.py"]
            cache_service["cache_service.py"]
            parser_service["parser_service.py"]
        end
    end

    main --> context
    main --> core
    main --> crawler
    main --> storage
    main --> notification
    main --> report
    server --> tools
    server --> services
```

---

### 4. 组件架构

#### 4.1 核心组件职责

```mermaid
graph TB
    subgraph Components["核心组件"]
        NA["NewsAnalyzer<br/>━━━━━━━━━━━━<br/>• 主编排器<br/>• 模式策略管理<br/>• 流程控制"]
        
        DF["DataFetcher<br/>━━━━━━━━━━━━<br/>• API 数据抓取<br/>• 自动重试<br/>• 代理支持"]
        
        SM["StorageManager<br/>━━━━━━━━━━━━<br/>• 后端选择<br/>• 环境检测<br/>• 统一接口"]
        
        AN["Analyzer<br/>━━━━━━━━━━━━<br/>• 词频统计<br/>• 权重计算<br/>• 新增检测"]
        
        ND["NotificationDispatcher<br/>━━━━━━━━━━━━<br/>• 多渠道分发<br/>• 多账号支持<br/>• 格式转换"]
        
        RG["ReportGenerator<br/>━━━━━━━━━━━━<br/>• HTML 生成<br/>• 内容格式化<br/>• 图片导出"]
    end

    NA --> DF
    NA --> SM
    NA --> AN
    NA --> ND
    NA --> RG
```

#### 4.2 组件交互

```mermaid
sequenceDiagram
    participant User as 用户/定时任务
    participant NA as NewsAnalyzer
    participant DF as DataFetcher
    participant SM as StorageManager
    participant AN as Analyzer
    participant ND as NotificationDispatcher
    participant RG as ReportGenerator

    User->>NA: 启动分析
    NA->>NA: 初始化配置
    NA->>SM: 初始化存储
    NA->>DF: 抓取热榜数据
    DF-->>NA: 返回原始数据
    NA->>SM: 保存新闻数据
    NA->>AN: 统计分析
    AN-->>NA: 返回统计结果
    NA->>RG: 生成HTML报告
    RG-->>NA: 返回HTML路径
    NA->>ND: 推送通知
    ND-->>NA: 推送结果
    NA-->>User: 完成
```

---

### 5. 类图

#### 5.1 数据模型

```mermaid
classDiagram
    class NewsItem {
        +str title
        +str source_id
        +str source_name
        +int rank
        +str url
        +str mobile_url
        +str crawl_time
        +List~int~ ranks
        +str first_time
        +str last_time
        +int count
        +to_dict() Dict
        +from_dict(data) NewsItem
    }

    class NewsData {
        +str date
        +str crawl_time
        +Dict~str,List~NewsItem~~ items
        +Dict~str,str~ id_to_name
        +List~str~ failed_ids
        +to_dict() Dict
        +from_dict(data) NewsData
        +get_total_count() int
        +merge_with(other)
    }

    class RSSItem {
        +str title
        +str feed_id
        +str feed_name
        +str url
        +str published_at
        +str summary
        +str author
        +str crawl_time
        +to_dict() Dict
        +from_dict(data) RSSItem
    }

    class RSSData {
        +str date
        +str crawl_time
        +Dict~str,List~RSSItem~~ items
        +Dict~str,str~ id_to_name
        +List~str~ failed_ids
        +to_dict() Dict
        +from_dict(data) RSSData
        +get_total_count() int
    }

    NewsData "1" *-- "*" NewsItem : contains
    RSSData "1" *-- "*" RSSItem : contains
```

#### 5.2 存储架构

```mermaid
classDiagram
    class StorageBackend {
        <<abstract>>
        +save_news_data(data) bool
        +get_today_all_data(date) NewsData
        +get_latest_crawl_data(date) NewsData
        +detect_new_titles(data) Dict
        +save_txt_snapshot(data) str
        +save_html_report(html, filename) str
        +is_first_crawl_today(date) bool
        +has_pushed_today(date) bool
        +record_push(report_type, date) bool
        +save_rss_data(data) bool
        +get_rss_data(date) RSSData
        +cleanup_old_data() int
    }

    class LocalStorageBackend {
        -str data_dir
        -str timezone
        -int retention_days
        -Connection db_conn
        +_get_db_path(date) str
        +_init_db(date)
        +_execute_query(sql, params)
    }

    class RemoteStorageBackend {
        -str bucket_name
        -str endpoint_url
        -str access_key
        -str secret_key
        -S3Client s3_client
        +_upload_file(local_path, remote_key)
        +_download_file(remote_key, local_path)
        +sync_to_local(days)
    }

    class StorageManager {
        -str backend_type
        -StorageBackend backend
        -bool pull_enabled
        -int pull_days
        +get_backend() StorageBackend
        +pull_from_remote() int
        +save_news_data(data)
        +get_today_all_data(date)
        +cleanup_old_data()
        +is_github_actions() bool
        +is_docker() bool
    }

    StorageBackend <|-- LocalStorageBackend
    StorageBackend <|-- RemoteStorageBackend
    StorageManager o-- StorageBackend : manages
```

#### 5.3 通知系统

```mermaid
classDiagram
    class NotificationDispatcher {
        -Dict config
        -Callable get_time_func
        -Callable split_content_func
        +dispatch_all(report_data, report_type, ...)
        -_send_to_multi_accounts(channel, config, func)
        -_send_feishu(report_data, ...)
        -_send_dingtalk(report_data, ...)
        -_send_wework(report_data, ...)
        -_send_telegram(report_data, ...)
        -_send_ntfy(report_data, ...)
        -_send_bark(report_data, ...)
        -_send_slack(report_data, ...)
        -_send_email(report_type, html_path)
    }

    class ContentSplitter {
        +split_content(content, max_size) List
        +estimate_size(content) int
        +split_for_feishu(content)
        +split_for_telegram(content)
        +split_for_dingtalk(content)
    }

    class Senders {
        <<module>>
        +send_to_feishu(webhook, content)
        +send_to_dingtalk(webhook, content)
        +send_to_wework(webhook, content)
        +send_to_telegram(token, chat_id, content)
        +send_to_ntfy(topic, content)
        +send_to_bark(url, content)
        +send_to_slack(webhook, content)
        +send_to_email(config, html_path)
    }

    class Renderer {
        <<module>>
        +render_feishu_content(stats, new_titles)
        +render_dingtalk_content(stats, new_titles)
        +render_markdown_content(stats, new_titles)
        +render_rss_feishu_content(rss_items)
        +render_rss_markdown_content(rss_items)
    }

    NotificationDispatcher --> ContentSplitter : uses
    NotificationDispatcher --> Senders : uses
    NotificationDispatcher --> Renderer : uses
```

---

### 6. 时序图

#### 6.1 增量模式工作流程

```mermaid
sequenceDiagram
    autonumber
    participant Timer as 定时器
    participant NA as NewsAnalyzer
    participant DF as DataFetcher
    participant SM as StorageManager
    participant DB as SQLite
    participant AN as Analyzer
    participant ND as Dispatcher

    Timer->>NA: 触发执行
    
    rect rgb(240, 248, 255)
        Note over NA,SM: 初始化阶段
        NA->>NA: 加载配置
        NA->>SM: 初始化存储管理器
        SM->>SM: 检测运行环境
        SM->>DB: 连接数据库
    end

    rect rgb(255, 248, 240)
        Note over NA,DF: 数据采集阶段
        NA->>DF: 抓取热榜数据
        loop 每个平台
            DF->>DF: fetch_data(platform_id)
            DF->>DF: 失败时自动重试
        end
        DF-->>NA: 返回 (results, id_to_name, failed_ids)
    end

    rect rgb(240, 255, 240)
        Note over NA,DB: 数据存储阶段
        NA->>NA: 转换为 NewsData
        NA->>SM: save_news_data(data)
        SM->>DB: INSERT/MERGE 新闻记录
    end

    rect rgb(255, 240, 255)
        Note over NA,AN: 分析阶段
        NA->>SM: detect_new_titles(current_data)
        SM->>DB: 查询历史标题
        SM-->>NA: 返回新增标题
        NA->>AN: count_word_frequency(results, ...)
        AN-->>NA: 返回统计结果
    end

    rect rgb(255, 255, 240)
        Note over NA,ND: 通知阶段
        alt 有新增内容
            NA->>ND: dispatch_all(report_data, ...)
            ND->>ND: 渲染各渠道内容
            ND->>ND: 分批推送
            ND-->>NA: 推送结果
        else 无新增
            NA->>NA: 跳过推送
        end
    end
```

#### 6.2 MCP 查询流程

```mermaid
sequenceDiagram
    autonumber
    participant Client as AI 客户端
    participant MCP as MCP Server
    participant DS as DataService
    participant SM as StorageManager
    participant DB as SQLite

    Client->>MCP: 调用工具 (如 search_news)
    MCP->>MCP: 解析参数
    MCP->>DS: query_news(keyword, date_range)
    DS->>SM: get_today_all_data(date)
    SM->>DB: SELECT * FROM news WHERE date = ?
    DB-->>SM: 返回记录
    SM-->>DS: NewsData
    DS->>DS: 过滤和排序
    DS-->>MCP: 查询结果
    MCP->>MCP: 格式化输出
    MCP-->>Client: JSON 响应
```

---

### 7. 数据流图

#### 7.1 数据处理流程

```mermaid
flowchart LR
    subgraph Input["数据输入"]
        API["NewsNow API"]
        RSS["RSS 源"]
    end

    subgraph Collect["数据采集"]
        DF["DataFetcher"]
        RF["RSSFetcher"]
    end

    subgraph Process["数据处理"]
        Parse["解析响应"]
        Convert["转换数据模型"]
        Merge["合并历史数据"]
    end

    subgraph Analyze["分析处理"]
        Match["关键词匹配"]
        Weight["权重计算"]
        Detect["新增检测"]
        Stats["统计汇总"]
    end

    subgraph Store["数据存储"]
        Local["本地 SQLite"]
        Remote["远程 S3"]
    end

    subgraph Output["输出"]
        HTML["HTML 报告"]
        Push["推送通知"]
        MCP["MCP 查询"]
    end

    API --> DF --> Parse
    RSS --> RF --> Parse
    Parse --> Convert --> Merge
    Merge --> Local
    Merge --> Remote
    Local --> Match
    Match --> Weight --> Detect --> Stats
    Stats --> HTML
    Stats --> Push
    Local --> MCP
```

#### 7.2 权重计算公式

```mermaid
graph LR
    subgraph Inputs["输入因子"]
        R["排名 (rank)"]
        F["出现频次 (count)"]
        H["热度值 (hotness)"]
    end

    subgraph Weights["权重配置"]
        RW["RANK_WEIGHT = 1.0"]
        FW["FREQUENCY_WEIGHT = 0.5"]
        HW["HOTNESS_WEIGHT = 0.3"]
    end

    subgraph Formula["计算公式"]
        W["weight = <br/>(threshold - avg_rank) × RW +<br/>count × FW +<br/>hotness × HW"]
    end

    subgraph Output["输出"]
        S["排序后的新闻列表"]
    end

    R --> W
    F --> W
    H --> W
    RW --> W
    FW --> W
    HW --> W
    W --> S
```

---

### 8. 部署架构

#### 8.1 部署模式

```mermaid
graph TB
    subgraph GitHub["GitHub Actions 部署"]
        GA["GitHub Actions"]
        GS["GitHub Secrets"]
        GP["GitHub Pages"]
        GA --> GS
        GA --> GP
    end

    subgraph Docker["Docker 部署"]
        DC["docker-compose"]
        DV["Volume 挂载"]
        DE["环境变量"]
        DC --> DV
        DC --> DE
    end

    subgraph Local["本地部署"]
        PY["Python 虚拟环境"]
        CF["config.yaml"]
        OP["output 目录"]
        PY --> CF
        PY --> OP
    end

    subgraph Storage["存储选择"]
        LS["本地 SQLite"]
        RS["远程 S3/R2"]
    end

    GitHub --> RS
    Docker --> LS
    Docker --> RS
    Local --> LS
```

#### 8.2 Docker 架构

```mermaid
graph TB
    subgraph Host["宿主机"]
        subgraph Container1["trendradar 容器"]
            App["Python 应用"]
            Cron["定时任务"]
        end
        
        subgraph Container2["trendradar-mcp 容器"]
            MCPApp["MCP Server"]
            Port["端口 3333"]
        end

        subgraph Volumes["数据卷"]
            Config["./config:/app/config"]
            Output["./output:/app/output"]
        end

        subgraph Network["网络"]
            Ext["外部网络"]
        end
    end

    App --> Config
    App --> Output
    MCPApp --> Config
    MCPApp --> Output
    MCPApp --> Port
    Port --> Ext
```

---

### 9. MCP 服务架构

#### 9.1 MCP 工具分类

```mermaid
mindmap
  root((MCP Tools))
    日期解析
      resolve_date_range
        自然语言解析
        标准日期输出
    数据查询
      get_latest_news
      get_news_by_date
      get_trending_topics
    RSS查询
      get_latest_rss
      search_rss
      get_rss_feeds_status
    智能搜索
      search_news
      find_related_news
      aggregate_news
    高级分析
      analyze_topic_trend
      analyze_data_insights
      compare_periods
    系统管理
      sync_from_remote
      get_storage_status
      list_available_dates
```

#### 9.2 MCP 服务架构

```mermaid
graph TB
    subgraph Clients["AI 客户端"]
        CD["Claude Desktop"]
        CS["Cherry Studio"]
        CU["Cursor"]
        CL["Cline"]
    end

    subgraph Transport["传输层"]
        STDIO["stdio 模式"]
        HTTP["HTTP 模式 (:3333)"]
    end

    subgraph Server["MCP Server"]
        FM["FastMCP 2.0"]
        
        subgraph Tools["工具层"]
            DQ["数据查询工具"]
            AT["分析工具"]
            ST["搜索工具"]
            SY["系统工具"]
        end

        subgraph Services["服务层"]
            DataSvc["DataService"]
            CacheSvc["CacheService"]
            ParserSvc["ParserService"]
        end
    end

    subgraph Data["数据层"]
        SM["StorageManager"]
        DB["SQLite"]
    end

    Clients --> STDIO
    Clients --> HTTP
    STDIO --> FM
    HTTP --> FM
    FM --> Tools
    Tools --> Services
    Services --> SM
    SM --> DB
```

#### 9.3 工具调用示例

```mermaid
sequenceDiagram
    participant User as 用户
    participant AI as AI 模型
    participant MCP as MCP Server
    participant Tool as 工具函数
    participant Data as 数据服务

    User->>AI: "分析本周 AI 相关新闻趋势"
    AI->>MCP: resolve_date_range("本周")
    MCP-->>AI: {start: "2026-12-26", end: "2026-01-01"}
    AI->>MCP: analyze_topic_trend("AI", date_range, "trend_tracking")
    MCP->>Tool: 调用分析工具
    Tool->>Data: 查询历史数据
    Data-->>Tool: 返回时序数据
    Tool->>Tool: 计算趋势
    Tool-->>MCP: 趋势分析结果
    MCP-->>AI: JSON 响应
    AI-->>User: "本周 AI 相关新闻呈上升趋势..."
```

---

### 附录

#### A. 配置文件结构

```yaml
# config/config.yaml 结构概览
app:
  enable_crawler: true
  report_mode: "daily"  # daily/current/incremental
  timezone: "Asia/Shanghai"

report:
  max_news_per_keyword: 10
  display_mode: "keyword"  # keyword/platform

notification:
  feishu_webhook_url: ""
  telegram_bot_token: ""
  # ... 其他渠道配置

storage:
  backend_type: "auto"  # local/remote/auto
  local_retention_days: 30
  remote_config:
    endpoint_url: ""
    bucket_name: ""

platforms:
  - zhihu
  - weibo
  - douyin
  # ... 更多平台

rss:
  enabled: false
  feeds: []
```

#### B. 数据库 Schema

```sql
-- 热榜新闻表
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    mobile_url TEXT,
    ranks TEXT,  -- JSON 数组
    first_time TEXT,
    last_time TEXT,
    count INTEGER DEFAULT 1,
    crawl_time TEXT,
    UNIQUE(source_id, title)
);

-- RSS 条目表
CREATE TABLE IF NOT EXISTS rss_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    published_at TEXT,
    summary TEXT,
    author TEXT,
    first_time TEXT,
    last_time TEXT,
    count INTEGER DEFAULT 1,
    crawl_time TEXT,
    UNIQUE(feed_id, title)
);

-- 推送记录表
CREATE TABLE IF NOT EXISTS push_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    push_time TEXT NOT NULL
);
```

---

*文档版本: v1.0.0 | 更新日期: 2026-01-01*

