# **人工智能多智能体系统：架构、交互与应用综合研究报告**

## **1\. 引言**

### **1.1 目的与范围**

多智能体系统（Multi-Agent Systems, MAS）作为人工智能（AI）和分布式系统领域的一个重要范式，近年来受到了广泛关注 1。本报告旨在基于英文学术文献和技术文档，对不同的人工智能多智能体系统进行全面的调研、分析和比较，并以中文形式呈现研究结果。报告将系统性地探讨MAS的定义、核心概念、关键组件、不同架构类型、典型框架与实例、智能体间的通信机制、协调与协商策略、学习能力（特别是多智能体强化学习）以及主要应用领域，最终进行综合比较分析。

### **1.2 MAS的重要性**

MAS之所以日益重要，在于其独特的解决复杂问题的能力。许多现实世界的问题对于单个智能体或单一的、集成的（monolithic）系统而言过于庞大或复杂，难以有效解决 1。MAS通过将问题分解，利用多个自主智能体的交互与协作，能够应对这种复杂性 3。此外，MAS天然适用于分布式环境，其架构特性使其具备良好的灵活性、可扩展性和鲁棒性，能够适应动态变化的环境 14。这些优势使得MAS在机器人、智能电网、交通管理、电子商务、社会模拟等众多领域展现出巨大的应用潜力 1。

### **1.3 报告结构**

本报告结构如下：第二部分介绍MAS的基础知识，包括定义、核心概念和关键组件；第三部分探讨MAS的不同架构分类；第四部分介绍著名的MAS框架和实例；第五部分分析智能体间的通信语言与协议；第六部分研究MAS中的协调、合作与协商策略；第七部分深入探讨MAS的学习能力，特别是MARL；第八部分识别MAS的主要应用领域；第九部分对不同MAS进行综合比较与分析；最后，第十部分总结研究发现并展望未来发展方向。

## **2\. 多智能体系统基础**

### **2.1 定义与核心概念**

**定义：** 多智能体系统（MAS）通常被定义为由多个交互的、自主的智能体组成的计算或分布式系统 1。这些智能体可以是软件程序、物理机器人、传感器、无人机，甚至是人类或人机混合团队 1。它们共同存在于一个共享的环境中，通过感知环境、进行决策并采取行动来实现各自或集体的目标 1。

**智能体：** “智能体”（Agent）是MAS的核心构成单元，它是一个能够自主行动的实体 14。智能体能够感知其所处的环境（物理或虚拟），基于感知信息和内部知识进行推理和决策，并执行动作以影响环境，旨在达成其预设的目标或任务 1。根据其能力和行为复杂性，智能体可以被分为不同类型，例如：被动智能体（无目标，如环境中的障碍物）、主动智能体（具有简单目标，如鸟群中的鸟）和认知智能体（能够进行复杂计算和推理）1。

**智能体特征：** MAS中的智能体通常具备以下关键特征：

* *自主性（Autonomy）:* 智能体至少是部分独立的，能够控制自身的内部状态和行为，无需外部直接干预 1。  
* *局部视角（Local Views）:* 通常情况下，没有一个智能体拥有完整的全局信息或系统状态视图，或者系统过于复杂以至于单个智能体无法利用全局知识 1。  
* *去中心化（Decentralization）:* 系统中通常没有指定的中心控制器（除非特殊设计，但这可能使其退化为单体系统），控制和决策权分布在各个智能体中 1。  
* *交互性（Interaction）:* 智能体之间通过通信、协调、合作或竞争等方式进行交互，以实现个体或集体目标 2。

**与其他范式的区别：** MAS与传统的软件范式（如面向对象编程）和单体AI系统有所不同。与对象（Object）主要封装状态并通过方法被动调用不同，智能体主动控制自身的行为，决定何时以及如何行动 4。与单体AI系统相比，MAS强调分布式、自主性、智能体间的交互以及可能的专业化分工 14。

**MAS作为隐喻与工具：** MAS不仅仅是一种工程范式，用于构建复杂的分布式系统，它也提供了一种强大的隐喻和工具，用于建模和理解自然界和社会系统中的复杂现象 1。例如，基于智能体的建模（Agent-Based Modeling, ABM）旨在通过模拟遵守简单规则的个体智能体（不一定需要“智能”）的行为，来探究群体行为的涌现机制，尤其是在自然系统（如鸟群、捕食者-猎物模型）或社会系统（如市场动态、流行病传播、交通流）中 1。这种双重角色——既是解决工程问题的方案，又是理解复杂现象的科学工具——深刻影响着MAS的设计理念和评估标准。用于工程应用的MAS可能更侧重于效率、鲁棒性和任务完成度，而用于科学建模的MAS则可能更注重行为的真实性、模型的解释力和对现象的洞察力 1。

### **2.2 关键组件**

一个典型的MAS由以下几个关键组件构成：

* **智能体（Agents）:** 系统的核心执行者，拥有特定的角色、能力、行为模式和知识模型 1。智能体的智能性体现在其学习、规划、推理和决策能力上 14。  
* **环境（Environment）:** 智能体所处的外部世界，可以是物理空间（如工厂、道路、电网）或模拟空间 1。智能体通过传感器感知环境状态，并通过执行器对环境施加影响 14。环境的特性，如可访问性（能否获取完整信息）、确定性（动作效果是否确定）、动态性（环境变化速度和影响因素）、离散性等，都会影响MAS的设计和行为 1。  
* **交互/通信（Interactions/Communication）:** 智能体之间进行信息交换和协调的机制。这可以通过标准化的智能体通信语言（ACL）进行显式通信 3，也可以通过环境进行间接通信，例如留下信息素（pheromone）供其他智能体感知 1。  
* **组织/结构（Organization/Structure）:** 定义了智能体之间的关系、角色和控制流程。组织结构可以是预定义的，如层级式控制 14，也可以是动态形成的，基于智能体交互和自组织规则 14。

### **2.3 主要特征与优势**

MAS展现出许多优于传统单体系统的特征和优势：

* **灵活性与适应性（Flexibility & Adaptability）:** MAS可以通过增加、移除或修改智能体来灵活适应变化的环境和需求 3。智能体可以动态调整其策略和行为 42。  
* **可扩展性（Scalability）:** 通过将复杂问题分解给多个智能体并行处理，MAS有潜力解决单个系统难以处理的大规模问题 3。  
* **鲁棒性与可靠性（Robustness & Reliability）:** 控制的去中心化提高了系统的容错能力。部分智能体或组件的失效通常不会导致整个系统崩溃 3。  
* **专业化与效率（Specialization & Efficiency）:** 每个智能体可以专注于特定的任务或领域，进行优化，从而提高特定任务的效率和性能，这比试图让一个单一模型涵盖所有能力可能更有效 14。  
* **自组织与涌现性（Self-Organization & Emergence）:** 即使单个智能体的规则很简单，通过智能体间的交互，系统整体也可能展现出复杂的、预先未明确设计的自组织行为和涌现特性（如鸟群的同步飞行）1。  
* **实时操作（Real-Time Operation）:** MAS有潜力在没有人类干预的情况下对环境变化做出即时响应，适用于需要快速反应的应用场景 14。  
* **可解释性（Interpretability）:** 相较于通常被视为“黑箱”的单一大型模型（如大型语言模型LLM），由多个专业化智能体组成的系统可能更容易理解和分析不同组件如何对整体行为做出贡献 14。

**可扩展性悖论：** 尽管可扩展性常被认为是MAS的核心优势之一 3，但在实践中实现大规模扩展却面临严峻挑战 17。随着智能体数量的增加，协调它们的行为、管理通信开销以及解决多智能体学习中的复杂性（如非平稳性、信用分配问题）变得异常困难 36。因此，MAS的*潜力*可扩展性需要通过精心的架构设计、高效的通信协议和先进的协调与学习算法才能转化为*实际*的可扩展性。这构成了一个悖论：分布式架构本身为扩展提供了基础，但维持该架构有效运行所需的动态交互和学习过程却可能成为扩展的瓶颈。

## **3\. 多智能体系统架构**

MAS的架构可以从不同维度进行分类，主要包括基于控制结构的组织方式和基于单个智能体内部推理机制的类型 3。需要注意的是，这些分类并非完全互斥，实际系统常常采用混合架构 3。

### **3.1 基于控制结构的架构**

这类架构关注智能体之间的组织关系和信息流控制方式。

* **中心化网络（Centralized Networks）:**  
  * *机制:* 存在一个中心单元（或智能体），负责维护全局知识库、连接所有智能体并监督它们的信息交换与协调 15。  
  * *优势:* 智能体间通信相对容易管理，知识可以保持一致性 15。  
  * *劣势:* 系统的可靠性完全依赖于中心单元，中心单元的故障会导致整个系统瘫痪，且可能成为性能瓶颈 15。  
* **去中心化网络（Decentralized Networks）:**  
  * *机制:* 智能体仅与其邻近的智能体进行信息共享和交互，没有全局控制中心 1。决策是自主做出或通过局部协调达成。  
  * *优势:* 鲁棒性高，容错性强，系统具有模块化特性。单个智能体的失败不会导致系统整体崩溃 3。  
  * *劣势:* 协调智能体行为以达成全局最优或使其他合作智能体受益可能非常具有挑战性 15。  
* **层级式结构（Hierarchical Structure）:**  
  * *机制:* 智能体被组织成树状结构，不同层级的智能体拥有不同的自主权和控制范围 15。下级智能体向上级汇报，上级智能体向下级分配任务或指令。决策权可以在顶层集中，也可以在各层级间分布 15。例如，垂直架构中，领导者智能体监督子任务和决策，下属智能体汇报结果 27。  
  * *优势:* 结构清晰，角色明确，对于可以清晰分解的任务可能效率较高 27。  
  * *劣势:* 结构相对刚性，可能在高层级产生瓶颈，对环境变化的适应性可能不如扁平结构。  
* **全子结构（Holonic Structure / Holarchies）:**  
  * *机制:* 智能体（称为“全子”Holon）本身可以由更小的子智能体组成，形成递归的“部分-整体”层级结构 15。一个全子对外表现为一个整体，但内部包含复杂的子结构和交互。子智能体可以同时属于多个全子。这种结构通常是自组织的，旨在通过子智能体的协作实现目标 15。  
  * *优势:* 提供了良好的模块化和抽象机制，支持自组织和复杂行为的构建。  
  * *劣势:* 设计和协调内部及全子间的交互可能非常复杂。  
* **联盟结构（Coalition Structure）:**  
  * *机制:* 当单个智能体或小组表现不佳时，智能体会临时组成联盟，以提高共同的效用或性能 15。一旦达到预期目标，联盟可能解散。  
  * *优势:* 具有灵活性，能够动态地组合力量以应对特定挑战或提升短期表现 15。  
  * *劣势:* 在动态环境中维持联盟的稳定性可能很困难，常常需要重新组合以保持性能 15。  
* **团队结构（Teams）:**  
  * *机制:* 类似于联盟，团队中的智能体也合作以提高群体表现 15。但与联盟不同的是，团队成员通常不是独立工作的，彼此之间的依赖性更强，结构也往往比联盟更具层级性或稳定性 15。  
  * *优势:* 能够实现紧密的合作和协调，适用于需要高度协同的任务 15。  
  * *劣势:* 高度相互依赖可能使团队对个别成员的失败或瓶颈更为敏感 15。

**架构选择与信任/控制假设：** 控制架构的选择（中心化、去中心化、层级化等）不仅仅是技术决策，它也隐含地反映了系统设计者对智能体可信度、全局监督必要性以及通信成本效益的假设 15。中心化系统可能意味着对中心节点的高度信任，或者认为需要严格的全局控制才能保证系统目标达成；而去中心化系统则更强调鲁棒性，假设局部交互足以应对环境变化，或者全局控制不可行、成本过高或不必要。在开放、动态的MAS中，智能体可能来自不同组织，具有异构能力和潜在的自利行为，此时信任管理变得至关重要 70，这往往促使系统向更去中心化、依赖局部交互和信任评估的架构演进。层级结构则在控制和分布之间取得某种平衡，适用于具有天然层级关系的任务。因此，架构选择体现了对效率（可能倾向中心化）和鲁棒性（可能倾向去中心化）之间的权衡，以及对系统内部信任关系的预期。

