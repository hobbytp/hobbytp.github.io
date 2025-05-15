



# 附录
## Ilya Sutskever推荐的30篇重要论文概述

<https://aman.ai/primers/ai/top-30-papers>
伊利亚・苏茨克维（Ilya Sutskever）与约翰・卡马克（John Carmack）分享了一份包含 30 篇论文的列表，并说道：“如果你真的学会了所有这些，你将了解当今 90% 的重要内容。” 下面我们将回顾这些[论文 / 资源](https://arc.net/folder/D0472A20-9C20-4D3F-B145-D2865C0A9FEE)。

### 摘要
本文提供了Ilya Sutskever推荐的30篇重要论文的概述，涵盖了复杂动力学、递归神经网络、卷积神经网络、注意力机制等领域的最新研究进展。这些论文为理解当前人工智能和机器学习领域的关键概念提供了重要的参考。

### 关键点
- Ilya Sutskever推荐的30篇重要论文列表，涵盖了复杂动力学、递归神经网络、卷积神经网络等领域。 
- “The First Law of Complexodynamics”讨论了物理系统复杂性的变化规律，提出了“complextropy”作为复杂性的新度量方式。 
- Andrej Karpathy的文章探讨了递归神经网络（RNN）的强大能力，尤其是在处理序列数据方面的应用。 
- Christopher Olah的文章解释了长短期记忆网络（LSTM）的结构和功能，解决了传统RNN在处理长期依赖性方面的局限。 
- 论文“Recurrent Neural Network Regularization”提出了一种新的LSTM正则化方法，通过在非递归连接应用dropout来减少过拟合。 
- Hinton和van Camp的论文介绍了一种通过最小化权重描述长度来简化神经网络的方法，以减少过拟合。 
- Oriol Vinyals等人的“Pointer Networks”提出了一种新型神经网络架构，能够处理可变长度的输出字典。 
- Alex Krizhevsky等人的论文介绍了深度卷积神经网络在ImageNet分类任务中的应用，取得了显著的性能提升。 
- Oriol Vinyals等人的“Order Matters: Sequence to Sequence for Sets”探讨了输入和输出顺序对序列到序列模型性能的影响。 
- GPipe通过微批次流水线并行化实现了大规模神经网络的高效训练。 
- Kaiming He等人的“Deep Residual Learning for Image Recognition”引入了残差网络（ResNet），显著提高了深度网络的训练效率和性能。 
- Fisher Yu等人的“Multi-Scale Context Aggregation by Dilated Convolutions”提出了一种改进语义分割的新方法，使用扩张卷积来聚合多尺度上下文信息。 
- Justin Gilmer等人的“Neural Message Passing for Quantum Chemistry”介绍了一种新的神经网络框架，用于预测分子图的量子化学属性。 
- Ashish Vaswani等人的“Attention Is All You Need”引入了Transformer架构，完全依赖自注意力机制，显著提高了序列转换任务的效率。 
- Dzmitry Bahdanau等人的论文提出了一种结合对齐和翻译的神经机器翻译方法，利用注意力机制提高了翻译质量。 
- Kaiming He等人的“Identity Mappings in Deep Residual Networks”探讨了身份映射在深度残差网络中的作用，提出了改进的残差单元设计。 
- Adam Santoro等人的“Relation Networks”引入了一种新的神经网络模块，用于解决需要关系推理的任务。 
- Xi Chen等人的“Variational Lossy Autoencoder”结合变分自编码器和自回归模型，实现了可控的表示学习和改进的密度估计。 
- Adam Santoro等人的“Relational Recurrent Neural Networks”介绍了一种新型记忆模块，改善了标准内存架构在处理复杂关系推理任务时的性能。 
- Scott Aaronson等人的论文探讨了封闭系统中复杂性的变化，使用“咖啡自动机”模型进行模拟。 
- Alex Graves等人的“Neural Turing Machines”介绍了一种结合神经网络和外部记忆资源的新架构，展示了其在算法任务中的卓越性能。 
- Baidu Research的“Deep Speech 2”提出了一种端到端的语音识别模型，能够处理英语和普通话。 
- Jared Kaplan等人的“Scaling Laws for Neural Language Models”探索了语言模型性能与模型大小、数据集大小和计算资源之间的关系。 
- Peter Grünwald的论文详细介绍了最小描述长度原则（MDL）的理论和应用。 
- Shane Legg的论文“Machine Super Intelligence”分析了超级智能机器发展的挑战和理论基础。 
- A. Shen等人的书籍“Kolmogorov Complexity and Algorithmic Randomness”提供了对Kolmogorov复杂性和算法随机性的深入探讨。 
- Stanford的CS231n课程介绍了卷积神经网络在视觉识别中的应用。 
- Fabian Gloeckle等人的论文“Better & Faster Large Language Models Via Multi-token Prediction”提出了一种多token预测的方法，提高了大语言模型的效率和性能。 
- Vladimir Karpukhin等人的“Dense Passage Retrieval for Open-Domain Question Answering”介绍了一种新方法，使用密集向量表示提高开放域问答的检索效率。 
- Lewis Tunstall等人的论文“HuggingFace Zephyr: Direct Distillation of LM Alignment”引入了一种新的蒸馏技术，以对齐小型语言模型与用户意图。 
- Liu等人的论文“Stanford Lost in the Middle: How Language Models Use Long Contexts”分析了语言模型在长上下文中使用相关信息的性能。 
- Gao等人的“Precise Zero-Shot Dense Retrieval Without Relevance Labels”提出了一种新的零样本密集检索方法，利用假想文档嵌入进行检索。 
- Xunjian Yin等人的“ALCUNA: Large Language Models Meet New Knowledge”提出了一种生成人工实体的新方法，用于评估大语言模型处理新知识的能力。 
- Dorian Quelle等人的论文“The Perils & Promises of Fact-checking with Large Language Models”评估了使用大型语言模型进行自动化事实核查的潜力和挑战。 