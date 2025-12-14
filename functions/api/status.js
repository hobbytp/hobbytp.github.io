export async function onRequestGet(context) {
  const { env } = context;
  const status = {
    status: "ok",
    db_status: "unknown",
    ai_status: "unknown",
    timestamp: new Date().toISOString(),
    details: {}
  };

  // Check D1 Database
  if (env.DB) {
    try {
      const start = Date.now();
      await env.DB.prepare("SELECT 1").first();
      status.db_status = "connected";
      status.details.db_latency_ms = Date.now() - start;
    } catch (err) {
      status.db_status = "error";
      status.status = "degraded";
      status.details.db_error = err.message;
    }
  } else {
    status.db_status = "missing_binding";
    status.status = "degraded";
  }

  // Check AI Binding
  if (env.AI) {
    status.ai_status = "connected";
  } else {
    status.ai_status = "missing_binding";
    status.status = "degraded";
  }

  return new Response(JSON.stringify(status, null, 2), {
    headers: {
      "content-type": "application/json;charset=UTF-8",
      "access-control-allow-origin": "*",
    },
  });
}
