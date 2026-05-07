import React, { useEffect, useMemo, useState } from "react";
import {
  Check,
  FileJson,
  FileSpreadsheet,
  FileText,
  Filter,
  GitCompareArrows,
  Library,
  Search,
  SortAsc,
  SortDesc,
  Trash2,
  X,
} from "lucide-react";
import {
  filterNarratives,
  sortNarratives,
  type ParsedNarrative,
  type SortKey,
} from "@/lib/narrativeParser";
import NarrativeCompare from "./NarrativeCompare";

interface NarrativeLibraryProps {
  narratives: ParsedNarrative[];
  onRemove?: (id: string) => void;
  onClear?: () => void;
}

type SourceFilter = "all" | ParsedNarrative["source"];
const MAX_SELECTION = 2;

export default function NarrativeLibrary({
  narratives,
  onRemove,
  onClear,
}: NarrativeLibraryProps) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<SourceFilter>("all");
  const [minPhi, setMinPhi] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("phi");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [compareOpen, setCompareOpen] = useState(false);

  useEffect(() => {
    setSelectedIds((prev) => prev.filter((id) => narratives.some((n) => n.id === id)));
  }, [narratives]);

  const visible = useMemo(() => {
    return sortNarratives(
      filterNarratives(narratives, query, source, minPhi),
      sortKey,
      sortDir
    );
  }, [narratives, query, source, minPhi, sortKey, sortDir]);

  const stats = useMemo(() => {
    const avgPhi = narratives.length
      ? narratives.reduce((sum, n) => sum + n.phi, 0) / narratives.length
      : 0;
    const topPhi = narratives.length ? Math.max(...narratives.map((n) => n.phi)) : 0;
    return {
      total: narratives.length,
      csv: narratives.filter((n) => n.source === "csv").length,
      narrative: narratives.filter((n) => n.source === "narrative").length,
      sdmx: narratives.filter((n) => n.source === "sdmx").length,
      avgPhi,
      topPhi,
    };
  }, [narratives]);

  const selectedNarratives = useMemo(
    () =>
      selectedIds
        .map((id) => narratives.find((n) => n.id === id))
        .filter((n): n is ParsedNarrative => n !== undefined),
    [selectedIds, narratives]
  );

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((item) => item !== id);
      if (prev.length >= MAX_SELECTION) return [...prev.slice(1), id];
      return [...prev, id];
    });
  };

  const canCompare = selectedNarratives.length === 2;

  return (
    <section className="nidm-card p-5">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono-data text-[10px] uppercase tracking-[1.5px] text-[var(--t4)]">
            Curated evidence
          </p>
          <div className="mt-1 flex items-center gap-2">
            <Library className="h-5 w-5 text-[var(--indigoL)]" />
            <h3 className="font-syne text-xl font-bold">Narrative library</h3>
          </div>
        </div>
        {narratives.length > 0 && onClear && (
          <button
            type="button"
            onClick={onClear}
            className="inline-flex items-center gap-2 rounded-lg border border-[rgba(255,107,53,.25)] bg-[rgba(255,107,53,.08)] px-3 py-2 text-xs font-semibold text-[var(--flame)] transition hover:bg-[rgba(255,107,53,.14)]"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear all
          </button>
        )}
      </div>

      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <LibraryStat label="Total" value={stats.total.toString()} accent="var(--t1)" />
        <LibraryStat label="CSV rows" value={stats.csv.toString()} accent="var(--gold)" />
        <LibraryStat label="Text" value={stats.narrative.toString()} accent="var(--verdant)" />
        <LibraryStat label="SDMX" value={stats.sdmx.toString()} accent="var(--sky)" />
        <LibraryStat label="Avg Phi" value={stats.avgPhi.toFixed(3)} accent="var(--indigoL)" />
        <LibraryStat label="Top Phi" value={stats.topPhi.toFixed(3)} accent="var(--violet)" />
      </div>

      <div className="mb-4 flex flex-col gap-3 xl:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--t4)]" />
          <input
            type="text"
            placeholder="Search by label, key, quote, type, or target..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="h-10 w-full rounded-lg border border-[var(--bdr)] bg-[var(--deep)] pl-9 pr-3 text-sm text-[var(--t1)] outline-none transition placeholder:text-[var(--t4)] focus:border-[var(--indigoL)]"
          />
        </div>

        <FilterGroup icon={<Filter className="h-4 w-4" />}>
          {(["all", "csv", "narrative", "sdmx"] as SourceFilter[]).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setSource(item)}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold capitalize transition ${
                source === item
                  ? "bg-[rgba(59,91,219,.2)] text-[var(--indigoL)]"
                  : "text-[var(--t3)] hover:text-[var(--t1)]"
              }`}
            >
              {item}
            </button>
          ))}
        </FilterGroup>

        <div className="flex items-center gap-2 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3">
          <span className="font-mono-data whitespace-nowrap text-[11px] uppercase tracking-[1px] text-[var(--t3)]">
            Min Phi
          </span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={minPhi}
            onChange={(event) => setMinPhi(Number(event.target.value))}
            className="nidm-range w-28"
            style={{ "--pct": `${minPhi * 100}%` } as React.CSSProperties}
          />
          <span className="font-mono-data w-10 text-right text-xs text-[var(--t1)]">
            {minPhi.toFixed(2)}
          </span>
        </div>

        <FilterGroup>
          {(["phi", "label", "uploadedAt"] as SortKey[]).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setSortKey(item)}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                sortKey === item
                  ? "bg-[rgba(151,117,250,.18)] text-[var(--violet)]"
                  : "text-[var(--t3)] hover:text-[var(--t1)]"
              }`}
            >
              {item === "uploadedAt" ? "Date" : item === "phi" ? "Phi" : "Name"}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setSortDir(sortDir === "asc" ? "desc" : "asc")}
            className="rounded-md p-1.5 text-[var(--t3)] transition hover:text-[var(--t1)]"
            title={sortDir === "asc" ? "Ascending" : "Descending"}
          >
            {sortDir === "asc" ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
          </button>
        </FilterGroup>
      </div>

      {narratives.length > 0 && (
        <div
          className={`mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3 transition ${
            selectedNarratives.length > 0
              ? "border-[rgba(59,91,219,.35)] bg-[rgba(59,91,219,.1)]"
              : "border-[var(--bdr)] bg-[var(--deep)]"
          }`}
        >
          <div className="flex flex-wrap items-center gap-3">
            <GitCompareArrows className="h-4 w-4 text-[var(--indigoL)]" />
            <span className="text-xs text-[var(--t3)]">
              {selectedNarratives.length === 0
                ? "Select two narratives for side-by-side scoring comparison."
                : selectedNarratives.length === 1
                ? "Select one more narrative to compare."
                : "Two narratives selected."}
            </span>
            {selectedNarratives.map((narrative, index) => (
              <button
                key={narrative.id}
                type="button"
                onClick={() => toggleSelect(narrative.id)}
                className="inline-flex max-w-[180px] items-center gap-2 rounded-md border border-[var(--bdrV)] bg-[var(--card)] px-2 py-1 text-xs text-[var(--t2)]"
              >
                <span className="font-mono-data text-[var(--indigoL)]">{index === 0 ? "A" : "B"}</span>
                <span className="truncate">{narrative.label}</span>
                <X className="h-3 w-3" />
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setCompareOpen(true)}
            disabled={!canCompare}
            className="inline-flex h-9 items-center gap-2 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 text-xs font-semibold text-[var(--t2)] transition hover:border-[var(--indigoL)] hover:text-[var(--t1)] disabled:cursor-not-allowed disabled:opacity-45"
          >
            <GitCompareArrows className="h-3.5 w-3.5" />
            Compare ({selectedNarratives.length}/2)
          </button>
        </div>
      )}

      {narratives.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[var(--bdrV)] bg-[var(--deep)] py-12 text-center">
          <Library className="mx-auto mb-3 h-10 w-10 text-[var(--t4)]" />
          <p className="text-sm text-[var(--t3)]">
            No narratives loaded yet. Upload CSV, text, or SDMX exchange data to populate the library.
          </p>
        </div>
      ) : visible.length === 0 ? (
        <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] py-8 text-center text-sm text-[var(--t3)]">
          No narratives match the current filters.
        </div>
      ) : (
        <div className="max-h-[540px] space-y-2 overflow-y-auto pr-1">
          {visible.map((narrative) => (
            <NarrativeRow
              key={narrative.id}
              narrative={narrative}
              selected={selectedIds.includes(narrative.id)}
              slot={selectedIds.indexOf(narrative.id)}
              onToggle={() => toggleSelect(narrative.id)}
              onRemove={onRemove ? () => onRemove(narrative.id) : undefined}
            />
          ))}
        </div>
      )}

      <NarrativeCompare
        a={selectedNarratives[0] ?? null}
        b={selectedNarratives[1] ?? null}
        open={compareOpen && canCompare}
        onOpenChange={setCompareOpen}
      />
    </section>
  );
}

