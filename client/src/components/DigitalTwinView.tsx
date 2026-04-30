import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  Database,
  Brain,
  Activity,
  Network,
  TrendingUp,
  Award,
  Zap,
  Target,
} from "lucide-react";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  type: "input" | "model" | "policy" | "output" | "feedback";
  description: string;
}

interface Edge {
  from: string;
  to: string;
  label?: string;
  curved?: boolean;
}

const NODES: Node[] = [
  { id: "narratives", label: "Narrative\nEncoder", x: 80,  y: 180, type: "input",
    description: "E, C, τ, κ scoring of incoming narratives" },
  { id: "data",       label: "Survey &\nField Data",   x: 80,  y: 320, type: "input",
    description: "Rwanda clean-cooking survey signals" },
  { id: "nidm",       label: "NIDM ODE\nSolver",        x: 320, y: 250, type: "model",
    description: "Susceptible / Misinformed / Truth / Inoculated / Resistant compartments" },
  { id: "twin",       label: "Digital\nTwin State",     x: 560, y: 180, type: "model",
    description: "Synchronised mirror of population belief dynamics" },
  { id: "rl",         label: "RL Policy\nOptimizer",    x: 560, y: 320, type: "policy",
    description: "Selects narrative actions that maximise long-term Φ-reward" },
  { id: "outputs",    label: "Φ Forecasts\n& KPIs",     x: 800, y: 250, type: "output",
    description: "Composite narrative-strength predictions and dashboard KPIs" },
];

const EDGES: Edge[] = [
  { from: "narratives", to: "nidm" },
  { from: "data",       to: "nidm" },
  { from: "nidm",       to: "twin" },
  { from: "nidm",       to: "rl" },
  { from: "twin",       to: "outputs" },
  { from: "rl",         to: "outputs" },
  { from: "outputs",    to: "narratives", label: "feedback", curved: true },
];

const NODE_STYLES: Record<Node["type"], { fill: string; stroke: string; icon: React.ReactNode }> = {
  input:    { fill: "#1A3668", stroke: "#00A9B5", icon: <Database className="w-4 h-4" /> },
  model:    { fill: "#0E2A52", stroke: "#00A9B5", icon: <Activity className="w-4 h-4" /> },
  policy:   { fill: "#2A2410", stroke: "#F4A500", icon: <Brain className="w-4 h-4" /> },
  output:   { fill: "#0E2A52", stroke: "#F4A500", icon: <Target className="w-4 h-4" /> },
  feedback: { fill: "#1A3668", stroke: "#56B870", icon: <Network className="w-4 h-4" /> },
};

// Synthetic reward curve for RL convergence visualization
const REWARD_CURVE = Array.from({ length: 50 }, (_, i) => ({
  episode: i + 1,
  reward: 0.30 + 0.55 * (1 - Math.exp(-i / 12)) + (Math.random() - 0.5) * 0.04,
  baseline: 0.45,
}));

