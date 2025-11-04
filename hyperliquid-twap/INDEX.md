# Hyperliquid TWAP Data Service - Documentation Index

Welcome! This index will help you navigate the complete documentation for the Hyperliquid TWAP Data Service.

---

## 🚀 Getting Started

**New to this project?** Start here:

1. **[QUICKSTART.md](QUICKSTART.md)** ⭐
   - 5-minute setup guide
   - Three setup options (Docker, Local, Makefile)
   - Sample commands and verification steps
   - **Start here if you want to run the service quickly**

2. **[README.md](README.md)** 📖
   - Complete project overview
   - Features and architecture
   - Detailed setup instructions
   - API usage examples
   - Database schema documentation
   - **Read this for comprehensive understanding**

---

## 📚 Core Documentation

### For Developers

- **[CONTRIBUTING.md](CONTRIBUTING.md)**
  - Development setup
  - Code style guidelines (Black, Ruff)
  - Pull request process
  - Testing requirements

### For Operations/DevOps

- **[DEPLOYMENT.md](DEPLOYMENT.md)**
  - Production deployment guide
  - Systemd service configuration
  - Nginx reverse proxy setup
  - Let's Encrypt HTTPS
  - Monitoring and backups
  - Scaling strategies
  - Docker deployment options

---

## 🔧 Technical Reference

### Source Code Documentation

#### Database Layer (`src/db/`)
- **`schema.sql`** - Complete PostgreSQL schema DDL
- **`models.py`** - SQLAlchemy ORM models with type hints
- **`init.py`** - Database initialization script

#### ETL Pipeline (`src/etl/`)
- **`s3_client.py`** - S3 client with requester-pays support
- **`parser.py`** - Parquet parser and data normalizer
- **`loader.py`** - Database batch loader
- **`run.py`** - CLI entrypoint with argument parsing
- **`config.py`** - ETL configuration

#### API Application (`src/api/`)
- **`main.py`** - FastAPI app and endpoints
- **`models.py`** - Pydantic request/response models
- **`database.py`** - Async database connection
- **`config.py`** - API configuration

#### Tests (`tests/`)
- **`test_etl.py`** - ETL pipeline tests
- **`test_api.py`** - API endpoint tests
- **`conftest.py`** - Pytest fixtures
- **`create_sample_data.py`** - Sample data generator

---

## 📋 Configuration Files

### Environment & Setup
- **`.env.example`** - Environment variables template
- **`requirements.txt`** - Python dependencies (pinned versions)
- **`pyproject.toml`** - Black & Ruff configuration

### Docker
- **`Dockerfile`** - Container image definition
- **`docker-compose.yml`** - Multi-service orchestration
- **`.dockerignore`** - Docker ignore patterns

### Development Tools
- **`Makefile`** - Common development tasks
- **`.github/workflows/ci.yml`** - CI/CD pipeline

---

## 🎯 Common Use Cases

### I want to...

