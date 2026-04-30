"use client";

import { useState } from "react";
import { post } from "../../lib/api";

export default function EvaluatePage() {
  const [encodingResult, setEncodingResult] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<any>(null);

  async function runEncodingEval() {
    const dummy = {
      ground_truth: [
        { narrative_id: "1", themes: ["health"], adoption_barrier_score: 0.7, trust_score: 0.3 }
      ],
      predictions: [
        { narrative_id: "1", themes: ["health"], adoption_barrier_score: 0.6, trust_score: 0.4 }
      ]
    };
    const res = await post("/evaluate/encoding", dummy);
    setEncodingResult(res);
  }

  async function runSimulationEval() {
    const dummy = {
      points: [
        { day: 0, observed: 0.1, predicted: 0.12 },
        { day: 1, observed: 0.12, predicted: 0.13 }
      ]
    };
    const res = await post("/evaluate/simulation", dummy);
    setSimulationResult(res);
  }

  return (
    <main>
      <h1>Evaluation Dashboard</h1>
      <p>Validate encoding quality and simulation accuracy using research metrics.</p>

      <div className="card">
        <button onClick={runEncodingEval}>Run Encoding Evaluation</button>
        {encodingResult && (
          <pre>{JSON.stringify(encodingResult, null, 2)}</pre>
        )}
      </div>

      <div className="card">
        <button onClick={runSimulationEval}>Run Simulation Evaluation</button>
        {simulationResult && (
          <pre>{JSON.stringify(simulationResult, null, 2)}</pre>
        )}
      </div>
    </main>
  );
}
