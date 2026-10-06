import { Container, getContainer } from "@cloudflare/containers";
import { sharedAnswers } from "./shared-answers";

// Required by the containers library once a deployment has used outbound interception (an earlier version did; its
// settings persist): without this export every container start fails with "ctx.exports.ContainerProxy is undefined".
export { ContainerProxy } from "@cloudflare/containers";

interface Env {
  ENGINE: DurableObjectNamespace<NdimEngine>;
  DB: D1Database;
  NDIM_ALLOWED_ORIGINS: string;
  NDIM_MIRROR_TOKEN: string;
  NDIM_SYNC_TOKENS?: string; // access keys for shared answers (src/shared-answers.ts); never given to the container
  DATABASE_URL?: string;
}

// The engine's data folder outlives the container through D1. The Worker restores it into each new container before
// any visitor's request, and pulls what changed after requests (backend/app/durable_mirror.py describes the engine's
// side). An earlier design had the engine push to a host on its egress; on Cloudflare that host was never reached.
const RESTORE_BATCH_BYTES = 3_000_000;
const PULL_AFTER_SECONDS = 15; // chat replies are written while they stream: pull again once they have finished

async function ensureTable(db: D1Database) {
  await db.prepare("CREATE TABLE IF NOT EXISTS files (key TEXT PRIMARY KEY, body BLOB NOT NULL, updated_at TEXT NOT NULL)").run();
}

function toBase64(bytes: Uint8Array) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

function fromBase64(text: string) {
  return Uint8Array.from(atob(text), (c) => c.charCodeAt(0));
}

/** Durations of a request's steps, sent back as a Server-Timing header so the cloud delay can be read per step. */
class Timing {
  private entries: string[] = [];

  async time<T>(name: string, step: () => Promise<T>): Promise<T> {
    const start = Date.now();
    try {
      return await step();
    } finally {
      this.entries.push(`${name};dur=${Date.now() - start}`);
    }
  }

  attach(response: Response, existing = response.headers.get("Server-Timing")) {
    const headers = new Headers(response.headers);
    headers.set("Server-Timing", [...this.entries, ...(existing ? [existing] : [])].join(", "));
    return new Response(response.body, { status: response.status, statusText: response.statusText, headers, webSocket: response.webSocket });
  }
}

/** A failed request answered as the engine answers errors ({detail}), with CORS so the browser can read it. */
function unavailable(request: Request, env: Env) {
  const headers = new Headers({ "Content-Type": "application/json", "Retry-After": "5" });
  const origin = request.headers.get("Origin");
  if (origin && env.NDIM_ALLOWED_ORIGINS.split(",").map((o) => o.trim()).includes(origin)) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Vary", "Origin");
  }
  const detail = "The engine is starting or restarting. Nothing was lost; try again in a few seconds.";
  return new Response(JSON.stringify({ detail }), { status: 503, headers });
}

export class NdimEngine extends Container<Env> {
  defaultPort = 8080;
  // The engine has no /ping; /health answers once uvicorn is up.
  pingEndpoint = "container/health";
  // The data folder is kept in D1, so a sleep no longer loses work; sleeping after 30 idle minutes saves cost.
  sleepAfter = "30m";
  private restored: Promise<boolean> | null = null; // true when this call put the saved files back
  private pullPending = false;
  private pulling: Promise<void> = Promise.resolve(); // one pull at a time: overlapping pulls would race on ack

  constructor(ctx: DurableObjectState<{}>, env: Env) {
    super(ctx, env);
    this.envVars = {
      NDIM_ALLOWED_ORIGINS: env.NDIM_ALLOWED_ORIGINS,
      NDIM_MIRROR_TOKEN: env.NDIM_MIRROR_TOKEN,
      ...(env.DATABASE_URL ? { DATABASE_URL: env.DATABASE_URL } : {}),
    };
  }

  // Not onStart: the library calls it on every startAndWaitForPorts, even with the container already running, and
  // restore() calls that itself. Resetting there made every request restore the whole data folder again (~2.5 s).
  override onStop() {
    this.restored = null; // the next container starts empty: restore it again
  }

