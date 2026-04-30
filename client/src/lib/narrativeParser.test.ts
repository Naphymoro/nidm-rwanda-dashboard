import { describe, expect, it } from "vitest";
import {
  PHI_WEIGHTS,
  computePhi,
  parseCsvLine,
  parseCsv,
  parseNarrativeText,
  filterNarratives,
  sortNarratives,
  ParsedNarrative,
} from "./narrativeParser";

describe("computePhi", () => {
  it("uses the documented 0.3 / 0.3 / 0.2 / 0.2 weights", () => {
    expect(PHI_WEIGHTS).toEqual({ E: 0.3, C: 0.3, tau: 0.2, kappa: 0.2 });
  });

  it("returns 1 when all dimensions are 1", () => {
    expect(computePhi(1, 1, 1, 1)).toBe(1);
  });

  it("returns 0 when all dimensions are 0", () => {
    expect(computePhi(0, 0, 0, 0)).toBe(0);
  });

  it("computes weighted sum correctly", () => {
    // 0.3*0.8 + 0.3*0.6 + 0.2*0.4 + 0.2*0.2 = 0.24 + 0.18 + 0.08 + 0.04 = 0.54
    expect(computePhi(0.8, 0.6, 0.4, 0.2)).toBeCloseTo(0.54, 4);
  });

  it("rounds to 4 decimal places", () => {
    const result = computePhi(0.333333, 0.333333, 0.333333, 0.333333);
    // ensure no floating noise beyond 4 decimals
    expect(result.toString().split(".")[1]?.length ?? 0).toBeLessThanOrEqual(4);
  });
});

describe("parseCsvLine", () => {
  it("splits a simple comma-separated line", () => {
    expect(parseCsvLine("a,b,c")).toEqual(["a", "b", "c"]);
  });

  it("preserves commas inside quoted fields", () => {
    expect(parseCsvLine('"hello, world",b,"c,d"')).toEqual([
      "hello, world",
      "b",
      "c,d",
    ]);
  });

  it("handles escaped double quotes inside quoted fields", () => {
    expect(parseCsvLine('"she said ""hi""",ok')).toEqual([
      'she said "hi"',
      "ok",
    ]);
  });

  it("trims whitespace around fields", () => {
    expect(parseCsvLine("  a , b ,c")).toEqual(["a", "b", "c"]);
  });
});

describe("parseCsv", () => {
  const csv = `key,label,type,quote,E,C,tau,kappa,targets
n_001,Health,story,"Clean cooking saves lives",0.8,0.7,0.9,0.8,all
n_002,Cost,fact,"Saves money",0.5,0.6,0.7,0.4,women`;

  it("parses each non-header row into a ParsedNarrative", () => {
    const result = parseCsv(csv, "test.csv");
    expect(result).toHaveLength(2);
  });

  it("populates all dimension fields and computes Φ", () => {
    const [first] = parseCsv(csv, "test.csv");
    expect(first.key).toBe("n_001");
    expect(first.label).toBe("Health");
    expect(first.type).toBe("story");
    expect(first.quote).toBe("Clean cooking saves lives");
    expect(first.E).toBe(0.8);
    expect(first.C).toBe(0.7);
    expect(first.tau).toBe(0.9);
    expect(first.kappa).toBe(0.8);
    expect(first.targets).toBe("all");
    expect(first.source).toBe("csv");
    expect(first.phi).toBeCloseTo(computePhi(0.8, 0.7, 0.9, 0.8), 4);
  });

  it("clamps out-of-range numeric values into [0, 1]", () => {
    const oddCsv = `key,label,type,quote,E,C,tau,kappa,targets
x,X,t,q,1.5,-0.3,2,0.5,a`;
    const [row] = parseCsv(oddCsv, "x.csv");
    expect(row.E).toBe(1);
    expect(row.C).toBe(0);
    expect(row.tau).toBe(1);
    expect(row.kappa).toBe(0.5);
  });

  it("returns an empty array for empty input", () => {
    expect(parseCsv("", "empty.csv")).toEqual([]);
  });

  it("matches column headers case-insensitively", () => {
    const upper = `KEY,LABEL,TYPE,QUOTE,E,C,TAU,KAPPA,TARGETS
n,N,t,q,0.5,0.5,0.5,0.5,a`;
    const [row] = parseCsv(upper, "u.csv");
    expect(row.key).toBe("n");
    expect(row.E).toBe(0.5);
  });
});

