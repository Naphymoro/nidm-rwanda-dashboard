// The research assistant's model, on Workers AI. The engine (backend/app/agent.py, provider "openai-compatible") calls
// /__ai/v1/chat/completions on this Worker with NDIM_AI_TOKEN; the Worker answers through the AI binding, which speaks
// the same chat-completions format (streaming and tool calls included), so no outside API key or company is involved.
//
// Costs stay inside the free allowance: the Worker picks the model (the engine cannot ask for a dearer one), caps the
// reply length, stops for the day once NDIM_AI_DAILY_NEURONS are used (Workers AI gives 10,000 a day free), and limits
// each visitor's assistant messages per day (visitorAllowed, checked on /agent/chat before the engine sees it).

export interface AiEnv {
  AI: Ai;
  DB: D1Database;
  NDIM_AI_TOKEN?: string;
  NDIM_AI_MODEL?: string;
  NDIM_AI_DAILY_NEURONS?: string;
  NDIM_AI_VISITOR_MESSAGES?: string;
}

const DAILY_NEURONS = 9000; // under the free 10,000, leaving room for replies already streaming when the cap is reached
const VISITOR_MESSAGES = 40;
const MAX_TOKENS = 1500;
const RESETS = "It resets at 00:00 UTC (2 a.m. in Kigali). Journeys and every NDIM tool still work with the buttons.";

const today = () => new Date().toISOString().slice(0, 10);

// The engine shows error.message to the researcher (agent.py _raise_for).
const refusal = (message: string, status: number) =>
  new Response(JSON.stringify({ error: { message } }), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

async function sha256(text: string) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function record(env: AiEnv, neurons: number) {
  return env.DB.prepare(
    "INSERT INTO ai_usage (day, requests, neurons) VALUES (?, 1, ?) " +
    "ON CONFLICT(day) DO UPDATE SET requests = requests + 1, neurons = neurons + excluded.neurons",
  ).bind(today(), neurons).run();
}

/** Counts the visitor's assistant message; false once they have used today's share. */
export async function visitorAllowed(request: Request, env: AiEnv) {
  const day = today();
  const visitor = (await sha256(`${request.headers.get("CF-Connecting-IP") || "unknown"}|${day}`)).slice(0, 32);
  try {
    const row = await env.DB.prepare(
      "INSERT INTO ai_visitors (day, visitor, messages) VALUES (?, ?, 1) " +
      "ON CONFLICT(day, visitor) DO UPDATE SET messages = messages + 1 RETURNING messages",
    ).bind(day, visitor).first<{ messages: number }>();
    return (row?.messages ?? 1) <= Number(env.NDIM_AI_VISITOR_MESSAGES || VISITOR_MESSAGES);
  } catch (error) {
    console.error("visitor count failed; letting the message through (the daily cap still holds)", error);
    return true;
  }
}

export function visitorRefusal() {
  // /agent/chat errors are read as {detail}, like the engine's own.
  return new Response(JSON.stringify({ detail: `You have used today's assistant messages on this demo. ${RESETS}` }),
    { status: 429, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
}

export async function aiProxy(request: Request, env: AiEnv, ctx: ExecutionContext): Promise<Response> {
  const token = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.NDIM_AI_TOKEN || !env.NDIM_AI_MODEL || token !== env.NDIM_AI_TOKEN) return new Response("Not Found", { status: 404 });
  if (request.method !== "POST" || new URL(request.url).pathname !== "/__ai/v1/chat/completions") return new Response("Not Found", { status: 404 });

  let used: { neurons: number } | null;
  try {
    used = await env.DB.prepare("SELECT neurons FROM ai_usage WHERE day = ?").bind(today()).first<{ neurons: number }>();
  } catch (error) {
    console.error("reading today's AI usage failed; refusing (the cap must hold)", error);
    return refusal("The research assistant is unavailable right now. Try again in a minute.", 503);
  }
  if ((used?.neurons ?? 0) >= Number(env.NDIM_AI_DAILY_NEURONS || DAILY_NEURONS)) {
    return refusal(`The research assistant has used today's free allowance. ${RESETS}`, 429);
  }
  let body: any;
  try {
    body = await request.json();
  } catch {
    return refusal("The request body is not JSON.", 400);
  }
  const inputs = {
    messages: body.messages,
    ...(body.tools ? { tools: body.tools } : {}),
    temperature: typeof body.temperature === "number" ? body.temperature : 0.3,
    max_tokens: Math.min(Number(body.max_tokens) || MAX_TOKENS, MAX_TOKENS),
    stream: body.stream === true,
  };
  let out: any;
  try {
    out = await env.AI.run(env.NDIM_AI_MODEL as any, inputs as any);
  } catch (error) {
    console.error("Workers AI failed", error);
    return refusal("The research assistant's model is not answering right now. Try again in a minute.", 502);
  }
  if (!(out instanceof ReadableStream)) {
    ctx.waitUntil(record(env, Number(out?.usage?.neurons) || 0));
    return Response.json(out);
  }
  // Each streamed chunk carries the running usage; the last Neurons figure is the reply's total.
  let neurons = 0;
  let tail = "";
  const decoder = new TextDecoder();
  const counted = new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      const text = tail + decoder.decode(chunk, { stream: true });
      for (const match of text.matchAll(/"neurons":\s*([\d.]+)/g)) neurons = Math.max(neurons, Number(match[1]));
      tail = text.slice(-64); // a figure split across chunks is read on the next one
      controller.enqueue(chunk);
    },
    flush() {
      ctx.waitUntil(record(env, neurons));
    },
  });
  return new Response(out.pipeThrough(counted), { headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-store" } });
}
