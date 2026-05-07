/**
 * Narrative file parser
 * Supports:
 *   - CSV with columns: key, label, type, quote, E, C, tau, kappa, targets
 *   - TXT/MD: each non-empty paragraph (or line) becomes a narrative entry
 */

export interface ParsedNarrative {
  id: string;
  key: string;
  label: string;
  type: string;
  quote: string;
  E: number;
  C: number;
  tau: number;
  kappa: number;
  phi: number;
  targets: string;
  source: "csv" | "narrative" | "sdmx";
  uploadedAt: number;
}

export const PHI_WEIGHTS = { E: 0.3, C: 0.3, tau: 0.2, kappa: 0.2 } as const;

export function computePhi(E: number, C: number, tau: number, kappa: number): number {
  const value =
    PHI_WEIGHTS.E * E +
    PHI_WEIGHTS.C * C +
    PHI_WEIGHTS.tau * tau +
    PHI_WEIGHTS.kappa * kappa;
  return Math.round(value * 10000) / 10000;
}

/**
 * Minimal but robust CSV parser that handles quoted fields and embedded commas.
 */
export function parseCsvLine(line: string): string[] {
  const fields: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "," && !inQuotes) {
      fields.push(current.trim());
      current = "";
    } else {
      current += ch;
    }
  }
  fields.push(current.trim());
  return fields;
}

function clamp01(n: number): number {
  if (Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

function safeNumber(value: string | undefined): number {
  if (!value) return 0;
  const n = parseFloat(value);
  return Number.isFinite(n) ? n : 0;
}

/**
 * Parse a CSV file's text content into structured narratives.
 * The first row is assumed to be a header. Column names are matched
 * case-insensitively.
 */
export function parseCsv(content: string, filename: string): ParsedNarrative[] {
  const lines = content
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.length > 0);

  if (lines.length === 0) return [];

  const header = parseCsvLine(lines[0]).map((h) => h.toLowerCase());
  const idx = (name: string) => header.indexOf(name.toLowerCase());

  const iKey = idx("key");
  const iLabel = idx("label");
  const iType = idx("type");
  const iQuote = idx("quote");
  const iE = idx("e");
  const iC = idx("c");
  const iTau = idx("tau");
  const iKappa = idx("kappa");
  const iTargets = idx("targets");

  const out: ParsedNarrative[] = [];
  for (let r = 1; r < lines.length; r++) {
    const cols = parseCsvLine(lines[r]);
    const E = clamp01(safeNumber(cols[iE]));
    const C = clamp01(safeNumber(cols[iC]));
    const tau = clamp01(safeNumber(cols[iTau]));
    const kappa = clamp01(safeNumber(cols[iKappa]));

    const key = (iKey >= 0 ? cols[iKey] : "") || `${filename}-${r}`;
    const label = (iLabel >= 0 ? cols[iLabel] : "") || key;

    out.push({
      id: `${filename}-${r}-${Date.now()}`,
      key,
      label,
      type: (iType >= 0 ? cols[iType] : "") || "story",
      quote: iQuote >= 0 ? cols[iQuote] : "",
      E,
      C,
      tau,
      kappa,
      phi: computePhi(E, C, tau, kappa),
      targets: (iTargets >= 0 ? cols[iTargets] : "") || "all",
      source: "csv",
      uploadedAt: Date.now(),
    });
  }
  return out;
}

/**
 * Parse a TXT or MD file into narrative entries.
 * Each non-empty paragraph (separated by a blank line) becomes one narrative.
 * If no blank lines are found, each non-empty line becomes a narrative.
 *
 * Heuristic scoring is applied based on text characteristics so that uploaded
 * narratives surface useful preliminary E, C, τ, κ scores.
 */
export function parseNarrativeText(
  content: string,
  filename: string
): ParsedNarrative[] {
  const trimmed = content.trim();
  if (!trimmed) return [];

  let chunks = trimmed.split(/\n\s*\n/).map((c) => c.trim()).filter(Boolean);
  if (chunks.length <= 1) {
    chunks = trimmed.split(/\r?\n/).map((c) => c.trim()).filter(Boolean);
  }

  return chunks.map((chunk, i) => {
    const wordCount = chunk.split(/\s+/).length;
    const exclamations = (chunk.match(/!/g) || []).length;
    const questions = (chunk.match(/\?/g) || []).length;
    const hasNumbers = /\d/.test(chunk);
    const hasQuotes = /["“”]/.test(chunk);

    // Heuristic dimension scores in [0, 1]
    const E = clamp01(0.4 + Math.min(0.4, exclamations * 0.1) + (questions > 0 ? 0.1 : 0));
    const C = clamp01(0.5 + (hasQuotes ? 0.2 : 0) + Math.min(0.2, wordCount / 200));
    const tau = clamp01(0.45 + (hasNumbers ? 0.25 : 0) + (wordCount > 50 ? 0.1 : 0));
    const kappa = clamp01(0.35 + Math.min(0.5, wordCount / 100));

    const firstSentence = chunk.split(/[.!?]/)[0].trim();
    const label =
      firstSentence.length > 0 && firstSentence.length <= 80
        ? firstSentence
        : `${filename} #${i + 1}`;

    return {
      id: `${filename}-${i}-${Date.now()}`,
      key: `${filename}-${i + 1}`,
      label,
      type: "narrative",
      quote: chunk.length > 280 ? chunk.slice(0, 277) + "..." : chunk,
      E,
      C,
      tau,
      kappa,
      phi: computePhi(E, C, tau, kappa),
      targets: "all",
      source: "narrative",
      uploadedAt: Date.now(),
    };
  });
}

type AnyRecord = Record<string, unknown>;

function readString(record: AnyRecord, keys: string[], fallback = ""): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) return value.trim();
    if (typeof value === "number") return String(value);
  }
  return fallback;
}

