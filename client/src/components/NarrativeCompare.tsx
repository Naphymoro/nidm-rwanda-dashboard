import React, { useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import {
  Trophy,
  Equal,
  ArrowUp,
  ArrowDown,
  FileSpreadsheet,
  FileText,
  Sparkles,
  Download,
  Loader2,
} from "lucide-react";
import {
  ParsedNarrative,
  compareNarratives,
  DimensionDiff,
} from "@/lib/narrativeParser";
import { buildComparisonFilename, exportElementToPdf } from "@/lib/pdfExport";

interface NarrativeCompareProps {
  a: ParsedNarrative | null;
  b: ParsedNarrative | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const COLOR_A = "#00A9B5"; // AIMS Teal
const COLOR_B = "#F4A500"; // AIMS Gold
const COLOR_TIE = "#94A3B8"; // Slate

function WinnerBadge({
  winner,
  side,
}: {
  winner: "a" | "b" | "tie";
  side: "a" | "b";
}) {
  if (winner === "tie") return null;
  if (winner !== side) return null;
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-accent/20 text-accent border border-accent/40">
      <Trophy className="w-3 h-3" /> Winner
    </span>
  );
}

function DimensionRow({ diff }: { diff: DimensionDiff }) {
  const aPct = diff.a * 100;
  const bPct = diff.b * 100;
  const deltaAbs = Math.abs(diff.delta);
  const deltaPct = (deltaAbs * 100).toFixed(1);

  const arrow =
    diff.winner === "tie" ? (
      <Equal className="w-3 h-3 text-muted-foreground" />
    ) : diff.winner === "b" ? (
      <ArrowUp className="w-3 h-3" style={{ color: COLOR_B }} />
    ) : (
      <ArrowDown className="w-3 h-3" style={{ color: COLOR_A }} />
    );

  return (
    <div className="bg-background/40 rounded-md p-3 border border-border/40">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-foreground">
          {diff.label}
        </span>
        <div className="flex items-center gap-1 text-[11px] font-mono text-muted-foreground">
          {arrow}
          <span>Δ {deltaPct}%</span>
        </div>
      </div>

      {/* A bar */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[11px] font-mono w-12 text-right" style={{ color: COLOR_A }}>
          {diff.a.toFixed(2)}
        </span>
        <div className="flex-1 h-2 bg-background/60 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${aPct}%`,
              background: COLOR_A,
              boxShadow: diff.winner === "a" ? `0 0 8px ${COLOR_A}` : "none",
            }}
          />
        </div>
        <span className="text-[10px] uppercase tracking-wider w-4" style={{ color: COLOR_A }}>
          A
        </span>
      </div>

      {/* B bar */}
      <div className="flex items-center gap-2">
        <span className="text-[11px] font-mono w-12 text-right" style={{ color: COLOR_B }}>
          {diff.b.toFixed(2)}
        </span>
        <div className="flex-1 h-2 bg-background/60 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${bPct}%`,
              background: COLOR_B,
              boxShadow: diff.winner === "b" ? `0 0 8px ${COLOR_B}` : "none",
            }}
          />
        </div>
        <span className="text-[10px] uppercase tracking-wider w-4" style={{ color: COLOR_B }}>
          B
        </span>
      </div>
    </div>
  );
}

