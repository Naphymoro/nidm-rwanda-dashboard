import React, { useEffect, useMemo, useRef, useState } from "react";
import { Play, Pause, RotateCcw, FastForward, SkipForward, SkipBack } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SimulationChart, { COMPARTMENT_COLORS } from "./SimulationChart";

interface SimulationDataPoint {
  time: number;
  Susceptible: number;
  Misinformed: number;
  Truth: number;
  Inoculated: number;
  Resistant: number;
}

interface SimulationPlayerProps {
  fullData: SimulationDataPoint[];
  title?: string;
}

const SPEED_OPTIONS = [0.5, 1, 2, 4];

/**
 * Animated playback controller for the NIDM compartmental simulation.
 * - Play / Pause / Reset
 * - Step forward / backward
 * - Variable playback speed
 * - Manual scrubbing through the timeline
 */
export default function SimulationPlayer({
  fullData,
  title = "NIDM Compartmental Model Trajectories",
}: SimulationPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(fullData.length - 1);
  const [speed, setSpeed] = useState(1);
  const intervalRef = useRef<number | null>(null);

  const maxIndex = fullData.length - 1;

  // Slice the visible portion of the trajectory based on the playhead.
  const visibleData = useMemo(
    () => fullData.slice(0, currentIndex + 1),
    [fullData, currentIndex]
  );

  const currentPoint = fullData[currentIndex];

  // Playback loop using setInterval, scaled by speed.
  useEffect(() => {
    if (!isPlaying) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const tickMs = 80 / speed;
    intervalRef.current = window.setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev >= maxIndex) {
          setIsPlaying(false);
          return maxIndex;
        }
        return prev + 1;
      });
    }, tickMs);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isPlaying, speed, maxIndex]);

  const handlePlayPause = () => setIsPlaying((p) => !p);

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentIndex(0);
  };

  const handleStepForward = () => {
    setCurrentIndex((prev) => Math.min(maxIndex, prev + 1));
  };

  const handleStepBack = () => {
    setCurrentIndex((prev) => Math.max(0, prev - 1));
  };

  const handleSkipToEnd = () => {
    setIsPlaying(false);
    setCurrentIndex(maxIndex);
  };

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentIndex(Number(e.target.value));
  };

  const progressPct = (currentIndex / maxIndex) * 100;

  return (
    <div className="space-y-4">
      <SimulationChart
        data={visibleData}
        title={title}
        currentTime={currentPoint?.time}
      />

      {/* Playback Control Bar */}
      <Card className="nidm-card p-5">
        <div className="flex flex-col gap-4">
          {/* Top Row: transport buttons + speed */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleReset}
                className="border-[var(--bdr)] bg-[var(--deep)] text-[var(--t2)] hover:border-[var(--bdrV)] hover:bg-[var(--well)]"
                title="Reset to start"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleStepBack}
                disabled={currentIndex === 0}
                className="border-[var(--bdr)] bg-[var(--deep)] text-[var(--t2)] hover:border-[var(--bdrV)] hover:bg-[var(--well)]"
                title="Step back"
              >
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button
                type="button"
                size="lg"
                onClick={handlePlayPause}
                className="border-[rgba(32,201,151,.35)] bg-[rgba(32,201,151,.14)] px-6 text-[var(--verdant)] hover:bg-[rgba(32,201,151,.2)]"
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? (
                  <>
                    <Pause className="w-5 h-5 mr-2" /> Pause
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" /> Play
                  </>
                )}
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleStepForward}
                disabled={currentIndex === maxIndex}
                className="border-[var(--bdr)] bg-[var(--deep)] text-[var(--t2)] hover:border-[var(--bdrV)] hover:bg-[var(--well)]"
                title="Step forward"
              >
                <SkipForward className="w-4 h-4" />
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleSkipToEnd}
                className="border-[var(--bdr)] bg-[var(--deep)] text-[var(--t2)] hover:border-[var(--bdrV)] hover:bg-[var(--well)]"
                title="Skip to end"
              >
                <FastForward className="w-4 h-4" />
              </Button>
            </div>

            {/* Speed selector */}
            <div className="flex items-center gap-2">
              <span className="font-mono-data text-xs text-[var(--t3)]">Speed</span>
              <div className="flex rounded-md border border-[var(--bdr)] bg-[var(--deep)] p-1">
                {SPEED_OPTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSpeed(s)}
                    className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                      speed === s
                        ? "bg-[var(--card)] text-[var(--indigoL)]"
                        : "text-[var(--t3)] hover:text-[var(--t1)]"
                    }`}
                  >
                    {s}x
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Scrub Bar */}
          <div className="flex items-center gap-3">
            <span className="font-mono-data w-16 text-xs text-[var(--t3)]">
              t = {currentPoint?.time.toFixed(1) ?? "0.0"}
            </span>
            <div className="flex-1 relative">
              <input
                type="range"
                min={0}
                max={maxIndex}
                value={currentIndex}
                onChange={handleScrub}
                style={{ "--pct": `${progressPct}%`, "--indigoL": "var(--verdant)" } as React.CSSProperties}
              />
            </div>
            <span className="font-mono-data w-20 text-right text-xs text-[var(--t3)]">
              {currentIndex} / {maxIndex}
            </span>
          </div>

          {/* Live compartment readouts */}
          {currentPoint && (
            <div className="grid grid-cols-2 gap-2 border-t border-[var(--bdr)] pt-2 md:grid-cols-5">
              {(Object.keys(COMPARTMENT_COLORS) as Array<keyof typeof COMPARTMENT_COLORS>).map(
                (key) => (
                  <div
                    key={key}
                    className="rounded-md border border-[var(--bdr)] bg-[var(--deep)] p-2"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: COMPARTMENT_COLORS[key] }}
                      />
                      <span className="font-mono-data text-[10px] uppercase tracking-wider text-[var(--t3)]">
                        {key}
                      </span>
                    </div>
                    <p
                      className="font-mono-data text-lg font-bold"
                      style={{ color: COMPARTMENT_COLORS[key] }}
                    >
                      {(currentPoint[key] * 100).toFixed(1)}%
                    </p>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
