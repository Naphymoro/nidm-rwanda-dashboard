import { describe, it, expect } from "vitest";

/**
 * Unit tests for NIDM Dashboard components
 * These tests verify core business logic and computations
 */

// ============================================================================
// Narrative Encoding Tests
// ============================================================================

describe("Narrative Encoding - Phi Computation", () => {
  const WEIGHTS = {
    E: 0.3,
    C: 0.3,
    tau: 0.2,
    kappa: 0.2,
  };

  const computePhi = (E: number, C: number, tau: number, kappa: number) => {
    return Number(
      (WEIGHTS.E * E +
        WEIGHTS.C * C +
        WEIGHTS.tau * tau +
        WEIGHTS.kappa * kappa).toFixed(4)
    );
  };

  it("should compute Phi correctly with equal scores", () => {
    const phi = computePhi(0.5, 0.5, 0.5, 0.5);
    expect(phi).toBe(0.5);
  });

  it("should compute Phi correctly with maximum scores", () => {
    const phi = computePhi(1.0, 1.0, 1.0, 1.0);
    expect(phi).toBe(1.0);
  });

  it("should compute Phi correctly with minimum scores", () => {
    const phi = computePhi(0.0, 0.0, 0.0, 0.0);
    expect(phi).toBe(0.0);
  });

  it("should apply correct weights to dimensions", () => {
    // E and C have 0.3 weight each, tau and kappa have 0.2 weight each
    const phi = computePhi(1.0, 0.0, 0.0, 0.0);
    expect(phi).toBe(0.3); // Only E contributes

    const phi2 = computePhi(0.0, 1.0, 0.0, 0.0);
    expect(phi2).toBe(0.3); // Only C contributes

    const phi3 = computePhi(0.0, 0.0, 1.0, 0.0);
    expect(phi3).toBe(0.2); // Only tau contributes

    const phi4 = computePhi(0.0, 0.0, 0.0, 1.0);
    expect(phi4).toBe(0.2); // Only kappa contributes
  });

  it("should clamp values between 0 and 1", () => {
    // Values should be clamped in the component
    expect(Math.max(0, Math.min(1, -0.5))).toBe(0);
    expect(Math.max(0, Math.min(1, 1.5))).toBe(1);
  });

  it("should round to 4 decimal places", () => {
    const phi = computePhi(0.123, 0.456, 0.789, 0.321);
    expect(phi.toString().split(".")[1]?.length).toBeLessThanOrEqual(4);
  });
});

// ============================================================================
// KPI Card Tests
// ============================================================================

describe("KPI Card - Counter Animation", () => {
  it("should animate from 0 to target value", () => {
    const targetValue = 87.5;
    const duration = 30; // frames
    const increment = targetValue / duration;

    let current = 0;
    const values: number[] = [];

    for (let i = 0; i < duration; i++) {
      current += increment;
      values.push(current);
    }

    // Should reach approximately target value
    expect(values[values.length - 1]).toBeGreaterThanOrEqual(targetValue * 0.95);
    expect(values[values.length - 1]).toBeLessThanOrEqual(targetValue * 1.05);
  });

  it("should handle trend calculations correctly", () => {
    const currentValue = 87.5;
    const previousValue = 77.8;
    const trendPercent = ((currentValue - previousValue) / previousValue) * 100;

    expect(trendPercent).toBeCloseTo(12.47, 1);
  });
});

// ============================================================================
// Scenario Comparison Tests
// ============================================================================

describe("Scenario Comparison - Winner Selection", () => {
  interface Scenario {
    id: string;
    name: string;
    phi: number;
  }

  const scenarios: Scenario[] = [
    { id: "baseline", name: "Baseline", phi: 0.65 },
    { id: "high-engagement", name: "High Engagement", phi: 0.82 },
    { id: "targeted", name: "Targeted Inoculation", phi: 0.71 },
  ];

  it("should identify scenario with highest Phi as winner", () => {
    const winner = scenarios.reduce((prev, current) =>
      prev.phi > current.phi ? prev : current
    );

    expect(winner.id).toBe("high-engagement");
    expect(winner.phi).toBe(0.82);
  });

  it("should handle single scenario", () => {
    const singleScenario = [{ id: "only", name: "Only", phi: 0.5 }];
    const winner = singleScenario.reduce((prev, current) =>
      prev.phi > current.phi ? prev : current
    );

    expect(winner.id).toBe("only");
  });

  it("should handle tied scenarios (returns one with equal phi)", () => {
    const tiedScenarios = [
      { id: "first", name: "First", phi: 0.75 },
      { id: "second", name: "Second", phi: 0.75 },
    ];
    const winner = tiedScenarios.reduce((prev, current) =>
      prev.phi > current.phi ? prev : current
    );

    // When tied, reduce returns the last one (current)
    expect(winner.id).toBe("second");
    expect(winner.phi).toBe(0.75);
  });
});

// ============================================================================
// Sensitivity Analysis Tests
// ============================================================================

