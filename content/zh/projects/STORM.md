---
title: "STORM - 通过检索和多视角提问来合成主题大纲和维基百科类文章"
date: "2024-06-14T14:30:00+08:00"
lastmod: "2024-06-20T22:30:00+08:00"
draft: false
tags:  ["STORM","Co-STORM","LangGraph","Deep Research"]
categories: ["projects"]
description: "STORM - 通过检索和多视角提问来合成主题大纲和维基百科类文章"
---


1. STORM 是什么？它的主要目标是什么？
STORM（通过检索和多视角提问来合成主题大纲）是一个基于大型语言模型（LLM）的写作系统，旨在从零开始编写结构良好、内容丰富的长篇文章，其广度和深度可与维基百科页面媲美。它的主要目标是自动化文章写作的“预写作阶段”，这包括研究给定主题和在开始写作之前准备大纲。

2. STORM 如何处理预写作阶段？
STORM 通过以下几个关键步骤来处理预写作阶段：

- 发现不同视角： 它通过考察与给定主题相关的现有维基百科文章，识别研究该主题的不同视角。
- 模拟对话： 它模拟不同视角的写作者与一个主题专家（基于可信互联网来源）之间的对话。在这些多轮对话中，写作者（LLM）根据当前主题、其特定视角和对话历史提问，而专家（LLM与检索系统结合）则根据搜索到的信息回答问题。
- 策划信息并创建大纲： 基于收集到的信息和 LLM 的内在知识，STORM 策划这些信息并创建一个详细的大纲。这个大纲随后可以逐节扩展，形成一篇完整的文章。

3. STORM 系统在生成文章时采用了哪些核心技术或方法？
STORM 系统核心采用了检索增强生成（RAG）方法，特别是通过“多视角提问”和“模拟对话”来增强检索过程。它不像传统的 RAG 系统可能只进行一次检索，而是通过模拟专家访谈式的多轮对话来引导信息检索和知识收集。此外，它利用 LLM 的能力从相关文章中识别视角并根据这些视角生成有针对性的问题，从而确保收集到更全面和深入的信息。

4. 为什么 STORM 强调“预写作阶段”？这个阶段为何重要？
预写作阶段在人类写作过程中至关重要，它涉及信息收集和整理（即研究）。研究表明，成功的学术写作很大程度上依赖于大纲的规划、起草和校对。STORM 强调预写作是因为高质量的长篇文章需要基于扎实的、有条理的研究。通过自动化这个阶段，STORM 可以帮助写作者克服从零开始研究一个新主题的挑战，确保文章的 groundedness（基于事实）和全面性。

5. STORM 如何利用“视角”来指导信息收集？
STORM 利用“视角”作为先验知识来引导 LLM 提出更有深度的问题。就像商业中的利益相关者理論认为不同利益相关者关注公司不同方面一样，拥有不同视角的人们在研究同一主题时会关注不同的方面。STORM 通过考察相关维基百科文章识别出潜在的视角，然后分配这些视角给模拟的写作者。这些写作者会根据其特定视角提出问题，从而确保信息收集的广度，覆盖主题的多个方面。例如，研究奥运会开幕式，事件策划者会关注交通安排和预算，而普通人可能只关心基本信息。

6. STORM 如何评估其生成的文章和预写作阶段的质量？
STORM 使用专门策划的 FreshWiki 数据集进行评估，该数据集包含最近的高质量维基百科文章，以避免训练数据泄露。它针对文章和预写作阶段（大纲）都建立了评估标准。评估包括自动指标（如 ROUGE 分数、实体召回率）和人工评估。人工评估由经验丰富的维基百科编辑进行，他们评估文章的兴趣水平、组织结构、相关性、覆盖度和可验证性。实验结果表明，STORM 在多项自动和人工评估指标上优于基线方法。

7. Co-STORM 是什么？它与 STORM 有何不同？
Co-STORM 是 STORM 的一个增强版本，它支持人与 LLM 系统的协作知识策展。虽然 STORM 自动化了整个过程，但 Co-STORM 允许用户观察并偶尔引导多个 LLM 代理之间的讨论。用户可以“参与”到模拟对话中，从而发现他们可能不知道的“未知未知”信息。Co-STORM 还维护一个动态更新的“思维导图”，帮助用户追踪讨论并组织收集到的信息，最终生成一份全面的报告。这使得信息获取过程更符合人类学习和信息探索的方式。

