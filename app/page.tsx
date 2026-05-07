"use client";

import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronRight,
  Circle,
  Clock3,
  Code2,
  Copy,
  Database,
  FileCode2,
  Files,
  FolderGit2,
  GitBranch,
  Hammer,
  LayoutPanelTop,
  Loader2,
  MessageSquare,
  MoreHorizontal,
  PanelRight,
  Plus,
  Search,
  Send,
  Sparkles,
  SquareTerminal,
  UserRound,
  Zap,
} from "lucide-react";
import type { FormEvent } from "react";
import { useMemo, useState } from "react";

type MessageRole = "assistant" | "user";
type StepState = "done" | "running" | "waiting";

type AgentMessage = {
  id: number;
  role: MessageRole;
  kicker?: string;
  body: string;
  bullets?: string[];
  artifact?: string;
};

type TraceStep = {
  label: string;
  detail: string;
  state: StepState;
};

type FileItem = {
  path: string;
  note: string;
  status: "changed" | "context" | "next";
};

const activeRun =
  "Build NDIM RW into a Codex-like agent workspace: dense, calm, developer-grade, with thread navigation, transparent task progress, chat responses, tool activity, terminal output, file context, and artifact previews.";

const implementationArtifact =
  "Implemented workspace\n\n- Thread navigation: active runs, repo branch, and workspace state\n- Conversation surface: assistant/user turns with concise reasoning summaries\n- Process visibility: live task trace and run state\n- Tool activity: file edits, checks, preview refresh, and blocked build note\n- Output surfaces: terminal log and artifact panel\n- Visual direction: quiet Codex-like developer workspace, no dashboard hero layout";

const toolEvents = [
  { name: "move", detail: "renamed repository folder to ndim_rw", state: "done" },
  { name: "read", detail: "audited root Next app and FastAPI backend", state: "done" },
  { name: "edit", detail: "replaced app/page.tsx and app/globals.css", state: "done" },
  { name: "preview", detail: "synced dependency-free ui-preview.html", state: "done" },
  { name: "build", detail: "blocked because npm/pnpm are unavailable here", state: "waiting" },
];

const starterMessages: AgentMessage[] = [
  {
    id: 1,
    role: "assistant",
    kicker: "Workspace rebuilt",
    body: "The interface has been redesigned as an active agent workspace, not a dashboard. It now centers the run, the conversation, the task trace, the file context, and the generated output.",
    bullets: [
      "Left rail behaves like Codex thread and workspace navigation.",
      "Center column is a chat-first work surface with task context.",
      "Right rail shows process, tool activity, terminal output, files, and artifacts.",
    ],
    artifact: implementationArtifact,
  },
  {
    id: 2,
    role: "assistant",
    kicker: "Execution note",
    body: "The served root UI and static preview now match this direction. The remaining gap is runtime wiring: replacing the local demo responses with streamed FastAPI agent events.",
  },
];

const starterTrace: TraceStep[] = [
  {
    label: "Clarify intent",
    detail: "Convert the rough request into a crisp UI product prompt.",
    state: "done",
  },
  {
    label: "Discard old layout",
    detail: "Drop the first preview aesthetic and rebuild the interface language.",
    state: "done",
  },
  {
    label: "Compose workspace",
    detail: "Create Codex-style chat, task trace, file context, and artifact panels.",
    state: "running",
  },
  {
    label: "Wire live agent",
    detail: "Next step: stream real backend events instead of local demo responses.",
    state: "waiting",
  },
];

const files: FileItem[] = [
  { path: "app/page.tsx", note: "Full Codex-style workspace", status: "changed" },
  { path: "app/globals.css", note: "New interface system", status: "changed" },
  { path: "ui-preview.html", note: "Dependency-free preview", status: "changed" },
  { path: "backend/app/main.py", note: "Agent endpoint target", status: "next" },
  { path: "README.md", note: "Setup docs need repair", status: "context" },
];

const threads = [
  { title: "Redesign Codex UI", meta: "active now" },
  { title: "Audit backend routes", meta: "4 files read" },
  { title: "Rwanda simulation", meta: "draft artifact" },
  { title: "Deployment gaps", meta: "docs missing" },
];

const quickActions = [
  "Audit the repo like Codex",
  "Show the agent task plan",
  "Create a live backend streaming endpoint",
];

