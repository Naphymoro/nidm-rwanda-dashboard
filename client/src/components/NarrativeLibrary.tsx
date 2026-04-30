import React, { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Search,
  Filter,
  SortAsc,
  SortDesc,
  FileSpreadsheet,
  FileText,
  Trash2,
  Library,
} from "lucide-react";
import {
  ParsedNarrative,
  SortKey,
  filterNarratives,
  sortNarratives,
} from "@/lib/narrativeParser";

interface NarrativeLibraryProps {
  narratives: ParsedNarrative[];
  onRemove?: (id: string) => void;
  onClear?: () => void;
}

export default function NarrativeLibrary({
  narratives,
  onRemove,
  onClear,
}: NarrativeLibraryProps) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<"all" | "csv" | "narrative">("all");
  const [minPhi, setMinPhi] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("phi");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const visible = useMemo(() => {
    const filtered = filterNarratives(narratives, query, source, minPhi);
    return sortNarratives(filtered, sortKey, sortDir);
  }, [narratives, query, source, minPhi, sortKey, sortDir]);

  const stats = useMemo(() => {
    if (narratives.length === 0) {
      return { total: 0, csv: 0, narrative: 0, avgPhi: 0, topPhi: 0 };
    }
    const csv = narratives.filter((n) => n.source === "csv").length;
    const narrative = narratives.filter((n) => n.source === "narrative").length;
    const avgPhi =
      narratives.reduce((s, n) => s + n.phi, 0) / narratives.length;
    const topPhi = Math.max(...narratives.map((n) => n.phi));
    return {
      total: narratives.length,
      csv,
      narrative,
      avgPhi: Math.round(avgPhi * 10000) / 10000,
      topPhi,
    };
  }, [narratives]);

  return (
    <Card className="glass-dark border-border/50 p-6 glow-primary">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Library className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-bold neon-text">Narrative Library</h3>
        </div>
        {narratives.length > 0 && onClear && (
          <button
            onClick={onClear}
            className="text-xs text-muted-foreground hover:text-destructive transition-colors flex items-center gap-1"
          >
            <Trash2 className="w-3 h-3" /> Clear all
          </button>
        )}
      </div>

      {/* Stats Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
        <div className="bg-background/40 rounded-md p-3 border border-border/40">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Total</p>
          <p className="text-xl font-bold text-foreground">{stats.total}</p>
        </div>
        <div className="bg-background/40 rounded-md p-3 border border-border/40">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">CSV rows</p>
          <p className="text-xl font-bold text-primary">{stats.csv}</p>
        </div>
        <div className="bg-background/40 rounded-md p-3 border border-border/40">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Narratives</p>
          <p className="text-xl font-bold text-accent">{stats.narrative}</p>
        </div>
        <div className="bg-background/40 rounded-md p-3 border border-border/40">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Avg Φ</p>
          <p className="text-xl font-bold text-foreground font-mono">
            {stats.avgPhi.toFixed(3)}
          </p>
        </div>
        <div className="bg-background/40 rounded-md p-3 border border-border/40">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Top Φ</p>
          <p className="text-xl font-bold text-accent font-mono">
            {stats.topPhi.toFixed(3)}
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col lg:flex-row gap-3 mb-5">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by label, key, quote, type, or target..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9"
          />
        </div>

        <div className="flex items-center gap-2 bg-background/40 border border-border/60 rounded-md p-1">
          <Filter className="w-4 h-4 text-muted-foreground ml-2" />
          {(["all", "csv", "narrative"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSource(s)}
              className={`px-3 py-1 rounded text-xs font-semibold capitalize transition-all ${
                source === s
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground whitespace-nowrap">Min Φ</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={minPhi}
            onChange={(e) => setMinPhi(Number(e.target.value))}
            className="w-24 accent-primary"
          />
          <span className="text-xs text-foreground font-mono w-10">{minPhi.toFixed(2)}</span>
        </div>

        <div className="flex items-center gap-2 bg-background/40 border border-border/60 rounded-md p-1">
          {(["phi", "label", "uploadedAt"] as SortKey[]).map((k) => (
            <button
              key={k}
              onClick={() => setSortKey(k)}
              className={`px-3 py-1 rounded text-xs font-semibold capitalize transition-all ${
                sortKey === k
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {k === "uploadedAt" ? "Date" : k === "phi" ? "Φ" : "Name"}
            </button>
          ))}
          <button
            onClick={() => setSortDir(sortDir === "asc" ? "desc" : "asc")}
            className="p-1 rounded text-muted-foreground hover:text-foreground"
            title={sortDir === "asc" ? "Ascending" : "Descending"}
          >
            {sortDir === "asc" ? (
              <SortAsc className="w-4 h-4" />
            ) : (
              <SortDesc className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {narratives.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-border/50 rounded-md">
          <Library className="w-10 h-10 mx-auto text-muted-foreground/50 mb-3" />
          <p className="text-sm text-muted-foreground">
            No narratives loaded yet. Upload a CSV or narrative file to populate the library.
          </p>
        </div>
      ) : visible.length === 0 ? (
        <div className="text-center py-8 text-sm text-muted-foreground">
          No narratives match the current filters.
        </div>
      ) : (
        <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
          {visible.map((n) => (
            <div
              key={n.id}
              className="group bg-background/40 border border-border/40 rounded-md p-4 hover:border-primary/60 transition-all animate-fade-in-up"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {n.source === "csv" ? (
                      <FileSpreadsheet className="w-4 h-4 text-primary flex-shrink-0" />
                    ) : (
                      <FileText className="w-4 h-4 text-accent flex-shrink-0" />
                    )}
                    <h4 className="font-semibold text-sm text-foreground truncate">
                      {n.label}
                    </h4>
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-background/50 px-1.5 py-0.5 rounded border border-border/40 flex-shrink-0">
                      {n.type}
                    </span>
                  </div>
                  {n.quote && (
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                      “{n.quote}”
                    </p>
                  )}
                  <div className="flex flex-wrap gap-3 text-[11px] font-mono">
                    <span className="text-muted-foreground">
                      E:{" "}
                      <span className="text-foreground">{n.E.toFixed(2)}</span>
                    </span>
                    <span className="text-muted-foreground">
                      C:{" "}
                      <span className="text-foreground">{n.C.toFixed(2)}</span>
                    </span>
                    <span className="text-muted-foreground">
                      τ:{" "}
                      <span className="text-foreground">{n.tau.toFixed(2)}</span>
                    </span>
                    <span className="text-muted-foreground">
                      κ:{" "}
                      <span className="text-foreground">
                        {n.kappa.toFixed(2)}
                      </span>
                    </span>
                    <span className="text-muted-foreground">
                      targets:{" "}
                      <span className="text-foreground">{n.targets}</span>
                    </span>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2 flex-shrink-0">
                  <div
                    className={`px-3 py-1 rounded-md text-sm font-bold font-mono ${
                      n.phi >= 0.7
                        ? "bg-accent/20 text-accent border border-accent/40"
                        : n.phi >= 0.5
                        ? "bg-primary/15 text-primary border border-primary/40"
                        : "bg-background/40 text-muted-foreground border border-border/40"
                    }`}
                    title="Composite narrative strength Φ"
                  >
                    Φ {n.phi.toFixed(3)}
                  </div>
                  {onRemove && (
                    <button
                      onClick={() => onRemove(n.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                      title="Remove narrative"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
