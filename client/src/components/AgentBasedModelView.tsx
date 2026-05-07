import React, { CSSProperties, useMemo, useState } from "react";
import {
  Activity,
  Brain,
  Network,
  Play,
  RotateCcw,
  UsersRound,
  Wifi,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import KPICard from "./KPICard";
import { useNIDMMode } from "./DashboardLayout";

type AgentState = "S" | "M" | "T" | "I" | "R";
type ParameterKey = "households" | "peerInfluence" | "trustThreshold" | "fieldWorkerReach" | "misinfoSeed";

type Agent = {
  id: number;
  district: string;
  state: AgentState;
  trust: number;
  media: number;
  peers: number;
};

type TracePoint = {
  day: number;
  truth: number;
  misinformed: number;
  inoculated: number;
  resistant: number;
  adoption: number;
};

const STATE_META: Record<AgentState, { label: string; color: string; description: string }> = {
  S: { label: "Susceptible", color: "var(--cS)", description: "Undecided household" },
  M: { label: "Misinformed", color: "var(--cM)", description: "Exposed to adoption barrier narrative" },
  T: { label: "Truth", color: "var(--cT)", description: "Persuaded by trusted clean-cooking narrative" },
  I: { label: "Inoculated", color: "var(--cI)", description: "Prepared against misinformation" },
  R: { label: "Resistant", color: "var(--cR)", description: "Durable adoption belief" },
};

const DISTRICTS = ["Kigali", "Musanze", "Huye", "Rubavu", "Nyagatare", "Rusizi"];

const PARAMS: Record<ParameterKey, { label: string; min: number; max: number; step: number; accent: string }> = {
  households: { label: "households", min: 60, max: 420, step: 20, accent: "var(--indigoL)" },
  peerInfluence: { label: "peer influence", min: 0.05, max: 0.9, step: 0.01, accent: "var(--sky)" },
  trustThreshold: { label: "trust threshold", min: 0.1, max: 0.95, step: 0.01, accent: "var(--gold)" },
  fieldWorkerReach: { label: "field worker reach", min: 0.05, max: 0.8, step: 0.01, accent: "var(--verdant)" },
  misinfoSeed: { label: "misinformation seed", min: 0.02, max: 0.5, step: 0.01, accent: "var(--flame)" },
};

function seededNoise(index: number) {
  const value = Math.sin(index * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

function initialAgents(count: number, misinfoSeed: number): Agent[] {
  return Array.from({ length: count }, (_, index) => {
    const trust = seededNoise(index + 4);
    const media = seededNoise(index + 13);
    const peers = Math.floor(seededNoise(index + 22) * 8) + 2;
    const m = seededNoise(index + 31) < misinfoSeed;
    const i = !m && seededNoise(index + 44) < 0.1;
    return {
      id: index,
      district: DISTRICTS[index % DISTRICTS.length],
      state: m ? "M" : i ? "I" : "S",
      trust,
      media,
      peers,
    };
  });
}

function transitionAgents(
  agents: Agent[],
  params: Record<ParameterKey, number>,
  day: number
): Agent[] {
  const counts = countStates(agents);
  const truthPressure = (counts.T + counts.R + params.fieldWorkerReach * agents.length * 0.55) / agents.length;
  const misinfoPressure = (counts.M + params.misinfoSeed * agents.length * 0.35) / agents.length;

  return agents.map((agent) => {
    const localNoise = seededNoise(agent.id * 17 + day * 7);
    const peerLift = params.peerInfluence * truthPressure * (agent.peers / 10);
    const trustSignal = agent.trust * 0.48 + agent.media * 0.16 + params.fieldWorkerReach * 0.28 + peerLift;
    const misinformationSignal = misinfoPressure * (1 - agent.trust * 0.45) + localNoise * 0.09;
    let state = agent.state;

    if (state === "S") {
      if (misinformationSignal > trustSignal + params.trustThreshold * 0.22) state = "M";
      else if (trustSignal > params.trustThreshold) state = "T";
      else if (params.fieldWorkerReach + localNoise * 0.2 > 0.76) state = "I";
    } else if (state === "M") {
      if (trustSignal + params.fieldWorkerReach * 0.25 > misinformationSignal + 0.22) state = "T";
    } else if (state === "T") {
      if (params.fieldWorkerReach + peerLift > 0.62) state = "I";
      else if (misinformationSignal > trustSignal + 0.24) state = "M";
    } else if (state === "I") {
      if (trustSignal + peerLift > 0.78) state = "R";
    }

    return {
      ...agent,
      state,
      trust: Math.max(0, Math.min(1, agent.trust + (state === "T" || state === "R" ? 0.018 : 0.002))),
    };
  });
}

function countStates(agents: Agent[]) {
  return agents.reduce<Record<AgentState, number>>(
    (acc, agent) => {
      acc[agent.state] += 1;
      return acc;
    },
    { S: 0, M: 0, T: 0, I: 0, R: 0 }
  );
}

function traceFromAgents(agents: Agent[], day: number): TracePoint {
  const counts = countStates(agents);
  const total = Math.max(1, agents.length);
  return {
    day,
    truth: counts.T / total,
    misinformed: counts.M / total,
    inoculated: counts.I / total,
    resistant: counts.R / total,
    adoption: (counts.T + counts.I + counts.R) / total,
  };
}

function runSimulation(params: Record<ParameterKey, number>) {
  let agents = initialAgents(params.households, params.misinfoSeed);
  const trace: TracePoint[] = [traceFromAgents(agents, 0)];
  const snapshots: Agent[][] = [agents];

  for (let day = 1; day <= 60; day += 1) {
    agents = transitionAgents(agents, params, day);
    trace.push(traceFromAgents(agents, day));
    if (day % 10 === 0 || day === 60) snapshots.push(agents);
  }

  return { agents, trace, snapshots };
}

function pct(value: number, min: number, max: number) {
  return ((value - min) / (max - min)) * 100;
}

export default function AgentBasedModelView() {
  const { mode } = useNIDMMode();
  const [params, setParams] = useState<Record<ParameterKey, number>>({
    households: 180,
    peerInfluence: 0.42,
    trustThreshold: 0.56,
    fieldWorkerReach: 0.34,
    misinfoSeed: 0.18,
  });
  const [runId, setRunId] = useState(1);

  const result = useMemo(() => runSimulation(params), [params, runId]);
  const counts = countStates(result.agents);
  const total = result.agents.length;
  const last = result.trace[result.trace.length - 1];
  const first = result.trace[0];
  const adoptionLift = (last.adoption - first.adoption) * 100;

  const explainer = {
    novice:
      "This view looks at households one by one. Each household reacts to trust, peers, field workers, and misinformation, then the population result emerges.",
    policy:
      "Use ABM to test whether a strategy works evenly across districts and social networks, not only in the aggregate compartment chart.",
    expert:
      "The ABM layer approximates heterogeneous agents with trust, media exposure, peer degree, local misinformation pressure, and field-worker intervention reach.",
  }[mode];

  function rerun() {
    setRunId((value) => value + 1);
  }

  function reset() {
    setParams({
      households: 180,
      peerInfluence: 0.42,
      trustThreshold: 0.56,
      fieldWorkerReach: 0.34,
      misinfoSeed: 0.18,
    });
    setRunId((value) => value + 1);
  }

  return (
    <div className="animate-page-in space-y-6">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>{explainer}</section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <KPICard
          label="Household agents"
          value={total}
          icon={<UsersRound className="h-5 w-5" />}
          glowColor="primary"
          precision={0}
        />
        <KPICard
          label="Adoption lift"
          value={adoptionLift}
          unit="pp"
          trend={adoptionLift >= 0 ? "up" : "down"}
          trendValue={Math.abs(adoptionLift)}
          icon={<Activity className="h-5 w-5" />}
          glowColor="secondary"
          precision={1}
        />
        <KPICard
          label="Misinformed final"
          value={(counts.M / total) * 100}
          unit="%"
          trend="neutral"
          icon={<Wifi className="h-5 w-5" />}
          glowColor="chart-2"
          precision={1}
        />
        <KPICard
          label="Resistant final"
          value={(counts.R / total) * 100}
          unit="%"
          trend="up"
          trendValue={(counts.R / total) * 100}
          icon={<Brain className="h-5 w-5" />}
          glowColor="accent"
          precision={1}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <section className="nidm-card p-5">
          <div className="mb-5 flex items-start justify-between gap-3">
            <div>
              <p className="font-mono-data text-[10px] uppercase tracking-[1.5px] text-[var(--t4)]">
                Agent-based model
              </p>
              <h2 className="font-syne mt-1 text-lg font-bold">Agent-based modelling flow</h2>
            </div>
            <span className="page-badge border border-[rgba(116,143,252,.28)] bg-[rgba(116,143,252,.08)] text-[var(--indigoL)]">
              run {runId}
            </span>
          </div>

          <div className="space-y-5">
            {(Object.keys(PARAMS) as ParameterKey[]).map((key) => {
              const meta = PARAMS[key];
              const value = params[key];
              return (
                <label key={key} className="block">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <span className="font-mono-data text-xs text-[var(--t2)]">{meta.label}</span>
                    <span className="font-mono-data text-xs" style={{ color: meta.accent }}>
                      {key === "households" ? value.toFixed(0) : value.toFixed(2)}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={meta.min}
                    max={meta.max}
                    step={meta.step}
                    value={value}
                    onChange={(event) => setParams((current) => ({ ...current, [key]: Number(event.target.value) }))}
                    style={{ "--pct": `${pct(value, meta.min, meta.max)}%`, "--indigoL": meta.accent } as CSSProperties}
                  />
                </label>
              );
            })}
          </div>

          <div className="mt-6 flex gap-2">
            <button
              type="button"
              onClick={rerun}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-[rgba(32,201,151,.35)] bg-[rgba(32,201,151,.13)] px-3 py-2 text-sm font-semibold text-[var(--verdant)] transition hover:bg-[rgba(32,201,151,.18)]"
            >
              <Play className="h-4 w-4" />
              Re-run ABM
            </button>
            <button
              type="button"
              onClick={reset}
              className="flex items-center justify-center rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2 text-[var(--t2)] transition hover:border-[var(--bdrV)]"
              title="Reset ABM parameters"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-5 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3">
            <p className="font-mono-data text-[10px] uppercase tracking-[1.3px] text-[var(--t4)]">
              Local transition rule
            </p>
            <p className="mt-2 text-xs leading-5 text-[var(--t3)]">
              A household changes state when trust plus peer influence and field-worker reach
              exceeds its threshold. Misinformation can reverse weak truth states unless the
              household is inoculated or resistant.
            </p>
          </div>
        </section>

        <section className="nidm-card p-5">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-syne text-lg font-bold">Agent state lattice</h2>
              <p className="mt-1 text-xs text-[var(--t3)]">
                Each dot is a household agent; color shows its final belief/adoption state.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {(Object.keys(STATE_META) as AgentState[]).map((state) => (
                <span key={state} className="font-mono-data text-[10px]" style={{ color: STATE_META[state].color }}>
                  {state} {counts[state]}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4">
            <div className="grid grid-cols-[repeat(auto-fill,minmax(18px,1fr))] gap-2">
              {result.agents.slice(0, 220).map((agent) => (
                <span
                  key={agent.id}
                  title={`${agent.district} agent ${agent.id}: ${STATE_META[agent.state].label}`}
                  className="aspect-square rounded-[5px] border border-[rgba(255,255,255,.08)]"
                  style={{
                    background: STATE_META[agent.state].color,
                    opacity: 0.45 + agent.trust * 0.5,
                  }}
                />
              ))}
            </div>
            {result.agents.length > 220 && (
              <p className="font-mono-data mt-3 text-[10px] text-[var(--t4)]">
                Showing first 220 of {result.agents.length} agents for readability.
              </p>
            )}
          </div>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <section className="nidm-card p-5">
          <div className="mb-5 flex items-center gap-2">
            <Network className="h-4 w-4 text-[var(--sky)]" />
            <h2 className="font-syne text-lg font-bold">ABM adoption trace</h2>
          </div>
          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={310}>
              <LineChart data={result.trace} margin={{ top: 8, right: 18, left: 0, bottom: 4 }}>
                <CartesianGrid stroke="rgba(255,255,255,.05)" vertical={false} />
                <XAxis dataKey="day" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${Math.round(Number(value) * 100)}%`} />
                <Tooltip formatter={(value: unknown) => `${(Number(value) * 100).toFixed(1)}%`} />
                <Line type="monotone" dataKey="adoption" stroke="var(--verdant)" strokeWidth={2.5} dot={false} name="Adoption" />
                <Line type="monotone" dataKey="misinformed" stroke="var(--flame)" strokeWidth={2} dot={false} name="Misinformed" />
                <Line type="monotone" dataKey="inoculated" stroke="var(--gold)" strokeWidth={2} dot={false} name="Inoculated" />
                <Line type="monotone" dataKey="resistant" stroke="var(--violet)" strokeWidth={2} dot={false} name="Resistant" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="nidm-card p-5">
          <h2 className="font-syne text-lg font-bold">ABM feedback signals</h2>
          <div className="mt-4 space-y-3">
            <FeedbackSignal
              label="District heterogeneity"
              value={`${DISTRICTS.length} district groups represented`}
              accent="var(--sky)"
            />
            <FeedbackSignal
              label="Peer effect"
              value={`${(params.peerInfluence * 100).toFixed(0)}% influence weight`}
              accent="var(--indigoL)"
            />
            <FeedbackSignal
              label="Intervention readout"
              value={last.misinformed < first.misinformed ? "Misinformation reduced" : "Misinformation still elevated"}
              accent={last.misinformed < first.misinformed ? "var(--verdant)" : "var(--flame)"}
            />
            <FeedbackSignal
              label="Policy handoff"
              value="Use this output to tune scenarios and RL rewards"
              accent="var(--gold)"
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function FeedbackSignal({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3">
      <p className="font-mono-data text-[10px] uppercase tracking-[1.2px] text-[var(--t4)]">{label}</p>
      <p className="mt-2 text-sm font-semibold" style={{ color: accent }}>{value}</p>
    </div>
  );
}