function readNestedRecord(record: AnyRecord, key: string): AnyRecord {
  const value = record[key];
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as AnyRecord)
    : {};
}

function recordToNarrative(record: AnyRecord, index: number, filename: string): ParsedNarrative {
  const dimensions = readNestedRecord(record, "dimensions");
  const measures = readNestedRecord(record, "measures");
  const attributes = readNestedRecord(record, "attributes");

  const key =
    readString(record, ["key", "id"]) ||
    readString(dimensions, ["narrative", "key", "id"]) ||
    `${filename}-${index + 1}`;
  const label =
    readString(record, ["label", "name"]) ||
    readString(attributes, ["label", "name"]) ||
    key;
  const quote =
    readString(record, ["quote", "body", "text", "value"]) ||
    readString(attributes, ["quote", "body", "text"]) ||
    "";
  const type =
    readString(record, ["type", "storyType"]) ||
    readString(dimensions, ["type"], "narrative");
  const targets =
    readString(record, ["targets", "target"]) ||
    readString(dimensions, ["target", "targets"], "all");

  const E = clamp01(safeNumber(String(measures.E ?? record.E ?? record.e ?? 0.5)));
  const C = clamp01(safeNumber(String(measures.C ?? record.C ?? record.c ?? 0.5)));
  const tau = clamp01(safeNumber(String(measures.tau ?? record.tau ?? record.TAU ?? 0.5)));
  const kappa = clamp01(safeNumber(String(measures.kappa ?? record.kappa ?? 0.5)));
  const phiValue = measures.phi ?? record.phi;
  const phi = phiValue === undefined
    ? computePhi(E, C, tau, kappa)
    : clamp01(safeNumber(String(phiValue)));

  return {
    id: `${filename}-${index}-${Date.now()}`,
    key,
    label,
    type,
    quote: quote.length > 420 ? quote.slice(0, 417) + "..." : quote,
    E,
    C,
    tau,
    kappa,
    phi,
    targets,
    source: "sdmx",
    uploadedAt: Date.now(),
  };
}

function extractJsonRecords(payload: unknown): AnyRecord[] {
  if (Array.isArray(payload)) return payload.filter((item): item is AnyRecord => !!item && typeof item === "object");
  if (!payload || typeof payload !== "object") return [];

  const root = payload as AnyRecord;
  const direct =
    root.narratives ??
    root.observations ??
    readNestedRecord(root, "data").narratives ??
    readNestedRecord(root, "data").observations;

  if (Array.isArray(direct)) {
    return direct.filter((item): item is AnyRecord => !!item && typeof item === "object");
  }

  const dataSets = root.dataSets;
  if (Array.isArray(dataSets) && dataSets.length > 0) {
    const observations = (dataSets[0] as AnyRecord).observations;
    if (Array.isArray(observations)) {
      return observations.filter((item): item is AnyRecord => !!item && typeof item === "object");
    }

    if (observations && typeof observations === "object") {
      return Object.entries(observations as Record<string, unknown>).map(([key, value]) => {
        if (Array.isArray(value)) {
          return {
            key,
            E: value[0],
            C: value[1],
            tau: value[2],
            kappa: value[3],
            phi: value[4],
          };
        }
        if (value && typeof value === "object") {
          return { key, ...(value as AnyRecord) };
        }
        return { key };
      });
    }
  }

  return [];
}

function parseAttributes(input: string): AnyRecord {
  const attrs: AnyRecord = {};
  const attrPattern = /([\w:-]+)\s*=\s*"([^"]*)"/g;
  let match: RegExpExecArray | null;
  while ((match = attrPattern.exec(input)) !== null) {
    attrs[match[1]] = match[2];
  }
  return attrs;
}

function extractXmlNarratives(content: string): AnyRecord[] {
  const records: AnyRecord[] = [];
  const nodePattern = /<(Narrative|narrative|Observation|observation|Obs)\b([^>]*)>([\s\S]*?)<\/\1>/g;
  let match: RegExpExecArray | null;

  while ((match = nodePattern.exec(content)) !== null) {
    const attrs = parseAttributes(match[2]);
    const body = match[3].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    records.push({ ...attrs, quote: attrs.quote ?? attrs.text ?? body });
  }

  return records;
}