### **3.2 基于智能体推理的架构**

这类架构关注单个智能体内部如何进行感知、推理和决策。

* **反应式架构（Reactive Architecture）:**  
  * *机制:* 智能体基于当前感知到的环境刺激，通过预定义的简单规则（如条件-动作对）直接映射到行动，不进行复杂的内部状态建模、记忆或未来规划 3。其核心是快速的“感知-行动”循环 65。例如，扫地机器人碰到障碍物立即转向 65。  
  * *优势:* 响应速度快，计算开销小，设计相对简单，在已知和变化迅速的环境中表现可靠 29。  
  * *劣势:* 缺乏规划和学习能力，难以处理需要长远考虑或策略性思考的任务，对于未预见的新情况适应性差 22。  
* **审议式架构（Deliberative Architecture）:**  
  * *机制:* 智能体维护关于世界的内部模型（信念），基于这些模型进行显式的推理和规划，以选择能够达成其目标（愿望、意图）的行动序列 3。它们会评估不同行动方案的潜在后果，进行长远考虑 65。  
  * *优势:* 能够进行战略性规划，追求长期目标，做出更深思熟虑的决策，可能获得更优的长期结果 29。  
  * *劣势:* 计算成本高（维护模型、模拟未来、评估方案），响应速度较慢，需要准确的世界模型，对环境的快速、未预期变化可能反应迟钝（规划可能过时）29。  
* **信念-愿望-意图架构（Belief-Desire-Intention, BDI）:**  
  * *机制:* BDI是一种特殊的、影响广泛的审议式架构，它明确地使用人类实践推理中的心理状态隐喻来构建智能体 27。智能体维护：  
    * *信念（Beliefs）:* 关于世界（包括自身和环境）状态的信息和知识，可能是部分的或不完全准确的 27。  
    * *愿望（Desires）:* 智能体希望达成的目标状态或想要完成的任务，代表其动机 27。  
    * *意图（Intentions）:* 智能体已承诺要去实现的一部分愿望，通常与一个或多个执行计划相关联 27。意图具有持续性，指导智能体的行动，直到目标达成、变得不可能或不再相关。 智能体的推理过程包括审议（Deliberation，从愿望中选择意图）和手段-目的推理（Means-Ends Reasoning，为意图寻找合适的计划）22。事件（内部或外部）可以触发信念更新、愿望生成或计划执行 34。  
  * *优势:* 提供了对理性行为的直观且有哲学基础的模型，能够较好地平衡反应性（对事件的响应）和目标导向性（对意图的承诺和规划），适用于需要智能体在动态环境中保持目标专注同时又能适应变化的复杂任务 29。  
  * *劣势:* 如何在坚持意图（避免不必要的重审议）和重新评估意图（适应环境变化）之间取得平衡是一个关键挑战 29。BDI系统的实现可能较为复杂，且推理过程可能带来一定的计算开销 29。  
* **混合架构（Hybrid Architecture）:**  
  * *机制:* 结合了反应式和审议式（或BDI）组件的优点，通常采用分层结构 3。例如，一个底层反应式层负责处理紧急情况和快速响应，而一个上层审议式层负责长期规划和战略决策 29。层间需要交互机制，如审议层设定目标给反应层执行，或反应层检测到异常时将控制权交给审议层 29。  
  * *优势:* 试图兼具反应式架构的速度和审议式架构的深思熟虑，能更好地适应复杂、动态的现实世界任务 29。  
  * *劣势:* 设计层间交互和协调机制可能非常复杂，需要解决不同层级间可能产生的冲突 29。  
* **基于效用的架构（Utility-Based Architecture）:**  
  * *机制:* 智能体使用一个效用函数（utility function）来评估不同行动可能导致的状态或结果的“好坏”程度（期望效用）43。智能体的目标是选择能够最大化其期望效用的行动。  
  * *优势:* 提供了一个形式化的理性决策框架，能够清晰地处理复杂的权衡（trade-offs），适用于需要优化性能或资源的场景 65。  
  * *劣势:* 设计一个能够准确反映智能体偏好和目标的效用函数本身可能非常困难，且计算和比较所有可能行动的期望效用可能计算成本很高。

**推理架构与控制结构的正交性：** 值得注意的是，单个智能体的内部推理架构（反应式、审议式、BDI、混合式）与其所属MAS的整体控制结构（中心化、去中心化、层级式）在很大程度上是相互独立的（正交的）设计维度 15。例如，一个完全去中心化的系统可以由大量简单的反应式智能体组成（如模拟鸟群的Boids算法 15），也可以由高度复杂的、具备BDI推理能力的智能体组成，它们通过复杂的协商协议进行协调（如分布式任务规划系统 74）。同样，一个层级式控制系统，其不同层级的智能体可能采用不同的推理架构。这表明MAS设计者需要在两个不同层面上做出选择：一是如何构建单个智能体的“大脑”（推理机制），二是如何组织这些智能体形成一个有效的“社会”（控制结构和交互模式）。这两方面的选择都需要根据具体应用的需求和环境特性来决定。

## **4\. 著名多智能体系统框架与实例**

为了简化MAS的开发，研究人员和工程师已经开发了多种软件框架和平台。这些框架提供了用于构建、部署和管理智能体的工具和库。

### **4.1 主流框架介绍**

以下是一些在学术界和工业界具有代表性的MAS框架：

* **JADE (Java Agent Development Framework):**  
  * *描述:* JADE是一个成熟且广泛使用的、基于Java的开源框架 55。它完全遵循FIPA（Foundation for Intelligent Physical Agents）规范，旨在简化符合标准的互操作智能多智能体系统的开发 55。JADE提供了一套全面的系统服务和代理，处理消息传输、编码解析、智能体生命周期管理等通用方面 87。它支持分布式部署，智能体可以在不同主机上的容器中运行，并提供了图形用户界面（GUI）用于监控和管理平台 83。  
  * *设计哲学:* 强调标准化和互操作性，严格遵守FIPA规范，提供一个健壮的中间件平台 55。  
  * *应用场景:* 特别适用于需要FIPA兼容性的企业级应用、分布式问题求解（如资源分配）、需要标准化交互的模拟系统等 55。  
* **Jason (基于AgentSpeak):**  
  * *描述:* Jason是一个基于Java的开源平台，其核心是一个用于解释和执行扩展版AgentSpeak语言的解释器 55。AgentSpeak是一种面向BDI（信念-愿望-意图）模型的、基于逻辑编程的智能体编程语言 83。Jason旨在提供一个具有坚实理论基础（基于操作语义）的平台，用于开发具有复杂推理能力的认知智能体 83。它允许用户定制智能体的许多方面，如信念库、选择函数等，并能与Java库无缝集成 83。  
  * *设计哲学:* 专注于BDI模型的实现，为理性智能体提供一种高级、声明式的编程范式，强调理论基础和类人推理能力的表达 69。  
  * *应用场景:* 开发需要复杂BDI推理的智能体，如社会模拟、机器人控制、虚拟现实环境、以及任何需要明确表示智能体信念、目标和计划的应用 69。  
* **其他框架 (简述):**  
  * *Mesa (Python):* 一个用于基于智能体建模（ABM）和仿真的Python库，特别适合社会科学研究或供应链仿真等领域，提供了网格和网络环境的可视化工具 55。  
  * *Ray (Python):* 一个专注于分布式计算的Python框架，其Actor模型非常适合实现大规模并行运行的智能体，尤其是在分布式强化学习（MARL）场景中，如自动驾驶协调 55。  
  * *Microsoft Autogen / CrewAI:* 近年来涌现出的新框架，专注于利用大型语言模型（LLM）构建协作式智能体系统。它们通常采用主管-工人（supervisor）或网络式架构来协调LLM驱动的智能体完成复杂任务 31。CrewAI提供了一个用于构建多智能体流程的开源库 98。
  * *Jadex:* 作为JADE的扩展，Jadex在其基础上增加了对BDI推理模型的内置支持，并引入了主动组件（AC）和面向服务组件架构（SCA）的概念 84。  
  * *SPADE (Python):* 一个支持基于行为的智能体开发的Python框架，以其灵活性著称，允许开发者根据需要添加新特性 64。  
  * *NetLogo:* 一个广泛用于基于智能体建模和仿真的平台，特别擅长探索由简单个体规则产生的复杂涌现行为，如集群（flocking）模拟 24。

### **4.2 设计哲学与特点**

不同的MAS框架体现了不同的设计侧重和理念 55。JADE的核心在于提供一个符合FIPA标准的、通用的、可互操作的基础设施 55。Jason则专注于为开发者提供一种强大的、基于BDI理论的语言和工具来构建具有复杂内部推理能力的智能体 83。Mesa和NetLogo则更侧重于模拟和建模应用，特别是ABM领域 24。而Autogen和CrewAI等新兴框架则抓住了LLM发展的浪潮，探索如何有效地编排和协调这些强大的语言模型来执行协作任务 31。

选择框架时需要考虑的关键特性包括：

* **编程语言:** Java (JADE, Jason, Jadex), Python (Mesa, Ray, SPADE, Autogen, CrewAI) 55。  
* **底层智能体模型:** FIPA兼容 (JADE), BDI (Jason, Jadex), 行为基础 (SPADE), Actor模型 (Ray), LLM基础 (Autogen, CrewAI), 模拟导向 (Mesa, NetLogo) 24。  
* **通信支持:** 是否内置支持标准ACL（如FIPA-ACL），通信方式（异步/同步消息传递）55。  
* **开发工具:** 是否提供GUI管理工具、调试器、可视化界面、编辑器插件等 83。  
* **社区与生态:** 框架的成熟度、活跃度、文档、社区支持和可用库 9。

**框架选择与智能体粒度/推理需求的关联：** 框架的选择在很大程度上取决于应用所需解决的核心问题是侧重于管理大量标准化交互，还是侧重于编程单个智能体的复杂内部推理，或是编排能力强大但可能定义不那么形式化的LLM智能体 31。JADE提供了强大的交互基础设施，适用于需要标准化和互操作性的场景，智能体本身的内部实现可以多样化 55。Jason则为需要深度BDI推理的智能体提供了专门的语言和解释器 83。而Autogen、CrewAI等LLM框架则利用了LLM的通用推理能力，通过相对简单的编排结构（如主管模式）来协调它们完成任务 31。因此，开发者需要判断问题的关键复杂性在于智能体“社会”的交互规则（可能选JADE），还是在于单个智能体的“心智”模型（可能选Jason），或是利用现有强大“大脑”（LLM）并进行有效组织（可能选LLM框架）。

## **5\. 智能体间通信**

有效的通信是MAS中实现协调、合作和协商的基础。智能体需要一种共同的“语言”来交换信息、表达意图和理解彼此 14。

### **5.1 通信语言 (Communication Languages)**

智能体通信语言（Agent Communication Languages, ACLs）为软件智能体提供了结构化的消息格式和语义，使其能够进行有意义的对话，而不仅仅是简单的数据交换 45。它们通常基于言语行为理论（Speech Act Theory）22。

* **言语行为理论基础:** 该理论认为，说话不仅仅是传递信息，更是在执行一种行为（言语行为），如请求（request）、告知（inform）、承诺（promise）、命令（command）等 47。ACLs通常定义一组“施事类型”（Performatives），对应不同的言语行为，来明确消息的意图或语用功能 45。消息还可能包含关于发送者对消息内容所持心理状态的信息，称为“命题态度”（Propositional Attitudes），如相信（believe）、意图（intend）等 33。  
* **KQML (Knowledge Query and Manipulation Language):**  
  * *起源与结构:* KQML是早期由DARPA知识共享项目（Knowledge Sharing Effort）开发的影响深远的ACL 33。它采用三层结构：内容层（实际知识）、通信层（关于内容的元信息，如本体、语言）和消息层（包含发送者、接收者、施事类型等参数）46。KQML定义了多种施事类型（如ask-if, tell, achieve, broker）47。  
  * *语义:* KQML的语义通常通过描述施事类型执行的前提条件、后置条件和完成条件来定义 46。  
  * *应用:* 主要用于学术研究和实验性分布式AI系统 45。它对促进者（facilitator）服务（如智能体注册、查找）有内建支持 45。  
