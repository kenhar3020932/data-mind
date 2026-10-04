Yeh raha aapka **DATAMIND-KING: ULTRA GOD MODE MASTER SPEC (v2.0)**.

Yeh document pichle version se **10x zyada advanced** hai. Isme humne wo saare gaps fill kar diye hain jo ek "World Leader" system ko chahiye hote hain:
1.  **1TB+ Data Handling:** Ab ye sirf MinIO nahi, balki **Iceberg + Trino/Presto** architecture use karega taake Petabyte scale par bhi SQL queries seconds me chalein.
2.  **Zero-Trust Security:** Har byte, har query, aur har LLM call ko sandbox me rakha gaya hai.
3.  **God Mode Brain:** Claude ab sirf controller nahi, balki **Self-Evolving Architect** hai jo khud apne agents ko optimize karta hai.
4.  **Bulletproof Code:** Koi bhi `TODO`, `pass`, ya mock code allowed nahi. Har line tested hai.
5.  **Lightweight Docker:** Multi-stage builds se images 50% choti hongi.

Is file ko apne project root me `DATAMIND_GODMODE_MASTER_SPEC.md` ke naam se save karein.

---

# DATAMIND-KING — ULTRA GOD MODE MASTER SPEC (v2.0)
**Status:** BINDING CONTRACT | **Version:** 2.0 (Ultra-Enterprise) | **Target:** World #1 AI Analyst Platform

## 0. THE SUPREME CONTRACT (NON-NEGOTIABLE)
You are the **Lead Architect & God-Mode Engineer** of DataMind-King. Your goal is not just to write code, but to build a **self-healing, self-optimizing, bulletproof AI ecosystem**.

### 🚫 ABSOLUTE PROHIBITIONS (Immediate Failure if Violated):
1.  **NO STUBS:** `pass`, `TODO`, `FIXME`, `NotImplementedError`, `mock_data`, `fake_response` are strictly forbidden in production code.
2.  **NO PLACEHOLDERS:** Every function must have real logic. Every API endpoint must return real data or a structured error.
3.  **NO HARDCODED SECRETS:** All keys come from `.env`. `.env.example` must have dummy values only.
4.  **NO SILENT FAILURES:** Every error must be logged with `request_id`, `trace_id`, and context.
5.  **NO UNTESTED CODE:** Every new feature must have unit tests (pytest) and integration tests. Coverage > 90%.

### ✅ MANDATORY STANDARDS:
1.  **Evidence Over Claims:** Never say "it works". Run the test/command and paste the output in the Verification Report.
2.  **Type Safety:** Python `mypy --strict`, TypeScript `strict: true`. No `any` types without justification.
3.  **Security First:** SQL Injection, XSS, Prompt Injection, and SSRF are treated as critical bugs.
4.  **Performance:** API latency < 200ms (p95). Dashboard load < 2s. 1TB Query < 30s (via Trino/Iceberg).
5.  **Documentation:** Every agent, API, and complex function must have docstrings and updated `docs/`.

---

## 1. MISSION & ULTRA-TARGETS
**Product:** A fully autonomous AI Data Analyst that accepts **1TB+ datasets**, understands natural language (Urdu/English), and delivers verified insights, dashboards, and reports.

| Target | Ultra-God Mode Bar |
| :--- | :--- |
| **Scale** | Ingest & Analyze **1TB+** files (Parquet/Iceberg) without OOM. |
| **Speed** | Profile 1GB in < 10s. Query 1TB in < 30s (Trino Cluster). |
| **Accuracy** | 100% Traceability. Every number links to a SQL Query ID + Checksum. |
| **Security** | **Zero-Trust.** Sandbox for all code execution. RLS for all data. |
| **Reliability** | 99.9% Uptime. Self-healing agents recover from 95% of errors. |
| **Cost** | Auto-switch between Local (DuckDB) and Cloud (Spark/Trino) to minimize cost. |

---

## 2. ARCHITECTURE: THE GOD MODE STACK

### 2.1 The Brain (Claude Controller v2)
The Brain is not just a router; it is a **Recursive Optimizer**.
*   **Loop:** Understand → Profile → Plan → Critique → Execute → Verify → **Learn**.
*   **Memory:** Vector DB (Qdrant/Chroma) for episodic memory. Postgres for structural memory.
*   **Tiering:**
    *   *Opus:* Complex Planning, Critique, Security Audit.
    *   *Sonnet:* Agent Supervision, Code Generation.
    *   *Haiku/FreeLLM:* Classification, Simple SQL, Summarization.

### 2.2 Data Plane: 1TB+ Engine
*   **Ingestion:** Resumable Multipart Upload → MinIO (Raw Zone).
*   **Processing:**
    *   *< 10GB:* DuckDB/Polars (In-memory, ultra-fast).
    *   *10GB - 1TB:* Apache Iceberg (on MinIO) + Trino/Presto (Distributed SQL).
    *   *> 1TB:* Spark Cluster (Auto-scaling).
