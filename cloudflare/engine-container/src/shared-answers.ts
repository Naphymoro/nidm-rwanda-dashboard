// Shared answers: researcher-approved answers that NDIM desktop engines exchange when their researcher turns online sync
// on (backend/app/answer_sync.py). Only the answer text is stored, with a random id and whether it was approved or
// corrected; never a question, evidence, workspace data or a name.
//
// Writing and reading need an access key from the NDIM_SYNC_TOKENS secret (comma-separated, one per research team, so
// one can be revoked alone). The public demo engine never gets a key and refuses to sync, so demo visitors cannot
// write. X-NDIM-Install is a random secret per computer: only the computer that sent an answer can withdraw it.

export interface SyncEnv {
  DB: D1Database;
  NDIM_SYNC_TOKENS?: string;
}

const MAX_BODY = 256_000;
const MAX_BATCH = 50;
const MAX_ANSWER = 4000;
const WRITES_PER_HOUR = 300; // per access key
const MAX_PER_COMPUTER = 5000;
const PAGE = 500;
const ID = /^[0-9a-f]{32}$/;
// A second, simpler privacy check: the engine checks first, and anything with an email or a long number is refused here too.
const EMAIL = /[\w.+-]+\s*(?:@|\(at\)|\[at\])\s*[\w-]+(?:\s*(?:\.|\(dot\))\s*[\w-]+)+/i;
const NUMBER = /\+?\d(?:[\s\-()/]{0,2}\d){6,}/;
const DATES = /\b(?:19|20)\d\d(?:\s*[-/]\s*\d\d?){2}\b|\b(?:19|20)\d\d\s*[-/]\s*(?:19|20)\d\d\b/g;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

async function sha256(text: string) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** The caller's key and computer, as hashes (the store never keeps either secret), or a refusal. */
async function caller(request: Request, env: SyncEnv) {
  const keys = (env.NDIM_SYNC_TOKENS || "").split(",").map((key) => key.trim()).filter((key) => key.length >= 16);
  if (!keys.length) return json({ error: "Answer sharing is not set up on this service." }, 503);
  const token = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  const install = request.headers.get("X-NDIM-Install") || "";
  // Compare hashes, so the time taken does not reveal how much of a key was right.
  const hashed = await sha256(token);
  const known = await Promise.all(keys.map(sha256));
  if (!token || !known.includes(hashed)) return json({ error: "A valid access key is needed." }, 401);
  if (install.length < 16 || install.length > 128) return json({ error: "X-NDIM-Install is missing." }, 400);
  return { key: hashed.slice(0, 16), owner: await sha256(install) };
}

function problem(item: any): string | null {
  if (!item || typeof item !== "object") return "not an object";
  if (typeof item.id !== "string" || !ID.test(item.id)) return "bad id";
  if (item.kind !== "answer" && item.kind !== "correction") return "kind must be answer or correction";
  if (typeof item.answer !== "string" || item.answer.trim().length < 2 || item.answer.length > MAX_ANSWER) return "answer is empty or too long";
  const plain = item.answer.normalize("NFKD");
  if (EMAIL.test(plain) || NUMBER.test(plain.replace(DATES, " "))) return "answer contains an email address or a long number";
  const extra = Object.keys(item).filter((key) => !["id", "kind", "answer"].includes(key));
  if (extra.length) return `only id, kind and answer are accepted (got ${extra.join(", ")})`;
  return null;
}

async function writesLastHour(env: SyncEnv, key: string) {
  const since = new Date(Date.now() - 3_600_000).toISOString();
  const row = await env.DB.prepare("SELECT COUNT(*) AS n FROM shared_answers WHERE key = ? AND updated_at > ?").bind(key, since).first<{ n: number }>();
  return row?.n ?? 0;
}

export async function sharedAnswers(request: Request, env: SyncEnv): Promise<Response> {
  const url = new URL(request.url);
  const who = await caller(request, env);
  if (who instanceof Response) return who;

  if (request.method === "GET" && url.pathname === "/shared-answers") {
    // Cursor "updated_at|id": answers and withdrawals since the last pull, oldest first, without the caller's own.
    const [at, id] = (url.searchParams.get("since") || "|").split("|");
    const { results } = await env.DB.prepare(
      `SELECT id, kind, answer, updated_at, deleted FROM shared_answers
       WHERE owner != ? AND (updated_at > ? OR (updated_at = ? AND id > ?)) ORDER BY updated_at, id LIMIT ?`,
    ).bind(who.owner, at || "", at || "", id || "", PAGE + 1).all<{ id: string; kind: string; answer: string; updated_at: string; deleted: number }>();
    const page = results.slice(0, PAGE);
    const last = page[page.length - 1];
    return json({
      answers: page.map((row) => row.deleted ? { id: row.id, deleted: true, updated_at: row.updated_at }
        : { id: row.id, kind: row.kind, answer: row.answer, updated_at: row.updated_at }),
      cursor: last ? `${last.updated_at}|${last.id}` : url.searchParams.get("since") || "",
      more: results.length > PAGE,
    });
  }

  if (request.method === "POST" && url.pathname === "/shared-answers") {
    const text = await request.text();
    if (text.length > MAX_BODY) return json({ error: `The request is larger than ${MAX_BODY} bytes.` }, 413);
    let body: any;
    try { body = JSON.parse(text); } catch { return json({ error: "The body must be JSON." }, 400); }
    const items = body?.answers;
    if (!Array.isArray(items) || !items.length || items.length > MAX_BATCH) return json({ error: `Send 1 to ${MAX_BATCH} answers.` }, 400);
    const refused = items.map((item, index) => ({ index, reason: problem(item) })).filter((row) => row.reason);
    if (refused.length) return json({ error: "Some answers were refused; nothing was saved.", refused }, 422);
    if (await writesLastHour(env, who.key) + items.length > WRITES_PER_HOUR) return json({ error: "Too many answers this hour; try later." }, 429);
    const live = await env.DB.prepare("SELECT COUNT(*) AS n FROM shared_answers WHERE owner = ? AND deleted = 0").bind(who.owner).first<{ n: number }>();
    if ((live?.n ?? 0) + items.length > MAX_PER_COMPUTER) return json({ error: "This computer has shared the most answers allowed." }, 429);
    const now = new Date().toISOString();
    // An id already used by another computer is left alone (WHERE owner = excluded.owner), never overwritten.
    await env.DB.batch(items.map((item: any) => env.DB.prepare(
      `INSERT INTO shared_answers (id, owner, key, kind, answer, created_at, updated_at, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
       ON CONFLICT(id) DO UPDATE SET kind = excluded.kind, answer = excluded.answer, updated_at = excluded.updated_at, deleted = 0
       WHERE shared_answers.owner = excluded.owner`,
    ).bind(item.id, who.owner, who.key, item.kind, item.answer, now, now)));
    return json({ saved: items.length });
  }

  const match = url.pathname.match(/^\/shared-answers\/([0-9a-f]{32})$/);
  if (request.method === "DELETE" && match) {
    // Withdrawn: the text is erased and a marker stays, so other computers remove their copy at their next pull.
    const result = await env.DB.prepare(
      "UPDATE shared_answers SET answer = '', deleted = 1, updated_at = ? WHERE id = ? AND owner = ? AND deleted = 0",
    ).bind(new Date().toISOString(), match[1], who.owner).run();
    return result.meta.changes ? new Response(null, { status: 204 }) : json({ error: "No answer of yours with that id." }, 404);
  }
  return json({ error: "Not found" }, 404);
}
