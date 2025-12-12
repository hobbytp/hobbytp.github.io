# **产品需求文档 (PRD): 基于 RAG 的博客数字分身助手 (v1.1)**

## **1\. 项目概述 (Project Overview)**

目标：在现有的 Hugo \+ Cloudflare Pages 博客架构中，集成一个 AI 聊天助手。该助手通过 RAG (检索增强生成) 技术，检索博客的历史文章内容，模拟博主的语气与访客进行对话。  
核心价值：提升访客互动性，将静态阅读转化为动态问答，打造“数字分身”。

## **2\. 技术栈架构 (Tech Stack)**

* **前端宿主**：Hugo (PaperMod 主题) / HTML \+ Vanilla JS  
* **应用托管**：Cloudflare Pages  
* **后端逻辑**：Cloudflare Pages Functions (Serverless)  
* **向量数据库**：Cloudflare Vectorize  
* **AI 推理引擎**：Cloudflare Workers AI  
  * **Embedding 模型**：@cf/baai/bge-base-en-v1.5 (推荐，支持中英文)  
  * **生成模型 (LLM)**：@cf/meta/llama-3-8b-instruct  
* **数据处理脚本**：Python 3 (本地运行，通过 REST API 与 Cloudflare 通信)

## **3\. 系统架构图 (System Architecture)**

sequenceDiagram  
    participant User as 用户 (Browser)  
    participant Front as 聊天 UI  
    participant Func as Pages Function (/api/chat)  
    participant AI as Workers AI (Embeddings)  
    participant Vec as Vectorize DB  
    participant LLM as Workers AI (Llama-3)

    User-\>\>Front: 输入问题 "你对 K8s 怎么看？" (带上 history)  
    Front-\>\>Func: POST /api/chat {message, history}  
    Func-\>\>AI: 将当前 message 转换为向量 (Embed)  
    AI--\>\>Func: 返回向量数组  
    Func-\>\>Vec: Query(向量, topK=3)  
    Vec--\>\>Func: 返回相关文章片段 (Context)  
    Func-\>\>LLM: 组装 Prompt (System \+ Context \+ History \+ User)  
    LLM--\>\>Func: 生成回答  
    Func--\>\>Front: 返回 JSON {response}  
    Front--\>\>User: 渲染 Markdown 回答

## **4\. 功能模块详细需求 (Functional Requirements)**

### **模块 A: 数据摄取管道 (Data Ingestion Pipeline)**

描述：Python 脚本，用于解析 Hugo Markdown，向量化并通过 REST API 存入 Cloudflare Vectorize。  
文件位置：/scripts/ingest.py

* **环境依赖**：requests, python-frontmatter (需生成 requirements.txt)  
* **鉴权配置**：脚本需读取环境变量 CLOUDFLARE\_ACCOUNT\_ID 和 CLOUDFLARE\_API\_TOKEN。  
* **状态管理**：使用 `.ingest_state.json` 记录文件哈希，实现增量更新。  
* **自动化**：通过 GitHub Actions (`.github/workflows/rag-ingest.yml`) 自动触发，并自动提交状态文件。

### **模块 B: 后端 API (Pages Function)**

描述：处理前端请求的核心 Serverless 函数，支持多轮对话上下文。  
文件位置：/functions/api/chat.js

* **Endpoint**：POST /api/chat  
* **Request Body**：  
  {  
    "message": "Kubernetes 有什么缺点？",  
    "history": \[  
      {"role": "user", "content": "你懂 K8s 吗？"},  
      {"role": "assistant", "content": "我是博主的数字分身，我不止懂..."}  
    \]  
  }

* **环境变量 (Bindings)**：  
  * AI: Workers AI Binding  
  * VECTOR\_INDEX: Vectorize Index Binding  
* **处理流程**：  
  1. **输入校验**：限制 message 长度 (如 1000 字符)。  
  2. **生成 Query Embedding**：针对 message 生成向量。  
  3. **向量检索**：Query VECTOR\_INDEX (topK=3)。  
  4. **Prompt 组装策略**：  
     * **System**: 包含角色设定。  
     * **Context**: 插入检索到的文本片段："Use the following context to answer: ..."  
     * **History**: 插入最近 2-3 轮对话历史 (防止 Token 超限，需截断)。  
     * **User**: 当前问题。  
  5. **LLM 推理**：调用 Llama-3。  
  6. **错误处理**：如果 AI 调用失败，返回友好的 JSON 错误信息。

### **模块 C: 前端 UI 组件 (Frontend Widget)**

描述：嵌入博客的悬浮聊天窗。  
文件位置：layouts/partials/chatbox.html
样式文件：assets/css/extended/chat.css (移动到 extended 目录以被 Hugo 自动处理)

* **技术栈**：Vanilla JS (无框架依赖，确保轻量)。  
* **依赖**：marked.js (用于渲染 Markdown 回复)。

## **5\. 提示词工程规范 (System Prompt Spec)**

在 functions/api/chat.js 中，System Message 结构：

Role: You are the digital twin of \[Blog Author Name\]. You answer questions based strictly on the provided Context.

Context:  
${retrieved\_documents}

Instructions:  
1\. Use a professional, friendly, slightly geeky tone.  
2\. If the answer is not in the Context, say "My memory bank doesn't have info on this specific topic based on the blog posts."  
3\. Answer in the same language as the user's question (Default to Chinese).  
4\. Keep answers concise.

## **6\. 开发环境配置 (Environment Setup)**

Cursor 提示 (Cursor Prompts)：  
请告知 Cursor 以下细节以生成正确的配置：

* Wrangler 配置 (wrangler.toml):  
  需手动创建或更新该文件，以绑定本地开发环境与远程资源。  
  name \= "blog-digital-twin"  
  pages\_build\_output\_dir \= "public"  
  compatibility\_date \= "2024-04-01"

  \[\[vectorize\]\]  
  binding \= "VECTOR\_INDEX"  
  index\_name \= "blog-index"

  \[ai\]  
  binding \= "AI"

* **依赖安装**：需要提醒用户在本地运行 npm install marked 或在 HTML header 中添加 CDN script tag。

## **7\. 交付清单 (Deliverables)**

1. scripts/ingest.py: 包含幂等性逻辑的数据处理脚本。  
2. requirements.txt: Python 依赖列表。  
3. functions/api/chat.js: 含历史记录处理的后端。  
4. layouts/partials/chatbox.html: 含 marked.js 集成的前端。  
5. assets/css/extended/chat.css: 适配移动端的样式。  
6. .github/workflows/rag-ingest.yml: 自动化数据更新工作流。