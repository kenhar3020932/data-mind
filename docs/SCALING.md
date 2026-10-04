# DataMind-King Scaling Guide

Comprehensive guide for scaling DataMind-King from development to enterprise production.

---

## Scaling Architecture

DataMind-King supports horizontal and vertical scaling across all components.

### Component Scaling Matrix

| Component | Scale Type | Min | Max | Auto? |
|-----------|------------|-----|-----|-------|
| Backend API | Horizontal | 1 | 50 | Yes (HPA) |
| PostgreSQL | Vertical + Read Replicas | 1 | 5 | Manual |
| Redis | Vertical + Cluster | 1 | 10 | Manual |
| MinIO | Horizontal ( erasure coding) | 1 | 64 | Manual |
| Spark | Horizontal | 1 | 100 | Auto |
| Trino | Horizontal | 1 | 20 | Manual |

---

## Development Scaling

### Single Developer Setup
```bash
# Start all services locally
docker compose -f infra/docker/docker-compose.dev.yml up -d

# Resources: 8GB RAM, 4 CPU cores
# Suitable for: Development, testing
```

### Local Optimization
```bash
# Reduce resource usage
docker compose -f infra/docker/docker-compose.dev.yml up -d --scale backend=1
docker compose -f infra/docker/docker-compose.dev.yml up -d --scale postgres=1

# Disable observability for speed
docker compose -f infra/docker/docker-compose.dev.yml up -d \
  --scale prometheus=0 \
  --scale grafana=0 \
  --scale loki=0
```

---

## Staging Scaling

### Small Team (5-10 developers)
```bash
# Production-like environment
docker compose -f infra/docker/docker-compose.core.yml up -d
docker compose -f infra/docker/docker-compose.bi.yml up -d
docker compose -f infra/docker/docker-compose.obs.yml up -d

# Resources: 32GB RAM, 16 CPU cores
# Storage: 500GB SSD
```

### Staging Databases
```bash
# Separate databases for staging
DATABASE_URL=postgresql://postgres:staging@postgres-staging:5432/datamind_staging
REDIS_URL=redis://redis-staging:6379/0
```

---

## Production Scaling

### Small Production (1-10K users)
```yaml
# Kubernetes Deployment
replicas: 3
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"

# HPA Configuration
minReplicas: 3
maxReplicas: 10
metrics:
  - cpu: 70%
  - memory: 80%
```

### Medium Production (10K-100K users)
```yaml
# Multiple replicas with spread
replicas: 5
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"

# Read replicas for database
primary: 1
replicas: 2

# Redis cluster
nodes: 3
shards: 3
```

### Large Production (100K+ users)
```yaml
# Auto-scaling with fine-tuned metrics
replicas: 10
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"

# Database with connection pooling
primary: 1
replicas: 3
pool_size: 100

# MinIO erasure coding
nodes: 4
disks: 8

# Spark cluster
masters: 2
workers: 10
```

---

## Database Scaling

### PostgreSQL Scaling Strategies

#### Strategy 1: Vertical Scaling
```yaml
# Increase resource allocation
resources:
  requests:
    memory: "8Gi"
    cpu: "4000m"
  limits:
    memory: "16Gi"
    cpu: "8000m"

# Connection pool tuning
max_connections: 200
statement_timeout: 30000
```

#### Strategy 2: Read Replicas
```yaml
# Primary database
primary:
  endpoints: postgres-primary:5432
  
# Read replicas
replicas:
  - postgres-replica-1:5432
  - postgres-replica-2:5432

# Routing configuration
routing_rules:
  writes: primary
  reads: replicas
  specific_queries:
    - pattern: "SELECT.*"
      target: replicas
```

#### Strategy 3: Partitioning
```sql
-- Example: Range partitioning by date
CREATE TABLE events (
    id BIGSERIAL,
    created_at TIMESTAMP NOT NULL,
    data JSONB
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2024_q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE events_2024_q2 PARTITION OF events
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

---

## Cache Scaling

### Redis Scaling

#### Single Instance (< 10GB data)
```yaml
redis:
  image: redis:7-alpine
  resources:
    limits:
      memory: 4Gi
  config:
    maxmemory: 3gb
    maxmemory-policy: allkeys-lru
```

#### Redis Cluster (10GB+ data)
```yaml
redis-cluster:
  image: redis:7-alpine
  replicas: 3
  shards: 3
  
  config:
    cluster-enabled: "yes"
    cluster-config-file: nodes.conf
    cluster-node-timeout: 5000
```

### Cache Strategies

#### Pattern 1: Cache-Aside
```python
async def get_dataset(dataset_id: str):
    cache_key = f"dataset:{dataset_id}"
    
    # Try cache first
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    dataset = await db.fetch_dataset(dataset_id)
    
    # Update cache
    await redis.setex(cache_key, 3600, json.dumps(dataset))
    
    return dataset
```

#### Pattern 2: Write-Through
```python
async def update_dataset(dataset_id: str, data: dict):
    # Update database
    await db.update_dataset(dataset_id, data)
    
    # Update cache immediately
    cache_key = f"dataset:{dataset_id}"
    await redis.setex(cache_key, 3600, json.dumps(data))
