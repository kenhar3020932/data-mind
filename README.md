# DataMind-King

World's most advanced AI Data Analyst platform.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + LangGraph
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS
- **Data Plane**: DuckDB (<10GB) → Iceberg/Trino (10GB-1TB) → Spark (>1TB)
- **Storage**: MinIO (S3-compatible)
- **Auth**: JWT with bcrypt
- **Monitoring**: Prometheus + Grafana + Loki

## Quick Start

```bash
# Clone and setup
git clone <repository>
cd datamind-king

# Start infrastructure
docker compose -f infra/docker/docker-compose.core.yml up -d

# Run backend
cd backend
pip install -r requirements/base.txt -r requirements/data.txt -r requirements/ml.txt
python -m uvicorn app.main:app --reload

# Run frontend
cd ../frontend
npm install
npm run dev
```

## Project Structure

```
datamind-king/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── core/     # Settings, security, SQL gate
│   │   ├── brain/    # AI controller, planner, critic
│   │   ├── agents/   # Specialized agents
│   │   ├── api/      # FastAPI routers
│   │   ├── services/ # Business logic
│   │   └── models/   # SQLAlchemy models
│   └── tests/
├── frontend/         # Next.js 15 frontend
├── infra/            # Docker, K8s, scripts
└── docs/             # Documentation
```

## Development

See [DATAMIND_GODMODE_MASTER_SPEC.md](./DATAMIND_GODMODE_MASTER_SPEC.md) for complete architecture specification.