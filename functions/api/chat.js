/**
 * 博客数字分身助手 - 后端API
 * 处理前端聊天请求，支持RAG检索和多轮对话
 * 
 * 架构升级 (2025-12-12):
 * - Embedding: @cf/baai/bge-m3 (多语言/中文优化, 1024维)
 * - Reranking: @cf/baai/bge-reranker-base (二阶段重排)
 * - Retrieval: Vector Search (Top-20) -> Rerank (Top-5)
 */

// Cloudflare Workers AI 模型ID常量
const EMBEDDING_MODEL = "@cf/baai/bge-m3";
const RERANKER_MODEL = "@cf/baai/bge-reranker-base";
const LLM_MODEL = "@cf/meta/llama-3-8b-instruct";

// 配置常量
const MAX_MESSAGE_LENGTH = 1000;
const MAX_HISTORY_TURNS = 3;
const TOP_K_RETRIEVAL = 20; // 初筛数量
const TOP_K_FINAL = 5;      // 最终上下文数量
const MIN_SCORE_RERANK = 0.25; // Reranker分数阈值 (Sigmoid后通常在0-1之间, 0.25相对宽松但能过滤无关内容)
const BLOG_AUTHOR_NAME = "Peng Tan";

/**
 * 获取Vectorize绑定 (兼容多种命名)
 */
function getVectorIndexBinding(env) {
  return env.VECTOR_INDEX || env.VECTORIZE_INDEX || env.VECTORIZE;
}

/**
 * 组装System Prompt
 */
function buildSystemPrompt(retrievedContexts) {
  const contextText = retrievedContexts
    .map((ctx, idx) => `[${idx + 1}] (Score: ${ctx.score.toFixed(2)}) ${ctx.text}`)
    .join("\n\n");
  const sources = retrievedContexts
    .map((ctx, idx) => `[${idx + 1}] ${ctx.title || "Untitled"} (${ctx.url || "No URL"})`)
    .join("\n");
    
  return `You are the digital twin of ${BLOG_AUTHOR_NAME}. Use the provided Context to answer the user's question.

Context:
${contextText}

Sources:
${sources}

Instructions:
1. Answer strictly based on the provided Context. Do not invent facts.
2. If the Context does not contain the answer, reply exactly: "没有找到相关内容".
3. Answer in Chinese (Simplified) unless the user asks otherwise.
4. Keep answers concise and informative.
5. You MUST cite your sources using the format [1], [2] corresponding to the Context items.`;
}

/**
 * 截断对话历史，保留最近N轮
 */
function truncateHistory(history, maxTurns = MAX_HISTORY_TURNS) {
  if (!history || history.length === 0) {
    return [];
  }
  
  const maxMessages = maxTurns * 2;
  if (history.length <= maxMessages) {
    return history;
  }
  
  return history.slice(-maxMessages);
}

/**
 * 推断问题分类 (用于Metadata过滤)
 */
function inferCategory(message) {
  const q = String(message || "");
  if (/(每日AI|Daily AI)/i.test(q) || /每日|日报|daily/i.test(q)) return "daily_ai";
  if (/论文|paper|arxiv|学术/i.test(q)) return "papers";
  if (/产品|工具|cursor|产品评测/i.test(q)) return "products";
  if (/项目|projects|项目描述/i.test(q)) return "projects";
  if (/基础|rag|检索|向量|embedding/i.test(q)) return "rag";
  return null;
}

/**
 * 处理POST /api/chat请求
 */
