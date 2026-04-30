"use client";

import { useState } from "react";
import { post } from "../../lib/api";

export default function SimulatePage() {
  const [days, setDays] = useState(180);
  const [result, setResult] = useState<any>(null);

  async function runSimulation() {
    const data = await post("/simulate", {
      model_mode: "hybrid",
      horizon_days: days,
      parameters: {},
    });
    setResult(data);
  }

  return (
    <main>
      <h1>Simulation Console</h1>
      <div className="card">
        <label>Horizon (days)</label>
        <input
          type="number"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        />
        <button onClick={runSimulation}>Run simulation</button>
      </div>

      {result && (
        <div className="card">
          <h2>Trajectory</h2>
          <pre>{JSON.stringify(result.trajectory.slice(0, 20), null, 2)}</pre>
        </div>
      )}
    </main>
  );
}
