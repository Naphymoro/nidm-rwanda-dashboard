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
      <Card className="glass-dark border-border/50 p-5">
        <div className="flex flex-col gap-4">
          {/* Top Row: transport buttons + speed */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleReset}
                className="bg-background/40 border-border/60 hover:bg-primary/10 hover:border-primary"
                title="Reset to start"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleStepBack}
                disabled={currentIndex === 0}
                className="bg-background/40 border-border/60 hover:bg-primary/10 hover:border-primary"
                title="Step back"
              >
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button
                size="lg"
                onClick={handlePlayPause}
                className="bg-primary text-primary-foreground hover:bg-primary/90 glow-primary px-6"
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
                size="sm"
                variant="outline"
                onClick={handleStepForward}
                disabled={currentIndex === maxIndex}
                className="bg-background/40 border-border/60 hover:bg-primary/10 hover:border-primary"
                title="Step forward"
              >
                <SkipForward className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleSkipToEnd}
                className="bg-background/40 border-border/60 hover:bg-accent/10 hover:border-accent"
                title="Skip to end"
              >
                <FastForward className="w-4 h-4" />
              </Button>
            </div>

            {/* Speed selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Speed</span>
              <div className="flex bg-background/40 border border-border/60 rounded-md p-1">
                {SPEED_OPTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => setSpeed(s)}
                    className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                      speed === s
                        ? "bg-primary text-primary-foreground glow-primary"
                        : "text-muted-foreground hover:text-foreground"
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
            <span className="text-xs text-muted-foreground font-mono w-16">
              t = {currentPoint?.time.toFixed(1) ?? "0.0"}
            </span>
            <div className="flex-1 relative">
              <input
                type="range"
                min={0}
                max={maxIndex}
                value={currentIndex}
                onChange={handleScrub}
                className="w-full h-2 bg-background/60 rounded-lg appearance-none cursor-pointer accent-primary"
                style={{
                  background: `linear-gradient(to right, #00A9B5 0%, #00A9B5 ${progressPct}%, rgba(255,255,255,0.1) ${progressPct}%, rgba(255,255,255,0.1) 100%)`,
                }}
              />
            </div>
            <span className="text-xs text-muted-foreground font-mono w-20 text-right">
              {currentIndex} / {maxIndex}
            </span>
          </div>

          {/* Live compartment readouts */}
          {currentPoint && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 pt-2 border-t border-border/40">
              {(Object.keys(COMPARTMENT_COLORS) as Array<keyof typeof COMPARTMENT_COLORS>).map(
                (key) => (
                  <div
                    key={key}
                    className="bg-background/30 rounded-md p-2 border border-border/40"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: COMPARTMENT_COLORS[key] }}
                      />
                      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                        {key}
                      </span>
                    </div>
                    <p
                      className="text-lg font-bold font-mono"
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
