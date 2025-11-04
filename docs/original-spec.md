# Hyperliquid TWAP Data Pipeline — Technical Spec

## 1. Overview
This repository ingests Hyperliquid TWAP data from a requester-pays S3 bucket (e.g. `artemis-hyperliquid-data`), normalizes and stores it in PostgreSQL, and exposes a FastAPI REST API to query TWAPs by wallet and time range, grouped by `twap_id`. The system is:

- **Incremental** (processes only new S3 objects)
- **Idempotent** (safe to re-run)
- **Open-source friendly** (MIT, dockerized, sample data)
- **Consumer-oriented** (stable JSON shape for tax platforms like Awaken)

Repo structure:

```text
hyperliquid-twap/
├─ src/
│  ├─ etl/
│  ├─ api/
│  └─ db/
├─ tests/
├─ docker-compose.yml
├─ .env.example
├─ README.md
└─ LICENSE
```

---

## 2. Requirements

- **Language**: Python 3.11+ (3.12 OK)
- **DB**: PostgreSQL 14+  
- **S3 Access**: AWS credentials or public requester-pays support
- **Containerization**: Docker / Docker Compose
- **OS**: Linux-based (for cron), but dev should run on Mac/Win

---

## 3. Configuration

All runtime configuration must come from environment variables:

```env
AWS_REGION=us-east-1
AWS_S3_BUCKET=artemis-hyperliquid-data
AWS_S3_PREFIX=raw/twap_statuses/
AWS_REQUEST_PAYER=requester

DATABASE_URL=postgresql+psycopg://user:pass@db:5432/hyperliquid

API_HOST=0.0.0.0
API_PORT=8000
```

Notes:

- `AWS_REQUEST_PAYER` **must** be used on every S3 call.
- Prefix must be configurable because the upstream may change foldering.

---

## 4. Database Design

### 4.1 Core Table

```sql
CREATE TABLE twap_status (
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
```

**Purpose / mapping:**

- `twap_id` ← parquet `twap_id`
- `wallet` ← parquet `state_user`
- `ts` ← parquet `state_timestamp` (normalized to UTC)
- `asset` ← `state_coin`
- `side` ← `state_side`
- `size_requested` ← `state_sz`
- `size_executed` ← `state_executedSz`
- `notional_executed` ← `state_executedNtl`
- `status` ← `status`
- `duration_minutes` ← `state_minutes`
- `raw_payload` ← entire parquet row (forward-compatible)

### 4.2 Ingest Log Table

```sql
CREATE TABLE etl_s3_ingest_log (
    s3_object_key  TEXT PRIMARY KEY,
    last_modified  TIMESTAMPTZ NOT NULL,
    rows_ingested  INTEGER,
    error_text     TEXT,
    ingested_at    TIMESTAMPTZ DEFAULT now()
);
```

Used to guarantee **incremental** + **idempotent** ingestion. If an object key is present, skip it on the next run unless we explicitly reprocess.

### 4.3 Indexes

```sql
CREATE INDEX twap_status_wallet_ts_idx ON twap_status (wallet, ts);
CREATE INDEX twap_status_twap_id_idx ON twap_status (twap_id);
```

These directly support API queries.

---

## 5. ETL Component

### 5.1 Responsibilities

1. **List** all S3 objects under `AWS_S3_PREFIX`.
2. **Skip** objects already in `etl_s3_ingest_log`.
3. **Download** each new object using `RequestPayer='requester'`.
4. **Parse** parquet with `pyarrow`/`pandas`.
5. **Normalize** column names → internal schema.
6. **Bulk insert** into Postgres with `ON CONFLICT DO NOTHING`.
7. **Record** result in `etl_s3_ingest_log`.

### 5.2 S3 Access

- Use `boto3` to list and download.
- Listing:
  ```python
  s3.list_objects_v2(
      Bucket=bucket,
      Prefix=prefix,
      RequestPayer="requester"
  )
  ```
- Download:
  ```python
  s3.get_object(
      Bucket=bucket,
      Key=key,
      RequestPayer="requester"
  )
  ```

### 5.3 Parsing

- Prefer `pyarrow.parquet.read_table()` → `to_pandas()` for simplicity.
- For each row, build a dict following DB schema.
- Convert timestamps to UTC (assume input is UTC or naïve → localize to UTC).

### 5.4 Loading

- Use SQLAlchemy Core or async engine.
- Insert in batches of 500–1000 rows.
- Use:
  ```sql
  INSERT INTO twap_status (...) VALUES (...)
  ON CONFLICT (twap_id, wallet, ts) DO NOTHING;
  ```

