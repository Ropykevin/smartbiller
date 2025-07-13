# SmartBiller Server Deployment Guide

## 🚀 Quick Deployment for External Server

### Step 1: Prepare Environment
```bash
# Copy environment template
cp env.example .env

# Edit with your values
nano .env
```

### Step 2: Deploy
```bash
# Make script executable
chmod +x deploy-server.sh

# Run deployment
./deploy-server.sh
```

## 🔧 Alternative: Manual Deployment

If the script fails, deploy manually:

```bash
# 1. Stop any existing containers
docker compose down

# 2. Clean up
docker compose down -v
docker system prune -f

# 3. Create directories
mkdir -p logs app/static/uploads app/static/invoices app/static/receipts

# 4. Build and start
docker compose build --no-cache
docker compose up -d

# 5. Wait for database
sleep 15

# 6. Run migrations
docker compose exec web python manage.py db upgrade
```

## 🚨 Troubleshooting

### Port Already in Use
If you get "address already in use" errors:

```bash
# Check what's using the ports
sudo netstat -tulpn | grep :5432
sudo netstat -tulpn | grep :5020

# Kill processes if needed
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Check database logs
docker compose logs db

# Test database connectivity
docker compose exec db pg_isready -U smartbiller

# Reset database if needed
docker compose down -v
docker compose up -d db
```

### Application Won't Start
```bash
# Check application logs
docker compose logs web

# Check environment variables
docker compose exec web env | grep DATABASE

# Verify .env file
cat .env
```

## 📊 Monitoring

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db
```

### Check Status
```bash
# Container status
docker compose ps

# Resource usage
docker stats
```

### Health Checks
```bash
# Application health
curl http://localhost:5020/health

# Database health
docker compose exec db pg_isready -U smartbiller
```

## 🔄 Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Backup Database
```bash
# Create backup
docker compose exec db pg_dump -U smartbiller smartbiller > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker compose exec -T db psql -U smartbiller smartbiller < backup_file.sql
```

### Database Migrations
```bash
# Run migrations
docker compose exec web python manage.py db upgrade

# Create new migration
docker compose exec web python manage.py db migrate -m "Description"
```

## 🌐 Access Points

After successful deployment:

- **Web Application**: http://your-server-ip:5020
- **Database**: your-server-ip:5433
- **Logs**: `docker compose logs -f`

## 🔒 Security Notes

1. **Change default passwords** in `.env` file
2. **Use strong SECRET_KEY**
3. **Configure firewall** to allow only necessary ports
4. **Set up SSL** if using domain name
5. **Regular backups** of database

## 📞 Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f

# Access container shell
docker compose exec web bash
docker compose exec db psql -U smartbiller

# Update and redeploy
git pull && docker compose down && docker compose build --no-cache && docker compose up -d
``` 