8. 维基百科编辑对 STORM 的看法如何？
根据对经验丰富的维基百科编辑的人工评估，所有参与者都认为 STORM 对他们的预写作阶段很有帮助。70% 的编辑认为它对于编辑新主题的维基百科文章很有用，而 70% 的编辑也认为它对维基百科社区是一个潜在的有用的工具。这表明 STORM 的方法论和产出得到了目标用户群体的积极反馈，尤其是在协助研究和组织信息方面。

## CO-STORM

基于我对Co-STORM代码的深入分析，创建一个详细的Mermaid流程图来描述Co-STORM的工作流程。

```mermaid
graph TD
    A["开始: Co-STORM 系统"] --> B["初始化配置"]
    B --> B1["配置LM模型<br/>- 问答模型<br/>- 话语管理模型<br/>- 话语润色模型<br/>- 热启动大纲生成模型<br/>- 问题提问模型<br/>- 知识库模型"]
    B --> B2["配置检索模块<br/>- BingSearch<br/>- YouRM<br/>- VectorRM等"]
    B --> B3["设置运行参数<br/>- 主题<br/>- 检索数量<br/>- 最大对话轮数<br/>- 专家数量等"]
    
    B1 --> C["热启动阶段 (Warm Start)"]
    B2 --> C
    B3 --> C
    
    C --> C1["背景信息收集"]
    C1 --> C1a["生成背景问题"]
    C1a --> C1b["基于检索的问答<br/>收集主题背景信息"]
    C1b --> C2["专家生成模块"]
    
    C2 --> C2a["分析背景信息"]
    C2a --> C2b["生成多视角专家<br/>例: AI研究员、产业专家、伦理学家"]
    C2b --> C3["热启动多轮对话"]
    
    C3 --> C3a["为每个专家分配角色"]
    C3a --> C3b["并行专家对话<br/>每个专家2轮对话"]
    C3b --> C3c["收集专家问答内容"]
    C3c --> C4["初始化知识库"]
    
    C4 --> C4a["信息插入模块<br/>构建层次化知识树"]
    C4a --> C4b["生成初始大纲"]
    C4b --> C4c["转换为对话记录<br/>供用户快速了解"]
    C4c --> D["主对话阶段"]
    
    D --> D1["话语管理器 (Discourse Manager)"]
    D1 --> D2{"确定下一轮策略"}
    
    D2 --> |"用户输入"| E["用户话语处理"]
    D2 --> |"系统生成"| F["系统话语生成"]
    
    E --> E1["解析用户输入"]
    E1 --> E2["添加到对话历史"]
    E2 --> H["知识库更新"]
    
    F --> F1{"选择代理类型"}
    F1 --> |"专家回答"| G1["Co-STORM专家代理"]
    F1 --> |"主持人提问"| G2["主持人代理"]
    F1 --> |"模拟用户"| G3["模拟用户代理"]
    F1 --> |"纯RAG模式"| G4["纯RAG代理"]
    
    G1 --> G1a["行动规划<br/>确定回答策略"]
    G1a --> G1b["基于检索的问答<br/>收集相关信息"]
    G1b --> G1c["生成专家回答"]
    G1c --> G1d["话语润色"]
    G1d --> G1e["引用信息处理"]
    G1e --> H
    
    G2 --> G2a["分析未使用信息片段"]
    G2a --> G2b["基于相似度排序"]
    G2b --> G2c["生成基于事实的问题"]
    G2c --> H
    
    G3 --> G3a["基于意图生成<br/>模拟用户话语"]
    G3a --> H
    
    G4 --> G4a["直接RAG问答<br/>无协作对话"]
    G4a --> H
    
    H --> H1["信息插入模块"]
    H1 --> H1a["层级导航<br/>确定信息位置"]
    H1a --> H1b["树结构插入<br/>- insert: 当前节点<br/>- step: 子节点<br/>- create: 新节点"]
    H1b --> H2["知识库重组"]
    
    H2 --> H2a["节点扩展<br/>当节点信息过多时"]
    H2a --> H2b["层次化组织<br/>维护思维导图结构"]
    H2b --> I{"对话是否继续?"}
    
    I --> |"是"| J["专家列表更新"]
    J --> J1["基于新信息<br/>动态调整专家"]
    J1 --> D1
    
    I --> |"否"| K["报告生成阶段"]
    K --> K1["遍历知识库节点"]
    K1 --> K2["按层次结构组织"]
    K2 --> K3["生成带引用的报告<br/>格式: # ## ### 表示层级<br/>[1][2] 表示引用"]
    K3 --> L["输出最终报告"]
    
    subgraph "知识库管理 (Knowledge Base)"
        KB1["层次化知识节点"]
        KB2["信息片段存储"]
        KB3["引用关系管理"]
        KB4["思维导图维护"]
        KB5["动态重组机制"]
    end
    
    subgraph "多智能体协作 (Multi-Agent Collaboration)"
        MA1["专家代理<br/>Co-STORM Expert"]
        MA2["主持人<br/>Moderator"]
        MA3["话语管理器<br/>Discourse Manager"]
        MA4["模拟用户<br/>Simulated User"]
    end
    
    subgraph "检索增强 (Retrieval Augmentation)"
        RA1["查询生成"]
        RA2["信息检索"]
        RA3["结果过滤"]
        RA4["引用处理"]
    end
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style K fill:#fff3e0
    style L fill:#ffebee

```

