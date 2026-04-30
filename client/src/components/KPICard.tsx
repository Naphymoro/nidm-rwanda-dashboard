import React, { useEffect, useState } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

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

  useEffect(() => {
    if (!animated) {
      setDisplayValue(value);
      return;
    }

    let current = 0;
    const increment = value / 30;
    const interval = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(interval);
      } else {
        setDisplayValue(current);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [value, animated]);

  const glowClasses = {
    primary: "glow-primary",
    accent: "glow-accent",
    secondary: "glow-secondary",
    "chart-1": "shadow-lg",
    "chart-2": "shadow-lg",
  };

  const textColorClasses = {
    primary: "text-primary",
    accent: "text-accent",
    secondary: "text-secondary",
    "chart-1": "text-chart-1",
    "chart-2": "text-chart-2",
  };

  return (
    <div
      className={`glass-dark border border-border/50 rounded-lg p-6 transition-all duration-300 hover:border-${glowColor}/50 animate-fade-in-up ${
        glowClasses[glowColor]
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
        </div>
        {icon && (
          <div className={`p-2 bg-${glowColor}/10 rounded-lg ${textColorClasses[glowColor]}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline gap-2">
          <span className={`text-4xl font-bold ${textColorClasses[glowColor]} animate-counter`}>
            {displayValue.toFixed(precision)}
          </span>
          {unit && <span className="text-lg text-muted-foreground">{unit}</span>}
        </div>

        {trend !== "neutral" && trendValue !== 0 && (
          <div className="flex items-center gap-1 text-sm">
            {trend === "up" ? (
              <>
                <TrendingUp className="w-4 h-4 text-chart-3" />
                <span className="text-chart-3 font-medium">
                  +{trendValue.toFixed(1)}%
                </span>
              </>
            ) : (
              <>
                <TrendingDown className="w-4 h-4 text-destructive" />
                <span className="text-destructive font-medium">
                  {trendValue.toFixed(1)}%
                </span>
              </>
            )}
            <span className="text-muted-foreground">vs last period</span>
          </div>
        )}
      </div>

      {/* Animated background pulse */}
      <div
        className="absolute inset-0 rounded-lg opacity-0 animate-pulse pointer-events-none"
        style={{
          background: `radial-gradient(circle, var(--color-${glowColor}), transparent)`,
          opacity: 0.05,
        }}
      />
    </div>
  );
}
