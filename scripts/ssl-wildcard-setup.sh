#!/bin/bash

# Wildcard SSL Setup Script for *.onatltd.com
# This script sets up wildcard SSL certificates for all subdomains

set -e

# Configuration
DOMAIN_NAME=${DOMAIN_NAME:-"onatltd.com"}
SSL_EMAIL=${SSL_EMAIL:-"admin@onatltd.com"}
NGINX_CONF_DIR="./nginx/conf.d"

echo "🔐 Setting up Wildcard SSL for *.${DOMAIN_NAME}"
echo "📧 SSL Email: ${SSL_EMAIL}"

# Check if running in production environment
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod file not found. Please create it first."
    exit 1
fi

# Load environment variables
source .env.prod

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "🚀 Starting wildcard SSL certificate generation..."

# Generate wildcard SSL certificate using Certbot
docker run --rm \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /var/lib/letsencrypt:/var/lib/letsencrypt \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email ${SSL_EMAIL} \
    --agree-tos \
    --no-eff-email \
    --expand \
    -d ${DOMAIN_NAME} \
    -d *.${DOMAIN_NAME}

if [ $? -eq 0 ]; then
    echo "✅ Wildcard SSL certificate generated successfully!"
    
    # Update nginx configurations for all subdomains
    echo "🔧 Updating nginx configurations..."
    
    # Update production config
    if [ -f "${NGINX_CONF_DIR}/default.conf" ]; then
        sed -i.bak "s|/etc/letsencrypt/live/[^/]*/|/etc/letsencrypt/live/${DOMAIN_NAME}/|g" "${NGINX_CONF_DIR}/default.conf"
        echo "✅ Updated production nginx config"
    fi
    
    # Update staging config
    if [ -f "${NGINX_CONF_DIR}/staging.conf" ]; then
        sed -i.bak "s|/etc/letsencrypt/live/[^/]*/|/etc/letsencrypt/live/${DOMAIN_NAME}/|g" "${NGINX_CONF_DIR}/staging.conf"
        echo "✅ Updated staging nginx config"
    fi
    
    echo "🎉 Wildcard SSL setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Make sure DNS records are configured:"
    echo "   - A record: ${DOMAIN_NAME} → Your VPS IP"
    echo "   - A record: app.${DOMAIN_NAME} → Your VPS IP"
    echo "   - A record: staging.${DOMAIN_NAME} → Your VPS IP"
    echo "   - A record: *.${DOMAIN_NAME} → Your VPS IP (for other subdomains)"
    echo ""
    echo "2. Deploy your applications:"
    echo "   - Production: docker-compose -f docker-compose.prod.yml up -d"
    echo "   - Staging: docker-compose -f docker-compose.staging.yml up -d"
    echo ""
    echo "3. Test your domains:"
    echo "   - curl -I https://app.${DOMAIN_NAME}/health"
    echo "   - curl -I https://staging.${DOMAIN_NAME}/health"
    
else
    echo "❌ SSL certificate generation failed!"
    echo "Please check:"
    echo "1. Domain DNS is pointing to this server"
    echo "2. Port 80 is accessible from the internet"
    echo "3. No other services are using port 80"
    exit 1
fi