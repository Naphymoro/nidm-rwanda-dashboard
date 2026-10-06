-- The research assistant on Workers AI (src/ai.ts): Neurons used per UTC day, for the daily cap, and messages per
-- visitor per day. A visitor is a hash of their IP address and the day, so it cannot be followed from one day to the next.
CREATE TABLE IF NOT EXISTS ai_usage (
  day TEXT PRIMARY KEY,
  requests INTEGER NOT NULL DEFAULT 0,
  neurons REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ai_visitors (
  day TEXT NOT NULL,
  visitor TEXT NOT NULL,
  messages INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, visitor)
);
