# Hyperliquid TWAP API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg?logo=postgresql)](https://www.postgresql.org)

**Production-ready open-source data pipeline and REST API for Hyperliquid TWAP (Time-Weighted Average Price) historical data.**

> *Perfect for tax compliance platforms, DeFi analytics tools, and traders who need complete TWAP execution history.*

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Configuration](#-configuration)
- [ETL Pipeline](#-etl-pipeline)
- [Production Deployment](#-production-deployment)
- [Testing](#-testing)
- [Cost Considerations](#-cost-considerations)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Project Overview

### The Problem

Hyperliquid's API only returns up to **2,000 TWAP trade records** per request, making it impossible to query complete historical data for wallets with extensive trading activity. This limitation blocks:

- 📊 Tax compliance platforms from generating accurate year-end reports
- 📈 DeFi analytics tools from analyzing trading patterns
- 🔍 Traders from auditing their complete TWAP execution history

### Our Solution

This project solves the limitation by:

1. **Fetching** complete historical data directly from Hyperliquid's S3 buckets (`artemis-hyperliquid-data`)
2. **Storing** normalized data in PostgreSQL with optimized indexes
3. **Exposing** a REST API with flexible filtering, pagination, and unlimited history access
4. **Automating** daily incremental updates to stay current

### Key Benefits

| User Type | Benefits |
|-----------|----------|
| **Tax Platforms** | Query complete TWAP history for any wallet and tax year. No 2K record limit. |
| **DeFi Analytics** | Track TWAP execution patterns, volumes, and market activity over time. |
| **Traders** | Monitor your own TWAP orders with full execution visibility. |
| **Developers** | Self-host your own instance. Open source and MIT licensed. |

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|:------:|
| **S3 Data Ingestion** | Fetch from Artemis requester-pays bucket with retry logic | ✅ |
| **Incremental ETL** | Only process new S3 objects - efficient and cost-effective | ✅ |
| **Idempotent Processing** | Safe to re-run without duplicates | ✅ |
| **PostgreSQL Storage** | Production-grade relational database with optimized indexes | ✅ |
| **FastAPI REST API** | Modern async API with auto-generated OpenAPI docs | ✅ |
| **Flexible Filtering** | Query by wallet, time range, asset, TWAP ID | ✅ |
| **Offset Pagination** | Handle large result sets efficiently | ✅ |
| **CORS Support** | Configurable cross-origin access for web apps | ✅ |
| **Prometheus Metrics** | Built-in `/metrics` endpoint for monitoring | ✅ |
| **Structured Logging** | JSON logs for production observability | ✅ |
| **Alembic Migrations** | Database schema versioning and migration management | ✅ |
| **Docker Support** | Full docker-compose setup for easy deployment | ✅ |
| **Type Safety** | Pydantic models and SQLAlchemy ORM | ✅ |
| **Comprehensive Tests** | Unit, integration, and E2E test coverage | ✅ |
| **Production Ready** | Error handling, retries, monitoring, and logging | ✅ |

---

## 🛠️ Tech Stack

### Language & Runtime
- **Python 3.11+** - Modern async features and type hints

### Frameworks & Libraries
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - Async ORM with type safety
- **Pydantic** - Data validation and serialization
- **Alembic** - Database migration management
- **pandas** - Data processing and transformation
- **boto3** - AWS S3 client with requester-pays support

### Infrastructure & Deployment
- **PostgreSQL 14+** - Production database (asyncpg driver)
- **Docker & Docker Compose** - Containerized deployment
- **uvicorn** - ASGI server for FastAPI
- **Prometheus** - Metrics and monitoring

### Testing & Quality
- **pytest** - Testing framework with async support
- **pytest-asyncio** - Async test fixtures
- **pytest-cov** - Code coverage reporting
- **black** - Code formatting
- **ruff** - Fast Python linter

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/) or use Docker
- ✅ **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop) (optional)
- ✅ **AWS Credentials** - For S3 access (create at [AWS IAM](https://console.aws.amazon.com/iam/))
- ✅ **Git** - To clone the repository

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source.git
cd Hyperliquid-TWAP-API-Open-Source/hyperliquid-twap
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Required environment variables:**

```env
# AWS Configuration (required for S3 access)
AWS_REGION=us-east-1
AWS_S3_BUCKET=artemis-hyperliquid-data
AWS_S3_PREFIX=raw/twap_statuses/
AWS_REQUEST_PAYER=requester
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid
```

### Step 3: Start PostgreSQL Database

**Using Docker (recommended for development):**

```bash
docker compose up -d db
```

**Expected output:**
```
✔ Container hyperliquid-twap-db-1  Started
```

Wait for database to be ready:
```bash
docker compose logs -f db
# Look for: "database system is ready to accept connections"
```

### Step 4: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 sqlalchemy-2.0.23 ...
```

### Step 5: Initialize Database Schema

**Using Alembic migrations (recommended):**

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> a1b2c3d4e5f6, Initial schema
```

**Alternative - Direct schema initialization:**

```bash
python -m src.db.init
```

### Step 6: Test with Sample Data

Generate and ingest sample data to verify setup:

```bash
# Generate sample parquet file
python tests/create_sample_data.py

# Ingest the sample data
python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

**Expected output:**
```
INFO - Processing local file: tests/data/sample_twap.parquet
INFO - Parsed 5 rows from parquet
INFO - Inserted batch 1: 5 rows (total: 5)
INFO - Successfully loaded 5 records
```

### Step 7: Start the API Server

```bash
uvicorn src.api.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 8: Test the API

**Health check:**
```bash
curl http://localhost:8000/healthz
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "last_ingested_object": "local:tests/data/sample_twap.parquet",
  "last_ingested_at": "2025-11-04T12:00:00Z"
}
```

**Interactive API documentation:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

🎉 **You're all set!** Continue to [API Reference](#-api-reference) for usage examples.

---

## 🏗️ Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Hyperliquid S3 Bucket                       │
│                    (artemis-hyperliquid-data)                       │
│                  Parquet files: raw/twap_statuses/                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (1) ETL lists new objects
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ETL Pipeline                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │   List   │──▶│ Download │──▶│  Parse   │──▶│   Load   │        │
│  │ S3 Objects│   │  Parquet │   │ Normalize│   │ to DB    │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│       │                                              │              │
│       └──────────────────────────────────────────────┘              │
│              Track processed objects in DB                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (2) Store normalized data
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                            │
│  ┌─────────────────────┐         ┌────────────────────────┐        │
│  │   twap_status       │         │ etl_s3_ingest_log      │        │
│  │  (TWAP records)     │         │ (Processed S3 objects) │        │
│  └─────────────────────┘         └────────────────────────┘        │
│         Indexed on: wallet + ts, twap_id                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (3) Query via REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FastAPI Server                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ GET /twaps   │  │GET /twaps/   │  │ GET /metrics │             │
│  │ (by wallet)  │  │    {id}      │  │ (Prometheus) │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│         CORS, Pagination, Filtering, Logging                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (4) Consume API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Consumers                               │
│    Tax Platforms  │  Analytics Tools  │  Trading Dashboards        │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **ETL Pipeline** | Fetch and process S3 data | Incremental, idempotent, retry logic |
| **PostgreSQL** | Store normalized TWAP data | Indexed queries, ACID compliance |
| **FastAPI Server** | Expose REST API | Async, auto-docs, type-safe |
| **Metrics** | Monitor health and performance | Prometheus endpoint |

---

## 🔌 API Reference

### Base URL

```
http://localhost:8000          # Development
https://api.yourdomain.com     # Production
```

### Interactive Documentation

When the API server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Endpoints Overview

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|:-------------:|
| `/healthz` | GET | Health check with database status | ❌ |
| `/metrics` | GET | Prometheus metrics | ❌ |
| `/api/v1/twaps` | GET | Query TWAPs by wallet and time range | ❌ |
| `/api/v1/twaps/{twap_id}` | GET | Get all status updates for a TWAP | ❌ |

### Authentication

**Current version**: No authentication required (suitable for internal/trusted deployments)

**Production recommendations**:
- Add API key authentication with rate limiting
- Implement JWT tokens for user-specific access
- Use reverse proxy (nginx) for IP whitelisting
- See [DEPLOYMENT.md](./hyperliquid-twap/docs/DEPLOYMENT.md) for security best practices

### Query TWAPs by Wallet

**Endpoint:** `GET /api/v1/twaps`

Query TWAP status records for a specific wallet and time range.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `wallet` | string | ✅ | - | Wallet address (case-sensitive) |
| `start` | datetime | ✅ | - | Start timestamp (ISO 8601 UTC) |
| `end` | datetime | ✅ | - | End timestamp (ISO 8601 UTC) |
| `asset` | string | ❌ | - | Filter by asset/coin (e.g., "SOL", "BTC") |
| `latest_per_twap` | boolean | ❌ | `true` | Return only latest status per TWAP ID |
| `limit` | integer | ❌ | `500` | Max results (1-5000) |
| `offset` | integer | ❌ | `0` | Results to skip (pagination) |

**Example Request:**

```bash
# Get all TWAPs for a wallet in November 2025
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123&start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z"

# Filter by asset
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123&start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z&asset=SOL"

# Pagination (get next 500 results)
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123&start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z&limit=500&offset=500"
```

**Example Response:**

```json
{
  "wallet": "0xabc123",
  "start": "2025-11-01T00:00:00Z",
  "end": "2025-11-30T23:59:59Z",
  "twaps": [
    {
      "twap_id": "123456",
      "asset": "SOL",
      "side": "B",
      "status": "completed",
      "duration_minutes": 30,
      "latest_ts": "2025-11-03T12:30:00Z",
      "executed": {
        "size": "100.0",
        "notional": "9050.00"
      },
      "raw": {
        "wallet": "0xabc123",
        "ts": 1730638200000000000,
        "asset": "SOL",
        "side": "B",
        "size_requested": "100.0",
        "size_executed": "100.0",
        "notional_executed": "9050.00"
      }
    }
  ]
}
```

### Get TWAP by ID

**Endpoint:** `GET /api/v1/twaps/{twap_id}`

Get all status updates for a specific TWAP order, including incomplete executions.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `twap_id` | string | TWAP order identifier |

**Example Request:**

```bash
curl http://localhost:8000/api/v1/twaps/123456
```

**Example Response:**

```json
{
  "twap_id": "123456",
  "updates": [
    {
      "ts": "2025-11-03T12:00:00Z",
      "status": "running",
      "executed": {"size": "50.0", "notional": "4500.00"}
    },
    {
      "ts": "2025-11-03T12:30:00Z",
      "status": "completed",
      "executed": {"size": "100.0", "notional": "9050.00"}
    }
  ]
}
```

### Client Library Examples

**Python:**

```python
import requests
from datetime import datetime, timezone

# Query TWAPs
response = requests.get(
    "http://localhost:8000/api/v1/twaps",
    params={
        "wallet": "0xabc123",
        "start": "2025-11-01T00:00:00Z",
        "end": "2025-11-30T23:59:59Z",
        "asset": "SOL",
        "limit": 100
    }
)
data = response.json()

for twap in data["twaps"]:
    print(f"TWAP {twap['twap_id']}: {twap['executed']['size']} {twap['asset']}")
```

**JavaScript:**

```javascript
// Using fetch API
const response = await fetch(
  'http://localhost:8000/api/v1/twaps?' + new URLSearchParams({
    wallet: '0xabc123',
    start: '2025-11-01T00:00:00Z',
    end: '2025-11-30T23:59:59Z',
    asset: 'SOL',
    limit: '100'
  })
);

const data = await response.json();
data.twaps.forEach(twap => {
  console.log(`TWAP ${twap.twap_id}: ${twap.executed.size} ${twap.asset}`);
});
```

**cURL with jq (pretty printing):**

```bash
curl -s "http://localhost:8000/api/v1/twaps?wallet=0xabc123&start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z" | jq '.twaps[] | {twap_id, asset, status, size: .executed.size}'
```

📖 **Full API Documentation**: See [docs/API.md](./hyperliquid-twap/docs/API.md) for complete reference with all response schemas and error codes.

---

## 💾 Database Schema

### `twap_status` Table

Primary table storing TWAP status records and execution history.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `twap_id` | TEXT | PK, NOT NULL | TWAP order identifier |
| `wallet` | TEXT | PK, NOT NULL | Wallet address |
| `ts` | TIMESTAMPTZ | PK, NOT NULL | Status update timestamp |
| `asset` | TEXT | NOT NULL | Asset/coin symbol (e.g., "SOL", "BTC") |
| `side` | TEXT | NOT NULL | "B" (Buy) or "A" (Ask/Sell) |
| `size_requested` | NUMERIC | - | Total requested order size |
| `size_executed` | NUMERIC | - | Size executed so far |
| `notional_executed` | NUMERIC | - | Notional value executed (USD) |
| `status` | TEXT | - | TWAP status (e.g., "running", "completed") |
| `duration_minutes` | INTEGER | - | TWAP order duration |
| `s3_object_key` | TEXT | - | Source S3 object path |
| `raw_payload` | JSONB | - | Full parquet row (for extensibility) |
| `inserted_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | ETL insertion timestamp |

**Primary Key**: `(twap_id, wallet, ts)` - Composite key ensures uniqueness per status update

**Indexes**:
```sql
-- Optimized for wallet + time range queries
CREATE INDEX idx_twap_status_wallet_ts ON twap_status(wallet, ts);

-- Optimized for TWAP ID lookups
CREATE INDEX idx_twap_status_twap_id ON twap_status(twap_id);
```

### `etl_s3_ingest_log` Table

Tracks processed S3 objects for idempotent ETL operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `s3_object_key` | TEXT | PK, NOT NULL | S3 object key (unique) |
| `last_modified` | TIMESTAMPTZ | - | S3 object last modified time |
| `rows_ingested` | INTEGER | - | Number of rows processed |
| `error_text` | TEXT | - | Error message if processing failed |
| `ingested_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Processing timestamp |

**Primary Key**: `s3_object_key`

**Query for failed ingestions:**
```sql
SELECT s3_object_key, error_text, ingested_at 
FROM etl_s3_ingest_log 
WHERE error_text IS NOT NULL 
ORDER BY ingested_at DESC;
```

### Performance Optimization

**Index Usage:**
- `idx_twap_status_wallet_ts`: Used for API queries filtering by wallet and time range (most common query pattern)
- `idx_twap_status_twap_id`: Used for TWAP ID lookups

**JSONB Benefits:**
- `raw_payload` stored as JSONB for flexibility
- Allows querying nested fields if needed
- Preserves original data for debugging

**Query Performance:**
```sql
-- Efficient query using composite index
EXPLAIN ANALYZE 
SELECT * FROM twap_status 
WHERE wallet = '0xabc123' 
  AND ts >= '2025-11-01' 
  AND ts < '2025-12-01';

-- Expected: Index Scan using idx_twap_status_wallet_ts
```

---

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for all options.

### Database Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |

**Example:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

**Special characters in password**: URL-encode special characters or use quotes:
```env
# Password with special chars: p@ss!word
DATABASE_URL=postgresql+asyncpg://user:p%40ss%21word@localhost:5432/dbname
```

### AWS S3 Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `AWS_REGION` | ❌ | `us-east-1` | AWS region |
| `AWS_S3_BUCKET` | ❌ | `artemis-hyperliquid-data` | S3 bucket name |
| `AWS_S3_PREFIX` | ❌ | `raw/twap_statuses/` | S3 prefix for TWAP data |
| `AWS_REQUEST_PAYER` | ❌ | `requester` | S3 requester-pays setting |
| `AWS_ACCESS_KEY_ID` | ✅ | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | - | AWS secret key |

**Cost Note**: The S3 bucket is requester-pays. You will be charged for data transfer and requests. See [Cost Considerations](#-cost-considerations).

### API Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `API_HOST` | ❌ | `0.0.0.0` | API server host |
| `API_PORT` | ❌ | `8000` | API server port |
| `CORS_ORIGINS` | ❌ | `*` | Comma-separated allowed origins |

**CORS Examples:**
```env
# Allow all (development only)
CORS_ORIGINS=*

# Allow specific origins (production)
CORS_ORIGINS=https://app.example.com,https://dashboard.example.com
```

### Logging Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `LOG_LEVEL` | ❌ | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | ❌ | `json` | Log format (`json` or `text`) |

**Log Format Examples:**

**JSON (production):**
```env
LOG_FORMAT=json
```
Output: `{"timestamp":"2025-11-04T12:00:00Z","level":"INFO","message":"Processing S3 object","s3_key":"raw/twap_statuses/2025/11/04/data.parquet"}`

**Text (development):**
```env
LOG_FORMAT=text
```
Output: `2025-11-04 12:00:00 - INFO - Processing S3 object: raw/twap_statuses/2025/11/04/data.parquet`

### Security Best Practices

**Environment Variables:**
- ✅ Use `.env` file for local development (never commit to Git)
- ✅ Use environment-specific secrets management in production (AWS Secrets Manager, HashiCorp Vault)
- ✅ Rotate AWS credentials regularly
- ✅ Use IAM roles with minimal required permissions

**Database:**
- ✅ Use strong passwords (minimum 16 characters)
- ✅ Restrict PostgreSQL network access (use `listen_addresses` and `pg_hba.conf`)
- ✅ Enable SSL/TLS for database connections in production
- ✅ Regular backups with encryption

**API:**
- ✅ Implement authentication and rate limiting for production
- ✅ Use HTTPS (TLS/SSL) with valid certificates
- ✅ Configure CORS restrictively (specific origins only)
- ✅ Deploy behind reverse proxy (nginx) with request filtering

---

## 🔄 ETL Pipeline

### ETL Modes

The ETL pipeline supports multiple modes for flexible data ingestion:

#### 1. Incremental Mode (Recommended)

Process only new S3 objects not yet in the database.

```bash
python -m src.etl.run --incremental
```

**Use case**: Daily automated runs to stay up-to-date

#### 2. Process Since Date

Process all S3 objects modified after a specific date.

```bash
python -m src.etl.run --since 2025-11-01T00:00:00Z
```

**Use case**: Backfill data from a specific date forward

#### 3. Process Specific Object

Process a single S3 object by its key.

```bash
python -m src.etl.run --object-key raw/twap_statuses/2025/11/03/data.parquet
```

**Use case**: Reprocess a specific file after fix

#### 4. Process Local File

Process a local parquet file (for testing or manual loads).

```bash
python -m src.etl.run --local-file /path/to/file.parquet
```

**Use case**: Testing with sample data

### Automated Scheduling

#### Using Cron (Linux/macOS)

Add to your crontab (`crontab -e`):

```cron
# Run ETL daily at 00:30 UTC
30 0 * * * cd /srv/hyperliquid-twap && /usr/bin/env bash -c 'source venv/bin/activate && python -m src.etl.run --incremental >> logs/etl.log 2>&1'
```

#### Using systemd Timer (Linux)

Create `/etc/systemd/system/hyperliquid-etl.service`:

```ini
[Unit]
Description=Hyperliquid TWAP ETL
After=network.target postgresql.service

[Service]
Type=oneshot
User=hyperliquid
WorkingDirectory=/srv/hyperliquid-twap
Environment="PATH=/srv/hyperliquid-twap/venv/bin"
EnvironmentFile=/srv/hyperliquid-twap/.env
ExecStart=/srv/hyperliquid-twap/venv/bin/python -m src.etl.run --incremental
StandardOutput=append:/var/log/hyperliquid-etl.log
StandardError=append:/var/log/hyperliquid-etl.log
```

Create `/etc/systemd/system/hyperliquid-etl.timer`:

```ini
[Unit]
Description=Run Hyperliquid TWAP ETL daily

[Timer]
OnCalendar=daily
OnCalendar=00:30
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable hyperliquid-etl.timer
sudo systemctl start hyperliquid-etl.timer
sudo systemctl status hyperliquid-etl.timer
```

### ETL Flow

```
┌─────────────────────────────────────────────────────┐
│  1. List S3 Objects                                 │
│     - Query objects not in etl_s3_ingest_log       │
│     - Filter by date if --since provided           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  2. Download & Parse                                │
│     - Download parquet from S3                      │
│     - Parse with pandas                             │
│     - Validate schema                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  3. Transform & Normalize                           │
│     - Convert timestamps                            │
│     - Normalize column names                        │
│     - Add metadata (s3_object_key, inserted_at)     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  4. Load to Database                                │
│     - Batch insert (1000 rows/batch)                │
│     - Skip duplicates (ON CONFLICT DO NOTHING)      │
│     - Update etl_s3_ingest_log                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  5. Track & Monitor                                 │
│     - Log success/failure                           │
│     - Update metrics                                │
│     - Continue to next object                       │
└─────────────────────────────────────────────────────┘
```

### Error Handling

The ETL pipeline includes robust error handling:

- ✅ **Per-object isolation**: One corrupted file won't stop the entire run
- ✅ **Automatic retries**: S3 downloads retry 3 times with exponential backoff
- ✅ **Error tracking**: Failed objects logged in `etl_s3_ingest_log` with error messages
- ✅ **Graceful degradation**: Processing continues with remaining objects

**Query failed ingestions:**
```sql
SELECT s3_object_key, error_text, ingested_at 
FROM etl_s3_ingest_log 
WHERE error_text IS NOT NULL 
ORDER BY ingested_at DESC;
```

---

## 🚀 Production Deployment

### Docker Deployment

#### Quick Start with Docker Compose

```bash
# Navigate to project directory
cd hyperliquid-twap

# Copy and configure environment
cp .env.example .env
# Edit .env with production values

# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service health
curl http://localhost:8000/healthz
```

#### Production docker-compose.yml

The included `docker-compose.yml` provides:
- PostgreSQL database with persistent volume
- API server with automatic restarts
- Shared network for service communication

**Volume management:**
```bash
# Backup database
docker compose exec db pg_dump -U hyperliquid hyperliquid > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251104.sql | docker compose exec -T db psql -U hyperliquid hyperliquid
```

### Systemd Service (Linux)

For running the API as a system service:

Create `/etc/systemd/system/hyperliquid-api.service`:

```ini
[Unit]
Description=Hyperliquid TWAP API
After=network.target postgresql.service

[Service]
Type=simple
User=hyperliquid
WorkingDirectory=/srv/hyperliquid-twap
Environment="PATH=/srv/hyperliquid-twap/venv/bin"
EnvironmentFile=/srv/hyperliquid-twap/.env
ExecStart=/srv/hyperliquid-twap/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hyperliquid-api
sudo systemctl start hyperliquid-api
sudo systemctl status hyperliquid-api
```

### Nginx Reverse Proxy

Example nginx configuration for HTTPS and load balancing:

```nginx
upstream hyperliquid_api {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location / {
        proxy_pass http://hyperliquid_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate limiting (optional)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://hyperliquid_api;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Monitoring & Alerting

#### Prometheus Scraping

Configure Prometheus to scrape the `/metrics` endpoint:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'hyperliquid-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

#### Grafana Dashboard

Available metrics:
- `http_requests_total` - Total HTTP requests by endpoint and status
- `http_request_duration_seconds` - Request latency histogram
- `database_connections_active` - Active database connections
- `etl_objects_processed_total` - Total S3 objects processed
- `etl_rows_ingested_total` - Total rows ingested

#### Health Check Monitoring

Use the `/healthz` endpoint for uptime monitoring:

```bash
# Example with UptimeRobot, Pingdom, or custom script
curl -f http://localhost:8000/healthz || alert_team
```

📖 **Full Deployment Guide**: See [docs/DEPLOYMENT.md](./hyperliquid-twap/docs/DEPLOYMENT.md) for complete production setup.

---

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

### Test Coverage

The project includes comprehensive test coverage:

| Test Type | Files | Coverage |
|-----------|-------|----------|
| **ETL Tests** | `tests/test_etl.py` | Parsing, loading, idempotency |
| **API Tests** | `tests/test_api.py` | Endpoints, validation, errors |
| **Async Tests** | `tests/test_api_async.py` | Database ops, grouping, filtering |
| **Integration** | Multiple | End-to-end workflows |

**View coverage report:**
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Test Data

Generate sample data for testing:

```bash
python tests/create_sample_data.py
```

This creates `tests/data/sample_twap.parquet` with realistic TWAP records.

### Continuous Integration

Example GitHub Actions workflow (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: hyperliquid
          POSTGRES_PASSWORD: password
          POSTGRES_DB: hyperliquid_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid_test
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 💰 Cost Considerations

This service uses AWS requester-pays S3 buckets. **You will be charged for**:

### AWS S3 Costs

| Cost Category | Rate (US East) | Estimation |
|---------------|----------------|------------|
| **LIST requests** | $0.005 per 1,000 requests | ~$0.01/day for incremental |
| **GET requests** | $0.0004 per 1,000 requests | ~$0.01/day for incremental |
| **Data transfer** | $0.09 per GB | Depends on data volume |

### Cost Estimates

| Scenario | Monthly Cost | Description |
|----------|--------------|-------------|
| **Initial backfill** | $5 - $50 | One-time cost for full historical data |
| **Daily incremental** | $0.10 - $1.00 | Processing new daily data |
| **Heavy usage** | $10 - $20 | Multiple backfills or large date ranges |

### Cost Optimization Tips

✅ **Run incrementally**: Use `--incremental` mode to only process new objects

```bash
# Good: Only new data
python -m src.etl.run --incremental

# Expensive: Full backfill
python -m src.etl.run --since 2020-01-01T00:00:00Z
```

✅ **Monitor processed objects**: Check `etl_s3_ingest_log` table to avoid reprocessing

```sql
SELECT COUNT(*) FROM etl_s3_ingest_log;  -- Objects processed
```

✅ **Use date filters**: Limit backfills to required date ranges

```bash
# Process only November 2025
python -m src.etl.run --since 2025-11-01T00:00:00Z
```

✅ **Schedule wisely**: Run ETL during off-peak hours to batch requests

✅ **Cache locally**: Once data is in PostgreSQL, use the API instead of re-fetching from S3

### Monitoring Costs

Track your AWS costs:
- **AWS Cost Explorer**: https://console.aws.amazon.com/cost-management/
- **CloudWatch Metrics**: Monitor S3 request counts
- **Billing Alerts**: Set up alerts for unexpected charges

---

## 📚 Documentation

### Quick Links

| Document | Description |
|----------|-------------|
| **[Quick Start Guide](./hyperliquid-twap/QUICKSTART.md)** | Get running in 5 minutes |
| **[API Reference](./hyperliquid-twap/docs/API.md)** | Complete REST API documentation |
| **[Deployment Guide](./hyperliquid-twap/docs/DEPLOYMENT.md)** | Production setup with systemd, nginx, Docker |
| **[Alembic Migrations](./hyperliquid-twap/docs/ALEMBIC_GUIDE.md)** | Database schema versioning |
| **[Contributing Guidelines](./hyperliquid-twap/docs/CONTRIBUTING.md)** | Development workflow and code style |

### Implementation Notes

For developers and maintainers:

- **[Improvements Log](./hyperliquid-twap/docs/implementation/improvements.md)** - All enhancements and fixes
- **[Code Review](./hyperliquid-twap/docs/implementation/review-summary.md)** - Architecture assessment
- **[Implementation Notes](./hyperliquid-twap/docs/implementation/implementation-notes.md)** - Feature completion details

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Fails

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

```bash
# Check PostgreSQL is running
docker compose ps
# or
sudo systemctl status postgresql

# View database logs
docker compose logs db

# Test connection manually
psql postgresql://hyperliquid:password@localhost:5432/hyperliquid

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://user:password@host:port/dbname
```

**Special characters in password**: URL-encode or quote:
```env
# Password: p@ss!word
DATABASE_URL=postgresql+asyncpg://user:p%40ss%21word@localhost:5432/dbname
```

#### 2. S3 Access Denied

**Symptom:**
```
botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the ListObjectsV2 operation
```

**Solutions:**

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test S3 access (requester-pays)
aws s3 ls s3://artemis-hyperliquid-data/raw/twap_statuses/ --request-payer requester

# Check IAM permissions
# Required: s3:ListBucket, s3:GetObject on artemis-hyperliquid-data
```

#### 3. ETL Processing Errors

**Symptom:**
```
ERROR - Failed to process S3 object: ...
```

**Solutions:**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m src.etl.run --incremental

# Check failed ingestions in database
psql $DATABASE_URL -c "SELECT s3_object_key, error_text FROM etl_s3_ingest_log WHERE error_text IS NOT NULL;"

# Reprocess specific failed object
python -m src.etl.run --object-key raw/twap_statuses/2025/11/04/data.parquet
```

#### 4. API Returns Empty Results

**Symptom:**
```json
{"wallet": "0xabc123", "twaps": []}
```

**Solutions:**

```bash
# Verify data exists in database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM twap_status WHERE wallet='0xabc123';"

# Check timestamp format (must be UTC ISO 8601)
# ✅ Correct: 2025-11-01T00:00:00Z
# ❌ Wrong: 2025-11-01 00:00:00

# Verify time range contains data
psql $DATABASE_URL -c "SELECT MIN(ts), MAX(ts) FROM twap_status WHERE wallet='0xabc123';"
```

#### 5. Tests Fail

**Symptom:**
```
ImportError: cannot import name 'load_to_db' from 'src.etl.loader'
```

**Solutions:**

```bash
# Ensure you're in the correct directory
pwd  # Should be: /path/to/hyperliquid-twap

# Install dependencies
pip install -r requirements.txt

# Generate test data
python tests/create_sample_data.py

# Run with verbose output
pytest -vv

# Run specific failing test
pytest tests/test_etl.py::test_parse_parquet -vv
```

### Debug Commands

**Check service status:**
```bash
# Database
docker compose ps db

# API server
curl http://localhost:8000/healthz

# Recent logs
docker compose logs --tail=100 api
```

**Database queries:**
```sql
-- Total records
SELECT COUNT(*) FROM twap_status;

-- Recent ingestions
SELECT * FROM etl_s3_ingest_log ORDER BY ingested_at DESC LIMIT 10;

-- Failed ingestions
SELECT s3_object_key, error_text FROM etl_s3_ingest_log WHERE error_text IS NOT NULL;

-- Records by wallet
SELECT wallet, COUNT(*) FROM twap_status GROUP BY wallet ORDER BY COUNT(*) DESC LIMIT 10;
```

**ETL debug mode:**
```bash
# Maximum verbosity
LOG_LEVEL=DEBUG LOG_FORMAT=text python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

### Getting Help

If you're still stuck:

1. **Check existing issues**: Search [GitHub Issues](https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source/issues)
2. **Review documentation**: See [docs/](./hyperliquid-twap/docs/) for detailed guides
3. **Open an issue**: Provide error logs, environment details, and steps to reproduce

---

## 🤝 Contributing

Contributions are welcome! This is an open-source project.

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
```bash
git clone https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source.git
cd Hyperliquid-TWAP-API-Open-Source/hyperliquid-twap
```

3. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Set up pre-commit hooks:**
```bash
pip install pre-commit
pre-commit install
```

### Code Style

We use automated code formatting and linting:

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking (optional)
mypy src/
```

### Running Tests

Ensure all tests pass before submitting a PR:

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term

# Ensure coverage is above 80%
```

### Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** with clear, atomic commits

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run tests and formatting:**
```bash
black src/ tests/
ruff check src/ tests/
pytest -v
```

6. **Push to your fork:**
```bash
git push origin feature/your-feature-name
```

7. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if UI changes)

### Commit Message Guidelines

Follow conventional commits format:

```
feat: add pagination to TWAP endpoint
fix: handle null values in size_executed
docs: update API reference with examples
test: add integration tests for ETL
refactor: extract S3 client to separate module
```

📖 **Full Contributing Guide**: See [docs/CONTRIBUTING.md](./hyperliquid-twap/docs/CONTRIBUTING.md)

---

## 📄 License

MIT License - See [hyperliquid-twap/LICENSE](./hyperliquid-twap/LICENSE)

```
Copyright (c) 2025 Hyperliquid TWAP API Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **Hyperliquid** for providing public S3 data access via Artemis
- **FastAPI** community for the excellent web framework
- **PostgreSQL** team for the robust database system
- **Open-source contributors** for the tools that power this project

---

## 📞 Support

### Documentation
- **Quick Start**: [QUICKSTART.md](./hyperliquid-twap/QUICKSTART.md)
- **API Docs**: [docs/API.md](./hyperliquid-twap/docs/API.md)
- **Deployment**: [docs/DEPLOYMENT.md](./hyperliquid-twap/docs/DEPLOYMENT.md)

### Community
- **Issues**: [GitHub Issues](https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source/discussions)

### Project Status
- **Version**: Production-Ready v2.0
- **Status**: ✅ Actively Maintained
- **License**: MIT

---

<div align="center">

**Built with ❤️ for the Hyperliquid and DeFi community**

[Report Bug](https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source/issues) · [Request Feature](https://github.com/yourusername/Hyperliquid-TWAP-API-Open-Source/issues) · [View Docs](./hyperliquid-twap/docs/)

</div>
