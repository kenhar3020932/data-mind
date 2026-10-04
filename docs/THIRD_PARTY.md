# DataMind-King Third-Party Dependencies

Complete inventory of third-party libraries, packages, and their licenses.

---

## Core Dependencies

### Web Framework
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| fastapi | >=0.110.0 | MIT | Async web framework |
| uvicorn | >=0.29.0 | BSD-3 | ASGI server |
| starlette | >=0.37.0 | BSD-3 | ASGI toolkit |

### Data Validation & Settings
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| pydantic | >=2.6.0 | MIT | Data validation |
| pydantic-settings | >=2.2.0 | MIT | Settings management |

### Database
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| sqlalchemy | >=2.0.29 | MIT | ORM + Async support |
| aiosqlite | >=0.19.0 | Apache-2.0 | Async SQLite driver |
| asyncpg | >=0.29.0 | MIT | PostgreSQL async driver |

### Security & Authentication
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| python-jose | >=3.3.0 | MIT | JWT tokens |
| passlib | >=1.7.4 | BSD-3 | Password hashing |
| argon2-cffi | >=23.1.0 | MIT | Argon2id hashing |
| pyjwt | >=2.8.0 | MIT | JWT encoding/decoding |
| casbin | >=1.30.0 | Apache-2.0 | RBAC authorization |
| slowapi | >=0.1.9 | MIT | Rate limiting |

### Data Processing
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| sqlglot | >=25.0.0 | MIT | SQL parser/transpiler |
| polars | >=0.44.0 | MIT | DataFrame processing |
| duckdb | >=1.0.0 | MIT | In-memory analytical DB |
| pyarrow | >=15.0.0 | Apache-2.0 | Arrow format support |

### Storage & Networking
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| minio | >=7.2.0 | Apache-2.0 | S3-compatible storage |
| httpx | >=0.27.0 | BSD-3 | Async HTTP client |
| redis | >=5.0.0 | MIT | Redis client |

### Observability
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| structlog | >=24.1.0 | Apache-2.0 | Structured logging |
| opentelemetry-api | >=1.24.0 | Apache-2.0 | Tracing API |
| opentelemetry-sdk | >=1.24.0 | Apache-2.0 | Tracing SDK |
| prometheus-client | >=0.20.0 | Apache-2.0 | Metrics exposition |

### LLM & AI
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| anthropic | >=0.28.0 | MIT | Anthropic API client |
| langchain-core | >=0.2.0 | MIT | LLM abstractions |
| langgraph | >=0.1.0 | MIT | Agent graph orchestration |

### Utilities
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| tenacity | >=8.2.0 | Apache-2.0 | Retry logic |
| python-multipart | >=0.0.9 | Apache-2.0 | Multipart form parsing |
| anyio | >=4.0.0 | MIT | Async utilities |

---

## Development Dependencies

### Testing
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| pytest | >=8.1.0 | MIT | Testing framework |
| pytest-asyncio | >=0.23.0 | Apache-2.0 | Async test support |
| pytest-cov | >=4.1.0 | MIT | Coverage reporting |
| pytest-mock | >=3.14.0 | MIT | Mocking utilities |
| freezegun | >=1.4.0 | Apache-2.0 | Time mocking |
| respx | >=0.21.0 | MIT | HTTP mocking |

### Code Quality
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| ruff | >=0.3.0 | MIT | Linting + formatting |
| mypy | >=1.8.0 | MIT | Static type checking |
| bandit | >=1.7.0 | Apache-2.0 | Security scanning |
| safety | >=2.3.0 | Apache-2.0 | Dependency scanning |

### Documentation
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| mkdocs | >=1.5.0 | BSD-3 | Documentation generator |
| mkdocs-material | >=9.5.0 | MIT | Documentation theme |

---

## Optional Dependencies

### Machine Learning
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| scikit-learn | >=1.4.0 | BSD-3 | ML algorithms |
| xgboost | >=2.0.0 | Apache-2.0 | Gradient boosting |
| pandas | >=2.0.0 | BSD-3 | Data manipulation |

### Data Format Support
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| openpyxl | >=3.1.0 | MIT | Excel file support |
| xlsxwriter | >=3.2.0 | BSD-3 | Excel generation |
| pillow | >=10.0.0 | HPND | Image processing |

### Additional Drivers
| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| clickhouse-driver | >=0.2.0 | MIT | ClickHouse client |
| trino | >=0.320.0 | Apache-2.0 | Trino client |
| pyspark | >=3.5.0 | Apache-2.0 | Spark integration |

---

## License Compliance

### Permissive Licenses (Commercial-friendly)
- MIT
- BSD-2/3
- Apache-2.0
- ISC
- HPND

### Copy-left Licenses (Review required)
- GPL (none in current dependencies)
- LGPL (none in current dependencies)
- AGPL (none in current dependencies)

### Verified Compatible
All dependencies use permissive licenses compatible with commercial use.

---

## Dependency Management

### Updating Dependencies
```bash
# Update all dependencies
uv pip compile requirements/base.in --generate-hashes -o requirements/base.txt
uv pip compile requirements/data.in --generate-hashes -o requirements/data.txt
uv pip compile requirements/dev.in --generate-hashes -o requirements/dev.txt

# Install updated dependencies
uv pip install -r requirements/base.txt
```

### Security Scanning
```bash
# Check for known vulnerabilities
safety check -r requirements/base.txt
safety check -r requirements/data.txt

# Run bandit for code security issues
bandit -r backend/app -ll

# Check for license compliance
pip-licenses --format=json > licenses.json
```

### Lock Files
Hash-verified lock files are generated for reproducible builds:
- `requirements/base.lock`
- `requirements/data.lock`
- `requirements/dev.lock`

---

## Vendor Security

### Critical Packages Security Review

#### FastAPI
- **Maintained by**: tiangolo (active)
- **Security track record**: Excellent
- **Vulnerability history**: None critical

#### SQLAlchemy
- **Maintained by**: zzzeek (active)
- **Security track record**: Excellent
- **Vulnerability history**: None critical

#### Pydantic
- **Maintained by**: samuelcolvin (active)
- **Security track record**: Excellent
- **Vulnerability history**: None critical

#### sqlglot
- **Maintained by**: tunisio (active)
- **Security track record**: Good
- **Vulnerability history**: None critical

---

## Supply Chain Security

### Dependency Verification
```bash
# Verify package integrity
uv pip check

# Scan for supply chain attacks
trivy image python:3.12-slim
```

### Transitive Dependencies
All transitive dependencies are tracked and reviewed quarterly.

### Pinning Strategy
- Major versions pinned for stability
- Minor versions allow for security patches
- Patch versions auto-updated

---

*Last Updated: 2024-10-05*  
*Maintained by: DataMind-King Security Team*
