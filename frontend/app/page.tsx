import { Activity, BrainCircuit, Globe2, Radar, Workflow } from "lucide-react";

const kpis = [
  { label: "Narratives", value: "12,480", delta: "+18.2%" },
  { label: "AI Confidence", value: "87.4%", delta: "+6.1%" },
  { label: "Scenario Lift", value: "+22.8%", delta: "hybrid twin" },
  { label: "Countries", value: "03", delta: "RW · KE · NG" },
];

export default function Home() {
  return (
    <main className="terminal-dashboard">
      <section className="command-hero">
        <div className="hero-left">
          <div className="system-pill"><Radar size={15} /> Digital twin command</div>
          <h1>Narrative Intelligence OS</h1>
          <p>High fidelity narrative → simulation pipeline for policy intelligence.</p>
        </div>

        <div className="webgl-stage">
          <div className="holo-cube">
            <div className="cube-face">NIDM</div>
          </div>
        </div>
      </section>

      <section className="market-strip">
        {kpis.map((item) => (
          <article className="market-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <em>{item.delta}</em>
          </article>
        ))}
      </section>

      <section className="analytics-grid">
        <article className="panel">
          <h2>Adoption trajectory</h2>
          <svg viewBox="0 0 520 220">
            <polyline points="35,178 95,162 150,138 210,118 270,82 340,60 420,46 500,34" />
          </svg>
        </article>

        <article className="panel">
          <h2>Multi-country signals</h2>
          <div>Rwanda 76%</div>
          <div>Kenya 64%</div>
          <div>Nigeria 58%</div>
        </article>
      </section>
    </main>
  );
}
