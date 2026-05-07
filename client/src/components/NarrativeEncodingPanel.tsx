import React, { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2, Copy } from "lucide-react";
import type { ParsedNarrative } from "@/lib/narrativeParser";

interface NarrativeScore {
  E: number;
  C: number;
  tau: number;
  kappa: number;
}

interface Narrative {
  id: string;
  label: string;
  quote: string;
  scores: NarrativeScore;
  phi: number;
}

interface NarrativeEncodingPanelProps {
  onNarrativeAdd?: (narrative: ParsedNarrative) => void;
}

const WEIGHTS = {
  E: 0.3,
  C: 0.3,
  tau: 0.2,
  kappa: 0.2,
};

export default function NarrativeEncodingPanel({
  onNarrativeAdd,
}: NarrativeEncodingPanelProps) {
  const [narratives, setNarratives] = useState<Narrative[]>([]);
  const [label, setLabel] = useState("");
  const [quote, setQuote] = useState("");
  const [scores, setScores] = useState<NarrativeScore>({
    E: 0.5,
    C: 0.5,
    tau: 0.5,
    kappa: 0.5,
  });

  const computePhi = (s: NarrativeScore): number => {
    return Number(
      (WEIGHTS.E * s.E +
        WEIGHTS.C * s.C +
        WEIGHTS.tau * s.tau +
        WEIGHTS.kappa * s.kappa).toFixed(4)
    );
  };

  const phi = useMemo(() => computePhi(scores), [scores]);

  const handleScoreChange = (key: keyof NarrativeScore, value: number) => {
    setScores((prev) => ({
      ...prev,
      [key]: Math.max(0, Math.min(1, value)),
    }));
  };

  const handleAddNarrative = () => {
    if (!label.trim() || !quote.trim()) {
      alert("Please fill in all fields");
      return;
    }

    const newNarrative: Narrative = {
      id: Date.now().toString(),
      label,
      quote,
      scores,
      phi,
    };

    setNarratives((prev) => [...prev, newNarrative]);
    onNarrativeAdd?.({
      id: newNarrative.id,
      key: `manual-${newNarrative.id}`,
      label: newNarrative.label,
      type: "manual",
      quote: newNarrative.quote,
      E: newNarrative.scores.E,
      C: newNarrative.scores.C,
      tau: newNarrative.scores.tau,
      kappa: newNarrative.scores.kappa,
      phi: newNarrative.phi,
      targets: "all",
      source: "narrative",
      uploadedAt: Date.now(),
    });

    setLabel("");
    setQuote("");
    setScores({ E: 0.5, C: 0.5, tau: 0.5, kappa: 0.5 });
  };

  const handleDeleteNarrative = (id: string) => {
    setNarratives((prev) => prev.filter((n) => n.id !== id));
  };

  const handleCopyNarrative = (narrative: Narrative) => {
    const text = `${narrative.label}\n${narrative.quote}\nPhi = ${narrative.phi}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card className="glass-dark border-border/50 p-6 glow-primary">
        <h3 className="text-lg font-bold neon-text mb-6">Narrative Encoding</h3>

        <div className="space-y-4">
          {/* Label Input */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Narrative Label
            </label>
            <Input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g., Clean Cooking Health Benefits"
              className="bg-input border-border/50"
            />
          </div>

          {/* Quote Input */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Narrative Quote
            </label>
            <Textarea
              value={quote}
              onChange={(e) => setQuote(e.target.value)}
              placeholder="Enter the narrative text..."
              className="bg-input border-border/50 min-h-24"
            />
          </div>

          {/* Scoring Dimensions */}
          <div className="grid grid-cols-2 gap-4">
            {/* Emotional Salience (E) */}
            <div>
              <label className="block text-sm font-medium text-primary mb-2">
                Emotional Salience (E)
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scores.E}
                  onChange={(e) =>
                    handleScoreChange("E", parseFloat(e.target.value))
                  }
                  className="flex-1 h-2 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <span className="text-sm font-bold text-primary w-12 text-right">
                  {scores.E.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Cultural Resonance (C) */}
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">
                Cultural Resonance (C)
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scores.C}
                  onChange={(e) =>
                    handleScoreChange("C", parseFloat(e.target.value))
                  }
                  className="flex-1 h-2 bg-border rounded-lg appearance-none cursor-pointer accent-secondary"
                />
                <span className="text-sm font-bold text-secondary w-12 text-right">
                  {scores.C.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Trust Alignment (tau) */}
            <div>
              <label className="block text-sm font-medium text-accent mb-2">
                Trust Alignment (tau)
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scores.tau}
                  onChange={(e) =>
                    handleScoreChange("tau", parseFloat(e.target.value))
                  }
                  className="flex-1 h-2 bg-border rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <span className="text-sm font-bold text-accent w-12 text-right">
                  {scores.tau.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Narrative Arc Strength (kappa) */}
            <div>
              <label className="block text-sm font-medium text-chart-4 mb-2">
                Narrative Arc Strength (kappa)
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={scores.kappa}
                  onChange={(e) =>
                    handleScoreChange("kappa", parseFloat(e.target.value))
                  }
                  className="flex-1 h-2 bg-border rounded-lg appearance-none cursor-pointer accent-chart-4"
                />
                <span className="text-sm font-bold text-chart-4 w-12 text-right">
                  {scores.kappa.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Narrative Strength Display */}
          <div className="mt-6 p-4 bg-primary/10 border border-primary/30 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">
                  Composite Narrative Strength
                </p>
                <p className="text-3xl font-bold neon-text mt-2">Phi = {phi.toFixed(4)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground mb-2">
                  Weights: E(0.3) + C(0.3) + tau(0.2) + kappa(0.2)
                </p>
                <div className="text-sm space-y-1 text-muted-foreground">
                  <p>E: {(WEIGHTS.E * scores.E).toFixed(3)}</p>
                  <p>C: {(WEIGHTS.C * scores.C).toFixed(3)}</p>
                  <p>tau: {(WEIGHTS.tau * scores.tau).toFixed(3)}</p>
                  <p>kappa: {(WEIGHTS.kappa * scores.kappa).toFixed(3)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Add Button */}
          <Button
            type="button"
            onClick={handleAddNarrative}
            className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/80 hover:to-accent/80 text-background font-bold py-3 rounded-lg transition-all duration-200 glow-primary"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Narrative
          </Button>
        </div>
      </Card>

      {/* Narrative Library */}
      {narratives.length > 0 && (
        <div>
          <h3 className="text-lg font-bold neon-text mb-4">
            Narrative Library ({narratives.length})
          </h3>
          <div className="grid gap-4">
            {narratives.map((narrative) => (
              <Card
                key={narrative.id}
                className="glass-dark border-border/50 p-4 hover:border-primary/50 transition-all duration-200 animate-fade-in-up"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-bold text-foreground mb-2">
                      {narrative.label}
                    </h4>
                    <p className="text-sm text-muted-foreground mb-3 italic">
                      "{narrative.quote}"
                    </p>
                    <div className="grid grid-cols-4 gap-2 text-xs">
                      <div className="bg-primary/10 p-2 rounded">
                        <p className="text-muted-foreground">E</p>
                        <p className="font-bold text-primary">
                          {narrative.scores.E.toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-secondary/10 p-2 rounded">
                        <p className="text-muted-foreground">C</p>
                        <p className="font-bold text-secondary">
                          {narrative.scores.C.toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-accent/10 p-2 rounded">
                        <p className="text-muted-foreground">tau</p>
                        <p className="font-bold text-accent">
                          {narrative.scores.tau.toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-chart-4/10 p-2 rounded">
                        <p className="text-muted-foreground">kappa</p>
                        <p className="font-bold text-chart-4">
                          {narrative.scores.kappa.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 p-2 bg-background/50 rounded border border-primary/20">
                      <p className="text-xs text-muted-foreground">
                        Narrative Strength
                      </p>
                      <p className="text-lg font-bold text-primary">
                        Phi = {narrative.phi.toFixed(4)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => handleCopyNarrative(narrative)}
                      className="p-2 hover:bg-primary/20 rounded-lg transition-colors text-primary"
                      title="Copy narrative"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteNarrative(narrative.id)}
                      className="p-2 hover:bg-destructive/20 rounded-lg transition-colors text-destructive"
                      title="Delete narrative"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