* **FIPA-ACL (Foundation for Intelligent Physical Agents \- ACL):**  
  * *起源与结构:* FIPA为了促进智能体技术的标准化和互操作性而开发的ACL，已成为事实上的工业标准 3。它借鉴了KQML的概念，同样使用施事类型（如request, inform, confirm, query-if）来表示消息意图 37。FIPA-ACL消息包含多个参数字段，如performative, sender, receiver, content, language, ontology, conversation-id等，其中performative是唯一必需的字段 37。  
  * *语义:* FIPA-ACL提供了更形式化的语义规范，通常使用模态逻辑来定义，基于可行性前置条件（Feasibility Preconditions）和理性效果（Rational Effects）46。它还定义了一种标准的语义语言（Semantic Language, SL）48。  
  * *应用:* 由于其标准化和明确的语义，FIPA-ACL在需要高互操作性的工业和企业级应用中得到广泛采用 37。  
* **KQML vs. FIPA-ACL 比较:**  
  * *语法:* 两者通常都采用类似LISP的括号表示法 46。  
  * *消息处理:* KQML区分内容消息和管理消息，而FIPA-ACL将所有消息统一视为具有明确语义的通信行为 46。  
  * *语义:* FIPA-ACL的语义定义更为形式化和严格 37。  
  * *促进服务:* KQML内建支持，FIPA-ACL将其视为标准请求处理 45。  
  * *标准化程度:* FIPA-ACL是经过标准化组织（后并入IEEE）认可的标准，而KQML更像是一系列相关的方言，缺乏统一规范 33。  
  * *选择考量:* FIPA-ACL通常是需要严格互操作性和标准符合性的商业或工业应用的首选，而KQML的灵活性可能使其在研究和快速原型设计中仍有价值 45。

### **5.2 内容语言与本体**

ACL消息本身只定义了通信的“信封”（元数据和意图），而实际承载的信息内容则由**内容语言**（Content Language）来表达 47。内容语言可以是任何双方都能理解的格式，例如：

* KIF (Knowledge Interchange Format): 一种基于一阶逻辑的知识表示语言 22。  
* FIPA-SL (Semantic Language): FIPA定义的形式化语义语言 48。  
* RDF (Resource Description Framework) / OWL (Web Ontology Language): 用于语义网的语言，可以表达丰富的语义关系 22。  
* XML, JSON, Prolog, SQL 等其他格式 22。

为了确保智能体能够正确理解内容语言中使用的术语和概念，需要**本体**（Ontology）22。本体明确定义了一个共享词汇表及其语义，规定了特定领域内概念、属性和它们之间关系的含义 22。本体是实现语义互操作性的关键，确保不同智能体对同一术语有相同的理解。本体可以使用专门的语言（如OWL, KIF）来构建和表示 22。

### **5.3 交互协议**

除了单条消息的语义，智能体间的交互通常遵循一定的**交互协议**（Interaction Protocols）或**对话模式**（Conversation Patterns）1。协议定义了在特定交互上下文（如协商、拍卖、任务分配）中，允许的消息类型、顺序以及参与者的角色和责任 12。

* **契约网协议（Contract Net Protocol, CNP）:**  
  * *机制:* 这是一种广泛用于任务分配和资源协商的协议 12。基本流程包括：  
    1. *任务发布（Task Announcement）:* 一个需要帮助的智能体（管理者 Manager）向其他潜在的智能体（承包者 Contractor）广播任务描述和要求 41。  
    2. *投标（Bidding）:* 有能力且愿意执行任务的承包者向管理者提交标书（bid），说明其能力、预期成本或完成时间等 41。  
    3. *合同授予（Contract Awarding）:* 管理者评估收到的标书，选择最合适的承包者，并向其发送接受（accept）消息（授予合同），同时向其他未中标者发送拒绝（reject）消息 41。  
    4. *任务执行与结果通知（Execution & Notification）:* 中标的承包者执行任务，完成后向管理者发送通知（inform），可能包含结果 106。如果无法完成，则发送取消（cancel）消息 106。 智能体的角色（管理者/承包者）是动态的，一个承包者在执行任务时，可能将任务分解并进一步外包给其他智能体，此时它就扮演了管理者的角色 41。  
  * *应用:* 分布式传感、制造控制、物流、资源分配等 12。FIPA已将CNP标准化 103。  
  * *变种与扩展:* 原始CNP存在一些局限性，后续研究提出了改进，例如：限制广播范围、处理承包者忙碌状态（如在标书中包含可用时间）、允许管理者直接向特定承包者发出定向邀约、增加反建议（counter-proposal）机制、引入信任和规范机制以提高效率和可靠性 101。  
* **拍卖协议（Auction Protocols）:**  
  * *机制:* 模仿人类拍卖过程，用于在多个竞争者之间分配资源或任务 2。存在多种拍卖形式，如英式拍卖（递增报价）、荷兰式拍卖（递减报价）、密封第一价格拍卖、密封第二价格拍卖（Vickrey拍卖）等，每种都有不同的规则和策略含义。  
  * *应用:* 电子商务、资源分配、任务分配等。  
* **基于论证的协商协议（Argumentation-Based Negotiation, ABN）:**  
  * *机制:* 智能体不仅交换提议（offer）和反提议（counter-offer），还会交换支持其提议或反驳对方提议的理由或论据（arguments）4。这些论据可能涉及智能体的信念、目标、偏好、约束或计划 40。通过论证，智能体试图说服对方接受自己的立场或做出让步 110。  
  * *应用:* 适用于需要更深入交流、解释理由、处理复杂偏好或不完全信息的协商场景。  
* **其他协议:** 还包括投票（Voting，用于群体决策）、讨价还价（Bargaining，通常指更简单的提议交换）等 4。

**协议复杂性与智能体理性的权衡：** 交互协议的选择往往需要在协议本身的复杂性与参与智能体所需的推理能力（理性程度）之间进行权衡 12。简单的协议，如基础的拍卖或契约网，可能对智能体的推理能力要求较低，但可能无法在所有情况下都达到最优或公平的结果 12。而复杂的协议，如基于论证的协商，允许更丰富、更细致的交互，能够处理不完全信息和动态偏好，但要求智能体具备更强的推理、论证生成和理解能力，同时也可能带来更高的通信开销 40。设计者需要根据应用场景、智能体的能力以及对结果质量的要求来选择合适的协议。例如，博弈论方法倾向于设计精巧的规则（协议），假设智能体是理性的，以保证特定结果（如真实报价是占优策略）102；而论证方法则可能使用相对简单的协议结构，但依赖智能体通过交换论据来动态地发现或构建更好的解决方案 40。

## **6\. 协调、合作与协商**

在MAS中，智能体需要有效地协调（Coordinate）它们的活动，进行合作（Cooperate）以达成共同目标，并通过协商（Negotiate）来解决冲突或分配资源 2。

### **6.1 核心策略与机制**

* **协调（Coordination）:** 协调的核心在于管理智能体活动之间的依赖关系，以避免冲突、减少冗余并确保集体目标的有效达成 17。它是MAS能够作为一个整体有效运作的关键 17。协调机制需要解决“与谁协调”和“如何协调”的问题 17。  
* **合作（Cooperation）:** 指多个智能体为了共同的目标或互利而一起工作 3。合作场景下，智能体的目标通常是一致的或至少是兼容的 16。合作方式包括：  
  * *任务共享（Task Sharing）:* 将大任务分解分配给不同智能体（如契约网）22。  
  * *结果共享（Result Sharing）:* 智能体分享各自处理的结果或信息 22。  
  * *联合意图（Joint Intentions）:* 智能体形成共同的承诺来执行一个计划 22。  
  * *相互建模（Mutual Modeling）:* 智能体通过对其他智能体的行为或状态进行建模来预测和协调行动 22。  
  * *规范与社会法则（Norms and Social Laws）:* 通过预定义的规则或社会规范来约束智能体行为，促进有序互动 22。  
* **协调技术概览:**  
  * *任务分配（Task Allocation）:* 如前所述，使用契约网、拍卖等机制将任务动态分配给最合适的智能体 22。  
  * *资源共享与冲突解决（Resource Sharing & Conflict Resolution）:* 管理对有限资源的访问，解决潜在的冲突 2。  
  * *同步（Synchronization）:* 确保智能体的行动在时间上得到协调 22。  
  * *信息共享（Information Sharing）:* 交换必要的知识、状态或感知信息 20。  
  * *基于规划的协调（Planning-Based Coordination）:* 智能体通过构建部分全局计划、形成联合意图或进行多智能体规划来协调行动 17。  
  * *涌现式协调（Emergent Coordination）:* 协调行为并非来自明确的全局计划，而是从智能体基于局部规则的交互中自发产生，如集群行为（flocking，基于分离、对齐、内聚规则）或基于信息素的协调 1。  
  * *基于市场的协调（Market-Based Coordination）:* 利用拍卖、定价等经济学机制来引导资源分配和任务协调 20。  
  * *基于规范的协调（Norm-Based Coordination）:* 智能体的行为受到共享的规范或社会法则的约束 22。  
* **竞争（Competition）:** 在许多场景中，智能体可能是自利的（selfish），它们的目标可能相互冲突，需要竞争有限的资源 3。  
* **混合场景（Mixed Scenarios）:** 现实世界中常见的是混合场景，智能体可能需要在团队内部进行合作，同时与其他团队或智能体进行竞争（例如团队机器人足球赛）16。

### **6.2 协商方法**

协商是MAS中解决冲突、达成协议的关键过程，尤其是在自利智能体之间 2。

* **协商定义:** 一个涉及多个（通常是自利的）智能体的交互过程，旨在就稀缺资源的分配或行动计划达成一致 12。协商的目标是找到一个各方都能接受的协议（deal）102。  
* **主要协商方法:**  
  * *讨价还价（Bargaining）:* 通过一系列提议和反提议的交换来逐步缩小分歧，直至达成协议或谈判破裂 4。  
  * *拍卖（Auctions）:* 如前所述，是一种结构化的竞价过程 2。  
  * *论证（Argumentation）:* 智能体交换论据来支持自己的立场、攻击对方的立场或说服对方，这可能导致智能体改变其信念或偏好，从而促进协议的达成 4。  
* **协商策略（Negotiation Strategies）:** 智能体在协商过程中需要采用策略来决定如何行动，例如：  
  * *让步策略（Concession Strategies）:* 决定何时以及如何降低自己的要求 110。  
  * *接受策略（Acceptance Strategies）:* 决定何时接受对方的提议 110。  
  * *提议策略（Offer Strategies）:* 如何设计自己的提议以最大化效用，同时考虑被接受的可能性 102。  
  * *约束考虑（Constraint Consideration）:* 将自身的约束（如时间限制、预算）纳入策略制定 110。  
  * *客观标准（Objective Criteria）:* 利用市场价值、先例等客观标准来支持自己的立场，增加说服力 120。  
* **信任与声誉（Trust and Reputation）:** 在重复交互的协商环境中，信任和声誉变得非常重要。智能体需要评估对手的可信度，并可能根据历史交互调整策略 38。信任模型可以帮助智能体选择合作伙伴并管理风险 70。

