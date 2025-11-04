# Quick Start Guide

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Get the Hyperliquid TWAP Data Service running in 5 minutes.

**Version**: Production-Ready v2.0

---

## Prerequisites

- ✅ Docker and Docker Compose installed
- ✅ Python 3.11+ (for local development)
- ✅ PostgreSQL 14+ (or use Docker)
- ✅ AWS credentials with S3 access (for production S3 ingestion)

## Option 1: Docker Compose (Recommended)

### 1. Setup Environment

```bash
cd hyperliquid-twap
cp .env.example .env
# Edit .env if needed (AWS credentials for S3 access)
```

### 2. Start Services

```bash
docker compose up -d
```

This starts:
- PostgreSQL database on port 5432
- FastAPI server on port 8000

### 3. Initialize Database

```bash
docker compose exec api python -m src.db.init
```

**Expected output:**
```
Connecting to database at localhost:5432/hyperliquid
Creating database schema...
Database schema initialized successfully!
```

### 4. Load Sample Data

```bash
# Generate sample parquet
docker compose exec api python tests/create_sample_data.py

# Ingest sample data
docker compose exec api python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

### 5. Test API

```bash
# Health check
curl http://localhost:8000/healthz

# Query TWAPs
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z"

# View API docs
open http://localhost:8000/docs
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "last_ingested_object": "local:tests/data/sample_twap.parquet"
}
```

🎉 **Success!** Your API is running. See [docs/API.md](docs/API.md) for complete API reference.

## Option 2: Local Development

### 1. Setup Python Environment

```bash
cd hyperliquid-twap

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Database

```bash
docker compose up -d db
# Wait for database to be ready
docker compose logs -f db
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Initialize Database

```bash
python -m src.db.init
```

### 5. Create and Load Sample Data

```bash
# Generate sample parquet
python tests/create_sample_data.py

# Load into database
python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

### 6. Start API Server

```bash
uvicorn src.api.main:app --reload
```

Server runs at http://localhost:8000

### 7. Test API

```bash
# Health check
curl http://localhost:8000/healthz

# Query TWAPs
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z" | jq

# Get specific TWAP
curl http://localhost:8000/api/v1/twaps/123456 | jq

# View interactive docs
open http://localhost:8000/docs
```

## Option 3: Using Makefile

If you have `make` installed:

```bash
# Install dependencies
make install

# Start Docker services
make docker-up

# Initialize database
make init-db

# Create sample data and run ETL
make run-etl

# Start API server
make run-api

# Run tests
make test
```

## Verify Installation

### 1. Check Database

```bash
docker compose exec db psql -U hyperliquid -d hyperliquid -c "SELECT COUNT(*) FROM twap_status;"
```

Should show 5 rows (from sample data).

### 2. Check API Health

```bash
curl http://localhost:8000/healthz
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "last_ingested_object": "local:tests/data/sample_twap.parquet",
  "last_ingested_at": "2025-11-04T..."
}
```

### 3. Query Sample Data

```bash
curl -s "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-05T00:00:00Z" | jq
```

Should return 2 TWAPs (IDs: 123456 and 789012).

## Next Steps

### Ingest Production Data from S3

> ⚠️ **Cost Note**: S3 bucket is requester-pays. See [README.md#cost-considerations](README.md#-cost-considerations) for cost estimates and optimization tips.

1. **Configure AWS Credentials** in `.env`:
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

2. **Run Incremental ETL**:
   ```bash
   python -m src.etl.run --incremental
   ```

   Or with date filter:
   ```bash
   python -m src.etl.run --since 2025-11-01T00:00:00Z
   ```

### Schedule Daily ETL

Add to crontab:
```bash
crontab -e
```

Add line:
```cron
30 0 * * * cd /path/to/hyperliquid-twap && /path/to/venv/bin/python -m src.etl.run --incremental >> logs/etl.log 2>&1
```

### Deploy to Production

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Systemd service setup
- Nginx reverse proxy
- HTTPS with Let's Encrypt
- Monitoring and backups
- Scaling strategies

## Common Commands

```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart

# Access database
docker compose exec db psql -U hyperliquid -d hyperliquid

# Run tests
pytest -v

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

## Troubleshooting

### Database Connection Failed

```bash
# Check database is running
docker compose ps

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### API Not Starting

```bash
# Check logs
docker compose logs api

# Check port availability
lsof -i :8000

# Restart API
docker compose restart api
```

### ETL Errors

```bash
# Check AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://artemis-hyperliquid-data/raw/twap_statuses/ --request-payer requester

# Run ETL with debug logging
LOG_LEVEL=DEBUG python -m src.etl.run --local-file tests/data/sample_twap.parquet
```

## API Examples

### Query with Asset Filter

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-05T00:00:00Z&asset=SOL"
```

### Get All Updates for a TWAP

```bash
curl http://localhost:8000/api/v1/twaps/123456 | jq
```

### Get All Rows (not just latest per TWAP)

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-05T00:00:00Z&latest_per_twap=false"
```

### Custom Limit

```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-05T00:00:00Z&limit=100"
```

## Interactive API Documentation

Visit http://localhost:8000/docs for:
- Interactive API explorer
- Request/response schemas
- Try-it-out functionality
- Download OpenAPI spec

## Resources

### Documentation
- [README.md](README.md) - Full documentation
- [docs/API.md](docs/API.md) - Complete API reference
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment guide
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - Development guidelines
- [docs/ALEMBIC_GUIDE.md](docs/ALEMBIC_GUIDE.md) - Database migrations

### API Endpoints
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **Metrics**: http://localhost:8000/metrics

## Getting Help

- **Troubleshooting**: See [README.md#troubleshooting](README.md#-troubleshooting)
- **Check logs**: `docker compose logs -f`
- **Common issues**: Review [README.md#troubleshooting](README.md#-troubleshooting) section
- **Open issue**: Include error messages, logs, and environment details

---

## See Also

- 📖 [Complete API Documentation](docs/API.md)
- 🚀 [Production Deployment Guide](docs/DEPLOYMENT.md)
- 💰 [Cost Considerations](README.md#-cost-considerations)
- 🔧 [Troubleshooting Guide](README.md#-troubleshooting)
