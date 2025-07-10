#!/bin/bash

# Exit immediately on any error
set -e

# === Configuration Variables ===
DB_NAME="smartbiller"
DB_USER="smartbiller"
DB_PASSWORD="smartbiller254!"
HOST="localhost"
PORT="5432"
DOMAIN="smartbiller.co.ke"
EMAIL="admin@${DOMAIN}"

PROJECT_DIR="/home/administrator/smartbiller"   # ✅ Adjust if needed
VENV_PATH="${PROJECT_DIR}/venv/bin/activate"
FLASK_CLI_APP="${PROJECT_DIR}/manage.py"
NGINX_CONF_PATH="/etc/nginx/sites-available/${DOMAIN}"

# === PostgreSQL Setup ===
echo "Creating PostgreSQL database and user..."

sudo -i -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}'
   ) THEN
      CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;

-- Create database if not exists
DO \$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '${DB_NAME}'
   ) THEN
      CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
   END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF

echo ""
echo "✅ PostgreSQL user and database created."
echo "🔑 Password: ${DB_PASSWORD}"
echo "🔗 URL: postgresql://${DB_USER}:${DB_PASSWORD}@${HOST}:${PORT}/${DB_NAME}"

# === Nginx Setup ===
echo "Setting up Nginx for domain ${DOMAIN}..."
sudo chmod -R 775 /etc/nginx/sites-available

sudo bash -c "cat > ${NGINX_CONF_PATH}" <<EOL
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:5020;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOL

sudo ln -sf ${NGINX_CONF_PATH} /etc/nginx/sites-enabled/

echo "Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

# === Flask-Migrate Database Migrations ===
echo "Running Flask-Migrate database migrations..."

source "${VENV_PATH}"
export FLASK_APP="${FLASK_CLI_APP}"
export FLASK_ENV=production

cd "${PROJECT_DIR}"

if [ -d "migrations" ]; then
    flask db upgrade
    echo "✅ Tables created using Flask-Migrate."
else
    echo "❌ migrations/ folder not found. Run 'flask db init' and 'flask db migrate' before running this script."
    exit 1
fi

# === SSL Certificate via Certbot ===
echo "Installing Let's Encrypt SSL certificate..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m ${EMAIL}

echo "Restarting Nginx with SSL..."
sudo systemctl restart nginx

echo ""
echo "🎉 Deployment complete!"
echo "🔗 ${DOMAIN} is now live with SSL and your Flask app database is migrated."
