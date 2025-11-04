-- Hyperliquid TWAP Data Service Database Schema

-- Main table for TWAP status records
CREATE TABLE IF NOT EXISTS twap_status (
    twap_id            TEXT NOT NULL,
    wallet             TEXT NOT NULL,
    ts                 TIMESTAMPTZ NOT NULL,
    asset              TEXT,
    side               TEXT,
    size_requested     NUMERIC,
    size_executed      NUMERIC,
    notional_executed  NUMERIC,
    status             TEXT,
    duration_minutes   INTEGER,
    s3_object_key      TEXT NOT NULL,
    raw_payload        JSONB,
    inserted_at        TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (twap_id, wallet, ts)
);

-- ETL ingestion tracking table for idempotent processing
CREATE TABLE IF NOT EXISTS etl_s3_ingest_log (
    s3_object_key  TEXT PRIMARY KEY,
    last_modified  TIMESTAMPTZ NOT NULL,
    rows_ingested  INTEGER,
    error_text     TEXT,
    ingested_at    TIMESTAMPTZ DEFAULT now()
);

-- Index for wallet-based time range queries
CREATE INDEX IF NOT EXISTS twap_status_wallet_ts_idx ON twap_status (wallet, ts);

-- Index for TWAP ID lookups
CREATE INDEX IF NOT EXISTS twap_status_twap_id_idx ON twap_status (twap_id);

-- Optional: Index for asset filtering
CREATE INDEX IF NOT EXISTS twap_status_asset_idx ON twap_status (asset);
