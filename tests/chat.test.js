
const assert = require('assert');

// Mock Cloudflare Workers Environment
class MockAI {
  constructor() {
    this.run = async (model, params) => { return {}; };
  }
}

class MockVectorIndex {
  constructor() {
    this.query = async (embedding, options) => { return { matches: [] }; };
  }
}

// Helper to load the module
// Since chat.js is an ES module, we'll use dynamic import in the tests
// or we can simulate the context if we were using a bundler.
// For Node.js test, we will import it.

describe('Chat API Tests', () => {
  let chatModule;
  let env;
  let request;
  let context;

  before(async () => {
    // Import the ES module
    chatModule = await import('../functions/api/chat.js');
  });

  beforeEach(() => {
    // Reset Env for each test
    env = {
      AI: new MockAI(),
      VECTOR_INDEX: new MockVectorIndex(),
      VECTORIZE_INDEX: null, // Test fallback binding
      VECTORIZE: null,
      DB: null // Default no DB
    };

    // Default Request
    request = {
      json: async () => ({ message: "hello", history: [] }),
      headers: new Map([["CF-Connecting-IP", "127.0.0.1"]])
    };

    context = { request, env, waitUntil: (p) => {} };
  });

  // Helper to read stream
  async function readStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      result += decoder.decode(value, { stream: true });
    }
    return result;
  }

  // --- Input Validation Tests ---
  
  it('should return 400 if message is missing', async () => {
    context.request.json = async () => ({ history: [] });
    const res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 400);
    const data = await res.json();
    assert.strictEqual(data.error, "message字段是必需的");
    assert.strictEqual(res.headers.get('Content-Type'), 'application/json');
  });

  it('should return 400 if message is too long', async () => {
    const longMsg = 'a'.repeat(1001);
    context.request.json = async () => ({ message: longMsg });
    const res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 400);
    const data = await res.json();
    assert.strictEqual(data.error, "消息过长");
  });

  it('should return 400 if history is not an array', async () => {
    context.request.json = async () => ({ message: "hi", history: "invalid" });
    const res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 400);
    const data = await res.json();
    assert.strictEqual(data.error, "history字段必须为数组");
  });

  // --- Category Inference Tests ---

  it('should infer category correctly', async () => {
    // We can indirectly test this by checking if VECTOR_INDEX.query receives the filter
    // or by exporting inferCategory (but it's not exported).
    // So we'll spy on VECTOR_INDEX.query.
    
    let calls = [];
    env.VECTOR_INDEX.query = async (emb, opts) => {
      // Capture a deep copy of options because chat.js modifies it in place for fallback
      calls.push(JSON.parse(JSON.stringify(opts)));
      return { matches: [] };
    };

    // Mock embedding response
    env.AI.run = async (model, params) => {
      if (model === "@cf/baai/bge-m3") return { data: [{ embedding: [0.1, 0.2] }] };
      return {}; // Stream placeholder
    };

    context.request.json = async () => ({ message: "每日AI汇报" });
    await chatModule.onRequestPost(context);
    
    // First call should have the filter
    assert.ok(calls.length >= 1);
    assert.deepStrictEqual(calls[0].filter, { category: { $eq: "daily_ai" } });
  });

  // --- Embedding Generation Tests ---

  it('should handle various embedding response formats', async () => {
    // 1. OpenAI format { data: [{ embedding: [...] }] }
    env.AI.run = async (model, params) => {
       if (params.stream) return new Response("").body; // Mock stream
       return { data: [{ embedding: [1, 2, 3] }] };
    };
    let res = await chatModule.onRequestPost(context);
    // If embedding works, it proceeds to vector search.
    // If vector search returns empty, it returns JSON "没有找到相关内容" (200 OK)
    assert.strictEqual(res.status, 200);

    // 2. Direct object { embedding: [...] }
    env.AI.run = async (model, params) => {
       if (params.stream) return new Response("").body; 
       return { embedding: [1, 2, 3] };
    };
    res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 200);

    // 3. Direct array [1, 2, 3]
    env.AI.run = async (model, params) => {
       if (params.stream) return new Response("").body; 
       return [1, 2, 3];
    };
    res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 200);
  });

  it('should return 500 if embedding fails', async () => {
    env.AI.run = async () => { throw new Error("AI Error"); };
    const res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 500);
    const data = await res.json();
    assert.strictEqual(data.error, "检索服务繁忙");
  });

  // --- Vector Search & Reranking Tests ---

  it('should perform two-stage retrieval successfully', async () => {
    // 1. Embedding
    env.AI.run = async (model, params) => {
      if (model === "@cf/baai/bge-m3") return { data: [{ embedding: [0.1] }] };
      if (model === "@cf/baai/bge-reranker-base") {
        return { 
          results: [
            { index: 0, score: 0.9 }, // High score
            { index: 1, score: 0.1 }  // Low score (should be filtered)
          ] 
        };
      }
      if (model === "@cf/meta/llama-3-8b-instruct") {
          return new Response("data: {\"response\":\"AI Answer\"}\n\n").body;
      }
      return {};
    };

    // 2. Vector Search
    env.VECTOR_INDEX.query = async () => ({
      matches: [
        { id: '1', metadata: { text: 'doc1', title: 't1', url: 'u1' }, score: 0.8 },
        { id: '2', metadata: { text: 'doc2', title: 't2', url: 'u2' }, score: 0.7 }
      ]
    });

    const res = await chatModule.onRequestPost(context);
    assert.strictEqual(res.status, 200);
    assert.strictEqual(res.headers.get('Content-Type'), 'text/event-stream');
    
    // Verify References Header
    const refs = JSON.parse(res.headers.get('X-RAG-References'));
    assert.strictEqual(refs.length, 1); // Only high score kept
    assert.strictEqual(refs[0].title, 't1');
    
    // Verify Stream Content (requires reading stream)
    // In Node test environment, Response.body might be a stream we can read
    // Note: Mocking env.AI.run to return a stream is tricky without full Workers env.
    // But we are returning what env.AI.run returns.
  });

  it('should fallback to vector results if reranking filters all', async () => {
    env.AI.run = async (model, params) => {
      if (model === "@cf/baai/bge-m3") return { data: [{ embedding: [0.1] }] };
      if (model === "@cf/baai/bge-reranker-base") {
        return { 
          results: [
            { index: 0, score: 0.1 } // All below 0.25 threshold
          ] 
        };
      }
      if (model === "@cf/meta/llama-3-8b-instruct") return new Response("data: {\"response\":\"Fallback Answer\"}\n\n").body;
      return {};
    };

    env.VECTOR_INDEX.query = async () => ({
      matches: [{ id: '1', metadata: { text: 'doc1', title: 't1', url: 'u1' }, score: 0.8 }]
    });

    const res = await chatModule.onRequestPost(context);
    
    // Should still have references (fallback used)
    const refs = JSON.parse(res.headers.get('X-RAG-References'));
    assert.strictEqual(refs.length, 1);
  });

  it('should handle reranker crash gracefully (fallback)', async () => {
    env.AI.run = async (model, params) => {
      if (model === "@cf/baai/bge-m3") return { data: [{ embedding: [0.1] }] };
      if (model === "@cf/baai/bge-reranker-base") throw new Error("Rerank Crash");
      if (model === "@cf/meta/llama-3-8b-instruct") return new Response("data: {\"response\":\"Crash Fallback\"}\n\n").body;
      return {};
    };

    env.VECTOR_INDEX.query = async () => ({
      matches: [{ id: '1', metadata: { text: 'doc1', title: 't1', url: 'u1' }, score: 0.8 }]
    });

    const res = await chatModule.onRequestPost(context);
    const refs = JSON.parse(res.headers.get('X-RAG-References'));
    assert.strictEqual(refs.length, 1);
  });

  // --- Fallback & Safety Tests ---

  it('should filter candidates with missing text in fallback', async () => {
    // Reranker fails, trigger fallback
    env.AI.run = async (model, params) => {
      if (model === "@cf/baai/bge-reranker-base") throw new Error("Fail");
      if (model === "@cf/baai/bge-m3") return [1];
      if (model === "@cf/meta/llama-3-8b-instruct") return new Response("ok").body;
    };

    env.VECTOR_INDEX.query = async () => ({
      matches: [
        { id: '1', metadata: { text: 'valid', title: 't1', url: 'u1' }, score: 0.9 },
        { id: '2', metadata: { }, score: 0.8 } // Missing text
      ]
    });

    const res = await chatModule.onRequestPost(context);
    const refs = JSON.parse(res.headers.get('X-RAG-References'));
    
    // Only 1 valid reference
    assert.strictEqual(refs.length, 1); 
  });

  // --- LLM & Error Handling ---

  it('should return 502 if LLM fails', async () => {
     env.AI.run = async (model) => {
       if (model === "@cf/baai/bge-m3") return [1];
       // Bypass retrieval by returning empty matches initially? 
       // No, we need matches to reach LLM.
       if (model === "@cf/meta/llama-3-8b-instruct") throw new Error("LLM Down");
       return {}; // Reranker default
     };

     env.VECTOR_INDEX.query = async () => ({
       matches: [{ id: '1', metadata: { text: 'doc' }, score: 0.9 }]
     });

     const res = await chatModule.onRequestPost(context);
     assert.strictEqual(res.status, 502);
     const data = await res.json();
     assert.strictEqual(data.error, "LLM服务暂时不可用");
  });
});
