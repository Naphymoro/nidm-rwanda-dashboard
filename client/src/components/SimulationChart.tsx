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
  Susceptible: "var(--cS)",
  Misinformed: "var(--cM)",
  Truth: "var(--cT)",
  Inoculated: "var(--cI)",
  Resistant: "var(--cR)",
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
    <div className="nidm-card p-5">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-syne text-lg font-bold">{title}</h3>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="twin-pulse" />
          <span className="font-mono-data text-[var(--t3)]">Live trajectory</span>
        </div>
      </div>

      <div className="rounded-lg bg-[var(--deep)] p-3">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,.05)"
            vertical={false}
          />
          <XAxis
            dataKey="time"
            stroke="rgba(232,236,247,.35)"
            style={{ fontSize: "12px" }}
            label={{
              value: "Time (days)",
              position: "insideBottom",
              offset: -2,
              fill: "rgba(232,236,247,.38)",
              fontSize: 11,
            }}
          />
          <YAxis
            stroke="rgba(232,236,247,.35)"
            style={{ fontSize: "12px" }}
            label={{
              value: "Population fraction",
              angle: -90,
              position: "insideLeft",
              fill: "rgba(232,236,247,.38)",
              fontSize: 11,
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--card)",
              border: "1px solid var(--bdrV)",
              borderRadius: "8px",
            }}
            labelStyle={{ color: "var(--t1)" }}
            itemStyle={{ color: "var(--t2)" }}
          />
          <Legend wrapperStyle={{ paddingTop: "20px" }} iconType="line" />

          {currentTime !== undefined && (
            <ReferenceLine
              x={Number(currentTime.toFixed(1))}
              stroke="var(--gold)"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: `t=${currentTime.toFixed(1)}`,
                position: "top",
                fill: "var(--gold)",
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
      </div>

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
              <span className="font-mono-data text-[10px] text-[var(--t3)]">{key}</span>
            </div>
          )
        )}
      </div>
    </div>
  );
}
