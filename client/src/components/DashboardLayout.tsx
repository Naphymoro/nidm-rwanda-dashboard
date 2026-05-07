import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Bot,
  Brain,
  ClipboardCheck,
  GitCompare,
  LayoutDashboard,
  Moon,
  Network,
  Play,
  SlidersHorizontal,
  Sun,
  Upload,
  UsersRound,
  Workflow,
} from "lucide-react";

export type NIDMMode = "novice" | "policy" | "expert";
type NIDMTheme = "dark" | "light";

type NIDMModeContextValue = {
  mode: NIDMMode;
  setMode: (mode: NIDMMode) => void;
};

const NIDMModeContext = createContext<NIDMModeContextValue>({
  mode: "policy",
  setMode: () => undefined,
});

export function useNIDMMode() {
  return useContext(NIDMModeContext);
}

function getInitialTheme(): NIDMTheme {
  if (typeof window === "undefined") return "dark";
  try {
    return window.localStorage.getItem("nidm-theme") === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

type TabInput = {
  id: string;
  label: string;
  icon?: React.ReactNode;
};

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  tabs?: TabInput[];
}

type NavItem = {
  id: string;
  label: string;
  sub: string;
  section: "model" | "analysis" | "decision";
  accent: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
};

const NAV_ITEMS: NavItem[] = [
  {
    id: "dashboard",
    label: "Overview",
    sub: "system state",
    section: "model",
    accent: "var(--indigo)",
    icon: LayoutDashboard,
    description: "Rwanda clean-cooking NIDM overview and headline performance signals.",
  },
  {
    id: "narratives",
    label: "Narratives",
    sub: "encoding",
    section: "model",
    accent: "var(--gold)",
    icon: Brain,
    description: "Narrative ingestion, SDMX gating, scoring, and library management for model inputs.",
  },
  {
    id: "ode",
    label: "ODE System",
    sub: "equations",
    section: "model",
    accent: "var(--sky)",
    icon: Workflow,
    description: "Differential equations, parameters, reproduction numbers, and compartments.",
  },
  {
    id: "agents",
    label: "Agent Model",
    sub: "households",
    section: "model",
    accent: "var(--indigoL)",
    icon: UsersRound,
    description: "Agent-based modelling for household behavior, peer effects, field outreach, and local feedback.",
  },
  {
    id: "simulation",
    label: "Simulation",
    sub: "trajectories",
    section: "analysis",
    accent: "var(--verdant)",
    icon: BarChart3,
    description: "Animated Susceptible, Misinformed, Truth, Inoculated, and Resistant trajectories.",
  },
  {
    id: "scenarios",
    label: "Scenarios",
    sub: "competition",
    section: "analysis",
    accent: "var(--violet)",
    icon: GitCompare,
    description: "Compare narrative strategies and identify the strongest policy scenario.",
  },
  {
    id: "sensitivity",
    label: "Sensitivity",
    sub: "stress test",
    section: "analysis",
    accent: "var(--flame)",
    icon: SlidersHorizontal,
    description: "Probe parameter uncertainty and rank the most sensitive model levers.",
  },
  {
    id: "twin",
    label: "Digital Twin",
    sub: "feedback",
    section: "decision",
    accent: "var(--verdant)",
    icon: Network,
    description: "Live architecture view linking narratives, field data, the model, and policy feedback.",
  },
  {
    id: "rl",
    label: "RL Optimizer",
    sub: "q-learning",
    section: "decision",
    accent: "var(--indigo)",
    icon: Bot,
    description: "Train a policy optimizer that searches for high-reward narrative interventions.",
  },
];

const MODE_COPY: Record<NIDMMode, string> = {
  novice: "Plain-language explanations are expanded across cards.",
  policy: "Policy implications, risk flags, and decision relevance are emphasized.",
  expert: "Mathematical notation, parameters, and diagnostics are shown with minimal simplification.",
};

const SECTION_LABELS: Record<NavItem["section"], string> = {
  model: "Model",
  analysis: "Analysis",
  decision: "Decision",
};

const VERCEL_URL = "https://nidm-rwanda-dashboard.vercel.app";
const REPO_URL = "https://github.com/Naphymoro/nidm-rwanda-dashboard";

const PIPELINE_STAGES = [
  { step: "01", id: "narratives", label: "Narrative upload", output: "Evidence ledger" },
  { step: "02", id: "narratives", label: "SDMX gate", output: "Validated observations" },
  { step: "03", id: "narratives", label: "Narrative encoding", output: "Phi features" },
  { step: "04", id: "ode", label: "ODE model", output: "Population flow" },
  { step: "05", id: "agents", label: "Agent model", output: "Household dynamics" },
  { step: "06", id: "scenarios", label: "Scenario test", output: "Policy tradeoffs" },
  { step: "07", id: "rl", label: "Policy output", output: "Decision brief" },
];

const ENDPOINT_LABELS: Record<string, string> = {
  dashboard: "/workbench/overview",
  narratives: "/evidence/narratives",
  ode: "/models/ode",
  agents: "/models/abm",
  simulation: "/simulation/run",
  scenarios: "/policy/scenarios",
  sensitivity: "/diagnostics/sensitivity",
  twin: "/digital-twin/feedback",
  rl: "/optimizer/rl",
};

const NEXT_STAGE: Record<string, string> = {
  dashboard: "narratives",
  narratives: "ode",
  ode: "agents",
  agents: "scenarios",
  simulation: "scenarios",
  scenarios: "sensitivity",
  sensitivity: "twin",
  twin: "rl",
  rl: "rl",
};

function getPipelineIndex(activeTab: string) {
  if (activeTab === "dashboard") return -1;
  if (activeTab === "sensitivity") return 5;
  if (activeTab === "simulation") return 3;
  if (activeTab === "twin") return 6;
  const index = PIPELINE_STAGES.findIndex((stage) => stage.id === activeTab);
  return index >= 0 ? index : -1;
}

export default function DashboardLayout({
  children,
  activeTab = "dashboard",
  onTabChange,
  tabs,
}: DashboardLayoutProps) {
  const [mode, setMode] = useState<NIDMMode>("policy");
  const [theme, setTheme] = useState<NIDMTheme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.classList.toggle("dark", theme === "dark");
    try {
      window.localStorage.setItem("nidm-theme", theme);
    } catch {
      // Theme still applies even if storage is unavailable.
    }
  }, [theme]);

  const navItems = useMemo(() => {
    const requestedIds = new Set((tabs ?? []).map((tab) => tab.id));
    const customItems: NavItem[] = (tabs ?? [])
      .filter((tab) => !NAV_ITEMS.some((item) => item.id === tab.id))
      .map((tab) => ({
        id: tab.id,
        label: tab.label,
        sub: "custom",
        section: "decision" as const,
        accent: "var(--indigoL)",
        icon: Activity,
        description: `${tab.label} workspace.`,
      }));

    const coreItems = NAV_ITEMS.filter((item) => requestedIds.size === 0 || requestedIds.has(item.id) || ["ode", "agents", "scenarios", "sensitivity", "rl"].includes(item.id));
    return [...coreItems, ...customItems];
  }, [tabs]);

  const activeItem = navItems.find((item) => item.id === activeTab) ?? NAV_ITEMS[0];
  const endpoint = ENDPOINT_LABELS[activeItem.id] ?? "/workbench/custom";
  const activePipelineIndex = getPipelineIndex(activeItem.id);

  function handleRunWorkflow() {
    const nextStage = NEXT_STAGE[activeItem.id] ?? "narratives";
    if (activeItem.id === "rl") {
      return;
    }
    onTabChange?.(nextStage);
  }

  return (
    <NIDMModeContext.Provider value={{ mode, setMode }}>
      <div className="nidm-shell">
        <aside className="nidm-sidebar">
          <div className="flex h-[58px] items-center gap-3 border-b border-[var(--bdr)] px-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(59,91,219,.18)] text-[var(--indigoL)]">
              <ClipboardCheck className="h-4 w-4" />
            </div>
            <div className="sidebar-copy min-w-0">
              <div className="font-syne text-[15px] font-bold leading-none text-[var(--t1)]">NIDM</div>
              <div className="font-mono-data mt-1 text-[9px] uppercase tracking-[1.4px] text-[var(--t4)]">Evidence workbench</div>
            </div>
          </div>

          <div className="control-section mx-3 mt-3">
            <div className="section-heading">
              <span>Workbench cards</span>
              <a href={REPO_URL} target="_blank" rel="noreferrer">Repo</a>
            </div>
            <p className="section-copy">
              Start with narrative upload, validate evidence, run scientific models, then produce a policy readout.
            </p>
          </div>

          <div className="pipeline-panel mx-3 mt-3">
            <div className="section-heading">
              <span>Scientific run</span>
              <span>start to output</span>
            </div>
            <button type="button" className="pipeline-start" onClick={() => onTabChange?.("narratives")}>
              <Upload className="h-4 w-4" />
              Start with narrative upload
            </button>
            <div className="pipeline-steps">
              {PIPELINE_STAGES.map((stage, index) => {
                const isActive = activePipelineIndex === index;
                const isDone = activePipelineIndex > index;
                return (
                  <button
                    key={`${stage.step}-${stage.label}`}
                    type="button"
                    className={`pipeline-step ${isActive ? "active" : ""} ${isDone ? "done" : ""}`}
                    onClick={() => onTabChange?.(stage.id)}
                  >
                    <span>{stage.step}</span>
                    <strong>{stage.label}</strong>
                    <em>{stage.output}</em>
                  </button>
                );
              })}
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto px-3 py-3">
            {(Object.keys(SECTION_LABELS) as Array<NavItem["section"]>).map((section) => {
              const sectionItems = navItems.filter((item) => item.section === section);
              if (!sectionItems.length) return null;

              return (
                <div key={section} className="mb-4">
                  <div className="section-label">{SECTION_LABELS[section]}</div>
                  <div className="space-y-1">
                    {sectionItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = item.id === activeItem.id;

                      return (
                        <button
                          key={item.id}
                          type="button"
                          className={`nidm-nav-item ${isActive ? "active" : ""}`}
                          onClick={() => onTabChange?.(item.id)}
                          title={item.label}
                        >
                          <span
                            className="nidm-nav-icon"
                            style={{
                              color: item.accent,
                              background: `color-mix(in srgb, ${item.accent} 16%, transparent)`,
                            }}
                          >
                            <Icon className="h-4 w-4" />
                          </span>
                          <span className="sidebar-copy min-w-0">
                            <span className="nidm-nav-label block">{item.label}</span>
                            <span className="nidm-nav-sub block">{item.sub}</span>
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </nav>

          <div className="space-y-3 border-t border-[var(--bdr)] p-3">
            <div className="sidebar-copy">
              <div className="section-label px-0 pt-0">Mode</div>
              <div className="mode-toggle">
                {(["novice", "policy", "expert"] as NIDMMode[]).map((item) => (
                  <button
                    key={item}
                    type="button"
                    className={`mode-btn ${mode === item ? "active" : ""}`}
                    onClick={() => setMode(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-[11px] leading-5 text-[var(--t3)]">{MODE_COPY[mode]}</p>
            </div>
            <div className="sidebar-copy">
              <div className="section-label px-0 pt-0">Theme</div>
              <div className="theme-toggle">
                <button
                  type="button"
                  className={`theme-btn ${theme === "dark" ? "active" : ""}`}
                  onClick={() => setTheme("dark")}
                  aria-pressed={theme === "dark"}
                >
                  <Moon className="h-3.5 w-3.5" />
                  Dark
                </button>
                <button
                  type="button"
                  className={`theme-btn ${theme === "light" ? "active" : ""}`}
                  onClick={() => setTheme("light")}
                  aria-pressed={theme === "light"}
                >
                  <Sun className="h-3.5 w-3.5" />
                  Light
                </button>
              </div>
            </div>
            <a
              className="sidebar-url font-mono-data block truncate rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2 text-[10px] text-[var(--indigoL)] transition hover:border-[var(--bdrV)]"
              href={VERCEL_URL}
              target="_blank"
              rel="noreferrer"
            >
              {VERCEL_URL}
            </a>
            <a
              className="sidebar-url font-mono-data block truncate rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2 text-[10px] text-[var(--verdant)] transition hover:border-[var(--bdrV)]"
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
            >
              GitHub source
            </a>
          </div>
        </aside>

        <section className="setup-panel min-w-0">
          <header className="nidm-topbar">
            <div className="min-w-0">
              <p className="eyebrow">Workflow setup</p>
              <div className="topbar-title">{activeItem.label}</div>
              <div className="topbar-sub">{activeItem.description}</div>
            </div>
            <div className="setup-meta">
              <span className="endpoint-label">{endpoint}</span>
              <button
                type="button"
                onClick={handleRunWorkflow}
                className="button-primary"
              >
                {activeItem.id === "dashboard" ? <ArrowRight className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                <span>{activeItem.id === "dashboard" ? "Start run" : "Run stage"}</span>
              </button>
            </div>
          </header>

          <main className="workbench-content">
            {children}
          </main>
        </section>

      </div>
    </NIDMModeContext.Provider>
  );
}