  private engine(path: string, init: RequestInit = {}) {
    return this.containerFetch(`http://container${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", "X-NDIM-Mirror-Token": this.env.NDIM_MIRROR_TOKEN },
    });
  }

  private restore() {
    this.restored ??= (async () => {
      await this.startAndWaitForPorts();
      // An empty batch writes nothing; 409 means the engine was already restored (this object restarted while the
      // container ran), so the saved files need not be read from D1 at all.
      const probe = await this.engine("/__mirror/restore", { method: "POST", body: JSON.stringify({ files: {}, done: false }) });
      if (probe.status === 409) return false;
      if (!probe.ok) throw new Error(`restore failed: ${probe.status} ${await probe.text()}`);
      await ensureTable(this.env.DB);
      const { results } = await this.env.DB.prepare("SELECT key, body FROM files ORDER BY key").all<{ key: string; body: ArrayBuffer }>();
      let files: Record<string, string> = {};
      let size = 0;
      const send = async (done: boolean) => {
        const response = await this.engine("/__mirror/restore", { method: "POST", body: JSON.stringify({ files, done }) });
        // 409: the engine is already restored (this Worker instance restarted while the container ran). Fine.
        if (!response.ok && response.status !== 409) throw new Error(`restore failed: ${response.status} ${await response.text()}`);
        files = {};
        size = 0;
      };
      for (const row of results) {
        const encoded = toBase64(new Uint8Array(row.body));
        if (size + encoded.length > RESTORE_BATCH_BYTES && size) await send(false);
        files[row.key] = encoded;
        size += encoded.length;
      }
      await send(true);
      return true;
    })().catch((error) => {
      this.restored = null; // try again on the next request
      throw error;
    });
    return this.restored;
  }

  /** Save what changed, one pull after another; a failed save never fails the visitor's request (retried later). */
  pull() {
    this.pulling = this.pulling.then(() => this.pullOnce()).catch((error) => {
      console.error("mirror pull failed; retrying shortly", error);
      this.pullPending = false; // let the next request (or the scheduled pull below) try again
    });
    return this.pulling;
  }

  /** Save what changed in the engine's data folder to D1, then acknowledge it. */
  private async pullOnce() {
    for (let round = 0; round < 20; round++) {
      const response = await this.engine("/__mirror/changes");
      if (!response.ok) throw new Error(`changes failed: ${response.status}`);
      const batch = await response.json<{ id: string | null; put: Record<string, string>; delete: string[]; more: boolean }>();
      if (!batch.id) return;
      const now = new Date().toISOString();
      const statements = [
        ...Object.entries(batch.put).map(([key, body]) => this.env.DB
          .prepare("INSERT OR REPLACE INTO files (key, body, updated_at) VALUES (?, ?, ?)").bind(key, fromBase64(body), now)),
        ...batch.delete.map((key) => this.env.DB.prepare("DELETE FROM files WHERE key = ?").bind(key)),
      ];
      if (statements.length) await this.env.DB.batch(statements);
      await this.engine("/__mirror/ack", { method: "POST", body: JSON.stringify({ id: batch.id }) });
      if (!batch.more) return;
    }
  }

  async pullLater() {
    this.pullPending = false;
    await this.pull();
  }

  override async fetch(request: Request): Promise<Response> {
    const timing = new Timing();
    let response: Response;
    try {
      await timing.time("restore", () => this.restore());
      const retry = request.clone() as Request;
      response = await timing.time("container", () => this.containerFetch(request));
      // A replaced container (a deploy rolling out, a crash) starts empty and answers 503 until restored, and onStop
      // can arrive late. The engine refuses before doing anything, so restoring and sending the request again is safe.
      if (response.status === 503) {
        this.restored = null;
        if (await timing.time("restore", () => this.restore())) {
          response = await timing.time("container", () => this.containerFetch(retry));
        }
      }
    } catch (error) {
      // Thrown while the container starts or is replaced (a deploy). Uncaught, it became Cloudflare's opaque error 1101.
      console.error("engine request failed", request.method, new URL(request.url).pathname, error);
      return unavailable(request, this.env);
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      await timing.time("pull", () => this.pull()); // most changes are saved before the visitor gets the answer
    }
    if (!this.pullPending) { // and once more shortly after, for anything written while a reply streamed
      this.pullPending = true;
      try {
        await timing.time("schedule", () => this.schedule(PULL_AFTER_SECONDS, "pullLater"));
      } catch (error) {
        this.pullPending = false; // the visitor's answer is ready; the next request schedules the pull
        console.error("scheduling the mirror pull failed", error);
      }
    }
    return timing.attach(response);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const path = new URL(request.url).pathname;
    if (path.startsWith("/__mirror")) {
      return new Response("Not Found", { status: 404 }); // the mirror routes are the Worker's, never a visitor's
    }
    if (path === "/shared-answers" || path.startsWith("/shared-answers/")) {
      return sharedAnswers(request, env); // answered by the Worker and D1; the container is not started for these
    }
    // One named instance: every request must reach the container that holds the files.
    const timing = new Timing();
    const safe = request.method === "GET" || request.method === "HEAD";
    for (let attempt = 0; ; attempt++) {
      try {
        // getContainer per attempt: a stub that saw its Durable Object reset (a deploy) stays broken.
        const response = await timing.time("object", () => getContainer(env.ENGINE, "main").fetch(request));
        return timing.attach(response);
      } catch (error: any) {
        // Only reads are retried: a write may have reached the engine before the error.
        if (safe && attempt === 0 && error?.retryable) continue;
        console.error("engine object failed", request.method, path, error);
        return unavailable(request, env);
      }
    }
  },
};