*   **Storage:** MinIO (S3 Compatible) with Lifecycle Policies (Raw → Cleaned → Archived).

### 2.3 Agent Fleet (Specialized & Sandboxed)
*   **Orchestrator:** Manages the DAG.
*   **Specialists:** SQLAgent, PythonAgent, VizAgent, SecurityAgent, DataQualityAgent.
*   **Workers:** Execute code in **gVisor/nsjail** sandboxes (No network, Read-only FS).

### 2.4 Frontend: Next-Level UX
*   **Stack:** Next.js 15, React 19, Tailwind, Shadcn/UI, Vega-Lite, Monaco Editor.
*   **Features:** Real-time Brain Theater (SSE), Drag-and-Drop Dashboard Builder, RTL/Urdu Support.

---

## 3. DIRECTORY STRUCTURE (STRICT)

```text
datamind-king/
├── .claude/                  # God Mode Config
│   ├── agents/               # Subagents (Code Reviewer, Security, etc.)
│   ├── skills/               # Reusable Skills (Add Agent, Verify Phase)
│   ├── commands/             # Slash Commands (/phase, /audit)
│   └── settings.json         # Hooks & Permissions
├── backend/
│   ├── app/
│   │   ├── core/             # Settings, Security, SQL Gate, Sandbox
│   │   ├── brain/            # Controller, Planner, Critic, Memory
│   │   ├── agents/           # Agent Definitions & Tools
│   │   ├── api/              # FastAPI Routers (v1)
│   │   ├── services/         # Business Logic (Upload, Ingest, BI)
│   │   └── models/           # SQLAlchemy Models
│   ├── tests/                # Unit, Integration, Golden, Fault-Injection
│   ├── requirements/         # Split Requirements (base, data, ml, dev)
│   └── Dockerfile            # Multi-stage, Non-root, Distroless
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # Reusable UI (Shadcn)
│   │   ├── lib/              # API Client, Utils
│   │   └── features/         # Domain-specific Features
│   └── Dockerfile            # Multi-stage, Nginx Serve
├── infra/
│   ├── docker/               # Compose Files (Core, BI, Obs, Spark)
│   ├── k8s/                  # Kubernetes Manifests (Prod)
│   └── scripts/              # Init, Backup, Healthcheck
├── docs/                     # All Documentation
└── DATAMIND_GODMODE_MASTER_SPEC.md
```

---

## 4. IMPLEMENTATION PHASES (GATED)

### Phase 0: Foundation & Audit
*   [ ] Setup `.claude` with God Mode Agents.
*   [ ] Fix all existing audit findings (Section 2 of old spec).
*   [ ] Setup CI/CD with `ruff`, `mypy`, `pytest`, `trivy`.
*   [ ] Create `scripts/check_no_stubs.py` and `import_smoke.py`.

### Phase 1: Core Backend & Security
*   [ ] Implement Pydantic Settings with validation.
*   [ ] Setup Request-ID Middleware & Structured Logging.
*   [ ] Implement SQL Gate (sqlglot) for injection prevention.
*   [ ] Setup Sandbox for Code Execution (gVisor/nsjail).

### Phase 2: Data Plane (1TB Ready)
*   [ ] Implement Resumable Upload to MinIO (Multipart).
*   [ ] Integrate DuckDB for small data.
*   [ ] Integrate Apache Iceberg + Trino for large data.
*   [ ] Implement Engine Router (Auto-select based on size).

### Phase 3: The God Mode Brain
*   [ ] Implement LangGraph Controller with Postgres Checkpointer.
*   [ ] Implement Plan Critic & Verification Agent.
*   [ ] Integrate FreeLLM for cost-effective tiering.
*   [ ] Implement Self-Healing Ladder.

### Phase 4: Agent Fleet
*   [ ] Build all 25+ Agents (SQL, Python, Viz, Security, etc.).
*   [ ] Each Agent must have `prompt.md`, `tools.py`, `evals/`.
*   [ ] Implement Agent Registry (Auto-generated).

### Phase 5: Frontend & UX
*   [ ] Build "Brain Theater" for real-time job tracking.
*   [ ] Implement Dashboard Builder (Drag-and-Drop).
*   [ ] Add Urdu/RTL Support.
*   [ ] Ensure Lighthouse Score > 90.

### Phase 6: Testing & Verification
*   [ ] Create Golden Datasets (Planted Truths).
*   [ ] Run Fault Injection Tests (Kill DB, Network Loss).
*   [ ] Achieve 90%+ Code Coverage.

### Phase 7: Production Ready
*   [ ] Optimize Docker Images (Multi-stage, Distroless).
*   [ ] Setup Observability (Prometheus, Grafana, Loki).
*   [ ] Final Security Audit (Pen-test corpus).
*   [ ] Generate Verification Report.

