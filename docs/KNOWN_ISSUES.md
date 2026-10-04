# Known Issues

This file tracks all known defects, limitations, and deferred work. Updated after every phase.

| ID | Phase | Severity | Issue | Mitigation | Status |
|----|-------|----------|-------|------------|--------|
| KI-001 | 0 | Low | `ruff` and `mypy` not installed in dev environment | Installed via `pip install` in CI runners | Open |
| KI-002 | 0 | Low | `import_smoke.py` vacuously passes (all modules empty) | Will become meaningful in Phase 1 | Open |
| KI-003 | 0 | Medium | No test coverage yet (0%) | Test engineer will build suite in Phase 6 | Open |