function NarrativeRow({
  narrative,
  selected,
  slot,
  onToggle,
  onRemove,
}: {
  narrative: ParsedNarrative;
  selected: boolean;
  slot: number;
  onToggle: () => void;
  onRemove?: () => void;
}) {
  const icon =
    narrative.source === "csv" ? (
      <FileSpreadsheet className="h-4 w-4 text-[var(--gold)]" />
    ) : narrative.source === "sdmx" ? (
      <FileJson className="h-4 w-4 text-[var(--sky)]" />
    ) : (
      <FileText className="h-4 w-4 text-[var(--verdant)]" />
    );

  return (
    <div
      className={`group flex items-start gap-3 rounded-lg border p-4 transition ${
        selected
          ? "border-[var(--indigoL)] bg-[rgba(59,91,219,.12)]"
          : "border-[var(--bdr)] bg-[var(--deep)] hover:border-[var(--bdrV)]"
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded border border-[var(--bdrV)] bg-[var(--card)] text-[var(--indigoL)]"
        aria-label={`Select ${narrative.label} for comparison`}
      >
        {selected ? <Check className="h-3.5 w-3.5" /> : <span className="font-mono-data text-[10px]">{slot >= 0 ? slot + 1 : ""}</span>}
      </button>

      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-center gap-2">
          {icon}
          <h4 className="truncate text-sm font-semibold text-[var(--t1)]">{narrative.label}</h4>
          <span className="font-mono-data shrink-0 rounded border border-[var(--bdr)] bg-[var(--card)] px-1.5 py-0.5 text-[10px] uppercase tracking-[.8px] text-[var(--t3)]">
            {narrative.type}
          </span>
        </div>
        {narrative.quote && (
          <p className="mb-2 line-clamp-2 text-xs leading-5 text-[var(--t3)]">"{narrative.quote}"</p>
        )}
        <div className="font-mono-data flex flex-wrap gap-3 text-[11px] text-[var(--t3)]">
          <span>E <strong className="text-[var(--t1)]">{narrative.E.toFixed(2)}</strong></span>
          <span>C <strong className="text-[var(--t1)]">{narrative.C.toFixed(2)}</strong></span>
          <span>tau <strong className="text-[var(--t1)]">{narrative.tau.toFixed(2)}</strong></span>
          <span>kappa <strong className="text-[var(--t1)]">{narrative.kappa.toFixed(2)}</strong></span>
          <span>target <strong className="text-[var(--t1)]">{narrative.targets}</strong></span>
        </div>
      </div>

      <div className="flex shrink-0 flex-col items-end gap-2">
        <div
          className="font-mono-data rounded-md border px-3 py-1 text-sm font-bold"
          style={{
            color: narrative.phi >= 0.7 ? "var(--verdant)" : narrative.phi >= 0.5 ? "var(--indigoL)" : "var(--t3)",
            borderColor: narrative.phi >= 0.7 ? "rgba(32,201,151,.35)" : "var(--bdr)",
            background: narrative.phi >= 0.7 ? "rgba(32,201,151,.08)" : "var(--card)",
          }}
          title="Composite narrative strength Phi"
        >
          Phi {narrative.phi.toFixed(3)}
        </div>
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="opacity-0 rounded-md p-1 text-[var(--t3)] transition hover:bg-white/10 hover:text-[var(--flame)] group-hover:opacity-100"
            title="Remove narrative"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}

function LibraryStat({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3">
      <p className="font-mono-data text-[10px] uppercase tracking-[1px] text-[var(--t4)]">{label}</p>
      <p className="font-syne mt-1 text-2xl font-bold" style={{ color: accent }}>{value}</p>
    </div>
  );
}

function FilterGroup({ icon, children }: { icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-1 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-1">
      {icon && <span className="px-1 text-[var(--t4)]">{icon}</span>}
      {children}
    </div>
  );
}
