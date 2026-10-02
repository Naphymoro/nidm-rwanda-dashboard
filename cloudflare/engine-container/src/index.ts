import { Container, getContainer } from "@cloudflare/containers";

// Required by the containers library once a deployment has used outbound interception (an earlier version did; its
// settings persist): without this export every container start fails with "ctx.exports.ContainerProxy is undefined".
export { ContainerProxy } from "@cloudflare/containers";

interface Env {
  ENGINE: DurableObjectNamespace<NdimEngine>;
  DB: D1Database;
  NDIM_ALLOWED_ORIGINS: string;
  NDIM_MIRROR_TOKEN: string;
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

export class NdimEngine extends Container<Env> {
  defaultPort = 8080;
  // The engine has no /ping; /health answers once uvicorn is up.
  pingEndpoint = "container/health";
  // The data folder is kept in D1, so a sleep no longer loses work; sleeping after 30 idle minutes saves cost.
  sleepAfter = "30m";
  private restored: Promise<void> | null = null;
  private pullPending = false;

  constructor(ctx: DurableObjectState<{}>, env: Env) {
    super(ctx, env);
    this.envVars = {
      NDIM_ALLOWED_ORIGINS: env.NDIM_ALLOWED_ORIGINS,
      NDIM_MIRROR_TOKEN: env.NDIM_MIRROR_TOKEN,
      ...(env.DATABASE_URL ? { DATABASE_URL: env.DATABASE_URL } : {}),
    };
  }

  override onStart() {
    this.restored = null; // a new container starts empty: restore it again
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
    })().catch((error) => {
      this.restored = null; // try again on the next request
      throw error;
    });
    return this.restored;
  }

  /** Save what changed in the engine's data folder to D1, then acknowledge it. */
  async pull() {
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
    await this.restore();
    const response = await this.containerFetch(request);
    if (request.method !== "GET" && request.method !== "HEAD") {
      await this.pull(); // most changes are saved before the visitor gets the answer
    }
    if (!this.pullPending) { // and once more shortly after, for anything written while a reply streamed
      this.pullPending = true;
      await this.schedule(PULL_AFTER_SECONDS, "pullLater");
    }
    return response;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (new URL(request.url).pathname.startsWith("/__mirror")) {
      return new Response("Not Found", { status: 404 }); // the mirror routes are the Worker's, never a visitor's
    }
    // One named instance: every request must reach the container that holds the files.
    return getContainer(env.ENGINE, "main").fetch(request);
  },
};
