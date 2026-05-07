import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  Award,
  Brain,
  Database,
  Network,
  Target,
  TrendingUp,
  UsersRound,
  Zap,
} from "lucide-react";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  type: "input" | "model" | "agent" | "policy" | "output" | "feedback";
  description: string;
}

interface Edge {
  from: string;
  to: string;
  label?: string;
  curved?: boolean;
}

const NODES: Node[] = [
  { id: "narratives", label: "Narrative\nEncoder", x: 80, y: 180, type: "input", description: "Evidence, credibility, trust, and channel scoring of incoming narratives" },
  { id: "data", label: "Survey &\nField Data", x: 80, y: 320, type: "input", description: "Rwanda clean-cooking survey and field data signals" },
  { id: "nidm", label: "NIDM ODE\nSolver", x: 320, y: 250, type: "model", description: "Susceptible, Misinformed, Truth, Inoculated, and Resistant compartments" },
  { id: "abm", label: "ABM\nAgents", x: 520, y: 250, type: "agent", description: "Household agents with trust, peer influence, media exposure, district context, and field-worker reach" },
  { id: "twin", label: "Digital\nTwin State", x: 680, y: 180, type: "model", description: "Synchronized mirror of population belief dynamics" },
  { id: "rl", label: "RL Policy\nOptimizer", x: 680, y: 320, type: "policy", description: "Selects narrative actions that maximize long-term Phi reward" },
  { id: "outputs", label: "Phi Forecasts\n& KPIs", x: 800, y: 250, type: "output", description: "Composite narrative-strength predictions and dashboard KPIs" },
];

const EDGES: Edge[] = [
  { from: "narratives", to: "nidm" },
  { from: "data", to: "nidm" },
  { from: "nidm", to: "abm" },
  { from: "abm", to: "twin" },
  { from: "abm", to: "rl" },
  { from: "twin", to: "outputs" },
  { from: "rl", to: "outputs" },
  { from: "outputs", to: "narratives", label: "feedback", curved: true },
];

const NODE_STYLES: Record<Node["type"], { fill: string; stroke: string; icon: React.ReactNode }> = {
  input: { fill: "var(--well)", stroke: "var(--sky)", icon: <Database className="h-4 w-4" /> },
  model: { fill: "var(--card)", stroke: "var(--indigoL)", icon: <Activity className="h-4 w-4" /> },
  agent: { fill: "var(--well)", stroke: "var(--sky)", icon: <UsersRound className="h-4 w-4" /> },
  policy: { fill: "var(--well)", stroke: "var(--gold)", icon: <Brain className="h-4 w-4" /> },
  output: { fill: "var(--card)", stroke: "var(--violet)", icon: <Target className="h-4 w-4" /> },
  feedback: { fill: "var(--well)", stroke: "var(--verdant)", icon: <Network className="h-4 w-4" /> },
};

const REWARD_CURVE = Array.from({ length: 50 }, (_, index) => ({
  episode: index + 1,
  reward: 0.3 + 0.55 * (1 - Math.exp(-index / 12)) + Math.sin(index * 0.7) * 0.018,
  baseline: 0.45,
}));

