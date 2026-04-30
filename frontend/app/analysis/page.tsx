"use client";

import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import jsPDF from "jspdf";
import { post } from "../../lib/api";

const defaultSeries = "0.12,0.15,0.18,0.22,0.27,0.31,0.36,0.41";
const demoCountries = {
  Rwanda: [0.12, 0.15, 0.18, 0.22, 0.27, 0.31, 0.36, 0.41],
  Kenya: [0.18, 0.2, 0.23, 0.28, 0.32, 0.37, 0.43, 0.49],
  Nigeria: [0.08, 0.1, 0.13, 0.17, 0.21, 0.25, 0.3, 0.34],
};
const narrativeTrace = {
  demand_generation: ["Low confidence in new cooking technologies requires trusted community demonstrations.", "Peer champions and radio messaging can reduce misinformation and improve trust."],
  consumer_subsidy: ["Affordability barriers appear where upfront stove or fuel costs delay adoption.", "Subsidy intensity should target lower-income households first to improve equity."],
  supply_chain: ["Fuel access and maintenance gaps can reduce continued use after initial adoption.", "Last-mile supply reliability and repair capacity reduce resistance over time."],
};
type Scenario = { scenario: string; allocation: Record<string, number>; cost: number; final_adoption: number; trajectory: { day: number; adoption: number }[] };
function fmt(value: number | undefined, digits = 3) { return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "n/a"; }
function allocationLabel(key: string) { return key.replace(/_/g, " "); }
function simulatePreview(start: number, allocation: Record<string, number>, horizon = 60) {
  let adoption = Math.max(0, Math.min(1, start));
  const influence = 0.035 + 0.035 * allocation.demand_generation + 0.045 * allocation.consumer_subsidy + 0.03 * allocation.supply_chain;
  const resistance = Math.max(0.004, 0.018 - 0.007 * allocation.supply_chain - 0.004 * allocation.consumer_subsidy);
  return Array.from({ length: horizon }, (_, i) => {
    adoption = Math.max(0, Math.min(1, adoption + influence * adoption * (1 - adoption) - resistance * adoption));
    return { day: i + 1, live_preview: adoption };
  });
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
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [focusedScenario, setFocusedScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [countryLoading, setCountryLoading] = useState(false);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [error, setError] = useState("");

  const values = () => series.split(",").map((x) => Number(x.trim())).filter((x) => !Number.isNaN(x));
  const selectedAllocation = { demand_generation: trustCampaign, consumer_subsidy: subsidy, supply_chain: supplyChain };
  const lastObserved = values().at(-1) ?? 0.25;

  const livePreview = useMemo(() => simulatePreview(lastObserved, selectedAllocation), [lastObserved, trustCampaign, subsidy, supplyChain]);
  const previewFinal = livePreview.at(-1)?.live_preview;
  const previewDelta = typeof previewFinal === "number" ? previewFinal - lastObserved : undefined;

  const bayesianChart = useMemo(() => {
    const mean = bayesian?.trajectory?.mean || [];
    const lower = bayesian?.trajectory?.lower_90 || [];
    const upper = bayesian?.trajectory?.upper_90 || [];
    return mean.map((m: number, i: number) => ({ day: i + 1, mean: m, lower: lower[i], upper: upper[i] }));
  }, [bayesian]);

  const allocationChart = useMemo(() => {
    const allocation = optimization?.best?.allocation || selectedAllocation;
    return Object.keys(allocation).map((key) => ({ name: allocationLabel(key), value: allocation[key] }));
  }, [optimization, trustCampaign, subsidy, supplyChain]);

  const scenarioChart = useMemo(() => {
    if (!scenarios.length) return [];
    const maxLength = Math.max(...scenarios.map((s) => s.trajectory.length));
    return Array.from({ length: maxLength }, (_, i) => {
      const row: Record<string, number | null> = { day: i + 1 };
      scenarios.forEach((scenario) => { row[scenario.scenario] = scenario.trajectory[i]?.adoption ?? null; });
      return row;
    });
  }, [scenarios]);

  const countryChart = useMemo(() => {
    const countries = hierarchical?.countries || {};
    return Object.keys(countries).map((country) => ({ country, beta: countries[country]?.beta?.mean, gamma: countries[country]?.gamma?.mean, delta: countries[country]?.delta?.mean }));
  }, [hierarchical]);

  const scenarioRanking = useMemo(() => [...scenarios].map((s) => {
    const efficiency = s.cost > 0 ? s.final_adoption / s.cost : s.final_adoption;
    const robustnessPenalty = bayesian?.parameters?.gamma ? (bayesian.parameters.gamma.q95 - bayesian.parameters.gamma.q05) : 0.1;
    const score = s.final_adoption - 0.18 * Math.min(1, s.cost) - 0.12 * robustnessPenalty;
    return { ...s, efficiency, score };
  }).sort((a, b) => b.score - a.score), [scenarios, bayesian]);

  const interpretation = useMemo(() => {
    const baseline = scenarios.find((s) => s.scenario === "Baseline");
    const selected = scenarios.find((s) => s.scenario === "Selected policy");
    const optimized = scenarios.find((s) => s.scenario === "Optimized");
    const best = scenarioRanking[0] || optimized || selected;
    const start = lastObserved;
    const dominantAllocation = optimization?.best?.allocation || selectedAllocation;
    const dominantLever = Object.entries(dominantAllocation).sort((a: any, b: any) => b[1] - a[1])[0];
    const uncertainty = [["diffusion", bayesian?.parameters?.beta?.q95 - bayesian?.parameters?.beta?.q05], ["intervention response", bayesian?.parameters?.gamma?.q95 - bayesian?.parameters?.gamma?.q05], ["resistance", bayesian?.parameters?.delta?.q95 - bayesian?.parameters?.delta?.q05]].filter((x: any) => Number.isFinite(x[1])).sort((a: any, b: any) => b[1] - a[1]);
    const widest = uncertainty[0];
    const highUncertainty = widest && widest[1] > 0.2;
    if (!scenarios.length) return { headline: "Live preview is active. Run analysis to validate with backend simulation.", adoptionChange: `${fmt(start)} → ${fmt(previewFinal)} (${previewDelta && previewDelta >= 0 ? "+" : ""}${fmt(previewDelta)} preview)`, recommendation: "Adjust sliders to preview policy direction, then run full analysis for calibrated ranking.", uncertaintyAdvice: "No Bayesian uncertainty assessment yet.", traceability: ["Traceability appears after policy allocation is selected."], driver: "Preview uses selected levers only.", evidence: "No backend scenario outputs yet.", confidence: "Preview" };
    const baselineGain = best && baseline ? best.final_adoption - baseline.final_adoption : undefined;
    const traceKey = dominantLever?.[0] as keyof typeof narrativeTrace;
    return {
      headline: best ? `${best.scenario} is currently the top-ranked strategy.` : "Scenario comparison is available.",
      adoptionChange: `${fmt(start)} → ${fmt(best?.final_adoption)} (${baselineGain && baselineGain >= 0 ? "+" : ""}${fmt(baselineGain)} vs baseline)`,
      recommendation: highUncertainty ? "Use this as a planning hypothesis and prioritize validation data before operational rollout." : "Use the top-ranked scenario as the preferred planning case, subject to field validation.",
      uncertaintyAdvice: widest ? `${highUncertainty ? "High" : "Moderate/low"} uncertainty in ${widest[0]} (90% width ${fmt(widest[1] as number)}).` : "Run Bayesian inference to quantify uncertainty.",
      driver: dominantLever ? `${allocationLabel(dominantLever[0])} is the largest lever (${fmt(dominantLever[1] as number, 2)}).` : "No dominant lever identified.",
      traceability: narrativeTrace[traceKey] || ["Traceability will improve when real narratives are linked to the model run."],
      evidence: `Baseline=${fmt(baseline?.final_adoption)}, Selected=${fmt(selected?.final_adoption)}, Optimized=${fmt(optimized?.final_adoption)}.`,
      confidence: highUncertainty ? "Provisional" : "Moderate",
    };
  }, [scenarios, scenarioRanking, optimization, bayesian, trustCampaign, subsidy, supplyChain, series, previewFinal, previewDelta]);

  async function runBackendScenarios(nextParams = params, opt = optimization) {
    setScenarioLoading(true); setError("");
    try {
      const optimizedAllocation = opt?.best?.allocation || { demand_generation: 0.7, consumer_subsidy: 0.8, supply_chain: 0.6 };
      const res = await post("/analytics/scenario-simulate", { base_params: nextParams, horizon: 180, scenarios: { Baseline: { demand_generation: 0, consumer_subsidy: 0, supply_chain: 0 }, "Selected policy": selectedAllocation, Optimized: optimizedAllocation } });
      setScenarios(res.scenarios || []);
      setFocusedScenario(null);
    } catch (e: any) { setError(e?.message || "Scenario simulation failed. Check NEXT_PUBLIC_API_URL."); }
    finally { setScenarioLoading(false); }
  }

  async function runAnalysis() {
    setLoading(true); setError("");
    try {
      const bayes = await post("/analytics/bayesian", values()); setBayesian(bayes);
      const learned = { beta: bayes?.parameters?.beta?.mean ?? params.beta, gamma: bayes?.parameters?.gamma?.mean ?? params.gamma, delta: bayes?.parameters?.delta?.mean ?? params.delta };
      setParams(learned);
      const opt = await post("/analytics/multi-objective", learned); setOptimization(opt);
      const allocation = opt?.best?.allocation || selectedAllocation;
      const mapped = await post("/analytics/policy-map", allocation); setPolicy(mapped);
      await runBackendScenarios(learned, opt);
    } catch (e: any) { setError(e?.message || "Analysis failed. Check NEXT_PUBLIC_API_URL."); }
    finally { setLoading(false); }
  }

  async function runMultiCountry() {
    setCountryLoading(true); setError("");
    try { const result = await post("/analytics/hierarchical", demoCountries); setHierarchical(result); }
    catch (e: any) { setError(e?.message || "Multi-country analysis failed. Using demo data requires backend access."); }
    finally { setCountryLoading(false); }
  }

  function exportPDF() {
    const doc = new jsPDF();
    doc.setFontSize(16); doc.text("NIDM Policy Analysis Report", 14, 18);
    doc.setFontSize(10); doc.text(`Observed adoption series: ${series}`, 14, 30); doc.text(`Budget: ${budget.toFixed(2)}`, 14, 38); doc.text(`Selected controls: trust=${trustCampaign.toFixed(2)}, subsidy=${subsidy.toFixed(2)}, supply=${supplyChain.toFixed(2)}`, 14, 46);
    let y = 60; doc.setFontSize(12); doc.text("Decision recommendation", 14, y); y += 8; doc.setFontSize(10);
    [interpretation.headline, interpretation.adoptionChange, interpretation.driver, interpretation.uncertaintyAdvice, interpretation.recommendation].forEach((line) => { doc.text(doc.splitTextToSize(line, 180), 14, y); y += 9; });
    y += 4; doc.setFontSize(12); doc.text("Scenario ranking", 14, y); y += 8;
    scenarioRanking.forEach((s, i) => { doc.text(`${i + 1}. ${s.scenario}: score=${fmt(s.score)}, adoption=${fmt(s.final_adoption)}, cost=${fmt(s.cost)}`, 14, y); y += 7; });
    doc.save("nidm-policy-report.pdf");
  }

  return (
    <section className="analysis-page" style={{ padding: 20 }}>
      <header style={{ marginBottom: 16 }}>
        <h1>Policy Analysis Workflow</h1>
        <p>Decision-first interface for simulation, uncertainty, traceability, and policy ranking. Demo data is used until field data is available.</p>
      </header>
      {error && <p className="error">{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "280px minmax(360px, 1fr) minmax(420px, 1.4fr)", gap: 16, alignItems: "start" }}>
        <aside className="card" style={{ display: "grid", gap: 12 }}>
          <h2>Inputs</h2>
          <label>Adoption series</label>
          <textarea value={series} onChange={(e) => setSeries(e.target.value)} rows={5} />
          <label>Budget {budget.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={budget} onChange={(e) => setBudget(Number(e.target.value))} /></label>
          <label>Trust campaign {trustCampaign.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={trustCampaign} onChange={(e) => setTrustCampaign(Number(e.target.value))} /></label>
          <label>Subsidy {subsidy.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={subsidy} onChange={(e) => setSubsidy(Number(e.target.value))} /></label>
          <label>Supply chain {supplyChain.toFixed(2)}<input type="range" min="0" max="1" step="0.05" value={supplyChain} onChange={(e) => setSupplyChain(Number(e.target.value))} /></label>
          <div className="card" style={{ padding: 12, boxShadow: "none" }}>
            <h2>Live preview</h2>
            <p><strong>Projected:</strong> {fmt(lastObserved)} → {fmt(previewFinal)} ({previewDelta && previewDelta >= 0 ? "+" : ""}{fmt(previewDelta)})</p>
            <ResponsiveContainer width="100%" height={120}><LineChart data={livePreview}><XAxis dataKey="day" hide /><YAxis domain={[0, 1]} hide /><Tooltip /><Line type="monotone" dataKey="live_preview" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer>
          </div>
          <button onClick={runAnalysis} disabled={loading}>{loading ? "Running..." : "Run full analysis"}</button>
          <button onClick={() => runBackendScenarios()} disabled={scenarioLoading}>{scenarioLoading ? "Running..." : "Run scenarios"}</button>
          <button onClick={runMultiCountry} disabled={countryLoading}>{countryLoading ? "Running..." : "Multi-country demo"}</button>
          <button onClick={exportPDF}>Export PDF</button>
        </aside>

        <main style={{ display: "grid", gap: 16 }}>
          <section className="card" style={{ border: "2px solid #2563eb" }}>
            <h2>Recommended decision</h2>
            <h3>{interpretation.headline}</h3>
            <p><strong>Expected change:</strong> {interpretation.adoptionChange}</p>
            <p><strong>Confidence:</strong> {interpretation.confidence}</p>
            <p><strong>Primary lever:</strong> {interpretation.driver}</p>
            <p><strong>Uncertainty:</strong> {interpretation.uncertaintyAdvice}</p>
            <p><strong>Recommendation:</strong> {interpretation.recommendation}</p>
            <p><strong>Evidence:</strong> {interpretation.evidence}</p>
          </section>
          <section className="card">
            <h2>Scenario ranking</h2>
            {scenarioRanking.length ? <table><thead><tr><th>Rank</th><th>Scenario</th><th>Adoption</th><th>Cost</th><th>Score</th></tr></thead><tbody>{scenarioRanking.map((s, i) => <tr key={s.scenario} onMouseEnter={() => setFocusedScenario(s.scenario)} onMouseLeave={() => setFocusedScenario(null)}><td>{i + 1}</td><td>{s.scenario}</td><td>{fmt(s.final_adoption)}</td><td>{fmt(s.cost)}</td><td>{fmt(s.score)}</td></tr>)}</tbody></table> : <p>No ranking yet.</p>}
          </section>
          <section className="card"><h2>Why this recommendation?</h2><ul>{interpretation.traceability.map((item, i) => <li key={i}>{item}</li>)}</ul></section>
        </main>

        <aside style={{ display: "grid", gap: 16 }}>
          <section className="card chart-card"><h2>Scenario comparison</h2>{scenarioChart.length ? <ResponsiveContainer width="100%" height={260}><LineChart data={scenarioChart}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="day" /><YAxis domain={[0, 1]} /><Tooltip /><Legend />{scenarios.map((s) => <Line key={s.scenario} type="monotone" dataKey={s.scenario} strokeWidth={focusedScenario === s.scenario || !focusedScenario ? 3 : 1} opacity={focusedScenario && focusedScenario !== s.scenario ? 0.28 : 1} dataKey={s.scenario} dot={false} />)}</LineChart></ResponsiveContainer> : <p>Run scenarios to view trajectories.</p>}</section>
          <section className="card chart-card"><h2>Bayesian credible band</h2>{bayesianChart.length ? <ResponsiveContainer width="100%" height={220}><LineChart data={bayesianChart}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="day" /><YAxis domain={[0, 1]} /><Tooltip /><Legend /><Line type="monotone" dataKey="upper" strokeWidth={1} dot={false} /><Line type="monotone" dataKey="mean" strokeWidth={2} dot={false} /><Line type="monotone" dataKey="lower" strokeWidth={1} dot={false} /></LineChart></ResponsiveContainer> : <p>No Bayesian run yet.</p>}</section>
          <section className="card chart-card"><h2>Policy allocation</h2><ResponsiveContainer width="100%" height={220}><BarChart data={allocationChart}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis domain={[0, 1]} /><Tooltip /><Bar dataKey="value" /></BarChart></ResponsiveContainer></section>
          <section className="card chart-card"><h2>Multi-country comparison</h2>{countryChart.length ? <ResponsiveContainer width="100%" height={220}><BarChart data={countryChart}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="country" /><YAxis /><Tooltip /><Legend /><Bar dataKey="beta" /><Bar dataKey="gamma" /><Bar dataKey="delta" /></BarChart></ResponsiveContainer> : <p>Run multi-country demo.</p>}</section>
        </aside>
      </div>
    </section>
  );
}
