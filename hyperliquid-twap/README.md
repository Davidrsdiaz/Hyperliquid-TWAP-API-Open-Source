# Hyperliquid TWAP Data Service

Open-source data pipeline and API for ingesting and querying Hyperliquid TWAP (Time-Weighted Average Price) data from the Artemis requester-pays S3 bucket.

## Overview

This service:

1. **Ingests** TWAP data from S3 (`artemis-hyperliquid-data`) in parquet format
2. **Normalizes** and stores it in PostgreSQL with idempotent, incremental processing
3. **Exposes** a REST API to query TWAPs by wallet, time range, and TWAP ID

## Features

- ✅ **Incremental ETL**: Only processes new S3 objects
- ✅ **Idempotent**: Safe to re-run without duplicates
- ✅ **Requester-Pays S3**: Handles AWS requester-pays bucket access
- ✅ **FastAPI**: Modern, async REST API with auto-generated docs
- ✅ **Docker**: Full docker-compose setup for local development
- ✅ **Type-Safe**: Pydantic models and SQLAlchemy ORM

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

```bash
# Install dependencies
pip install -r requirements.txt

# Create tables and indexes
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

## API Usage

### Health Check

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "last_ingested_object": "local:tests/data/sample_twap.parquet",
  "last_ingested_at": "2025-11-04T12:00:00Z"
}
```

### Query TWAPs by Wallet

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z"
```

Response:
```json
{
  "wallet": "0xabc123def456",
  "start": "2025-11-01T00:00:00Z",
  "end": "2025-11-04T00:00:00Z",
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
      "raw": { }
    }
  ]
}
```

### Query with Asset Filter

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&asset=SOL"
```

### Get All Rows for a TWAP

```bash
curl http://localhost:8000/api/v1/twaps/123456
```

Response:
```json
{
  "twap_id": "123456",
  "rows": [
    {
      "wallet": "0xabc123def456",
      "ts": "2025-11-03T12:30:00Z",
      "status": "completed",
      "size_executed": "100.0",
      "notional_executed": "9050.00",
      "raw": { }
    },
    {
      "wallet": "0xabc123def456",
      "ts": "2025-11-03T12:15:00Z",
      "status": "executing",
      "size_executed": "25.8",
      "notional_executed": "2332.20",
      "raw": { }
    }
  ]
}
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

## Production Deployment

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

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_api.py -v
```

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
```

### S3 Access Errors

Ensure AWS credentials are configured:

```bash
# Check credentials
aws sts get-caller-identity

# Test S3 access (requester-pays)
aws s3 ls s3://artemis-hyperliquid-data/raw/twap_statuses/ --request-payer requester
```

### ETL Errors

Check logs for detailed error messages:

```bash
# View ETL logs
tail -f logs/etl.log

# Re-run with verbose logging
LOG_LEVEL=DEBUG python -m src.etl.run --incremental
```

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
