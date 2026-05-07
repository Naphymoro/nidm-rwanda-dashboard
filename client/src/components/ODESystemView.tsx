import React, { CSSProperties, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BookOpen, Sigma, SlidersHorizontal } from "lucide-react";
import { useNIDMMode } from "./DashboardLayout";

type ParameterKey = "betaT" | "betaM" | "iota" | "rho" | "mu";

const PARAMETER_META: Record<ParameterKey, { label: React.ReactNode; min: number; max: number; step: number; accent: string }> = {
  betaT: { label: <><span>&beta;</span><sub>t</sub></>, min: 0.05, max: 1.2, step: 0.01, accent: "var(--sky)" },
  betaM: { label: <><span>&beta;</span><sub>m</sub></>, min: 0.05, max: 1.2, step: 0.01, accent: "var(--flame)" },
  iota: { label: <span>&iota;</span>, min: 0, max: 0.8, step: 0.01, accent: "var(--gold)" },
  rho: { label: <span>&rho;</span>, min: 0, max: 0.8, step: 0.01, accent: "var(--verdant)" },
  mu: { label: <span>&mu;</span>, min: 0, max: 0.4, step: 0.01, accent: "var(--violet)" },
};

const GLOSSARY: Array<{ symbol: React.ReactNode; description: string }> = [
  { symbol: <span>S</span>, description: "Susceptible households that have not yet adopted a stable clean-cooking belief state." },
  { symbol: <span>M</span>, description: "Misinformed households influenced by false, confusing, or adoption-discouraging narratives." },
  { symbol: <span>T</span>, description: "Truth-aligned households exposed to accurate and trust-building clean-cooking information." },
  { symbol: <span>I</span>, description: "Inoculated households prepared to resist misinformation before it spreads." },
  { symbol: <span>R</span>, description: "Resistant households with durable belief protection and lower reversion risk." },
  { symbol: <span>&Phi;</span>, description: "Composite narrative force that balances trust, credibility, channel fit, and counter-message strength." },
];

const COMPARTMENTS = [
  { key: "S", name: "Susceptible", color: "var(--cS)" },
  { key: "M", name: "Misinformed", color: "var(--cM)" },
  { key: "T", name: "Truth", color: "var(--cT)" },
  { key: "I", name: "Inoculated", color: "var(--cI)" },
  { key: "R", name: "Resistant", color: "var(--cR)" },
];

function EquationLine({ children }: { children: React.ReactNode }) {
  return <div className="eq-block">{children}</div>;
}

function pct(value: number, min: number, max: number) {
  return ((value - min) / (max - min)) * 100;
}