**协商作为信息揭示机制：** 传统的协商模型（尤其是基于博弈论的模型）常常假设智能体拥有完全的信息和固定的、已知的偏好 102。然而，在许多现实场景中，智能体是有限理性的（bounded rational），它们的信息可能不完整或不确定，偏好也可能不完全清晰或可在交互中被影响 40。在这种情况下，协商（特别是基于论证的协商）不仅仅是在预定义的协议空间中寻找一个平衡点，更是一个**信息揭示**的过程 12。通过交换论据，智能体可以揭示其背后的兴趣、信念、约束或计划 40，这有助于澄清误解、发现潜在的价值创造机会（trade-offs）、甚至改变对方的偏好或信念，从而可能达成比仅基于初始不完全信息进行简单讨价还价更好的、更明智的协议 40。

## **7\. 多智能体系统中的学习**

学习能力是智能体适应动态环境、提高性能和自主性的关键 13。

### **7.1 学习类型与挑战**

* **概述:** 学习使智能体能够通过经验改进其行为策略 32。在MAS中，学习变得更加复杂，因为智能体不仅要适应环境，还要适应其他可能同时在学习和改变策略的智能体 32。  
* **个体学习 vs. 多智能体学习:** 需要区分单个智能体独立学习（可能将其他智能体视为环境的一部分）和多个智能体共同学习（明确考虑交互和相互影响）32。多智能体学习（Multi-Agent Learning, MAL）旨在让智能体学会有效地协调、合作或竞争 32。  
* **MAL/MARL的核心挑战:**  
  * *非平稳性（Non-stationarity）:* 这是MARL中最核心的挑战之一 58。从单个智能体的角度看，环境是动态变化的，因为其他智能体的策略在不断学习和调整。这使得传统的单智能体强化学习算法（通常假设环境是马尔可夫的、平稳的）难以直接应用或保证收敛 53。智能体学习到的最优策略可能很快就会因为其他智能体的策略改变而变得次优 58。  
  * *可扩展性（Scalability）:* 随着智能体数量的增加，联合状态空间和联合动作空间呈指数级增长，导致学习过程的计算复杂度和样本复杂度急剧上升 53。  
  * *部分可观测性（Partial Observability）:* 在许多实际应用中，智能体只能观测到环境的局部信息，无法获取完整的全局状态或其他智能体的内部状态（如意图、策略），这使得决策和协调更加困难 36。  
  * *多智能体信用分配（Multi-agent Credit Assignment）:* 当多个智能体协作完成任务并获得一个共同的奖励信号时，很难判断每个智能体的具体行动对最终结果的贡献有多大。这使得奖励分配和策略更新变得困难 38。  
  * *协调（Coordination）:* 如何让智能体学会采取相互协调的行动以实现集体目标是一个难题，尤其是在缺乏明确通信或全局规划的情况下 32。  
  * *探索与利用（Exploration vs. Exploitation）:* 在多智能体环境中，探索（尝试新行为）和利用（执行已知最优行为）的平衡问题更加复杂，因为一个智能体的探索行为会影响其他智能体的学习环境 60。  
  * *目标设定（Goal Specification）:* 如何设计奖励函数以平衡个体利益和集体利益，引导智能体朝向期望的协作或竞争行为 32。

### **7.2 多智能体强化学习 (Multi-Agent Reinforcement Learning \- MARL)**

MARL是应用强化学习（RL）技术来解决多智能体问题的研究领域，旨在让多个智能体通过与环境和其他智能体的交互来自主学习最优行为策略 1。

* **理论框架:** MARL问题通常被建模为随机博弈（Stochastic Games, SG）或马尔可夫博弈（Markov Games, MG），这是马尔可夫决策过程（MDP）在多智能体环境下的自然扩展 32。部分可观测的场景则使用部分可观测随机博弈（Partially Observable Stochastic Game, POSG）或Dec-POMDP（Decentralized POMDP）模型 127。  
* **中心化训练与去中心化执行（Centralized Training with Decentralized Execution, CTDE）:** 这是MARL中一种非常流行的范式 123。在训练阶段，算法可以利用一个中心化的模块（如中心化评论家 Critic）访问全局信息（如所有智能体的观测、动作甚至状态），以帮助智能体更有效地学习策略或值函数，从而缓解非平稳性和部分可观测性问题。但在执行阶段，每个智能体仅根据自己的局部观测独立做出决策，这使得训练好的策略可以在实际的分布式环境中使用 123。  
* **核心算法类别:**  
  * *独立学习者（Independent Learners, IL）:* 最简单的方法，每个智能体独立运行一个单智能体RL算法（如Independent Q-Learning, IQL），将其他智能体视为环境的一部分 58。优点是简单、易于实现，但由于忽略了其他智能体的学习动态，严重受到非平稳性问题的影响，通常难以收敛到最优策略 58。  
  * *值分解方法（Value Decomposition Methods）:* 主要用于协作式MARL，核心思想是将团队的全局Q值函数（衡量联合动作的好坏）分解为每个智能体的个体效用函数（或Q值）的总和或某种组合 123。这有助于解决信用分配问题。  
    * *VDN (Value Decomposition Networks):* 假设全局Q值是所有个体Q值的简单加和：Qtot​(s,a)=∑i​Qi​(oi​,ai​)。这个加性假设较强，但易于实现 123。  
    * *QMIX:* 放宽了VDN的加性假设，使用一个混合网络（Mixing Network）以非线性方式结合个体Q值来估计全局Q值：Qtot​(s,a)=fmix​({Qi​(oi​,ai​)}i​,s)。混合网络通常被约束为单调的，即个体Q值的增加不会导致全局Q值的减少，以保证个体最优选择能够导致全局最优选择（IGM原则）123。QMIX比VDN更具表达能力，能处理更复杂的协作任务。  
  * *策略梯度方法（Policy Gradient Methods）:* 直接学习每个智能体的策略（将观测映射到动作或动作概率），通常也采用CTDE范式 123。  
    * *MADDPG (Multi-Agent Deep Deterministic Policy Gradient):* 将DDPG算法扩展到多智能体领域。每个智能体学习一个确定性策略，同时训练一个中心化的评论家（Critic），该评论家接收所有智能体的观测和动作作为输入，为每个智能体的策略提供梯度指导 123。中心化评论家有助于在非平稳环境中稳定学习。  
    * *MAPPO (Multi-Agent Proximal Policy Optimization):* 将PPO算法扩展到多智能体领域。每个智能体学习一个随机策略，同样通常使用一个中心化的评论家来评估状态值或动作优势 123。PPO使用信任域优化方法来限制策略更新幅度，提高学习稳定性。  
  * *其他方法:* 还包括基于通信的MARL（Comm-MADRL），智能体学习何时、与谁以及如何通信以改善协调 122；进化算法方法 16；博弈论方法，关注均衡解（如纳什均衡）的学习 16；模仿学习和逆强化学习等 112。  
* **关键挑战分析:**  
  * *非平稳性:* CTDE通过中心化评论家获取其他智能体信息来缓解 123。值分解方法通过学习稳定的个体效用函数间接处理。  
  * *可扩展性:* IL天然可扩展但性能差。值分解和策略梯度方法通过参数共享、分解或利用局部信息等方式尝试提高可扩展性，但中心化组件仍可能成为瓶颈 123。  
  * *部分可观测性:* CTDE中的中心化评论家可以访问全局信息，缓解训练中的部分可观测性问题 123。一些算法也显式地处理POMDP设置，如使用循环神经网络（RNN）来维护内部状态。  
  * *信用分配:* 值分解方法直接针对协作环境下的信用分配问题设计 123。策略梯度方法中的中心化评论家也能提供更准确的个体贡献评估。  
  * *协调:* 通过共享奖励（协作设置）、中心化评论家评估联合动作、值分解确保个体优化导向全局优化，或显式学习通信策略等方式来促进协调 112。

**MARL中的中心化-去中心化谱系：** MARL算法在训练和执行阶段的中心化程度上存在一个谱系 58。完全去中心化的学习（如IL）简单但通常效果不佳 58。完全中心化的学习（将所有智能体视为一个整体，学习一个巨大的联合策略或值函数）理论上最优但因状态-动作空间爆炸而不可扩展 58。CTDE范式提供了一种实用的折中方案，利用中心化信息进行有效训练，同时保持执行的去中心化 123。然而，如何设计有效的中心化训练组件（评论家、混合网络等）以及如何确保从中心化训练到去中心化执行的有效转换（例如，保证IGM原则）仍然是MARL研究的核心问题和挑战所在。

## **8\. 应用领域**

MAS由于其分布式、协作和自主的特性，在众多领域都有广泛的应用前景。

### **8.1 典型应用场景**

* **机器人学（Robotics）:**  
  * *多机器人协调:* 编队控制、任务分配、路径规划（如Multi-Agent Path Finding, MAPF）106。  
  * *群体机器人（Swarm Robotics）:* 模拟生物集群行为（如蚂蚁、鸟群），用于探索、搜救、环境监测等任务 1。  
  * *自动化制造:* 智能控制机器、库存、物流和装配线，提高生产效率 1。  
  * *仓库自动化:* 大量机器人在仓库中协作完成货物的拣选、搬运和存储 17。  
* **仿真与建模（Simulation and Modeling）:**  
  * *社会模拟:* 建模和分析社会动态、经济行为、流行病传播、冲突管理、舆情演化等 1。  
  * *交通流模拟:* 预测交通拥堵，评估交通规则或基础设施变化的影响 1。  
  * *游戏AI:* 创建更真实、更具挑战性的非玩家角色（NPC）行为 1。  
  * *军事与防御模拟:* 战场环境仿真，战术测试，训练系统 15。  
* **资源管理（Resource Management）:**  
  * *智能电网（Smart Grids）:* 协调发电机、储能、电网和消费者，优化电力分配，整合可再生能源，实现需求响应 1。  
  * *供应链管理（Supply Chain Management）:* 优化生产、库存、运输和物流，提高效率和响应速度 14。  
  * *网络资源管理:* 动态负载均衡，带宽分配 1。  
* **电子商务与金融（E-commerce and Finance）:**  
  * *自动化交易（Automated Trading）:* 算法交易，高频交易 1。  
  * *推荐系统:* 个性化推荐。  
  * *协商平台:* 自动化合同谈判，服务等级协议（SLA）协商 12。  
  * *欺诈检测:* 协作检测异常交易模式 44。  
  * *风险评估与投资组合管理:* 多个专业智能体监控不同市场和风险因素 20。  
* **交通系统（Transportation Systems）:**  
  * *智能交通信号控制:* 实时优化信号灯配时，减少拥堵 14。  
  * *自动驾驶汽车协调:* 车联网（V2X）通信，协作驾驶，避免碰撞，优化交通流 1。  
  * *共享出行服务:* 优化车辆调度和乘客匹配 14。  
  * *航空交通管理:* 飞机排序，空域管理 74。  
  * *铁路与船舶管理:* 优化调度，减少延误 15。  
* **医疗健康（Healthcare）:**  
  * *病人监护:* 实时监测生命体征，异常检测与警报 14。  
  * *医疗资源优化:* 协调病床、医护人员、设备分配 14。  
  * *流行病模拟与预测:* 模拟疾病传播，评估干预措施效果 1。  
  * *药物发现与研究协调:* 协调不同研究阶段或专业领域的智能体 15。  
  * *个性化医疗与护理协调:* 协调不同专科医生、设备和病人数据 14。  
* **其他应用:**  
  * *分布式传感网络:* 协作感知和信息融合 22。  
  * *信息检索与管理:* 分布式信息收集、过滤和摘要 22。  
  * *工作流与业务流程管理:* 自动化和优化业务流程 15。  
  * *防御系统与网络安全:* 协作监控，威胁检测与响应，攻击模拟 1。  
  * *环境监测与管理:* 监测空气/水质，追踪野生动物，灾害预测与响应 20。

### **8.2 架构与应用的匹配**

不同的MAS架构适用于不同的应用需求：

