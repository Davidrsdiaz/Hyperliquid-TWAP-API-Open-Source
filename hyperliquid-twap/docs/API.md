# API Reference

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg)](https://www.postgresql.org)

Complete REST API documentation for the Hyperliquid TWAP Data Service.

**Version**: Production-Ready v2.0

---

## Base URL

```
http://localhost:8000  # Development
https://api.yourdomain.com  # Production
```

## Interactive Documentation

When the API server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Endpoints

### 1. Health Check

**GET** `/healthz`

Check service health and database connectivity.

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "last_ingested_object": "local:tests/data/sample_twap.parquet",
  "last_ingested_at": "2025-11-04T12:00:00Z"
}
```

**Example:**
```bash
curl http://localhost:8000/healthz
```

---

### 2. Query TWAPs by Wallet

**GET** `/api/v1/twaps`

Query TWAPs by wallet address and time range with optional filtering.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `wallet` | string | ✅ Yes | - | Wallet address |
| `start` | datetime | ✅ Yes | - | Start timestamp (ISO8601) |
| `end` | datetime | ✅ Yes | - | End timestamp (ISO8601) |
| `asset` | string | ❌ No | - | Filter by asset/coin (e.g., "SOL", "ETH") |
| `latest_per_twap` | boolean | ❌ No | `true` | Return only latest row per TWAP ID |
| `limit` | integer | ❌ No | `500` | Maximum number of TWAPs (1-5000) |
| `offset` | integer | ❌ No | `0` | Number of TWAPs to skip (pagination) |

#### Response

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
      "raw": {}
    }
  ]
}
```

#### Response Fields

- `wallet` - Wallet address queried
- `start` - Start timestamp
- `end` - End timestamp
- `twaps[]` - Array of TWAP objects
  - `twap_id` - Unique TWAP identifier
  - `asset` - Asset/coin symbol
  - `side` - "B" (Buy) or "A" (Ask/Sell)
  - `status` - TWAP status (e.g., "completed", "executing", "cancelled")
  - `duration_minutes` - TWAP duration in minutes
  - `latest_ts` - Timestamp of latest status update
  - `executed.size` - Executed size (string decimal)
  - `executed.notional` - Executed notional value (string decimal)
  - `raw` - Raw parquet payload (JSONB)

#### Examples

**Basic Query:**
```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z"
```

**With Asset Filter:**
```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&asset=SOL"
```

**With Pagination (Page 1):**
```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&limit=100&offset=0"
```

**With Pagination (Page 2):**
```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&limit=100&offset=100"
```

**All Status Updates:**
```bash
curl "http://localhost:8000/api/v1/twaps?wallet=0xabc123def456&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z&latest_per_twap=false"
```

---

### 3. Get TWAP by ID

**GET** `/api/v1/twaps/{twap_id}`

Get all status update rows for a specific TWAP ID.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `twap_id` | string | ✅ Yes | TWAP identifier |

#### Response

```json
{
  "twap_id": "123456",
  "rows": [
    {
      "wallet": "0xabc123def456",
      "ts": "2025-11-03T12:30:00Z",
      "asset": "SOL",
      "side": "B",
      "size_requested": "100.0",
      "size_executed": "100.0",
      "notional_executed": "9050.00",
      "status": "completed",
      "duration_minutes": 30,
      "raw": {}
    },
    {
      "wallet": "0xabc123def456",
      "ts": "2025-11-03T12:15:00Z",
      "asset": "SOL",
      "side": "B",
      "size_requested": "100.0",
      "size_executed": "25.8",
      "notional_executed": "2332.20",
      "status": "executing",
      "duration_minutes": 30,
      "raw": {}
    }
  ]
}
```

#### Response Fields

- `twap_id` - TWAP identifier
- `rows[]` - Array of status updates (newest first)
  - `wallet` - Wallet address
  - `ts` - Timestamp of this status update
  - `asset` - Asset/coin symbol
  - `side` - "B" (Buy) or "A" (Ask/Sell)
  - `size_requested` - Requested size (string decimal)
  - `size_executed` - Executed size at this timestamp (string decimal)
  - `notional_executed` - Executed notional value (string decimal)
  - `status` - Status at this timestamp
  - `duration_minutes` - TWAP duration
  - `raw` - Raw parquet payload (JSONB)

#### Example

```bash
curl http://localhost:8000/api/v1/twaps/123456
```

#### Error Responses

**404 Not Found:**
```json
{
  "detail": "TWAP ID 123456 not found"
}
```

---

### 4. Prometheus Metrics

**GET** `/metrics`

Get Prometheus-formatted metrics for monitoring.

**Parameters:** None

**Response:** Plain text (Prometheus format)

