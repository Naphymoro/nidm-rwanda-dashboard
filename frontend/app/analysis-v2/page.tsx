"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const modes = ["Explore", "Analyze", "Compare", "Decide"] as const;
type Mode = (typeof modes)[number];

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

function fmt(value: number | undefined, digits = 3) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "n/a";
}

function simulate(start: number, trust: number, subsidy: number, supply: number, horizon = 90) {
  let adoption = clamp01(start);
  const influence = 0.032 + trust * 0.035 + subsidy * 0.052 + supply * 0.026;
  const resistance = Math.max(0.004, 0.018 - supply * 0.008 - subsidy * 0.004);
  return Array.from({ length: horizon }, (_, i) => {
    adoption = clamp01(adoption + influence * adoption * (1 - adoption) - resistance * adoption);
    return { day: i + 1, preview: adoption };
  });
}

export default function AnalysisV2Page() {
  const [mode, setMode] = useState<Mode>("Explore");
  const [trust, setTrust] = useState(0.4);
  const [subsidy, setSubsidy] = useState(0.5);
  const [supply, setSupply] = useState(0.3);
  const [budget, setBudget] = useState(0.7);
  const [learning, setLearning] = useState(true);

  const preview = useMemo(() => simulate(0.41, trust, subsidy, supply), [trust, subsidy, supply]);
  const finalAdoption = preview.at(-1)?.preview;
  const lift = typeof finalAdoption === "number" ? finalAdoption - 0.41 : undefined;
  const mainLever = subsidy >= trust && subsidy >= supply ? "consumer subsidy" : trust >= supply ? "trust campaign" : "supply chain";
  const confidence = subsidy > budget ? "Budget risk" : lift && lift > 0.3 ? "Strong" : "Moderate";

  const comparisonData = preview.map((row) => ({
    day: row.day,
    Baseline: clamp01(0.41 + 0.0016 * row.day),
    Selected: row.preview,
    Optimized: clamp01(row.preview + 0.055 + subsidy * 0.035),
  }));

  const metrics = [
    ["Current", "0.410", "Observed endpoint"],
    ["Projected", fmt(finalAdoption), `${lift && lift >= 0 ? "+" : ""}${fmt(lift)} lift`],
    ["Confidence", confidence, learning ? "Learning enabled" : "Learning paused"],
    ["Main lever", mainLever, "Highest active driver"],
  ];

  return (
    <section className="analysis-v2-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">NIDM Decision Lab</p>
          <h1>Policy Intelligence Console</h1>
          <p className="subtitle">A cleaner decision-first workspace for live policy preview, uncertainty, scenario comparison, and action guidance.</p>
        </div>
        <nav className="mode-switcher">
          {modes.map((item) => (
            <button key={item} onClick={() => setMode(item)} className={mode === item ? "active" : ""}>{item}</button>
          ))}
        </nav>
      </header>

      <div className="layout-grid">
        <aside className="panel controls">
          <h2>Controls</h2>
          <Control label="Budget" value={budget} onChange={setBudget} />
          <Control label="Trust campaign" value={trust} onChange={setTrust} />
          <Control label="Consumer subsidy" value={subsidy} onChange={setSubsidy} />
          <Control label="Supply chain" value={supply} onChange={setSupply} />
          <label className="toggle"><input type="checkbox" checked={learning} onChange={(e) => setLearning(e.target.checked)} /> Adaptive learning</label>
          <button className="primary" onClick={() => setMode("Decide")}>Run decision pass</button>
          <button className="secondary" onClick={() => setMode("Compare")}>Compare scenarios</button>
        </aside>

        <main className="main-stack">
          <section className="panel workspace">
            <div className="workspace-top">
              <div>
                <p className="eyebrow">{mode} workspace</p>
                <h2>{titleFor(mode)}</h2>
              </div>
              <span className={`confidence ${confidence === "Budget risk" ? "risk" : ""}`}>{confidence}</span>
            </div>

            <div className="metric-grid">
              {metrics.map(([label, value, hint]) => (
                <div className="metric" key={label}>
                  <p>{label}</p>
                  <strong>{value}</strong>
                  <span>{hint}</span>
                </div>
              ))}
            </div>

            <div className="chart-card">
              {mode === "Compare" ? (
                <ResponsiveContainer width="100%" height={380}>
                  <LineChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line dataKey="Baseline" strokeWidth={2} dot={false} />
                    <Line dataKey="Selected" strokeWidth={3} dot={false} />
                    <Line dataKey="Optimized" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <ResponsiveContainer width="100%" height={380}>
                  <LineChart data={preview}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line dataKey="preview" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </section>

          {mode === "Decide" ? (
            <section className="panel decision-strip">
              <h2>Decision package</h2>
              <div className="decision-grid">
                <DecisionCard title="Recommended action" body={`Prioritize ${mainLever} while keeping budget feasibility under review.`} />
                <DecisionCard title="Expected impact" body={`Adoption changes from 0.410 to ${fmt(finalAdoption)}.`} />
                <DecisionCard title="Governance check" body={confidence === "Budget risk" ? "Reduce subsidy intensity or raise available budget before rollout." : "Recommendation is suitable for planning, pending field validation."} />
              </div>
            </section>
          ) : (
            <section className="panel assistant-strip">
              <h2>Assistant insight</h2>
              <p>{confidence === "Budget risk" ? "Subsidy exceeds the budget setting. The assistant recommends lowering subsidy or increasing the budget envelope." : `The current policy mix is led by ${mainLever}. Move to Decide when ready to frame the recommendation.`}</p>
            </section>
          )}
        </main>

        <aside className="panel insight">
          <p className="eyebrow">Decision summary</p>
          <h2>{mode === "Decide" ? "Ready for decision review" : "Live preview active"}</h2>
          <p><strong>Projected adoption:</strong> {fmt(finalAdoption)}</p>
          <p><strong>Lift:</strong> {lift && lift >= 0 ? "+" : ""}{fmt(lift)}</p>
          <p><strong>Primary lever:</strong> {mainLever}</p>
          <p><strong>Status:</strong> {confidence}</p>
          <button className="primary" onClick={() => setMode("Decide")}>Open decision view</button>
          <div className="monitor">
            <h3>Proactive monitor</h3>
            <ul>
              <li>{lift && lift < 0.18 ? "Lift is weak. Strengthen the policy mix." : "Projected lift is acceptable for exploration."}</li>
              <li>{subsidy > budget ? "Budget risk detected." : "Budget setting appears feasible."}</li>
              <li>{learning ? "Learning mode is enabled." : "Learning mode is paused."}</li>
            </ul>
          </div>
        </aside>
      </div>

      <style jsx>{`
        .analysis-v2-shell {
          min-height: 100vh;
          padding: 24px;
          color: #e5edf8;
          background:
            radial-gradient(circle at top left, rgba(37,99,235,.22), transparent 34rem),
            radial-gradient(circle at bottom right, rgba(34,211,238,.12), transparent 30rem),
            linear-gradient(135deg, #050712 0%, #0b1020 48%, #050712 100%);
        }
        .hero { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; margin-bottom: 22px; animation: fadeUp .45s ease both; }
        h1 { margin: 4px 0; font-size: clamp(28px, 3vw, 44px); letter-spacing: -.06em; }
        h2 { margin: 0 0 12px; letter-spacing: -.035em; }
        .subtitle { max-width: 760px; color: #93a4ba; line-height: 1.55; }
        .eyebrow { margin: 0 0 7px; color: #22d3ee; font-size: 11px; font-weight: 900; letter-spacing: .14em; text-transform: uppercase; }
        .mode-switcher { display: flex; gap: 8px; padding: 6px; border: 1px solid rgba(148,163,184,.18); border-radius: 16px; background: rgba(2,6,23,.46); backdrop-filter: blur(16px); }
        button { border: 1px solid rgba(96,165,250,.26); border-radius: 12px; padding: 10px 13px; color: white; background: rgba(15,23,42,.82); font-weight: 800; cursor: pointer; transition: transform .16s ease, border-color .16s ease, background .16s ease, box-shadow .16s ease; }
        button:hover { transform: translateY(-1px); border-color: rgba(34,211,238,.55); box-shadow: 0 10px 28px rgba(37,99,235,.22); }
        button.active, .primary { background: linear-gradient(135deg, #2563eb, #22d3ee); border-color: rgba(147,197,253,.52); }
        .secondary { background: rgba(15,23,42,.86); }
        .layout-grid { display: grid; grid-template-columns: 300px minmax(520px, 1fr) 330px; gap: 18px; align-items: start; }
        .panel { position: relative; overflow: hidden; border: 1px solid rgba(148,163,184,.18); border-radius: 18px; padding: 18px; background: linear-gradient(180deg, rgba(15,23,42,.86), rgba(2,6,23,.72)); box-shadow: 0 22px 70px rgba(0,0,0,.36); backdrop-filter: blur(22px); animation: fadeUp .45s ease both; }
        .panel::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(120deg, rgba(255,255,255,.06), transparent 30%, rgba(34,211,238,.04)); }
        .panel > * { position: relative; z-index: 1; }
        .controls, .insight { position: sticky; top: 18px; display: grid; gap: 13px; }
        label { display: grid; gap: 7px; color: #93a4ba; font-size: 12px; font-weight: 800; }
        input[type='range'] { width: 100%; accent-color: #22d3ee; }
        .toggle { display: flex; align-items: center; gap: 8px; }
        .main-stack { display: grid; gap: 18px; }
        .workspace { border-color: rgba(96,165,250,.42); animation: scaleIn .38s ease both; }
        .workspace-top { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
        .confidence { border: 1px solid rgba(34,197,94,.28); color: #86efac; background: rgba(34,197,94,.11); border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 900; }
        .confidence.risk { border-color: rgba(245,158,11,.36); color: #fcd34d; background: rgba(245,158,11,.12); }
        .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0 16px; }
        .metric { padding: 14px; border: 1px solid rgba(148,163,184,.14); border-radius: 16px; background: rgba(2,6,23,.48); transition: transform .18s ease, border-color .18s ease; }
        .metric:hover { transform: translateY(-2px); border-color: rgba(34,211,238,.38); }
        .metric p { margin: 0; color: #93a4ba; font-size: 11px; }
        .metric strong { display: block; margin: 5px 0; font-size: 25px; letter-spacing: -.055em; }
        .metric span { color: #64748b; font-size: 11px; }
        .chart-card { min-height: 380px; animation: fadeIn .35s ease both; }
        .assistant-strip p, .insight p, .decision-strip p { color: #93a4ba; line-height: 1.55; }
        .decision-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .decision-mini { border: 1px solid rgba(148,163,184,.16); background: rgba(2,6,23,.46); border-radius: 16px; padding: 14px; }
        .decision-mini h3 { margin: 0 0 8px; }
        .monitor { margin-top: 12px; border-top: 1px solid rgba(148,163,184,.16); padding-top: 14px; }
        .monitor ul { padding-left: 18px; color: #93a4ba; line-height: 1.7; }
        :global(.recharts-wrapper text) { fill: #93a4ba; font-size: 11px; }
        :global(.recharts-cartesian-grid line) { stroke: rgba(148,163,184,.13); }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(.985); } to { opacity: 1; transform: scale(1); } }
        @media (max-width: 1180px) { .layout-grid { grid-template-columns: 1fr; } .controls, .insight { position: static; } }
        @media (max-width: 760px) { .hero { flex-direction: column; } .mode-switcher { flex-wrap: wrap; } .metric-grid, .decision-grid { grid-template-columns: 1fr; } }
      `}</style>
    </section>
  );
}

function Control({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return <label>{label} {value.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={value} onChange={(event) => onChange(Number(event.target.value))} /></label>;
}

function titleFor(mode: Mode) {
  if (mode === "Explore") return "Live policy preview";
  if (mode === "Analyze") return "Uncertainty workspace";
  if (mode === "Compare") return "Scenario comparison";
  return "Decision recommendation";
}

function DecisionCard({ title, body }: { title: string; body: string }) {
  return <article className="decision-mini"><h3>{title}</h3><p>{body}</p></article>;
}
