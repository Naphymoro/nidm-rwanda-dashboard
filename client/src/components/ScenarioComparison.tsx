import React, { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
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

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

interface ScenarioComparisonProps {
  scenarios?: Scenario[];
  simulationData?: SimulationDataPoint[];
  title?: string;
}

function scenariosFromSimulation(data?: SimulationDataPoint[]): Scenario[] {
  const last = data?.at(-1);
  const mid = data?.[Math.floor((data.length || 1) / 2)];

  return [
    {
      id: "baseline",
      name: "Baseline",
      phi: 0.62,
      adoptionRate: ((last?.Truth ?? 0.42) + (last?.Resistant ?? 0.18)) * 100,
      inoculationCoverage: (last?.Inoculated ?? 0.28) * 100,
      convergenceTime: 74,
      misinformationPeak: mid?.Misinformed ?? 0.24,
    },
    {
      id: "trust-led",
      name: "Trust-led",
      phi: 0.78,
      adoptionRate: Math.min(88, ((last?.Truth ?? 0.42) + 0.18) * 100),
      inoculationCoverage: Math.min(76, ((last?.Inoculated ?? 0.28) + 0.14) * 100),
      convergenceTime: 58,
      misinformationPeak: Math.max(0.08, (mid?.Misinformed ?? 0.24) - 0.08),
      isWinner: true,
    },
    {
      id: "prebunking",
      name: "Prebunking",
      phi: 0.72,
      adoptionRate: Math.min(80, ((last?.Truth ?? 0.42) + 0.12) * 100),
      inoculationCoverage: Math.min(84, ((last?.Inoculated ?? 0.28) + 0.28) * 100),
      convergenceTime: 62,
      misinformationPeak: Math.max(0.06, (mid?.Misinformed ?? 0.24) - 0.12),
    },
  ];
}

const COLORS = ["var(--indigoL)", "var(--violet)", "var(--verdant)", "var(--gold)"];

export default function ScenarioComparison({
  scenarios,
  simulationData,
  title = "Scenario competition analysis",
}: ScenarioComparisonProps) {
  const scenarioList = useMemo(() => scenarios ?? scenariosFromSimulation(simulationData), [scenarios, simulationData]);
  const winner = scenarioList.reduce((prev, current) => (prev.phi > current.phi ? prev : current));

  const barChartData = scenarioList.map((scenario) => ({
    name: scenario.name,
    "Narrative Strength": Number(scenario.phi.toFixed(3)),
    "Adoption Rate": Number(scenario.adoptionRate.toFixed(1)),
    "Inoculation Coverage": Number(scenario.inoculationCoverage.toFixed(1)),
  }));

  const radarData = [
    {
      metric: "Phi",
      ...scenarioList.reduce((acc, scenario) => ({ ...acc, [scenario.name]: Number((scenario.phi * 100).toFixed(1)) }), {}),
    },
    {
      metric: "Adoption",
      ...scenarioList.reduce((acc, scenario) => ({ ...acc, [scenario.name]: Number(scenario.adoptionRate.toFixed(1)) }), {}),
    },
    {
      metric: "Inoculation",
      ...scenarioList.reduce((acc, scenario) => ({ ...acc, [scenario.name]: Number(scenario.inoculationCoverage.toFixed(1)) }), {}),
    },
    {
      metric: "Speed",
      ...scenarioList.reduce((acc, scenario) => ({ ...acc, [scenario.name]: Number((100 - scenario.convergenceTime).toFixed(1)) }), {}),
    },
  ];

  return (
    <div className="animate-page-in space-y-6">
      <section className="nidm-card p-5">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-mono-data text-[10px] uppercase tracking-[1.5px] text-[var(--t4)]">Competition</p>
            <h2 className="font-syne text-xl font-bold">{title}</h2>
          </div>
          <div className="flex items-center gap-3 rounded-lg border border-[rgba(245,159,0,.35)] bg-[rgba(245,159,0,.08)] px-3 py-2">
            <Trophy className="h-4 w-4 text-[var(--gold)]" />
            <div>
              <p className="font-mono-data text-[9px] uppercase tracking-[1.2px] text-[var(--t4)]">Current winner</p>
              <p className="font-syne text-sm font-bold text-[var(--gold)]">{winner.name}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={310}>
              <BarChart data={barChartData}>
                <CartesianGrid stroke="rgba(255,255,255,.05)" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Narrative Strength" fill="var(--indigoL)" radius={[7, 7, 0, 0]} />
                <Bar dataKey="Adoption Rate" fill="var(--verdant)" radius={[7, 7, 0, 0]} />
                <Bar dataKey="Inoculation Coverage" fill="var(--violet)" radius={[7, 7, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={310}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,.08)" />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                {scenarioList.map((scenario, index) => (
                  <Radar
                    key={scenario.id}
                    name={scenario.name}
                    dataKey={scenario.name}
                    stroke={COLORS[index % COLORS.length]}
                    fill={COLORS[index % COLORS.length]}
                    fillOpacity={0.2}
                  />
                ))}
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="nidm-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--bdr)] font-mono-data text-[10px] uppercase tracking-[1.4px] text-[var(--t4)]">
                <th className="px-4 py-3 text-left">Scenario</th>
                <th className="px-4 py-3 text-center">Phi</th>
                <th className="px-4 py-3 text-center">Adoption</th>
                <th className="px-4 py-3 text-center">Inoculation</th>
                <th className="px-4 py-3 text-center">Convergence</th>
                <th className="px-4 py-3 text-center">Peak M</th>
              </tr>
            </thead>
            <tbody>
              {scenarioList.map((scenario) => (
                <tr
                  key={scenario.id}
                  className={`border-b border-[rgba(255,255,255,.04)] ${scenario.id === winner.id ? "bg-[rgba(245,159,0,.06)]" : "hover:bg-[rgba(255,255,255,.025)]"}`}
                >
                  <td className="px-4 py-3 font-medium">
                    <span className="inline-flex items-center gap-2">
                      {scenario.id === winner.id ? <Trophy className="h-4 w-4 text-[var(--gold)]" /> : null}
                      {scenario.name}
                    </span>
                  </td>
                  <td className="font-mono-data px-4 py-3 text-center text-[var(--indigoL)]">{scenario.phi.toFixed(3)}</td>
                  <td className="font-mono-data px-4 py-3 text-center text-[var(--verdant)]">{scenario.adoptionRate.toFixed(1)}%</td>
                  <td className="font-mono-data px-4 py-3 text-center text-[var(--violet)]">{scenario.inoculationCoverage.toFixed(1)}%</td>
                  <td className="font-mono-data px-4 py-3 text-center text-[var(--gold)]">{scenario.convergenceTime.toFixed(0)}d</td>
                  <td className="font-mono-data px-4 py-3 text-center text-[var(--flame)]">{scenario.misinformationPeak.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