**Co-STORM 工作流程详解**

### 1. **初始化阶段**

- **多模型配置**: Co-STORM使用多个专门的LLM模型来处理不同任务，包括问答、话语管理、话语润色等
- **检索模块设置**: 集成多种搜索引擎（Bing、You.com、向量检索等）
- **参数配置**: 设置对话轮数、专家数量、检索深度等关键参数

### 2. **热启动阶段 (Warm Start)**

- **背景研究**: 系统首先进行主题背景信息收集
- **多视角专家生成**: 基于背景信息自动生成具有不同专业视角的虚拟专家
- **并行专家对话**: 每个专家进行多轮对话，从不同角度探讨主题
- **知识库初始化**: 将收集的信息组织成层次化的思维导图结构

### 3. **主对话阶段**

- **协作式话语协议**: 实现了一套完整的轮次管理策略
- **多智能体协作**:
  - **Co-STORM专家**: 基于检索信息生成专业回答
  - **主持人**: 基于未使用信息生成启发性问题
  - **用户**: 可以观察或主动参与对话
- **动态知识管理**: 实时更新和重组知识库结构

### 4. **知识库管理**

- **层次化信息组织**: 使用树状结构组织信息
- **智能信息插入**: 通过导航算法确定新信息的最佳位置
- **动态重组**: 当信息过多时自动扩展节点结构
- **思维导图维护**: 保持信息的逻辑层次关系

### 5. **报告生成**

- **结构化输出**: 基于知识库的层次结构生成报告
- **完整引用**: 每个信息点都有对应的来源引用
- **Wiki风格**: 采用Wikipedia式的文章结构

### 核心创新点

1. **协作式对话协议**: 不同于传统的单轮问答，Co-STORM实现了多智能体的协作对话
2. **动态思维导图**: 实时构建和维护知识的层次化结构
3. **基于检索的专家系统**: 每个专家都能基于实时检索信息进行回答
4. **人机协作**: 用户可以在任何时候介入对话，引导讨论方向

这个工作流程体现了Co-STORM作为一个**协作式知识管理系统**的核心特点，它不仅能够自动收集和组织信息，还能通过多智能体协作产生更深入和全面的知识理解。

## LangGraph STORM实现分析

LangGraph里面有个基于STORM论文和LangGraph实现，我基于这个实现，创建了一个详细的STORM工作流程图。这个流程图展示了STORM（Synthesis of Topic Outline through Retrieval and Multi-perspective question asking）系统的完整工作流程，包括以下关键阶段：

