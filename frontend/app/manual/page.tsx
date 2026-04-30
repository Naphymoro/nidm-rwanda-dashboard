"use client";

import { useState } from "react";

const sections = [
  "Overview",
  "Model",
  "Inference",
  "Optimization",
  "Scenarios",
  "Worked Example",
  "Diagrams",
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
          <button onClick={() => setMode("policy")} style={{ marginRight: 8 }}>Policy View</button>
          <button onClick={() => setMode("technical")}>Technical View</button>
        </div>
        {sections.map((s) => (
          <div key={s} onClick={() => setActive(s)} style={{ cursor: "pointer", padding: 8, fontWeight: active === s ? "bold" : "normal" }}>
            {s}
          </div>
        ))}
      </aside>

      <main style={{ flex: 1, padding: 24, overflowY: "auto" }}>

        {active === "Overview" && (
          <Section
            title="Overview"
            technical={<p>This system integrates narrative encoding, Bayesian inference, and optimal control of adoption dynamics.</p>}
            policy={<p>This tool helps identify what policies will increase adoption and why.</p>}
          />
        )}

        {active === "Model" && (
          <Section
            title="Mathematical Model"
            technical={<div>
              <p>Core equation:</p>
              <pre>{`dA/dt = βA(1-A) + γ(1-A) - δA`}</pre>
              <p>β: diffusion, γ: intervention, δ: resistance</p>
            </div>}
            policy={<p>Adoption increases through social influence and policy support but slows due to barriers.</p>}
          />
        )}

        {active === "Inference" && (
          <Section
            title="Bayesian Inference"
            technical={<div>
              <pre>{`p(θ|data) ∝ p(data|θ)p(θ)`}</pre>
              <p>Posterior distributions quantify uncertainty.</p>
            </div>}
            policy={<p>The system learns from data and updates its confidence about outcomes.</p>}
          />
        )}

        {active === "Optimization" && (
          <Section
            title="Optimization"
            technical={<div>
              <pre>{`max A_final - λ Cost + α Equity`}</pre>
              <p>Multi-objective optimization balances outcomes.</p>
            </div>}
            policy={<p>The system finds the best policy mix within your constraints.</p>}
          />
        )}

        {active === "Scenarios" && (
          <Section
            title="Scenario Simulation"
            technical={<p>Policies map to parameters → trajectories.</p>}
            policy={<p>You can compare different strategies before acting.</p>}
          />
        )}

        {active === "Worked Example" && (
          <Section
            title="Worked Example"
            technical={<div>
              <pre>{`Input: [0.12,0.15,0.18,0.22]
→ Bayesian inference → parameters
→ Optimization → allocation
→ Simulation → trajectories`}</pre>
            </div>}
            policy={<ol>
              <li>Enter data</li>
              <li>Run analysis</li>
              <li>Compare scenarios</li>
              <li>Select best policy</li>
            </ol>}
          />
        )}

        {active === "Diagrams" && (
          <Section
            title="System Diagram"
            technical={<pre>{`Narratives → Encoding → Parameters → Simulation → Optimization → Policy`}</pre>}
            policy={<p>The system converts stories into decisions through a structured pipeline.</p>}
          />
        )}

        {active === "Guidelines" && (
          <Section
            title="Guidelines"
            technical={<ul><li>Check uncertainty</li><li>Validate assumptions</li></ul>}
            policy={<ul><li>Compare scenarios</li><li>Avoid single values</li></ul>}
          />
        )}

      </main>
    </div>
  );
}