```

---

## Object Storage Scaling

### MinIO Scaling

#### Single Node (< 10TB)
```yaml
minio:
  image: minio/minio:latest
  resources:
    limits:
      memory: 8Gi
  volumes:
    - /data/minio:/data
```

#### Distributed MinIO (10TB+)
```yaml
minio:
  image: minio/minio:latest
  command: server http://minio-{1...4}/data
  resources:
    limits:
      memory: 16Gi
  volumes:
    - /data/minio1:/data1
    - /data/minio2:/data2
    - /data/minio3:/data3
    - /data/minio4:/data4
```

### Lifecycle Policies
```json
{
  "rules": [
    {
      "id": "raw-data-retention",
      "status": "Enabled",
      "filter": {"prefix": "raw/"},
      "transition": {
        "days": 30,
        "storageClass": "STANDARD_IA"
      },
      "expiration": {
        "days": 365
      }
    },
    {
      "id": "archived-data",
      "status": "Enabled",
      "filter": {"prefix": "archived/"},
      "transition": {
        "days": 90,
        "storageClass": "GLACIER"
      }
    }
  ]
}
```

---

## Compute Scaling

### Spark Cluster Scaling

#### Small Cluster (100GB-1TB)
```yaml
spark:
  master:
    replicas: 1
    resources:
      limits:
        memory: 8Gi
        cpu: "4"
  worker:
    replicas: 3
    resources:
      limits:
        memory: 16Gi
        cpu: "8"
```

#### Large Cluster (>1TB)
```yaml
spark:
  master:
    replicas: 2  # High availability
  worker:
    replicas: 20  # Auto-scaling
    resources:
      limits:
        memory: 32Gi
        cpu: "16"
    
  # Auto-scaling configuration
  autoscaling:
    enabled: true
    minExecutors: 5
    maxExecutors: 100
    scaleUpThreshold: 0.8
    scaleDownThreshold: 0.2
```

### Trino Cluster Scaling

```yaml
trino:
  coordinator:
    resources:
      limits:
        memory: 16Gi
        cpu: "8"
  worker:
    replicas: 3
    resources:
      limits:
        memory: 32Gi
        cpu: "16"
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

#### Infrastructure Metrics
- CPU utilization (< 80%)
- Memory utilization (< 85%)
- Disk I/O throughput
- Network bandwidth
- Container restart count

#### Application Metrics
- API latency (p95 < 200ms)
- Error rate (< 0.1%)
- Request throughput
- Database connection pool usage
- Cache hit rate (> 90%)

#### Business Metrics
- Active users
- Dataset processing time
- Query completion rate
- Agent execution success rate
- Cost per operation

### Alert Rules
```yaml
groups:
  - name: infrastructure
    rules:
      - alert: HighCPU
        expr: cpu_usage > 80
        for: 10m
        severity: warning
      
      - alert: HighMemory
        expr: memory_usage > 85
        for: 5m
        severity: warning
      
      - alert: DiskSpaceRunningLow
        expr: disk_free_percent < 15
        for: 1h
        severity: critical

  - name: application
    rules:
      - alert: HighLatency
        expr: api_latency_p95 > 200
        for: 5m
        severity: warning
      
      - alert: HighErrorRate
        expr: error_rate > 0.001
        for: 2m
        severity: critical
      
      - alert: CacheMissRateHigh
        expr: cache_miss_rate > 0.1
        for: 10m
        severity: warning
```

---

## Cost Optimization

### Resource Right-Sizing
```bash
# Identify over-provisioned resources
kubernetes-top-usage --namespace datamind --sort-by memory

# Identify under-provisioned resources
kubernetes-top-usage --namespace datamind --sort-by cpu
```

### Auto-Scaling Policies
```yaml
# Aggressive scaling up, conservative scaling down
autoscaling:
  scaleUp:
    stabilizationWindowSeconds: 60
    policies:
      - type: Percent
        value: 50
        periodSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 300
    policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Spot Instance Strategy
```yaml
# Use spot instances for non-critical workloads
spark:
  workers:
    nodeSelector:
      node-type: spot
    tolerations:
      - key: spot
        operator: Exists
        effect: NoSchedule
```

---

## Disaster Recovery

### Backup Strategy
```bash
# Daily full backup
./infra/scripts/backup.sh

# Hourly incremental
crontab -e
# */60 * * * * /path/to/incremental-backup.sh
```

### Recovery Procedures
```bash
# Full restore
./infra/scripts/restore.sh

# Point-in-time recovery
./infra/scripts/restore.sh --time "2024-10-05 14:30:00"

# Disaster recovery drill
./infra/scripts/restore.sh --dry-run
```

---

## Scaling Checklist

### Pre-Scale Verification
- [ ] All health checks passing
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place
- [ ] Disaster recovery tested
- [ ] Cost estimate reviewed

### Post-Scale Verification
- [ ] Performance targets met
- [ ] Error rates within tolerance
- [ ] Resource utilization optimal
- [ ] Cost within budget
- [ ] User experience verified

---

*Last Updated: 2024-10-05*  
*Maintained by: DataMind-King Infrastructure Team*
