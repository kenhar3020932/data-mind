#!/bin/bash
# DataMind-King Seed Data Script
# Populates database with initial demo/reference data

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INFRA_DIR")"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Get database connection
get_db_url() {
    grep "^DATABASE_URL=" "$INFRA_DIR/docker/.env" 2>/dev/null | cut -d= -f2- || \
        echo "postgresql://postgres:postgres@localhost:5432/datamind"
}

# Create seed data SQL
create_seed_sql() {
    cat << 'SQL'
-- DataMind-King Seed Data
-- Organization and Users

INSERT INTO organizations (id, name, slug, created_at, updated_at)
VALUES
    ('org-demo-001', 'Acme Corporation', 'acme-corp', NOW(), NOW()),
    ('org-demo-002', 'Globex Industries', 'globex', NOW(), NOW()),
    ('org-demo-003', 'Initech LLC', 'initech', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Sample Users
INSERT INTO users (id, email, username, hashed_password, org_id, role, is_active, created_at)
VALUES
    ('user-001', 'admin@acme.com', 'admin_acme', 'hashed_password_placeholder', 'org-demo-001', 'admin', true, NOW()),
    ('user-002', 'analyst@acme.com', 'analyst_acme', 'hashed_password_placeholder', 'org-demo-001', 'analyst', true, NOW()),
    ('user-003', 'admin@globex.com', 'admin_globex', 'hashed_password_placeholder', 'org-demo-002', 'admin', true, NOW())
ON CONFLICT DO NOTHING;

-- Sample Datasets
INSERT INTO datasets (id, name, org_id, description, file_type, size_bytes, row_count, status, created_at)
VALUES
    ('ds-001', 'Sales Data 2024', 'org-demo-001', 'Annual sales transactions', 'parquet', 104857600, 1000000, 'processed', NOW()),
    ('ds-002', 'Customer Metrics', 'org-demo-001', 'Customer behavior analytics', 'csv', 52428800, 500000, 'processed', NOW()),
    ('ds-003', 'Inventory Levels', 'org-demo-002', 'Real-time inventory data', 'parquet', 209715200, 2000000, 'processed', NOW())
ON CONFLICT DO NOTHING;

-- Sample Dashboards
INSERT INTO dashboards (id, name, org_id, description, layout, created_at, updated_at)
VALUES
    ('dash-001', 'Sales Overview', 'org-demo-001', 'Key sales metrics and trends',
     '[{"x":0,"y":0,"w":6,"h":4,"type":"line","query":"SELECT date,SUM(revenue) FROM sales GROUP BY date"},{"x":6,"y":0,"w":6,"h":4,"type":"bar","query":"SELECT region,SUM(revenue) FROM sales GROUP BY region"}]',
     NOW(), NOW()),
    ('dash-002', 'Customer Analytics', 'org-demo-001', 'Customer behavior dashboard',
     '[{"x":0,"y":0,"w":12,"h":6,"type":"table","query":"SELECT * FROM customer_metrics LIMIT 100"}]',
     NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Sample Jobs (Templates)
INSERT INTO jobs (id, name, org_id, agent_type, config, status, created_at)
VALUES
    ('job-001', 'Daily Sales Report', 'org-demo-001', 'report',
     '{"dataset_id": "ds-001", "format": "pdf", "schedule": "0 9 * * *"}',
     'completed', NOW()),
    ('job-002', 'Customer Analysis', 'org-demo-001', 'analysis',
     '{"dataset_id": "ds-002", "agents": ["sql_agent", "viz_agent"]}',
     'completed', NOW())
ON CONFLICT DO NOTHING;

-- Golden Dataset for Testing
INSERT INTO datasets (id, name, org_id, description, file_type, size_bytes, row_count, status, metadata_, created_at)
VALUES
    ('golden-001', 'Golden Test Dataset', 'org-demo-001', 'Planted truth dataset for validation',
     'parquet', 1048576, 10000, 'processed',
     '{"golden": true, "known_answers": {"total_revenue": 1500000, "unique_customers": 5000, "avg_order_value": 300}}',
     NOW())
ON CONFLICT DO NOTHING;

-- Grant permissions
INSERT INTO role_permissions (role, permission, org_id)
VALUES
    ('admin', 'all', 'org-demo-001'),
    ('analyst', 'read', 'org-demo-001'),
    ('analyst', 'execute_query', 'org-demo-001')
ON CONFLICT DO NOTHING;

SQL
}

# Main execution
main() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║           DataMind-King Seed Data Loader               ║"
    log_info "╚════════════════════════════════════════════════════════╝"

    local db_url
    db_url=$(get_db_url)

    log_info "Database URL: ${db_url/.*:@/**masked**}"

    # Check if database is accessible
    if ! psql "$db_url" -c "SELECT 1" >/dev/null 2>&1; then
        log_error "Cannot connect to database: $db_url"
    fi

    log_info "Creating seed data..."

    # Generate and execute SQL
    local seed_sql
    seed_sql=$(create_seed_sql)

    echo "$seed_sql" | psql "$db_url" --verbose || {
        log_error "Failed to execute seed SQL"
    }

    log_info "Verifying seed data..."

    # Count seeded records
    local org_count user_count dataset_count
    org_count=$(psql "$db_url" -t -c "SELECT COUNT(*) FROM organizations" | xargs)
    user_count=$(psql "$db_url" -t -c "SELECT COUNT(*) FROM users" | xargs)
    dataset_count=$(psql "$db_url" -t -c "SELECT COUNT(*) FROM datasets" | xargs)

    echo ""
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║                    Seed Complete                       ║"
    log_info "║                                                        ║"
    log_info "║  Organizations: $org_count                                 ║"
    log_info "║  Users:         $user_count                                 ║"
    log_info "║  Datasets:      $dataset_count                                 ║"
    log_info "║                                                        ║"
    log_info "║  Demo credentials:                                     ║"
    log_info "║    admin@acme.com / password                            ║"
    log_info "║    analyst@acme.com / password                          ║"
    log_info "╚════════════════════════════════════════════════════════╝"
}

main "$@"
