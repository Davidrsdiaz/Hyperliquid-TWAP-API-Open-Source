# Alembic Migration Guide

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg)](https://www.postgresql.org)

Database schema management with Alembic for the Hyperliquid TWAP Data Service.

**Version**: Production-Ready v2.0

> 📖 **Database Schema**: See [../README.md#-database-schema](../README.md#-database-schema) for table definitions and indexes.

---

## Quick Start

### Initialize Database (First Time)

```bash
# Install dependencies
pip install -r requirements.txt

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/dbname"

# Run migrations
alembic upgrade head
```

This will create:
- `twap_status` table with composite primary key (twap_id, wallet, ts)
- `etl_s3_ingest_log` table with primary key (s3_object_key)
- Three indexes on `twap_status`: wallet_ts_idx, twap_id_idx, asset_idx

## Common Operations

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

### Upgrade to Latest

```bash
alembic upgrade head
```

### Upgrade One Version

```bash
alembic upgrade +1
```

### Downgrade One Version

```bash
alembic downgrade -1
```

### Downgrade to Specific Version

```bash
alembic downgrade 001
```

### Downgrade All (Drop Everything)

```bash
alembic downgrade base
```

## Creating New Migrations

### Auto-generate Migration

```bash
# Alembic will detect changes to models.py
alembic revision --autogenerate -m "Add new column to twap_status"
```

### Create Empty Migration

```bash
alembic revision -m "Custom migration"
```

## Migration File Structure

Migrations are stored in `alembic/versions/`:

```
alembic/
├── versions/
│   └── 001_initial_schema.py    # Initial schema
├── env.py                        # Environment config
└── script.py.mako               # Template for new migrations
```

## Configuration

Alembic reads configuration from:

1. **alembic.ini** - Base configuration
2. **Environment variable** - `DATABASE_URL` (takes precedence)
3. **alembic/env.py** - Custom environment setup

### DATABASE_URL Format

Alembic automatically converts async URLs to sync:

```bash
# These are both valid
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

## Initial Migration Details

The initial migration (`001_initial_schema.py`) creates:

### twap_status Table

```sql
CREATE TABLE twap_status (
    twap_id TEXT NOT NULL,
    wallet TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    asset TEXT,
    side TEXT,
    size_requested NUMERIC,
    size_executed NUMERIC,
    notional_executed NUMERIC,
    status TEXT,
    duration_minutes INTEGER,
    s3_object_key TEXT NOT NULL,
    raw_payload JSON,
    inserted_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (twap_id, wallet, ts)
);

CREATE INDEX twap_status_wallet_ts_idx ON twap_status (wallet, ts);
CREATE INDEX twap_status_twap_id_idx ON twap_status (twap_id);
CREATE INDEX twap_status_asset_idx ON twap_status (asset);
```

### etl_s3_ingest_log Table

```sql
CREATE TABLE etl_s3_ingest_log (
    s3_object_key TEXT PRIMARY KEY,
    last_modified TIMESTAMPTZ NOT NULL,
    rows_ingested INTEGER,
    error_text TEXT,
    ingested_at TIMESTAMPTZ NOT NULL
);
```

## Comparison: Alembic vs schema.sql

### Using Alembic (Recommended)

**Pros:**
- ✅ Version control for schema changes
- ✅ Rollback capability
- ✅ Migration history tracking
- ✅ Team collaboration on schema changes
- ✅ Production-safe upgrades

**Cons:**
- ⚠️ Slightly more complex initial setup

```bash
alembic upgrade head
```

### Using schema.sql (Quick Start)

**Pros:**
- ✅ Simple, direct execution
- ✅ Good for development/testing
- ✅ No additional tools needed

**Cons:**
- ❌ No version control
- ❌ No rollback capability
- ❌ Manual schema updates required

```bash
python -m src.db.init
```

### Recommendation

- **Development/Testing**: Either method works
- **Production**: Use Alembic for schema versioning and safe migrations

## Troubleshooting

### "Can't locate revision identified by..."

The database has a different migration version than your code. Options:

```bash
# Check current version
alembic current

# Force stamp to specific version (careful!)
alembic stamp head

# Or downgrade and re-upgrade
alembic downgrade base
alembic upgrade head
```

### "Target database is not up to date"

Run migrations:

```bash
alembic upgrade head
```

### "Multiple head revisions"

You have conflicting migration branches. Resolve by:

```bash
# View branches
alembic branches

# Merge branches
alembic merge heads -m "Merge branches"
```

### Database Connection Error

Verify DATABASE_URL:

```bash
# Check environment variable
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

## Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on staging** before production
3. **Keep migrations small and focused**
4. **Never edit applied migrations** (create new ones instead)
5. **Use descriptive migration messages**
6. **Backup database** before major migrations

## Production Migration Workflow

```bash
# 1. Backup database
pg_dump -Fc $DATABASE_URL > backup_$(date +%Y%m%d).dump

# 2. Check current version
alembic current

# 3. Review pending migrations
alembic history

# 4. Run migrations
alembic upgrade head

# 5. Verify
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d twap_status"  # Describe table

# 6. If issues, rollback
alembic downgrade -1
```

## Integration with Application

The application code works with both initialization methods:

- **ETL**: Uses sync SQLAlchemy (works with both)
- **API**: Uses async SQLAlchemy (works with both)

---

## Troubleshooting

**Migration fails with connection error:**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://user:pass@host:port/dbname
```

**Can't import models:**
```bash
# Ensure you're in project root
pwd  # Should be: /path/to/hyperliquid-twap
```

**More help**: See [../README.md#-troubleshooting](../README.md#-troubleshooting)

---

## See Also

- 💾 [Database Schema](../README.md#-database-schema) - Table definitions and indexes
- 🚀 [Deployment Guide](DEPLOYMENT.md) - Production database setup
- 📖 [Main Documentation](../README.md)
- 🔧 [Alembic Docs](https://alembic.sqlalchemy.org) - Official documentation
- **Tests**: Can use either method for setup

Choose Alembic for production deployments where schema evolution and safety are priorities.
