#!/bin/bash
# DataMind-King Infrastructure Init Script
# Sets up all required infrastructure components

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infra"

echo "╔════════════════════════════════════════════════════════╗"
echo "║     DataMind-King Infrastructure Initialization        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

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
    log_info "Checking prerequisites..."

    command -v docker >/dev/null 2>&1 || log_error "Docker is required but not installed"
    command -v docker-compose >/dev/null 2>&1 || {
        command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 || \
            log_error "Docker Compose is required but not installed"
    }
    command -v openssl >/dev/null 2>&1 || log_warn "openssl not found, using system random"

    log_info "Prerequisites check passed"
}

# Generate secrets
generate_secrets() {
    log_info "Generating secrets..."

    mkdir -p "$PROJECT_ROOT/.secrets"

    if [ ! -f "$PROJECT_ROOT/.secrets/pg_password" ]; then
        openssl rand -hex 32 > "$PROJECT_ROOT/.secrets/pg_password"
        chmod 600 "$PROJECT_ROOT/.secrets/pg_password"
        log_info "Generated PostgreSQL password"
    fi

    if [ ! -f "$PROJECT_ROOT/.secrets/minio_password" ]; then
        openssl rand -hex 32 > "$PROJECT_ROOT/.secrets/minio_password"
        chmod 600 "$PROJECT_ROOT/.secrets/minio_password"
        log_info "Generated MinIO password"
    fi

    if [ ! -f "$PROJECT_ROOT/.secrets/secret_key" ]; then
        openssl rand -base64 48 > "$PROJECT_ROOT/.secrets/secret_key"
        chmod 600 "$PROJECT_ROOT/.secrets/secret_key"
        log_info "Generated JWT secret key"
    fi

    if [ ! -f "$PROJECT_ROOT/.secrets/anthropic_key" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        log_warn "Please set ANTHROPIC_API_KEY environment variable or create .secrets/anthropic_key"
    fi

    log_info "Secrets generation complete"
}

# Create .env file from example
create_env_file() {
    log_info "Creating .env file..."

    local env_file="$INFRA_DIR/docker/.env"
    local env_example="$INFRA_DIR/docker/.env.example"

    if [ ! -f "$env_file" ] || [ -z "$(grep -v '^#' "$env_file" | grep -v '^$')" ]; then
        if [ -f "$env_example" ]; then
            cp "$env_example" "$env_file"
            log_info "Created .env from .env.example"
        else
            log_warn "No .env.example found, skipping"
        fi
    else
        log_info ".env file already exists, skipping"
    fi

    # Update secrets in .env
    if [ -f "$PROJECT_ROOT/.secrets/pg_password" ]; then
        sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(cat $PROJECT_ROOT/.secrets/pg_password)|" "$env_file"
    fi

    if [ -f "$PROJECT_ROOT/.secrets/minio_password" ]; then
        sed -i "s|MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=$(cat $PROJECT_ROOT/.secrets/minio_password)|" "$env_file"
    fi

    if [ -f "$PROJECT_ROOT/.secrets/secret_key" ]; then
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=$(cat $PROJECT_ROOT/.secrets/secret_key)|" "$env_file"
    fi

    log_info "Environment configuration complete"
}

# Pull Docker images
pull_images() {
    log_info "Pulling Docker images..."

    cd "$INFRA_DIR"
    docker compose -f docker-compose.core.yml config >/dev/null 2>&1 || {
        log_warn "docker-compose.core.yml not valid, skipping image pull"
        return
    }

    docker compose -f docker-compose.core.yml pull --quiet || log_warn "Some images failed to pull"

    log_info "Docker images pulled"
}

# Create required directories
setup_directories() {
    log_info "Setting up directories..."

    mkdir -p \
        "$PROJECT_ROOT/data/postgres" \
        "$PROJECT_ROOT/data/redis" \
        "$PROJECT_ROOT/data/minio" \
        "$PROJECT_ROOT/logs" \
        "$PROJECT_ROOT/backups"

    chmod 750 "$PROJECT_ROOT/data"
    chmod 750 "$PROJECT_ROOT/logs"

    log_info "Directories created"
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."

    cd "$INFRA_DIR"

    if docker compose -f docker-compose.core.yml config --quiet 2>/dev/null; then
        log_info "Core configuration valid"
    else
        log_warn "Core configuration has issues (may be expected in dev mode)"
    fi

    if [ -f "docker-compose.bi.yml" ]; then
        docker compose -f docker-compose.bi.yml config --quiet 2>/dev/null && \
            log_info "BI configuration valid" || \
            log_warn "BI configuration has issues"
    fi

    log_info "Configuration validation complete"
}

# Main execution
main() {
    log_info "Starting DataMind-King infrastructure initialization"
    log_info "Project root: $PROJECT_ROOT"

    check_prerequisites
    generate_secrets
    setup_directories
    create_env_file
    pull_images
    validate_config

    echo ""
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║           Infrastructure Initialization Complete       ║"
    log_info "║                                                        ║"
    log_info "║  Next steps:                                           ║"
    log_info "║    1. Review .env file at $INFRA_DIR/docker/.env      ║"
    log_info "║    2. Set ANTHROPIC_API_KEY or create .secrets/anthropic_key║"
    log_info "║    3. Run: docker compose -f infra/docker/docker-compose.core.yml up -d ║"
    log_info "║                                                        ║"
    log_info "╚════════════════════════════════════════════════════════╝"
}

main "$@"