function NarrativeHeader({
  n,
  side,
  isWinner,
}: {
  n: ParsedNarrative;
  side: "a" | "b";
  isWinner: boolean;
}) {
  const color = side === "a" ? COLOR_A : COLOR_B;
  return (
    <div
      className="rounded-lg p-4 border-2 transition-all"
      style={{
        borderColor: color,
        background: `${color}11`,
        boxShadow: isWinner ? `0 0 20px ${color}55` : "none",
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span
            className="px-2 py-0.5 rounded-md text-xs font-bold"
            style={{ background: color, color: "#0E1A33" }}
          >
            {side.toUpperCase()}
          </span>
          {n.source === "csv" ? (
            <FileSpreadsheet className="w-4 h-4" style={{ color }} />
          ) : (
            <FileText className="w-4 h-4" style={{ color }} />
          )}
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-background/50 px-1.5 py-0.5 rounded border border-border/40">
            {n.type}
          </span>
        </div>
        {isWinner && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-accent/20 text-accent border border-accent/40">
            <Trophy className="w-3 h-3" /> Higher Φ
          </span>
        )}
      </div>
      <h3 className="text-sm font-bold text-foreground mb-1 line-clamp-2">
        {n.label}
      </h3>
      <p className="text-[11px] text-muted-foreground font-mono">{n.key}</p>
      {n.quote && (
        <p className="text-xs text-muted-foreground italic mt-2 line-clamp-3">
          “{n.quote}”
        </p>
      )}
      <div className="mt-3 pt-3 border-t border-border/30 flex items-baseline justify-between">
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
          Composite Φ
        </span>
        <span className="text-2xl font-bold font-mono" style={{ color }}>
          {n.phi.toFixed(3)}
        </span>
      </div>
      <div className="mt-1 text-[11px] text-muted-foreground">
        Targets: <span className="text-foreground">{n.targets}</span>
      </div>
    </div>
  );
}

export default function NarrativeCompare({
  a,
  b,
  open,
  onOpenChange,
}: NarrativeCompareProps) {
  const comparison = useMemo(() => {
    if (!a || !b) return null;
    return compareNarratives(a, b);
  }, [a, b]);

  const exportRef = useRef<HTMLDivElement | null>(null);
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (!a || !b || !exportRef.current || exporting) return;
    setExporting(true);
    const toastId = toast.loading("Rendering PDF...");
    try {
      const filename = buildComparisonFilename(a.label, b.label);
      await exportElementToPdf(exportRef.current, {
        filename,
        title: `NIDM Comparison: ${a.label} vs ${b.label}`,
        subject: "Side-by-side narrative comparison report",
      });
      toast.success("PDF downloaded", { id: toastId, description: filename });
    } catch (err) {
      console.error("PDF export failed", err);
      toast.error("PDF export failed", {
        id: toastId,
        description: err instanceof Error ? err.message : "Unknown error",
      });
    } finally {
      setExporting(false);
    }
  };

  const radarData = useMemo(() => {
    if (!a || !b) return [];
    return [
      { dimension: "E (Emotional)", A: a.E, B: b.E },
      { dimension: "C (Cultural)", A: a.C, B: b.C },
      { dimension: "τ (Trust)", A: a.tau, B: b.tau },
      { dimension: "κ (Arc)", A: a.kappa, B: b.kappa },
    ];
  }, [a, b]);

  if (!a || !b || !comparison) return null;

  const phiWinnerLabel =
    comparison.phiWinner === "tie"
      ? "Tie"
      : comparison.phiWinner === "a"
      ? "A wins"
      : "B wins";
  const phiWinnerColor =
    comparison.phiWinner === "tie"
      ? COLOR_TIE
      : comparison.phiWinner === "a"
      ? COLOR_A
      : COLOR_B;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto glass-dark border-border/60">
        <DialogHeader>
          <div className="flex items-start justify-between gap-3">
            <div>
              <DialogTitle className="flex items-center gap-2 text-xl neon-text">
                <Sparkles className="w-5 h-5 text-accent" />
                Side-by-Side Narrative Comparison
              </DialogTitle>
              <DialogDescription className="text-muted-foreground">
                Compare two narratives across the four NIDM scoring dimensions and the
                composite narrative-strength score Φ.
              </DialogDescription>
            </div>
            <Button
              size="sm"
              onClick={handleExport}
              disabled={exporting}
              className="bg-accent text-accent-foreground hover:bg-accent/90 font-semibold mt-1 shrink-0"
              data-export-ignore
              title="Download this comparison as a PDF"
            >
              {exporting ? (
                <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-1.5" />
              )}
              {exporting ? "Rendering..." : "Export PDF"}
            </Button>
          </div>
        </DialogHeader>

        <div ref={exportRef} className="space-y-4 p-1">
        {/* Verdict strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
          <div className="bg-background/40 rounded-md p-3 border border-border/40">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Overall Φ verdict
            </p>
            <p
              className="text-lg font-bold mt-1"
              style={{ color: phiWinnerColor }}
            >
              {phiWinnerLabel}
            </p>
          </div>
          <div className="bg-background/40 rounded-md p-3 border border-border/40">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Φ delta (B − A)
            </p>
            <p
              className="text-lg font-bold font-mono mt-1"
              style={{
                color:
                  comparison.phiDelta > 0
                    ? COLOR_B
                    : comparison.phiDelta < 0
                    ? COLOR_A
                    : COLOR_TIE,
              }}
            >
              {comparison.phiDelta > 0 ? "+" : ""}
              {comparison.phiDelta.toFixed(3)}
            </p>
          </div>
          <div className="bg-background/40 rounded-md p-3 border border-border/40">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Dimensions won
            </p>
            <p className="text-sm font-bold mt-1">
              <span style={{ color: COLOR_A }}>A {comparison.aWins}</span>
              <span className="text-muted-foreground mx-1">·</span>
              <span style={{ color: COLOR_B }}>B {comparison.bWins}</span>
              {comparison.ties > 0 && (
                <>
                  <span className="text-muted-foreground mx-1">·</span>
                  <span className="text-muted-foreground">
                    Ties {comparison.ties}
                  </span>
                </>
              )}
            </p>
          </div>
          <div className="bg-background/40 rounded-md p-3 border border-border/40">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Largest gap
            </p>
            <p className="text-sm font-bold mt-1 text-foreground">
              {comparison.largestGap.label.split(" ")[0]}{" "}
              <span className="font-mono text-xs text-muted-foreground">
                ({(Math.abs(comparison.largestGap.delta) * 100).toFixed(1)}%)
              </span>
            </p>
          </div>
        </div>

        {/* Side-by-side header cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <NarrativeHeader n={a} side="a" isWinner={comparison.phiWinner === "a"} />
          <NarrativeHeader n={b} side="b" isWinner={comparison.phiWinner === "b"} />
        </div>

        {/* Radar overlay */}
        <div className="mt-6 bg-background/30 rounded-lg p-4 border border-border/40">
          <h4 className="text-sm font-semibold text-foreground mb-3">
            Dimension overlay
          </h4>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData} outerRadius={95}>
              <PolarGrid stroke="rgba(255,255,255,0.12)" />
              <PolarAngleAxis
                dataKey="dimension"
                tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 1]}
                tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(14,26,51,0.95)",
                  border: "1px solid rgba(0,169,181,0.3)",
                  borderRadius: "8px",
                }}
              />
              <Legend wrapperStyle={{ paddingTop: 10, fontSize: 12 }} />
              <Radar
                name={`A · ${a.label}`}
                dataKey="A"
                stroke={COLOR_A}
                fill={COLOR_A}
                fillOpacity={0.25}
                strokeWidth={2}
                isAnimationActive
              />
              <Radar
                name={`B · ${b.label}`}
                dataKey="B"
                stroke={COLOR_B}
                fill={COLOR_B}
                fillOpacity={0.25}
                strokeWidth={2}
                isAnimationActive
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Per-dimension breakdown */}
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-foreground mb-3">
            Per-dimension breakdown
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {comparison.dimensionDiffs.map((diff) => (
              <DimensionRow key={diff.dimension} diff={diff} />
            ))}
          </div>
        </div>

        {/* Hidden but kept for accessibility / parity with side cards */}
        <div className="sr-only">
          <WinnerBadge winner={comparison.phiWinner} side="a" />
          <WinnerBadge winner={comparison.phiWinner} side="b" />
        </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
