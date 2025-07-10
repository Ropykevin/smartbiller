#!/bin/bash

# Exit immediately on error
set -e

# === Configuration Variables ===
DB_NAME="smartbiller"
DB_USER="smartbiller"
DB_PASSWORD="smartbiller254!"
HOST="localhost"
PORT="5432"
DOMAIN="smartbiller.co.ke"
EMAIL="admin@${DOMAIN}"

PROJECT_DIR="/home/ubuntu/smartbiller"  # ✅ Your Flask project directory
VENV_PATH="${PROJECT_DIR}/venv/bin/activate"
FLASK_APP_FILE="wsgi.py"  # ✅ Change if your entry point is app.py, main.py, etc.
NGINX_CONF_PATH="/etc/nginx/sites-available/${DOMAIN}"

# === PostgreSQL Setup ===
echo "Creating PostgreSQL database and user..."

sudo -i -u postgres psql <<EOF
DO \$\$
BEGIN#!/bin/bash

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

PROJECT_DIR="/home/administrator/smartbiller"   # ✅ Update this if project path changes
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

# Activate virtual environment
source "${VENV_PATH}"

# Set environment variables
export FLASK_APP="${FLASK_CLI_APP}"
export FLASK_ENV=production

# Navigate to project directory
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

   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}') THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;

CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF

echo ""
echo "✅ PostgreSQL user and database created."
echo "🔑 Password: ${DB_PASSWORD}"
echo "🔗 URL: postgresql://${DB_USER}:${DB_PASSWORD}@${HOST}:${PORT}/${DB_NAME}"

# === Nginx Configuration ===
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

# === Flask Migrations ===
echo "Running Flask-Migrate database migrations..."

# Activate virtualenv
source "${VENV_PATH}"

# Set Flask app context
export FLASK_APP="${PROJECT_DIR}/${FLASK_APP_FILE}"
export FLASK_ENV=production

cd "${PROJECT_DIR}"

if [ -d "migrations" ]; then
    flask db upgrade
    echo "✅ Tables created using Flask-Migrate."
else
    echo "❌ migrations/ folder not found. Run 'flask db init' and 'flask db migrate' first."
    exit 1
fi

# === SSL with Certbot ===
echo "Installing SSL certificate for ${DOMAIN}..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m ${EMAIL}

echo "Restarting Nginx with SSL..."
sudo systemctl restart nginx

echo ""
echo "🎉 Deployment complete! ${DOMAIN} is live with SSL and DB migrations applied."
