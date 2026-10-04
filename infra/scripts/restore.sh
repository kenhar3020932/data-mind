#!/bin/bash
# DataMind-King Database Restore Script
# Restores PostgreSQL and MinIO data from backups

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INFRA_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
ENCRYPTION_KEY_FILE="$PROJECT_ROOT/.secrets/pg_backup_key"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "This script should not be run as root"
    fi
}

# Find backup file
find_backup() {
    local backup_file="${1:-}"

    if [ -z "$backup_file" ]; then
        log_info "Available backups:"
        echo ""
        ls -lh "$BACKUP_DIR"/pg_backup_*.sql.gz 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || \
            log_error "No backups found in $BACKUP_DIR"
        echo ""
        read -p "Enter backup filename: " backup_file
    fi

    if [ ! -f "$backup_file" ]; then
        backup_file="$BACKUP_DIR/$backup_file"
    fi

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
    fi

    echo "$backup_file"
}

# Decrypt backup if needed
decrypt_backup() {
    local backup_file=$1
    local decrypted_file="/tmp/restore_$(basename "$backup_file")"

    if [[ "$backup_file" == *.enc ]]; then
        log_info "Decrypting backup..."

        if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
            log_error "Encryption key not found: $ENCRYPTION_KEY_FILE"
        fi

        openssl enc -d -aes-256-cbc -pbkdf2 \
            -in "$backup_file" \
            -out "$decrypted_file" \
            -pass file:"$ENCRYPTION_KEY_FILE" 2>/dev/null || {
            log_error "Decryption failed. Wrong key or corrupted backup."
        }

        backup_file="$decrypted_file"
        log_info "Backup decrypted"
    fi

    echo "$backup_file"
}

# Restore PostgreSQL
restore_postgresql() {
    local backup_file=$1

    log_info "Restoring PostgreSQL database..."

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

    log_info "Connecting to $host:$port/$dbname as $user"

    # Create database if it doesn't exist
    psql -h "$host" -p "$port" -U "$user" -d postgres -c \
        "SELECT 'CREATE DATABASE $dbname' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$dbname')" \
        \gexec 2>/dev/null || true

    # Restore backup
    log_info "Restoring database..."

    if gunzip -c "$backup_file" | psql -h "$host" -p "$port" -U "$user" -d "$dbname" --verbose; then
        log_info "PostgreSQL restore completed successfully"
    else
        log_error "PostgreSQL restore failed"
    fi

    unset PGPASSWORD
}

# Restore MinIO data
restore_minio() {
    local minio_dir="${1:-}"

    log_info "Restoring MinIO data..."

    # Check for MinIO backup
    if [ -z "$minio_dir" ]; then
        minio_dir=$(ls -dt "$BACKUP_DIR"/minio_* 2>/dev/null | head -1)
    fi

    if [ -z "$minio_dir" ] || [ ! -d "$minio_dir" ]; then
        log_warn "No MinIO backup found, skipping MinIO restore"
        return 0
    fi

    # Check if MinIO container is running
    if ! docker ps --format '{{.Names}}' | grep -q "datamind-minio"; then
        log_warn "MinIO container not running, skipping MinIO restore"
        return 0
    fi

    # Restore data
    log_info "Copying MinIO data from $minio_dir"

    docker cp "$minio_dir/data" datamind-minio:/data/ 2>/dev/null || {
        log_warn "Failed to restore MinIO data"
        return 0
    }

    # Fix permissions
    docker exec datamind-minio chown -R 1000:1000 /data 2>/dev/null || true

    log_info "MinIO restore completed"
}

# Verify restore
verify_restore() {
    log_info "Verifying restore..."

    local db_url
    db_url=$(grep "^DATABASE_URL=" "$INFRA_DIR/docker/.env" 2>/dev/null | cut -d= -f2- || echo "")

    if [ -z "$db_url" ]; then
        log_warn "Cannot verify: DATABASE_URL not found"
        return 0
    fi

    local host port dbname user password
    host=$(echo "$db_url" | grep -oP '(?<=@)[^:]+(?=:)' || echo "localhost")
    port=$(echo "$db_url" | grep -oP '(?<=:)\d+(?=\/)' || echo "5432")
    dbname=$(echo "$db_url" | grep -oP '(?<=\/)\w+(?=\?|$)' || echo "datamind")
    user=$(echo "$db_url" | grep -oP '(?<=://)\w+' || echo "postgres")
    password=$(echo "$db_url" | grep -oP '(?<=:)\w+(?=@)' || echo "")

    export PGPASSWORD="$password"

    # Check table count
    local table_count
    table_count=$(psql -h "$host" -p "$port" -U "$user" -d "$dbname" -t -c \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null || echo "0")

    unset PGPASSWORD

    if [ "$table_count" -gt 0 ]; then
        log_info "Verification passed: Found $table_count tables"
        return 0
    else
        log_warn "Verification warning: No tables found"
        return 1
    fi
}

# Main execution
main() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║           DataMind-King Database Restore               ║"
    log_info "╚════════════════════════════════════════════════════════╝"

    check_not_root

    local backup_file
    backup_file=$(find_backup "${1:-}")

    log_info "Using backup: $backup_file"

    # Decrypt if needed
    backup_file=$(decrypt_backup "$backup_file")

    # Restore PostgreSQL
    restore_postgresql "$backup_file"

    # Restore MinIO (optional)
    restore_minio

    # Verify restore
    if verify_restore; then
        echo ""
        log_info "╔════════════════════════════════════════════════════════╗"
        log_info "║                   Restore Complete                     ║"
        log_info "║                                                        ║"
        log_info "║  Database: PostgreSQL restored                         ║"
        log_info "║  Storage:  MinIO restore (if available)                ║"
        log_info "║  Status:   Verified ✓                                  ║"
        log_info "╚════════════════════════════════════════════════════════╝"
    else
        log_error "Restore completed but verification failed"
    fi
}

main "$@"
