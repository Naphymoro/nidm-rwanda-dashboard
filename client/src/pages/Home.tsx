import React, { useState, useMemo } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import NarrativeEncodingPanel from "@/components/NarrativeEncodingPanel";
import SimulationChart from "@/components/SimulationChart";
import KPICard from "@/components/KPICard";
import ScenarioComparison from "@/components/ScenarioComparison";
import SensitivityAnalysis from "@/components/SensitivityAnalysis";
import FileUploadPanel from "@/components/FileUploadPanel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Zap, BarChart3, Settings, Upload, Brain } from "lucide-react";

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

// Generate mock simulation data
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

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: <Zap className="w-5 h-5" /> },
    { id: "narratives", label: "Narratives", icon: <Brain className="w-5 h-5" /> },
    { id: "simulation", label: "Simulation", icon: <BarChart3 className="w-5 h-5" /> },
    { id: "analysis", label: "Analysis", icon: <Settings className="w-5 h-5" /> },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardView simulationData={simulationData} />;
      case "narratives":
        return <NarrativesView />;
      case "simulation":
        return <SimulationView simulationData={simulationData} />;
      case "analysis":
        return <AnalysisView />;
      default:
        return <DashboardView simulationData={simulationData} />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab} tabs={tabs}>
      {renderContent()}
    </DashboardLayout>
  );
}

// Dashboard View
function DashboardView({ simulationData }: { simulationData: SimulationDataPoint[] }) {
  return (
    <div className="space-y-8">
      {/* KPI Cards */}
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

      {/* Simulation Overview */}
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">Simulation Overview</h2>
        <SimulationChart data={simulationData} height={300} />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass-dark border-border/50 p-6 glow-primary">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">
            Active Narratives
          </h3>
          <p className="text-3xl font-bold text-primary">12</p>
          <p className="text-xs text-muted-foreground mt-2">+3 this week</p>
        </Card>
        <Card className="glass-dark border-border/50 p-6 glow-accent">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">
            Scenario Runs
          </h3>
          <p className="text-3xl font-bold text-accent">47</p>
          <p className="text-xs text-muted-foreground mt-2">+8 this week</p>
        </Card>
        <Card className="glass-dark border-border/50 p-6 glow-secondary">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">
            Model Accuracy
          </h3>
          <p className="text-3xl font-bold text-secondary">94.2%</p>
          <p className="text-xs text-muted-foreground mt-2">±2.1% confidence</p>
        </Card>
      </div>
    </div>
  );
}

// Narratives View
function NarrativesView() {
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
      <FileUploadPanel />
    </div>
  );
}

// Simulation View
function SimulationView({ simulationData }: { simulationData: SimulationDataPoint[] }) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold neon-text mb-4">NIDM Simulation</h2>
        <p className="text-muted-foreground mb-6">
          Visualize the compartmental model trajectories showing how populations transition between
          Susceptible, Misinformed, Truth, Inoculated, and Resistant states over time.
        </p>
      </div>
      <SimulationChart data={simulationData} height={500} />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="glass-dark border-border/50 p-6">
          <h3 className="text-lg font-bold neon-text mb-4">Simulation Parameters</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">
                Transmission Rate (β)
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                defaultValue="0.5"
                className="w-full accent-primary"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">
                Recovery Rate (γ)
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                defaultValue="0.3"
                className="w-full accent-primary"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">
                Inoculation Rate (ι)
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                defaultValue="0.2"
                className="w-full accent-primary"
              />
            </div>
            <Button className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/80 hover:to-accent/80 text-background font-bold">
              Run Simulation
            </Button>
          </div>
        </Card>
        <Card className="glass-dark border-border/50 p-6">
          <h3 className="text-lg font-bold neon-text mb-4">Model Statistics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Peak Misinformation</span>
              <span className="font-bold text-accent">0.28 (t=35)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Final Truth Adoption</span>
              <span className="font-bold text-chart-3">0.62</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Inoculation Effectiveness</span>
              <span className="font-bold text-chart-4">85.3%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Model Convergence Time</span>
              <span className="font-bold text-primary">~75 days</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

// Analysis View
function AnalysisView() {
  const mockScenarios = [
    {
      id: "baseline",
      name: "Baseline Scenario",
      phi: 0.6500,
      adoptionRate: 42.3,
      inoculationCoverage: 31.8,
      convergenceTime: 75,
      misinformationPeak: 0.28,
    },
    {
      id: "high-engagement",
      name: "High Engagement",
      phi: 0.8200,
      adoptionRate: 68.5,
      inoculationCoverage: 52.1,
      convergenceTime: 62,
      misinformationPeak: 0.18,
      isWinner: true,
    },
    {
      id: "targeted-inoculation",
      name: "Targeted Inoculation",
      phi: 0.7100,
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

      {/* Scenario Comparison */}
      <ScenarioComparison scenarios={mockScenarios} />

      {/* Sensitivity Analysis */}
      <SensitivityAnalysis />
    </div>
  );
}
