"use client";

import { useEffect, useMemo, useState } from "react";
import { get } from "../../lib/api";

export default function ExplorerPage() {
  const [narratives, setNarratives] = useState<any[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    get("/narratives").then(setNarratives).catch(() => setNarratives([]));
  }, []);

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return narratives.filter((n) =>
      [n.text, n.country, n.admin_unit, n.source_type]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [narratives, query]);

  return (
    <main>
      <h1>Narrative Explorer</h1>
      <p>Browse stored narratives by country, administrative unit, source, or keyword.</p>

      <div className="card">
        <input
          className="input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search narratives, country, admin unit..."
        />
      </div>

      <div className="card">
        <h2>{filtered.length} narratives</h2>
        {filtered.map((n) => (
          <article key={n.id} className="record">
            <div className="meta">
              <span>{n.country || "Unknown country"}</span>
              <span>{n.admin_unit || "No admin unit"}</span>
              <span>{n.source_type || "unknown source"}</span>
            </div>
            <p>{n.text}</p>
          </article>
        ))}
      </div>
    </main>
  );
}
