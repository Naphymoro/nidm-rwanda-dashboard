"use client";

import { useMemo, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, BarChart, Bar } from "recharts";
import { post } from "../../lib/api";

const defaultSeries = "0.12,0.15,0.18,0.22,0.27,0.31,0.36,0.41";
const demoCountries = {
  Rwanda: [0.12, 0.15, 0.18, 0.22, 0.27, 0.31, 0.36, 0.41],
  Kenya: [0.18, 0.2, 0.23, 0.28, 0.32, 0.37, 0.43, 0.49],
  Nigeria: [0.08, 0.1, 0.13, 0.17, 0.21, 0.25, 0.3, 0.34],
};

export default function AnalysisPage() {
  const [series, setSeries] = useState(defaultSeries);
  const [params, setParams] = useState<any>({ beta: 0.3, gamma: 0.2, delta: 0.1 });
  const [bayesian, setBayesian] = useState<any>(null);
  const [optimization, setOptimization] = useState<any>(null);
  const [policy, setPolicy] = useState<any>(null);
  const [hierarchical, setHierarchical] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [countryLoading, setCountryLoading] = useState(false);
  const [error, setError] = useState("");

  const values = () => series.split(",").map((x) => Number(x.trim())).filter((x) => !Number.isNaN(x));

  const bayesianChart = useMemo(() => {
    const mean = bayesian?.trajectory?.mean || [];
    const lower = bayesian?.trajectory?.lower_90 || [];
    const upper = bayesian?.trajectory?.upper_90 || [];
    return mean.map((m: number, i: number) => ({ day: i + 1, mean: m, lower: lower[i], upper: upper[i] }));
  }, [bayesian]);

  const allocationChart = useMemo(() => {
    const allocation = optimization?.best?.allocation || {};
    return Object.keys(allocation).map((key) => ({ name: key.replace("_", " "), value: allocation[key] }));
  }, [optimization]);

  const countryChart = useMemo(() => {
    const countries = hierarchical?.countries || {};
    return Object.keys(countries).map((country) => ({
      country,
      beta: countries[country]?.beta?.mean,
      gamma: countries[country]?.gamma?.mean,
      delta: countries[country]?.delta?.mean,
    }));
  }, [hierarchical]);

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
      const allocation = opt?.best?.allocation || { demand_generation: 0.4, consumer_subsidy: 0.4, supply_chain: 0.2 };
      const mapped = await post("/analytics/policy-map", allocation);
      setPolicy(mapped);
    } catch (e: any) {
      setError(e?.message || "Analysis failed. Check NEXT_PUBLIC_API_URL.");
    } finally {
      setLoading(false);
    }
  }

  async function runMultiCountry() {
    setCountryLoading(true);
    setError("");
    try {
      const result = await post("/analytics/hierarchical", demoCountries);
      setHierarchical(result);
    } catch (e: any) {
      setError(e?.message || "Multi-country analysis failed. Using demo data requires backend access.");
    } finally {
      setCountryLoading(false);
    }
  }

  return (
    <section className="analysis-page">
      <header>
        <h1>Policy Analysis Workflow</h1>
        <p>Use demo time-series while field collection is underway. Replace these values when real Rwanda data is ready.</p>
      </header>

      <div className="card">
        <label>Observed adoption time series</label>
        <textarea value={series} onChange={(e) => setSeries(e.target.value)} rows={4} />
        <div className="button-row">
          <button onClick={runAnalysis} disabled={loading}>{loading ? "Running..." : "Run full analysis"}</button>
          <button onClick={runMultiCountry} disabled={countryLoading}>{countryLoading ? "Running..." : "Run multi-country demo"}</button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="analysis-grid">
        <div className="card chart-card">
          <h2>Bayesian forecast with credible band</h2>
          {bayesianChart.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={bayesianChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Line type="monotone" dataKey="upper" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="mean" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="lower" strokeWidth={1} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <p>No run yet</p>}
        </div>

        <div className="card chart-card">
          <h2>Optimized policy allocation</h2>
          {allocationChart.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={allocationChart}>
                <XAxis dataKey="name" />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Bar dataKey="value" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p>No run yet</p>}
        </div>

        <div className="card">
          <h2>Policy package</h2>
          <pre>{policy ? JSON.stringify(policy, null, 2) : "No run yet"}</pre>
        </div>

        <div className="card chart-card">
          <h2>Multi-country parameter comparison</h2>
          {countryChart.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={countryChart}>
                <XAxis dataKey="country" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="beta" />
                <Bar dataKey="gamma" />
                <Bar dataKey="delta" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p>Run multi-country demo</p>}
        </div>
      </div>
    </section>
  );
}
