import React, { CSSProperties, useMemo, useState } from "react";
import { RotateCcw, SlidersHorizontal } from "lucide-react";
import { useNIDMMode } from "./DashboardLayout";

interface SensitivityData {
  parameter: string;
  baseline: number;
  min: number;
  max: number;
  step: number;
  impact: number;
}

interface SensitivityAnalysisProps {
  parameters?: SensitivityData[];
  title?: string;
}

const DEFAULT_PARAMETERS: SensitivityData[] = [
  { parameter: "beta transmission", baseline: 0.5, min: 0.1, max: 1.0, step: 0.05, impact: 0.85 },
  { parameter: "gamma recovery", baseline: 0.3, min: 0.05, max: 0.8, step: 0.05, impact: 0.42 },
  { parameter: "iota inoculation", baseline: 0.2, min: 0.0, max: 0.6, step: 0.05, impact: 0.68 },
  { parameter: "Phi strength", baseline: 0.65, min: 0.2, max: 1.0, step: 0.05, impact: 0.72 },
];

function impactColor(value: number) {
  if (value < 0.1) return "var(--verdant)";
  if (value < 0.25) return "var(--gold)";
  if (value < 0.5) return "var(--flame)";
  return "var(--violet)";
}

export default function SensitivityAnalysis({
  parameters = DEFAULT_PARAMETERS,
  title = "Sensitivity analysis",
}: SensitivityAnalysisProps) {
  const { mode } = useNIDMMode();
  const [values, setValues] = useState<Record<string, number>>(
    parameters.reduce((acc, param) => ({ ...acc, [param.parameter]: param.baseline }), {})
  );

  const heatmapData = useMemo(() => {
    return parameters.map((param) => {
      const current = values[param.parameter];
      const deviation = ((current - param.baseline) / Math.max(0.001, param.baseline)) * 100;
      const impact = param.impact * Math.abs(deviation) / 100;
      return { ...param, current, deviation, impact };
    });
  }, [parameters, values]);

  const averageImpact = heatmapData.reduce((sum, item) => sum + item.impact, 0) / heatmapData.length;
  const maxImpact = Math.max(...heatmapData.map((item) => item.impact));

  const explainer = {
    novice: "Move one parameter at a time to see which assumptions create the biggest shift in model behavior.",
    policy: "Sensitivity results identify which intervention assumptions need stronger evidence before decisions are made.",
    expert: "Deviation is normalized against baseline and multiplied by each parameter impact coefficient.",
  }[mode];

  function reset() {
    setValues(parameters.reduce((acc, param) => ({ ...acc, [param.parameter]: param.baseline }), {}));
  }

  return (
    <div className="animate-page-in space-y-6">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>{explainer}</section>

      <section className="nidm-card p-5">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-[var(--flame)]" />
            <h2 className="font-syne text-xl font-bold">{title}</h2>
          </div>
          <button
            type="button"
            onClick={reset}
            className="flex items-center gap-2 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2 text-xs font-semibold text-[var(--t2)]"
          >
            <RotateCcw className="h-4 w-4" />
            Reset baseline
          </button>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_.95fr]">
          <div className="space-y-6">
            {parameters.map((param) => {
              const value = values[param.parameter];
              const pct = ((value - param.min) / (param.max - param.min)) * 100;

              return (
                <label key={param.parameter} className="block">
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="font-mono-data text-xs text-[var(--t2)]">{param.parameter}</span>
                    <span className="font-mono-data text-xs text-[var(--indigoL)]">
                      {value.toFixed(3)} <span className="text-[var(--t4)]">base {param.baseline.toFixed(3)}</span>
                    </span>
                  </div>
                  <input
                    type="range"
                    min={param.min}
                    max={param.max}
                    step={param.step}
                    value={value}
                    onChange={(event) => setValues((current) => ({ ...current, [param.parameter]: Number(event.target.value) }))}
                    style={{ "--pct": `${pct}%` } as CSSProperties}
                  />
                </label>
              );
            })}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <SummaryCard label="Average impact" value={`${(averageImpact * 100).toFixed(1)}%`} accent="var(--indigoL)" />
            <SummaryCard label="Max impact" value={`${(maxImpact * 100).toFixed(1)}%`} accent="var(--flame)" />
            <SummaryCard label="High sensitivity" value={heatmapData.filter((item) => item.impact > 0.5).length.toString()} accent="var(--gold)" />
            <SummaryCard label="Robust parameters" value={heatmapData.filter((item) => item.impact < 0.1).length.toString()} accent="var(--verdant)" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {heatmapData.map((item) => {
          const color = impactColor(item.impact);

          return (
            <article key={item.parameter} className="nidm-card p-4" style={{ borderColor: `color-mix(in srgb, ${color} 36%, var(--bdr))` }}>
              <div className="mb-3 flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-syne text-base font-bold">{item.parameter}</h3>
                  <p className="mt-1 text-xs text-[var(--t3)]">Baseline {item.baseline.toFixed(3)}</p>
                </div>
                <span className="font-mono-data text-lg font-semibold" style={{ color }}>
                  {(item.impact * 100).toFixed(1)}%
                </span>
              </div>
              <div className="comp-bar-track">
                <div className="comp-bar-fill" style={{ width: `${Math.min(100, item.impact * 100)}%`, background: color }} />
              </div>
              <div className="mt-3 flex justify-between text-xs text-[var(--t3)]">
                <span className="font-mono-data">current {item.current.toFixed(3)}</span>
                <span className="font-mono-data">{item.deviation > 0 ? "+" : ""}{item.deviation.toFixed(1)}%</span>
              </div>
            </article>
          );
        })}
      </section>
    </div>
  );
}

function SummaryCard({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4">
      <p className="stat-lbl">{label}</p>
      <p className="font-syne mt-2 text-2xl font-bold" style={{ color: accent }}>{value}</p>
    </div>
  );
}
