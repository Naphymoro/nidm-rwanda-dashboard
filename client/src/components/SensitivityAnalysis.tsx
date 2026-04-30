import React, { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface SensitivityData {
  parameter: string;
  baseline: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  impact: number;
}

interface SensitivityAnalysisProps {
  parameters?: SensitivityData[];
  title?: string;
}

const DEFAULT_PARAMETERS: SensitivityData[] = [
  {
    parameter: "β (Transmission Rate)",
    baseline: 0.5,
    min: 0.1,
    max: 1.0,
    step: 0.05,
    unit: "",
    impact: 0.85,
  },
  {
    parameter: "γ (Recovery Rate)",
    baseline: 0.3,
    min: 0.05,
    max: 0.8,
    step: 0.05,
    unit: "",
    impact: 0.42,
  },
  {
    parameter: "ι (Inoculation Rate)",
    baseline: 0.2,
    min: 0.0,
    max: 0.6,
    step: 0.05,
    unit: "",
    impact: 0.68,
  },
  {
    parameter: "Φ (Narrative Strength)",
    baseline: 0.65,
    min: 0.2,
    max: 1.0,
    step: 0.05,
    unit: "",
    impact: 0.72,
  },
];

export default function SensitivityAnalysis({
  parameters = DEFAULT_PARAMETERS,
  title = "Sensitivity Analysis",
}: SensitivityAnalysisProps) {
  const [values, setValues] = useState<Record<string, number>>(
    parameters.reduce((acc, p) => ({ ...acc, [p.parameter]: p.baseline }), {})
  );

  const handleParameterChange = (parameter: string, value: number) => {
    setValues((prev) => ({ ...prev, [parameter]: value }));
  };

  const handleReset = () => {
    setValues(
      parameters.reduce((acc, p) => ({ ...acc, [p.parameter]: p.baseline }), {})
    );
  };

  // Generate heatmap data
  const heatmapData = useMemo(() => {
    return parameters.map((param) => {
      const current = values[param.parameter];
      const deviation = ((current - param.baseline) / param.baseline) * 100;
      const impact = param.impact * Math.abs(deviation) / 100;
      return {
        parameter: param.parameter,
        current,
        baseline: param.baseline,
        deviation,
        impact,
        color: getHeatmapColor(impact),
      };
    });
  }, [values, parameters]);

  const getHeatmapColor = (impact: number): string => {
    if (impact < 10) return "bg-green-900/30 border-green-500/50";
    if (impact < 25) return "bg-yellow-900/30 border-yellow-500/50";
    if (impact < 50) return "bg-orange-900/30 border-orange-500/50";
    return "bg-red-900/30 border-red-500/50";
  };

  const getImpactColor = (impact: number): string => {
    if (impact < 10) return "text-green-400";
    if (impact < 25) return "text-yellow-400";
    if (impact < 50) return "text-orange-400";
    return "text-red-400";
  };

  return (
    <div className="space-y-6">
      <div className="glass-dark border border-border/50 rounded-lg p-6 glow-secondary">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold neon-text">{title}</h3>
          <Button
            onClick={handleReset}
            className="text-sm bg-primary/20 hover:bg-primary/30 text-primary"
          >
            Reset to Baseline
          </Button>
        </div>

        {/* Parameter Sliders */}
        <div className="space-y-6 mb-8">
          {parameters.map((param) => (
            <div key={param.parameter} className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-foreground">
                  {param.parameter}
                </label>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-primary">
                    {values[param.parameter].toFixed(3)}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    (baseline: {param.baseline.toFixed(3)})
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  value={values[param.parameter]}
                  onChange={(e) =>
                    handleParameterChange(param.parameter, parseFloat(e.target.value))
                  }
                  className="flex-1 h-2 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <span className="text-xs text-muted-foreground w-16 text-right">
                  {param.min.toFixed(2)} - {param.max.toFixed(2)}
                </span>
              </div>

              {/* Impact indicator */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1 bg-border rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.abs(
                          ((values[param.parameter] - param.baseline) /
                            param.baseline) *
                            100
                        )
                      )}%`,
                    }}
                  />
                </div>
                <span className="text-xs text-muted-foreground w-12 text-right">
                  {(
                    ((values[param.parameter] - param.baseline) /
                      param.baseline) *
                    100
                  ).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Heatmap */}
        <div className="border-t border-border/50 pt-6">
          <h4 className="text-sm font-semibold text-foreground mb-4">
            Impact Heatmap
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {heatmapData.map((data) => (
              <Card
                key={data.parameter}
                className={`border p-4 transition-all duration-300 ${data.color}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-sm font-medium text-foreground">
                    {data.parameter}
                  </span>
                  <span className={`text-lg font-bold ${getImpactColor(data.impact)}`}>
                    {data.impact.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <p>
                    Current: <span className="font-mono">{data.current.toFixed(3)}</span>
                  </p>
                  <p>
                    Deviation:{" "}
                    <span className={data.deviation > 0 ? "text-chart-3" : "text-accent"}>
                      {data.deviation > 0 ? "+" : ""}
                      {data.deviation.toFixed(1)}%
                    </span>
                  </p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Summary Statistics */}
        <div className="border-t border-border/50 pt-6 mt-6">
          <h4 className="text-sm font-semibold text-foreground mb-4">
            Sensitivity Summary
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
              <p className="text-xs text-muted-foreground mb-1">Average Impact</p>
              <p className="text-2xl font-bold text-primary">
                {(
                  heatmapData.reduce((sum, d) => sum + d.impact, 0) /
                  heatmapData.length
                ).toFixed(1)}
                %
              </p>
            </div>
            <div className="bg-accent/10 border border-accent/20 rounded-lg p-4">
              <p className="text-xs text-muted-foreground mb-1">Max Impact</p>
              <p className="text-2xl font-bold text-accent">
                {Math.max(...heatmapData.map((d) => d.impact)).toFixed(1)}%
              </p>
            </div>
            <div className="bg-secondary/10 border border-secondary/20 rounded-lg p-4">
              <p className="text-xs text-muted-foreground mb-1">High Sensitivity</p>
              <p className="text-2xl font-bold text-secondary">
                {heatmapData.filter((d) => d.impact > 50).length}
              </p>
            </div>
            <div className="bg-chart-4/10 border border-chart-4/20 rounded-lg p-4">
              <p className="text-xs text-muted-foreground mb-1">Robust Parameters</p>
              <p className="text-2xl font-bold text-chart-4">
                {heatmapData.filter((d) => d.impact < 10).length}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