* **反应式MAS:** 适用于需要快速响应、环境相对简单或可预测、或者个体智能体功能要求不高的场景。例如，基本的机器人避障 65、简单的游戏NPC 19、实时监控系统中的简单触发器 72。群体行为模拟（如flocking）通常也基于反应式规则 15。  
* **审议式/BDI MAS:** 适用于需要复杂规划、战略决策、目标管理和推理能力的场景。例如，需要进行长期任务规划的机器人 64、航空交通管制 74、需要进行复杂协商的电子商务智能体 74、具有复杂行为模式的高级游戏AI 69。  
* **混合式MAS:** 适用于那些既需要快速反应能力以应对突发事件，又需要深思熟虑的规划以实现长期目标的复杂动态环境。例如，自动驾驶汽车（需要立即刹车避险，也需要规划最优路径）65、高级机器人系统（如搜救机器人）20、动态资源分配系统 54。  
* **去中心化控制结构:** 常用于需要高鲁棒性、可扩展性且允许或鼓励自组织行为的系统。例如，大规模群体机器人系统 23、P2P网络、智能电网的分布式控制 3、某些类型的社会或生物模拟 1。  
* **层级式控制结构:** 适用于具有明确指挥链、任务可以清晰分解并自上而下分配的系统。例如，制造执行系统（MES）14、模拟具有层级结构的组织 25、某些军事指挥控制系统。  
* **基于MARL的系统:** 适用于那些环境复杂、动态变化、最优策略难以预先设计、需要智能体通过与环境和彼此的交互来自适应学习协调策略的场景。应用范围非常广泛，涵盖了机器人、游戏、交通控制、资源优化等多个领域 16。

**应用驱动架构选择：** 最终，不存在一个普遍最优的MAS架构。架构的选择（包括智能体推理机制和系统控制结构）必须由具体的应用需求驱动 4。设计者需要权衡各种因素：任务是对速度要求高还是对最优性要求高？环境是静态的还是动态的？系统规模有多大？通信是否受限？是否需要智能体具备学习和适应能力？系统是否需要高容错性？是否需要行为的可解释性？对这些问题的回答将指导架构的选择。例如，需要极快反应的应用可能选择反应式架构 65，而需要复杂战略规划的应用则需要审议式或BDI架构 65。对鲁棒性要求高的分布式系统可能采用去中心化结构 15，而需要严格流程控制的系统可能采用层级结构 14。需要从经验中学习复杂协调策略的问题则适合采用MARL方法 56。

## **9\. 多智能体系统比较与综合分析**

本节旨在整合前述章节的讨论，对不同的MAS方法进行比较，并分析其整体的优势、局限性和适用性。

### **9.1 综合比较表**

为了提供一个清晰的概览，下表总结了本报告中讨论的主要MAS类型/架构的关键特征：

| 类别/架构 (Category/Architecture) | 关键特征 (Key Characteristics) | 通信需求 (Communication Needs) | 协调复杂度 (Coordination Complexity) | 学习方法 (Learning Approach) | 典型应用 (Typical Applications) | 优势 (Strengths) | 局限性 (Limitations) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **反应式MAS (Reactive MAS)** | 基于规则的刺激-响应；无内部状态/规划 27 | 通常较低或基于局部感知 65 | 较低（通常涌现式或预定义）15 | 通常不学习或简单适应 27 | 简单机器人避障、游戏NPC、实时监控 19 | 快速响应、计算高效、简单鲁棒 29 | 缺乏远见、适应性差、难处理复杂任务 27 |
| **审议式/BDI MAS (Deliberative/BDI MAS)** | 基于模型、规划和推理；BDI使用信念-愿望-意图 27 | 可能较高，用于信息共享、协调、协商 22 | 较高（显式规划或协商）17 | 可以集成学习，但核心是推理 34 | 复杂机器人任务、空管、协商代理 65 | 目标导向、战略规划、处理复杂性 29 | 计算昂贵、响应较慢、依赖模型准确性 29 |
| **混合式MAS (Hybrid MAS)** | 结合反应式和审议式层 27 | 中到高，取决于层间交互和任务需求 | 较高（需要协调不同层级）29 | 可在不同层级集成学习 | 自动驾驶、高级机器人、动态资源分配 20 | 平衡速度与规划、适应性强 29 | 设计复杂、层间协调困难 29 |
| **去中心化控制 (Decentralized Control)** | 无中心控制节点；基于局部交互 1 | 依赖局部通信或间接交互（环境）1 | 可能很高（自组织协调难度大）或较低（简单规则）15 | 可应用各种学习方法（IL, MARL） | 群体机器人、P2P系统、智能电网 3 | 鲁棒性、容错性、可扩展性潜力 3 | 全局最优性难保证、协调困难 15 |
| **层级式控制 (Hierarchical Control)** | 树状结构，不同控制层级 15 | 通常是上下级之间的通信 | 中到高（依赖层级设计） | 可在各层级应用学习 | 制造控制、组织模拟 14 | 结构清晰、任务分解明确 27 | 刚性、可能存在瓶颈、适应性受限 |
| **基于MARL的系统 (MARL-based Systems)** | 通过强化学习学习协作/竞争策略 16 | 可能需要通信以协调或传递信息（如CTDE）122 | 极高（学习协调本身是核心挑战）38 | 核心是MARL算法（值分解、策略梯度等）123 | 游戏AI、机器人协作、交通优化 16 | 自适应性强、能发现复杂策略 | 训练复杂、样本效率低、非平稳性、扩展性挑战 53 |

此表提供了一个高层次的比较框架，有助于理解不同MAS方法之间的权衡。

### **9.2 优势、局限性与适用性分析**

综合来看，MAS作为一种重要的AI范式，其核心优势在于能够利用分布式、自主协作的智能体来解决单个系统难以应对的复杂问题，并带来**灵活性、潜在的可扩展性、鲁棒性**和**专业化分工**的好处 3。然而，这些优势的实现并非没有代价。

主要的**局限性**和**挑战**贯穿于MAS的设计和应用中：

* **协调与通信开销:** 让众多自主智能体有效协调是一项核心挑战 17。设计高效的协调机制和通信协议至关重要，但通信本身也可能成为瓶颈 36。  
* **学习的复杂性 (尤其MARL):** 在多智能体环境中学习面临非平稳性、信用分配、可扩展性等固有难题 53。虽然MARL取得了显著进展，但开发稳定、高效且可扩展的算法仍是活跃的研究领域。  
* **系统设计与理论:** 缺乏全面的分布式智能控制理论来定量分析和预测MAS的行为，尤其是涌现行为 36。设计和验证复杂的MAS仍然具有挑战性 36。  
* **信任、安全与伦理:** 在开放系统中，智能体的可信度是一个问题 70。确保系统安全、防止恶意行为、处理伦理问题（如偏见、责任归属）也日益重要 3。

**适用性**取决于具体问题和环境特性：

* 对于需要快速反应且环境相对简单的任务，**反应式MAS**可能是有效且高效的选择。  
* 对于需要深层推理、规划和目标管理，且允许一定响应延迟的任务，**审议式或BDI MAS**更为合适。  
* 对于需要在速度和规划之间取得平衡的复杂动态环境，**混合式MAS**通常是首选。  
* 对于强调鲁棒性和容错性的系统，或者天然分布式的应用（如电网、P2P），**去中心化控制**结构具有优势。  
* 对于具有明确指挥结构或任务可清晰分解的系统，**层级式控制**可能更易于管理。  
* 对于需要智能体通过经验学习复杂协作或竞争策略，且最优行为难以预先设计的场景，**MARL**提供了强大的工具。

最终，MAS的设计是一个涉及多方面权衡的过程，需要在智能体个体能力、交互机制、组织结构和学习方法之间找到适合特定应用的最佳组合。理解这些权衡是成功应用MAS技术的关键。

## **10\. 结论与未来展望**

### **10.1 总结**

本报告基于英文学术与技术文献，对人工智能多智能体系统（MAS）进行了全面的调研和分析。MAS是由多个自主智能体组成的系统，它们在共享环境中交互以实现个体或集体目标。报告探讨了MAS的核心概念（自主性、局部视角、去中心化、交互）、关键组件（智能体、环境、交互、组织），并区分了其作为工程范式和科学建模工具的双重角色。

报告详细分类和比较了不同的MAS架构，包括基于控制结构（中心化、去中心化、层级式、全子式、联盟、团队）和基于智能体推理机制（反应式、审议式、BDI、混合式、基于效用）的架构，并分析了它们之间的正交性。报告还介绍了JADE、Jason等著名MAS框架及其设计哲学。

智能体间的通信是MAS运作的基础，报告分析了主要的通信语言（KQML、FIPA-ACL）、内容语言、本体以及交互协议（如契约网、拍卖、论证）。协调、合作与协商是管理智能体交互的关键，报告探讨了相关的策略、机制和挑战，并特别指出了协商作为信息揭示过程的意义。

学习能力，特别是多智能体强化学习（MARL），对于MAS的适应性和性能至关重要。报告深入讨论了MARL的核心概念、算法类别（如值分解、策略梯度）以及面临的主要挑战（非平稳性、可扩展性、信用分配等），并分析了CTDE范式和中心化-去中心化谱系。

最后，报告梳理了MAS在机器人、仿真、资源管理、电子商务、交通、医疗等众多领域的广泛应用，并强调了应用需求对架构选择的驱动作用。通过综合比较，报告总结了各类MAS方法的优势、局限性和适用场景。

### **10.2 当前进展与挑战**

MAS领域的研究已取得显著进展，尤其是在标准化（如FIPA规范 48）、基础框架开发（如JADE, Jason 55）以及特定协调协议（如契约网 103）方面已相对成熟。然而，该领域仍面临诸多挑战，阻碍着其在更复杂现实问题中的广泛应用 3。

关键挑战包括：

* **可扩展性与复杂性管理:** 如何设计和管理包含大量异构智能体的系统，并保证其高效、稳定运行 3。  
* **MARL的理论与实践鸿沟:** 尽管MARL算法发展迅速，但在样本效率、稳定性、泛化能力以及对非平稳性和部分可观测性的处理上仍有很大提升空间 16。建立更完善的理论基础来理解和保证MARL算法的性能仍然困难 36。  
* **信任、安全与可解释性:** 在开放和关键应用中，确保智能体的可信行为、系统的安全性以及决策过程的可解释性至关重要，但目前仍是难题 14。  
* **人机协作:** 如何设计能够与人类用户或其他人类团队无缝协作、有效沟通的MAS是一个重要的研究方向 1。

### **10.3 未来研究方向**

基于当前的进展和挑战，未来MAS领域的研究可能集中在以下几个方向：

* **可扩展与鲁棒的MARL:** 开发更具样本效率、能够处理大规模智能体、在非平稳和部分可观测环境下表现更稳定的MARL算法 3。  
* **理论基础深化:** 发展更完善的分布式智能控制理论，以更好地理解、预测和保证MAS的行为，特别是涌现行为和学习动态 36。  
* **信任、安全与可解释AI:** 研究信任建模、安全协议、隐私保护机制，以及能够解释其决策过程和集体行为的MAS方法 14。  
* **人机混合智能:** 设计更自然、更高效的人-智能体交互接口和协作框架，实现人机优势互补 1。  
* **LLM驱动的MAS:** 深入探索利用大型语言模型作为构建块来创建具有高级推理、沟通和协作能力的MAS，并解决相关的协调、一致性和效率问题 1。  
* **混合智能架构:** 结合符号推理（如BDI模型）和子符号学习（如深度强化学习）的优势，构建更强大、更灵活的混合智能体架构 36。  
* **伦理与社会影响:** 持续关注和研究MAS在社会中应用可能带来的伦理挑战，如偏见、责任、公平性等，并制定相应的规范和治理框架 3。

### **10.4 结语**

多智能体系统代表了人工智能和分布式计算领域一个充满活力和潜力的研究方向。通过模拟和实现智能体间的复杂交互，MAS为解决从工程控制到社会建模等一系列广泛而具有挑战性的问题提供了强大的范式。尽管在理论、算法和应用方面仍面临诸多挑战，但随着相关技术的不断进步，MAS有望在未来科技发展和社会进步中扮演越来越重要的角色。持续的研究和创新将是释放MAS全部潜力的关键。

#### **引用的著作**

