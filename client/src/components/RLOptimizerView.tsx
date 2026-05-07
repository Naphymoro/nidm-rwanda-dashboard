import React, { CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import {
  Line,
  LineChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Bot, BrainCircuit, Play, RotateCcw, Trophy } from "lucide-react";
import KPICard from "./KPICard";
import { useNIDMMode } from "./DashboardLayout";

type RewardPoint = {
  episode: number;
  reward: number;
  movingAverage: number;
  truthFraction: number;
};

type Config = {
  episodes: number;
  alpha: number;
  gamma: number;
  epsilon: number;
};

const ACTIONS = [
  { name: "Trust radio", truth: 0.16, inoculation: 0.08, cost: 0.09 },
  { name: "Community champions", truth: 0.13, inoculation: 0.15, cost: 0.12 },
  { name: "Myth prebunking", truth: 0.08, inoculation: 0.24, cost: 0.14 },
  { name: "Subsidy narrative", truth: 0.2, inoculation: 0.06, cost: 0.16 },
];

function clamp(value: number, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function movingAverage(points: RewardPoint[], nextReward: number, window = 20) {
  const recent = [...points.slice(-(window - 1)).map((point) => point.reward), nextReward];
  return recent.reduce((sum, value) => sum + value, 0) / recent.length;
}

function chooseAction(q: number[], epsilon: number) {
  if (Math.random() < epsilon) return Math.floor(Math.random() * ACTIONS.length);
  const best = Math.max(...q);
  return q.findIndex((value) => value === best);
}

function rewardFor(actionIndex: number, episode: number) {
  const action = ACTIONS[actionIndex];
  const learningLift = 1 - Math.exp(-episode / 60);
  const truthFraction = clamp(0.32 + action.truth * 1.8 + learningLift * 0.22 + (Math.random() - 0.5) * 0.08);
  const inoculation = clamp(0.22 + action.inoculation * 1.4 + learningLift * 0.12);
  const misinformationPenalty = clamp(0.34 - action.inoculation * 0.75 - learningLift * 0.08, 0.04, 0.34);
  const reward = clamp(truthFraction * 0.52 + inoculation * 0.34 - misinformationPenalty * 0.22 - action.cost * 0.18);

  return { reward, truthFraction };
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: React.ReactNode;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}) {
  const pct = ((value - min) / (max - min)) * 100;

  return (
    <label className="block">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono-data text-xs text-[var(--t2)]">{label}</span>
        <span className="font-mono-data text-xs text-[var(--indigoL)]">{value.toFixed(step < 0.01 ? 3 : 2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        style={{ "--pct": `${pct}%` } as CSSProperties}
      />
    </label>
  );
}

export default function RLOptimizerView() {
  const { mode } = useNIDMMode();
  const [config, setConfig] = useState<Config>({
    episodes: 180,
    alpha: 0.18,
    gamma: 0.86,
    epsilon: 0.22,
  });
  const [isTraining, setIsTraining] = useState(false);
  const [episode, setEpisode] = useState(0);
  const [points, setPoints] = useState<RewardPoint[]>([]);
  const [qValues, setQValues] = useState<number[]>(ACTIONS.map(() => 0.25));
  const timeoutRef = useRef<number | null>(null);

  const best = useMemo(() => {
    const bestPoint = points.reduce<RewardPoint | null>((current, point) => (!current || point.reward > current.reward ? point : current), null);
    const bestActionIndex = qValues.findIndex((value) => value === Math.max(...qValues));

    return {
      point: bestPoint,
      action: ACTIONS[Math.max(0, bestActionIndex)],
      truthFraction: bestPoint?.truthFraction ?? 0,
      reward: bestPoint?.reward ?? 0,
    };
  }, [points, qValues]);

  useEffect(() => {
    if (!isTraining) return;

    if (episode >= config.episodes) {
      setIsTraining(false);
      return;
    }

    timeoutRef.current = window.setTimeout(() => {
      setQValues((currentQ) => {
        let q = [...currentQ];
        const batchPoints: RewardPoint[] = [];
        let nextEpisode = episode;

        for (let i = 0; i < 8 && nextEpisode < config.episodes; i += 1) {
          nextEpisode += 1;
          const actionIndex = chooseAction(q, config.epsilon);
          const { reward, truthFraction } = rewardFor(actionIndex, nextEpisode);
          const oldValue = q[actionIndex];
          const future = Math.max(...q);
          q[actionIndex] = oldValue + config.alpha * (reward + config.gamma * future - oldValue);
          batchPoints.push({
            episode: nextEpisode,
            reward,
            truthFraction,
            movingAverage: movingAverage([...points, ...batchPoints], reward),
          });
        }

        setPoints((current) => [...current, ...batchPoints]);
        setEpisode(nextEpisode);
        return q;
      });
    }, 80);

    return () => {
      if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    };
  }, [config, episode, isTraining, points]);

  function startTraining() {
    setEpisode(0);
    setPoints([]);
    setQValues(ACTIONS.map(() => 0.25));
    setIsTraining(true);
  }

  function resetTraining() {
    setIsTraining(false);
    setEpisode(0);
    setPoints([]);
    setQValues(ACTIONS.map(() => 0.25));
  }

  const explainer = {
    novice: "The optimizer tests communication choices over many episodes and learns which action most reliably increases truth adoption.",
    policy: "Use the reward curve to compare intervention packages by adoption gain, inoculation coverage, and cost pressure.",
    expert: "This panel uses a compact epsilon-greedy Q-learning loop with configurable alpha, gamma, epsilon, and reward shaping.",
  }[mode];

  return (
    <div className="animate-page-in space-y-6">
      <section className={`explainer ${mode === "expert" ? "science" : mode}`}>
        {explainer}
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <KPICard
          label="Best T fraction"
          value={best.truthFraction * 100}
          unit="%"
          trend="up"
          trendValue={best.truthFraction > 0 ? 6.8 : 0}
          icon={<Trophy className="h-5 w-5" />}
          glowColor="secondary"
          precision={1}
        />
        <KPICard
          label="Best reward"
          value={best.reward}
          trend="up"
          trendValue={best.reward > 0 ? 4.2 : 0}
          icon={<BrainCircuit className="h-5 w-5" />}
          glowColor="primary"
          precision={3}
        />
        <KPICard
          label="Episodes completed"
          value={episode}
          unit=""
          trend="neutral"
          icon={<Bot className="h-5 w-5" />}
          glowColor="accent"
          animated={false}
          precision={0}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <section className="nidm-card p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="font-syne text-lg font-bold">RL configuration</h2>
              <p className="mt-1 text-xs text-[var(--t3)]">Epsilon-greedy policy search</p>
            </div>
            <div className="twin-pulse" />
          </div>

          <div className="space-y-5">
            <Slider
              label="episodes"
              value={config.episodes}
              min={40}
              max={400}
              step={10}
              onChange={(value) => setConfig((current) => ({ ...current, episodes: value }))}
            />
            <Slider
              label={<><span>&alpha;</span> learning rate</>}
              value={config.alpha}
              min={0.02}
              max={0.6}
              step={0.01}
              onChange={(value) => setConfig((current) => ({ ...current, alpha: value }))}
            />
            <Slider
              label={<><span>&gamma;</span> discount</>}
              value={config.gamma}
              min={0.2}
              max={0.99}
              step={0.01}
              onChange={(value) => setConfig((current) => ({ ...current, gamma: value }))}
            />
            <Slider
              label={<><span>&epsilon;</span> greedy</>}
              value={config.epsilon}
              min={0}
              max={0.8}
              step={0.01}
              onChange={(value) => setConfig((current) => ({ ...current, epsilon: value }))}
            />
          </div>

          <div className="mt-6 flex gap-2">
            <button
              type="button"
              onClick={startTraining}
              disabled={isTraining}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-[rgba(32,201,151,.35)] bg-[rgba(32,201,151,.13)] px-3 py-2 text-sm font-semibold text-[var(--verdant)]"
            >
              <Play className="h-4 w-4" />
              Train
            </button>
            <button
              type="button"
              onClick={resetTraining}
              className="flex items-center justify-center rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2 text-[var(--t2)]"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-5 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3">
            <p className="font-mono-data text-[10px] uppercase tracking-[1.4px] text-[var(--t4)]">Best policy</p>
            <p className="mt-2 font-syne text-lg font-bold text-[var(--t1)]">{best.action.name}</p>
            <p className="mt-1 text-xs leading-5 text-[var(--t3)]">
              Current policy emphasizes {best.action.name.toLowerCase()} with a Q-value of {Math.max(...qValues).toFixed(3)}.
            </p>
          </div>
        </section>

        <section className="nidm-card p-5">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="font-syne text-lg font-bold">Episode rewards</h2>
            <span className="page-badge border border-[rgba(116,143,252,.28)] bg-[rgba(116,143,252,.08)] text-[var(--indigoL)]">
              {isTraining ? "training" : "ready"}
            </span>
          </div>

          <div className="rounded-lg bg-[var(--deep)] p-3">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={points} margin={{ top: 10, right: 18, left: 0, bottom: 4 }}>
                <CartesianGrid stroke="rgba(255,255,255,.05)" vertical={false} />
                <XAxis dataKey="episode" />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(value: unknown) => Number(value).toFixed(3)} />
                <Line type="monotone" dataKey="reward" stroke="var(--verdant)" strokeWidth={2.5} dot={false} name="Reward" />
                <Line type="monotone" dataKey="movingAverage" stroke="var(--gold)" strokeWidth={2} dot={false} name="20-episode moving average" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-5 max-h-72 space-y-2 overflow-auto pr-1">
            {[...points].slice(-28).reverse().map((point) => (
              <div key={point.episode} className={`rl-episode ${point.reward === best.reward ? "best" : ""}`}>
                <span className="font-mono-data w-14 text-xs text-[var(--t3)]">#{point.episode}</span>
                <div className="rl-bar-track">
                  <div className="rl-bar-fill" style={{ width: `${point.reward * 100}%` }} />
                </div>
                <span className="font-mono-data w-16 text-right text-xs text-[var(--t2)]">{point.reward.toFixed(3)}</span>
              </div>
            ))}
            {!points.length ? (
              <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4 text-sm text-[var(--t3)]">
                Run training to populate the episode feed.
              </div>
            ) : null}
          </div>
        </section>
      </div>
    </div>
  );
}
