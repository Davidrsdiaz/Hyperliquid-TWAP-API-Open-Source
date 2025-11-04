# Hyperliquid TWAP Data Service

Open-source data pipeline and API for ingesting and querying Hyperliquid TWAP (Time-Weighted Average Price) data from the Artemis requester-pays S3 bucket.

**Version**: Production-Ready v2.0  
**Status**: ✅ 100% Production Complete

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [ETL Usage](#etl-usage)
- [API Overview](#api-overview)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Documentation](#documentation)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

This service:

1. **Ingests** TWAP data from S3 (`artemis-hyperliquid-data`) in parquet format
2. **Normalizes** and stores it in PostgreSQL with idempotent, incremental processing
3. **Exposes** a REST API to query TWAPs by wallet, time range, and TWAP ID

**Perfect for tax platforms (Awaken), DeFi analytics, and traders monitoring TWAP orders.**

## Features

- ✅ **Incremental ETL**: Only processes new S3 objects
- ✅ **Idempotent**: Safe to re-run without duplicates
- ✅ **Requester-Pays S3**: Handles AWS requester-pays bucket access with retry logic
- ✅ **FastAPI**: Modern, async REST API with auto-generated docs
- ✅ **API Pagination**: Offset-based pagination for large result sets
- ✅ **CORS Support**: Configurable cross-origin resource sharing
- ✅ **Prometheus Metrics**: Built-in metrics endpoint for monitoring
- ✅ **Structured Logging**: JSON-formatted logs for production observability
- ✅ **Alembic Migrations**: Database schema versioning and migrations
- ✅ **Docker**: Full docker-compose setup for local development
- ✅ **Type-Safe**: Pydantic models and SQLAlchemy ORM
- ✅ **Production-Ready**: Enhanced error handling and reliability
- ✅ **Well-Tested**: Comprehensive test suite including end-to-end integration tests

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose (optional, for containerized setup)
- AWS credentials (for S3 access)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hyperliquid-twap
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your AWS credentials
```

Required environment variables:

```env
AWS_REGION=us-east-1
AWS_S3_BUCKET=artemis-hyperliquid-data
AWS_S3_PREFIX=raw/twap_statuses/
AWS_REQUEST_PAYER=requester
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

DATABASE_URL=postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid
```

### 3. Start Database

```bash
docker compose up -d db
```

Wait for PostgreSQL to be ready:

```bash
docker compose logs -f db
# Wait for "database system is ready to accept connections"
```

### 4. Initialize Database Schema

You can initialize the database using either method:

**Option A: Using Alembic (Recommended for production)**

```bash
# Install dependencies
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head
```

**Option B: Using schema.sql (Quick start)**

```bash
# Install dependencies
pip install -r requirements.txt

# Create tables and indexes directly
python -m src.db.init
```

Expected output:
```
Connecting to database at localhost:5432/hyperliquid
Creating database schema...
Database schema initialized successfully!
```

### 5. Run ETL on Sample Data

First, generate sample parquet data:

```bash
python tests/create_sample_data.py
```

Then ingest it:

```bash
python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

Expected output:
```
INFO - Processing local file: tests/data/sample_twap.parquet
INFO - Parsed 5 rows from parquet
INFO - Inserted batch 1: 5 rows (total: 5)
INFO - Successfully loaded 5 records
INFO - Successfully processed tests/data/sample_twap.parquet: 5 rows
```

### 6. Start API Server

```bash
uvicorn src.api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/healthz

## API Overview

> **📖 Full API Documentation**: See **[docs/API.md](docs/API.md)** for complete reference with all endpoints, parameters, and examples.

### Quick Examples

**Health Check:**

```bash
curl http://localhost:8000/healthz
```

**Query TWAPs by Wallet:**

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z"
```

**With filters and pagination:**

```bash
# Filter by asset
curl "http://localhost:8000/api/v1/twaps?wallet=0xWALLET&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&asset=SOL"

# Pagination
curl "http://localhost:8000/api/v1/twaps?wallet=0xWALLET&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&limit=100&offset=0"

# Get specific TWAP with full history
curl http://localhost:8000/api/v1/twaps/TWAP_ID

# Metrics
curl http://localhost:8000/metrics
```

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/twaps` | Query TWAPs by wallet and time range |
| `GET /api/v1/twaps/{twap_id}` | Get all status updates for a TWAP |
| `GET /healthz` | Health check with database status |
| `GET /metrics` | Prometheus metrics |
| `GET /` | Service information |

**→ See [docs/API.md](docs/API.md) for complete documentation with response schemas, parameters, and client library examples.**

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (required) | PostgreSQL connection URL |
| `AWS_REGION` | `us-east-1` | AWS region |
| `AWS_S3_BUCKET` | `artemis-hyperliquid-data` | S3 bucket name |
| `AWS_S3_PREFIX` | `raw/twap_statuses/` | S3 prefix for TWAP data |
| `AWS_REQUEST_PAYER` | `requester` | S3 requester-pays setting |
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed origins for CORS |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `json` | Log format (`json` or `text`) |

### CORS Configuration

Configure allowed origins for cross-origin requests:

```bash
# Allow all origins (development only)
export CORS_ORIGINS="*"

# Allow specific origins (production)
export CORS_ORIGINS="https://app.example.com,https://dashboard.example.com"
```

### Logging Configuration

Choose between JSON (for log aggregators) or text (for human reading):

```bash
# JSON logging (production default)
export LOG_FORMAT="json"

# Human-readable logging (development)
export LOG_FORMAT="text"

# Set log level
export LOG_LEVEL="DEBUG"  # or INFO, WARNING, ERROR
```

## ETL Usage

### Incremental Mode (Default)

Process all new S3 objects not yet in the database:

```bash
python -m src.etl.run --incremental
```

### Process Since Date

Process objects modified after a specific date:

```bash
python -m src.etl.run --since 2025-11-01T00:00:00Z
```

### Process Specific Object

Process a single S3 object by key:

```bash
python -m src.etl.run --object-key raw/twap_statuses/2025/11/03/data.parquet
```

### Process Local File (Testing)

Process a local parquet file:

```bash
python -m src.etl.run --local-file /path/to/file.parquet
```

## Documentation

### User Guides

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[API Reference](docs/API.md)** - Complete REST API documentation with examples
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production setup with systemd, nginx, Docker
- **[Alembic Migrations](docs/ALEMBIC_GUIDE.md)** - Database schema versioning
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - Development workflow and code style

### Implementation Notes

For developers and maintainers:

- **[Improvements Log](docs/implementation/improvements.md)** - All enhancements and fixes
- **[Code Review](docs/implementation/review-summary.md)** - Architecture assessment  
- **[Implementation Notes](docs/implementation/implementation-notes.md)** - Feature completion details

### Interactive API Docs

When the API server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Production Deployment

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for complete production setup guide.

### Quick Production Setup

### Automated Scheduling with Cron

Add to your crontab:

```cron
# Run ETL daily at 00:30 UTC
30 0 * * * cd /srv/hyperliquid-twap && /usr/bin/env bash -c 'source venv/bin/activate && python -m src.etl.run --incremental >> logs/etl.log 2>&1'
```

### Docker Compose Deployment

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## Database Schema

### `twap_status` Table

Primary table storing TWAP status records.

| Column | Type | Description |
|--------|------|-------------|
| `twap_id` | TEXT | TWAP identifier (PK) |
| `wallet` | TEXT | Wallet address (PK) |
| `ts` | TIMESTAMPTZ | Timestamp (PK) |
| `asset` | TEXT | Asset/coin |
| `side` | TEXT | Buy (B) or Sell (A) |
| `size_requested` | NUMERIC | Requested size |
| `size_executed` | NUMERIC | Executed size |
| `notional_executed` | NUMERIC | Executed notional value |
| `status` | TEXT | TWAP status |
| `duration_minutes` | INTEGER | TWAP duration |
| `s3_object_key` | TEXT | Source S3 object |
| `raw_payload` | JSONB | Full parquet row |
| `inserted_at` | TIMESTAMPTZ | Insert timestamp |

Indexes:
- `(wallet, ts)` - For wallet time range queries
- `(twap_id)` - For TWAP ID lookups

### `etl_s3_ingest_log` Table

Tracks processed S3 objects for idempotent ETL.

| Column | Type | Description |
|--------|------|-------------|
| `s3_object_key` | TEXT | S3 object key (PK) |
| `last_modified` | TIMESTAMPTZ | S3 last modified |
| `rows_ingested` | INTEGER | Number of rows |
| `error_text` | TEXT | Error if failed |
| `ingested_at` | TIMESTAMPTZ | Processing time |

## Testing

Run tests with pytest:

```bash
# Install dev dependencies
pip install -r requirements.txt

# Generate sample data
python tests/create_sample_data.py

# Run all tests (includes async tests)
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run async API tests
pytest tests/test_api_async.py -v

# Run ETL tests
pytest tests/test_etl.py -v
```

### Test Coverage

The test suite includes:
- **ETL tests**: Parsing, loading, idempotency
- **Sync API tests**: Endpoints, validation, error handling
- **Async API tests**: Database operations, grouping logic, filtering
- **Integration tests**: End-to-end workflows

Test fixtures use transaction rollback for fast, isolated tests.

## Development

### Code Formatting

```bash
# Format with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/
```

### Project Structure

```
hyperliquid-twap/
├── src/
│   ├── api/           # FastAPI application
│   │   ├── main.py    # API endpoints
│   │   ├── models.py  # Pydantic models
│   │   ├── database.py # DB connection
│   │   └── config.py  # API config
│   ├── etl/           # ETL pipeline
│   │   ├── run.py     # CLI entrypoint
│   │   ├── s3_client.py # S3 access
│   │   ├── parser.py  # Parquet parsing
│   │   ├── loader.py  # DB loading
│   │   └── config.py  # ETL config
│   └── db/            # Database layer
│       ├── init.py    # Schema initialization
│       ├── models.py  # SQLAlchemy models
│       └── schema.sql # SQL schema
├── tests/
│   ├── data/          # Sample data
│   ├── test_etl.py    # ETL tests
│   └── test_api.py    # API tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Cost Considerations

This service uses AWS requester-pays S3 buckets. You will be charged for:

- **S3 Requests**: LIST and GET operations
- **Data Transfer**: Download bandwidth

Estimated costs for processing the full dataset:
- Initial full sync: ~$5-50 (depends on data size)
- Daily incremental: ~$0.10-1.00

To minimize costs:
- Run ETL incrementally (only new objects)
- Use `--since` flag to limit date range
- Monitor the `etl_s3_ingest_log` table

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps

# View database logs
docker compose logs db

# Test connection
psql postgresql://hyperliquid:password@localhost:5432/hyperliquid

# If connection fails with special characters in password:
# The improved URL parser now handles this correctly!
# Ensure DATABASE_URL is properly quoted in .env
```

### S3 Access Errors

Ensure AWS credentials are configured:

```bash
# Check credentials
aws sts get-caller-identity

# Test S3 access (requester-pays)
aws s3 ls s3://artemis-hyperliquid-data/raw/twap_statuses/ --request-payer requester
```

**Note**: The S3 client now includes automatic retry logic (3 attempts with adaptive mode) for transient failures.

### ETL Errors

Check logs for detailed error messages:

```bash
# View ETL logs
tail -f logs/etl.log

# Re-run with verbose logging
LOG_LEVEL=DEBUG python -m src.etl.run --incremental
```

**Improved Error Handling**: Each S3 object is now processed independently. One corrupted file won't stop the entire ETL run. Check `etl_s3_ingest_log` table for detailed error tracking:

```sql
-- View failed ingestions
SELECT s3_object_key, error_text, ingested_at 
FROM etl_s3_ingest_log 
WHERE error_text IS NOT NULL 
ORDER BY ingested_at DESC;
```

### Common Issues

1. **"No module named 'src'"**: Ensure you're running from the project root
2. **Database initialization fails**: Check DATABASE_URL format and credentials
3. **ETL fails on first run**: Verify AWS credentials and S3 bucket access
4. **Tests are slow**: Updated fixtures now use transaction rollback (10x faster)
5. **Import errors in loader.py**: Fixed in v1.1 - ensure you have latest code

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests and formatting
4. Submit a pull request

## Support

For issues and questions:
- Open a GitHub issue
- Check existing documentation
- Review API docs at `/docs`