export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    // 1. 解析请求体
    const body = await request.json();
    const { message, history = [] } = body;
    
    // 2. 输入校验
    if (!message || typeof message !== 'string') {
      return new Response(JSON.stringify({ error: "message字段是必需的" }), { status: 400 });
    }
    
    if (message.length > MAX_MESSAGE_LENGTH) {
      return new Response(JSON.stringify({ error: "消息过长" }), { status: 400 });
    }
    
    // 3. 生成Query Embedding (Stage 1: Retrieval)
    let queryEmbedding;
    try {
      const embeddingResponse = await env.AI.run(EMBEDDING_MODEL, { text: message });
      // bge-m3 兼容处理
      if (embeddingResponse.data && embeddingResponse.data[0]) {
         queryEmbedding = embeddingResponse.data[0].embedding || embeddingResponse.data[0];
      } else if (embeddingResponse.embedding) {
         queryEmbedding = embeddingResponse.embedding;
      } else {
         // 某些情况直接返回数组
         queryEmbedding = embeddingResponse; 
      }
      
      if (!Array.isArray(queryEmbedding)) {
         throw new Error("Embedding格式错误");
      }
    } catch (error) {
      console.error("Embedding generation failed:", error);
      return new Response(JSON.stringify({ error: "检索服务繁忙" }), { status: 500 });
    }
    
    // 4. 向量检索 (Vector Search)
    let candidates = [];
    try {
      const vectorClient = getVectorIndexBinding(env);
      if (!vectorClient) throw new Error("Vector Index未绑定");
      
      const category = inferCategory(message);
      const queryOptions = { topK: TOP_K_RETRIEVAL, returnMetadata: true };
      
      // 尝试带分类检索
      if (category) {
        queryOptions.filter = { category: { $eq: category } };
      }
      
      let vectorQuery = await vectorClient.query(queryEmbedding, queryOptions);
      
      // 降级策略: 如果带分类检索无结果，回退到全局检索
      if ((!vectorQuery.matches || vectorQuery.matches.length === 0) && category) {
        delete queryOptions.filter;
        vectorQuery = await vectorClient.query(queryEmbedding, queryOptions);
      }
      
      candidates = vectorQuery.matches || [];
    } catch (error) {
      console.error("Vector search failed:", error);
    }
    
    // 5. 重排序 (Reranking - Stage 2: Precision)
    let finalContexts = [];
    if (candidates.length > 0) {
      try {
        // 去重 (基于URL或文本)
        const uniqMap = new Map();
        candidates.forEach(c => {
          const key = c.metadata?.url || c.id;
          if (!uniqMap.has(key)) {
            uniqMap.set(key, {
              id: c.id,
              text: c.metadata?.text || "",
              title: c.metadata?.title || "",
              url: c.metadata?.url || ""
            });
          }
        });
        
        const uniqueCandidates = Array.from(uniqMap.values()).filter(c => c.text);
        
        if (uniqueCandidates.length > 0) {
          // 调用 Reranker
          const rerankResponse = await env.AI.run(RERANKER_MODEL, {
            query: message,
            source_documents: uniqueCandidates.map(c => c.text)
          });
          
          // 解析 Rerank 结果
          // rerankResponse 格式通常为: { results: [ { index: 0, score: 0.9 }, ... ] }
          if (rerankResponse.results) {
            const ranked = rerankResponse.results
              .filter(r => r.score >= MIN_SCORE_RERANK)
              .sort((a, b) => b.score - a.score) // 降序
              .slice(0, TOP_K_FINAL);
              
            if (ranked.length > 0) {
              finalContexts = ranked.map(r => {
                const candidate = uniqueCandidates[r.index];
                return {
                  ...candidate,
                  score: r.score
                };
              });
            } else {
              // Fallback: if all reranked results are filtered out, use top vector search results
              finalContexts = uniqueCandidates.slice(0, TOP_K_FINAL).map(c => ({...c, score: 0.5}));
            }
          } else {
            // Fallback if reranker fails to return standard format
            finalContexts = uniqueCandidates.slice(0, TOP_K_FINAL).map(c => ({...c, score: 0.5}));
          }
        }
      } catch (error) {
        console.error("Reranking failed:", error);
        // Fallback: use vector search order
        finalContexts = candidates
          .filter(c => c.metadata?.text)
          .slice(0, TOP_K_FINAL)
          .map(c => ({
            text: c.metadata.text,
            title: c.metadata?.title,
            url: c.metadata?.url,
            score: c.score
        }));
      }
    }
    
    // 6. 兜底响应
    if (finalContexts.length === 0) {
      return new Response(JSON.stringify({ 
        response: "没有找到相关内容", 
        references: [] 
      }), { 
        status: 200, 
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } 
      });
    }
    
    // 7. LLM 生成
    const systemPrompt = buildSystemPrompt(finalContexts);
    const messages = [
      { role: "system", content: systemPrompt },
      ...truncateHistory(history),
      { role: "user", content: message }
    ];
    
    const llmResponse = await env.AI.run(LLM_MODEL, { messages });
    let aiResponse = "";
    if (typeof llmResponse === 'string') aiResponse = llmResponse;
    else if (llmResponse.response) aiResponse = llmResponse.response;
    else if (llmResponse.choices) aiResponse = llmResponse.choices[0].message?.content || "";
    
    // 8. 返回结果
    return new Response(JSON.stringify({
      response: aiResponse,
      references: finalContexts.map(c => ({ title: c.title, url: c.url }))
    }), {
      status: 200,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      }
    });
    
  } catch (error) {
    console.error("Server Error:", error);
    return new Response(JSON.stringify({ error: "服务暂时不可用" }), { status: 500 });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }
  });
}