**...run the service locally for development**
→ See [QUICKSTART.md § Option 2: Local Development](QUICKSTART.md#option-2-local-development)

**...deploy to production**
→ See [DEPLOYMENT.md § Production Setup](DEPLOYMENT.md#production-setup)

**...understand the API**
→ Run the service and visit http://localhost:8000/docs
→ Or see [README.md § API Usage](README.md#api-usage)

**...run the ETL from S3**
→ See [README.md § ETL Usage](README.md#etl-usage)
→ Configure AWS credentials in `.env`

**...add a new feature**
→ See [CONTRIBUTING.md](CONTRIBUTING.md)
→ Follow the development setup and PR process

**...understand the database schema**
→ See [README.md § Database Schema](README.md#database-schema)
→ Or read `src/db/schema.sql` directly

**...run tests**
→ See [README.md § Testing](README.md#testing)

**...troubleshoot issues**
→ See [QUICKSTART.md § Troubleshooting](QUICKSTART.md#troubleshooting)
→ See [DEPLOYMENT.md § Troubleshooting](DEPLOYMENT.md#troubleshooting)

---

## 📖 API Documentation

### Live Documentation
When the API is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints

1. **`GET /api/v1/twaps`**
   - Query TWAPs by wallet and time range
   - Supports filtering, grouping, and pagination
   - See [README.md § Query TWAPs by Wallet](README.md#query-twaps-by-wallet)

2. **`GET /api/v1/twaps/{twap_id}`**
   - Get all rows for a specific TWAP ID
   - Returns complete history
   - See [README.md § Get All Rows for a TWAP](README.md#get-all-rows-for-a-twap)

3. **`GET /healthz`**
   - Health check endpoint
   - Returns DB status and last ingested object
   - See [README.md § Health Check](README.md#health-check)

---

## 🗂️ File Organization

```
hyperliquid-twap/
├── 📚 Documentation
│   ├── INDEX.md (this file)
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
├── 💻 Source Code
│   ├── src/db/         # Database layer
│   ├── src/etl/        # ETL pipeline
│   └── src/api/        # FastAPI app
│
├── 🧪 Tests
│   ├── tests/data/     # Sample data
│   └── tests/*.py      # Test suites
│
├── 🐳 Docker
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── ⚙️ Configuration
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Makefile
│
└── 🔄 CI/CD
    └── .github/workflows/ci.yml
```

---

## 🎓 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md) - Understand basic usage
2. Run the service locally with sample data
3. Explore the API at http://localhost:8000/docs
4. Try different API queries

### Intermediate
1. Read [README.md](README.md) - Understand architecture
2. Review `src/db/schema.sql` - Learn the data model
3. Review `src/etl/run.py` - Understand ETL flow
4. Review `src/api/main.py` - Understand API endpoints
5. Run tests: `pytest -v`

### Advanced
1. Read [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow
3. Study the database models and queries
4. Explore scaling and optimization strategies
5. Consider adding new features

---

## 📊 Key Concepts

### ETL Pipeline
- **Incremental**: Only processes new S3 objects
- **Idempotent**: Safe to re-run without duplicates
- **Requester-Pays**: All S3 calls include `RequestPayer='requester'`
- **Batch Processing**: Inserts 1000 rows at a time

### Database Schema
- **Primary Key**: `(twap_id, wallet, ts)` ensures uniqueness
- **Indexes**: Optimized for wallet queries and TWAP lookups
- **JSONB**: Full parquet row stored for forward compatibility

### API Design
- **Async**: Uses asyncpg for high performance
- **Type-Safe**: Pydantic models for validation
- **Grouped**: Returns latest status per TWAP by default
- **Documented**: Auto-generated OpenAPI docs

---

## 🔗 Quick Links

| Link | Description |
|------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [README.md](README.md) | Complete documentation |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development guidelines |
| [src/db/schema.sql](src/db/schema.sql) | Database schema |
| [requirements.txt](requirements.txt) | Python dependencies |
| [docker-compose.yml](docker-compose.yml) | Docker setup |
| [Makefile](Makefile) | Development commands |

---

## 💡 Tips

- **First time?** Start with [QUICKSTART.md](QUICKSTART.md)
- **Want to understand everything?** Read [README.md](README.md)
- **Ready to deploy?** Follow [DEPLOYMENT.md](DEPLOYMENT.md)
- **Want to contribute?** Check [CONTRIBUTING.md](CONTRIBUTING.md)
- **Need help?** Check the troubleshooting sections in each guide

---

## 📞 Support

- **Documentation Issues**: Check this index for the right guide
- **Setup Problems**: See troubleshooting in [QUICKSTART.md](QUICKSTART.md)
- **Production Issues**: See [DEPLOYMENT.md § Troubleshooting](DEPLOYMENT.md#troubleshooting)
- **Code Questions**: Review inline comments in source files

---

## ✅ Checklist for New Users

- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Set up local environment
- [ ] Run with sample data
- [ ] Test API endpoints
- [ ] Read [README.md](README.md) for details
- [ ] Review database schema
- [ ] Understand ETL process
- [ ] (Optional) Deploy to production

---

**Happy coding! 🚀**

For the most up-to-date information, always check the individual documentation files.
