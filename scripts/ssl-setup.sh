#!/bin/bash

# SSL Setup Script for Zero@Design
# This script sets up Let's Encrypt SSL certificates

set -e

# Configuration
DOMAIN_NAME=${DOMAIN_NAME:-"onatltd.com"}
SSL_EMAIL=${SSL_EMAIL:-"admin@onatltd.com"}
NGINX_CONF_DIR="./nginx/conf.d"
CERTBOT_DIR="./nginx/www"
CERTS_DIR="./nginx/certs"

echo "Setting up SSL for domain: ${DOMAIN_NAME}"
echo "Email: ${SSL_EMAIL}"

# Create necessary directories
mkdir -p ${CERTBOT_DIR}
mkdir -p ${CERTS_DIR}

# Update nginx configuration with actual domain
sed -i.bak "s/onatltd.com/${DOMAIN_NAME}/g" ${NGINX_CONF_DIR}/default.conf

echo "Updated nginx configuration with domain: ${DOMAIN_NAME}"

# Start nginx for initial certificate request
echo "Starting nginx for certificate request..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
sleep 10

# Request initial certificate
echo "Requesting SSL certificate from Let's Encrypt..."
docker run --rm \
    -v ${PWD}/nginx/certs:/etc/letsencrypt \
    -v ${PWD}/nginx/www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email ${SSL_EMAIL} \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d ${DOMAIN_NAME} \
    -d www.${DOMAIN_NAME}

if [ $? -eq 0 ]; then
    echo "SSL certificate obtained successfully!"
    
    # Restart nginx with SSL configuration
    echo "Restarting nginx with SSL configuration..."
    docker-compose -f docker-compose.prod.yml restart nginx
    
    echo "SSL setup completed successfully!"
    echo "Your site should now be accessible at: https://${DOMAIN_NAME}"
else
    echo "ERROR: Failed to obtain SSL certificate"
    echo "Please check:"
    echo "1. Domain DNS is pointing to this server"
    echo "2. Port 80 is accessible from the internet"
    echo "3. Domain name is correct: ${DOMAIN_NAME}"
    exit 1
fi

# Test SSL certificate
echo "Testing SSL certificate..."
sleep 5
curl -I https://${DOMAIN_NAME}/health || echo "SSL test failed - this is normal if the app isn't fully started yet"

echo "SSL setup script completed!"
echo ""
echo "Next steps:"
echo "1. Start the full application: docker-compose -f docker-compose.prod.yml up -d"
echo "2. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "3. Visit your site: https://${DOMAIN_NAME}"