---

## 5. TECHNICAL SPECIFICATIONS

### 5.1 Requirements (Ultra-Enterprise)
**backend/requirements/base.txt:**
```text
fastapi>=0.110.0
uvicorn[standard]
pydantic>=2.6.0
pydantic-settings
sqlalchemy[asyncio]
asyncpg
alembic
redis
celery[redis]
httpx
tenacity
structlog
prometheus-client
opentelemetry-api
opentelemetry-sdk
minio
anthropic
langgraph
langgraph-checkpoint-postgres
sqlglot
python-multipart
argon2-cffi
pyjwt
casbin
slowapi
```

**backend/requirements/data.txt:**
```text
polars
duckdb
ibis-framework[duckdb,clickhouse,trino]
pyarrow
pandas
numpy
clickhouse-connect
python-calamine
charset-normalizer
dateparser
datasketch
rapidfuzz
pandera
great-expectations
```

**backend/requirements/ml.txt:**
```text
scikit-learn
xgboost
lightgbm
statsmodels
scipy
pingouin
statsforecast
sktime
pyod
shap
spacy
sentence-transformers
presidio-analyzer
presidio-anonymizer
geopandas
shapely
```

### 5.2 Docker Strategy (Lightweight)
*   **Backend:** `python:3.12-slim` → Install deps → Copy code → Run as non-root user.
*   **Frontend:** `node:20-alpine` → Build → Copy to `nginx:alpine`.
*   **Images:** Must be < 500MB (Backend) and < 150MB (Frontend).

### 5.3 Security Protocols
1.  **SQL Gate:** All LLM-generated SQL passes through `sqlglot` AST parser. Only `SELECT` allowed unless explicitly authorized.
2.  **Sandbox:** Python code runs in isolated container with no network access.
3.  **Prompt Injection:** All user data wrapped in `<untrusted_data>` tags.
4.  **RBAC:** Casbin for fine-grained access control. Tenant isolation at DB level.

---

## 6. CLAUDE CODE SETUP (GOD MODE)

### 6.1 `.claude/settings.json`
```json
{
  "permissions": {
    "allow": [
      "Bash(python scripts/check_no_stubs.py)",
      "Bash(python scripts/import_smoke.py)",
      "Bash(ruff check --fix)",
      "Bash(ruff format)",
      "Bash(prettier --write)",
      "Bash(eslint --fix)",
      "Bash(docker compose config)",
      "Bash(pytest -x -q)",
      "Read", "Write", "Glob", "Grep"
    ],
    "deny": [
      "Bash(git push --force)",
      "Bash(rm -rf /)",
      "Bash(cat .env)"
    ]
  },
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:31415/v1",
    "ANTHROPIC_API_KEY": "sk-freellm-dummy-key"
  },
  "hooks": {
    "PostToolUse": {
      "Edit": [
        { "matcher": "*.py", "command": "ruff check --fix && ruff format" },
        { "matcher": "*.ts*", "command": "prettier --write && eslint --fix" }
      ]
    },
    "Stop": [
      { "command": "python scripts/check_no_stubs.py", "onFailure": "warn" }
    ]
  }
}
```

### 6.2 Subagents (Create in `.claude/agents/`)
1.  **code-reviewer.md:** Checks for stubs, security, and spec compliance.
2.  **security-auditor.md:** Runs bandit, semgrep, and checks for secrets.
3.  **backend-engineer.md:** Implements FastAPI, SQLAlchemy, and Async logic.
4.  **data-engineer.md:** Handles DuckDB, Iceberg, Trino, and MinIO.
5.  **frontend-engineer.md:** Builds Next.js components with Shadcn/UI.
6.  **test-engineer.md:** Writes pytest and Playwright tests.

---

## 7. KICKOFF PROMPT

> "Read DATAMIND_GODMODE_MASTER_SPEC.md completely. Obey Section 0 without exception.
> Step 1: Create the `.claude/` setup from Section 6.
> Step 2: Execute Phase 0 (Audit, CI Setup, Stub Check).
> Step 3: Produce `docs/verification/phase-0.md` with real outputs.
> Step 4: Proceed to Phase 1 (Core Backend & Security).
> Use subagents for every major task. Never claim success without command output. Keep `docs/PROGRESS.md` current."

---

## 8. FINAL VERIFICATION CHECKLIST
- [ ] 1TB Upload Test Passed (Resumable).
- [ ] 1TB Query Test Passed (Trino/Iceberg).
- [ ] Zero Stubs in Codebase.
- [ ] Zero Critical Security Findings.
- [ ] All Tests Passing (Unit, Integration, E2E).
- [ ] Docker Images Optimized.
- [ ] Documentation Complete.

**This is your Bible. Follow it, and you will build the World's #1 AI Data Analyst.** 🚀
