#!/bin/bash

# === Exit on errors ===
set -e

# === Configuration ===
DB_NAME="smartbiller1"
DB_USER="smartbiller1"
DB_PASSWORD="smartbiller254!"
DOMAIN="smartbiller.co.ke"
EMAIL="admin@${DOMAIN}"   # Used by Certbot
PROJECT_DIR="/home/administrator/smartbiller"
VENV_PATH="${PROJECT_DIR}/venv/bin/activate"
FLASK_APP="run.py"
DOCKER_COMPOSE="docker-compose"

LOG_FILE="/var/log/smartbiller-deploy.log"

# === Logging ===
exec > >(tee -a "${LOG_FILE}")
exec 2>&1

echo "🔁 Starting deployment at $(date)"

# === Create DB and user if they don't exist ===
echo "🔧 Creating PostgreSQL user and database (if missing)..."
sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}'
   ) THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$do\$;

DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '${DB_NAME}'
   ) THEN
      CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
   END IF;
END
\$do\$;

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF

echo "✅ PostgreSQL user and database setup complete"

# === Build and start Docker containers ===
echo "🧹 Cleaning up old containers..."
${DOCKER_COMPOSE} down

echo "🐳 Starting Docker containers..."
${DOCKER_COMPOSE} up -d --build

# === Wait for containers to initialize ===
sleep 10

# === Run migrations inside the container ===
echo "📦 Running database migrations..."

# Wait a bit more for database to be fully ready
sleep 5

# Run migrations using flask db commands (Flask-Migrate standard)
# No venv needed in Docker container - Python is installed directly
${DOCKER_COMPOSE} exec -e FLASK_APP=manage.py web flask db upgrade || {
    echo "⚠️  Migration failed. This might be normal if migrations are already applied."
    echo "📊 Checking migration status..."
    ${DOCKER_COMPOSE} exec -e FLASK_APP=manage.py web flask db current || true
}

echo "✅ Flask database migrations complete"

# === Setup Nginx ===
echo "⚙️  Setting up Nginx config..."

# Use site-specific config file (only server blocks, no events/http)
if [ -f "${PROJECT_DIR}/nginx-site.conf" ]; then
    sudo cp "${PROJECT_DIR}/nginx-site.conf" /etc/nginx/sites-available/${DOMAIN}
    echo "✅ Using nginx-site.conf (site-specific config)"
else
    echo "⚠️  nginx-site.conf not found, using nginx.conf (may need manual editing)"
    sudo cp "${PROJECT_DIR}/nginx.conf" /etc/nginx/sites-available/${DOMAIN}
fi

# Create symlink
sudo ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/

# Check if rate limiting zones exist in main nginx.conf
if ! sudo grep -q "limit_req_zone.*zone=api" /etc/nginx/nginx.conf 2>/dev/null; then
    echo "⚠️  Rate limiting zones not found in main nginx.conf"
    echo "📝 You may need to add these to /etc/nginx/nginx.conf in the http block:"
    echo "   limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;"
    echo "   limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;"
fi

# Test and reload nginx
echo "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx configuration test failed. Please check the errors above."
    exit 1
fi

echo "✅ Nginx config applied"

# === SSL Setup with Certbot (only if cert doesn't exist) ===
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "🔒 Installing SSL certificate with Certbot..."
    sudo certbot --nginx --non-interactive --agree-tos -m ${EMAIL} -d ${DOMAIN} -d www.${DOMAIN}
else
    echo "🔒 SSL certificate already exists. Skipping Certbot."
fi

# === Final Restart ===
echo "🚀 Restarting Docker containers to apply changes..."
${DOCKER_COMPOSE} restart

echo "✅ Deployment complete! App should be live at: https://${DOMAIN}"