1. Multi-agent system \- Wikipedia, 访问时间为 四月 18, 2025， [https://en.wikipedia.org/wiki/Multi-agent\_system](https://en.wikipedia.org/wiki/Multi-agent_system)  
2. Multiagent Systems Course, 访问时间为 四月 18, 2025， [https://staff.science.uva.nl/\~ulle/teaching/mas/](https://staff.science.uva.nl/~ulle/teaching/mas/)  
3. (PDF) Multi-Agent Systems \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/389350729\_Multi-Agent\_Systems](https://www.researchgate.net/publication/389350729_Multi-Agent_Systems)  
4. An Introduction To Multiagent Systems \- 2nd Edition By Michael Wooldridge (paperback), 访问时间为 四月 18, 2025， [https://www.target.com/p/an-introduction-to-multiagent-systems-2nd-edition-by-michael-j-wooldridge-paperback/-/A-94292281](https://www.target.com/p/an-introduction-to-multiagent-systems-2nd-edition-by-michael-j-wooldridge-paperback/-/A-94292281)  
5. An Introduction to MultiAgent Systems: Wooldridge, Michael \- Amazon.com, 访问时间为 四月 18, 2025， [https://www.amazon.com/Introduction-MultiAgent-Systems-Michael-Wooldridge/dp/0470519460](https://www.amazon.com/Introduction-MultiAgent-Systems-Michael-Wooldridge/dp/0470519460)  
6. An Introduction to MultiAgent Systems, 2nd Edition \- Wiley, 访问时间为 四月 18, 2025， [https://www.wiley.com/en-us/An+Introduction+to+MultiAgent+Systems%2C+2nd+Edition-p-9780470519462](https://www.wiley.com/en-us/An+Introduction+to+MultiAgent+Systems%2C+2nd+Edition-p-9780470519462)  
7. An Introduction to MultiAgent Systems \- Michael Wooldridge \- Google Books, 访问时间为 四月 18, 2025， [https://books.google.com/books/about/An\_Introduction\_to\_MultiAgent\_Systems.html?id=X3ZQ7yeDn2IC](https://books.google.com/books/about/An_Introduction_to_MultiAgent_Systems.html?id=X3ZQ7yeDn2IC)  
8. Multi-Agent Systems Tutorial: A Comprehensive Guide \- BytePlus, 访问时间为 四月 18, 2025， [https://www.byteplus.com/en/topic/400859](https://www.byteplus.com/en/topic/400859)  
9. A Survey of Agent Platforms \- JASSS, 访问时间为 四月 18, 2025， [https://jasss.soc.surrey.ac.uk/18/1/11.html](https://jasss.soc.surrey.ac.uk/18/1/11.html)  
10. A Survey of Agent Platforms \- Journal of Artificial Societies and Social Simulation, 访问时间为 四月 18, 2025， [https://www.jasss.org/18/1/11.html](https://www.jasss.org/18/1/11.html)  
11. A Review of Platforms for the Development of Agent Systems \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/pdf/2007.08961](https://arxiv.org/pdf/2007.08961)  
12. (PDF) Negotiation in Multi-Agent Systems \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/2805325\_Negotiation\_in\_Multi-Agent\_Systems](https://www.researchgate.net/publication/2805325_Negotiation_in_Multi-Agent_Systems)  
13. Multiagent Systems: A Survey from a Machine Learning Perspective \- CMU School of Computer Science, 访问时间为 四月 18, 2025， [https://www.cs.cmu.edu/\~mmv/papers/MASsurvey.pdf](https://www.cs.cmu.edu/~mmv/papers/MASsurvey.pdf)  
14. What is a Multi Agent System \- Relevance AI, 访问时间为 四月 18, 2025， [https://relevanceai.com/learn/what-is-a-multi-agent-system](https://relevanceai.com/learn/what-is-a-multi-agent-system)  
15. What is a Multiagent System? \- IBM, 访问时间为 四月 18, 2025， [https://www.ibm.com/think/topics/multiagent-system](https://www.ibm.com/think/topics/multiagent-system)  
16. A Comprehensive Survey on Multi-Agent Cooperative Decision-Making: Scenarios, Approaches, Challenges and Perspectives \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/html/2503.13415v1](https://arxiv.org/html/2503.13415v1)  
17. Multi-Agent Coordination across Diverse Applications: A Survey \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/html/2502.14743v1](https://arxiv.org/html/2502.14743v1)  
18. Multi-Agent Systems for Resource Allocation and Scheduling in a Smart Grid \- PMC, 访问时间为 四月 18, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC9656614/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9656614/)  
19. What is Multi-Agent Systems? Types & Applications \- Kanerika, 访问时间为 四月 18, 2025， [https://kanerika.com/blogs/multi-agent-systems/](https://kanerika.com/blogs/multi-agent-systems/)  
20. Multi-Agent Systems: When Teams of AI Work Together \- Arion Research LLC, 访问时间为 四月 18, 2025， [https://www.arionresearch.com/blog/xptz2i7i9morzkzolthnrn2khu30au](https://www.arionresearch.com/blog/xptz2i7i9morzkzolthnrn2khu30au)  
21. Multi-agent Reinforcement Learning: A Comprehensive Survey \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/pdf/2312.10256](https://arxiv.org/pdf/2312.10256)  
22. An Introduction to MultiAgent Systems / Edition 2 by Michael Wooldridge | 9780470519462, 访问时间为 四月 18, 2025， [https://www.barnesandnoble.com/w/an-introduction-to-multiagent-systems-michael-wooldridge/1101203226](https://www.barnesandnoble.com/w/an-introduction-to-multiagent-systems-michael-wooldridge/1101203226)  
23. Hands-On Multi-Agent Systems Tutorials: Building Your First Distributed AI System, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-tutorials/](https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-tutorials/)  
24. Multi-Agent Systems \- microsoft/AI-For-Beginners \- GitHub, 访问时间为 四月 18, 2025， [https://github.com/microsoft/AI-For-Beginners/blob/main/lessons/6-Other/23-MultiagentSystems/README.md](https://github.com/microsoft/AI-For-Beginners/blob/main/lessons/6-Other/23-MultiagentSystems/README.md)  
25. A Survey of Multi-Agent Systems for Smartgrids \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/1996-1073/17/15/3620](https://www.mdpi.com/1996-1073/17/15/3620)  
26. Question what is a multi agent system? : r/ArtificialInteligence \- Reddit, 访问时间为 四月 18, 2025， [https://www.reddit.com/r/ArtificialInteligence/comments/edbv98/question\_what\_is\_a\_multi\_agent\_system/](https://www.reddit.com/r/ArtificialInteligence/comments/edbv98/question_what_is_a_multi_agent_system/)  
27. What Is Agentic Architecture? | IBM, 访问时间为 四月 18, 2025， [https://www.ibm.com/think/topics/agentic-architecture](https://www.ibm.com/think/topics/agentic-architecture)  
28. Multi Agent Systems Agents Architectures Outline Agent external definition (1) Agent external definition (2), 访问时间为 四月 18, 2025， [https://www.emse.fr/\~boissier/enseignement/sma01/pdf/agent.pdf](https://www.emse.fr/~boissier/enseignement/sma01/pdf/agent.pdf)  
29. tost.unise.org, 访问时间为 四月 18, 2025， [https://tost.unise.org/pdfs/vol1n1/1118\_35.pdf](https://tost.unise.org/pdfs/vol1n1/1118_35.pdf)  
30. Multi-Agent Systems \- University of Oxford Department of Computer Science, 访问时间为 四月 18, 2025， [http://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/kr-handbook.pdf](http://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/kr-handbook.pdf)  
31. Building Your First Multi-Agent System: A Beginner's Guide \- MachineLearningMastery.com, 访问时间为 四月 18, 2025， [https://machinelearningmastery.com/building-first-multi-agent-system-beginner-guide/](https://machinelearningmastery.com/building-first-multi-agent-system-beginner-guide/)  
32. Multiagent Learning \- Foundations and Recent Trends \- Texas Computer Science, 访问时间为 四月 18, 2025， [https://www.cs.utexas.edu/\~larg/ijcai17\_tutorial/multiagent\_learning.pdf](https://www.cs.utexas.edu/~larg/ijcai17_tutorial/multiagent_learning.pdf)  
33. AGENT- COMMUNICATION LANGUAGES: \- ARTIFICIAL INTELLIGENCE RESEARCH INSTITUTE, 访问时间为 四月 18, 2025， [https://www.iiia.csic.es/\~puyol/SEIAD2001/publicacions/ACL-FIPA.doc.pdf](https://www.iiia.csic.es/~puyol/SEIAD2001/publicacions/ACL-FIPA.doc.pdf)  
34. Belief–desire–intention software model \- Wikipedia, 访问时间为 四月 18, 2025， [https://en.wikipedia.org/wiki/Belief%E2%80%93desire%E2%80%93intention\_software\_model](https://en.wikipedia.org/wiki/Belief%E2%80%93desire%E2%80%93intention_software_model)  
35. Negotiation and Argumentation in Multi-Agent Systems: Fundamentals, Theories, Systems and Applications \- Bentham Books, 访问时间为 四月 18, 2025， [https://benthambooks.com/book/9781608058242/preface/](https://benthambooks.com/book/9781608058242/preface/)  
36. (PDF) Autonomous agents and multiagent systems: perspectives on 20 years of AAMAS, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/358253673\_Autonomous\_agents\_and\_multiagent\_systems\_perspectives\_on\_20\_years\_of\_AAMAS](https://www.researchgate.net/publication/358253673_Autonomous_agents_and_multiagent_systems_perspectives_on_20_years_of_AAMAS)  
37. A FIPA-ACL Ontology in Enhancing Interoperability Multi-agent Communication, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/323362944\_A\_FIPA-ACL\_Ontology\_in\_Enhancing\_Interoperability\_Multi-agent\_Communication](https://www.researchgate.net/publication/323362944_A_FIPA-ACL_Ontology_in_Enhancing_Interoperability_Multi-agent_Communication)  
38. A review of cooperation in multi-agent learning \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/html/2312.05162](https://arxiv.org/html/2312.05162)  
39. Multi Agent Systems: Studying Coordination and Cooperation Mechanisms in Multi-Agent Systems to Achieve Collective Goals Efficiently | Journal of Artificial Intelligence Research, 访问时间为 四月 18, 2025， [https://thesciencebrigade.com/JAIR/article/view/98](https://thesciencebrigade.com/JAIR/article/view/98)  
40. Interest-based Negotiation in Multi-Agent Systems \- Minerva Access, 访问时间为 四月 18, 2025， [https://minerva-access.unimelb.edu.au/bitstreams/221011ec-eba9-5408-a4eb-06f9e2a40881/download](https://minerva-access.unimelb.edu.au/bitstreams/221011ec-eba9-5408-a4eb-06f9e2a40881/download)  
41. The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver \- Reid G. Smith, 访问时间为 四月 18, 2025， [https://www.reidgsmith.com/The\_Contract\_Net\_Protocol\_Dec-1980.pdf](https://www.reidgsmith.com/The_Contract_Net_Protocol_Dec-1980.pdf)  
42. Multi-agent Systems and Coordination: Techniques for Effective Agent Collaboration, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-and-coordination/](https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-and-coordination/)  
43. Review of Wooldridge, Michael: An Introduction to Multi-Agent Systems \- JASSS, 访问时间为 四月 18, 2025， [https://www.jasss.org/7/3/reviews/robertson.html](https://www.jasss.org/7/3/reviews/robertson.html)  
44. Multi-Agent Systems Fundamentals \- A Personal Experience \- Catio.tech, 访问时间为 四月 18, 2025， [https://www.catio.tech/blog/multi-agent-systems-fundamentals---a-personal-experience](https://www.catio.tech/blog/multi-agent-systems-fundamentals---a-personal-experience)  
45. Agent Communication and Interaction Protocols: Key Concepts and Best Practices, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/ai-agent-development/agent-communication-and-interaction-protocols/](https://smythos.com/ai-agents/ai-agent-development/agent-communication-and-interaction-protocols/)  
46. Comparing Agent Communication Languages and Protocols: Choosing the Right Framework for Multi-Agent Systems \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/ai-agent-development/agent-communication-languages-and-protocols-comparison/](https://smythos.com/ai-agents/ai-agent-development/agent-communication-languages-and-protocols-comparison/)  
47. AA'01 Tutorial on Agent Communication Languages \- UMBC CSEE, 访问时间为 四月 18, 2025， [https://www.csee.umbc.edu/\~finin/talks/691m.pdf](https://www.csee.umbc.edu/~finin/talks/691m.pdf)  
48. Standards and Interoperability – IEEE Power & Energy Society Multi-Agent Systems Working Group, 访问时间为 四月 18, 2025， [https://site.ieee.org/pes-mas/agent-technology/standards-and-interoperability/](https://site.ieee.org/pes-mas/agent-technology/standards-and-interoperability/)  
49. The FIPA-OS agent platform: Open Source for Open Standards, 访问时间为 四月 18, 2025， [http://www.eecs.qmul.ac.uk/\~stefan/publications/2000-paam2000-fipaos.pdf](http://www.eecs.qmul.ac.uk/~stefan/publications/2000-paam2000-fipaos.pdf)  
50. Department of Electrical and Computer Engineering SENG 609.22 – Agent Based Software Engineering Tutorial Report Agent Communi \- CiteSeerX, 访问时间为 四月 18, 2025， [https://citeseerx.ist.psu.edu/document?repid=rep1\&type=pdf\&doi=5c199c3d9b0f7a08c2cfb236ad4de19a3b27c1f6](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=5c199c3d9b0f7a08c2cfb236ad4de19a3b27c1f6)  
51. Agent Communication Languages: Rethinking the Principles \- computer science at N.C. State, 访问时间为 四月 18, 2025， [https://www.csc2.ncsu.edu/faculty/mpsingh/papers/mas/computer-acl-98.pdf](https://www.csc2.ncsu.edu/faculty/mpsingh/papers/mas/computer-acl-98.pdf)  
52. Agent Communication Languages \- Computer Science and Electrical Engineering, 访问时间为 四月 18, 2025， [https://redirect.cs.umbc.edu/courses/pub/finin/papers/papers/asama99tutorial.pdf](https://redirect.cs.umbc.edu/courses/pub/finin/papers/papers/asama99tutorial.pdf)  
53. What is Multi-Agent Reinforcement Learning (MARL) \- Activeloop, 访问时间为 四月 18, 2025， [https://www.activeloop.ai/resources/glossary/multi-agent-reinforcement-learning-marl/](https://www.activeloop.ai/resources/glossary/multi-agent-reinforcement-learning-marl/)  
54. The Future of Multi-Agent Systems: Trends, Challenges, and Opportunities \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/multi-agent-systems/future-of-multi-agent-systems/](https://smythos.com/ai-agents/multi-agent-systems/future-of-multi-agent-systems/)  
55. What are popular frameworks for building multi-agent systems? \- Milvus, 访问时间为 四月 18, 2025， [https://milvus.io/ai-quick-reference/what-are-popular-frameworks-for-building-multiagent-systems](https://milvus.io/ai-quick-reference/what-are-popular-frameworks-for-building-multiagent-systems)  
56. A Review of Multi-Agent Reinforcement Learning Algorithms \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/2079-9292/14/4/820](https://www.mdpi.com/2079-9292/14/4/820)  
57. All You Need to Know About Multi-Agent Reinforcement Learning, 访问时间为 四月 18, 2025， [https://adasci.org/all-you-need-to-know-about-multi-agent-reinforcement-learning/](https://adasci.org/all-you-need-to-know-about-multi-agent-reinforcement-learning/)  
58. Multi-Agent Reinforcement Learning: A Review of Challenges and Applications \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/2076-3417/11/11/4948](https://www.mdpi.com/2076-3417/11/11/4948)  
59. MARLlib: A Scalable and Efficient Multi-agent Reinforcement Learning Library, 访问时间为 四月 18, 2025， [https://www.jmlr.org/papers/v24/23-0378.html](https://www.jmlr.org/papers/v24/23-0378.html)  
60. Challenges and Opportunities for Multi-Agent Reinforcement Learning – AAAI Spring Symposium 2020 \- Frans A. Oliehoek, 访问时间为 四月 18, 2025， [https://www.fransoliehoek.net/wp/2019/challenges-and-opportunities-for-multi-agent-reinforcement-learning-aaai-spring-symposium-2020/](https://www.fransoliehoek.net/wp/2019/challenges-and-opportunities-for-multi-agent-reinforcement-learning-aaai-spring-symposium-2020/)  
61. Multi-Agent Reinforcement Learning: A Review of Challenges and Applications, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/351926368\_Multi-Agent\_Reinforcement\_Learning\_A\_Review\_of\_Challenges\_and\_Applications](https://www.researchgate.net/publication/351926368_Multi-Agent_Reinforcement_Learning_A_Review_of_Challenges_and_Applications)  
62. (PDF) Stability analysis method and application of multi-agent systems from the perspective of hybrid systems \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/357293391\_Stability\_analysis\_method\_and\_application\_of\_multi-agent\_systems\_from\_the\_perspective\_of\_hybrid\_systems](https://www.researchgate.net/publication/357293391_Stability_analysis_method_and_application_of_multi-agent_systems_from_the_perspective_of_hybrid_systems)  
63. A Survey of Multi-agent Coordination. \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/220834642\_A\_Survey\_of\_Multi-agent\_Coordination](https://www.researchgate.net/publication/220834642_A_Survey_of_Multi-agent_Coordination)  
64. Flexible Agent Architecture: Mixing Reactive and Deliberative Behaviors in SPADE \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/2079-9292/12/3/659](https://www.mdpi.com/2079-9292/12/3/659)  
65. Types of Agent Architectures: A Guide to Reactive ... \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/agent-architectures/types-of-agent-architectures/](https://smythos.com/ai-agents/agent-architectures/types-of-agent-architectures/)  
66. RAG, AI Agents, and Agentic RAG: An In-Depth Review and Comparative Analysis, 访问时间为 四月 18, 2025， [https://www.digitalocean.com/community/conceptual-articles/rag-ai-agents-agentic-rag-comparative-analysis](https://www.digitalocean.com/community/conceptual-articles/rag-ai-agents-agentic-rag-comparative-analysis)  
67. A multi-agent system of artificial intelligence forming principles., 访问时间为 四月 18, 2025， [https://cit.lntu.edu.ua/index.php/cit/article/view/372](https://cit.lntu.edu.ua/index.php/cit/article/view/372)  
68. (PDF) On the architectures of complex multi-agent systems \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/228604746\_On\_the\_architectures\_of\_complex\_multi-agent\_systems](https://www.researchgate.net/publication/228604746_On_the_architectures_of_complex_multi-agent_systems)  
69. Understanding BDI Agents in Agent-Oriented Programming \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/agent-architectures/agent-oriented-programming-and-bdi-agents/](https://smythos.com/ai-agents/agent-architectures/agent-oriented-programming-and-bdi-agents/)  
70. Trusted AI and the Contribution ofTrust Modeling in Multiagent Systems \- IFAAMAS, 访问时间为 四月 18, 2025， [https://www.ifaamas.org/Proceedings/aamas2019/pdfs/p1644.pdf](https://www.ifaamas.org/Proceedings/aamas2019/pdfs/p1644.pdf)  
71. A Trust Establishment Model in Multi-Agent Systems \- AAAI, 访问时间为 四月 18, 2025， [https://cdn.aaai.org/ocs/ws/ws0005/10055-45962-1-PB.pdf](https://cdn.aaai.org/ocs/ws/ws0005/10055-45962-1-PB.pdf)  
72. Reactive and Deliberative AI agents \- Vikas Goyal, 访问时间为 四月 18, 2025， [https://vikasgoyal.github.io/agentic/reactivedeliberativeagents.html](https://vikasgoyal.github.io/agentic/reactivedeliberativeagents.html)  
73. Integration of Reactive and Telerobotic Control in Multi-agent Robotic Systems, 访问时间为 四月 18, 2025， [https://www-robotics.jpl.nasa.gov/media/documents/sab94.pdf](https://www-robotics.jpl.nasa.gov/media/documents/sab94.pdf)  
74. BDI: Applications and Architectures \- International Journal of Engineering Research & Technology, 访问时间为 四月 18, 2025， [https://www.ijert.org/research/bdi-applications-and-architectures-IJERTV2IS2173.pdf](https://www.ijert.org/research/bdi-applications-and-architectures-IJERTV2IS2173.pdf)  
75. Deliberative Agents: AI & Multi-Agent Systems \- StudySmarter, 访问时间为 四月 18, 2025， [https://www.studysmarter.co.uk/explanations/engineering/artificial-intelligence-engineering/deliberative-agents/](https://www.studysmarter.co.uk/explanations/engineering/artificial-intelligence-engineering/deliberative-agents/)  
76. BDI Agents: From Theory to Practice Anand S. Rao and Michael P. Georgeff \- AAAI, 访问时间为 四月 18, 2025， [https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf](https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf)  
77. COMPUTATIONAL LOGICS AND AGENTS \- \[A Roadmap of Current Technologies and Future Trends\], 访问时间为 四月 18, 2025， [https://www.csc.liv.ac.uk/\~michael/comp-int-www.pdf](https://www.csc.liv.ac.uk/~michael/comp-int-www.pdf)  
78. Leveraging the Beliefs-Desires-Intentions Agent Architecture | Microsoft Learn, 访问时间为 四月 18, 2025， [https://learn.microsoft.com/en-us/archive/msdn-magazine/2019/january/machine-learning-leveraging-the-beliefs-desires-intentions-agent-architecture](https://learn.microsoft.com/en-us/archive/msdn-magazine/2019/january/machine-learning-leveraging-the-beliefs-desires-intentions-agent-architecture)  
79. (PDF) The Belief-Desire-Intention Model of Agency \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/2596320\_The\_Belief-Desire-Intention\_Model\_of\_Agency](https://www.researchgate.net/publication/2596320_The_Belief-Desire-Intention_Model_of_Agency)  
80. Modularization in Belief-Desire-Intention agent programming and artifact-based environments \- PMC, 访问时间为 四月 18, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC9748826/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9748826/)  
81. What are hybrid multi-agent systems? \- Milvus, 访问时间为 四月 18, 2025， [https://milvus.io/ai-quick-reference/what-are-hybrid-multiagent-systems](https://milvus.io/ai-quick-reference/what-are-hybrid-multiagent-systems)  
82. Enhancing Enterprise AI with Multi-hop Orchestration Agents: Advanced Reasoning for Accurate, Reliable Decision Making \- C3 AI, 访问时间为 四月 18, 2025， [https://c3.ai/blog/enhancing-enterprise-ai-with-multi-hop-orchestration-agents-advanced-reasoning-for-accurate-reliable-decision-making-part-2/](https://c3.ai/blog/enhancing-enterprise-ai-with-multi-hop-orchestration-agents-advanced-reasoning-for-accurate-reliable-decision-making-part-2/)  
83. Multi-Agent Environment Tools: Top Frameworks \- Rapid Innovation, 访问时间为 四月 18, 2025， [https://www.rapidinnovation.io/post/frameworks-and-tools-for-building-multi-agent-environments](https://www.rapidinnovation.io/post/frameworks-and-tools-for-building-multi-agent-environments)  
84. Comparison of Multi-Agent Platform Usability for Industrial-Grade Applications \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/2076-3417/14/22/10124](https://www.mdpi.com/2076-3417/14/22/10124)  
85. Agentic Frameworks in Java with JADE \- DEV Community, 访问时间为 四月 18, 2025， [https://dev.to/vishalmysore/agentic-frameworks-in-java-with-jade-4ma1](https://dev.to/vishalmysore/agentic-frameworks-in-java-with-jade-4ma1)  
86. Java Agent DEvelopment Framework \- JADE \- Invoxico Technologies, 访问时间为 四月 18, 2025， [https://www.invoxico.com/java-agent-development-framework-jade/](https://www.invoxico.com/java-agent-development-framework-jade/)  
87. Who | Jade Site \- Java Agent DEvelopment Framework, 访问时间为 四月 18, 2025， [https://jade.tilab.com/who/](https://jade.tilab.com/who/)  
88. Java Agent Development Framework \- Wikipedia, 访问时间为 四月 18, 2025， [https://en.wikipedia.org/wiki/Java\_Agent\_Development\_Framework](https://en.wikipedia.org/wiki/Java_Agent_Development_Framework)  
89. JADE for Autonomous Agent Development \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/ai-agent-development/jade-java-agent-development-framework/](https://smythos.com/ai-agents/ai-agent-development/jade-java-agent-development-framework/)  
90. About JADE, 访问时间为 四月 18, 2025， [https://jade-project.gitlab.io/page/about/](https://jade-project.gitlab.io/page/about/)  
91. (PDF) Integrating Jason into AgentScape \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/253016443\_Integrating\_Jason\_into\_AgentScape](https://www.researchgate.net/publication/253016443_Integrating_Jason_into_AgentScape)  
92. An overview of Jason \- DTAI, 访问时间为 四月 18, 2025， [https://dtai.cs.kuleuven.be/projects/ALP/newsletter/aug06/nav/articles/article5/article.html](https://dtai.cs.kuleuven.be/projects/ALP/newsletter/aug06/nav/articles/article5/article.html)  
93. Jason is a fully-fledged interpreter for an extended version of AgentSpeak, a BDI agent-oriented logic programming language. \- GitHub, 访问时间为 四月 18, 2025， [https://github.com/jason-lang/jason](https://github.com/jason-lang/jason)  
94. jason download | SourceForge.net, 访问时间为 四月 18, 2025， [https://sourceforge.net/projects/jason/](https://sourceforge.net/projects/jason/)  
95. Projects \- Jason, a BDI agent programming language, 访问时间为 四月 18, 2025， [https://jason-lang.github.io/projects/](https://jason-lang.github.io/projects/)  
96. Getting Started with Jason, 访问时间为 四月 18, 2025， [https://www.emse.fr/\~boissier/enseignement/maop14/DOC/jason/mini-tutorial/getting-started/index.html](https://www.emse.fr/~boissier/enseignement/maop14/DOC/jason/mini-tutorial/getting-started/index.html)  
97. LightJason — AgentSpeak(L++) Component, 访问时间为 四月 18, 2025， [https://lightjason.org/framework/agentspeak/](https://lightjason.org/framework/agentspeak/)  
98. Multi AI Agent Systems with crewAI \- DeepLearning.AI, 访问时间为 四月 18, 2025， [https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)  
99. Multi Agent Systems and how to build them, 访问时间为 四月 18, 2025， [https://learn.crewai.com/](https://learn.crewai.com/)  
100. Insights and Learnings from Building a Complex Multi-Agent System : r/LangChain \- Reddit, 访问时间为 四月 18, 2025， [https://www.reddit.com/r/LangChain/comments/1byz3lr/insights\_and\_learnings\_from\_building\_a\_complex/](https://www.reddit.com/r/LangChain/comments/1byz3lr/insights_and_learnings_from_building_a_complex/)  
101. The Evolution of the Contract Net Protocol \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/221509636\_The\_Evolution\_of\_the\_Contract\_Net\_Protocol](https://www.researchgate.net/publication/221509636_The_Evolution_of_the_Contract_Net_Protocol)  
102. Computational Models for Argumentation in MAS, 访问时间为 四月 18, 2025， [https://cs.uns.edu.ar/\~grs/Publications/tutorial-2ndpart-BW.pdf](https://cs.uns.edu.ar/~grs/Publications/tutorial-2ndpart-BW.pdf)  
103. Contract Net Protocol for Coordination in Multi-Agent System | Request PDF \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/232636898\_Contract\_Net\_Protocol\_for\_Coordination\_in\_Multi-Agent\_System](https://www.researchgate.net/publication/232636898_Contract_Net_Protocol_for_Coordination_in_Multi-Agent_System)  
104. Agent Communication and Negotiation: Enhancing Decision-Making and Collaboration in Multi-Agent Systems \- SmythOS, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/agent-architectures/agent-communication-and-negotiation/](https://smythos.com/ai-agents/agent-architectures/agent-communication-and-negotiation/)  
105. Multi-Agent Systems and Negotiation: Strategies for Effective Agent Collaboration, 访问时间为 四月 18, 2025， [https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-and-negotiation/](https://smythos.com/ai-agents/multi-agent-systems/multi-agent-systems-and-negotiation/)  
106. Contract Net Protocol \- Wikipedia, 访问时间为 四月 18, 2025， [https://en.wikipedia.org/wiki/Contract\_Net\_Protocol](https://en.wikipedia.org/wiki/Contract_Net_Protocol)  
107. Contract net protocol – Knowledge and References \- Taylor & Francis, 访问时间为 四月 18, 2025， [https://taylorandfrancis.com/knowledge/Engineering\_and\_technology/Artificial\_intelligence/Contract\_net\_protocol/](https://taylorandfrancis.com/knowledge/Engineering_and_technology/Artificial_intelligence/Contract_net_protocol/)  
108. Modification of Contract Net Protocol (CNP) : A Rule-Updation Approach, 访问时间为 四月 18, 2025， [https://thesai.org/Publications/ViewPaper?Volume=4\&Issue=11\&Code=IJACSA\&SerialNo=6](https://thesai.org/Publications/ViewPaper?Volume=4&Issue=11&Code=IJACSA&SerialNo=6)  
109. \[1312.4259\] Modification of Contract Net Protocol(CNP) : A Rule-Updation Approach \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/abs/1312.4259](https://arxiv.org/abs/1312.4259)  
110. On the Argumentative Agent Types and Negotiation | Request PDF \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/279131451\_On\_the\_Argumentative\_Agent\_Types\_and\_Negotiation](https://www.researchgate.net/publication/279131451_On_the_Argumentative_Agent_Types_and_Negotiation)  
111. Interest-based Negotiation in Multi-Agent Systems \- CiteSeerX, 访问时间为 四月 18, 2025， [https://citeseerx.ist.psu.edu/document?repid=rep1\&type=pdf\&doi=1a00b193cd709bc7e9def993f4794a7d7e856e9c](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=1a00b193cd709bc7e9def993f4794a7d7e856e9c)  
112. RaghuHemadri/Multi-Agent-Reinforcement-Learning-Survey-Papers \- GitHub, 访问时间为 四月 18, 2025， [https://github.com/RaghuHemadri/Multi-Agent-Reinforcement-Learning-Survey-Papers](https://github.com/RaghuHemadri/Multi-Agent-Reinforcement-Learning-Survey-Papers)  
113. 10 Types of Multi-Agent Systems \- Integrail, 访问时间为 四月 18, 2025， [https://integrail.ai/blog/types-of-multi-agent-systems](https://integrail.ai/blog/types-of-multi-agent-systems)  
114. Tutorials – AAMAS 2025 Detroit, 访问时间为 四月 18, 2025， [https://aamas2025.org/index.php/conference/program/tutorials/](https://aamas2025.org/index.php/conference/program/tutorials/)  
115. Towards a Standardised Performance Evaluation Protocol for Cooperative MARL \- NeurIPS, 访问时间为 四月 18, 2025， [https://proceedings.neurips.cc/paper\_files/paper/2022/file/249f73e01f0a2bb6c8d971b565f159a7-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2022/file/249f73e01f0a2bb6c8d971b565f159a7-Paper-Conference.pdf)  
116. \[2502.14743\] Multi-Agent Coordination across Diverse Applications: A Survey \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/abs/2502.14743](https://arxiv.org/abs/2502.14743)  
117. Multi-Agent Planning and Diagnosis with Commonsense Reasoning \- Washington University, 访问时间为 四月 18, 2025， [https://yeoh-lab.wustl.edu/assets/pdf/dai-Son0SK23.pdf](https://yeoh-lab.wustl.edu/assets/pdf/dai-Son0SK23.pdf)  
118. Multi-Agent Coordination Across Diverse Applications: A Survey (Feb 2025\) \- YouTube, 访问时间为 四月 18, 2025， [https://www.youtube.com/watch?v=jDVX6HI38bA](https://www.youtube.com/watch?v=jDVX6HI38bA)  
119. Multi-Agent Coordination for Strategic Maneuver with a Survey of Reinforcement Learning \- DTIC, 访问时间为 四月 18, 2025， [https://apps.dtic.mil/sti/trecms/pdf/AD1154872.pdf](https://apps.dtic.mil/sti/trecms/pdf/AD1154872.pdf)  
120. The Five Golden Rules of Negotiation for Lawyers, 访问时间为 四月 18, 2025， [https://www.expertnegotiator.com/blog/strategically-speaking-five-golden-rules-negotiation-lawyers/](https://www.expertnegotiator.com/blog/strategically-speaking-five-golden-rules-negotiation-lawyers/)  
121. Multi-Agent Systems \- IJCAI, 访问时间为 四月 18, 2025， [https://www.ijcai.org/Proceedings/01/IJCAI-2001-m.pdf](https://www.ijcai.org/Proceedings/01/IJCAI-2001-m.pdf)  
122. A Survey of Multi-Agent Deep Reinforcement Learning with Communication \- arXiv, 访问时间为 四月 18, 2025， [https://arxiv.org/html/2203.08975v2](https://arxiv.org/html/2203.08975v2)  
123. arxiv.org, 访问时间为 四月 18, 2025， [https://arxiv.org/abs/2312.10256](https://arxiv.org/abs/2312.10256)  
124. Multi-Agent Deep Reinforcement Learning for Multi-Robot Applications: A Survey \- MDPI, 访问时间为 四月 18, 2025， [https://www.mdpi.com/1424-8220/23/7/3625](https://www.mdpi.com/1424-8220/23/7/3625)  
125. (PDF) A Comprehensive Survey of Multiagent Reinforcement Learning \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/3421909\_A\_Comprehensive\_Survey\_of\_Multiagent\_Reinforcement\_Learning](https://www.researchgate.net/publication/3421909_A_Comprehensive_Survey_of_Multiagent_Reinforcement_Learning)  
126. Off-Policy Correction For Multi-Agent Reinforcement Learning \- deepsense.ai, 访问时间为 四月 18, 2025， [https://deepsense.ai/resource/off-policy-correction-for-multi-agent-reinforcement-learning/](https://deepsense.ai/resource/off-policy-correction-for-multi-agent-reinforcement-learning/)  
127. arXiv:2203.08975v2 \[cs.MA\] 18 Oct 2024, 访问时间为 四月 18, 2025， [https://arxiv.org/pdf/2203.08975](https://arxiv.org/pdf/2203.08975)  
128. Multi-agent Reinforcement Learning: A Comprehensive Survey : r/reinforcementlearning, 访问时间为 四月 18, 2025， [https://www.reddit.com/r/reinforcementlearning/comments/197lq1j/multiagent\_reinforcement\_learning\_a\_comprehensive/](https://www.reddit.com/r/reinforcementlearning/comments/197lq1j/multiagent_reinforcement_learning_a_comprehensive/)  
129. Lifelong Multi-Agent Path Finding in Large-Scale Warehouses, 访问时间为 四月 18, 2025， [https://ojs.aaai.org/index.php/AAAI/article/view/17344/17151](https://ojs.aaai.org/index.php/AAAI/article/view/17344/17151)  
130. Applications of Multi-Agent Systems in Smart Grids: A survey \- ResearchGate, 访问时间为 四月 18, 2025， [https://www.researchgate.net/publication/286109101\_Applications\_of\_Multi-Agent\_Systems\_in\_Smart\_Grids\_A\_survey](https://www.researchgate.net/publication/286109101_Applications_of_Multi-Agent_Systems_in_Smart_Grids_A_survey)
