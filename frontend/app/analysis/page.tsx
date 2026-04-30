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

function projectSeries(start: number, influence: number, horizon = 24) {
  let adoption = start;
  const rows = [];
  for (let day = 1; day <= horizon; day++) {
    adoption = Math.min(1, adoption + influence * adoption * (1 - adoption));
    rows.push({ day, adoption });
  }
  return rows;
}

export default function AnalysisPage() {
  const [series, setSeries] = useState(defaultSeries);
  const [budget, setBudget] = useState(0.7);
  const [trustCampaign, setTrustCampaign] = useState(0.4);
  const [subsidy, setSubsidy] = useState(0.5);
  const [supplyChain, setSupplyChain] = useState(0.3);
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
    const allocation = optimization?.best?.allocation || { demand_generation: trustCampaign, consumer_subsidy: subsidy, supply_chain: supplyChain };
    return Object.keys(allocation).map((key) => ({ name: key.replace("_", " "), value: allocation[key] }));
  }, [optimization, trustCampaign, subsidy, supplyChain]);

  const scenarioChart = useMemo(() => {
    const last = values().at(-1) ?? 0.25;
    const baseline = projectSeries(last, 0.07);
    const user = projectSeries(last, 0.07 + 0.04 * trustCampaign + 0.05 * subsidy + 0.035 * supplyChain);
    const optimizedInfluence = optimization?.best?.final_adoption ? 0.16 : 0.13;
    const optimized = projectSeries(last, optimizedInfluence);
    return baseline.map((row, i) => ({
      day: row.day,
      baseline: row.adoption,
      selected_policy: user[i].adoption,
      optimized: optimized[i].adoption,
    }));
  }, [series, trustCampaign, subsidy, supplyChain, optimization]);

  const countryChart = useMemo(() => {
    const countries = hierarchical?.countries || {};
    return Object.keys(countries).map((country) => ({
      country,
      beta: countries[country]?.beta?.mean,
      gamma: countries[country]?.gamma?.mean,
      delta: countries[country]?.delta?.mean,
    }));
  }, [hierarchical]);

  function exportReport() {
    const report = [
      "NIDM Policy Analysis Report",
      "===========================",
      `Observed adoption series: ${series}`,
      `Budget setting: ${budget}`,
      `Manual policy controls: trust campaign=${trustCampaign}, subsidy=${subsidy}, supply chain=${supplyChain}`,
      "",
      "Bayesian parameters:",
      JSON.stringify(bayesian?.parameters || {}, null, 2),
      "",
      "Optimized allocation:",
      JSON.stringify(optimization?.best || {}, null, 2),
      "",
      "Policy package:",
      JSON.stringify(policy || {}, null, 2),
    ].join("\n");
    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "nidm-policy-report.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

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
      const allocation = opt?.best?.allocation || { demand_generation: trustCampaign, consumer_subsidy: subsidy, supply_chain: supplyChain };
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
        <div className="slider-grid">
          <label>Budget {budget.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={budget} onChange={(e) => setBudget(Number(e.target.value))} /></label>
          <label>Trust campaign {trustCampaign.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={trustCampaign} onChange={(e) => setTrustCampaign(Number(e.target.value))} /></label>
          <label>Subsidy {subsidy.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={subsidy} onChange={(e) => setSubsidy(Number(e.target.value))} /></label>
          <label>Supply chain {supplyChain.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={supplyChain} onChange={(e) => setSupplyChain(Number(e.target.value))} /></label>
        </div>
        <div className="button-row">
          <button onClick={runAnalysis} disabled={loading}>{loading ? "Running..." : "Run full analysis"}</button>
          <button onClick={runMultiCountry} disabled={countryLoading}>{countryLoading ? "Running..." : "Run multi-country demo"}</button>
          <button onClick={exportReport}>Export policymaker report</button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="analysis-grid">
        <div className="card chart-card">
          <h2>Scenario comparison</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={scenarioChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="baseline" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="selected_policy" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="optimized" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

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
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={allocationChart}>
              <XAxis dataKey="name" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
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
