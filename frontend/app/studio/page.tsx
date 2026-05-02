"use client";

import { useMemo, useState } from "react";

const navigation = ["Command", "Ingest", "Encode", "Simulate", "Explore", "Evaluate"];

function clamp(value: number) {
  return Math.max(0, Math.min(1, value));
}

function generatePath(trust: number, subsidy: number, supply: number) {
  let adoption = 0.32;
  return Array.from({ length: 42 }, (_, index) => {
    const lift = 0.022 + trust * 0.026 + subsidy * 0.04 + supply * 0.024;
    const resistance = Math.max(0.006, 0.018 - supply * 0.008);
    adoption = clamp(adoption + lift * adoption * (1 - adoption) - resistance * adoption);
    return { x: index, y: adoption };
  });
}

function pathFromSeries(series: { x: number; y: number }[]) {
  const width = 680;
  const height = 260;
  return series.map((point, index) => {
    const x = (point.x / Math.max(1, series.length - 1)) * width;
    const y = height - point.y * height;
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

export default function StudioPage() {
  const [active, setActive] = useState("Command");
  const [trust, setTrust] = useState(0.46);
  const [subsidy, setSubsidy] = useState(0.62);
  const [supply, setSupply] = useState(0.38);
  const [learning, setLearning] = useState(true);

  const series = useMemo(() => generatePath(trust, subsidy, supply), [trust, subsidy, supply]);
  const trajectory = pathFromSeries(series);
  const final = series.at(-1)?.y ?? 0;
  const lift = final - 0.32;
  const dominant = subsidy >= trust && subsidy >= supply ? "Subsidy" : trust >= supply ? "Trust" : "Supply";
  const risk = subsidy > 0.72 ? "Budget pressure" : supply < 0.3 ? "Supply risk" : "Operationally balanced";

  return (
    <main className="screen">
      <aside className="rail">
        <div className="brand">
          <div className="brandMark">N</div>
          <div>
            <strong>NIDM</strong>
            <span>Research OS</span>
          </div>
        </div>
        <nav>
          {navigation.map((item) => (
            <button key={item} className={active === item ? "navActive" : ""} onClick={() => setActive(item)}>{item}</button>
          ))}
        </nav>
        <div className="railCard">
          <span>Live workspace</span>
          <strong>Rwanda pilot</strong>
          <p>RW · KE · NG</p>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Narrative Intelligence OS</p>
            <h1>Policy simulation cockpit</h1>
            <p className="subhead">A clean command interface for narrative ingestion, AI encoding, Bayesian simulation, and decision-ready recommendations.</p>
          </div>
          <div className="statusBlock">
            <span className="pulse" />
            <div>
              <strong>System online</strong>
              <p>Adaptive twin active</p>
            </div>
          </div>
        </header>

        <section className="kpiGrid">
          <Metric label="Narratives" value="12,480" delta="+18.2%" />
          <Metric label="AI confidence" value="87.4%" delta="+6.1%" />
          <Metric label="Scenario lift" value={`+${(lift * 100).toFixed(1)}%`} delta="live" />
          <Metric label="Countries" value="03" delta="RW · KE · NG" />
        </section>

        <section className="mainGrid">
          <article className="panel chartPanel">
            <div className="panelHeader">
              <div>
                <p className="eyebrow">Digital twin</p>
                <h2>Adoption trajectory</h2>
              </div>
              <span className="chip">{active}</span>
            </div>
            <svg className="chart" viewBox="0 0 680 260" preserveAspectRatio="none">
              <defs>
                <linearGradient id="lineGlow" x1="0" x2="1" y1="0" y2="0">
                  <stop offset="0%" stopColor="#38bdf8" />
                  <stop offset="45%" stopColor="#60a5fa" />
                  <stop offset="100%" stopColor="#a78bfa" />
                </linearGradient>
                <filter id="glow"><feGaussianBlur stdDeviation="4" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
              </defs>
              {[0, 1, 2, 3, 4].map((i) => <line key={i} x1="0" x2="680" y1={i * 65} y2={i * 65} className="gridLine" />)}
              <path d={trajectory} fill="none" stroke="url(#lineGlow)" strokeWidth="4" filter="url(#glow)" />
            </svg>
            <div className="chartFooter">
              <div><span>Current</span><strong>0.320</strong></div>
              <div><span>Projected</span><strong>{final.toFixed(3)}</strong></div>
              <div><span>Primary lever</span><strong>{dominant}</strong></div>
              <div><span>Status</span><strong>{risk}</strong></div>
            </div>
          </article>

          <article className="panel controlPanel">
            <div className="panelHeader compact">
              <div>
                <p className="eyebrow">Controls</p>
                <h2>Policy levers</h2>
              </div>
            </div>
            <Slider label="Trust campaign" value={trust} setValue={setTrust} />
            <Slider label="Consumer subsidy" value={subsidy} setValue={setSubsidy} />
            <Slider label="Supply chain" value={supply} setValue={setSupply} />
            <label className="toggle"><input type="checkbox" checked={learning} onChange={(event) => setLearning(event.target.checked)} /> Adaptive learning enabled</label>
            <button className="primary">Run decision pass</button>
          </article>
        </section>

        <section className="bottomGrid">
          <article className="panel recommendation">
            <p className="eyebrow">Recommendation</p>
            <h2>{dominant} led strategy</h2>
            <p>Prioritize {dominant.toLowerCase()} while monitoring {risk.toLowerCase()}. Current projected adoption reaches <strong>{final.toFixed(3)}</strong> with a lift of <strong>{(lift * 100).toFixed(1)}%</strong>.</p>
            <div className="actions"><button className="primary">Apply strategy</button><button>Export brief</button></div>
          </article>
          <article className="panel scenarioStack">
            <p className="eyebrow">Scenario ranking</p>
            <Scenario rank="01" title="Optimized" value={final + 0.05} active />
            <Scenario rank="02" title="Selected" value={final} />
            <Scenario rank="03" title="Baseline" value={0.47} />
          </article>
          <article className="panel monitor">
            <p className="eyebrow">Proactive monitor</p>
            <ul>
              <li>{learning ? "Learning mode is active and will adapt recommendations." : "Learning mode is paused."}</li>
              <li>{risk === "Operationally balanced" ? "No major feasibility alert detected." : risk}</li>
              <li>Traceability layer ready for narrative evidence.</li>
            </ul>
          </article>
        </section>
      </section>

      <style jsx>{`
        .screen { min-height: 100vh; display: grid; grid-template-columns: 280px 1fr; background: #050713; color: #edf4ff; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .rail { padding: 24px; border-right: 1px solid rgba(148, 163, 184, .16); background: linear-gradient(180deg, rgba(2, 6, 23, .96), rgba(8, 13, 28, .92)); display: flex; flex-direction: column; gap: 24px; }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brandMark { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, #2563eb, #22d3ee); font-weight: 900; box-shadow: 0 0 36px rgba(34, 211, 238, .24); }
        .brand strong { display: block; font-size: 18px; letter-spacing: -.04em; }
        .brand span, .railCard span { color: #8da2bd; font-size: 12px; }
        nav { display: grid; gap: 8px; }
        button { border: 1px solid rgba(148, 163, 184, .16); background: rgba(15, 23, 42, .68); color: #edf4ff; border-radius: 14px; padding: 11px 13px; font-weight: 800; cursor: pointer; transition: .18s ease; }
        button:hover { transform: translateY(-1px); border-color: rgba(56, 189, 248, .55); box-shadow: 0 12px 32px rgba(37, 99, 235, .2); }
        nav button { text-align: left; }
        .navActive, .primary { background: linear-gradient(135deg, #2563eb, #22d3ee); border-color: rgba(147, 197, 253, .45); }
        .railCard { margin-top: auto; border: 1px solid rgba(148, 163, 184, .16); border-radius: 18px; padding: 16px; background: rgba(15, 23, 42, .66); }
        .railCard strong { display: block; margin-top: 6px; }
        .workspace { padding: 26px; overflow: hidden; background: radial-gradient(circle at 18% 2%, rgba(37, 99, 235, .22), transparent 28rem), radial-gradient(circle at 100% 88%, rgba(34, 211, 238, .12), transparent 30rem); }
        .topbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; margin-bottom: 22px; animation: fadeUp .45s ease both; }
        .eyebrow { color: #22d3ee; font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: .14em; margin: 0 0 7px; }
        h1 { font-size: clamp(34px, 4vw, 60px); line-height: .95; letter-spacing: -.075em; margin: 0 0 12px; }
        h2 { margin: 0; letter-spacing: -.045em; font-size: 24px; }
        .subhead { color: #9fb2c9; font-size: 16px; max-width: 760px; line-height: 1.55; margin: 0; }
        .statusBlock { display: flex; gap: 10px; align-items: center; border: 1px solid rgba(34, 197, 94, .22); background: rgba(34, 197, 94, .08); color: #bbf7d0; padding: 12px 14px; border-radius: 18px; min-width: 210px; }
        .statusBlock p { margin: 2px 0 0; color: #86efac; font-size: 12px; }
        .pulse { width: 10px; height: 10px; border-radius: 999px; background: #22c55e; box-shadow: 0 0 0 6px rgba(34, 197, 94, .12); }
        .kpiGrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
        .panel, .metric { border: 1px solid rgba(148, 163, 184, .16); background: linear-gradient(180deg, rgba(15, 23, 42, .82), rgba(2, 6, 23, .72)); border-radius: 22px; box-shadow: 0 24px 70px rgba(0, 0, 0, .34); backdrop-filter: blur(18px); }
        .metric { padding: 16px; transition: .18s ease; animation: fadeUp .45s ease both; }
        .metric:hover, .panel:hover { border-color: rgba(56, 189, 248, .32); }
        .metric span { color: #8da2bd; font-size: 12px; }
        .metric strong { display: block; font-size: 29px; letter-spacing: -.06em; margin: 6px 0; }
        .metric em { color: #93c5fd; font-style: normal; font-size: 12px; }
        .mainGrid { display: grid; grid-template-columns: 1fr 340px; gap: 18px; margin-bottom: 18px; }
        .panel { padding: 18px; animation: scaleIn .4s ease both; }
        .panelHeader { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
        .chip { border: 1px solid rgba(96, 165, 250, .34); border-radius: 999px; color: #bfdbfe; padding: 6px 10px; font-size: 12px; font-weight: 900; }
        .chart { width: 100%; height: 330px; display: block; overflow: visible; }
        .gridLine { stroke: rgba(148, 163, 184, .14); stroke-width: 1; }
        .chartFooter { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 14px; }
        .chartFooter div { border: 1px solid rgba(148, 163, 184, .12); border-radius: 16px; padding: 12px; background: rgba(2, 6, 23, .45); }
        .chartFooter span { display: block; color: #8da2bd; font-size: 11px; }
        .chartFooter strong { display: block; margin-top: 4px; }
        .controlPanel { display: grid; gap: 16px; }
        label { color: #9fb2c9; font-weight: 800; font-size: 12px; }
        input[type='range'] { width: 100%; accent-color: #22d3ee; margin-top: 8px; }
        .toggle { display: flex; align-items: center; gap: 8px; }
        .bottomGrid { display: grid; grid-template-columns: 1.1fr .9fr .9fr; gap: 18px; }
        .recommendation p, .monitor li { color: #9fb2c9; line-height: 1.65; }
        .actions { display: flex; gap: 10px; margin-top: 16px; }
        .scenarioStack { display: grid; gap: 10px; }
        .scenario { display: grid; grid-template-columns: 42px 1fr auto; gap: 10px; align-items: center; border: 1px solid rgba(148, 163, 184, .14); border-radius: 16px; padding: 10px; background: rgba(2, 6, 23, .42); }
        .scenario.active { border-color: rgba(96, 165, 250, .42); background: rgba(37, 99, 235, .16); }
        .scenario small { color: #8da2bd; }
        .scenario strong { font-size: 18px; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(.986); } to { opacity: 1; transform: scale(1); } }
        @media (max-width: 1120px) { .screen { grid-template-columns: 1fr; } .rail { position: relative; } .mainGrid, .bottomGrid, .kpiGrid { grid-template-columns: 1fr; } .chartFooter { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 720px) { .workspace { padding: 18px; } .topbar { flex-direction: column; } .chartFooter { grid-template-columns: 1fr; } }
      `}</style>
    </main>
  );
}

function Metric({ label, value, delta }: { label: string; value: string; delta: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong><em>{delta}</em></div>;
}

function Slider({ label, value, setValue }: { label: string; value: number; setValue: (value: number) => void }) {
  return <label>{label} {value.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={value} onChange={(event) => setValue(Number(event.target.value))} /></label>;
}

function Scenario({ rank, title, value, active = false }: { rank: string; title: string; value: number; active?: boolean }) {
  return <div className={`scenario ${active ? "active" : ""}`}><small>{rank}</small><span>{title}</span><strong>{value.toFixed(3)}</strong></div>;
}
