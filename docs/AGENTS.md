# DataMind-King Agent Catalog

Complete documentation of all specialized agents in the DataMind-King agent fleet.

---

## Agent Overview

DataMind-King employs a multi-agent architecture where each agent specializes in a specific domain. Agents communicate through a shared task brief system and are orchestrated by the Brain Controller.

### Agent Fleet Summary

| Agent | Description | Model Tier | Complexity |
|-------|-------------|------------|------------|
| sql_agent | SQL query execution and optimization | sonnet | Medium |
| dashboard_agent | BI dashboard provisioning | sonnet | Medium |
| data_quality_agent | Dataset profiling and validation | sonnet | High |
| planning_agent | Plan generation with DAG validation | opus | High |
| viz_agent | Visualization generation | haiku | Medium |
| python_agent | Python code execution | sonnet | Medium |
| security_agent | Security scanning and validation | opus | High |

---

## Agent Specifications

### 1. SQL Agent

**Name:** `sql_agent`  
**Model Tier:** sonnet  
**Description:** Executes SQL queries with gated validation, tenant isolation, and dynamic engine routing

#### Capabilities
- Dynamic engine selection (DuckDB/ClickHouse/Spark)
- SQL injection prevention via sqlglot AST validation
- Self-healing query optimization with LLM
- Tenant isolation enforcement
- Execution metrics and confidence scoring

#### Interface
```python
from app.agents.sql.agent import SQLAgent
from app.agents.base import TaskBrief, Acknowledgement

agent = SQLAgent()
brief = TaskBrief(
    task_id="sql-1",
    org_id="org-123",
    context={"query": "SELECT * FROM users", "size_bytes": 1024*1024*100}
)
ack = await agent.acknowledge(brief)
result = await agent.execute(brief, ack)
```

#### Output Schema
```json
{
  "task_id": "string",
  "success": true,
  "output": {
    "query": "string",
    "engine": "duckdb|clickhouse|spark",
    "rows": "array",
    "columns": "array",
    "row_count": 0,
    "execution_time_ms": 0.0,
    "attempts": 1
  },
  "confidence": 0.95
}
```

---

### 2. Dashboard Agent

**Name:** `dashboard_agent`  
**Model Tier:** sonnet  
**Description:** Provisions BI dashboards in Superset, Metabase, or Vega-Lite

#### Capabilities
- Multi-tool dashboard provisioning
- Widget layout optimization
- Data source configuration
- Auto-generated visualizations
- Dashboard validation and testing

#### Interface
```python
from app.agents.dashboard.agent import DashboardAgent

agent = DashboardAgent()
brief = TaskBrief(
    task_id="dash-1",
    org_id="org-123",
    context={"widgets": [...], "layout": [...]}
)
result = await agent.execute(brief, ack)
```

---

### 3. Data Quality Agent

**Name:** `data_quality_agent`  
**Model Tier:** sonnet  
**Description:** Profiles datasets with dynamic tool selection and quality analysis

#### Capabilities
- Dynamic tool selection (Polars/Pandas/Great Expectations)
- Statistical profiling
- Data quality validation
- Issue detection and reporting
- Confidence-based quality scoring

#### Interface
```python
from app.agents.data_quality.agent import DataQualityAgent

agent = DataQualityAgent()
brief = TaskBrief(
    task_id="dq-1",
    org_id="org-123",
    context={"dataset_id": "ds-123", "profile_level": "full"}
)
result = await agent.execute(brief, ack)
```

---

### 4. Planning Agent

**Name:** `planning_agent`  
**Model Tier:** opus  
**Description:** Creates validated execution plans with cycle detection and parallel step identification

#### Capabilities
- LLM-based plan generation
- DAG validation with cycle detection
- PlanCritic independent review
- Parallel group identification
- Self-healing with critic feedback

#### Interface
```python
from app.agents.planning.agent import PlanningAgent

agent = PlanningAgent()
brief = TaskBrief(
    task_id="plan-1",
    org_id="org-123",
    context={"task": "Analyze sales data by region"}
)
result = await agent.execute(brief, ack)
```

---

### 5. Visualization Agent

**Name:** `viz_agent`  
**Model Tier:** haiku  
**Description:** Generates charts and visualizations from query results

#### Capabilities
- Chart type auto-selection
- Vega-Lite spec generation
- Responsive layout optimization
- Theme customization
- Export to multiple formats

#### Interface
```python
from app.agents.viz.agent import VizAgent

agent = VizAgent()
brief = TaskBrief(
    task_id="viz-1",
    org_id="org-123",
    context={"data": [...], "type": "chart"}
)
result = await agent.execute(brief, ack)
```

---

### 6. Python Agent

**Name:** `python_agent`  
**Model Tier:** sonnet  
**Description:** Executes Python code in sandboxed environment

#### Capabilities
- Code validation and sanitization
- Sandbox execution (gVisor/nsjail)
- Resource limits enforcement
- Result serialization
- Error isolation

#### Interface
```python
from app.agents.python.agent import PythonAgent

agent = PythonAgent()
brief = TaskBrief(
    task_id="py-1",
    org_id="org-123",
    context={"code": "import pandas as pd\n..."}
)
result = await agent.execute(brief, ack)
```

---

### 7. Security Agent

**Name:** `security_agent`  
**Model Tier:** opus  
**Description:** Scans code and configurations for security vulnerabilities

#### Capabilities
- Secret scanning (GitLeaks, TruffleHog)
- SQL injection detection
- XSS vulnerability scanning
- Dependency vulnerability checking
- Security policy validation

#### Interface
```python
from app.agents.security.agent import SecurityAgent

agent = SecurityAgent()
brief = TaskBrief(
    task_id="sec-1",
    org_id="org-123",
    context={"target": "backend/", "scan_type": "full"}
)
result = await agent.execute(brief, ack)
```

---

## Agent Lifecycle

### Registration
Agents are automatically discovered and registered via the `registry.register()` call at module import time.

### Acknowledgement
Each agent must acknowledge tasks it can handle before execution begins.

### Execution
Agents execute their specialized logic with self-healing and fallback mechanisms.

### Result
Results include confidence scores, metrics, and audit trail entries.

---

## Extending the Agent Fleet

To add a new agent:

1. Create agent directory: `backend/app/agents/<agent_name>/`
2. Implement `agent.py` extending `BaseAgent`
3. Add `schemas.py` and `tools.py` as needed
4. Register in `__init__.py`
5. Add unit tests
6. Document in this catalog

```python
from app.agents.base import BaseAgent, TaskBrief, Acknowledgement, AgentResult

class NewAgent(BaseAgent):
    name = "new_agent"
    description = "Description of new agent"
    prompt_version = "v1.0"
    model_tier = "sonnet"
    
    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        # Return acknowledgement
        
    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        # Return result

from app.agents.base import registry
registry.register(NewAgent)
```

---

*Last Updated: 2024-10-05*  
*Maintained by: DataMind-King Agent Team*
