#!/bin/bash

# Zero@Design Production Deployment Script
# This script handles the complete deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env.prod exists
    if [ ! -f "${ENV_FILE}" ]; then
        log_error "${ENV_FILE} not found. Please copy .env.prod.example to ${ENV_FILE} and configure it."
        exit 1
    fi
    
    # Check if nginx directory exists
    if [ ! -d "nginx/conf.d" ]; then
        log_error "nginx/conf.d directory not found. Please ensure nginx configuration is in place."
        exit 1
    fi
    
    log_success "All requirements met!"
}

backup_database() {
    log_info "Creating database backup before deployment..."
    
    if docker-compose -f ${COMPOSE_FILE} ps postgres | grep -q "Up"; then
        docker-compose -f ${COMPOSE_FILE} exec postgres /backup.sh || log_warning "Backup failed or no existing database"
    else
        log_warning "Database not running, skipping backup"
    fi
}

build_images() {
    log_info "Building Docker images..."
    docker-compose -f ${COMPOSE_FILE} build --no-cache
    log_success "Images built successfully!"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f ${COMPOSE_FILE} down || true
    
    # Start new containers
    log_info "Starting new containers..."
    docker-compose -f ${COMPOSE_FILE} up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_health
}

check_health() {
    log_info "Checking service health..."
    
    # Check if containers are running
    if ! docker-compose -f ${COMPOSE_FILE} ps | grep -q "Up"; then
        log_error "Some containers are not running!"
        docker-compose -f ${COMPOSE_FILE} logs
        exit 1
    fi
    
    # Check web service health
    for i in {1..10}; do
        if docker-compose -f ${COMPOSE_FILE} exec -T web curl -f http://localhost:5000/health > /dev/null 2>&1; then
            log_success "Web service is healthy!"
            break
        else
            log_info "Waiting for web service to be ready... (attempt $i/10)"
            sleep 10
        fi
        
        if [ $i -eq 10 ]; then
            log_error "Web service health check failed!"
            docker-compose -f ${COMPOSE_FILE} logs web
            exit 1
        fi
    done
    
    # Check database health
    if docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_isready -U ${POSTGRES_USER:-zero_design_user} > /dev/null 2>&1; then
        log_success "Database is healthy!"
    else
        log_error "Database health check failed!"
        docker-compose -f ${COMPOSE_FILE} logs postgres
        exit 1
    fi
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    if [ -f "scripts/ssl-setup.sh" ]; then
        ./scripts/ssl-setup.sh
    else
        log_warning "SSL setup script not found. Please run SSL setup manually."
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose -f ${COMPOSE_FILE} ps
    echo ""
    
    # Show service URLs
    source ${ENV_FILE}
    echo "🌐 Application URLs:"
    echo "   • HTTP:  http://${DOMAIN_NAME:-localhost}"
    echo "   • HTTPS: https://${DOMAIN_NAME:-localhost}"
    echo ""
    
    echo "📊 Useful Commands:"
    echo "   • View logs:     docker-compose -f ${COMPOSE_FILE} logs -f"
    echo "   • Stop services: docker-compose -f ${COMPOSE_FILE} down"
    echo "   • Restart:       docker-compose -f ${COMPOSE_FILE} restart"
    echo "   • Update:        ./scripts/deploy.sh"
    echo ""
}

cleanup() {
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    log_success "Cleanup completed!"
}

# Main deployment process
main() {
    log_info "Starting Zero@Design production deployment..."
    echo ""
    
    check_requirements
    backup_database
    build_images
    deploy_application
    
    # Ask about SSL setup
    read -p "Do you want to set up SSL certificates? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_ssl
    fi
    
    show_status
    cleanup
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Your Zero@Design application is now running in production mode."
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "health")
        check_health
        ;;
    "backup")
        backup_database
        ;;
    "ssl")
        setup_ssl
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|health|backup|ssl|status|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment process (default)"
        echo "  health  - Check service health"
        echo "  backup  - Create database backup"
        echo "  ssl     - Setup SSL certificates"
        echo "  status  - Show deployment status"
        echo "  cleanup - Clean up Docker resources"
        exit 1
        ;;
esac