/**
 * 博客数字分身助手 - 后端API
 * 处理前端聊天请求，支持RAG检索和多轮对话
 */

// Cloudflare Workers AI 模型ID常量
const EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5";
const LLM_MODEL = "@cf/meta/llama-3-8b-instruct";

// 配置常量
const MAX_MESSAGE_LENGTH = 1000;  // 最大消息长度
const MAX_HISTORY_TURNS = 3;      // 最大历史对话轮数
const TOP_K = 3;                  // 向量检索返回的topK结果
const BLOG_AUTHOR_NAME = "Peng Tan";  // 博主名称（可根据实际情况修改）

/**
 * 组装System Prompt
 */
function buildSystemPrompt(retrievedContexts) {
  const contextText = retrievedContexts
    .map((ctx, idx) => `${idx + 1}. ${ctx.text}`)
    .join("\n\n");
  
  return `You are the digital twin of ${BLOG_AUTHOR_NAME}. You answer questions based strictly on the provided Context.

Context:
${contextText}

Instructions:
1. Use a professional, friendly, slightly geeky tone.
2. If the answer is not in the Context, you MUST reply exactly with: "没有找到相关内容".
3. Answer in Chinese (Simplified) by default, unless the user asks in another language.
4. Keep answers concise and helpful.`;
}

/**
 * 截断对话历史，保留最近N轮
 */
function truncateHistory(history, maxTurns = MAX_HISTORY_TURNS) {
  if (!history || history.length === 0) {
    return [];
  }
  
  // 保留最近的maxTurns轮对话（每轮包含user和assistant两条消息）
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
    
    // 4. 向量检索
    let retrievedContexts = [];
    try {
      const vectorQuery = await env.VECTOR_INDEX.query(queryEmbedding, {
        topK: TOP_K
      });
      
      if (vectorQuery.matches && vectorQuery.matches.length > 0) {
        retrievedContexts = vectorQuery.matches.map(match => ({
          text: match.metadata?.text || match.text || "",
          url: match.metadata?.url || "",
          title: match.metadata?.title || "",
          score: match.score || 0
        })).filter(ctx => ctx.text);  // 过滤掉空文本
      }
    } catch (error) {
      console.error("向量检索失败:", error);
      // 检索失败不阻断流程，继续使用空context
    }
    
    // 5. 组装Prompt
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


