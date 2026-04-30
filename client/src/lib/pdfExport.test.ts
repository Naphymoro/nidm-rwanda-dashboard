import { describe, expect, it } from "vitest";
import { buildComparisonFilename } from "./pdfExport";

describe("buildComparisonFilename", () => {
  const fixedDate = new Date(2026, 3, 30); // April 30 2026 (month is 0-indexed)

  it("produces a kebab-case filename ending in .pdf", () => {
    const name = buildComparisonFilename("Health Story", "Cost Fact", fixedDate);
    expect(name).toBe(
      "nidm-comparison-health-story-vs-cost-fact-2026-04-30.pdf"
    );
  });

  it("zero-pads month and day", () => {
    const jan5 = new Date(2026, 0, 5);
    const name = buildComparisonFilename("a", "b", jan5);
    expect(name).toContain("2026-01-05");
  });

  it("strips punctuation and special characters", () => {
    const name = buildComparisonFilename(
      "Hello, World! (v2)",
      "Other/Story",
      fixedDate
    );
    expect(name).toMatch(/^nidm-comparison-hello-world-v2-vs-other-story-/);
  });

  it("collapses runs of separators into a single dash", () => {
    const name = buildComparisonFilename("a   b___c", "d", fixedDate);
    expect(name).toContain("a-b-c");
    expect(name).not.toContain("--");
  });

  it("trims leading and trailing separators per slug", () => {
    const name = buildComparisonFilename("--alpha--", "__beta__", fixedDate);
    expect(name).toBe("nidm-comparison-alpha-vs-beta-2026-04-30.pdf");
  });

  it("falls back to 'narrative' when a label has no usable characters", () => {
    const name = buildComparisonFilename("???", "***", fixedDate);
    expect(name).toBe("nidm-comparison-narrative-vs-narrative-2026-04-30.pdf");
  });

  it("falls back to 'narrative' for empty strings", () => {
    const name = buildComparisonFilename("", "", fixedDate);
    expect(name).toBe("nidm-comparison-narrative-vs-narrative-2026-04-30.pdf");
  });

  it("truncates each label slug to 32 characters", () => {
    const long = "a".repeat(80);
    const name = buildComparisonFilename(long, long, fixedDate);
    const aSlug = "a".repeat(32);
    expect(name).toBe(`nidm-comparison-${aSlug}-vs-${aSlug}-2026-04-30.pdf`);
  });

  it("uses the current date when no date is provided", () => {
    const name = buildComparisonFilename("x", "y");
    expect(name).toMatch(/-\d{4}-\d{2}-\d{2}\.pdf$/);
  });

  it("lower-cases input regardless of original case", () => {
    const name = buildComparisonFilename("UPPER", "MiXeD", fixedDate);
    expect(name).toBe("nidm-comparison-upper-vs-mixed-2026-04-30.pdf");
  });
});
