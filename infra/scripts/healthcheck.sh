#!/bin/bash
# DataMind-King Health Check Script
# Monitors all infrastructure components and reports status

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE="$INFRA_DIR/docker/docker-compose.core.yml"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Health status tracking
declare -A HEALTH_STATUS
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

log_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           DataMind-King Health Check Report            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}\n"
}

log_service() {
    local service=$1
    local status=$2
    local message=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    case $status in
        "healthy")
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            echo -e "  ${GREEN}✓${NC} $service: $message"
            ;;
        "unhealthy")
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            echo -e "  ${RED}✗${NC} $service: $message"
            ;;
        "warning")
            WARNINGS=$((WARNINGS + 1))
            echo -e "  ${YELLOW}⚠${NC} $service: $message"
            ;;
        *)
            echo -e "  ? $service: $message"
            ;;
    esac
}

check_container_health() {
    local service=$1
    local expected_status=${2:-"healthy"}

    local container_name
    container_name=$(docker ps -q -f "name=$service" 2>/dev/null | head -1)

    if [ -z "$container_name" ]; then
        log_service "$service" "warning" "Container not running"
        return
    fi

    local health_status
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "unknown")

    case $health_status in
        "healthy")
            log_service "$service" "healthy" "Running ($health_status)"
            ;;
        "unhealthy")
            log_service "$service" "unhealthy" "Health check failed"
            ;;
        "starting")
            log_service "$service" "warning" "Container starting"
            ;;
        *)
            log_service "$service" "warning" "Status unknown"
            ;;
    esac
}

check_api_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")

    if [ "$http_code" = "$expected_code" ]; then
        log_service "$name" "healthy" "HTTP $http_code"
    elif [ "$http_code" = "000" ]; then
        log_service "$name" "unhealthy" "Connection refused"
    else
        log_service "$name" "warning" "HTTP $http_code (expected $expected_code)"
    fi
}

check_disk_space() {
    local path=$1
    local threshold=${2:-90}

    local usage
    usage=$(df -h "$path" 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ -z "$usage" ]; then
        log_service "Disk Space ($path)" "warning" "Unable to check"
        return
    fi

    if [ "$usage" -lt "$threshold" ]; then
        log_service "Disk Space ($path)" "healthy" "${usage}% used"
    else
        log_service "Disk Space ($path)" "unhealthy" "${usage}% used - CRITICAL"
    fi
}

check_database_connection() {
    local service=$1
    local db_name=$2

    if ! command -v psql >/dev/null 2>&1; then
        log_service "$service" "warning" "psql not installed"
        return
    fi

    local database_url
    database_url=$(grep "^DATABASE_URL=" "$INFRA_DIR/docker/.env" 2>/dev/null | cut -d= -f2-)

    if [ -z "$database_url" ]; then
        log_service "$service" "warning" "DATABASE_URL not found in .env"
        return
    fi

    if PGPASSWORD=$(echo "$database_url" | sed 's/.*password=//;s/@.*//') \
        psql -h localhost -U postgres -d "$db_name" -c "SELECT 1" >/dev/null 2>&1; then
        log_service "$service" "healthy" "Connection successful"
    else
        log_service "$service" "unhealthy" "Connection failed"
    fi
}

check_redis_connection() {
    local service=$1

    if ! command -v redis-cli >/dev/null 2>&1; then
        log_service "$service" "warning" "redis-cli not installed"
        return
    fi

    if redis-cli -h localhost ping >/dev/null 2>&1; then
        log_service "$service" "healthy" "PONG"
    else
        log_service "$service" "unhealthy" "Connection failed"
    fi
}

check_minio_connection() {
    local service=$1

    local minio_endpoint
    minio_endpoint=$(grep "^MINIO_ENDPOINT=" "$INFRA_DIR/docker/.env" 2>/dev/null | cut -d= -f2- || echo "localhost:9000")

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://$minio_endpoint/minio/health/live" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log_service "$service" "healthy" "MinIO health check passed"
    else
        log_service "$service" "unhealthy" "MinIO health check failed (HTTP $http_code)"
    fi
}

check_services() {
    echo -e "\n${YELLOW}━━━ Services ━━━${NC}"

    check_container_health "datamind-backend"
    check_container_health "datamind-postgres"
    check_container_health "datamind-redis"
    check_container_health "datamind-minio"
    check_container_health "datamind-prometheus"
    check_container_health "datamind-grafana"

    echo -e "\n${YELLOW}━━━ APIs ━━━${NC}"

    check_api_endpoint "Backend API" "http://localhost:8000/health" 200
    check_api_endpoint "Prometheus" "http://localhost:9090/-/healthy" 200
    check_api_endpoint "Grafana" "http://localhost:3001/api/health" 200

    echo -e "\n${YELLOW}━━━ Databases ━━━${NC}"

    check_database_connection "PostgreSQL" "datamind"
    check_redis_connection "Redis"
    check_minio_connection "MinIO"

    echo -e "\n${YELLOW}━━━ Storage ━━━${NC}"

    check_disk_space "/" 90
    check_disk_space "/data" 85
}

print_summary() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}                    SUMMARY                           ${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Total Checks:  $TOTAL_CHECKS"
    echo -e "  ${GREEN}Passed:        $PASSED_CHECKS${NC}"
    echo -e "  ${RED}Failed:        $FAILED_CHECKS${NC}"
    echo -e "  ${YELLOW}Warnings:      $WARNINGS${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ "$FAILED_CHECKS" -eq 0 ]; then
        echo -e "\n${GREEN}✓ All critical checks passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ $FAILED_CHECKS check(s) failed!${NC}"
        echo -e "\n  Run './infra/scripts/init.sh' to fix common issues"
        exit 1
    fi
}

main() {
    log_header

    if [ ! -f "$DOCKER_COMPOSE" ]; then
        log_error "Docker Compose file not found: $DOCKER_COMPOSE"
    fi

    check_services
    print_summary
}

main "$@"
