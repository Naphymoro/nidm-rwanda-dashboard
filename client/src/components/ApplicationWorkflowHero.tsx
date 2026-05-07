import React from "react";
import {
  ArrowRight,
  Bot,
  Database,
  GitCompare,
  MessageSquareText,
  Network,
  Play,
  ShieldCheck,
  Sigma,
  UsersRound,
} from "lucide-react";
import { useNIDMMode } from "@/components/DashboardLayout";

type WorkflowHeroProps = {
  onNavigate: (tab: string) => void;
};

const WORKFLOW_STEPS = [
  {
    tab: "narratives",
    label: "Load evidence",
    detail: "CSV, text, field notes, SDMX",
    icon: Database,
    accent: "var(--gold)",
  },
  {
    tab: "narratives",
    label: "Validate gate",
    detail: "SDMX-NIDM input/output contract",
    icon: ShieldCheck,
    accent: "var(--sky)",
  },
  {
    tab: "ode",
    label: "Encode Phi",
    detail: "Narrative force into equations",
    icon: Sigma,
    accent: "var(--violet)",
  },
  {
    tab: "simulation",
    label: "Simulate flow",
    detail: "S, M, T, I, R population states",
    icon: Play,
    accent: "var(--verdant)",
  },
  {
    tab: "agents",
    label: "Run ABM",
    detail: "Households, peers, media, districts",
    icon: UsersRound,
    accent: "var(--indigoL)",
  },
  {
    tab: "rl",
    label: "Optimize policy",
    detail: "Scenario comparison and RL actions",
    icon: Bot,
    accent: "var(--flame)",
  },
];

const FEEDBACKS = [
  {
    label: "Field feedback",
    value: "Narratives and survey signals update the evidence library.",
    icon: MessageSquareText,
    accent: "var(--gold)",
  },
  {
    label: "Model feedback",
    value: "ODE and ABM deltas expose where assumptions drift.",
    icon: Network,
    accent: "var(--sky)",
  },
  {
    label: "Decision feedback",
    value: "Scenario winners and RL rewards feed the next intervention cycle.",
    icon: GitCompare,
    accent: "var(--verdant)",
  },
];

export default function ApplicationWorkflowHero({ onNavigate }: WorkflowHeroProps) {
  const { mode } = useNIDMMode();
  const copy = {
    novice:
      "Follow evidence from raw story to model result. Each step shows what the tool is doing and where feedback returns.",
    policy:
      "A decision workflow for clean-cooking adoption: evidence enters once, then simulation, ABM, scenarios, and feedback keep the policy loop accountable.",
    expert:
      "Trace SDMX-normalized narrative observations through Phi, ODE population flow, ABM micro-dynamics, scenario comparison, and RL reward feedback.",
  }[mode];

  return (
    <section className="nidm-card overflow-hidden">
      <div className="grid gap-0 xl:grid-cols-[.92fr_1.08fr]">
        <div className="border-b border-[var(--bdr)] p-6 xl:border-b-0 xl:border-r">
          <p className="font-mono-data text-[10px] uppercase tracking-[1.7px] text-[var(--t4)]">
            NIDM Rwanda workflow
          </p>
          <h1 className="font-syne mt-3 max-w-3xl text-3xl font-bold leading-tight text-[var(--t1)] md:text-5xl">
            Evidence to adoption intelligence
          </h1>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-[var(--t2)]">{copy}</p>

          <div className="mt-6 flex flex-wrap gap-2">
            <HeroButton label="Load narratives" tab="narratives" accent="var(--gold)" onNavigate={onNavigate} />
            <HeroButton label="Run simulation" tab="simulation" accent="var(--verdant)" onNavigate={onNavigate} />
            <HeroButton label="Open ABM" tab="agents" accent="var(--indigoL)" onNavigate={onNavigate} />
            <HeroButton label="Review feedback" tab="twin" accent="var(--sky)" onNavigate={onNavigate} />
          </div>
        </div>

        <div className="p-5">
          <div className="grid gap-3 lg:grid-cols-3 xl:grid-cols-2 2xl:grid-cols-3">
            {WORKFLOW_STEPS.map((step, index) => {
              const Icon = step.icon;
              return (
                <button
                  key={`${step.label}-${index}`}
                  type="button"
                  onClick={() => onNavigate(step.tab)}
                  className="group relative rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4 text-left transition hover:-translate-y-0.5 hover:border-[var(--bdrV)]"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span
                      className="flex h-8 w-8 items-center justify-center rounded-lg"
                      style={{ color: step.accent, background: `color-mix(in srgb, ${step.accent} 15%, transparent)` }}
                    >
                      <Icon className="h-4 w-4" />
                    </span>
                    <span className="font-mono-data text-[10px] text-[var(--t4)]">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </div>
                  <h2 className="font-syne text-sm font-bold text-[var(--t1)]">{step.label}</h2>
                  <p className="mt-1 text-xs leading-5 text-[var(--t3)]">{step.detail}</p>
                  <ArrowRight className="absolute bottom-4 right-4 h-3.5 w-3.5 text-[var(--t4)] opacity-0 transition group-hover:opacity-100" />
                </button>
              );
            })}
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            {FEEDBACKS.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-lg border border-[var(--bdr)] bg-[rgba(255,255,255,.025)] p-3">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" style={{ color: item.accent }} />
                    <span className="font-mono-data text-[10px] uppercase tracking-[1px] text-[var(--t4)]">
                      {item.label}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-[var(--t3)]">{item.value}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function HeroButton({
  label,
  tab,
  accent,
  onNavigate,
}: {
  label: string;
  tab: string;
  accent: string;
  onNavigate: (tab: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onNavigate(tab)}
      className="rounded-lg border px-3 py-2 text-xs font-semibold transition hover:-translate-y-0.5"
      style={{
        color: accent,
        borderColor: `color-mix(in srgb, ${accent} 38%, transparent)`,
        background: `color-mix(in srgb, ${accent} 11%, transparent)`,
      }}
    >
      {label}
    </button>
  );
}