```mermaid
graph TB
    Start([开始: 输入研究主题]) --> InitOutline["生成初始大纲"]
    
    %% 初始化阶段
    InitOutline --> |快速LLM生成| InitialStruct{"初始大纲结构"}
    InitialStruct --> |包含主要部分| RelatedTopics["扩展相关主题"]
    
    %% 相关主题生成
    RelatedTopics --> |Wikipedia检索| WikiSearch["搜索相关Wikipedia页面"]
    WikiSearch --> |格式化内容| WikiDocs["Wikipedia文档列表"]
    
    %% 生成多角度编辑者
    WikiDocs --> GenPerspectives["生成不同视角的编辑者"]
    GenPerspectives --> |基于相关主题| EditorList{"编辑者列表"}
    EditorList --> |N个编辑者| Editor1["编辑者1: 角色A<br/>关注点: 技术实现"]
    EditorList --> |并行生成| Editor2["编辑者2: 角色B<br/>关注点: 商业应用"]
    EditorList --> |多视角| EditorN["编辑者N: 角色N<br/>关注点: 研究前沿"]
    
    %% 专家访谈阶段
    subgraph InterviewStage ["专家访谈阶段-并行执行"]
        direction TB
        
        %% 访谈流程1
        I1Start["访谈1开始"] --> I1Question["编辑者1提问"]
        I1Question --> I1Search["专家搜索引擎查询"]
        I1Search --> |Tavily API| I1Results["获取搜索结果"]
        I1Results --> I1Answer["专家回答并引用"]
        I1Answer --> I1Continue{"对话是否继续?"}
        I1Continue --> |未达到M轮| I1Question
        I1Continue --> |达到M轮或感谢| I1End["访谈1结束"]
        
        %% 访谈流程2
        I2Start["访谈2开始"] --> I2Question["编辑者2提问"]
        I2Question --> I2Search["专家搜索引擎查询"]
        I2Search --> |Tavily API| I2Results["获取搜索结果"]
        I2Results --> I2Answer["专家回答并引用"]
        I2Answer --> I2Continue{"对话是否继续?"}
        I2Continue --> |未达到M轮| I2Question
        I2Continue --> |达到M轮或感谢| I2End["访谈2结束"]
        
        %% 访谈流程N
        INStart["访谈N开始"] --> INQuestion["编辑者N提问"]
        INQuestion --> INSearch["专家搜索引擎查询"]
        INSearch --> |Tavily API| INResults["获取搜索结果"]
        INResults --> INAnswer["专家回答并引用"]
        INAnswer --> INContinue{"对话是否继续?"}
        INContinue --> |未达到M轮| INQuestion
        INContinue --> |达到M轮或感谢| INEnd["访谈N结束"]
    end
    
    %% 连接到访谈阶段
    Editor1 --> I1Start
    Editor2 --> I2Start
    EditorN --> INStart
    
    %% 收集访谈结果
    I1End --> CollectResults["收集所有访谈结果"]
    I2End --> CollectResults
    INEnd --> CollectResults
    
    %% 大纲优化阶段
    CollectResults --> RefineOutline["优化大纲"]
    RefineOutline --> |长上下文LLM分析| UpdatedOutline{"更新后的大纲"}
    
    %% 建立参考文档索引
    UpdatedOutline --> IndexRefs["建立参考文档索引"]
    IndexRefs --> |向量嵌入| VectorStore[("向量数据库<br/>存储引用文档")]
    
    %% 分章节写作阶段
    VectorStore --> WriteSection["分章节并行写作"]
    
    subgraph WritingStage ["章节写作阶段-并行执行"]
        direction TB
        WriteSection --> Section1["章节1写作<br/>检索相关参考"]
        WriteSection --> Section2["章节2写作<br/>检索相关参考"]
        WriteSection --> SectionN["章节N写作<br/>检索相关参考"]
        
        Section1 --> |RAG检索| S1Refs["获取相关引用1"]
        Section2 --> |RAG检索| S2Refs["获取相关引用2"]
        SectionN --> |RAG检索| SNRefs["获取相关引用N"]
        
        S1Refs --> S1Complete["章节1完成"]
        S2Refs --> S2Complete["章节2完成"]
        SNRefs --> SNComplete["章节N完成"]
    end
    
    %% 最终文章生成
    S1Complete --> CombineSections["合并所有章节"]
    S2Complete --> CombineSections
    SNComplete --> CombineSections
    
    CombineSections --> FinalDraft["生成初稿"]
    FinalDraft --> |长上下文LLM优化| FinalArticle["最终Wikipedia风格文章"]
    
    %% 输出
    FinalArticle --> End([完成: 输出完整文章])
    
    %% 关键组件说明
    subgraph Components ["关键组件"]
        direction LR
        Comp1["快速LLM: GPT-4o-mini<br/>处理大部分任务"]
        Comp2["长上下文LLM: GPT-4o<br/>大纲优化和最终写作"]
        Comp3["搜索引擎: Tavily API<br/>获取外部知识"]
        Comp4["向量数据库: 存储和检索<br/>参考文档"]
    end
    
    subgraph Parameters ["超参数设置"]
        direction TB
        Param1["N: 编辑者视角数量"]
        Param2["M: 每次访谈最大轮数"]
        Param3["max_num_turns: 5"]
        Param4["top_k_results: 检索文档数"]
    end
    
    %% 样式定义
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef parallel fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef storage fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class Start,End startEnd
    class InitOutline,RelatedTopics,WikiSearch,GenPerspectives,RefineOutline,IndexRefs,WriteSection,CombineSections,FinalDraft,FinalArticle process
    class InitialStruct,EditorList,UpdatedOutline,I1Continue,I2Continue,INContinue decision
    class Editor1,Editor2,EditorN,Section1,Section2,SectionN parallel
    class VectorStore storage
```

