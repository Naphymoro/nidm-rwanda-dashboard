"use client";

import { useState } from "react";

export default function IngestPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const res = await fetch("http://localhost:8000/ingest/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ narrative: text }),
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Ingest Narrative</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />
      <button onClick={submit}>Submit</button>

      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