/**
 * Parse a lightweight SDMX-style JSON/XML exchange into NIDM narratives.
 * The dashboard emits and accepts the same narrative observation shape:
 * dimensions identify narrative/type/target/source and measures carry
 * E, C, tau, kappa, and phi values.
 */
export function parseSdmxNarratives(content: string, filename: string): ParsedNarrative[] {
  const trimmed = content.trim();
  if (!trimmed) return [];

  let records: AnyRecord[] = [];
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      records = extractJsonRecords(JSON.parse(trimmed));
    } catch {
      records = [];
    }
  } else if (trimmed.startsWith("<")) {
    records = extractXmlNarratives(trimmed);
  }

  return records.map((record, index) => recordToNarrative(record, index, filename));
}

/**
 * Filter and sort utilities for the narrative library.
 */
export type SortKey = "phi" | "label" | "uploadedAt";

export function filterNarratives(
  list: ParsedNarrative[],
  query: string,
  source: "all" | ParsedNarrative["source"],
  minPhi: number
): ParsedNarrative[] {
  const q = query.trim().toLowerCase();
  return list.filter((n) => {
    if (source !== "all" && n.source !== source) return false;
    if (n.phi < minPhi) return false;
    if (q.length === 0) return true;
    return (
      n.label.toLowerCase().includes(q) ||
      n.key.toLowerCase().includes(q) ||
      n.quote.toLowerCase().includes(q) ||
      n.type.toLowerCase().includes(q) ||
      n.targets.toLowerCase().includes(q)
    );
  });
}

export function sortNarratives(
  list: ParsedNarrative[],
  key: SortKey,
  direction: "asc" | "desc"
): ParsedNarrative[] {
  const copy = [...list];
  copy.sort((a, b) => {
    let cmp = 0;
    if (key === "phi") cmp = a.phi - b.phi;
    else if (key === "label") cmp = a.label.localeCompare(b.label);
    else if (key === "uploadedAt") cmp = a.uploadedAt - b.uploadedAt;
    return direction === "asc" ? cmp : -cmp;
  });
  return copy;
}

// ────────────────────────────────────────────────────────────────────────────
// Comparison helpers
// ────────────────────────────────────────────────────────────────────────────

export type DimensionKey = "E" | "C" | "tau" | "kappa";

export const DIMENSION_LABELS: Record<DimensionKey, string> = {
  E: "Emotional Salience (E)",
  C: "Cultural Resonance (C)",
  tau: "Trust Alignment (τ)",
  kappa: "Narrative Arc Strength (κ)",
};

export interface DimensionDiff {
  dimension: DimensionKey;
  label: string;
  a: number;
  b: number;
  delta: number; // b - a
  winner: "a" | "b" | "tie";
}

export interface NarrativeComparison {
  a: ParsedNarrative;
  b: ParsedNarrative;
  phiDelta: number;            // b.phi - a.phi
  phiWinner: "a" | "b" | "tie";
  dimensionDiffs: DimensionDiff[];
  aWins: number;               // dimensions where a > b
  bWins: number;               // dimensions where b > a
  ties: number;
  largestGap: DimensionDiff;   // dimension with greatest |delta|
}

const TIE_THRESHOLD = 1e-6;

function pickWinner(a: number, b: number): "a" | "b" | "tie" {
  if (Math.abs(a - b) < TIE_THRESHOLD) return "tie";
  return a > b ? "a" : "b";
}

/**
 * Build a structured side-by-side comparison between two narratives.
 * Computes per-dimension deltas, the overall Φ winner, and the dimension
 * with the largest absolute gap so the UI can highlight it.
 */
export function compareNarratives(
  a: ParsedNarrative,
  b: ParsedNarrative
): NarrativeComparison {
  const dims: DimensionKey[] = ["E", "C", "tau", "kappa"];

  const dimensionDiffs: DimensionDiff[] = dims.map((dim) => {
    const av = a[dim];
    const bv = b[dim];
    return {
      dimension: dim,
      label: DIMENSION_LABELS[dim],
      a: av,
      b: bv,
      delta: Math.round((bv - av) * 10000) / 10000,
      winner: pickWinner(av, bv),
    };
  });

  const aWins = dimensionDiffs.filter((d) => d.winner === "a").length;
  const bWins = dimensionDiffs.filter((d) => d.winner === "b").length;
  const ties = dimensionDiffs.filter((d) => d.winner === "tie").length;

  const largestGap = dimensionDiffs.reduce((best, cur) =>
    Math.abs(cur.delta) > Math.abs(best.delta) ? cur : best
  );

  return {
    a,
    b,
    phiDelta: Math.round((b.phi - a.phi) * 10000) / 10000,
    phiWinner: pickWinner(a.phi, b.phi),
    dimensionDiffs,
    aWins,
    bWins,
    ties,
    largestGap,
  };
}
