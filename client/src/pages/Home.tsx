import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Brain,
  CheckCircle2,
  Cpu,
  GitCompare,
  LayoutDashboard,
  Network,
  Play,
  SlidersHorizontal,
  Terminal,
  Upload,
  UsersRound,
  Workflow,
  Bot,
} from "lucide-react";
import AgentBasedModelView from "@/components/AgentBasedModelView";
import DashboardLayout, { useNIDMMode } from "@/components/DashboardLayout";
import DigitalTwinView from "@/components/DigitalTwinView";
import FileUploadPanel from "@/components/FileUploadPanel";
import ModelAuditBridge from "@/components/ModelAuditBridge";
import NarrativeEncodingPanel from "@/components/NarrativeEncodingPanel";
import NarrativeLibrary from "@/components/NarrativeLibrary";
import ODESystemView from "@/components/ODESystemView";
import RLOptimizerView from "@/components/RLOptimizerView";
import ScenarioComparison from "@/components/ScenarioComparison";
import SensitivityAnalysis from "@/components/SensitivityAnalysis";
import SimulationChart from "@/components/SimulationChart";
import SimulationPlayer from "@/components/SimulationPlayer";
import type { ParsedNarrative } from "@/lib/narrativeParser";

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

type BackendEncodedNarrative = {
  narrative_id: string;
  encoding_mode: string;
  themes: string[];
  sentiment?: number | null;
  adoption_barrier_score?: number | null;
  trust_score?: number | null;
  confidence?: number | null;
  model_notes?: string | null;
};

type PipelineRunResult = {
  narrative_count?: number;
  encoded?: BackendEncodedNarrative[];
  parameters?: Record<string, number>;
  model_mode?: string;
  summary?: {
    final_adoption?: number;
    average_trust?: number;
    average_barrier?: number;
  };
};

const BACKEND_URL = "http://127.0.0.1:8010";
const REPO_URL = "https://github.com/Naphymoro/nidm-rwanda-dashboard";

const tabs = [
  { id: "dashboard", label: "Overview", icon: <LayoutDashboard className="h-4 w-4" /> },
  { id: "narratives", label: "Narratives", icon: <Brain className="h-4 w-4" /> },
  { id: "ode", label: "ODE System", icon: <Workflow className="h-4 w-4" /> },
  { id: "agents", label: "Agent Model", icon: <UsersRound className="h-4 w-4" /> },
  { id: "simulation", label: "Simulation", icon: <BarChart3 className="h-4 w-4" /> },
  { id: "scenarios", label: "Scenarios", icon: <GitCompare className="h-4 w-4" /> },
  { id: "sensitivity", label: "Sensitivity", icon: <SlidersHorizontal className="h-4 w-4" /> },
  { id: "twin", label: "Digital Twin", icon: <Network className="h-4 w-4" /> },
  { id: "rl", label: "RL Optimizer", icon: <Bot className="h-4 w-4" /> },
];