export default function DigitalTwinView() {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const getNode = (id: string) => NODES.find((node) => node.id === id)!;
  const finalReward = REWARD_CURVE[REWARD_CURVE.length - 1].reward;
  const improvement = ((finalReward - REWARD_CURVE[0].reward) / REWARD_CURVE[0].reward) * 100;

  return (
    <div className="animate-page-in space-y-6">
      <Card className="nidm-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-syne text-lg font-bold">Digital Twin Architecture</h3>
            <p className="mt-1 text-xs text-[var(--t3)]">
              Live data flow between narrative inputs, ODE compartments, ABM household agents, the digital twin, and reinforcement-learning policy.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-[var(--t3)]">
            <span className="twin-pulse" />
            <span>Hover nodes</span>
          </div>
        </div>

        <div className="relative w-full overflow-x-auto rounded-lg bg-[var(--deep)]">
          <svg viewBox="0 0 900 460" className="h-auto w-full min-w-[700px]">
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--indigoL)" />
              </marker>
              <marker id="arrow-feedback" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--gold)" />
              </marker>
            </defs>

            {EDGES.map((edge, index) => {
              const a = getNode(edge.from);
              const b = getNode(edge.to);
              const isFeedback = edge.label === "feedback";
              const stroke = isFeedback ? "var(--gold)" : "var(--indigoL)";
              const marker = isFeedback ? "url(#arrow-feedback)" : "url(#arrow)";

              if (edge.curved) {
                const path = `M ${b.x + 40} ${b.y - 20} C ${(a.x + b.x) / 2} 440, ${(a.x + b.x) / 2} 440, ${a.x - 40} ${a.y + 20}`;
                return (
                  <g key={index}>
                    <path d={path} fill="none" stroke={stroke} strokeWidth="2" strokeDasharray="6 4" markerEnd={marker} className="animate-flow-line" opacity="0.72" />
                    <text x={(a.x + b.x) / 2} y={420} fill="var(--gold)" fontSize="11" textAnchor="middle" fontWeight="600">
                      RL feedback loop
                    </text>
                  </g>
                );
              }

              return (
                <line key={index} x1={a.x + 40} y1={a.y} x2={b.x - 40} y2={b.y} stroke={stroke} strokeWidth="2" strokeDasharray="6 4" markerEnd={marker} className="animate-flow-line" opacity="0.75" />
              );
            })}

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
                  {isHovered ? <circle r="48" fill={style.stroke} opacity="0.15" className="animate-pulse-dot" /> : null}
                  <rect x="-50" y="-28" width="100" height="56" rx="10" fill={style.fill} stroke={style.stroke} strokeWidth={isHovered ? 2.5 : 1.5} />
                  {node.label.split("\n").map((line, lineIndex, arr) => (
                    <text key={line} x="0" y={(lineIndex - (arr.length - 1) / 2) * 14 + 4} textAnchor="middle" fill="var(--t1)" fontSize="11" fontWeight="600">
                      {line}
                    </text>
                  ))}
                </g>
              );
            })}
          </svg>
        </div>

        <div className="mt-4 min-h-[60px] rounded-md border border-[var(--bdr)] bg-[var(--deep)] p-4">
          {hoveredNode ? (
            <div className="animate-fade-in-up flex items-start gap-3">
              <div className="text-[var(--indigoL)]">{NODE_STYLES[getNode(hoveredNode).type].icon}</div>
              <div>
                <p className="text-sm font-semibold text-[var(--t1)]">{getNode(hoveredNode).label.replace(/\n/g, " ")}</p>
                <p className="mt-1 text-xs text-[var(--t3)]">{getNode(hoveredNode).description}</p>
              </div>
            </div>
          ) : (
            <p className="text-xs italic text-[var(--t3)]">
              The NIDM digital twin continuously ingests narratives and field data, simulates compartmental and agent-based dynamics, and feeds the policy optimizer.
            </p>
          )}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="nidm-card p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-[var(--indigoL)]" />
              <h4 className="font-syne text-base font-bold">Reward Curve</h4>
            </div>
            <div className="font-mono-data text-xs text-[var(--t3)]">50 training episodes</div>
          </div>

          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={REWARD_CURVE} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.05)" vertical={false} />
                <XAxis dataKey="episode" stroke="rgba(232,236,247,.35)" label={{ value: "Episode", position: "insideBottom", offset: -2, fill: "rgba(232,236,247,.38)", fontSize: 10 }} />
                <YAxis stroke="rgba(232,236,247,.35)" domain={[0, 1]} />
                <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--bdrV)", borderRadius: "8px" }} />
                <Line type="monotone" dataKey="baseline" stroke="var(--fold)" strokeWidth={2} strokeDasharray="4 4" dot={false} name="Baseline policy" />
                <Line type="monotone" dataKey="reward" stroke="var(--verdant)" strokeWidth={2.5} dot={false} name="RL agent" isAnimationActive />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="nidm-card p-5">
          <div className="mb-4 flex items-center gap-2">
            <Award className="h-5 w-5 text-[var(--gold)]" />
            <h4 className="font-syne text-base font-bold">Optimization Results</h4>
          </div>

          <div className="space-y-3">
            <div className="rounded-md border border-[rgba(116,143,252,.3)] bg-[rgba(116,143,252,.08)] p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs text-[var(--t3)]">Best Phi achieved</span>
                <TrendingUp className="h-3 w-3 text-[var(--indigoL)]" />
              </div>
              <p className="font-syne text-2xl font-bold text-[var(--indigoL)]">{finalReward.toFixed(3)}</p>
            </div>

            <div className="rounded-md border border-[rgba(245,159,0,.3)] bg-[rgba(245,159,0,.08)] p-3">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs text-[var(--t3)]">vs baseline</span>
                <Zap className="h-3 w-3 text-[var(--gold)]" />
              </div>
              <p className="font-syne text-2xl font-bold text-[var(--gold)]">+{improvement.toFixed(1)}%</p>
            </div>

            <div className="border-t border-[var(--bdr)] pt-3">
              <p className="mb-2 text-xs text-[var(--t3)]">Top action</p>
              <p className="text-sm font-semibold text-[var(--t1)]">Boost trust alignment</p>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-[var(--fold)]">
                <div className="h-full bg-gradient-to-r from-[var(--indigo)] to-[var(--gold)]" style={{ width: "82%" }} />
              </div>
              <p className="mt-1 text-xs text-[var(--t3)]">82% policy weight</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
