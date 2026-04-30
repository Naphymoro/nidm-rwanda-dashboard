"use client";

import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { post } from "../../lib/api";

export default function SimulatePage() {
  const [days, setDays] = useState(180);
  const [modelMode, setModelMode] = useState("hybrid");
  const [result, setResult] = useState<any>(null);

  async function runSimulation() {
    const data = await post("/simulate", {
      model_mode: modelMode,
      horizon_days: days,
      parameters: {},
    });
    setResult(data);
  }

  return (
    <main>
      <h1>Simulation Console</h1>
      <p>Configure the digital twin and inspect adoption trajectories over time.</p>

      <div className="card controls">
        <label>
          Model mode
          <select value={modelMode} onChange={(e) => setModelMode(e.target.value)}>
            <option value="compartmental">Compartmental</option>
            <option value="agent_based">Agent-based</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>

        <label>
          Horizon days
          <input
            type="number"
            value={days}
            min={1}
            max={3650}
            onChange={(e) => setDays(Number(e.target.value))}
          />
        </label>

        <button onClick={runSimulation}>Run simulation</button>
      </div>

      {result && (
        <div className="card chart-card">
          <h2>Adoption trajectory</h2>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={result.trajectory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="adoption" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <p className="hint">Mode: {result.model_mode}. Assumption: {result.assumptions?.note}</p>
        </div>
      )}
    </main>
  );
}
