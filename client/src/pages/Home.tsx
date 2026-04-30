import React, { useCallback, useMemo, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import NarrativeEncodingPanel from "@/components/NarrativeEncodingPanel";
import SimulationPlayer from "@/components/SimulationPlayer";
import SimulationChart from "@/components/SimulationChart";
import KPICard from "@/components/KPICard";
import ScenarioComparison from "@/components/ScenarioComparison";
import SensitivityAnalysis from "@/components/SensitivityAnalysis";
import FileUploadPanel from "@/components/FileUploadPanel";
import NarrativeLibrary from "@/components/NarrativeLibrary";
import DigitalTwinView from "@/components/DigitalTwinView";
import { Card } from "@/components/ui/card";
import {
  Zap,
  BarChart3,
  Settings,
  Upload,
  Brain,
  Network,
} from "lucide-react";
import { ParsedNarrative } from "@/lib/narrativeParser";

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

const generateSimulationData = (): SimulationDataPoint[] => {
  const data: SimulationDataPoint[] = [];
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

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const simulationData = useMemo(() => generateSimulationData(), []);
  const [narratives, setNarratives] = useState<ParsedNarrative[]>([]);

  const handleNarrativesParsed = useCallback((parsed: ParsedNarrative[]) => {
    setNarratives((prev) => [...prev, ...parsed]);
  }, []);

  const handleRemoveNarrative = useCallback((id: string) => {
    setNarratives((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const handleClearNarratives = useCallback(() => setNarratives([]), []);

  const tabs = [
    { id: "dashboard",  label: "Dashboard",   icon: <Zap className="w-5 h-5" /> },
    { id: "narratives", label: "Narratives",  icon: <Brain className="w-5 h-5" /> },
    { id: "simulation", label: "Simulation",  icon: <BarChart3 className="w-5 h-5" /> },
    { id: "twin",       label: "Digital Twin", icon: <Network className="w-5 h-5" /> },
    { id: "analysis",   label: "Analysis",    icon: <Settings className="w-5 h-5" /> },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardView simulationData={simulationData} narrativeCount={narratives.length} />;
      case "narratives":
        return (
          <NarrativesView
            narratives={narratives}
            onNarrativesParsed={handleNarrativesParsed}
            onRemove={handleRemoveNarrative}
            onClear={handleClearNarratives}
          />
        );
      case "simulation":
        return <SimulationView simulationData={simulationData} />;
      case "twin":
        return <DigitalTwinView />;
      case "analysis":
        return <AnalysisView />;
      default:
        return <DashboardView simulationData={simulationData} narrativeCount={narratives.length} />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab} tabs={tabs}>
      {renderContent()}
    </DashboardLayout>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Dashboard View
// ────────────────────────────────────────────────────────────────────────────
function DashboardView({
  simulationData,
  narrativeCount,
}: {
  simulationData: SimulationDataPoint[];
  narrativeCount: number;
}) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">Key Performance Indicators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Model Convergence"
            value={87.5}
            unit="%"
            trend="up"
            trendValue={12.3}
            icon={<Zap className="w-5 h-5" />}
            glowColor="primary"
          />
          <KPICard
            label="Narrative Strength (Φ)"
            value={0.6842}
            unit=""
            trend="up"
            trendValue={5.2}
            icon={<Brain className="w-5 h-5" />}
            glowColor="accent"
          />
          <KPICard
            label="Truth Adoption Rate"
            value={42.3}
            unit="%"
            trend="up"
            trendValue={8.7}
            icon={<BarChart3 className="w-5 h-5" />}
            glowColor="secondary"
          />
          <KPICard
            label="Inoculation Coverage"
            value={31.8}
            unit="%"
            trend="up"
            trendValue={3.1}
            icon={<Upload className="w-5 h-5" />}
            glowColor="chart-1"
          />
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">Simulation Overview</h2>
        <SimulationChart data={simulationData} height={300} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass-dark border-border/50 p-6 glow-primary">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Active Narratives</h3>
          <p className="text-3xl font-bold text-primary">{Math.max(narrativeCount, 12)}</p>
          <p className="text-xs text-muted-foreground mt-2">
            {narrativeCount > 0 ? `${narrativeCount} loaded from files` : "+3 this week"}
          </p>
        </Card>
        <Card className="glass-dark border-border/50 p-6 glow-accent">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Scenario Runs</h3>
          <p className="text-3xl font-bold text-accent">47</p>
          <p className="text-xs text-muted-foreground mt-2">+8 this week</p>
        </Card>
        <Card className="glass-dark border-border/50 p-6 glow-secondary">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Model Accuracy</h3>
          <p className="text-3xl font-bold text-foreground">94.2%</p>
          <p className="text-xs text-muted-foreground mt-2">±2.1% confidence</p>
        </Card>
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Narratives View
// ────────────────────────────────────────────────────────────────────────────
function NarrativesView({
  narratives,
  onNarrativesParsed,
  onRemove,
  onClear,
}: {
  narratives: ParsedNarrative[];
  onNarrativesParsed: (n: ParsedNarrative[]) => void;
  onRemove: (id: string) => void;
  onClear: () => void;
}) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">Narrative Management</h2>
        <p className="text-muted-foreground mb-6">
          Create and manage narratives for your NIDM simulations. Score each narrative across
          four dimensions to compute the composite Narrative Strength (Φ).
        </p>
      </div>
      <NarrativeEncodingPanel />
      <FileUploadPanel onNarrativesParsed={onNarrativesParsed} />
      <NarrativeLibrary
        narratives={narratives}
        onRemove={onRemove}
        onClear={onClear}
      />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Simulation View (with playback controls)
// ────────────────────────────────────────────────────────────────────────────
function SimulationView({ simulationData }: { simulationData: SimulationDataPoint[] }) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">NIDM Simulation</h2>
        <p className="text-muted-foreground mb-6">
          Visualise the compartmental model trajectories for the Susceptible, Misinformed,
          Truth, Inoculated, and Resistant populations. Use the playback controls below the
          chart to scrub through time, pause on a moment of interest, or replay at variable
          speed.
        </p>
      </div>
      <SimulationPlayer fullData={simulationData} />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Analysis View
// ────────────────────────────────────────────────────────────────────────────
function AnalysisView() {
  const mockScenarios = [
    {
      id: "baseline",
      name: "Baseline Scenario",
      phi: 0.65,
      adoptionRate: 42.3,
      inoculationCoverage: 31.8,
      convergenceTime: 75,
      misinformationPeak: 0.28,
    },
    {
      id: "high-engagement",
      name: "High Engagement",
      phi: 0.82,
      adoptionRate: 68.5,
      inoculationCoverage: 52.1,
      convergenceTime: 62,
      misinformationPeak: 0.18,
      isWinner: true,
    },
    {
      id: "targeted-inoculation",
      name: "Targeted Inoculation",
      phi: 0.71,
      adoptionRate: 55.2,
      inoculationCoverage: 71.3,
      convergenceTime: 58,
      misinformationPeak: 0.15,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">Sensitivity & Scenario Analysis</h2>
        <p className="text-muted-foreground mb-6">
          Explore how model outputs change as you vary input parameters and compare multiple
          narrative scenarios.
        </p>
      </div>
      <ScenarioComparison scenarios={mockScenarios} />
      <SensitivityAnalysis />
    </div>
  );
}