function responseFor(prompt: string, id: number): AgentMessage {
  const lower = prompt.toLowerCase();

  if (lower.includes("backend") || lower.includes("stream")) {
    return {
      id,
      role: "assistant",
      kicker: "Implementation route",
      body: "The next serious upgrade is an agent run endpoint that emits structured events to this UI: message deltas, tool calls, observations, file edits, and artifacts.",
      bullets: [
        "Add `POST /agent/runs` to create a run.",
        "Add `GET /agent/runs/{id}/events` for server-sent events.",
        "Persist messages, trace steps, tool events, and artifacts in the database.",
      ],
      artifact:
        "Backend target\n\n- FastAPI route: /agent/runs\n- Transport: server-sent events\n- Event types: status, message, tool_call, observation, artifact, done\n- UI state: replace demo timers with streamed events",
    };
  }

  if (lower.includes("plan") || lower.includes("task")) {
    return {
      id,
      role: "assistant",
      kicker: "Task plan",
      body: "The work should move in four passes: stabilize the app entrypoint, connect a real agent service, stream task progress, then attach simulation artifacts.",
      bullets: [
        "Unify root app and archived frontend folders.",
        "Add real model/provider configuration with safe fallbacks.",
        "Render backend events in the process rail and transcript.",
      ],
      artifact:
        "Plan\n\n1. App shell and preview polish\n2. Agent run API\n3. Streaming event renderer\n4. Simulation and export artifacts\n5. README and environment setup repair",
    };
  }

  return {
    id,
    role: "assistant",
    kicker: "Repo audit",
    body: "The UI is now shaped around code work: inspect files, show process, respond in chat, and surface outputs. The product gap is not visual anymore; it is connecting the demo state to real backend runs.",
    bullets: [
      "Strong backend: ingestion, encoding, simulation, evaluation, analytics.",
      "Weak integration: no live agent endpoint yet.",
      "Documentation gap: setup instructions mention missing env and compose files.",
    ],
    artifact:
      "Audit\n\nStatus: redesigned shell ready\nRisk: missing package manager prevents local Next build here\nNext: add live agent API and stream progress into the UI",
  };
}

