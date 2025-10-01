#!/bin/bash

# Automated Subdomain Creation Script
# Usage: ./scripts/create-subdomain.sh <project_name> <subdomain>
# Example: ./scripts/create-subdomain.sh dpp dpp

set -e

# Check arguments
if [ $# -ne 2 ]; then
    echo "❌ Usage: $0 <project_name> <subdomain>"
    echo "📝 Example: $0 dpp dpp"
    echo "📝 This will create dpp.onatltd.com subdomain"
    exit 1
fi

PROJECT_NAME=$1
SUBDOMAIN=$2
DOMAIN="onatltd.com"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "🚀 Creating subdomain configuration for ${FULL_DOMAIN}"
echo "📦 Project name: ${PROJECT_NAME}"

# Create nginx configuration
NGINX_CONF="nginx/conf.d/${PROJECT_NAME}.conf"
echo "📝 Creating nginx configuration: ${NGINX_CONF}"

cp nginx/conf.d/multi-subdomain.conf.template "${NGINX_CONF}"

# Replace placeholders
sed -i.bak "s/PROJECT_NAME/${PROJECT_NAME}/g" "${NGINX_CONF}"
sed -i.bak "s/PROJECT_SUBDOMAIN/${SUBDOMAIN}/g" "${NGINX_CONF}"

# Remove backup file
rm "${NGINX_CONF}.bak"

echo "✅ Nginx configuration created: ${NGINX_CONF}"

# Create docker-compose configuration
DOCKER_COMPOSE="docker-compose.${PROJECT_NAME}.yml"
echo "📝 Creating docker-compose configuration: ${DOCKER_COMPOSE}"

cat > "${DOCKER_COMPOSE}" << EOF
services:
  ${PROJECT_NAME}_web:
    build: .
    container_name: ${PROJECT_NAME}-web
    restart: unless-stopped
    env_file:
      - .env.${PROJECT_NAME}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - ${PROJECT_NAME}_db
      - ${PROJECT_NAME}_redis
    networks:
      - ${PROJECT_NAME}-network

  ${PROJECT_NAME}_db:
    image: postgres:15-alpine
    container_name: ${PROJECT_NAME}-db
    restart: unless-stopped
    env_file:
      - .env.${PROJECT_NAME}
    volumes:
      - ${PROJECT_NAME}_postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - ${PROJECT_NAME}-network

  ${PROJECT_NAME}_redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}-redis
    restart: unless-stopped
    volumes:
      - ${PROJECT_NAME}_redis_data:/data
    networks:
      - ${PROJECT_NAME}-network

  ${PROJECT_NAME}_nginx:
    image: nginx:alpine
    container_name: ${PROJECT_NAME}-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d/${PROJECT_NAME}.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./static:/var/www/${PROJECT_NAME}/static:ro
    depends_on:
      - ${PROJECT_NAME}_web
    networks:
      - ${PROJECT_NAME}-network

volumes:
  ${PROJECT_NAME}_postgres_data:
  ${PROJECT_NAME}_redis_data:

networks:
  ${PROJECT_NAME}-network:
    driver: bridge
EOF

echo "✅ Docker-compose configuration created: ${DOCKER_COMPOSE}"

# Create environment file template
ENV_FILE=".env.${PROJECT_NAME}"
echo "📝 Creating environment file template: ${ENV_FILE}"

cat > "${ENV_FILE}" << EOF
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-${PROJECT_NAME}-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://${PROJECT_NAME}_user:${PROJECT_NAME}_password@${PROJECT_NAME}_db:5432/${PROJECT_NAME}_db
POSTGRES_DB=${PROJECT_NAME}_db
POSTGRES_USER=${PROJECT_NAME}_user
POSTGRES_PASSWORD=${PROJECT_NAME}_password

# Redis Configuration
REDIS_URL=redis://${PROJECT_NAME}_redis:6379/0

# Domain Configuration
DOMAIN_NAME=${FULL_DOMAIN}
SSL_EMAIL=admin@${DOMAIN}

# Security Settings
ALLOWED_HOSTS=${FULL_DOMAIN},www.${FULL_DOMAIN}
CORS_ORIGINS=https://${FULL_DOMAIN},https://www.${FULL_DOMAIN}

# Monitoring & Alerts
ADMIN_EMAIL=admin@${DOMAIN}
SMTP_SERVER=smtp.${DOMAIN}
SMTP_PORT=587
SMTP_USERNAME=admin@${DOMAIN}
SMTP_PASSWORD=your-smtp-password

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
S3_BUCKET=${PROJECT_NAME}-backups
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=eu-west-1

# Application Settings
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://${PROJECT_NAME}_redis:6379/1
RATELIMIT_DEFAULT=100 per hour
RATELIMIT_LOGIN=10 per minute
RATELIMIT_API=50 per minute
EOF

echo "✅ Environment file template created: ${ENV_FILE}"

# Create deployment script
DEPLOY_SCRIPT="scripts/deploy-${PROJECT_NAME}.sh"
echo "📝 Creating deployment script: ${DEPLOY_SCRIPT}"

cat > "${DEPLOY_SCRIPT}" << EOF
#!/bin/bash

# Deployment script for ${PROJECT_NAME} (${FULL_DOMAIN})

set -e

echo "🚀 Deploying ${PROJECT_NAME} to ${FULL_DOMAIN}"

# Check if environment file exists
if [ ! -f ".env.${PROJECT_NAME}" ]; then
    echo "❌ Error: .env.${PROJECT_NAME} file not found!"
    echo "📝 Please copy and configure: cp .env.${PROJECT_NAME} .env.${PROJECT_NAME}"
    exit 1
fi

# Build and deploy
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.${PROJECT_NAME}.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking service health..."
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ ${PROJECT_NAME} is running successfully!"
    echo "🌐 Access your application at: https://${FULL_DOMAIN}"
else
    echo "❌ Health check failed. Check logs:"
    echo "docker-compose -f docker-compose.${PROJECT_NAME}.yml logs"
fi
EOF

chmod +x "${DEPLOY_SCRIPT}"
echo "✅ Deployment script created: ${DEPLOY_SCRIPT}"

echo ""
echo "🎉 Subdomain configuration completed!"
echo ""
echo "📋 Next steps:"
echo "1. 🌐 Add DNS record: ${FULL_DOMAIN} → Your VPS IP"
echo "2. ⚙️  Configure environment: nano ${ENV_FILE}"
echo "3. 🔐 Setup SSL: DOMAIN_NAME=${FULL_DOMAIN} ./scripts/ssl-setup.sh"
echo "4. 🚀 Deploy: ${DEPLOY_SCRIPT}"
echo "5. ✅ Test: curl -I https://${FULL_DOMAIN}/health"
echo ""
echo "📁 Created files:"
echo "   - ${NGINX_CONF}"
echo "   - ${DOCKER_COMPOSE}"
echo "   - ${ENV_FILE}"
echo "   - ${DEPLOY_SCRIPT}"