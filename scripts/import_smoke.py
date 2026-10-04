#!/usr/bin/env python3
"""Smoke test for imports to ensure all modules can be loaded."""

import sys
from pathlib import Path


def main():
    """Test that all critical modules can be imported."""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / 'backend'

    sys.path.insert(0, str(backend_dir))

    modules_to_test = [
        # Core modules
        'app.main',
        'app.core.settings',
        'app.core.database',
        'app.core.security',
        'app.core.sql_gate',
        'app.core.audit_log',
        'app.core.logging_config',
        'app.core.minio_service',

        # Services
        'app.services.bi_service',
        'app.services.engine_service',
        'app.services.data_quality_service',
        'app.services.llm_service',
        'app.services.plan_critic_service',
        'app.services.upload_service',

        # Agents
        'app.agents.base',
        'app.agents.registry',
        'app.agents.sql.agent',
        'app.agents.dashboard.agent',
        'app.agents.data_quality.agent',
        'app.agents.planning.agent',
        'app.agents.viz.agent',
        'app.agents.python.agent',
        'app.agents.security.agent',

        # API routes
        'app.api.v1.auth',
        'app.api.v1.agents',
        'app.api.v1.bi',
        'app.api.v1.dashboards',
        'app.api.v1.datasets',
        'app.api.v1.jobs',
        'app.api.v1.reports',
        'app.api.v1.uploads',

        # Models
        'app.models.base',
        'app.models.user',
        'app.models.dataset',
        'app.models.dashboard',
        'app.models.job',
        'app.models.report',

        # Brain controller
        'app.brain.controller',
        'app.brain.memory',
    ]

    failed = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, str(e)))

    if failed:
        print(f"\n❌ {len(failed)} import(s) failed")
        for module, error in failed:
            print(f"  - {module}: {error}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(modules_to_test)} modules imported successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
