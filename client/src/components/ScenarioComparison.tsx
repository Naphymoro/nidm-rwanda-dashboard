import React from "react";
import { Card } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import { Trophy } from "lucide-react";

interface Scenario {
  id: string;
  name: string;
  phi: number;
  adoptionRate: number;
  inoculationCoverage: number;
  convergenceTime: number;
  misinformationPeak: number;
  isWinner?: boolean;
}

interface ScenarioComparisonProps {
  scenarios: Scenario[];
  title?: string;
}

export default function ScenarioComparison({
  scenarios,
  title = "Scenario Competition Analysis",
}: ScenarioComparisonProps) {
  // Determine winner based on Φ (Narrative Strength)
  const winner = scenarios.reduce((prev, current) =>
    prev.phi > current.phi ? prev : current
  );

  // Prepare data for bar chart
  const barChartData = scenarios.map((s) => ({
    name: s.name,
    "Narrative Strength (Φ)": parseFloat(s.phi.toFixed(4)),
    "Adoption Rate": s.adoptionRate,
    "Inoculation Coverage": s.inoculationCoverage,
  }));

  // Prepare data for radar chart
  const radarData = [
    {
      metric: "Narrative Strength",
      ...scenarios.reduce(
        (acc, s) => ({ ...acc, [s.name]: parseFloat((s.phi * 100).toFixed(1)) }),
        {}
      ),
    },
    {
      metric: "Adoption Rate",
      ...scenarios.reduce(
        (acc, s) => ({ ...acc, [s.name]: s.adoptionRate }),
        {}
      ),
    },
    {
      metric: "Inoculation",
      ...scenarios.reduce(
        (acc, s) => ({ ...acc, [s.name]: s.inoculationCoverage }),
        {}
      ),
    },
    {
      metric: "Convergence",
      ...scenarios.reduce(
        (acc, s) => ({ ...acc, [s.name]: 100 - s.convergenceTime }),
        {}
      ),
    },
  ];

  const colors = [
    "rgb(0, 255, 200)",
    "rgb(255, 0, 150)",
    "rgb(100, 200, 255)",
    "rgb(243, 156, 18)",
  ];

  return (
    <div className="space-y-6">
      <div className="glass-dark border border-border/50 rounded-lg p-6 glow-accent">
        <h3 className="text-lg font-bold neon-text mb-6">{title}</h3>

        {/* Winner Badge */}
        {winner && (
          <div className="mb-6 p-4 bg-gradient-to-r from-chart-4/20 to-accent/20 border border-chart-4/50 rounded-lg flex items-center gap-3">
            <Trophy className="w-6 h-6 text-chart-4" />
            <div>
              <p className="text-sm text-muted-foreground">Current Winner</p>
              <p className="text-lg font-bold text-chart-4">{winner.name}</p>
              <p className="text-sm text-muted-foreground">
                Φ = {winner.phi.toFixed(4)}
              </p>
            </div>
          </div>
        )}

        {/* Bar Chart Comparison */}
        <div className="mb-8">
          <h4 className="text-sm font-semibold text-foreground mb-4">
            Key Metrics Comparison
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255, 255, 255, 0.1)"
              />
              <XAxis dataKey="name" stroke="rgba(255, 255, 255, 0.5)" />
              <YAxis stroke="rgba(255, 255, 255, 0.5)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(13, 13, 26, 0.95)",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Bar
                dataKey="Narrative Strength (Φ)"
                fill="rgb(0, 255, 200)"
                radius={[8, 8, 0, 0]}
              />
              <Bar
                dataKey="Adoption Rate"
                fill="rgb(255, 0, 150)"
                radius={[8, 8, 0, 0]}
              />
              <Bar
                dataKey="Inoculation Coverage"
                fill="rgb(100, 200, 255)"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar Chart */}
        <div className="mb-8">
          <h4 className="text-sm font-semibold text-foreground mb-4">
            Multi-Dimensional Performance
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255, 255, 255, 0.1)" />
              <PolarAngleAxis
                dataKey="metric"
                stroke="rgba(255, 255, 255, 0.5)"
              />
              <PolarRadiusAxis stroke="rgba(255, 255, 255, 0.5)" />
              <Radar
                name={scenarios[0]?.name}
                dataKey={scenarios[0]?.name}
                stroke={colors[0]}
                fill={colors[0]}
                fillOpacity={0.25}
              />
              {scenarios.length > 1 && (
                <Radar
                  name={scenarios[1]?.name}
                  dataKey={scenarios[1]?.name}
                  stroke={colors[1]}
                  fill={colors[1]}
                  fillOpacity={0.25}
                />
              )}
              {scenarios.length > 2 && (
                <Radar
                  name={scenarios[2]?.name}
                  dataKey={scenarios[2]?.name}
                  stroke={colors[2]}
                  fill={colors[2]}
                  fillOpacity={0.25}
                />
              )}
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Comparison Table */}
        <div>
          <h4 className="text-sm font-semibold text-foreground mb-4">
            Detailed Metrics
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/50">
                  <th className="text-left py-3 px-4 text-muted-foreground font-medium">
                    Scenario
                  </th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                    Φ (Strength)
                  </th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                    Adoption %
                  </th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                    Inoculation %
                  </th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                    Convergence (days)
                  </th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                    Peak Misinformation
                  </th>
                </tr>
              </thead>
              <tbody>
                {scenarios.map((scenario) => (
                  <tr
                    key={scenario.id}
                    className={`border-b border-border/30 transition-colors ${
                      scenario.id === winner.id
                        ? "bg-chart-4/10"
                        : "hover:bg-white/5"
                    }`}
                  >
                    <td className="py-3 px-4 font-medium">
                      <div className="flex items-center gap-2">
                        {scenario.id === winner.id && (
                          <Trophy className="w-4 h-4 text-chart-4" />
                        )}
                        {scenario.name}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-primary">
                        {scenario.phi.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-chart-3">
                        {scenario.adoptionRate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-secondary">
                        {scenario.inoculationCoverage.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-accent">
                        {scenario.convergenceTime.toFixed(0)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-destructive">
                        {scenario.misinformationPeak.toFixed(3)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
