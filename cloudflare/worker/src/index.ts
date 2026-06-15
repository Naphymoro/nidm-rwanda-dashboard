export interface Env {
  DB: D1Database;
  FILES: R2Bucket;
  NDIM_ENV?: string;
  MAX_UPLOAD_MB?: string;
}

type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

interface NarrativePayload {
  workspace_id?: string;
  route?: string;
  title?: string;
  body?: string;
  country?: string;
  admin1?: string;
  admin2?: string;
  admin3?: string;
  language?: string;
  source_type?: string;
  source_name?: string;
  period?: string;
  consent_level?: string;
  visibility?: string;
  metadata?: Record<string, JsonValue>;
}

interface WorkspacePayload {
  id?: string;
  name?: string;
  country?: string;
  domain?: string;
  description?: string;
}

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store"
};

const CORS_HEADERS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,PUT,OPTIONS",
  "access-control-allow-headers": "content-type, authorization",
  "access-control-max-age": "86400"
};

function nowIso(): string {
  return new Date().toISOString();
}

function id(prefix: string): string {
  return `${prefix}_${crypto.randomUUID()}`;
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { ...JSON_HEADERS, ...CORS_HEADERS }
  });
}

function bad(message: string, status = 400): Response {
  return json({ ok: false, error: message }, status);
}

async function parseJson<T>(request: Request): Promise<T> {
  try {
    return (await request.json()) as T;
  } catch {
    throw new Error("Expected a valid JSON body.");
  }
}

