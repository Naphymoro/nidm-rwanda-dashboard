import React, { useEffect, useState } from "react";
import { TrendingDown, TrendingUp } from "lucide-react";

interface KPICardProps {
  label: string;
  value: number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: number;
  icon?: React.ReactNode;
  glowColor?: "primary" | "accent" | "secondary" | "chart-1" | "chart-2";
  animated?: boolean;
  precision?: number;
}

const COLOR_MAP = {
  primary: "var(--indigoL)",
  accent: "var(--violet)",
  secondary: "var(--verdant)",
  "chart-1": "var(--gold)",
  "chart-2": "var(--flame)",
};

export default function KPICard({
  label,
  value,
  unit = "",
  trend = "neutral",
  trendValue = 0,
  icon,
  glowColor = "primary",
  animated = true,
  precision = 2,
}: KPICardProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const accent = COLOR_MAP[glowColor];

  useEffect(() => {
    if (!animated) {
      setDisplayValue(value);
      return;
    }

    let current = 0;
    const increment = value / 30 || value;
    const interval = window.setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        window.clearInterval(interval);
      } else {
        setDisplayValue(current);
      }
    }, 24);

    return () => window.clearInterval(interval);
  }, [value, animated]);

  return (
    <article className="stat-card relative p-5" style={{ boxShadow: `0 18px 50px color-mix(in srgb, ${accent} 11%, transparent)` }}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <p className="stat-lbl">{label}</p>
        {icon ? (
          <div
            className="kpi-icon"
            style={{
              color: accent,
              background: `color-mix(in srgb, ${accent} 14%, transparent)`,
              border: `1px solid color-mix(in srgb, ${accent} 28%, transparent)`,
            }}
          >
            {icon}
          </div>
        ) : null}
      </div>

      <div className="flex items-end gap-2">
        <span className="stat-val" style={{ color: accent }}>
          {displayValue.toFixed(precision)}
        </span>
        {unit ? <span className="font-mono-data pb-1 text-xs text-[var(--t3)]">{unit}</span> : null}
      </div>

      {trend !== "neutral" && trendValue !== 0 ? (
        <div className="mt-3 flex items-center gap-1 text-xs">
          {trend === "up" ? (
            <TrendingUp className="h-4 w-4 text-[var(--verdant)]" />
          ) : (
            <TrendingDown className="h-4 w-4 text-[var(--flame)]" />
          )}
          <span className="font-mono-data font-semibold" style={{ color: trend === "up" ? "var(--verdant)" : "var(--flame)" }}>
            {trend === "up" ? "+" : ""}
            {trendValue.toFixed(1)}%
          </span>
          <span className="text-[var(--t3)]">vs last period</span>
        </div>
      ) : null}
    </article>
  );
}
