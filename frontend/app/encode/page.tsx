"use client";

import { useState } from "react";
import { get, post } from "../../lib/api";

export default function EncodePage() {
  const [narratives, setNarratives] = useState<any[]>([]);
  const [encoded, setEncoded] = useState<any[]>([]);

  async function loadNarratives() {
    const data = await get("/narratives");
    setNarratives(data);
  }

  async function runEncoding() {
    const records = narratives.map((n) => ({
      narrative_id: n.id,
      text: n.text,
      metadata: {
        source_type: n.source_type || "database",
        country: n.country,
        admin_unit: n.admin_unit,
      },
      tags: [],
    }));
    const data = await post("/encode", records);
    setEncoded(data);
  }

  return (
    <main>
      <h1>Encoding Review Workspace</h1>
      <p>Convert narratives into model-ready signals and review AI-generated scores.</p>

      <div className="card">
        <button onClick={loadNarratives}>Load narratives</button>{" "}
        <button onClick={runEncoding} disabled={!narratives.length}>Run encoding</button>
      </div>

      <section className="grid">
        <div className="card">
          <h2>Narratives</h2>
          {narratives.map((n) => (
            <article key={n.id} className="record">
              <strong>{n.country || "Unknown country"}</strong>
              <p>{n.text}</p>
            </article>
          ))}
        </div>

        <div className="card">
          <h2>Encoded Signals</h2>
          {encoded.map((e) => (
            <article key={e.narrative_id} className="record">
              <strong>{e.themes.join(", ")}</strong>
              <p>Barrier: {e.adoption_barrier_score} | Trust: {e.trust_score} | Confidence: {e.confidence}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
