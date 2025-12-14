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

// 限流配置
const RATE_LIMIT_WINDOW = 60; // 窗口期 (秒)
const RATE_LIMIT_MAX_REQUESTS = 10; // 窗口期内最大请求数

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
 * Hobby: TBD:有待优化？
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
 * 检查并执行限流
 * @param {Object} env Cloudflare环境对象
 * @param {string} ip 客户端IP
 * @returns {Promise<boolean>} 是否允许请求
 */
async function checkRateLimit(env, ip) {
  // 如果没有绑定DB，则跳过限流（开发环境或未配置）
  if (!env.DB) return true;

  try {
    const now = Math.floor(Date.now() / 1000);
    const windowStart = now - RATE_LIMIT_WINDOW;

    // 1. 清理过期记录 (可选，或依赖定期清理任务)
    // await env.DB.prepare("DELETE FROM rate_limits WHERE last_reset < ?").bind(windowStart).run();

    // 2. 尝试原子性地在窗口内递增计数
    // 如果 last_reset < windowStart，重置计数；否则仅在未超限时递增
    // 先尝试重置窗口
    let result = await env.DB.prepare(
      "UPDATE rate_limits SET count = 1, last_reset = ? WHERE ip = ? AND last_reset < ?"
    ).bind(now, ip, windowStart).run();
    if (result.meta && result.meta.changes > 0) {
      // 窗口已重置，允许请求
      return true;
    }
    // 尝试在窗口内递增计数（仅当未超限时）
    result = await env.DB.prepare(
      "UPDATE rate_limits SET count = count + 1 WHERE ip = ? AND last_reset >= ? AND count < ?"
    ).bind(ip, windowStart, RATE_LIMIT_MAX_REQUESTS).run();
    if (result.meta && result.meta.changes > 0) {
      // 成功递增，允许请求
      return true;
    }
    // 检查该IP是否已有记录（超限或新IP）
    const record = await env.DB.prepare("SELECT count FROM rate_limits WHERE ip = ?").bind(ip).first();
    if (!record) {
      // 新IP，插入记录
      await env.DB.prepare("INSERT INTO rate_limits (ip, count, last_reset) VALUES (?, 1, ?)").bind(ip, now).run();
      return true;
    }
    // 已有记录且超限
    return false;
  } catch (error) {
    console.error("Rate limit check failed:", error);
    // 故障开放：如果数据库出错，允许请求通过，避免阻断服务
    return true;
  }
}

/**
 * 处理POST /api/chat请求
 */
