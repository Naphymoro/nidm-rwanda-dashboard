import React from "react";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  Calculator,
  Database,
  ShieldCheck,
  UsersRound,
  Workflow,
} from "lucide-react";
import { useNIDMMode } from "@/components/DashboardLayout";

const MODE_COPY = {
  novice:
    "This bridge shows how plain-language evidence becomes model inputs, then adoption trajectories.",
  policy:
    "The audit path keeps evidence, SDMX exchange, model parameters, and policy outputs traceable for review.",
  expert:
    "Pipeline trace: narrative encoder -> SDMX-NIDM observations -> Phi -> S/M/T/I/R ODE rates -> ABM agents -> simulation/RL reward.",
} as const;

const STEPS = [
  {
    label: "Narrative/LLM encoder",
    detail: "Paragraphs, transcripts, or CSV rows are scored into E, C, tau, and kappa.",
    accent: "var(--gold)",
    icon: BrainCircuit,
  },
  {
    label: "SDMX gate",
    detail: "Input and output are normalized as narrative observations with dimensions and measures.",
    accent: "var(--sky)",
    icon: ShieldCheck,
  },
  {
    label: "Phi calculation",
    detail: "Weighted narrative strength becomes a model lever for truth adoption and inoculation.",
    accent: "var(--violet)",
    icon: Calculator,
  },
  {
    label: "Compartmental model",
    detail: "S, M, T, I, and R trajectories update through the ODE system.",
    accent: "var(--verdant)",
    icon: Workflow,
  },
  {
    label: "Agent-based model",
    detail: "Household agents test peer influence, trust thresholds, and intervention reach.",
    accent: "var(--sky)",
    icon: UsersRound,
  },
  {
    label: "Decision agents",
    detail: "Scenario comparison and RL training search for stronger intervention policies.",
    accent: "var(--indigoL)",
    icon: Bot,
  },
];

export default function ModelAuditBridge() {
  const { mode } = useNIDMMode();

  return (
    <section className="nidm-card p-5">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono-data text-[10px] uppercase tracking-[1.5px] text-[var(--t4)]">
            Model audit bridge
          </p>
          <h3 className="font-syne mt-1 text-xl font-bold">LLM evidence to compartmental dynamics</h3>
          <p className="mt-2 max-w-3xl text-sm text-[var(--t3)]">{MODE_COPY[mode]}</p>
        </div>
        <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3">
          <div className="flex items-center gap-2 text-[var(--indigoL)]">
            <Database className="h-4 w-4" />
            <span className="font-mono-data text-[10px] uppercase tracking-[1px]">Traceable</span>
          </div>
          <p className="mt-1 text-xs text-[var(--t3)]">Every accepted batch can emit SDMX-NIDM JSON.</p>
        </div>
      </div>

      <div className="grid gap-3 xl:grid-cols-6">
        {STEPS.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={step.label} className="relative rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4">
              <div
                className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg"
                style={{ color: step.accent, background: `color-mix(in srgb, ${step.accent} 15%, transparent)` }}
              >
                <Icon className="h-4 w-4" />
              </div>
              <h4 className="font-syne text-sm font-bold text-[var(--t1)]">{step.label}</h4>
              <p className="mt-2 text-xs leading-5 text-[var(--t3)]">{step.detail}</p>
              {index < STEPS.length - 1 && (
                <ArrowRight className="absolute right-3 top-4 hidden h-4 w-4 text-[var(--t4)] xl:block" />
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
