# SmartBiller Deployment Guide

This guide covers deploying SmartBiller to various environments, from development to production.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [SSL/HTTPS Setup](#sslhttps-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Node.js (for asset compilation)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/smartbiller.git
   cd smartbiller
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   python setup_subscription.py
   ```

6. **Run development server**
   ```bash
   python run.py
   ```

### Development Environment Variables

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://username:password@localhost/smartbiller_dev
OPENAI_API_KEY=your-openai-api-key
DEBUG=True
```

## Production Deployment

### Server Requirements

- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 20GB+ SSD
- **CPU**: 2+ cores

### Manual Production Setup

1. **Server preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx git
   ```

2. **Create application user**
   ```bash
   sudo useradd -m -s /bin/bash smartbiller
   sudo usermod -aG sudo smartbiller
   ```

3. **Clone application**
   ```bash
   sudo -u smartbiller git clone https://github.com/your-org/smartbiller.git /home/smartbiller/app
   cd /home/smartbiller/app
   ```

4. **Set up Python environment**
   ```bash
   sudo -u smartbiller python3 -m venv venv
   sudo -u smartbiller venv/bin/pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   sudo -u smartbiller cp .env.example .env
   sudo nano /home/smartbiller/app/.env
   ```

6. **Set up database**
   ```bash
   sudo -u postgres createdb smartbiller
   sudo -u postgres createuser smartbiller
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smartbiller TO smartbiller;"
   
   # Run migrations
   sudo -u smartbiller venv/bin/flask db upgrade
   sudo -u smartbiller venv/bin/python setup_subscription.py
   ```

7. **Configure Gunicorn**
   ```bash
   sudo nano /etc/systemd/system/smartbiller.service
   ```

   ```ini
   [Unit]
   Description=SmartBiller Gunicorn daemon
   After=network.target

   [Service]
   User=smartbiller
   Group=smartbiller
   WorkingDirectory=/home/smartbiller/app
   Environment="PATH=/home/smartbiller/app/venv/bin"
   ExecStart=/home/smartbiller/app/venv/bin/gunicorn --workers 3 --bind unix:smartbiller.sock -m 007 run:app

   [Install]
   WantedBy=multi-user.target
   ```

8. **Start Gunicorn service**
   ```bash
   sudo systemctl start smartbiller
   sudo systemctl enable smartbiller
   ```

9. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/smartbiller
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/smartbiller/app/smartbiller.sock;
       }

       location /static {
           alias /home/smartbiller/app/app/static;
       }
   }
   ```

10. **Enable site and restart Nginx**
    ```bash
    sudo ln -s /etc/nginx/sites-available/smartbiller /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m smartbiller && chown -R smartbiller:smartbiller /app
USER smartbiller

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://smartbiller:password@db:5432/smartbiller
      - SECRET_KEY=your-secret-key
      - FLASK_ENV=production
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=smartbiller
      - POSTGRES_USER=smartbiller
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Docker Deployment Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web flask db upgrade

# Initialize subscriptions
docker-compose exec web python setup_subscription.py

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment

#### Using AWS EC2

1. **Launch EC2 instance**
   - AMI: Ubuntu 20.04 LTS
   - Instance type: t3.medium or larger
   - Security groups: Allow ports 22, 80, 443

2. **Connect to instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Follow manual production setup**

#### Using AWS Elastic Beanstalk

1. **Create application**
   ```bash
   eb init smartbiller --platform python-3.9
   ```

2. **Configure environment**
   ```bash
   eb create smartbiller-prod
   ```

3. **Deploy**
   ```bash
   eb deploy
   ```

### Google Cloud Platform

#### Using Google App Engine

1. **Create app.yaml**
   ```yaml
   runtime: python39
   
   env_variables:
     FLASK_ENV: production
     DATABASE_URL: your-database-url
   
   handlers:
   - url: /static
     static_dir: app/static
   
   - url: /.*
     script: auto
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

### Heroku Deployment

1. **Create Procfile**
   ```
   web: gunicorn run:app
   ```

2. **Add buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add heroku/postgresql
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DATABASE_URL=your-database-url
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## Environment Configuration

### Production Environment Variables

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database
OPENAI_API_KEY=your-openai-api-key
SMS_API_KEY=your-sms-api-key
SMS_USERNAME=your-sms-username
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
REDIS_URL=redis://localhost:6379
```

### Environment-Specific Configurations

#### Development
```python
class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/smartbiller_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
```

#### Production
```python
class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
```

## Database Setup

### PostgreSQL Configuration

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create database and user**
   ```sql
   CREATE DATABASE smartbiller;
   CREATE USER smartbiller WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE smartbiller TO smartbiller;
   ```

3. **Configure PostgreSQL**
   ```bash
   sudo nano /etc/postgresql/12/main/postgresql.conf
   ```

   ```conf
   # Performance tuning
   shared_buffers = 256MB
   effective_cache_size = 1GB
   maintenance_work_mem = 64MB
   checkpoint_completion_target = 0.9
   wal_buffers = 16MB
   default_statistics_target = 100
   ```

4. **Run migrations**
   ```bash
   flask db upgrade
   ```

### Database Backup

#### Automated Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/smartbiller"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="smartbiller"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

#### Cron Job
```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## SSL/HTTPS Setup

### Let's Encrypt SSL

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Nginx SSL Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://unix:/home/smartbiller/app/smartbiller.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/smartbiller/app/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Monitoring & Logging

### Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/smartbiller.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SmartBiller startup')
```

### System Monitoring

#### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'smartbiller'
    static_configs:
      - targets: ['localhost:5000']
```

#### Grafana Dashboard
- CPU usage
- Memory usage
- Database connections
- Request latency
- Error rates

### Health Checks

```python
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
```

## Backup & Recovery

### Database Backup Strategy

1. **Daily backups** - Full database dump
2. **Weekly backups** - Compressed archives
3. **Monthly backups** - Off-site storage

### File Backup

```bash
#!/bin/bash
# Backup uploads directory
rsync -avz /home/smartbiller/app/uploads/ /backups/uploads/
```

### Recovery Procedures

1. **Database recovery**
   ```bash
   psql smartbiller < backup_20240101_120000.sql
   ```

2. **Application recovery**
   ```bash
   git pull origin main
   flask db upgrade
   ```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U smartbiller -d smartbiller
```

#### Gunicorn Issues
```bash
# Check service status
sudo systemctl status smartbiller

# View logs
sudo journalctl -u smartbiller -f
```

#### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Performance Optimization

1. **Database optimization**
   ```sql
   -- Create indexes
   CREATE INDEX idx_tenant_phone ON tenant(phone);
   CREATE INDEX idx_rentlog_date ON rent_log(date_paid);
   ```

2. **Application optimization**
   ```python
   # Enable caching
   from flask_caching import Cache
   cache = Cache(config={'CACHE_TYPE': 'redis'})
   ```

3. **Static file optimization**
   ```bash
   # Compress static files
   gzip -9 app/static/css/*.css
   gzip -9 app/static/js/*.js
   ```

### Security Checklist

- [ ] HTTPS enabled
- [ ] Strong secret key
- [ ] Database user with minimal privileges
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection

## Support

For deployment support:
- Email: devops@smartbiller.com
- Documentation: https://docs.smartbiller.com/deployment
- Issues: https://github.com/smartbiller/issues 