export default function DigitalTwinView() {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const getNode = (id: string) => NODES.find((n) => n.id === id)!;

  const finalReward = REWARD_CURVE[REWARD_CURVE.length - 1].reward;
  const improvement = ((finalReward - REWARD_CURVE[0].reward) / REWARD_CURVE[0].reward) * 100;

  return (
    <div className="space-y-6">
      {/* Architecture Diagram */}
      <Card className="glass-dark border-border/50 p-6 glow-secondary">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold neon-text">Digital Twin Architecture</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Live data flow between narrative inputs, the NIDM model, the digital twin,
              and the reinforcement-learning policy.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse-dot" />
            <span>Hover any node for details</span>
          </div>
        </div>

        <div className="relative w-full overflow-x-auto">
          <svg
            viewBox="0 0 900 460"
            className="w-full h-auto min-w-[700px]"
            style={{ background: "transparent" }}
          >
            <defs>
              <marker
                id="arrow"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#00A9B5" />
              </marker>
              <marker
                id="arrow-feedback"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#F4A500" />
              </marker>
            </defs>

            {/* Edges */}
            {EDGES.map((edge, i) => {
              const a = getNode(edge.from);
              const b = getNode(edge.to);
              const isFeedback = edge.label === "feedback";
              const stroke = isFeedback ? "#F4A500" : "#00A9B5";
              const marker = isFeedback ? "url(#arrow-feedback)" : "url(#arrow)";

              if (edge.curved) {
                // Curved feedback loop along the bottom
                const path = `M ${b.x + 40} ${b.y - 20} C ${(a.x + b.x) / 2} 440, ${(a.x + b.x) / 2} 440, ${a.x - 40} ${a.y + 20}`;
                return (
                  <g key={i}>
                    <path
                      d={path}
                      fill="none"
                      stroke={stroke}
                      strokeWidth="2"
                      strokeDasharray="6 4"
                      markerEnd={marker}
                      className="animate-flow-line"
                      opacity="0.7"
                    />
                    <text
                      x={(a.x + b.x) / 2}
                      y={420}
                      fill="#F4A500"
                      fontSize="11"
                      textAnchor="middle"
                      fontWeight="600"
                    >
                      RL feedback loop
                    </text>
                  </g>
                );
              }

              return (
                <line
                  key={i}
                  x1={a.x + 40}
                  y1={a.y}
                  x2={b.x - 40}
                  y2={b.y}
                  stroke={stroke}
                  strokeWidth="2"
                  strokeDasharray="6 4"
                  markerEnd={marker}
                  className="animate-flow-line"
                  opacity="0.75"
                />
              );
            })}

            {/* Nodes */}
            {NODES.map((node) => {
              const style = NODE_STYLES[node.type];
              const isHovered = hoveredNode === node.id;

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-transform"
                  onMouseEnter={() => setHoveredNode(node.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  style={{ transform: `translate(${node.x}px, ${node.y}px) ${isHovered ? "scale(1.06)" : "scale(1)"}`, transformBox: "fill-box", transformOrigin: "center" }}
                >
                  {/* Outer glow when hovered */}
                  {isHovered && (
                    <circle
                      r="48"
                      fill={style.stroke}
                      opacity="0.15"
                      className="animate-pulse-dot"
                    />
                  )}
                  <rect
                    x="-50"
                    y="-28"
                    width="100"
                    height="56"
                    rx="10"
                    fill={style.fill}
                    stroke={style.stroke}
                    strokeWidth={isHovered ? 2.5 : 1.5}
                  />
                  {node.label.split("\n").map((line, i, arr) => (
                    <text
                      key={i}
                      x="0"
                      y={(i - (arr.length - 1) / 2) * 14 + 4}
                      textAnchor="middle"
                      fill="#F5F7FA"
                      fontSize="11"
                      fontWeight="600"
                    >
                      {line}
                    </text>
                  ))}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Node details panel */}
        <div className="mt-4 p-4 bg-background/40 rounded-md border border-border/40 min-h-[60px]">
          {hoveredNode ? (
            <div className="flex items-start gap-3 animate-fade-in-up">
              <div className="text-primary">
                {NODE_STYLES[getNode(hoveredNode).type].icon}
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground">
                  {getNode(hoveredNode).label.replace(/\n/g, " ")}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {getNode(hoveredNode).description}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">
              The NIDM digital twin continuously ingests narratives and field data, simulates
              compartmental dynamics, and feeds the policy optimizer that selects the next-best
              communication action.
            </p>
          )}
        </div>
      </Card>

      {/* Reinforcement Learning Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="glass-dark border-border/50 p-5 lg:col-span-2 glow-primary">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              <h4 className="text-base font-bold neon-text">Reward Curve</h4>
            </div>
            <div className="text-xs text-muted-foreground">
              50 training episodes
            </div>
          </div>

          <ResponsiveContainer width="100%" height={220}>
            <LineChart
              data={REWARD_CURVE}
              margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
              <XAxis
                dataKey="episode"
                stroke="rgba(255,255,255,0.5)"
                style={{ fontSize: "11px" }}
                label={{ value: "Episode", position: "insideBottom", offset: -2, fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
              />
              <YAxis
                stroke="rgba(255,255,255,0.5)"
                style={{ fontSize: "11px" }}
                domain={[0, 1]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(14,26,51,0.95)",
                  border: "1px solid rgba(0,169,181,0.3)",
                  borderRadius: "8px",
                }}
              />
              <Line
                type="monotone"
                dataKey="baseline"
                stroke="#1A3668"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="Baseline policy"
              />
              <Line
                type="monotone"
                dataKey="reward"
                stroke="#00A9B5"
                strokeWidth={2.5}
                dot={false}
                name="RL agent"
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="glass-dark border-border/50 p-5 glow-accent">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-5 h-5 text-accent" />
            <h4 className="text-base font-bold neon-text">Optimization Results</h4>
          </div>

          <div className="space-y-3">
            <div className="p-3 bg-primary/10 rounded-md border border-primary/30">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">Best Φ achieved</span>
                <TrendingUp className="w-3 h-3 text-primary" />
              </div>
              <p className="text-2xl font-bold text-primary">
                {finalReward.toFixed(3)}
              </p>
            </div>

            <div className="p-3 bg-accent/10 rounded-md border border-accent/30">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">vs baseline</span>
                <Zap className="w-3 h-3 text-accent" />
              </div>
              <p className="text-2xl font-bold text-accent">
                +{improvement.toFixed(1)}%
              </p>
            </div>

            <div className="pt-3 border-t border-border/40">
              <p className="text-xs text-muted-foreground mb-2">Top action</p>
              <p className="text-sm font-semibold text-foreground">
                Boost trust alignment (τ)
              </p>
              <div className="w-full h-2 bg-background/40 rounded-full mt-2 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent"
                  style={{ width: "82%" }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">82% policy weight</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
