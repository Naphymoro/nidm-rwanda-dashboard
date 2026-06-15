CREATE TABLE IF NOT EXISTS workspaces (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT,
  domain TEXT,
  description TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS narratives (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  route TEXT NOT NULL,
  title TEXT,
  body TEXT NOT NULL,
  country TEXT,
  admin1 TEXT,
  admin2 TEXT,
  admin3 TEXT,
  language TEXT,
  source_type TEXT,
  source_name TEXT,
  period TEXT,
  consent_level TEXT,
  visibility TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  evidence_hash TEXT NOT NULL,
  metadata_json TEXT,
  reviewer TEXT,
  review_decision TEXT,
  review_note TEXT,
  reviewed_at TEXT,
  committed_at TEXT,
  uncommitted_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE IF NOT EXISTS encodings (
  id TEXT PRIMARY KEY,
  narrative_id TEXT NOT NULL,
  mode TEXT NOT NULL,
  encoder TEXT NOT NULL,
  barrier_strength REAL NOT NULL,
  trust_signal REAL NOT NULL,
  misinformation_risk REAL NOT NULL,
  inoculation_opportunity REAL NOT NULL,
  social_influence REAL NOT NULL,
  adoption_stance TEXT NOT NULL,
  emotional_intensity REAL NOT NULL,
  credibility REAL NOT NULL,
  summary TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (narrative_id) REFERENCES narratives(id)
);

CREATE TABLE IF NOT EXISTS files (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  r2_key TEXT NOT NULL,
  filename TEXT NOT NULL,
  content_type TEXT,
  byte_size INTEGER,
  sha256 TEXT NOT NULL,
  route TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  action TEXT NOT NULL,
  actor TEXT,
  details_json TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_narratives_workspace_status ON narratives(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_narratives_route ON narratives(route);
CREATE INDEX IF NOT EXISTS idx_encodings_narrative ON encodings(narrative_id);
CREATE INDEX IF NOT EXISTS idx_files_workspace ON files(workspace_id);

