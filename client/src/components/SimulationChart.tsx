import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

interface SimulationChartProps {
  data: SimulationDataPoint[];
  title?: string;
  height?: number;
  /** Current playback time (used to draw a vertical "playhead" reference line). */
  currentTime?: number;
}

/**
 * Colorblind-safe AIMS palette + Okabe-Ito extensions.
 * Each line also uses a distinct dash pattern so that users with any form of
 * color-vision deficiency can still tell the five compartments apart.
 */
export const COMPARTMENT_COLORS = {
  Susceptible: "#00A9B5", // AIMS Teal
  Misinformed: "#F4A500", // AIMS Gold
  Truth: "#56B870",       // Bluish-green (Okabe-Ito)
  Inoculated: "#1A3668",  // AIMS Navy
  Resistant: "#D55E00",   // Vermillion (Okabe-Ito)
} as const;

const COMPARTMENT_DASH = {
  Susceptible: undefined,           // solid
  Misinformed: "6 4",               // dashed
  Truth: "2 3",                     // dotted
  Inoculated: "10 4 2 4",           // dash-dot
  Resistant: "12 6",                // long dash
} as const;

export default function SimulationChart({
  data,
  title = "NIDM Compartmental Model Trajectories",
  height = 400,
  currentTime,
}: SimulationChartProps) {
  const chartData = useMemo(() => {
    return data.map((point) => ({
      time: Number(point.time.toFixed(1)),
      Susceptible: Math.round(point.Susceptible * 1000) / 1000,
      Misinformed: Math.round(point.Misinformed * 1000) / 1000,
      Truth: Math.round(point.Truth * 1000) / 1000,
      Inoculated: Math.round(point.Inoculated * 1000) / 1000,
      Resistant: Math.round(point.Resistant * 1000) / 1000,
    }));
  }, [data]);

  return (
    <div className="glass-dark border border-border/50 rounded-lg p-6 glow-secondary">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold neon-text">{title}</h3>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse-dot" />
          <span>Live trajectory</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255, 255, 255, 0.08)"
            vertical={false}
          />
          <XAxis
            dataKey="time"
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: "12px" }}
            label={{
              value: "Time (days)",
              position: "insideBottom",
              offset: -2,
              fill: "rgba(255,255,255,0.5)",
              fontSize: 11,
            }}
          />
          <YAxis
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: "12px" }}
            label={{
              value: "Population fraction",
              angle: -90,
              position: "insideLeft",
              fill: "rgba(255,255,255,0.5)",
              fontSize: 11,
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(14, 26, 51, 0.95)",
              border: "1px solid rgba(0, 169, 181, 0.3)",
              borderRadius: "8px",
              boxShadow: "0 0 20px rgba(0, 169, 181, 0.25)",
            }}
            labelStyle={{ color: "rgba(255, 255, 255, 0.9)" }}
            itemStyle={{ color: "rgba(255, 255, 255, 0.85)" }}
          />
          <Legend wrapperStyle={{ paddingTop: "20px" }} iconType="line" />

          {currentTime !== undefined && (
            <ReferenceLine
              x={Number(currentTime.toFixed(1))}
              stroke="#F4A500"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: `t=${currentTime.toFixed(1)}`,
                position: "top",
                fill: "#F4A500",
                fontSize: 11,
              }}
            />
          )}

          {(Object.keys(COMPARTMENT_COLORS) as Array<keyof typeof COMPARTMENT_COLORS>).map(
            (key) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COMPARTMENT_COLORS[key]}
                strokeWidth={2.5}
                strokeDasharray={COMPARTMENT_DASH[key]}
                dot={false}
                isAnimationActive={true}
                animationDuration={800}
              />
            )
          )}
        </LineChart>
      </ResponsiveContainer>

      {/* Legend explanation with dash patterns visible */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6 text-xs">
        {(Object.keys(COMPARTMENT_COLORS) as Array<keyof typeof COMPARTMENT_COLORS>).map(
          (key) => (
            <div key={key} className="flex items-center gap-2">
              <svg width="24" height="6" className="flex-shrink-0">
                <line
                  x1="0"
                  y1="3"
                  x2="24"
                  y2="3"
                  stroke={COMPARTMENT_COLORS[key]}
                  strokeWidth="2.5"
                  strokeDasharray={COMPARTMENT_DASH[key]}
                />
              </svg>
              <span className="text-muted-foreground">{key}</span>
            </div>
          )
        )}
      </div>
    </div>
  );
}
