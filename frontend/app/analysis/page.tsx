"use client";

import { useState } from "react";
import { post } from "../../lib/api";

const defaultSeries = "0.12,0.15,0.18,0.22,0.27,0.31,0.36,0.41";

export default function AnalysisPage() {
  const [series, setSeries] = useState(defaultSeries);
  const [params, setParams] = useState<any>({ beta: 0.3, gamma: 0.2, delta: 0.1 });
  const [bayesian, setBayesian] = useState<any>(null);
  const [optimization, setOptimization] = useState<any>(null);
  const [policy, setPolicy] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const values = () => series.split(",").map((x) => Number(x.trim())).filter((x) => !Number.isNaN(x));

  async function runAnalysis() {
    setLoading(true);
    setError("");
    try {
      const bayes = await post("/analytics/bayesian", values());
      setBayesian(bayes);

      const learned = {
        beta: bayes?.parameters?.beta?.mean ?? params.beta,
        gamma: bayes?.parameters?.gamma?.mean ?? params.gamma,
        delta: bayes?.parameters?.delta?.mean ?? params.delta,
      };
      setParams(learned);

      const opt = await post("/analytics/multi-objective", learned);
      setOptimization(opt);

      const allocation = opt?.best?.allocation || {
        demand_generation: 0.4,
        consumer_subsidy: 0.4,
        supply_chain: 0.2,
      };
      const mapped = await post("/analytics/policy-map", allocation);
      setPolicy(mapped);
    } catch (e: any) {
      setError(e?.message || "Analysis failed. Check that NEXT_PUBLIC_API_URL points to your backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="analysis-page">
      <header>
        <h1>Policy Analysis Workflow</h1>
        <p>Run Bayesian inference, optimize policy allocation, and map model outputs into real interventions.</p>
      </header>

      <div className="card">
        <label>Observed adoption time series</label>
        <textarea value={series} onChange={(e) => setSeries(e.target.value)} rows={4} />
        <button onClick={runAnalysis} disabled={loading}>{loading ? "Running..." : "Run full analysis"}</button>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="analysis-grid">
        <div className="card">
          <h2>Bayesian parameters</h2>
          <pre>{bayesian ? JSON.stringify(bayesian.parameters, null, 2) : "No run yet"}</pre>
        </div>

        <div className="card">
          <h2>Optimized allocation</h2>
          <pre>{optimization ? JSON.stringify(optimization.best, null, 2) : "No run yet"}</pre>
        </div>

        <div className="card">
          <h2>Policy package</h2>
          <pre>{policy ? JSON.stringify(policy, null, 2) : "No run yet"}</pre>
        </div>
      </div>
    </section>
  );
}