const generateSimulationData = (): SimulationDataPoint[] => {
  const data: SimulationDataPoint[] = [];

  for (let t = 0; t <= 100; t += 1) {
    const factor = t / 100;
    data.push({
      time: t,
      Susceptible: Math.max(0.04, 0.54 * Math.exp(-0.021 * t)),
      Misinformed: Math.max(0.03, 0.28 * Math.sin(factor * Math.PI) * Math.exp(-0.012 * t)),
      Truth: Math.min(0.62, 0.13 + 0.35 * (1 - Math.exp(-0.032 * t))),
      Inoculated: Math.min(0.44, 0.08 + 0.26 * (1 - Math.exp(-0.023 * t))),
      Resistant: Math.min(0.36, 0.06 + 0.23 * (1 - Math.exp(-0.018 * t))),
    });
  }

  return data;
};

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const simulationData = useMemo(() => generateSimulationData(), []);
  const [narratives, setNarratives] = useState<ParsedNarrative[]>([]);

  useEffect(() => {
    const handleRunSimulation = () => setActiveTab("simulation");
    window.addEventListener("nidm:run-simulation", handleRunSimulation);
    return () => window.removeEventListener("nidm:run-simulation", handleRunSimulation);
  }, []);

  const handleNarrativesParsed = useCallback((parsed: ParsedNarrative[]) => {
    setNarratives((prev) => [...prev, ...parsed]);
  }, []);

  const handleRemoveNarrative = useCallback((id: string) => {
    setNarratives((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const handleClearNarratives = useCallback(() => setNarratives([]), []);

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardView simulationData={simulationData} narratives={narratives} onNavigate={setActiveTab} />;
      case "narratives":
        return (
          <NarrativesView
            narratives={narratives}
            onNarrativesParsed={handleNarrativesParsed}
            onRemove={handleRemoveNarrative}
            onClear={handleClearNarratives}
          />
        );
      case "ode":
        return <ODESystemView />;
      case "agents":
        return <AgentBasedModelView />;
      case "simulation":
        return <SimulationView simulationData={simulationData} />;
      case "scenarios":
        return <ScenarioComparison simulationData={simulationData} />;
      case "sensitivity":
        return <SensitivityAnalysis />;
      case "twin":
        return <DigitalTwinView />;
      case "rl":
        return <RLOptimizerView />;
      default:
        return <DashboardView simulationData={simulationData} narratives={narratives} onNavigate={setActiveTab} />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab} tabs={tabs}>
      {renderContent()}
    </DashboardLayout>
  );
}

function DashboardView({
  simulationData,
  narratives,
  onNavigate,
}: {
  simulationData: SimulationDataPoint[];
  narratives: ParsedNarrative[];
  onNavigate: (tab: string) => void;
}) {
  const { mode } = useNIDMMode();
  const narrativeCount = narratives.length;
  const explainer = {
    novice: "Start here. Upload narrative evidence first, then let the tool validate it, encode it, run models, compare policies, and produce a decision brief.",
    policy: "This runbook follows the policy evidence chain from field narratives to model outputs and a traceable clean-cooking recommendation.",
    expert: "Scientific runbook: source evidence -> SDMX validation -> narrative encoding -> Phi -> ODE/ABM dynamics -> scenario diagnostics -> policy output.",
  }[mode];

  const stages = [
    ["01", "Narrative upload", "Bring in CSV, text, field notes, JSON, XML, or SDMX evidence.", "Evidence ledger", "narratives"],
    ["02", "SDMX gate", "Validate source, place, period, language, and measure fields.", "Clean observations", "narratives"],
    ["03", "Narrative encoding", "Convert multi-paragraph narratives into E, C, tau, kappa, and Phi inputs.", "Model features", "narratives"],
    ["04", "ODE model", "Run the population compartment flow for S, M, T, I, and R.", "Population dynamics", "ode"],
    ["05", "Agent model", "Test household trust, peers, outreach, and district variation.", "Local dynamics", "agents"],
    ["06", "Policy comparison", "Compare scenarios, sensitivity, cost, risk, and feasibility.", "Policy tradeoffs", "scenarios"],
    ["07", "Policy output", "Produce the decision brief with evidence trail and human review.", "Policy brief", "rl"],
  ];

  const modules = [
    ["Input", "Narrative + SDMX", "Upload or paste evidence and keep every paragraph traceable to its source.", "narratives"],
    ["Validation", "SDMX gate", "Stop weak or incomplete evidence before it changes the scientific model.", "narratives"],
    ["Model", "ODE system", "Explain population compartment flow with transparent parameters and equations.", "ode"],
    ["Model", "Agent-based layer", "Check household-level variation that aggregate curves can hide.", "agents"],
    ["Decision", "Scenario comparison", "Rank interventions by impact, cost, risk, and implementation readiness.", "scenarios"],
    ["Decision", "Policy brief", "Convert model readouts into a reviewable recommendation, not an automatic decision.", "rl"],
  ];

  return (
    <div className="minimal-page animate-page-in space-y-5">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>{explainer}</section>

      <section className="minimal-hero">
        <div>
          <p className="eyebrow">Scientific question</p>
          <h2>From narrative evidence to a policy recommendation.</h2>
          <p>
            NIDM Rwanda should feel like a clear scientific instrument: collect evidence, validate it, model it at population and household levels, then explain the policy implication with an audit trail.
          </p>
          <div className="run-actions">
            <button type="button" className="button-primary" onClick={() => onNavigate("narratives")}>
              Start with upload
            </button>
            <button type="button" className="button-ghost" onClick={() => onNavigate("twin")}>
              Review feedback
            </button>
          </div>
        </div>
          <div className="hero-facts">
            <div className="hero-fact">
              <span>Evidence</span>
              <strong>{narrativeCount} narratives loaded</strong>
            </div>
            <div className="hero-fact">
              <span>Method</span>
            <strong>ODE compartments plus household ABM</strong>
          </div>
          <div className="hero-fact">
            <span>Output</span>
            <strong>Scenario matrix and policy brief</strong>
          </div>
        </div>
      </section>

      <AgenticRunPanel narratives={narratives} onNavigate={onNavigate} />

      <section className="control-section">
        <div className="section-heading">
          <span>Simple run path</span>
          <span>evidence to policy</span>
        </div>
        <div className="story-strip mt-3">
          {stages.map(([step, title, description, output, tab]) => (
            <button key={step} type="button" className="story-card" onClick={() => onNavigate(tab)}>
              <span className="story-card-number">{step}</span>
              <span>
                <h3>{title}</h3>
                <p>{description}</p>
              </span>
              <span className="story-card-output">{output}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="control-section">
        <div className="section-heading">
          <span>What each part does</span>
          <span>complete tool coverage</span>
        </div>
        <div className="module-grid mt-3">
          {modules.map(([kicker, title, copy, tab]) => (
            <button key={title} type="button" className="module-card text-left" onClick={() => onNavigate(tab)}>
              <span className="module-kicker">{kicker}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </button>
          ))}
        </div>
      </section>

      <FunctionalityMap onNavigate={onNavigate} />

      <section className="control-section">
        <div className="section-heading">
          <span>Scientific display</span>
          <span>population compartment preview</span>
        </div>
        <div className="mt-4">
          <SimulationChart data={simulationData} height={260} />
        </div>
      </section>

      <section className="policy-output-card">
        <div>
          <p className="eyebrow">Policy output</p>
          <h3>Decision brief, not a black box.</h3>
          <p>
            The final output should show the recommendation, evidence used, model assumptions, ABM warnings, scenario tradeoffs, and the feedback needed before policy sign-off.
          </p>
        </div>
        <div className="output-list">
          <div>Recommendation: trust-led outreach with district review.</div>
          <div>Audit: evidence rows, SDMX gate, Phi, ODE, ABM, scenarios.</div>
          <div>Human review: required before export.</div>
        </div>
      </section>
    </div>
  );
}

function toBackendRecords(narratives: ParsedNarrative[]) {
  return narratives.map((narrative) => ({
    narrative_id: narrative.id,
    text: narrative.quote || narrative.label,
    metadata: {
      source_type: narrative.source,
      source_name: narrative.key,
      country: "Rwanda",
      admin_unit: narrative.targets,
      language: "en",
      provenance: {
        phi: narrative.phi,
        E: narrative.E,
        C: narrative.C,
        tau: narrative.tau,
        kappa: narrative.kappa,
      },
    },
    tags: [narrative.type, narrative.targets].filter(Boolean),
  }));
}

function AgenticRunPanel({
  narratives,
  onNavigate,
}: {
  narratives: ParsedNarrative[];
  onNavigate: (tab: string) => void;
}) {
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const [trace, setTrace] = useState<string[]>([
    "Waiting for evidence. Upload narratives first, then run the scientific pipeline.",
  ]);
  const [result, setResult] = useState<PipelineRunResult | null>(null);

  const readiness = [
    {
      label: "Narrative evidence",
      value: narratives.length ? `${narratives.length} observation${narratives.length === 1 ? "" : "s"}` : "none loaded",
      ready: narratives.length > 0,
    },
    { label: "SDMX gate", value: "client parser wired", ready: true },
    { label: "LLM encoder", value: "backend /encode ready", ready: true },
    { label: "Hybrid model", value: "backend /pipeline/run ready", ready: true },
  ];

  async function runPipeline() {
    if (!narratives.length) {
      setStatus("error");
      setTrace([
        "Blocked: no narratives are loaded.",
        "Open Narratives, upload CSV/TXT/MD/JSON/XML/SDMX, then return here to run the pipeline.",
      ]);
      return;
    }

    setStatus("running");
    setResult(null);
    setTrace([
      "Checking evidence library and preparing backend NarrativeRecord payload.",
      "Calling the SDMX-normalized experiment pipeline.",
    ]);

    try {
      const response = await fetch(`${BACKEND_URL}/pipeline/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toBackendRecords(narratives)),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = (await response.json()) as PipelineRunResult;
      setResult(data);
      setStatus("complete");
      setTrace([
        "Evidence payload accepted by backend pipeline.",
        "Narratives encoded through the AI encoder path; backend falls back to rule-based encoding when no OpenAI key is configured.",
        "Hybrid digital twin completed and produced adoption, trust, and barrier summary values.",
      ]);
    } catch (error) {
      setStatus("error");
      setTrace([
        "The UI is wired, but the backend at http://127.0.0.1:8000 is not reachable from the browser.",
        error instanceof Error ? error.message : "Unknown backend error.",
        "You can still use the client-side upload, SDMX gate, ODE, ABM, scenario, sensitivity, and RL modules.",
      ]);
    }
  }

  return (
    <section className="agentic-panel">
      <div className="agentic-header">
        <div>
          <p className="eyebrow">Agentic run controller</p>
          <h3>Run the evidence-to-model pipeline.</h3>
          <p>
            This panel is the public processing trace: it shows what the tool checks, which endpoint it calls,
            and what result came back.
          </p>
        </div>
        <div className={`status-pill ${status}`}>
          {status === "complete" ? <CheckCircle2 className="h-4 w-4" /> : status === "error" ? <AlertTriangle className="h-4 w-4" /> : <Terminal className="h-4 w-4" />}
          {status}
        </div>
      </div>

      <div className="agentic-grid">
        <div className="readiness-list">
          {readiness.map((item) => (
            <div key={item.label} className={`readiness-item ${item.ready ? "ready" : ""}`}>
              <span>{item.ready ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}</span>
              <div>
                <strong>{item.label}</strong>
                <p>{item.value}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="agent-trace">
          <div className="section-heading">
            <span>Processing trace</span>
            <span>{BACKEND_URL}</span>
          </div>
          <div className="trace-lines">
            {trace.map((line, index) => (
              <div key={`${line}-${index}`} className="trace-line">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{line}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="agent-output">
          <div className="section-heading">
            <span>Latest output</span>
            <span>{result?.model_mode ?? "not run"}</span>
          </div>
          {result?.summary ? (
            <div className="output-metrics">
              <div>
                <span>Final adoption</span>
                <strong>{((result.summary.final_adoption ?? 0) * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span>Average trust</span>
                <strong>{((result.summary.average_trust ?? 0) * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span>Average barrier</span>
                <strong>{((result.summary.average_barrier ?? 0) * 100).toFixed(1)}%</strong>
              </div>
            </div>
          ) : (
            <p className="empty-output">
              Run the pipeline after loading narratives to see encoded features, model parameters, and a policy-ready summary.
            </p>
          )}
        </div>
      </div>

      <div className="agent-actions">
        <button type="button" className="button-primary" onClick={runPipeline} disabled={status === "running"}>
          <Play className="h-4 w-4" />
          {status === "running" ? "Running pipeline" : "Run pipeline"}
        </button>
        <button type="button" className="button-ghost" onClick={() => onNavigate("narratives")}>
          <Upload className="h-4 w-4" />
          Open upload
        </button>
        <button type="button" className="button-ghost" onClick={() => onNavigate("agents")}>
          <UsersRound className="h-4 w-4" />
          Open ABM
        </button>
      </div>
    </section>
  );
}

function FunctionalityMap({ onNavigate }: { onNavigate: (tab: string) => void }) {
  const rows = [
    ["Ingest", "CSV, TXT, MD, JSON, XML, SDMX upload and paste", "FileUploadPanel + narrativeParser + sdmxGate", "narratives"],
    ["Encode", "Phi scoring plus backend OpenAI/fallback narrative encoding", "NarrativeEncodingPanel + backend/app/encoding.py", "narratives"],
    ["Model", "Population compartment flow S/M/T/I/R", "ODESystemView + backend/app/modelling.py", "ode"],
    ["Model", "Agent-based household dynamics", "AgentBasedModelView + backend agent_based proxy", "agents"],
    ["Analyze", "Simulation, scenario competition, sensitivity", "SimulationPlayer + ScenarioComparison + SensitivityAnalysis", "simulation"],
    ["Optimize", "RL policy search and final policy output", "RLOptimizerView + backend/app/optimization.py", "rl"],
  ];

  return (
    <section className="control-section">
      <div className="section-heading">
        <span>Functionality audit</span>
        <a href={REPO_URL} target="_blank" rel="noreferrer">GitHub repo</a>
      </div>
      <div className="coverage-table mt-3">
        <div className="coverage-row coverage-head">
          <span>Stage</span>
          <span>What the UI must expose</span>
          <span>Code path checked</span>
          <span>Action</span>
        </div>
        {rows.map(([stage, capability, code, tab]) => (
          <div key={`${stage}-${capability}`} className="coverage-row">
            <span className="coverage-stage">{stage}</span>
            <span>{capability}</span>
            <span className="font-mono-data">{code}</span>
            <button type="button" onClick={() => onNavigate(tab)}>Open</button>
          </div>
        ))}
      </div>
    </section>
  );
}

function NarrativesView({
  narratives,
  onNarrativesParsed,
  onRemove,
  onClear,
}: {
  narratives: ParsedNarrative[];
  onNarrativesParsed: (n: ParsedNarrative[]) => void;
  onRemove: (id: string) => void;
  onClear: () => void;
}) {
  const { mode } = useNIDMMode();
  const explainer = {
    novice: "Add narratives from field reports, interviews, or policy briefs, then score the signals that affect household adoption.",
    policy: "Narrative coding turns qualitative evidence into policy-ready model parameters for Rwanda clean-cooking strategy.",
    expert: "Encoding maps narratives into exposure, credibility, trust, and inoculation features used by Phi and the ODE system.",
  }[mode];

  return (
    <div className="animate-page-in space-y-8">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>{explainer}</section>
      <FileUploadPanel onNarrativesParsed={onNarrativesParsed} />
      <LLMEncodingWorkbench narratives={narratives} />
      <NarrativeEncodingPanel onNarrativeAdd={(narrative) => onNarrativesParsed([narrative])} />
      <NarrativeLibrary narratives={narratives} onRemove={onRemove} onClear={onClear} />
      <ModelAuditBridge />
    </div>
  );
}

function LLMEncodingWorkbench({ narratives }: { narratives: ParsedNarrative[] }) {
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const [encoded, setEncoded] = useState<BackendEncodedNarrative[]>([]);
  const [note, setNote] = useState("Backend encoder has not been run in this browser session.");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "agent" | "user"; content: string }>>([
    {
      role: "agent",
      content:
        "Load narratives, then run backend encoding. I will report whether the OpenAI path or fallback path produced the scores.",
    },
  ]);

  async function runEncoding() {
    if (!narratives.length) {
      setStatus("error");
      setNote("No narratives loaded. Upload or paste evidence before running LLM encoding.");
      return;
    }

    setStatus("running");
    setNote("Calling backend /encode with NarrativeRecord payload.");

    try {
      const response = await fetch(`${BACKEND_URL}/encode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toBackendRecords(narratives)),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = (await response.json()) as BackendEncodedNarrative[];
      setEncoded(data);
      setStatus("complete");
      const mode = data.some((item) => item.encoding_mode === "ai") ? "OpenAI LLM encoding" : "fallback rule-based encoding";
      setNote(`${mode} returned ${data.length} encoded narrative${data.length === 1 ? "" : "s"}.`);
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: `${mode} completed. Review themes, trust, barrier, and confidence before modelling.` },
      ]);
    } catch (error) {
      setStatus("error");
      setNote(
        error instanceof Error
          ? `Backend encoder unavailable: ${error.message}`
          : "Backend encoder unavailable."
      );
    }
  }

  function sendQuestion() {
    const trimmed = question.trim();
    if (!trimmed) return;

    const top = narratives.length
      ? [...narratives].sort((a, b) => b.phi - a.phi)[0]
      : null;
    const response = top
      ? `Current library has ${narratives.length} narrative${narratives.length === 1 ? "" : "s"}. The strongest Phi signal is "${top.label}" at ${top.phi.toFixed(3)}. Run backend encoding to compare this heuristic Phi score with the LLM/fallback encoder themes.`
      : "No narratives are loaded yet. Start with the upload and SDMX gate, then I can summarize the strongest evidence signals.";

    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmed },
      { role: "agent", content: response },
    ]);
    setQuestion("");
  }

  return (
    <section className="agentic-panel">
      <div className="agentic-header">
        <div>
          <p className="eyebrow">LLM encoding workbench</p>
          <h3>Score narratives before they influence the model.</h3>
          <p>
            The backend uses OpenAI when `OPENAI_API_KEY` is configured and otherwise returns a transparent fallback score.
          </p>
        </div>
        <div className={`status-pill ${status}`}>
          {status === "complete" ? <CheckCircle2 className="h-4 w-4" /> : status === "error" ? <AlertTriangle className="h-4 w-4" /> : <Cpu className="h-4 w-4" />}
          {status}
        </div>
      </div>

      <div className="encoding-layout">
        <div>
          <div className="agent-actions mb-3">
            <button type="button" className="button-primary" onClick={runEncoding} disabled={status === "running"}>
              <Brain className="h-4 w-4" />
              {status === "running" ? "Encoding" : "Run backend encoding"}
            </button>
            <span className="font-mono-data text-xs text-[var(--t3)]">{narratives.length} loaded</span>
          </div>
          <p className="encoder-note">{note}</p>

          <div className="encoding-table">
            <div className="encoding-row encoding-head">
              <span>ID</span>
              <span>Mode</span>
              <span>Themes</span>
              <span>Trust</span>
              <span>Barrier</span>
              <span>Confidence</span>
            </div>
            {encoded.length ? (
              encoded.map((item) => (
                <div key={item.narrative_id} className="encoding-row">
                  <span className="truncate">{item.narrative_id}</span>
                  <span>{item.encoding_mode}</span>
                  <span>{item.themes?.join(", ") || "general"}</span>
                  <span>{typeof item.trust_score === "number" ? item.trust_score.toFixed(2) : "-"}</span>
                  <span>{typeof item.adoption_barrier_score === "number" ? item.adoption_barrier_score.toFixed(2) : "-"}</span>
                  <span>{typeof item.confidence === "number" ? item.confidence.toFixed(2) : "-"}</span>
                </div>
              ))
            ) : (
              <div className="encoding-empty">No backend encoding results yet.</div>
            )}
          </div>
        </div>

        <div className="agent-chat">
          <div className="section-heading">
            <span>Encoding agent</span>
            <span>public summary</span>
          </div>
          <div className="chat-log">
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>
                <span>{message.role === "agent" ? "agent" : "you"}</span>
                <p>{message.content}</p>
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendQuestion();
              }}
              placeholder="Ask what evidence signal is strongest..."
            />
            <button type="button" onClick={sendQuestion}>Send</button>
          </div>
        </div>
      </div>
    </section>
  );
}

function SimulationView({ simulationData }: { simulationData: SimulationDataPoint[] }) {
  const { mode } = useNIDMMode();
  const explainer = {
    novice: "Press play to see households move between belief states over time.",
    policy: "Use the playhead to inspect when misinformation peaks and when truth adoption becomes durable.",
    expert: "The animated line chart exposes S, M, T, I, and R trajectories with a time-indexed reference line.",
  }[mode];

  return (
    <div className="animate-page-in space-y-8">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>{explainer}</section>
      <SimulationPlayer fullData={simulationData} />
    </div>
  );
}