**STORM工作流程详解**

### 1. **初始化阶段**

- 用户输入研究主题（topic，也就是我们说的研究主题，query等等）
- 使用快速LLM（GPT-4o-mini）生成初始大纲（outline）
- 从Wikipedia搜索相关主题（subjects）作为参考（perspective）

### 2. **多视角编辑者生成**

- 基于相关主题生成N个不同视角的编辑者（editor）
- 每个编辑者代表不同的专业背景和关注点（perspective）
- 例如：技术实现专家、商业应用专家、学术研究专家等（role）

### 3. **专家访谈阶段（核心创新）**

- **并行执行**：多个编辑者同时进行访谈（parallel）
- **角色扮演**：编辑者（editor）提出问题，专家（expert）通过搜索引擎查询回答（role-play）
- **引用追踪**：专家回答时保存引用来源（reference）
- **轮次限制**：每次访谈最多M轮（默认5轮）（max_num_turns）
- **自然结束**：编辑者说"感谢"时结束访谈（natural end）

### 4. **大纲优化阶段**

- 收集所有访谈结果（collect_results）
- 使用长上下文LLM（GPT-4o）分析访谈内容（analyze_results）
- 基于新获得的信息优化初始大纲（refine_outline）

### 5. **参考文档索引**

- 将所有访谈中收集的引用文档进行向量嵌入（vector_embed）
- 建立向量数据库用于后续RAG检索（vector_store）

### 6. **分章节写作**

- **并行执行**：同时写作多个章节（parallel）
- **RAG检索**：每个章节写作时检索相关参考文档（rag_retrieval）
- **引用整合**：确保内容有据可查（reference_integration）

### 7. **最终文章生成**

- 合并所有章节（combine_sections）
- 使用长上下文LLM进行最终优化（final_optimization）
- 输出Wikipedia风格的完整文章（final_article）

## 关键特性

1. **多视角研究**：通过不同角色的编辑者确保内容全面性（multi-perspective）
2. **搜索增强**：每个问答都通过实时搜索获取最新信息（search_enhancement）
3. **并行处理**：访谈和写作阶段都采用并行处理提高效率（parallel_processing）
4. **引用追踪**：全程跟踪信息来源，确保内容可信度（reference_tracking）
5. **两阶段LLM**：快速LLM处理大量任务，长上下文LLM处理复杂分析（two-stage_llm）

这个工作流程的核心创新在于通过多视角的"模拟专家访谈"来获取更全面、更深入的信息，从而生成高质量的研究文章。

## 参考

- [Storm UI](https://storm.genie.stanford.edu/)
- [Storm github](https://github.com/stanfordnlp/storm)
