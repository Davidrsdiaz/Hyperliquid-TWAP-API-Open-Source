# Hyperliquid Tax Analytics (HTA-2)

Production-ready open-source tools for Hyperliquid TWAP data analysis and tax reporting.

---

## 🚀 Main Project

### **[Hyperliquid TWAP Data Service](./hyperliquid-twap/)**

ETL pipeline and REST API for querying Hyperliquid TWAPs by wallet and timeframe.

**Perfect for tax platforms like Awaken and other DeFi analytics tools.**

#### Key Features

- ✅ **Incremental S3 ingestion** from Artemis requester-pays bucket
- ✅ **PostgreSQL storage** with idempotent processing  
- ✅ **FastAPI REST API** with pagination and filtering
- ✅ **Production-ready** with monitoring, metrics, and structured logging
- ✅ **Database migrations** with Alembic
- ✅ **Comprehensive tests** including end-to-end integration tests
- ✅ **Docker deployment** with docker-compose setup

#### Quick Links

- **[Quick Start Guide →](./hyperliquid-twap/QUICKSTART.md)** - Get running in 5 minutes
- **[Full Documentation →](./hyperliquid-twap/README.md)** - Complete technical docs
- **[API Reference →](./hyperliquid-twap/docs/API.md)** - REST API documentation
- **[Deployment Guide →](./hyperliquid-twap/docs/DEPLOYMENT.md)** - Production setup

---

## 💡 Use Cases

### For Tax Platforms (Awaken, etc.)
Query complete TWAP history for any wallet and tax year:
```bash
curl "http://api.example.com/api/v1/twaps?wallet=0xWALLET&start=2025-01-01T00:00:00Z&end=2025-12-31T23:59:59Z"
```

### For DeFi Analytics
Track TWAP execution patterns, volumes, and market activity:
```bash
curl "http://api.example.com/api/v1/twaps?wallet=0xWALLET&asset=SOL&start=2025-11-01T00:00:00Z&end=2025-11-04T00:00:00Z"
```

### For Traders
Monitor your own TWAP orders with complete execution history:
```bash
curl "http://api.example.com/api/v1/twaps/TWAP_ID_123456"
```

---

## 📚 Documentation

### Project Documentation
- [hyperliquid-twap/README.md](./hyperliquid-twap/README.md) - Main documentation
- [hyperliquid-twap/docs/](./hyperliquid-twap/docs/) - Technical guides

### Archive
- [docs/](./docs/) - Historical specs and implementation notes

---

## 📄 License

MIT License - See [hyperliquid-twap/LICENSE](./hyperliquid-twap/LICENSE)

---

## 🤝 Contributing

This is an open-source project. Contributions welcome!

See [Contributing Guidelines](./hyperliquid-twap/docs/CONTRIBUTING.md) for development setup and PR process.
