-- risk_scored table schema
-- Stores all scored loan events from the streaming pipeline

CREATE TABLE IF NOT EXISTS risk_scored (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ DEFAULT NOW(),
  loan_id TEXT,
  purpose TEXT,
  term TEXT,
  loan_amnt DOUBLE PRECISION,
  annual_inc DOUBLE PRECISION,
  dti DOUBLE PRECISION,
  int_rate_pct DOUBLE PRECISION,
  revol_util_pct DOUBLE PRECISION,
  delinq_2yrs DOUBLE PRECISION,
  inq_last_6mths DOUBLE PRECISION,
  credit_history_years DOUBLE PRECISION,
  emp_length_yrs DOUBLE PRECISION,
  dti_band TEXT,
  util_band TEXT,
  rate_band TEXT,
  early_warning_flag INTEGER,
  risk_tier TEXT,
  reasons TEXT
);

CREATE INDEX IF NOT EXISTS idx_risk_scored_time ON risk_scored(event_time DESC);
CREATE INDEX IF NOT EXISTS idx_risk_scored_tier ON risk_scored(risk_tier);