export default function ODESystemView() {
  const { mode } = useNIDMMode();
  const [params, setParams] = useState<Record<ParameterKey, number>>({
    betaT: 0.42,
    betaM: 0.36,
    iota: 0.24,
    rho: 0.18,
    mu: 0.08,
  });

  const phi = useMemo(() => {
    return Math.max(0.1, Math.min(1, 0.58 + params.betaT * 0.18 - params.betaM * 0.12 + params.iota * 0.2));
  }, [params]);

  const reproduction = useMemo(() => {
    const rt = (params.betaT * phi) / Math.max(0.05, params.rho + params.mu);
    const rm = (params.betaM * (1 - params.iota * 0.4)) / Math.max(0.05, params.rho + params.mu);
    return { rt, rm };
  }, [params, phi]);

  const compartments = useMemo(() => {
    const truth = Math.min(0.72, 0.22 + params.betaT * 0.2 + phi * 0.22);
    const misinfo = Math.max(0.05, 0.26 + params.betaM * 0.18 - params.iota * 0.2 - params.rho * 0.08);
    const inoculated = Math.min(0.5, 0.12 + params.iota * 0.36 + params.rho * 0.14);
    const resistant = Math.min(0.44, 0.08 + params.rho * 0.28 + params.mu * 0.08);
    const susceptible = Math.max(0.04, 1 - truth - misinfo - inoculated - resistant);

    return [
      { name: "S", value: susceptible, color: "var(--cS)" },
      { name: "M", value: misinfo, color: "var(--cM)" },
      { name: "T", value: truth, color: "var(--cT)" },
      { name: "I", value: inoculated, color: "var(--cI)" },
      { name: "R", value: resistant, color: "var(--cR)" },
    ];
  }, [params, phi]);

  const explainer = {
    novice: "This page shows how households move between belief states. Higher truth exposure and inoculation push the system toward durable clean-cooking adoption.",
    policy: "Use this system view to identify whether adoption is constrained by misinformation pressure, weak truth transmission, or insufficient inoculation coverage.",
    expert: "The controls expose transmission, inoculation, recovery, and decay terms so the reproduction numbers can be interpreted against policy thresholds.",
  }[mode];

  return (
    <div className="animate-page-in space-y-6">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>
        {explainer}
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.25fr_.75fr]">
        <section className="nidm-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <Sigma className="h-4 w-4 text-[var(--sky)]" />
            <h2 className="font-syne text-lg font-bold">NIDM differential system</h2>
          </div>

          <div className="grid gap-3">
            <EquationLine>
              <span className="eq-var">dS/dt</span> <span className="eq-op">=</span> <span className="eq-op">-</span><span className="eq-var">&beta;<sub>m</sub>SM</span> <span className="eq-op">-</span> <span className="eq-var">&beta;<sub>t</sub>S&Phi;</span> <span className="eq-op">-</span> <span className="eq-var">&iota;S</span>
            </EquationLine>
            <EquationLine>
              <span className="eq-var">dM/dt</span> <span className="eq-op">=</span> <span className="eq-var">&beta;<sub>m</sub>SM</span> <span className="eq-op">-</span> <span className="eq-var">&rho;M</span> <span className="eq-op">-</span> <span className="eq-var">&mu;M</span>
            </EquationLine>
            <EquationLine>
              <span className="eq-var">dT/dt</span> <span className="eq-op">=</span> <span className="eq-var">&beta;<sub>t</sub>S&Phi;</span> <span className="eq-op">+</span> <span className="eq-var">&rho;M</span> <span className="eq-op">-</span> <span className="eq-var">&iota;T</span>
            </EquationLine>
            <EquationLine>
              <span className="eq-var">dI/dt</span> <span className="eq-op">=</span> <span className="eq-var">&iota;(S+T)</span> <span className="eq-op">-</span> <span className="eq-var">&mu;I</span>
            </EquationLine>
            <EquationLine>
              <span className="eq-var">dR/dt</span> <span className="eq-op">=</span> <span className="eq-var">&mu;(M+I)</span> <span className="eq-op">+</span> <span className="eq-var">&rho;I</span>
            </EquationLine>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="eq-block">
              <span className="eq-var">&Phi;</span> <span className="eq-op">=</span> <span className="eq-num">{phi.toFixed(3)}</span> <span className="eq-cmt"> composite force</span>
            </div>
            <div className="eq-block">
              <span className="eq-var">R<sub>m</sub></span> <span className="eq-op">=</span> <span className="eq-num">{reproduction.rm.toFixed(2)}</span>
            </div>
            <div className="eq-block">
              <span className="eq-var">R<sub>t</sub></span> <span className="eq-op">=</span> <span className="eq-num">{reproduction.rt.toFixed(2)}</span>
            </div>
          </div>
        </section>

        <section className="nidm-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-[var(--indigoL)]" />
            <h2 className="font-syne text-lg font-bold">Parameters</h2>
          </div>
          <div className="space-y-5">
            {(Object.keys(PARAMETER_META) as ParameterKey[]).map((key) => {
              const meta = PARAMETER_META[key];
              const pctValue = pct(params[key], meta.min, meta.max);

              return (
                <label key={key} className="block">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-mono-data text-xs text-[var(--t2)]">{meta.label}</span>
                    <span className="font-mono-data text-xs" style={{ color: meta.accent }}>{params[key].toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min={meta.min}
                    max={meta.max}
                    step={meta.step}
                    value={params[key]}
                    onChange={(event) => setParams((current) => ({ ...current, [key]: Number(event.target.value) }))}
                    style={{ "--pct": `${pctValue}%`, "--indigoL": meta.accent } as CSSProperties}
                  />
                </label>
              );
            })}
          </div>
        </section>
      </div>

      <div className="grid gap-6 xl:grid-cols-[.95fr_1.05fr]">
        <section className="nidm-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-[var(--gold)]" />
            <h2 className="font-syne text-lg font-bold">Parameter glossary</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--bdr)] font-mono-data text-[10px] uppercase tracking-[1.4px] text-[var(--t4)]">
                  <th className="py-3 pr-4">Symbol</th>
                  <th className="py-3">Description</th>
                </tr>
              </thead>
              <tbody>
                {GLOSSARY.map((item) => (
                  <tr key={String(item.description)} className="border-b border-[rgba(255,255,255,.04)]">
                    <td className="font-mono-data py-3 pr-4 text-[var(--indigoL)]">{item.symbol}</td>
                    <td className="py-3 text-[var(--t2)]">{item.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="nidm-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-syne text-lg font-bold">Population compartment flow</h2>
            <div className="flex gap-2">
              {COMPARTMENTS.map((item) => (
                <span key={item.key} className="font-mono-data text-[10px]" style={{ color: item.color }}>{item.key}</span>
              ))}
            </div>
          </div>
          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={compartments} layout="vertical" margin={{ top: 8, right: 22, left: 12, bottom: 8 }}>
                <CartesianGrid stroke="rgba(255,255,255,.05)" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tickFormatter={(value) => `${Math.round(Number(value) * 100)}%`} />
                <YAxis type="category" dataKey="name" width={36} />
                <Tooltip formatter={(value: unknown) => `${(Number(value) * 100).toFixed(1)}%`} />
                <Bar dataKey="value" radius={[0, 7, 7, 0]}>
                  {compartments.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}
