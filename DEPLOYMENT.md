# SmartBiller Deployment Guide

This guide covers deploying SmartBiller to production using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git repository access
- Domain name configured (optional)

### 1. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your actual values
nano .env
```

### 2. Deploy

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 📋 Detailed Deployment Steps

### Step 1: Environment Configuration

Create your `.env` file with the following variables:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=postgresql://smartbiller:smartbiller254!@db:5432/smartbiller

# External APIs
OPENAI_API_KEY=your-openai-api-key

# SMS Configuration (Africa's Talking)
AT_USERNAME=sandbox
AT_API_KEY=your-africas-talking-api-key

# Email Configuration (if using SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Domain Configuration
DOMAIN=smartbiller.co.ke
EMAIL=admin@smartbiller.co.ke
```

### Step 2: SSL Certificate Setup

For production with SSL:

```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/smartbiller.co.ke.key \
  -out ssl/smartbiller.co.ke.crt

# For production, use Let's Encrypt
sudo certbot certonly --standalone -d smartbiller.co.ke
```

### Step 3: Database Setup

The PostgreSQL database will be automatically created by Docker Compose.

### Step 4: Deploy Application

```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Service Architecture

### Services Overview

1. **Web Application** (`smartbiller-web`)
   - Flask application with uWSGI and Nginx
   - Port: 5020 (external) → 80 (internal)

2. **Database** (`smartbiller-db`)
   - PostgreSQL 13
   - Port: 5432
   - Persistent volume: `postgres_data`

3. **Reverse Proxy** (`smartbiller-nginx`)
   - Nginx with SSL termination
   - Ports: 80, 443
   - Rate limiting and security headers

### Network Configuration

- All services communicate via `smartbiller-network`
- Database accessible only within Docker network
- Nginx handles external traffic

## 📊 Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Application logs
tail -f logs/smartbiller.log
```

### Health Checks

```bash
# Application health
curl http://localhost:5020/health

# Database connection
docker-compose exec db pg_isready -U smartbiller
```

## 🔄 Maintenance

### Database Migrations

```bash
# Run migrations
docker-compose exec web python manage.py db upgrade

# Create new migration
docker-compose exec web python manage.py db migrate -m "Description"
```

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U smartbiller smartbiller > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U smartbiller smartbiller < backup_file.sql
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🛡️ Security Considerations

### Environment Variables
- Never commit `.env` file to version control
- Use strong, unique SECRET_KEY
- Rotate API keys regularly

### Database Security
- Change default database password
- Use SSL connections in production
- Regular backups

### Network Security
- Firewall configuration
- Rate limiting enabled
- SSL/TLS encryption

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose exec db pg_isready -U smartbiller
   
   # View database logs
   docker-compose logs db
   ```

2. **Application Won't Start**
   ```bash
   # Check application logs
   docker-compose logs web
   
   # Verify environment variables
   docker-compose exec web env | grep DATABASE
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/smartbiller.co.ke.crt -text -noout
   
   # Test nginx configuration
   docker-compose exec nginx nginx -t
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_tenant_phone ON tenant(phone);
   CREATE INDEX idx_rentlog_date ON rent_log(date_paid);
   ```

2. **Caching**
   - Consider adding Redis for session storage
   - Implement application-level caching

3. **Static Files**
   - Use CDN for static assets
   - Enable gzip compression

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/smartbiller
```

### Load Balancing

Use external load balancer (HAProxy, Traefik) for multiple web instances.

## 🔍 Monitoring

### Application Metrics

- Response times
- Error rates
- Database query performance
- Memory usage

### Infrastructure Metrics

- CPU and memory usage
- Disk space
- Network traffic
- Container health

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Test database connectivity
4. Review SSL certificate configuration

## 📝 Changelog

### v1.0.0
- Initial Docker deployment setup
- PostgreSQL database integration
- Nginx reverse proxy with SSL
- Automated deployment script 