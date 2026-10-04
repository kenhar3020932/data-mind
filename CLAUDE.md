# DataMind-King
Read DATAMIND_GODMODE_MASTER_SPEC.md before any work; Section 0 is binding.

## Commands
- Backend: `cd backend && uv run pytest -x -q`
- Lint: `ruff check . && mypy app/core`
- Frontend: `cd frontend && pnpm lint && pnpm type-check && pnpm build`
- Stack: `docker compose up -d`
- Gates: `python scripts/check_no_stubs.py && python scripts/import_smoke.py`

## Rules
1. No stubs (`pass`, `TODO`).
2. Evidence over claims (run commands, show output).
3. One commit per logical unit.
4. Update docs/DECISIONS.md for deviations.
5. Never commit secrets.

## Current Phase
See docs/PROGRESS.md (update after each phase).
