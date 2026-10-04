#!/bin/bash
# DataMind-King Database Backup Script
# Creates encrypted backups of PostgreSQL and MinIO data

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INFRA_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pg_backup_$TIMESTAMP.sql.gz"
ENCRYPTION_KEY_FILE="$PROJECT_ROOT/.secrets/pg_backup_key"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check prerequisites
check_prerequisites() {
    command -v pg_dump >/dev/null 2>&1 || log_error "pg_dump not found. Install postgresql-client."
    command -v openssl >/dev/null 2>&1 || log_warn "openssl not found, backups will not be encrypted"
    command -v docker >/dev/null 2>&1 || log_warn "docker not found, using local PostgreSQL"
}

# Create backup directory
setup_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    chmod 750 "$BACKUP_DIR"
    log_info "Backup directory: $BACKUP_DIR"
}

# Generate encryption key if needed
setup_encryption() {
    if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
        openssl genrsa -out "$ENCRYPTION_KEY_FILE" 4096 2>/dev/null || \
            log_warn "Failed to generate encryption key"
        chmod 600 "$ENCRYPTION_KEY_FILE"
    fi
}

# Backup PostgreSQL
backup_postgresql() {
    log_info "Backing up PostgreSQL database..."

    local db_url
    db_url=$(grep "^DATABASE_URL=" "$INFRA_DIR/docker/.env" 2>/dev/null | cut -d= -f2- || echo "")

    if [ -z "$db_url" ]; then
        log_warn "DATABASE_URL not found, using defaults"
        db_url="postgresql://postgres:postgres@localhost:5432/datamind"
    fi

    # Extract connection parameters
    local host port dbname user password
    host=$(echo "$db_url" | grep -oP '(?<=@)[^:]+(?=:)' || echo "localhost")
    port=$(echo "$db_url" | grep -oP '(?<=:)\d+(?=\/)' || echo "5432")
    dbname=$(echo "$db_url" | grep -oP '(?<=\/)\w+(?=\?|$)' || echo "datamind")
    user=$(echo "$db_url" | grep -oP '(?<=://)\w+' || echo "postgres")
    password=$(echo "$db_url" | grep -oP '(?<=:)\w+(?=@)' || echo "")

    export PGPASSWORD="$password"

    local backup_cmd="pg_dump -h $host -p $port -U $user -d $dbname --verbose"
    backup_cmd+=" --clean --if-exists"
    backup_cmd+=" --create"

    log_info "Running: $backup_cmd | gzip > $BACKUP_FILE"

    if eval "$backup_cmd" | gzip > "$BACKUP_FILE" 2>&1; then
        local size
        size=$(du -h "$BACKUP_FILE" | cut -f1)
        log_info "PostgreSQL backup completed: $BACKUP_FILE ($size)"
    else
        log_error "PostgreSQL backup failed"
    fi

    unset PGPASSWORD
}

# Backup MinIO data
backup_minio() {
    log_info "Backing up MinIO data..."

    local minio_backup_dir="$BACKUP_DIR/minio_$TIMESTAMP"
    mkdir -p "$minio_backup_dir"

    # Check if MinIO container is running
    if docker ps --format '{{.Names}}' | grep -q "datamind-minio"; then
        docker cp datamind-minio:/data "$minio_backup_dir/" || {
            log_warn "Failed to copy MinIO data from container"
            return 1
        }
    else
        log_warn "MinIO container not running, skipping MinIO backup"
        return 0
    fi

    # Create manifest
    cat > "$minio_backup_dir/manifest.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "type": "minio",
  "buckets": [
    "raw",
    "cleaned",
    "archived",
    "models",
    "reports"
  ]
}
EOF

    local size
    size=$(du -sh "$minio_backup_dir" | cut -f1)
    log_info "MinIO backup completed: $minio_backup_dir ($size)"
}

# Encrypt backup
encrypt_backup() {
    if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
        log_warn "No encryption key found, skipping encryption"
        return 0
    fi

    local encrypted_file="${BACKUP_FILE}.enc"

    log_info "Encrypting backup..."

    openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "$BACKUP_FILE" \
        -out "$encrypted_file" \
        -pass file:"$ENCRYPTION_KEY_FILE" 2>/dev/null || {
        log_warn "Encryption failed, keeping unencrypted backup"
        return 0
    }

    mv "$encrypted_file" "$BACKUP_FILE"
    chmod 600 "$BACKUP_FILE"
    log_info "Backup encrypted: $BACKUP_FILE"
}

# Cleanup old backups
cleanup_old_backups() {
    local retention_days=${1:-30}

    log_info "Cleaning up backups older than $retention_days days..."

    find "$BACKUP_DIR" -name "pg_backup_*.sql.gz" -mtime +"$retention_days" -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "minio_*" -type d -mtime +"$retention_days" -delete 2>/dev/null || true

    log_info "Cleanup completed"
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."

    if gzip -t "$BACKUP_FILE" 2>/dev/null; then
        log_info "Backup integrity check passed"

        # Show backup stats
        local lines
        lines=$(zcat "$BACKUP_FILE" | wc -l)
        local size
        size=$(du -h "$BACKUP_FILE" | cut -f1)

        log_info "Backup contains approximately $lines lines ($size)"
    else
        log_error "Backup integrity check failed!"
    fi
}

# Main execution
main() {
    log_info "Starting DataMind-King database backup"
    log_info "Timestamp: $TIMESTAMP"

    check_prerequisites
    setup_backup_dir
    setup_encryption

    backup_postgresql
    backup_minio || true
    encrypt_backup
    verify_backup
    cleanup_old_backups 30

    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║                    Backup Complete                     ║"
    log_info "║                                                        ║"
    log_info "║  File: $BACKUP_FILE                   ║"
    log_info "║  Size: $(du -h "$BACKUP_FILE" | cut -f1)                    ║"
    log_info "║  Timestamp: $TIMESTAMP                    ║"
    log_info "║                                                        ║"
    log_info "║  To restore: ./infra/scripts/restore.sh $BACKUP_FILE   ║"
    log_info "╚════════════════════════════════════════════════════════╝"
}

# Handle command line arguments
case "${1:-backup}" in
    backup)
        main
        ;;
    verify)
        setup_backup_dir
        verify_backup
        ;;
    cleanup)
        setup_backup_dir
        cleanup_old_backups "${2:-30}"
        ;;
    *)
        echo "Usage: $0 {backup|verify|cleanup [days]}"
        exit 1
        ;;
esac