### 5.5 CLI Interface

The ETL must support:

- `--incremental` (default): process all new S3 objects
- `--since <ISO>`: process objects whose `LastModified` ≥ date
- `--object-key <key>`: process a single object (debug)
- `--local-file <path>`: process local parquet (for tests/CI)

Example:

```bash
python -m src.etl.run --incremental
python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

---

## 6. Scheduling

Primary recommendation: **cron on a Linux VM**.

Example crontab:

```cron
30 0 * * * cd /srv/hyperliquid-twap && /usr/bin/env bash -c 'source venv/bin/activate && python -m src.etl.run --incremental >> logs/etl.log 2>&1'
```

Notes:

- Run at **00:30 UTC** to give upstream time to publish.
- Log to file.
- ETL is idempotent, so a second daily run is harmless.

---

## 7. API Component (FastAPI)

### 7.1 App Setup

- Framework: **FastAPI**
- Server: **uvicorn**
- DB: async engine (e.g. `asyncpg` via SQLAlchemy)
- Docs: auto-exposed at `/docs` and `/openapi.json`

### 7.2 Endpoints

#### 1. `GET /api/v1/twaps`

**Query params:**

- `wallet` (required, string)
- `start` (required, ISO8601)
- `end` (required, ISO8601)
- `asset` (optional, string)
- `latest_per_twap` (optional, bool, default `true`)
- `limit` (optional, int, default `500`)

**Behavior:**

1. Fetch rows matching `wallet` and `ts BETWEEN start AND end`.
2. If `asset` provided, filter by asset.
3. Group by `twap_id`.
4. If `latest_per_twap=true`, pick the row with max `ts` per `twap_id`.

**Response shape:**

```json
{
  "wallet": "0xabc...",
  "start": "2025-11-01T00:00:00Z",
  "end": "2025-11-04T00:00:00Z",
  "twaps": [
    {
      "twap_id": "123456",
      "asset": "SOL",
      "side": "B",
      "status": "activated",
      "duration_minutes": 30,
      "latest_ts": "2025-11-03T12:00:00Z",
      "executed": {
        "size": "10.5",
        "notional": "950.25"
      },
      "raw": {
        "...": "original parquet row"
      }
    }
  ]
}
```

#### 2. `GET /api/v1/twaps/{twap_id}`

Returns **all** rows for that TWAP ID.

```json
{
  "twap_id": "123456",
  "rows": [
    {
      "wallet": "0xabc...",
      "ts": "2025-11-03T12:00:00Z",
      "status": "activated",
      "raw": { }
    }
  ]
}
```

#### 3. `GET /healthz`

Returns DB connectivity + last ingested S3 object from `etl_s3_ingest_log`.

---

## 8. Open Source Packaging

1. **License**: MIT in root.
2. **README** must include:
   - Introduction
   - Prereqs
   - Quick start (docker compose up Postgres, run migrations, run ETL on sample, start API)
   - Example curl requests
   - Notes on requester-pays S3 cost
3. **.env.example** with all variables.
4. **docker-compose.yml** with:
   - `postgres` service
   - optional `api` service
5. **Tests**: `pytest` with a local sample parquet.
6. **GitHub Actions**:
   - run `black`/`ruff`
   - run `pytest`
   - run ETL on sample parquet

---

## 9. Prompt to Hand to Another Agent

You can provide the following prompt to another agent to build this repo end-to-end:

> You are an expert Python data engineer and API developer. Your task is to implement, from scratch, the repository described below **exactly as specified**. Do not change the data model or API contract unless it is obviously impossible; prefer to add small compatibility helpers instead. The final result must run locally with Docker and expose a FastAPI app that serves data from Postgres populated by an ETL that pulls parquet files from a requester-pays S3 bucket.
> 
> **Goals:**
> 1. ETL: S3 (requester-pays) → parse parquet → normalize → Postgres.
> 2. Incremental + idempotent ingestion using an `etl_s3_ingest_log` table.
> 3. API: FastAPI endpoints to query TWAPs by wallet + time; group by `twap_id`; and fetch by `twap_id`.
> 4. Open-source ready: MIT license, README, .env.example, docker-compose, tests.
> 
> **Implement the repo with this structure:**
> ```text
> hyperliquid-twap/
> ├─ src/
> │  ├─ etl/
> │  ├─ api/
> │  └─ db/
> ├─ tests/
> ├─ docker-compose.yml
> ├─ .env.example
> ├─ README.md
> └─ LICENSE
> ```
> 
> **Database schema (must create on startup):**
> ```sql
> CREATE TABLE twap_status (
>     twap_id            TEXT NOT NULL,
>     wallet             TEXT NOT NULL,
>     ts                 TIMESTAMPTZ NOT NULL,
>     asset              TEXT,
>     side               TEXT,
>     size_requested     NUMERIC,
>     size_executed      NUMERIC,
>     notional_executed  NUMERIC,
>     status             TEXT,
>     duration_minutes   INTEGER,
>     s3_object_key      TEXT NOT NULL,
>     raw_payload        JSONB,
>     inserted_at        TIMESTAMPTZ DEFAULT now(),
>     PRIMARY KEY (twap_id, wallet, ts)
> );
> 
> CREATE TABLE etl_s3_ingest_log (
>     s3_object_key  TEXT PRIMARY KEY,
>     last_modified  TIMESTAMPTZ NOT NULL,
>     rows_ingested  INTEGER,
>     error_text     TEXT,
>     ingested_at    TIMESTAMPTZ DEFAULT now()
> );
> 
> CREATE INDEX twap_status_wallet_ts_idx ON twap_status (wallet, ts);
> CREATE INDEX twap_status_twap_id_idx ON twap_status (twap_id);
> ```
> 
> **ETL requirements:**
> - Use `boto3` to list and download parquet files from the bucket defined in env (`AWS_S3_BUCKET`, `AWS_S3_PREFIX`, `AWS_REQUEST_PAYER=requester`).
> - For each object **not** present in `etl_s3_ingest_log`, download and parse parquet using `pyarrow` or `pandas`.
> - Map parquet columns to DB fields as follows (missing columns → NULL):
>   - `twap_id` → `twap_id`
>   - `state_user` → `wallet`
>   - `state_timestamp` → `ts` (convert to UTC timestamptz)
>   - `state_coin` → `asset`
>   - `state_side` → `side`
>   - `state_sz` → `size_requested`
>   - `state_executedSz` → `size_executed`
>   - `state_executedNtl` → `notional_executed`
>   - `status` → `status`
>   - `state_minutes` → `duration_minutes`
> - Insert rows in batches using `ON CONFLICT (twap_id, wallet, ts) DO NOTHING`.
> - After successful insert, insert a row into `etl_s3_ingest_log` with the S3 object key, last modified, and row count.
> - Provide a CLI entrypoint:
>   - `--incremental` (default)
>   - `--since <ISO date>`
>   - `--object-key <key>`
>   - `--local-file <path>` (for tests)
> 
> **API requirements (FastAPI):**
> 1. `GET /api/v1/twaps`
>    - Query params: `wallet` (required), `start` (ISO, required), `end` (ISO, required), `asset` (optional), `latest_per_twap` (bool, default true), `limit` (int, default 500)
>    - Query Postgres for matching rows.
>    - Group by `twap_id`.
>    - If `latest_per_twap=true`, return only the most recent row per `twap_id` (max `ts`).
>    - Response shape:
>      ```json
>      {
>        "wallet": "...",
>        "start": "...",
>        "end": "...",
>        "twaps": [
>          {
>            "twap_id": "123",
>            "asset": "SOL",
>            "side": "B",
>            "status": "activated",
>            "duration_minutes": 30,
>            "latest_ts": "2025-11-03T12:00:00Z",
>            "executed": {
>              "size": "10.5",
>              "notional": "950.25"
>            },
>            "raw": { "...": "original parquet row" }
>          }
>        ]
>      }
>      ```
> 2. `GET /api/v1/twaps/{twap_id}` → return **all** rows for that TWAP ID.
> 3. `GET /healthz` → return DB status and last ingested S3 object (query `etl_s3_ingest_log`).
> 
> **Dev environment:**
> - Provide `docker-compose.yml` that starts Postgres and (optionally) the API service.
> - Provide `.env.example` with all variables.
> - Provide `tests/` with a small sample parquet and unit tests for ETL and API.
> 
> **Coding standards:**
> - Use `black` and `ruff`.
> - Use Pydantic models for API responses.
> - Document each module.
> 
> At the end, produce:
> 1. The full repo tree
> 2. All source files
> 3. Instructions to run:
>    - `docker compose up -d`
>    - `python -m src.db.init`
>    - `python -m src.etl.run --local-file tests/data/sample_twap.parquet`
>    - `uvicorn src.api.main:app --reload`
> 
> Do not leave TODOs. Implement everything.