describe("parseNarrativeText", () => {
  it("treats each blank-line-separated paragraph as one narrative", () => {
    const text = `Para one with content.\n\nPara two has more text.\n\nPara three is here.`;
    const result = parseNarrativeText(text, "story.txt");
    expect(result).toHaveLength(3);
  });

  it("falls back to line-by-line splitting when there are no blank lines", () => {
    const text = `Line one\nLine two\nLine three`;
    const result = parseNarrativeText(text, "lines.txt");
    expect(result).toHaveLength(3);
  });

  it("returns an empty array for empty input", () => {
    expect(parseNarrativeText("", "e.txt")).toEqual([]);
    expect(parseNarrativeText("   \n\n   ", "e.txt")).toEqual([]);
  });

  it("computes Φ scores within [0, 1]", () => {
    const text = "A short narrative paragraph for testing purposes.";
    const [n] = parseNarrativeText(text, "t.txt");
    expect(n.phi).toBeGreaterThanOrEqual(0);
    expect(n.phi).toBeLessThanOrEqual(1);
    expect(n.E).toBeGreaterThanOrEqual(0);
    expect(n.E).toBeLessThanOrEqual(1);
  });

  it("marks source as 'narrative'", () => {
    const [n] = parseNarrativeText("Hello world.", "t.txt");
    expect(n.source).toBe("narrative");
  });

  it("truncates very long quotes to 280 chars", () => {
    const long = "x".repeat(500);
    const [n] = parseNarrativeText(long, "t.txt");
    expect(n.quote.length).toBeLessThanOrEqual(280);
    expect(n.quote.endsWith("...")).toBe(true);
  });
});

describe("filterNarratives", () => {
  const items: ParsedNarrative[] = [
    {
      id: "1", key: "k1", label: "Health Benefits", type: "story",
      quote: "Clean cooking is healthy", E: 0.8, C: 0.7, tau: 0.9, kappa: 0.8,
      phi: 0.81, targets: "women", source: "csv", uploadedAt: 1,
    },
    {
      id: "2", key: "k2", label: "Cost Savings", type: "fact",
      quote: "Saves money each month", E: 0.5, C: 0.5, tau: 0.7, kappa: 0.4,
      phi: 0.52, targets: "all", source: "csv", uploadedAt: 2,
    },
    {
      id: "3", key: "k3", label: "Personal Story", type: "narrative",
      quote: "My family's experience", E: 0.6, C: 0.8, tau: 0.5, kappa: 0.7,
      phi: 0.66, targets: "youth", source: "narrative", uploadedAt: 3,
    },
  ];

  it("returns all items when query is empty and source is 'all'", () => {
    expect(filterNarratives(items, "", "all", 0)).toHaveLength(3);
  });

  it("filters by case-insensitive query against label/quote/type/targets", () => {
    expect(filterNarratives(items, "health", "all", 0)).toHaveLength(1);
    expect(filterNarratives(items, "saves", "all", 0)).toHaveLength(1);
    expect(filterNarratives(items, "youth", "all", 0)).toHaveLength(1);
  });

  it("filters by source", () => {
    expect(filterNarratives(items, "", "csv", 0)).toHaveLength(2);
    expect(filterNarratives(items, "", "narrative", 0)).toHaveLength(1);
  });

  it("excludes items below minPhi", () => {
    expect(filterNarratives(items, "", "all", 0.6)).toHaveLength(2);
    expect(filterNarratives(items, "", "all", 0.8)).toHaveLength(1);
    expect(filterNarratives(items, "", "all", 1.0)).toHaveLength(0);
  });

  it("combines query + source + minPhi filters", () => {
    expect(filterNarratives(items, "story", "csv", 0.7)).toHaveLength(1);
    expect(filterNarratives(items, "story", "narrative", 0.5)).toHaveLength(1);
  });
});

describe("sortNarratives", () => {
  const items: ParsedNarrative[] = [
    {
      id: "1", key: "k1", label: "Charlie", type: "x",
      quote: "", E: 0, C: 0, tau: 0, kappa: 0, phi: 0.5,
      targets: "", source: "csv", uploadedAt: 100,
    },
    {
      id: "2", key: "k2", label: "Alpha", type: "x",
      quote: "", E: 0, C: 0, tau: 0, kappa: 0, phi: 0.9,
      targets: "", source: "csv", uploadedAt: 50,
    },
    {
      id: "3", key: "k3", label: "Bravo", type: "x",
      quote: "", E: 0, C: 0, tau: 0, kappa: 0, phi: 0.3,
      targets: "", source: "csv", uploadedAt: 200,
    },
  ];

  it("sorts by phi descending", () => {
    const sorted = sortNarratives(items, "phi", "desc");
    expect(sorted.map((s) => s.phi)).toEqual([0.9, 0.5, 0.3]);
  });

  it("sorts by phi ascending", () => {
    const sorted = sortNarratives(items, "phi", "asc");
    expect(sorted.map((s) => s.phi)).toEqual([0.3, 0.5, 0.9]);
  });

  it("sorts by label alphabetically", () => {
    const sorted = sortNarratives(items, "label", "asc");
    expect(sorted.map((s) => s.label)).toEqual(["Alpha", "Bravo", "Charlie"]);
  });

  it("sorts by uploadedAt descending", () => {
    const sorted = sortNarratives(items, "uploadedAt", "desc");
    expect(sorted.map((s) => s.uploadedAt)).toEqual([200, 100, 50]);
  });

  it("does not mutate the input array", () => {
    const before = items.map((i) => i.id);
    sortNarratives(items, "phi", "desc");
    expect(items.map((i) => i.id)).toEqual(before);
  });
});
