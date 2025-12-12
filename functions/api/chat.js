/**
 * 博客数字分身助手 - 后端API
 * 处理前端聊天请求，支持RAG检索和多轮对话
 */

// Cloudflare Workers AI 模型ID常量
const EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5";
const LLM_MODEL = "@cf/meta/llama-3-8b-instruct";

// 配置常量
const MAX_MESSAGE_LENGTH = 1000;
const MAX_HISTORY_TURNS = 3;
const TOP_K = 4;
const MIN_SCORE = 0.55;
const BLOG_AUTHOR_NAME = "Peng Tan";

/**
 * 组装System Prompt
 */
function buildSystemPrompt(retrievedContexts) {
  const contextText = retrievedContexts
    .map((ctx, idx) => `${idx + 1}. ${ctx.text}`)
    .join("\n\n");
  const sources = retrievedContexts
    .map((ctx, idx) => `${idx + 1}. ${ctx.title || ""} ${ctx.url || ""}`)
    .join("\n");
  return `You are the digital twin of ${BLOG_AUTHOR_NAME}. Only use the provided Context to answer.

Context:
${contextText}

Sources:
${sources}

Instructions:
1. Answer strictly based on Context. Do not invent facts.
2. If the answer is not in the Context, reply exactly: "没有找到相关内容".
3. Answer in Chinese (Simplified) unless the user asks otherwise.
4. Keep answers concise and include bracket citations like [1], [2] where appropriate.`;
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
      return new Response(
        JSON.stringify({ error: "message字段是必需的，且必须是字符串" }),
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }
    
    if (message.length > MAX_MESSAGE_LENGTH) {
      return new Response(
        JSON.stringify({ 
          error: `消息长度不能超过${MAX_MESSAGE_LENGTH}字符` 
        }),
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }
    
    // 验证history格式
    if (!Array.isArray(history)) {
      return new Response(
        JSON.stringify({ error: "history必须是数组" }),
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }
    
    // 3. 生成Query Embedding
    let queryEmbedding;
    try {
      const embeddingResponse = await env.AI.run(EMBEDDING_MODEL, {
        text: message
      });
      
      // 处理不同的响应格式
      if (embeddingResponse.data && Array.isArray(embeddingResponse.data)) {
        if (Array.isArray(embeddingResponse.data[0])) {
          // 格式: {data: [[...]]}
          queryEmbedding = embeddingResponse.data[0];
        } else if (embeddingResponse.data[0].embedding) {
          // OpenAI兼容格式: {data: [{embedding: [...]}]}
          queryEmbedding = embeddingResponse.data[0].embedding;
        } else {
          queryEmbedding = embeddingResponse.data[0];
        }
      } else if (embeddingResponse.embedding) {
        queryEmbedding = embeddingResponse.embedding;
      } else {
        throw new Error("无法解析embedding响应格式");
      }
    } catch (error) {
      console.error("生成embedding失败:", error);
      return new Response(
        JSON.stringify({ 
          error: "生成查询向量失败，请稍后重试",
          details: error.message 
        }),
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }
    
    let retrievedContexts = [];
    try {
      const category = inferCategory(message);
      const queryOptions = { topK: TOP_K * 2 };
      if (category) {
        queryOptions.filter = { category: { $eq: category } };
      }
      const vectorQuery = await env.VECTOR_INDEX.query(queryEmbedding, queryOptions);
      if (vectorQuery.matches && vectorQuery.matches.length > 0) {
        const uniq = new Map();
        vectorQuery.matches.forEach(match => {
          const text = match.metadata?.text || match.text || "";
          if (!text) return;
          const url = match.metadata?.url || "";
          const key = url || text.slice(0, 50);
          const item = {
            text,
            url,
            title: match.metadata?.title || "",
            score: typeof match.score === "number" ? match.score : 0
          };
          if (!uniq.has(key) || (uniq.get(key).score < item.score)) {
            uniq.set(key, item);
          }
        });
        retrievedContexts = Array.from(uniq.values())
          .sort((a, b) => b.score - a.score)
          .slice(0, TOP_K);
      }
    } catch (error) {
      console.error("向量检索失败:", error);
    }
    
    // 5. 组装Prompt
    if (!retrievedContexts.length || (retrievedContexts[0]?.score ?? 0) < MIN_SCORE) {
      const response = { response: "没有找到相关内容", references: [] };
      return new Response(JSON.stringify(response), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" } });
    }
    const systemPrompt = buildSystemPrompt(retrievedContexts);
    
    // 截断历史对话
    const truncatedHistory = truncateHistory(history);
    
    // 构建消息列表
    const messages = [
      { role: "system", content: systemPrompt },
      ...truncatedHistory,
      { role: "user", content: message }
    ];
    
    // 6. LLM推理
    let aiResponse;
    try {
      const llmResponse = await env.AI.run(LLM_MODEL, {
        messages: messages
      });
      
      // 处理不同的响应格式
      if (typeof llmResponse === 'string') {
        aiResponse = llmResponse;
      } else if (llmResponse.response) {
        aiResponse = llmResponse.response;
      } else if (llmResponse.choices && llmResponse.choices[0]) {
        aiResponse = llmResponse.choices[0].message?.content || 
                     llmResponse.choices[0].text || "";
      } else {
        throw new Error("无法解析LLM响应格式");
      }
    } catch (error) {
      console.error("LLM推理失败:", error);
      return new Response(
        JSON.stringify({ 
          error: "AI生成回答失败，请稍后重试",
          details: error.message 
        }),
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }
    
    // 7. 构建响应
    const response = {
      response: aiResponse,
      references: retrievedContexts.map(ctx => ({
        title: ctx.title,
        url: ctx.url
      })).filter(ref => ref.url)  // 只返回有URL的引用
    };
    
    return new Response(
      JSON.stringify(response),
      { 
        status: 200,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",  // CORS支持
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      }
    );
    
  } catch (error) {
    console.error("处理请求失败:", error);
    return new Response(
      JSON.stringify({ 
        error: "服务器内部错误",
        details: error.message 
      }),
      { 
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}

/**
 * 处理OPTIONS请求（CORS预检）
 */
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


function inferCategory(message) {
  const q = String(message || "");
  if (/[每日AI|Daily AI]/i.test(q) || /每日|日报|daily/i.test(q)) return "daily_ai";
  if (/论文|paper|arxiv|学术/i.test(q)) return "papers";
  if (/产品|工具|cursor|产品评测/i.test(q)) return "products";
  if (/项目|projects|项目描述/i.test(q)) return "projects";
  if (/基础|rag|检索|向量|embedding/i.test(q)) return "rag";
  return null;
}
