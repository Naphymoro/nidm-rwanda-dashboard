# NIDM Rwanda Research Dashboard

Research-grade narrative ingestion and digital-twin SaaS scaffold for the Narrative Inoculation Diffusion Model.

## Stack

- Frontend: Next.js, TypeScript, CSS3 futuristic dashboard UI
- Backend: FastAPI, Pydantic, Python scientific stack
- Database: PostgreSQL/PostGIS-ready schema path, no Supabase dependency
- Runtime: Docker Compose for local development
- Deployment target: Render, Railway, Fly.io, or self-hosted VPS. Vercel is optional for frontend only.

## Core modules

1. SDMX-inspired narrative ingestion gateway
2. Canonical narrative schema
3. Manual, AI, and hybrid encoding workflow
4. Country and administrative-unit categorization
5. Compartmental model API
6. Agent-based/hybrid digital-twin API placeholder
7. RL feedback and model-improvement loop placeholder
8. Futuristic SaaS research dashboard

## Local development

```bash
cp .env.example .env
docker compose up --build
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs

## Recommended deployment

Best no-Supabase path: Render Blueprint or Railway monorepo deployment with managed PostgreSQL.

Vercel is excellent for the Next.js frontend, but this platform also needs a Python backend and database. For a simpler single-platform deployment, Render or Railway is better than Vercel alone.
