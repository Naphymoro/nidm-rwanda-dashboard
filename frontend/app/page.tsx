const stats = [
  { label: "Narratives ingested", value: "12.4k", trend: "+18%" },
  { label: "Encoding confidence", value: "87%", trend: "+6%" },
  { label: "Countries configured", value: "3", trend: "RW · KE · NG" },
  { label: "Scenario lift", value: "+22%", trend: "hybrid model" },
];

const modules = [
  "SDMX ingestion gateway",
  "LLM narrative encoder",
  "Human-AI review cockpit",
  "Digital twin simulator",
  "Scenario comparison lab",
  "Evaluation and audit trail",
];

export default function Home() {
  return (
    <main className="dashboard">
      <section className="hero-panel">
        <div>
          <div className="eyebrow">Narrative Intelligence Digital Twin</div>
          <h1>Research-grade policy simulation for narrative-driven adoption dynamics.</h1>
          <p className="hero-copy">
            Ingest long-form stories, encode trust and barriers with AI, and simulate clean-cooking adoption across countries and administrative units.
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="/ingest">Start ingestion</a>
            <a className="secondary-action" href="/simulate">Run simulation</a>
          </div>
        </div>
        <div className="orbital-card">
          <div className="pulse-ring ring-one" />
          <div className="pulse-ring ring-two" />
          <div className="core-orb">NIDM</div>
          <div className="orbit-label label-a">LLM</div>
          <div className="orbit-label label-b">ABM</div>
          <div className="orbit-label label-c">ODE</div>
        </div>
      </section>

      <section className="stat-grid">
        {stats.map((s) => (
          <article className="glass-stat" key={s.label}>
            <span>{s.label}</span>
            <strong>{s.value}</strong>
            <em>{s.trend}</em>
          </article>
        ))}
      </section>

      <section className="workspace-grid">
        <div className="card glow-card">
          <h2>Agentic workflow</h2>
          <div className="pipeline">
            {modules.map((m, i) => (
              <div className="pipeline-step" key={m}>
                <span>{String(i + 1).padStart(2, "0")}</span>
                <p>{m}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card signal-card">
          <h2>Live model signals</h2>
          <div className="signal-row"><span>Trust</span><div><i style={{ width: "76%" }} /></div><b>0.76</b></div>
          <div className="signal-row"><span>Barrier</span><div><i style={{ width: "38%" }} /></div><b>0.38</b></div>
          <div className="signal-row"><span>Influence</span><div><i style={{ width: "69%" }} /></div><b>0.69</b></div>
          <div className="mini-console">
            <code>hybrid_model.run(country="Rwanda", horizon=180)</code>
          </div>
        </div>
      </section>
    </main>
  );
}
