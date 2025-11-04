# Documentation

Technical guides and reference documentation for the Hyperliquid TWAP Data Service.

## 📖 User Guides

- **[API.md](API.md)** - Complete REST API reference
  - All endpoints with examples
  - Query parameters and responses
  - Client library examples (Python, JavaScript)
  - Best practices

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
  - Server setup (systemd, nginx, HTTPS)
  - Docker deployment
  - Monitoring and backups
  - Scaling strategies

- **[ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)** - Database migrations
  - Using Alembic for schema management
  - Creating and running migrations
  - Rollback procedures
  - Comparison with schema.sql

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
  - Setup instructions
  - Code style (Black, Ruff)
  - Pull request process
  - Testing requirements

## 🔧 Implementation Notes

Internal documentation for developers and maintainers:

- **[implementation/improvements.md](implementation/improvements.md)** - Production improvements log
  - Critical fixes applied
  - Reliability enhancements
  - Performance optimizations
  - Feature additions

- **[implementation/review-summary.md](implementation/review-summary.md)** - Code review findings
  - Architecture assessment
  - Bug discoveries
  - Quality improvements
  - Best practices applied

- **[implementation/implementation-notes.md](implementation/implementation-notes.md)** - Implementation completion notes
  - Feature checklist
  - Testing results
  - Deployment verification

## 🚀 Quick Links

| Guide | Purpose | Audience |
|-------|---------|----------|
| [API.md](API.md) | REST API reference | Integrators, Frontend devs |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production setup | DevOps, SRE |
| [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) | Database migrations | Backend devs, DBA |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow | Contributors |

## 📚 Additional Resources

- **[../README.md](../README.md)** - Main project documentation
- **[../QUICKSTART.md](../QUICKSTART.md)** - 5-minute setup guide
- **[../../docs/](../../docs/)** - Historical specs and architecture docs

## 💡 Finding What You Need

**I want to...**

- **...integrate with the API** → Read [API.md](API.md)
- **...deploy to production** → Follow [DEPLOYMENT.md](DEPLOYMENT.md)
- **...modify the database schema** → See [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)
- **...contribute code** → Check [CONTRIBUTING.md](CONTRIBUTING.md)
- **...understand design decisions** → Review [implementation/](implementation/) notes
- **...get started quickly** → Go to [../QUICKSTART.md](../QUICKSTART.md)
