-- Answers researchers approved and chose to share (src/shared-answers.ts). Only the answer text is kept: no question,
-- evidence, workspace data or name. owner is a hash of a random per-computer secret, key a hash prefix of the access key.
CREATE TABLE IF NOT EXISTS shared_answers (
  id TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  key TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('answer', 'correction')),
  answer TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS shared_answers_updated ON shared_answers (updated_at, id);
CREATE INDEX IF NOT EXISTS shared_answers_key ON shared_answers (key, updated_at);
CREATE INDEX IF NOT EXISTS shared_answers_owner ON shared_answers (owner, deleted);
