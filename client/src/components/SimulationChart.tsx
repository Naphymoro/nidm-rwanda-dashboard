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
}

export default function SimulationChart({
  data,
  title = "NIDM Compartmental Model Trajectories",
  height = 400,
}: SimulationChartProps) {
  const chartData = useMemo(() => {
    return data.map((point) => ({
      time: point.time.toFixed(1),
      Susceptible: Math.round(point.Susceptible * 100) / 100,
      Misinformed: Math.round(point.Misinformed * 100) / 100,
      Truth: Math.round(point.Truth * 100) / 100,
      Inoculated: Math.round(point.Inoculated * 100) / 100,
      Resistant: Math.round(point.Resistant * 100) / 100,
    }));
  }, [data]);

  const colors = {
    Susceptible: "rgb(74, 144, 217)",      // Blue
    Misinformed: "rgb(232, 82, 58)",       // Red-orange
    Truth: "rgb(46, 204, 113)",            // Green
    Inoculated: "rgb(243, 156, 18)",       // Gold
    Resistant: "rgb(155, 89, 182)",        // Purple
  };

  return (
    <div className="glass-dark border border-border/50 rounded-lg p-6 glow-secondary">
      <h3 className="text-lg font-bold neon-text mb-6">{title}</h3>

      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <defs>
            {/* Gradient definitions for each line */}
            <linearGradient id="grad-susceptible" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.Susceptible} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.Susceptible} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="grad-misinformed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.Misinformed} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.Misinformed} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="grad-truth" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.Truth} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.Truth} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="grad-inoculated" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.Inoculated} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.Inoculated} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="grad-resistant" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors.Resistant} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.Resistant} stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255, 255, 255, 0.1)"
            vertical={false}
          />
          <XAxis
            dataKey="time"
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: "12px" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(13, 13, 26, 0.95)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              boxShadow: "0 0 20px rgba(0, 255, 200, 0.2)",
            }}
            labelStyle={{ color: "rgba(255, 255, 255, 0.9)" }}
          />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            iconType="line"
          />

          <Line
            type="monotone"
            dataKey="Susceptible"
            stroke={colors.Susceptible}
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
          <Line
            type="monotone"
            dataKey="Misinformed"
            stroke={colors.Misinformed}
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
          <Line
            type="monotone"
            dataKey="Truth"
            stroke={colors.Truth}
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
          <Line
            type="monotone"
            dataKey="Inoculated"
            stroke={colors.Inoculated}
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
          <Line
            type="monotone"
            dataKey="Resistant"
            stroke={colors.Resistant}
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={true}
            animationDuration={1000}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend explanation */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6 text-xs">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors.Susceptible }}
          />
          <span className="text-muted-foreground">Susceptible</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors.Misinformed }}
          />
          <span className="text-muted-foreground">Misinformed</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors.Truth }}
          />
          <span className="text-muted-foreground">Truth</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors.Inoculated }}
          />
          <span className="text-muted-foreground">Inoculated</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: colors.Resistant }}
          />
          <span className="text-muted-foreground">Resistant</span>
        </div>
      </div>
    </div>
  );
}