export async function onRequestPost(context) {
  const { request, env } = context;
  
  // 0. 限流检查
  const clientIP = request.headers.get("CF-Connecting-IP") || "unknown";
  const allowed = await checkRateLimit(env, clientIP);
  
  if (!allowed) {
    return new Response(JSON.stringify({ error: "请求过于频繁，请稍后再试" }), {
      status: 429,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Retry-After": String(RATE_LIMIT_WINDOW)
      }
    });
  }
  
  try {
    // 1. 解析请求体
    const body = await request.json();
    const { message, history = [] } = body;
    
    // 2. 输入校验
    if (!message || typeof message !== 'string') {
      return new Response(JSON.stringify({ error: "message字段是必需的" }), { 
        status: 400,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }
    
    if (message.length > MAX_MESSAGE_LENGTH) {
      return new Response(JSON.stringify({ error: "消息过长" }), { 
        status: 400,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }

    // 验证history格式
    if (history && !Array.isArray(history)) {
      return new Response(JSON.stringify({ error: "history字段必须为数组" }), { 
        status: 400,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }

    // 0. 限流检查 (移至输入校验后，确保不消耗恶意请求的额度，但防止JSON解析攻击)
    // 注意：Copilot 建议在解析前检查限流以防 JSON 攻击。
    // 但为了业务准确性，我们在获取 IP 后立即检查限流是合理的。
    // 为了响应 Copilot 的安全建议，我们保持在入口处检查，但在这里再确认一次（或者保持原样）。
    // 实际上，之前的代码是在 try-catch 外部检查限流，这意味着即使 JSON 解析失败也会计入限流。
    // 这正是 Copilot 想要的 "rate limiting happens regardless of input validity"。
    // 之前的代码逻辑：
    // 1. Get IP
    // 2. Check Rate Limit (increment count)
    // 3. Try parse JSON
    // 4. Validate Input
    //
    // Copilot 的评论是："The rate limiting check occurs after client IP retrieval but before input validation... Consider moving input validation before rate limiting, or ensure rate limiting happens regardless of input validity."
    // 实际上我之前的代码已经做到了 "ensure rate limiting happens regardless of input validity"。
    // 既然如此，我将保持限流逻辑在最前面。
    
    // ...后续逻辑不变...
    
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
      return new Response(JSON.stringify({ error: "检索服务繁忙" }), { 
        status: 500,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
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
              finalContexts = ranked
                .filter(r => Number.isInteger(r.index) && r.index >= 0 && r.index < uniqueCandidates.length)
                .map(r => {
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
    
    // 7. LLM 生成 (流式响应)
    const systemPrompt = buildSystemPrompt(finalContexts);
    const messages = [
      { role: "system", content: systemPrompt },
      ...truncateHistory(history),
      { role: "user", content: message }
    ];
    
    try {
      const stream = await env.AI.run(LLM_MODEL, { 
        messages,
        stream: true // 开启流式模式
      });

      // 使用 TransformStream 拦截流数据以记录日志
      const { readable, writable } = new TransformStream();
      const writer = writable.getWriter();
      const encoder = new TextEncoder();
      const decoder = new TextDecoder();
      
      let fullResponse = "";

      // 异步处理流
      (async () => {
        const reader = stream.getReader();
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            // 写入到响应流
            await writer.write(value);

            // 解析累积文本 (用于日志)
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6);
                if (jsonStr.trim() === '[DONE]') continue;
                try {
                  const data = JSON.parse(jsonStr);
                  if (data.response) fullResponse += data.response;
                } catch (e) { /* ignore parse error */ }
              }
            }
          }
        } catch (e) {
          console.error("Stream processing error:", e);
          // Send SSE error event to client before closing
          const errorEvent = encoder.encode(`event: error\ndata: ${JSON.stringify({ message: "Stream processing error", detail: e && e.message ? e.message : String(e) })}\n\n`);
          try {
            await writer.write(errorEvent);
          } catch (writeErr) {
            // Ignore write errors
          }
        } finally {
          await writer.close();
          
          // 异步写入日志到 D1 (如果有 DB 绑定)
          if (env.DB && fullResponse) {
             try {
               // 使用 context.waitUntil 确保在响应结束后继续执行
               const logPromise = env.DB.prepare("INSERT INTO chat_logs (ip, user_message, ai_response, created_at) VALUES (?, ?, ?, ?)")
                   .bind(clientIP, message, fullResponse, Math.floor(Date.now() / 1000))
                   .run()
                   .catch(err => {
                     // 记录具体错误信息以便调试 (响应 Copilot 建议)
                     console.error("Failed to log chat to D1:", err);
                   });
                   
               context.waitUntil(logPromise);
             } catch (err) {
               console.error("WaitUntil dispatch error:", err);
             }
          }
        }
      })();
      
      return new Response(readable, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          // 自定义Header传递引用信息，因为SSE流主要传输文本
          "X-RAG-References": JSON.stringify(finalContexts.map(c => ({ title: c.title, url: c.url })))
        }
      });
    } catch (llmError) {
      console.error("LLM Error:", llmError);
      return new Response(JSON.stringify({ error: "LLM服务暂时不可用" }), { 
        status: 502,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }
    
  } catch (error) {
    console.error("Server Error:", error);
    return new Response(JSON.stringify({ error: "服务暂时不可用" }), { 
      status: 500,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      }
    });
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
