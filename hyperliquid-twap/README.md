# Hyperliquid TWAP Data Service

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Production-ready ETL pipeline and REST API for querying Hyperliquid TWAP (Time-Weighted Average Price) historical data from Artemis S3 buckets.

**Version**: Production-Ready v2.0  
**Status**: ✅ 100% Complete

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [ETL Pipeline](#etl-pipeline)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [Development](#development)
- [Cost Considerations](#cost-considerations)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

### The Problem

Hyperliquid's API returns a maximum of **2,000 TWAP trade records** per request. For wallets with extensive trading activity, this makes it impossible to:

- Generate complete tax reports for a full year
- Analyze trading patterns over time
- Audit complete TWAP execution history

### The Solution

This service addresses these limitations by:

1. **Fetching** complete historical TWAP data from Hyperliquid's S3 buckets (`artemis-hyperliquid-data`)
2. **Storing** normalized data in PostgreSQL with optimized indexes for fast queries
3. **Exposing** a REST API with flexible filtering, pagination, and unlimited historical access
4. **Automating** incremental daily updates to stay current

### Use Cases

| Use Case | Example |
|----------|---------|
| **Tax Platforms** | Query complete TWAP history for wallet `0xabc123` for tax year 2025 |
| **DeFi Analytics** | Track TWAP execution patterns, volumes, and market activity |
| **Traders** | Monitor your own TWAP orders with complete execution visibility |
| **Developers** | Self-host your own instance with full source access |

---

## Features

### Core Functionality

| Feature | Status | Description |
|---------|:------:|-------------|
| **S3 Data Ingestion** | ✅ | Fetch from Artemis requester-pays bucket (`artemis-hyperliquid-data`) |
| **Incremental ETL** | ✅ | Only process new S3 objects for efficiency |
| **Idempotent Processing** | ✅ | Safe to re-run without duplicates (tracked in `etl_s3_ingest_log`) |
| **PostgreSQL Storage** | ✅ | Production-grade database with composite indexes |
| **Async FastAPI** | ✅ | High-performance async REST API |
| **Flexible Filtering** | ✅ | Query by wallet, time range, asset, TWAP ID |
| **Pagination** | ✅ | Offset-based pagination (1-5000 results per page) |
| **CORS Support** | ✅ | Configurable cross-origin resource sharing |
| **Prometheus Metrics** | ✅ | Built-in `/metrics` endpoint for monitoring |
| **Structured Logging** | ✅ | JSON or text format for observability |
| **Alembic Migrations** | ✅ | Database schema versioning |
| **Type Safety** | ✅ | Pydantic models + SQLAlchemy 2.0 |
| **Comprehensive Tests** | ✅ | Unit, integration, and E2E coverage |
| **Docker Support** | ✅ | Full docker-compose setup |

### Technical Highlights

- **Async/Await**: Modern Python async throughout (SQLAlchemy 2.0 + asyncpg)
- **Error Handling**: Per-object isolation in ETL - one corrupted file won't stop entire run
- **Retry Logic**: Automatic S3 retry with exponential backoff (3 attempts, adaptive mode)
- **Batch Processing**: Efficient batch inserts (1000 rows per batch)
- **Conflict Resolution**: `ON CONFLICT DO NOTHING` for idempotent loads
- **Performance**: Composite indexes optimized for common query patterns

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hyperliquid S3 Bucket                        │
│              artemis-hyperliquid-data (requester-pays)          │
│                   raw/twap_statuses/*.parquet                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ ETL: boto3 + pandas
                             │ • List new objects
                             │ • Download parquet
                             │ • Parse & transform
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                        │
│  ┌──────────────────────┐        ┌────────────────────┐        │
│  │  twap_status         │        │ etl_s3_ingest_log  │        │
│  │  (TWAP records)      │        │ (Tracking table)   │        │
│  │  PK: (twap_id,       │        │ PK: s3_object_key  │        │
│  │       wallet, ts)    │        │                    │        │
│  └──────────────────────┘        └────────────────────┘        │
│       Indexes:                                                  │
│       • (wallet, ts)  - Fast wallet queries                     │
│       • (twap_id)     - Fast TWAP lookups                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Query: FastAPI + SQLAlchemy
                             │ • Async endpoints
                             │ • Auto-generated docs
                             │ • Prometheus metrics
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         REST API                                │
│  GET /api/v1/twaps           - Query by wallet + time range    │
│  GET /api/v1/twaps/{id}      - Get TWAP by ID                  │
│  GET /healthz                - Health check                     │
│  GET /metrics                - Prometheus metrics               │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
S3 Object → Download → Parse Parquet → Transform → Batch Insert → PostgreSQL
                                                            ↓
                                              Track in etl_s3_ingest_log
                                                            ↓
                                                  Expose via REST API
```

### Component Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Storage** | AWS S3 | Source data (parquet files) |
| **ETL** | boto3 + pandas | Data extraction and transformation |
| **Database** | PostgreSQL 14+ | Normalized data storage |
| **ORM** | SQLAlchemy 2.0 (async) | Database operations |
| **API** | FastAPI + uvicorn | REST API server |
| **Validation** | Pydantic | Request/response validation |
| **Monitoring** | Prometheus | Metrics and observability |
| **Deployment** | Docker Compose | Container orchestration |

---

## Quick Start

### Prerequisites

- ✅ Python 3.11+
- ✅ PostgreSQL 14+
- ✅ Docker & Docker Compose (optional)
- ✅ AWS credentials (for S3 access)

### 1. Clone Repository

```bash
git clone <repository-url>
cd hyperliquid-twap
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials and database URL
```

**Required variables:**
```env
DATABASE_URL=postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 3. Start Database

```bash
docker compose up -d db
```

### 4. Initialize Schema

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

### 5. Load Sample Data

```bash
# Generate sample data
python tests/create_sample_data.py

# Ingest it
python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

### 6. Start API Server

```bash
uvicorn src.api.main:app --reload
```

### 7. Test API

```bash
# Health check
curl http://localhost:8000/healthz

# Interactive docs
open http://localhost:8000/docs
```

🎉 **Done!** See [QUICKSTART.md](QUICKSTART.md) for detailed guide.

---

## API Reference

### Base URL

```
http://localhost:8000          # Development
https://api.yourdomain.com     # Production
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check with database status |
| `/metrics` | GET | Prometheus metrics |
| `/api/v1/twaps` | GET | Query TWAPs by wallet and time range |
| `/api/v1/twaps/{twap_id}` | GET | Get all status updates for a TWAP |

### Query TWAPs by Wallet

**Endpoint:** `GET /api/v1/twaps`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `wallet` | string | ✅ | - | Wallet address |
| `start` | datetime | ✅ | - | Start timestamp (ISO 8601 UTC) |
| `end` | datetime | ✅ | - | End timestamp (ISO 8601 UTC) |
| `asset` | string | ❌ | - | Filter by asset (e.g., "SOL") |
| `latest_per_twap` | boolean | ❌ | `true` | Latest status only |
| `limit` | integer | ❌ | `500` | Max results (1-5000) |
| `offset` | integer | ❌ | `0` | Pagination offset |

**Example:**

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123&start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z&asset=SOL"
```

**Response:**

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
      }
    }
  ]
}
```

### Client Examples

**Python:**

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/twaps",
    params={
        "wallet": "0xabc123",
        "start": "2025-11-01T00:00:00Z",
        "end": "2025-11-30T23:59:59Z",
        "asset": "SOL"
    }
)
data = response.json()
```

**JavaScript:**

```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/twaps?' + new URLSearchParams({
    wallet: '0xabc123',
    start: '2025-11-01T00:00:00Z',
    end: '2025-11-30T23:59:59Z',
    asset: 'SOL'
  })
);
const data = await response.json();
```

📖 **Full API Documentation**: [docs/API.md](docs/API.md)

---

## Database Schema

### `twap_status` Table

Primary table for TWAP status records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `twap_id` | TEXT | PK, NOT NULL | TWAP order ID |
| `wallet` | TEXT | PK, NOT NULL | Wallet address |
| `ts` | TIMESTAMPTZ | PK, NOT NULL | Status timestamp (UTC) |
| `asset` | TEXT | NOT NULL | Asset symbol (e.g., "SOL") |
| `side` | TEXT | NOT NULL | "B" (Buy) or "A" (Sell) |
| `size_requested` | NUMERIC | - | Total requested size |
| `size_executed` | NUMERIC | - | Executed size so far |
| `notional_executed` | NUMERIC | - | Executed notional (USD) |
| `status` | TEXT | - | TWAP status |
| `duration_minutes` | INTEGER | - | TWAP duration |
| `s3_object_key` | TEXT | - | Source S3 object |
| `raw_payload` | JSONB | - | Full parquet row |
| `inserted_at` | TIMESTAMPTZ | NOT NULL | ETL insert time |

**Primary Key:** `(twap_id, wallet, ts)`

**Indexes:**

```sql
-- Optimized for wallet + time range queries
CREATE INDEX idx_twap_status_wallet_ts ON twap_status(wallet, ts);

-- Optimized for TWAP ID lookups
CREATE INDEX idx_twap_status_twap_id ON twap_status(twap_id);
```

### `etl_s3_ingest_log` Table

Tracks processed S3 objects for idempotent ETL.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `s3_object_key` | TEXT | PK | S3 object key |
| `last_modified` | TIMESTAMPTZ | - | S3 last modified |
| `rows_ingested` | INTEGER | - | Rows processed |
| `error_text` | TEXT | - | Error if failed |
| `ingested_at` | TIMESTAMPTZ | NOT NULL | Processing time |

**Query failed ingestions:**

```sql
SELECT s3_object_key, error_text, ingested_at 
FROM etl_s3_ingest_log 
WHERE error_text IS NOT NULL 
ORDER BY ingested_at DESC;
```

---

## ETL Pipeline

### ETL Modes

#### 1. Incremental (Recommended)

Process only new S3 objects:

```bash
python -m src.etl.run --incremental
```

#### 2. Since Date

Process objects since specific date:

```bash
python -m src.etl.run --since 2025-11-01T00:00:00Z
```

#### 3. Specific Object

Process single S3 object:

```bash
python -m src.etl.run --object-key raw/twap_statuses/2025/11/03/data.parquet
```

#### 4. Local File

Process local parquet file:

```bash
python -m src.etl.run --local-file /path/to/file.parquet
```

### ETL Process Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. List S3 Objects                                           │
│    • Query new objects not in etl_s3_ingest_log              │
│    • Filter by --since date if provided                      │
│    • Use requester-pays mode                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Download & Parse                                          │
│    • Download parquet from S3 (with retry: 3 attempts)       │
│    • Parse with pandas.read_parquet()                        │
│    • Validate schema and data types                          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Transform & Normalize                                     │
│    • Convert nanosecond timestamps to UTC datetime           │
│    • Normalize column names                                  │
│    • Add metadata: s3_object_key, inserted_at                │
│    • Convert to dict records                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Load to Database                                          │
│    • Batch insert (1000 rows per batch)                      │
│    • Use INSERT ... ON CONFLICT DO NOTHING                   │
│    • Update etl_s3_ingest_log with success/failure           │
│    • Commit transaction                                      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Track & Continue                                          │
│    • Log success with row count                              │
│    • On error: log but continue to next object               │
│    • Update Prometheus metrics                               │
└──────────────────────────────────────────────────────────────┘
```

### Error Handling

- **Per-object isolation**: One corrupted file won't stop entire ETL run
- **Automatic retries**: S3 downloads retry 3 times with exponential backoff
- **Error tracking**: Failed objects logged in `etl_s3_ingest_log.error_text`
- **Graceful degradation**: Processing continues with remaining objects

### Automated Scheduling

**Cron (daily at 00:30 UTC):**

```cron
30 0 * * * cd /srv/hyperliquid-twap && source venv/bin/activate && python -m src.etl.run --incremental >> logs/etl.log 2>&1
```

**Systemd timer:**

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for systemd service + timer configuration.

---

## Configuration

### Environment Variables

Configuration via `.env` file or environment:

#### Database

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection URL |

**Format:** `postgresql+asyncpg://user:password@host:port/dbname`

#### AWS S3

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `AWS_REGION` | ❌ | `us-east-1` | AWS region |
| `AWS_S3_BUCKET` | ❌ | `artemis-hyperliquid-data` | S3 bucket name |
| `AWS_S3_PREFIX` | ❌ | `raw/twap_statuses/` | S3 prefix |
| `AWS_REQUEST_PAYER` | ❌ | `requester` | Requester-pays mode |
| `AWS_ACCESS_KEY_ID` | ✅ | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | - | AWS secret key |

#### API Server

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `API_HOST` | ❌ | `0.0.0.0` | API bind host |
| `API_PORT` | ❌ | `8000` | API bind port |
| `CORS_ORIGINS` | ❌ | `*` | Allowed CORS origins |

#### Logging

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `LOG_FORMAT` | ❌ | `json` | Log format (`json` or `text`) |

### Example .env

```env
# Database
DATABASE_URL=postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid

# AWS
AWS_REGION=us-east-1
AWS_S3_BUCKET=artemis-hyperliquid-data
AWS_S3_PREFIX=raw/twap_statuses/
AWS_REQUEST_PAYER=requester
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=secret...

# API
CORS_ORIGINS=https://app.example.com,https://dashboard.example.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Production Deployment

### Docker Deployment

**Start all services:**

```bash
docker compose up -d
```

**View logs:**

```bash
docker compose logs -f api
```

**Stop services:**

```bash
docker compose down
```

**Backup database:**

```bash
docker compose exec db pg_dump -U hyperliquid hyperliquid > backup_$(date +%Y%m%d).sql
```

### Systemd Service

Example service file for API server:

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

[Install]
WantedBy=multi-user.target
```

### Monitoring

**Prometheus metrics** available at `/metrics`:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `database_connections_active` - DB connections
- `etl_objects_processed_total` - S3 objects processed
- `etl_rows_ingested_total` - Total rows ingested

**Health checks** at `/healthz`:

```bash
curl http://localhost:8000/healthz
```

📖 **Full Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Testing

### Run Tests

```bash
# All tests
pytest -v

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# Specific test file
pytest tests/test_api.py -v

# Specific test
pytest tests/test_etl.py::test_parse_parquet -v
```

### Test Coverage

| Test Type | File | Coverage |
|-----------|------|----------|
| **ETL Tests** | `tests/test_etl.py` | Parsing, loading, idempotency |
| **API Tests** | `tests/test_api.py` | Endpoints, validation |
| **Async Tests** | `tests/test_api_async.py` | DB ops, grouping |
| **Integration** | Multiple | End-to-end flows |

### Generate Sample Data

```bash
python tests/create_sample_data.py
```

Creates `tests/data/sample_twap.parquet` with realistic data.

---

## Development

### Project Structure

```
hyperliquid-twap/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # API endpoints
│   │   ├── models.py     # Pydantic models
│   │   ├── database.py   # DB connection
│   │   └── config.py     # API config
│   ├── etl/              # ETL pipeline
│   │   ├── run.py        # CLI entrypoint
│   │   ├── s3_client.py  # S3 access
│   │   ├── parser.py     # Parquet parsing
│   │   ├── loader.py     # DB loading
│   │   └── config.py     # ETL config
│   └── db/               # Database layer
│       ├── init.py       # Schema init
│       ├── models.py     # SQLAlchemy models
│       └── schema.sql    # SQL DDL
├── alembic/              # DB migrations
├── tests/                # Test suite
├── docs/                 # Documentation
├── docker-compose.yml    # Docker setup
├── requirements.txt      # Dependencies
└── README.md             # This file
```

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Adding Features

1. Create feature branch
2. Add tests first (TDD)
3. Implement feature
4. Run tests + linting
5. Update documentation
6. Submit PR

📖 **Contributing Guide**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## Cost Considerations

### AWS S3 Costs

This service uses **requester-pays** S3 buckets. You pay for:

| Cost Type | Rate (US East) | Estimated |
|-----------|----------------|-----------|
| **LIST requests** | $0.005 / 1K requests | $0.01/day incremental |
| **GET requests** | $0.0004 / 1K requests | $0.01/day incremental |
| **Data transfer** | $0.09 / GB | Depends on volume |

### Cost Estimates

| Scenario | Monthly Cost |
|----------|--------------|
| **Initial backfill** | $5 - $50 (one-time) |
| **Daily incremental** | $0.10 - $1.00 |
| **Heavy usage** | $10 - $20 |

### Cost Optimization

✅ **Use incremental mode**: Only process new objects

```bash
python -m src.etl.run --incremental  # Good
```

✅ **Limit date ranges**: Use `--since` for targeted backfills

```bash
python -m src.etl.run --since 2025-11-01T00:00:00Z
```

✅ **Monitor processed objects**:

```sql
SELECT COUNT(*) FROM etl_s3_ingest_log;
```

---

## Troubleshooting

### Database Connection Fails

```bash
# Check PostgreSQL is running
docker compose ps db

# Test connection
psql $DATABASE_URL
```

### S3 Access Denied

```bash
# Verify credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://artemis-hyperliquid-data/raw/twap_statuses/ --request-payer requester
```

### ETL Errors

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m src.etl.run --incremental

# Check failed ingestions
psql $DATABASE_URL -c "SELECT * FROM etl_s3_ingest_log WHERE error_text IS NOT NULL;"
```

### API Returns Empty

```bash
# Verify data exists
psql $DATABASE_URL -c "SELECT COUNT(*) FROM twap_status WHERE wallet='0xabc123';"

# Check timestamp format (must be UTC ISO 8601)
# Correct: 2025-11-01T00:00:00Z
```

---

## Documentation

### User Guides

- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[API Reference](docs/API.md)** - Complete REST API documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production setup
- **[Alembic Guide](docs/ALEMBIC_GUIDE.md)** - Database migrations
- **[Contributing](docs/CONTRIBUTING.md)** - Development workflow

### Implementation Notes

- **[Improvements Log](docs/implementation/improvements.md)** - All enhancements
- **[Code Review](docs/implementation/review-summary.md)** - Architecture assessment
- **[Implementation Notes](docs/implementation/implementation-notes.md)** - Feature details

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/repo/discussions)
- **Documentation**: [docs/](docs/)

---

<div align="center">

**Production-Ready v2.0** | **MIT Licensed** | **Built for Hyperliquid**

[Documentation](docs/) · [API Reference](docs/API.md) · [Quick Start](QUICKSTART.md)

</div>