export default function Home() {
  const [messages, setMessages] = useState<AgentMessage[]>(starterMessages);
  const [trace, setTrace] = useState<TraceStep[]>(starterTrace);
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);
  const [copied, setCopied] = useState(false);

  const latestArtifact = useMemo(() => {
    return [...messages].reverse().find((message) => message.artifact)?.artifact ?? implementationArtifact;
  }, [messages]);

  function submitPrompt(value: string) {
    const trimmed = value.trim();
    if (!trimmed || running) return;

    const userId = Date.now();
    const assistantId = userId + 1;

    setMessages((current) => [
      ...current,
      { id: userId, role: "user", body: trimmed },
    ]);
    setPrompt("");
    setRunning(true);
    setTrace([
      { label: "Read prompt", detail: "Classify intent and pick the workflow.", state: "done" },
      { label: "Inspect context", detail: "Map request to app files, backend routes, and UI state.", state: "running" },
      { label: "Draft response", detail: "Prepare chat answer and artifact output.", state: "waiting" },
      { label: "Update workspace", detail: "Refresh process rail and terminal panel.", state: "waiting" },
    ]);

    window.setTimeout(() => {
      setTrace([
        { label: "Read prompt", detail: "Classified intent and selected workflow.", state: "done" },
        { label: "Inspect context", detail: "Relevant app and backend context reviewed.", state: "done" },
        { label: "Draft response", detail: "Writing response with visible reasoning summary.", state: "running" },
        { label: "Update workspace", detail: "Artifact panel will refresh after completion.", state: "waiting" },
      ]);
    }, 450);

    window.setTimeout(() => {
      setMessages((current) => [...current, responseFor(trimmed, assistantId)]);
      setTrace([
        { label: "Read prompt", detail: "Classified intent and selected workflow.", state: "done" },
        { label: "Inspect context", detail: "Relevant app and backend context reviewed.", state: "done" },
        { label: "Draft response", detail: "Response and artifact are ready.", state: "done" },
        { label: "Update workspace", detail: "Workspace is ready for the next command.", state: "running" },
      ]);
      setRunning(false);
    }, 980);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitPrompt(prompt);
  }

  async function copyArtifact() {
    try {
      await navigator.clipboard.writeText(latestArtifact);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <main className="agent-os">
      <aside className="thread-rail" aria-label="Threads and workspace">
        <section className="identity">
          <div className="identity-mark">C</div>
          <div>
            <strong>NDIM Codex</strong>
            <span>workspace-write</span>
          </div>
        </section>

        <button className="primary-action" type="button" onClick={() => submitPrompt("Audit the repo like Codex")}>
          <Plus size={16} />
          New run
        </button>

        <section className="rail-block">
          <div className="rail-label">Threads</div>
          {threads.map((thread, index) => (
            <button key={thread.title} className={index === 0 ? "thread active" : "thread"} type="button">
              <MessageSquare size={15} />
              <span>
                <strong>{thread.title}</strong>
                <em>{thread.meta}</em>
              </span>
            </button>
          ))}
        </section>

        <section className="rail-block">
          <div className="rail-label">Workspace</div>
          <div className="workspace-pill"><FolderGit2 size={15} /> ndim_rw</div>
          <div className="workspace-pill"><GitBranch size={15} /> main</div>
          <div className="workspace-pill"><Database size={15} /> local sqlite fallback</div>
        </section>
      </aside>

      <section className="session">
        <header className="session-topbar">
          <div className="breadcrumbs">
            <span>Codex</span>
            <ChevronRight size={14} />
            <span>ndim_rw</span>
            <ChevronRight size={14} />
            <strong>UI redesign</strong>
          </div>
          <div className="session-tools">
            <button type="button" title="Search"><Search size={16} /></button>
            <button type="button" title="Layout"><LayoutPanelTop size={16} /></button>
            <button type="button" title="More"><MoreHorizontal size={16} /></button>
          </div>
        </header>

        <section className="work-surface">
          <div className="brief-card">
            <div className="brief-icon"><Sparkles size={18} /></div>
            <div>
              <span>Active run</span>
              <p>{activeRun}</p>
            </div>
          </div>

          <section className="transcript" aria-live="polite">
            {messages.map((message) => (
              <article key={message.id} className={`turn ${message.role}`}>
                <div className="turn-avatar">
                  {message.role === "assistant" ? <Bot size={16} /> : <UserRound size={16} />}
                </div>
                <div className="turn-body">
                  {message.kicker ? <span className="turn-kicker">{message.kicker}</span> : null}
                  <p>{message.body}</p>
                  {message.bullets ? (
                    <div className="summary-box">
                      <strong><Zap size={14} /> Reasoning summary</strong>
                      <ul>
                        {message.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}
                      </ul>
                    </div>
                  ) : null}
                  {message.artifact ? <pre>{message.artifact}</pre> : null}
                </div>
              </article>
            ))}

            {running ? (
              <article className="turn assistant">
                <div className="turn-avatar"><Loader2 className="spin" size={16} /></div>
                <div className="turn-body live">
                  <span className="turn-kicker">Working</span>
                  <p>Inspecting the request, composing the response, and updating the workspace panels.</p>
                </div>
              </article>
            ) : null}
          </section>
        </section>

        <section className="quick-actions" aria-label="Quick actions">
          {quickActions.map((action) => (
            <button key={action} type="button" onClick={() => submitPrompt(action)}>
              {action}
              <ChevronRight size={14} />
            </button>
          ))}
        </section>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            aria-label="Agent prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Message NDIM Codex. Ask it to audit, implement, simulate, or explain..."
            rows={2}
          />
          <button type="submit" disabled={!prompt.trim() || running} title="Send">
            {running ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
          </button>
        </form>
      </section>

      <aside className="inspector" aria-label="Agent state inspector">
        <section className="inspector-card run-state">
          <div>
            <span>Run state</span>
            <strong>{running ? "thinking" : "ready"}</strong>
          </div>
          <Activity size={18} />
        </section>

        <section className="inspector-card">
          <div className="card-title">
            <PanelRight size={16} />
            <h2>Process</h2>
          </div>
          <div className="steps">
            {trace.map((step) => (
              <div key={step.label} className={`step ${step.state}`}>
                <div className="step-icon">
                  {step.state === "done" ? <CheckCircle2 size={14} /> : step.state === "running" ? <Loader2 size={14} className="spin" /> : <Circle size={14} />}
                </div>
                <div>
                  <strong>{step.label}</strong>
                  <p>{step.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="inspector-card">
          <div className="card-title">
            <Files size={16} />
            <h2>Context</h2>
          </div>
          <div className="file-stack">
            {files.map((file) => (
              <div key={file.path} className={`file-row ${file.status}`}>
                <FileCode2 size={15} />
                <span>
                  <strong>{file.path}</strong>
                  <em>{file.note}</em>
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="inspector-card">
          <div className="card-title">
            <Code2 size={16} />
            <h2>Tool activity</h2>
          </div>
          <div className="tool-stack">
            {toolEvents.map((event) => (
              <div key={`${event.name}-${event.detail}`} className={`tool-event ${event.state}`}>
                <span>{event.name}</span>
                <p>{event.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="inspector-card terminal-card">
          <div className="card-title">
            <SquareTerminal size={16} />
            <h2>Terminal</h2>
            <Clock3 size={14} />
          </div>
          <pre>{`$ git status --short
 M app/globals.css
 M app/page.tsx
 M ui-preview.html

$ next build
blocked: npm/pnpm unavailable in this shell`}</pre>
        </section>

        <section className="inspector-card artifact-card">
          <div className="card-title">
            <Hammer size={16} />
            <h2>Artifact</h2>
            <button type="button" onClick={copyArtifact}>{copied ? "Copied" : <Copy size={14} />}</button>
          </div>
          <pre>{latestArtifact}</pre>
        </section>
      </aside>
    </main>
  );
}