async function sha256Hex(input: string | ArrayBuffer): Promise<string> {
  const data = typeof input === "string" ? new TextEncoder().encode(input) : input;
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function normalizeStatus(status: string | null): string | null {
  if (!status || status === "all") return null;
  const allowed = new Set(["pending", "reviewed_approved", "reviewed_rejected", "accepted", "rejected"]);
  return allowed.has(status) ? status : null;
}

async function audit(env: Env, entityType: string, entityId: string, action: string, actor?: string, details?: unknown): Promise<void> {
  await env.DB.prepare(
    "INSERT INTO audit_events (id, entity_type, entity_id, action, actor, details_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
  )
    .bind(id("evt"), entityType, entityId, action, actor || null, JSON.stringify(details || {}), nowIso())
    .run();
}

async function ensureWorkspace(env: Env, payload: WorkspacePayload): Promise<string> {
  const workspaceId = payload.id || "default";
  const existing = await env.DB.prepare("SELECT id FROM workspaces WHERE id = ?").bind(workspaceId).first();
  if (!existing) {
    const ts = nowIso();
    await env.DB.prepare(
      "INSERT INTO workspaces (id, name, country, domain, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
      .bind(
        workspaceId,
        payload.name || "NDIM Default Workspace",
        payload.country || null,
        payload.domain || "narrative diffusion and inoculation",
        payload.description || "Default Cloudflare alpha workspace.",
        ts,
        ts
      )
      .run();
  }
  return workspaceId;
}

async function handleHealth(env: Env): Promise<Response> {
  const dbOk = await env.DB.prepare("SELECT 1 AS ok").first<{ ok: number }>();
  return json({
    ok: true,
    service: "NDIM Cloudflare Worker API",
    environment: env.NDIM_ENV || "alpha",
    database: dbOk?.ok === 1 ? "connected" : "unknown",
    storage: "R2 binding expected",
    heavy_modelling: "not_in_worker",
    note: "This backend supports the lightweight web workflow. Heavy Python modelling remains local, Cloud Run, or Colab."
  });
}

async function listWorkspaces(env: Env): Promise<Response> {
  await ensureWorkspace(env, { id: "default" });
  const rows = await env.DB.prepare("SELECT * FROM workspaces ORDER BY updated_at DESC").all();
  return json({ ok: true, workspaces: rows.results || [] });
}

async function createWorkspace(request: Request, env: Env): Promise<Response> {
  const payload = await parseJson<WorkspacePayload>(request);
  if (!payload.name || payload.name.trim().length < 2) return bad("Workspace name is required.");
  const workspaceId = payload.id || id("ws");
  const ts = nowIso();
  await env.DB.prepare(
    "INSERT INTO workspaces (id, name, country, domain, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
  )
    .bind(
      workspaceId,
      payload.name.trim(),
      payload.country || null,
      payload.domain || null,
      payload.description || null,
      ts,
      ts
    )
    .run();
  await audit(env, "workspace", workspaceId, "created", undefined, payload);
  return json({ ok: true, workspace_id: workspaceId });
}

async function createNarrative(request: Request, env: Env): Promise<Response> {
  const payload = await parseJson<NarrativePayload>(request);
  if (!payload.body || payload.body.trim().length < 20) return bad("Narrative body must contain at least 20 characters.");
  const workspaceId = await ensureWorkspace(env, { id: payload.workspace_id || "default" });
  const narrativeId = id("nar");
  const ts = nowIso();
  const route = payload.route || "open_story";
  const evidenceHash = await sha256Hex(
    JSON.stringify({
      body: payload.body,
      route,
      country: payload.country || "",
      source: payload.source_name || "",
      period: payload.period || ""
    })
  );

  await env.DB.prepare(
    `INSERT INTO narratives (
      id, workspace_id, route, title, body, country, admin1, admin2, admin3,
      language, source_type, source_name, period, consent_level, visibility,
      status, evidence_hash, metadata_json, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      narrativeId,
      workspaceId,
      route,
      payload.title || null,
      payload.body.trim(),
      payload.country || null,
      payload.admin1 || null,
      payload.admin2 || null,
      payload.admin3 || null,
      payload.language || null,
      payload.source_type || null,
      payload.source_name || null,
      payload.period || null,
      payload.consent_level || null,
      payload.visibility || "restricted",
      "pending",
      evidenceHash,
      JSON.stringify(payload.metadata || {}),
      ts,
      ts
    )
    .run();

  await audit(env, "narrative", narrativeId, "created", undefined, { route, evidence_hash: evidenceHash });
  return json({ ok: true, narrative_id: narrativeId, evidence_hash: evidenceHash, status: "pending" }, 201);
}

async function listNarratives(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const workspaceId = url.searchParams.get("workspace_id") || "default";
  const status = normalizeStatus(url.searchParams.get("status"));
  const route = url.searchParams.get("route");
  const q = url.searchParams.get("q");

  const where: string[] = ["workspace_id = ?"];
  const binds: (string | number | null)[] = [workspaceId];
  if (status) {
    where.push("status = ?");
    binds.push(status);
  }
  if (route) {
    where.push("route = ?");
    binds.push(route);
  }
  if (q) {
    where.push("(body LIKE ? OR title LIKE ? OR admin1 LIKE ? OR admin2 LIKE ? OR source_name LIKE ?)");
    const like = `%${q}%`;
    binds.push(like, like, like, like, like);
  }

  const sql = `SELECT id, workspace_id, route, title, country, admin1, admin2, admin3, language,
    source_type, source_name, period, consent_level, visibility, status, evidence_hash,
    reviewer, review_decision, review_note, reviewed_at, committed_at, uncommitted_at,
    created_at, updated_at
    FROM narratives WHERE ${where.join(" AND ")} ORDER BY created_at DESC LIMIT 200`;
  const rows = await env.DB.prepare(sql).bind(...binds).all();
  return json({ ok: true, narratives: rows.results || [] });
}

async function getNarrative(env: Env, narrativeId: string): Promise<Response> {
  const record = await env.DB.prepare("SELECT * FROM narratives WHERE id = ?").bind(narrativeId).first();
  if (!record) return bad("Narrative not found.", 404);
  const encodings = await env.DB.prepare("SELECT * FROM encodings WHERE narrative_id = ? ORDER BY created_at DESC").bind(narrativeId).all();
  return json({ ok: true, narrative: record, encodings: encodings.results || [] });
}

async function reviewNarrative(request: Request, env: Env, narrativeId: string): Promise<Response> {
  const payload = await parseJson<{ decision?: string; reviewer?: string; note?: string }>(request);
  const decision = payload.decision === "rejected" ? "rejected" : payload.decision === "approved" ? "approved" : null;
  if (!decision) return bad("Decision must be approved or rejected.");
  const status = decision === "approved" ? "reviewed_approved" : "reviewed_rejected";
  const ts = nowIso();
  const result = await env.DB.prepare(
    "UPDATE narratives SET status = ?, review_decision = ?, reviewer = ?, review_note = ?, reviewed_at = ?, updated_at = ? WHERE id = ?"
  )
    .bind(status, decision, payload.reviewer || "anonymous reviewer", payload.note || null, ts, ts, narrativeId)
    .run();
  if (result.meta.changes === 0) return bad("Narrative not found.", 404);
  await audit(env, "narrative", narrativeId, `review_${decision}`, payload.reviewer, { note: payload.note || "" });
  return json({ ok: true, narrative_id: narrativeId, status });
}

async function commitReviewed(request: Request, env: Env): Promise<Response> {
  const payload = await parseJson<{ workspace_id?: string; actor?: string }>(request);
  const workspaceId = payload.workspace_id || "default";
  const ts = nowIso();
  const approved = await env.DB.prepare(
    "UPDATE narratives SET status = 'accepted', committed_at = ?, updated_at = ? WHERE workspace_id = ? AND status = 'reviewed_approved'"
  )
    .bind(ts, ts, workspaceId)
    .run();
  const rejected = await env.DB.prepare(
    "UPDATE narratives SET status = 'rejected', committed_at = ?, updated_at = ? WHERE workspace_id = ? AND status = 'reviewed_rejected'"
  )
    .bind(ts, ts, workspaceId)
    .run();
  await audit(env, "workspace", workspaceId, "commit_reviewed_records", payload.actor, {
    accepted: approved.meta.changes,
    rejected: rejected.meta.changes
  });
  return json({ ok: true, accepted: approved.meta.changes, rejected: rejected.meta.changes });
}

async function uncommitNarrative(request: Request, env: Env, narrativeId: string): Promise<Response> {
  const payload = await parseJson<{ actor?: string; note?: string }>(request);
  const ts = nowIso();
  const result = await env.DB.prepare(
    "UPDATE narratives SET status = 'pending', review_decision = NULL, committed_at = NULL, uncommitted_at = ?, updated_at = ? WHERE id = ? AND status IN ('accepted', 'rejected')"
  )
    .bind(ts, ts, narrativeId)
    .run();
  if (result.meta.changes === 0) return bad("Narrative not found, or it is not committed.", 404);
  await audit(env, "narrative", narrativeId, "uncommitted", payload.actor, { note: payload.note || "" });
  return json({ ok: true, narrative_id: narrativeId, status: "pending" });
}

function countMatches(text: string, words: string[]): number {
  return words.reduce((count, word) => count + (text.includes(word) ? 1 : 0), 0);
}

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function heuristicEncode(body: string) {
  const text = body.toLowerCase();
  const barrier = countMatches(text, ["expensive", "cost", "money", "cannot afford", "price", "loan", "repair", "broken", "fuel", "charcoal", "firewood", "smoke"]);
  const trust = countMatches(text, ["trusted", "leader", "health worker", "cooperative", "neighbor", "neighbour", "demonstration", "training", "savings group", "teacher"]);
  const misinformation = countMatches(text, ["danger", "explode", "rumor", "rumour", "fear", "unsafe", "poison", "government trick", "fake", "heard that"]);
  const social = countMatches(text, ["people say", "women", "neighbors", "church", "market", "group", "family", "husband", "mother", "friends"]);
  const positive = countMatches(text, ["save time", "saved time", "quick", "clean", "less smoke", "school", "business", "convenient", "adopt", "like"]);
  const negative = countMatches(text, ["refuse", "stopped", "difficult", "afraid", "against", "doubt", "problem", "not use"]);
  const emotional = countMatches(text, ["afraid", "angry", "happy", "proud", "ashamed", "worried", "relieved", "fear", "hope"]);
  const grounded = countMatches(text, ["district", "sector", "village", "cell", "rwanda", "kigali", "musanze", "nyamagabe", "nyaruguru", "rubavu", "gasabo"]);

  return {
    barrier_strength: clamp01(0.15 + barrier * 0.12 + negative * 0.05),
    trust_signal: clamp01(0.18 + trust * 0.13 + positive * 0.04),
    misinformation_risk: clamp01(0.08 + misinformation * 0.16),
    inoculation_opportunity: clamp01(0.12 + misinformation * 0.12 + social * 0.06 + negative * 0.04),
    social_influence: clamp01(0.1 + social * 0.12),
    adoption_stance: positive > negative ? "supportive" : negative > positive ? "resistant_or_uncertain" : "mixed_or_unclear",
    emotional_intensity: clamp01(0.1 + emotional * 0.12 + misinformation * 0.04),
    credibility: clamp01(0.35 + grounded * 0.1 + trust * 0.04),
    summary:
      misinformation > 0
        ? "This narrative contains a potential misinformation or safety concern that may benefit from prebunking and trusted messenger response."
        : barrier > trust
          ? "This narrative is mainly a practical adoption-barrier account. Policy should address affordability, access, repair, or usability before persuasion."
          : "This narrative contains usable adoption and trust signals that can inform model assumptions and policy communication."
  };
}

async function encodeNarrative(request: Request, env: Env, narrativeId: string): Promise<Response> {
  const payload = await parseJson<{ mode?: string; encoder?: string }>(request);
  const record = await env.DB.prepare("SELECT id, body FROM narratives WHERE id = ?").bind(narrativeId).first<{ id: string; body: string }>();
  if (!record) return bad("Narrative not found.", 404);
  const encoding = heuristicEncode(record.body);
  const encodingId = id("enc");
  const ts = nowIso();
  await env.DB.prepare(
    `INSERT INTO encodings (
      id, narrative_id, mode, encoder, barrier_strength, trust_signal,
      misinformation_risk, inoculation_opportunity, social_influence,
      adoption_stance, emotional_intensity, credibility, summary, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      encodingId,
      narrativeId,
      payload.mode || "heuristic",
      payload.encoder || "cloudflare-local-heuristic",
      encoding.barrier_strength,
      encoding.trust_signal,
      encoding.misinformation_risk,
      encoding.inoculation_opportunity,
      encoding.social_influence,
      encoding.adoption_stance,
      encoding.emotional_intensity,
      encoding.credibility,
      encoding.summary,
      ts
    )
    .run();
  await audit(env, "narrative", narrativeId, "encoded", payload.encoder || "cloudflare-local-heuristic", encoding);
  return json({ ok: true, encoding_id: encodingId, encoding });
}

async function exportRepository(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const workspaceId = url.searchParams.get("workspace_id") || "default";
  const narratives = await env.DB.prepare("SELECT * FROM narratives WHERE workspace_id = ? ORDER BY created_at DESC").bind(workspaceId).all();
  const encodings = await env.DB.prepare(
    "SELECT e.* FROM encodings e JOIN narratives n ON n.id = e.narrative_id WHERE n.workspace_id = ? ORDER BY e.created_at DESC"
  )
    .bind(workspaceId)
    .all();
  const auditRows = await env.DB.prepare("SELECT * FROM audit_events ORDER BY created_at DESC LIMIT 500").all();
  return json({
    ok: true,
    exported_at: nowIso(),
    workspace_id: workspaceId,
    narratives: narratives.results || [],
    encodings: encodings.results || [],
    audit: auditRows.results || []
  });
}

async function uploadFile(request: Request, env: Env): Promise<Response> {
  const maxMb = Number(env.MAX_UPLOAD_MB || "20");
  const form = await request.formData();
  const file = form.get("file");
  if (!(file instanceof File)) return bad("Upload must include a file field.");
  if (file.size > maxMb * 1024 * 1024) return bad(`File is too large. Maximum is ${maxMb} MB.`, 413);
  const workspaceId = String(form.get("workspace_id") || "default");
  const route = String(form.get("route") || "");
  await ensureWorkspace(env, { id: workspaceId });
  const bytes = await file.arrayBuffer();
  const digest = await sha256Hex(bytes);
  const fileId = id("file");
  const key = `${workspaceId}/${fileId}/${file.name.replace(/[^a-zA-Z0-9._-]/g, "_")}`;
  await env.FILES.put(key, bytes, {
    httpMetadata: { contentType: file.type || "application/octet-stream" },
    customMetadata: { sha256: digest, workspace_id: workspaceId, route }
  });
  await env.DB.prepare(
    "INSERT INTO files (id, workspace_id, r2_key, filename, content_type, byte_size, sha256, route, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  )
    .bind(fileId, workspaceId, key, file.name, file.type || null, file.size, digest, route || null, nowIso())
    .run();
  await audit(env, "file", fileId, "uploaded", undefined, { filename: file.name, sha256: digest, route });
  return json({ ok: true, file_id: fileId, filename: file.name, sha256: digest, r2_key: key }, 201);
}

async function route(request: Request, env: Env): Promise<Response> {
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS_HEADERS });
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "") || "/";

  if (request.method === "GET" && path === "/api/health") return handleHealth(env);
  if (request.method === "GET" && path === "/api/workspaces") return listWorkspaces(env);
  if (request.method === "POST" && path === "/api/workspaces") return createWorkspace(request, env);
  if (request.method === "GET" && path === "/api/narratives") return listNarratives(request, env);
  if (request.method === "POST" && path === "/api/narratives") return createNarrative(request, env);
  if (request.method === "POST" && path === "/api/narratives/commit-reviewed") return commitReviewed(request, env);
  if (request.method === "GET" && path === "/api/repository/export") return exportRepository(request, env);
  if (request.method === "POST" && path === "/api/files/upload") return uploadFile(request, env);

  const narrativeMatch = path.match(/^\/api\/narratives\/([^/]+)$/);
  if (narrativeMatch && request.method === "GET") return getNarrative(env, narrativeMatch[1]);

  const reviewMatch = path.match(/^\/api\/narratives\/([^/]+)\/review$/);
  if (reviewMatch && request.method === "POST") return reviewNarrative(request, env, reviewMatch[1]);

  const uncommitMatch = path.match(/^\/api\/narratives\/([^/]+)\/uncommit$/);
  if (uncommitMatch && request.method === "POST") return uncommitNarrative(request, env, uncommitMatch[1]);

  const encodeMatch = path.match(/^\/api\/narratives\/([^/]+)\/encode$/);
  if (encodeMatch && request.method === "POST") return encodeNarrative(request, env, encodeMatch[1]);

  return bad("Endpoint not found.", 404);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      return await route(request, env);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown server error.";
      return json({ ok: false, error: message }, 500);
    }
  }
};
