# Deployment Guide

This guide covers deploying the Hyperliquid TWAP Data Service to production.

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  S3 Bucket  │─────▶│  ETL Process │─────▶│  PostgreSQL  │
│ (Artemis)   │      │  (Scheduled) │      │   Database   │
└─────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
                                                   │
                                            ┌──────▼───────┐
                                            │  FastAPI     │
                                            │  REST API    │
                                            └──────────────┘
```

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.11+
- PostgreSQL 14+
- AWS credentials with S3 access
- Domain name (optional, for HTTPS)

## Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv postgresql postgresql-contrib nginx

# Create application user
sudo useradd -m -s /bin/bash hyperliquid
sudo su - hyperliquid
```

### 2. Application Setup

```bash
# Clone repository
cd /srv
git clone <repository-url> hyperliquid-twap
cd hyperliquid-twap

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql << EOF
CREATE USER hyperliquid WITH PASSWORD 'secure_password_here';
CREATE DATABASE hyperliquid OWNER hyperliquid;
GRANT ALL PRIVILEGES ON DATABASE hyperliquid TO hyperliquid;
EOF

# Initialize schema
python -m src.db.init
```

### 4. Environment Configuration

```bash
# Create production .env file
cat > .env << EOF
AWS_REGION=us-east-1
AWS_S3_BUCKET=artemis-hyperliquid-data
AWS_S3_PREFIX=raw/twap_statuses/
AWS_REQUEST_PAYER=requester
AWS_ACCESS_KEY_ID=your_production_key
AWS_SECRET_ACCESS_KEY=your_production_secret

DATABASE_URL=postgresql+asyncpg://hyperliquid:secure_password_here@localhost:5432/hyperliquid

API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
EOF

# Secure environment file
chmod 600 .env
```

### 5. Systemd Service (API)

Create `/etc/systemd/system/hyperliquid-api.service`:

```ini
[Unit]
Description=Hyperliquid TWAP API Service
After=network.target postgresql.service

[Service]
Type=notify
User=hyperliquid
Group=hyperliquid
WorkingDirectory=/srv/hyperliquid-twap
Environment="PATH=/srv/hyperliquid-twap/venv/bin"
ExecStart=/srv/hyperliquid-twap/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hyperliquid-api
sudo systemctl start hyperliquid-api
sudo systemctl status hyperliquid-api
```

### 6. Cron Job (ETL)

Add to crontab:

```bash
sudo crontab -e -u hyperliquid
```

Add:

```cron
# Run ETL daily at 00:30 UTC
30 0 * * * cd /srv/hyperliquid-twap && /srv/hyperliquid-twap/venv/bin/python -m src.etl.run --incremental >> /srv/hyperliquid-twap/logs/etl.log 2>&1

# Cleanup old logs monthly
0 0 1 * * find /srv/hyperliquid-twap/logs -name "*.log" -mtime +30 -delete
```

### 7. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/hyperliquid-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/hyperliquid-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Docker Deployment (Alternative)

### Using Docker Compose

```bash
# Build and start services
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose logs -f

# Update application
git pull
docker compose build
docker compose up -d
```

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: hyperliquid
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: hyperliquid
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hyperliquid"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    restart: always
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

  etl:
    build: .
    restart: "no"
    env_file: .env
    depends_on:
      - db
    command: python -m src.etl.run --incremental

volumes:
  postgres_data:
```

## Monitoring

### Application Logs

```bash
# API logs
sudo journalctl -u hyperliquid-api -f

# ETL logs
tail -f /srv/hyperliquid-twap/logs/etl.log
```

### Health Checks

```bash
# API health
curl http://localhost:8000/healthz

# Database health
sudo -u postgres psql -d hyperliquid -c "SELECT COUNT(*) FROM twap_status;"
```

### Prometheus Metrics (Optional)

Add to `requirements.txt`:
```
prometheus-fastapi-instrumentator==6.1.0
```

Update `src/api/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Backup Strategy

### Database Backups

```bash
# Create backup script
cat > /srv/hyperliquid-twap/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/srv/backups/hyperliquid
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U hyperliquid hyperliquid | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /srv/hyperliquid-twap/backup.sh

# Add to cron
0 2 * * * /srv/hyperliquid-twap/backup.sh
```

### S3 Backup (Optional)

```bash
# Sync backups to S3
aws s3 sync /srv/backups/hyperliquid s3://your-backup-bucket/hyperliquid/
```

## Security Considerations

1. **Firewall**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **PostgreSQL**
   - Use strong passwords
   - Restrict connections to localhost
   - Enable SSL for remote connections

3. **Environment Variables**
   - Never commit `.env` to version control
   - Use secrets management (AWS Secrets Manager, Vault)
   - Rotate AWS credentials regularly

4. **API Security**
   - Implement rate limiting
   - Add authentication/authorization if needed
   - Use HTTPS in production

## Scaling

### Horizontal Scaling (API)

Use multiple API workers behind a load balancer:

```bash
# Start multiple API instances
uvicorn src.api.main:app --workers 8
```

### Database Scaling

- Enable connection pooling
- Add read replicas for queries
- Implement partitioning for `twap_status` by date

### ETL Optimization

- Process S3 objects in parallel
- Increase batch size for inserts
- Use multiprocessing for large datasets

## Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u hyperliquid-api -n 50

# Test manually
cd /srv/hyperliquid-twap
source venv/bin/activate
uvicorn src.api.main:app --reload
```

### ETL Failures

```bash
# Check last ETL run
tail -50 /srv/hyperliquid-twap/logs/etl.log

# Run manually
cd /srv/hyperliquid-twap
source venv/bin/activate
python -m src.etl.run --incremental
```

### Database Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## Maintenance

### Updates

```bash
cd /srv/hyperliquid-twap
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart hyperliquid-api
```

### Database Maintenance

```bash
# Vacuum and analyze
sudo -u postgres psql -d hyperliquid -c "VACUUM ANALYZE;"

# Reindex
sudo -u postgres psql -d hyperliquid -c "REINDEX DATABASE hyperliquid;"
```

## Cost Optimization

1. **S3 Costs**
   - Run ETL less frequently if data updates are predictable
   - Use `--since` flag to limit date ranges

2. **Database**
   - Archive old data to cold storage
   - Implement data retention policies

3. **Compute**
   - Use spot instances for non-critical workloads
   - Scale API workers based on traffic

## Support

For production issues:
- Check logs first
- Review monitoring dashboards
- Open GitHub issue with logs and error messages
