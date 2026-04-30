"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import jsPDF from "jspdf";
import { post } from "../../lib/api";

const defaultSeries = "0.12,0.15,0.18,0.22,0.27,0.31,0.36,0.41";

const demoCountries = {
  Rwanda: [0.12, 0.15, 0.18, 0.22, 0.27, 0.31, 0.36, 0.41],
  Kenya: [0.18, 0.2, 0.23, 0.28, 0.32, 0.37, 0.43, 0.49],
  Nigeria: [0.08, 0.1, 0.13, 0.17, 0.21, 0.25, 0.3, 0.34],
};

type Scenario = {
  scenario: string;
  allocation: Record<string, number>;
  cost: number;
  final_adoption: number;
  trajectory: { day: number; adoption: number }[];
};

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
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [countryLoading, setCountryLoading] = useState(false);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [error, setError] = useState("");

  const values = () =>
    series
      .split(",")
      .map((x) => Number(x.trim()))
      .filter((x) => !Number.isNaN(x));

  const selectedAllocation = {
    demand_generation: trustCampaign,
    consumer_subsidy: subsidy,
    supply_chain: supplyChain,
  };

  const bayesianChart = useMemo(() => {
    const mean = bayesian?.trajectory?.mean || [];
    const lower = bayesian?.trajectory?.lower_90 || [];
    const upper = bayesian?.trajectory?.upper_90 || [];
    return mean.map((m: number, i: number) => ({ day: i + 1, mean: m, lower: lower[i], upper: upper[i] }));
  }, [bayesian]);

  const allocationChart = useMemo(() => {
    const allocation = optimization?.best?.allocation || selectedAllocation;
    return Object.keys(allocation).map((key) => ({ name: key.replace("_", " "), value: allocation[key] }));
  }, [optimization, trustCampaign, subsidy, supplyChain]);

  const scenarioChart = useMemo(() => {
    if (!scenarios.length) return [];
    const maxLength = Math.max(...scenarios.map((s) => s.trajectory.length));
    return Array.from({ length: maxLength }, (_, i) => {
      const row: Record<string, number> = { day: i + 1 };
      scenarios.forEach((scenario) => {
        row[scenario.scenario] = scenario.trajectory[i]?.adoption ?? null;
      });
      return row;
    });
  }, [scenarios]);

  const countryChart = useMemo(() => {
    const countries = hierarchical?.countries || {};
    return Object.keys(countries).map((country) => ({
      country,
      beta: countries[country]?.beta?.mean,
      gamma: countries[country]?.gamma?.mean,
      delta: countries[country]?.delta?.mean,
    }));
  }, [hierarchical]);

  async function runBackendScenarios(nextParams = params, opt = optimization) {
    setScenarioLoading(true);
    setError("");
    try {
      const optimizedAllocation = opt?.best?.allocation || {
        demand_generation: 0.7,
        consumer_subsidy: 0.8,
        supply_chain: 0.6,
      };
      const res = await post("/analytics/scenario-simulate", {
        base_params: nextParams,
        horizon: 180,
        scenarios: {
          Baseline: { demand_generation: 0, consumer_subsidy: 0, supply_chain: 0 },
          "Selected policy": selectedAllocation,
          Optimized: optimizedAllocation,
        },
      });
      setScenarios(res.scenarios || []);
    } catch (e: any) {
      setError(e?.message || "Scenario simulation failed. Check NEXT_PUBLIC_API_URL.");
    } finally {
      setScenarioLoading(false);
    }
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

      const allocation = opt?.best?.allocation || selectedAllocation;
      const mapped = await post("/analytics/policy-map", allocation);
      setPolicy(mapped);

      await runBackendScenarios(learned, opt);
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

  function exportPDF() {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("NIDM Policy Analysis Report", 14, 18);
    doc.setFontSize(10);
    doc.text(`Observed adoption series: ${series}`, 14, 30);
    doc.text(`Budget: ${budget.toFixed(2)}`, 14, 38);
    doc.text(`Selected controls: trust=${trustCampaign.toFixed(2)}, subsidy=${subsidy.toFixed(2)}, supply=${supplyChain.toFixed(2)}`, 14, 46);

    let y = 60;
    doc.setFontSize(12);
    doc.text("Scenario outcomes", 14, y);
    y += 8;
    doc.setFontSize(10);
    scenarios.forEach((s) => {
      doc.text(`${s.scenario}: final adoption=${s.final_adoption.toFixed(3)}, cost=${s.cost.toFixed(3)}`, 14, y);
      y += 7;
    });

    y += 6;
    doc.setFontSize(12);
    doc.text("Recommended policy package", 14, y);
    y += 8;
    doc.setFontSize(9);
    const packageText = JSON.stringify(policy || {}, null, 2).slice(0, 2200);
    doc.text(doc.splitTextToSize(packageText, 180), 14, y);
    doc.save("nidm-policy-report.pdf");
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
          <button onClick={() => runBackendScenarios()} disabled={scenarioLoading}>{scenarioLoading ? "Running..." : "Run backend scenarios"}</button>
          <button onClick={runMultiCountry} disabled={countryLoading}>{countryLoading ? "Running..." : "Run multi-country demo"}</button>
          <button onClick={exportPDF}>Export PDF report</button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="analysis-grid">
        <div className="card chart-card">
          <h2>Backend-driven scenario comparison</h2>
          {scenarioChart.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={scenarioChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Legend />
                {scenarios.map((scenario) => (
                  <Line key={scenario.scenario} type="monotone" dataKey={scenario.scenario} strokeWidth={2} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : <p>Run backend scenarios to compare Baseline, Selected policy, and Optimized trajectories.</p>}
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
                <Legend />
                <Line type="monotone" dataKey="upper" strokeWidth={1} dot={false} />
                <Line type="monotone" dataKey="mean" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="lower" strokeWidth={1} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <p>No Bayesian run yet.</p>}
        </div>

        <div className="card chart-card">
          <h2>Optimized policy allocation</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={allocationChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>Scenario outcomes</h2>
          <pre>{scenarios.length ? JSON.stringify(scenarios.map(({ scenario, cost, final_adoption, allocation }) => ({ scenario, cost, final_adoption, allocation })), null, 2) : "No scenario run yet"}</pre>
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
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="beta" />
                <Bar dataKey="gamma" />
                <Bar dataKey="delta" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p>Run multi-country demo.</p>}
        </div>
      </div>
    </section>
  );
}
