#!/bin/bash

# PostgreSQL Backup Script for Zero@Design
# This script creates daily backups and manages retention

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="zero_design_backup_${TIMESTAMP}.sql"

# Database connection details
DB_HOST="postgres"
DB_NAME=${POSTGRES_DB}
DB_USER=${POSTGRES_USER}
DB_PASSWORD=${POSTGRES_PASSWORD}

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

echo "Starting backup at $(date)"

# Create database backup
PGPASSWORD=${DB_PASSWORD} pg_dump \
    -h ${DB_HOST} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=plain \
    > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress the backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "Backup created: ${BACKUP_FILE}"

# Check backup file size
BACKUP_SIZE=$(stat -f%z "${BACKUP_DIR}/${BACKUP_FILE}" 2>/dev/null || stat -c%s "${BACKUP_DIR}/${BACKUP_FILE}")
echo "Backup size: ${BACKUP_SIZE} bytes"

# Verify backup integrity
if [ ${BACKUP_SIZE} -lt 1024 ]; then
    echo "ERROR: Backup file is too small (${BACKUP_SIZE} bytes). Backup may have failed."
    exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find ${BACKUP_DIR} -name "zero_design_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# List remaining backups
echo "Current backups:"
ls -lah ${BACKUP_DIR}/zero_design_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "Backup completed successfully at $(date)"

# Optional: Upload to S3 if configured
if [ ! -z "${AWS_ACCESS_KEY_ID}" ] && [ ! -z "${BACKUP_S3_BUCKET}" ]; then
    echo "Uploading backup to S3..."
    aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE} s3://${BACKUP_S3_BUCKET}/database-backups/${BACKUP_FILE}
    echo "Backup uploaded to S3"
fi