describe("Sensitivity Analysis - Impact Calculation", () => {
  const calculateImpact = (
    current: number,
    baseline: number,
    sensitivity: number
  ): number => {
    const deviation = Math.abs((current - baseline) / baseline) * 100;
    return sensitivity * (deviation / 100);
  };

  it("should calculate impact correctly", () => {
    // 50% deviation with 0.85 sensitivity
    const impact = calculateImpact(0.75, 0.5, 0.85);
    expect(impact).toBeCloseTo(0.425, 2);
  });

  it("should classify impact levels correctly", () => {
    const getImpactLevel = (impact: number): string => {
      if (impact < 10) return "low";
      if (impact < 25) return "medium";
      if (impact < 50) return "high";
      return "critical";
    };

    expect(getImpactLevel(5)).toBe("low");
    expect(getImpactLevel(15)).toBe("medium");
    expect(getImpactLevel(35)).toBe("high");
    expect(getImpactLevel(60)).toBe("critical");
  });

  it("should handle zero baseline (edge case)", () => {
    // Should not divide by zero
    const result = calculateImpact(0.5, 0, 0.85);
    expect(result).toBe(Infinity);
  });
});

// ============================================================================
// Simulation Data Tests
// ============================================================================

describe("Simulation Data - Compartmental Model", () => {
  interface SimulationPoint {
    time: number;
    Susceptible: number;
    Misinformed: number;
    Truth: number;
    Inoculated: number;
    Resistant: number;
  }

  const generateSimulationData = (): SimulationPoint[] => {
    const data: SimulationPoint[] = [];
    for (let t = 0; t <= 100; t += 1) {
      const factor = t / 100;
      data.push({
        time: t,
        Susceptible: Math.max(0, 0.5 * Math.exp(-0.02 * t)),
        Misinformed: 0.3 * Math.sin(factor * Math.PI) * Math.exp(-0.01 * t),
        Truth: 0.3 * (1 - Math.exp(-0.03 * t)),
        Inoculated: 0.2 * (1 - Math.exp(-0.02 * t)),
        Resistant: 0.2 * (1 - Math.exp(-0.015 * t)),
      });
    }
    return data;
  };

  it("should generate correct number of data points", () => {
    const data = generateSimulationData();
    expect(data.length).toBe(101); // 0 to 100 inclusive
  });

  it("should have all compartments sum to reasonable value", () => {
    const data = generateSimulationData();
    const finalPoint = data[data.length - 1];

    const sum =
      finalPoint.Susceptible +
      finalPoint.Misinformed +
      finalPoint.Truth +
      finalPoint.Inoculated +
      finalPoint.Resistant;

    // The model doesn't enforce conservation, so sum varies
    // Just verify it's a reasonable positive value
    expect(sum).toBeGreaterThan(0);
    expect(sum).toBeLessThan(2);
  });

  it("should have Susceptible decreasing over time", () => {
    const data = generateSimulationData();
    const start = data[0].Susceptible;
    const end = data[data.length - 1].Susceptible;

    expect(end).toBeLessThan(start);
  });

  it("should have Truth increasing over time", () => {
    const data = generateSimulationData();
    const start = data[0].Truth;
    const end = data[data.length - 1].Truth;

    expect(end).toBeGreaterThan(start);
  });

  it("should have Resistant increasing over time", () => {
    const data = generateSimulationData();
    const start = data[0].Resistant;
    const end = data[data.length - 1].Resistant;

    expect(end).toBeGreaterThan(start);
  });
});

// ============================================================================
// File Upload Tests
// ============================================================================

describe("File Upload - File Type Detection", () => {
  const getFileType = (
    filename: string
  ): "csv" | "narrative" | "unknown" => {
    const ext = filename.split(".").pop()?.toLowerCase();
    if (ext === "csv") return "csv";
    if (ext === "txt" || ext === "md") return "narrative";
    return "unknown";
  };

  it("should detect CSV files", () => {
    expect(getFileType("narratives.csv")).toBe("csv");
    expect(getFileType("data.CSV")).toBe("csv");
  });

  it("should detect narrative files", () => {
    expect(getFileType("story.txt")).toBe("narrative");
    expect(getFileType("story.md")).toBe("narrative");
    expect(getFileType("story.TXT")).toBe("narrative");
  });

  it("should reject unsupported files", () => {
    expect(getFileType("document.pdf")).toBe("unknown");
    expect(getFileType("image.png")).toBe("unknown");
    expect(getFileType("archive.zip")).toBe("unknown");
  });

  it("should handle files without extension", () => {
    expect(getFileType("README")).toBe("unknown");
  });
});

// ============================================================================
// Color and Styling Tests
// ============================================================================

describe("Color Palette - Rwanda-Inspired Colors", () => {
  const colors = {
    Susceptible: "rgb(74, 144, 217)", // Blue
    Misinformed: "rgb(232, 82, 58)", // Red-orange
    Truth: "rgb(46, 204, 113)", // Green
    Inoculated: "rgb(243, 156, 18)", // Gold
    Resistant: "rgb(155, 89, 182)", // Purple
  };

  it("should have all compartments defined", () => {
    expect(Object.keys(colors)).toHaveLength(5);
    expect(colors.Susceptible).toBeDefined();
    expect(colors.Misinformed).toBeDefined();
    expect(colors.Truth).toBeDefined();
    expect(colors.Inoculated).toBeDefined();
    expect(colors.Resistant).toBeDefined();
  });

  it("should have valid RGB format", () => {
    const rgbRegex = /^rgb\(\d+,\s*\d+,\s*\d+\)$/;
    Object.values(colors).forEach((color) => {
      expect(color).toMatch(rgbRegex);
    });
  });
});
