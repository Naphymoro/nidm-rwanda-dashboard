import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  ENGINE: DurableObjectNamespace<NdimEngine>;
  NDIM_ALLOWED_ORIGINS: string;
  DATABASE_URL?: string;
}

export class NdimEngine extends Container<Env> {
  defaultPort = 8080;
  // The engine has no /ping; /health answers once uvicorn is up.
  pingEndpoint = "container/health";
  // Files on the container's disk are lost when it sleeps, so keep it up well past a working session.
  sleepAfter = "2h";

  constructor(ctx: DurableObjectState<{}>, env: Env) {
    super(ctx, env);
    this.envVars = {
      NDIM_ALLOWED_ORIGINS: env.NDIM_ALLOWED_ORIGINS,
      ...(env.DATABASE_URL ? { DATABASE_URL: env.DATABASE_URL } : {}),
    };
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // One named instance: every request must reach the container that holds the files.
    return getContainer(env.ENGINE, "main").fetch(request);
  },
};
