"use client";

import { useState } from "react";

const sections = [
  "Overview",
  "Model",
  "Narratives",
  "Inference",
  "Optimization",
  "Scenarios",
  "Causality",
  "Data",
  "Tutorial",
  "Guidelines",
];

export default function ManualPage() {
  const [active, setActive] = useState("Overview");
  const [mode, setMode] = useState<"technical" | "policy">("policy");

  const Section = ({ title, technical, policy }: any) => (
    <section>
      <h1>{title}</h1>
      {mode === "technical" ? technical : policy}
    </section>
  );

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <aside style={{ width: 260, borderRight: "1px solid #ddd", padding: 16 }}>
        <h3>NIDM Manual</h3>

        <div style={{ marginBottom: 16 }}>
          <button onClick={() => setMode("policy")} style={{ marginRight: 8 }}>
            Policy View
          </button>
          <button onClick={() => setMode("technical")}>Technical View</button>
        </div>

        {sections.map((s) => (
          <div
            key={s}
            onClick={() => setActive(s)}
            style={{ cursor: "pointer", padding: 8, fontWeight: active === s ? "bold" : "normal" }}
          >
            {s}
          </div>
        ))}
      </aside>

      <main style={{ flex: 1, padding: 24, overflowY: "auto" }}>
        {active === "Overview" && (
          <Section
            title="Overview"
            technical={<p>NIDM integrates narrative encoding, Bayesian inference, optimization, and simulation into a unified computational framework.</p>}
            policy={<p>This tool helps you understand what drives adoption and which policies are likely to work best.</p>}
          />
        )}

        {active === "Model" && (
          <Section
            title="Model"
            technical={<div>
              <p>Core equation:</p>
              <pre>{`dA/dt = βA(1-A) + γ(1-A) - δA`}</pre>
              <p>β = diffusion, γ = intervention effect, δ = resistance</p>
            </div>}
            policy={<p>Adoption grows through peer influence and policy support, but can slow due to barriers.</p>}
          />
        )}

        {active === "Narratives" && (
          <Section
            title="Narratives"
            technical={<p>Narratives are encoded into structured variables influencing model parameters.</p>}
            policy={<p>Community stories reveal trust, barriers, and affordability issues that shape outcomes.</p>}
          />
        )}

        {active === "Inference" && (
          <Section
            title="Inference"
            technical={<p>Bayesian inference updates parameter distributions using observed data.</p>}
            policy={<p>The system learns from data and improves its understanding over time.</p>}
          />
        )}

        {active === "Optimization" && (
          <Section
            title="Optimization"
            technical={<p>Multi-objective optimization maximizes adoption under constraints.</p>}
            policy={<p>The system suggests the best mix of interventions within your budget.</p>}
          />
        )}

        {active === "Scenarios" && (
          <Section
            title="Scenarios"
            technical={<p>Scenario simulation evaluates trajectories under different parameter settings.</p>}
            policy={<p>You can compare different strategies before making decisions.</p>}
          />
        )}

        {active === "Causality" && (
          <Section
            title="Causality"
            technical={<p>Counterfactual methods estimate causal impact of interventions.</p>}
            policy={<p>The system helps you understand what actually causes change.</p>}
          />
        )}

        {active === "Data" && (
          <Section
            title="Data"
            technical={<p>Requires narrative, adoption, and intervention datasets.</p>}
            policy={<p>Better data leads to better insights.</p>}
          />
        )}

        {active === "Tutorial" && (
          <Section
            title="Tutorial"
            technical={<ol><li>Input data</li><li>Run inference</li><li>Run optimization</li><li>Analyze outputs</li></ol>}
            policy={<ol><li>Enter your data</li><li>Run analysis</li><li>Compare results</li><li>Export report</li></ol>}
          />
        )}

        {active === "Guidelines" && (
          <Section
            title="Guidelines"
            technical={<ul><li>Check uncertainty</li><li>Validate assumptions</li></ul>}
            policy={<ul><li>Compare scenarios</li><li>Avoid single-number conclusions</li><li>Use outputs as guidance</li></ul>}
          />
        )}
      </main>
    </div>
  );
}
