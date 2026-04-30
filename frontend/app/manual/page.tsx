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

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <aside style={{ width: 240, borderRight: "1px solid #ddd", padding: 16 }}>
        <h3>NIDM Manual</h3>
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
          <section>
            <h1>Overview</h1>
            <p>
              NIDM is a narrative-driven digital twin for modeling clean-cooking adoption.
              It integrates qualitative narratives, Bayesian inference, optimization, and
              policy simulation into a unified decision system.
            </p>
          </section>
        )}

        {active === "Model" && (
          <section>
            <h1>Mathematical Model</h1>
            <p>
              The system models adoption using a diffusion equation with intervention and resistance terms.
            </p>
            <pre>{`dA/dt = βA(1-A) + γ(1-A) - δA`}</pre>
            <p>
              Where A is adoption, β is diffusion, γ is intervention effect, and δ is resistance.
            </p>
          </section>
        )}

        {active === "Narratives" && (
          <section>
            <h1>Narratives → Encoding</h1>
            <p>
              Narratives are transformed into structured variables such as trust, barriers, and affordability.
              These variables influence model parameters.
            </p>
          </section>
        )}

        {active === "Inference" && (
          <section>
            <h1>Bayesian Inference</h1>
            <p>
              The system estimates parameter distributions using observed adoption data and prior assumptions.
            </p>
          </section>
        )}

        {active === "Optimization" && (
          <section>
            <h1>Optimization</h1>
            <p>
              Policy allocation is optimized to maximize adoption while minimizing cost and improving equity.
            </p>
          </section>
        )}

        {active === "Scenarios" && (
          <section>
            <h1>Scenario Simulation</h1>
            <p>
              Multiple policy scenarios are simulated to compare trajectories and outcomes.
            </p>
          </section>
        )}

        {active === "Causality" && (
          <section>
            <h1>Causal Interpretation</h1>
            <p>
              The system estimates causal effects of interventions using counterfactual analysis.
            </p>
          </section>
        )}

        {active === "Data" && (
          <section>
            <h1>Data Requirements</h1>
            <p>
              Requires narrative data, adoption time series, and intervention records.
            </p>
          </section>
        )}

        {active === "Tutorial" && (
          <section>
            <h1>Tutorial</h1>
            <ol>
              <li>Input adoption data</li>
              <li>Run analysis</li>
              <li>Review scenarios</li>
              <li>Export report</li>
            </ol>
          </section>
        )}

        {active === "Guidelines" && (
          <section>
            <h1>Guidelines</h1>
            <ul>
              <li>Compare scenarios, not single values</li>
              <li>Consider uncertainty</li>
              <li>Validate with real data</li>
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}