```
# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total{endpoint="GET /api/v1/twaps"} 42
api_requests_total{endpoint="GET /healthz"} 15

# HELP api_request_duration_seconds API request duration
# TYPE api_request_duration_seconds summary
api_request_duration_seconds_count{endpoint="GET /api/v1/twaps"} 42
api_request_duration_seconds_sum{endpoint="GET /api/v1/twaps"} 1.234
api_request_duration_seconds{endpoint="GET /api/v1/twaps",quantile="0.5"} 0.025
api_request_duration_seconds{endpoint="GET /api/v1/twaps",quantile="0.95"} 0.100
api_request_duration_seconds{endpoint="GET /api/v1/twaps",quantile="0.99"} 0.250

# HELP etl_runs_total Total number of ETL runs
# TYPE etl_runs_total counter
etl_runs_total 15

# HELP etl_failures_total Total number of ETL failures
# TYPE etl_failures_total counter
etl_failures_total 0

# HELP etl_last_run_timestamp Unix timestamp of last ETL run
# TYPE etl_last_run_timestamp gauge
etl_last_run_timestamp 1730736000.0
```

#### Metrics Tracked

- `api_requests_total` - Total API requests by endpoint
- `api_request_duration_seconds` - Request duration (count, sum, p50, p95, p99)
- `etl_runs_total` - Total ETL runs
- `etl_failures_total` - Failed ETL runs
- `etl_last_run_timestamp` - Last ETL run timestamp (Unix time)

#### Example

```bash
curl http://localhost:8000/metrics
```

---

### 5. Root Info

**GET** `/`

Get basic service information.

**Parameters:** None

**Response:**
```json
{
  "service": "Hyperliquid TWAP Data Service",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/healthz",
  "metrics": "/metrics"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
Invalid query parameters or request format.

```json
{
  "detail": [
    {
      "loc": ["query", "start"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 404 Not Found
Resource not found (e.g., TWAP ID doesn't exist).

```json
{
  "detail": "TWAP ID 123456 not found"
}
```

### 500 Internal Server Error
Database or internal server error.

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. For production deployments, consider adding rate limiting via:
- API Gateway (AWS API Gateway, Kong, etc.)
- Nginx `limit_req` module
- Application-level middleware

---

## CORS

CORS is enabled and configurable via the `CORS_ORIGINS` environment variable:

```bash
# Allow all origins (development)
CORS_ORIGINS="*"

# Allow specific origins (production)
CORS_ORIGINS="https://app.example.com,https://dashboard.example.com"
```

Allowed methods: GET, POST, PUT, DELETE, OPTIONS  
Allowed headers: All

---

## Authentication

Currently no authentication is required. For production deployments, consider adding:

- API key authentication
- JWT tokens
- OAuth 2.0
- Mutual TLS

Example with API key header:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/twaps?...
```

---

## Client Libraries

### Python Example

```python
import requests
from datetime import datetime

class HyperliquidTWAPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_twaps(self, wallet, start, end, asset=None, limit=500, offset=0):
        """Query TWAPs by wallet and time range."""
        params = {
            "wallet": wallet,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "offset": offset,
        }
        if asset:
            params["asset"] = asset
        
        response = requests.get(f"{self.base_url}/api/v1/twaps", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_twap_by_id(self, twap_id):
        """Get all rows for a specific TWAP."""
        response = requests.get(f"{self.base_url}/api/v1/twaps/{twap_id}")
        response.raise_for_status()
        return response.json()

# Usage
client = HyperliquidTWAPClient()
twaps = client.get_twaps(
    wallet="0xabc123def456",
    start=datetime(2025, 11, 1),
    end=datetime(2025, 11, 4),
    asset="SOL"
)
print(f"Found {len(twaps['twaps'])} TWAPs")
```

### JavaScript Example

```javascript
class HyperliquidTWAPClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getTWAPs(wallet, start, end, options = {}) {
    const params = new URLSearchParams({
      wallet,
      start: start.toISOString(),
      end: end.toISOString(),
      limit: options.limit || 500,
      offset: options.offset || 0,
    });
    
    if (options.asset) params.append('asset', options.asset);
    
    const response = await fetch(`${this.baseUrl}/api/v1/twaps?${params}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getTWAPById(twapId) {
    const response = await fetch(`${this.baseUrl}/api/v1/twaps/${twapId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// Usage
const client = new HyperliquidTWAPClient();
const twaps = await client.getTWAPs(
  '0xabc123def456',
  new Date('2025-11-01'),
  new Date('2025-11-04'),
  { asset: 'SOL' }
);
console.log(`Found ${twaps.twaps.length} TWAPs`);
```

---

## Best Practices

1. **Use pagination** for large result sets to avoid timeouts
2. **Cache responses** when appropriate (data doesn't change frequently)
3. **Handle errors gracefully** with exponential backoff for retries
4. **Validate timestamps** are in ISO8601 format with timezone
5. **Monitor metrics** endpoint for system health

---

## Performance Considerations

> 💰 **Cost Note**: High-volume queries may increase database load. For large date ranges, use pagination. See [../README.md#-cost-considerations](../README.md#-cost-considerations) for optimization tips.

**Query optimization:**
- Use specific date ranges (avoid full-year queries)
- Set `latest_per_twap=true` to reduce result size
- Use pagination (`limit` + `offset`) for results > 1000 records
- Filter by `asset` when possible

---

## See Also

- 📖 [Main Documentation](../README.md)
- 🚀 [Quick Start Guide](../QUICKSTART.md)
- 🔧 [Deployment Guide](DEPLOYMENT.md)
- 💾 [Database Schema](../README.md#-database-schema)
- 🔧 [Troubleshooting](../README.md#-troubleshooting)
