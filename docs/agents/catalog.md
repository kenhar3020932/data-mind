# DataMind-King Agent Catalog

Complete catalog of all agents in the DataMind-King platform with detailed specifications.

---

## Agent Summary

| Agent | Name | Tier | Status | Tests | Coverage |
|-------|------|------|--------|-------|----------|
| SQL Agent | sql_agent | sonnet | ✅ Production | 18 | 98% |
| Dashboard Agent | dashboard_agent | sonnet | ✅ Production | 12 | 95% |
| Data Quality Agent | data_quality_agent | sonnet | ✅ Production | 15 | 96% |
| Planning Agent | planning_agent | opus | ✅ Production | 14 | 97% |
| Visualization Agent | viz_agent | haiku | ✅ Production | 10 | 94% |
| Python Agent | python_agent | sonnet | ✅ Production | 11 | 95% |
| Security Agent | security_agent | opus | ✅ Production | 16 | 98% |

**Total: 7 agents | 96 tests | 96.3% average coverage**

---

## Agent Details

### 1. SQL Agent (sql_agent)

**Tier:** sonnet  
**Description:** Executes SQL queries with gated validation, tenant isolation, and dynamic engine routing

**Specializations:**
- DuckDB queries (< 10GB)
- ClickHouse queries (10GB - 1TB)
- Spark queries (> 1TB)
- Query optimization and self-healing

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_select_engine(size_bytes: int, query_complexity: float) -> str
_optimize_query_with_llm(query: str, error_msg: str) -> str | None
_calculate_confidence(result: dict, execution_time_ms: float, ...) -> float
```

**Test Coverage:** 98%  
**Files:**
- `backend/app/agents/sql/agent.py` - Main agent implementation
- `backend/app/agents/sql/schemas.py` - Input/output schemas
- `backend/app/agents/sql/tools.py` - SQL utility functions

---

### 2. Dashboard Agent (dashboard_agent)

**Tier:** sonnet  
**Description:** Provisions BI dashboards in Superset, Metabase, or Vega-Lite

**Specializations:**
- Superset dashboard creation
- Metabase dashboard configuration
- Vega-Lite visualization generation
- Dashboard layout optimization

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_select_tool(context: dict) -> str
_provision_dashboard(tool: str, org_id: str, widgets: list) -> dict
```

**Test Coverage:** 95%  
**Files:**
- `backend/app/agents/dashboard/agent.py` - Main agent implementation
- `backend/app/agents/dashboard/schemas.py` - Dashboard schemas
- `backend/app/agents/dashboard/tools.py` - Dashboard utilities

---

### 3. Data Quality Agent (data_quality_agent)

**Tier:** sonnet  
**Description:** Profiles datasets with dynamic tool selection and quality analysis

**Specializations:**
- Polars profiling (large datasets)
- Pandas profiling (medium datasets)
- Great Expectations validation (complex patterns)
- Quality metric calculation

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_llm_select_tool(context: dict) -> str
_heuristic_select_tool(context: dict) -> str
_calculate_confidence(metrics: dict, tool_used: str, ...) -> float
```

**Test Coverage:** 96%  
**Files:**
- `backend/app/agents/data_quality/agent.py` - Main agent implementation
- `backend/app/agents/data_quality/schemas.py` - Quality schemas
- `backend/app/agents/data_quality/tools.py` - Quality utilities

---

### 4. Planning Agent (planning_agent)

**Tier:** opus  
**Description:** Creates validated execution plans with DAG validation and PlanCritic integration

**Specializations:**
- LLM-based plan generation
- DAG cycle detection (Kahn's algorithm)
- Parallel step identification
- PlanCritic independent review
- Self-healing refinement

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_generate_plan_with_llm(task_desc: str, context: dict) -> dict
_validate_dag_and_detect_cycles(steps: list) -> tuple[bool, list, list]
_calculate_confidence(critic_score: float, step_count: int, ...) -> float
```

**Test Coverage:** 97%  
**Files:**
- `backend/app/agents/planning/agent.py` - Main agent implementation
- `backend/app/agents/planning/schemas.py` - Plan schemas
- `backend/app/agents/planning/tools.py` - DAG utilities

---

### 5. Visualization Agent (viz_agent)

**Tier:** haiku  
**Description:** Generates charts and visualizations from query results

**Specializations:**
- Automatic chart type selection
- Vega-Lite specification generation
- Theme customization
- Export to multiple formats

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_select_chart_type(data: list, context: dict) -> str
_generate_vegalite_spec(chart_type: str, data: list, ...) -> dict
```

**Test Coverage:** 94%  
**Files:**
- `backend/app/agents/viz/agent.py` - Main agent implementation
- `backend/app/agents/viz/schemas.py` - Visualization schemas
- `backend/app/agents/viz/tools.py` - Chart utilities

---

### 6. Python Agent (python_agent)

**Tier:** sonnet  
**Description:** Executes Python code in sandboxed environment

**Specializations:**
- Code validation and sanitization
- Sandbox execution (gVisor/nsjail)
- Resource limit enforcement
- Result serialization

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_validate_code(code: str) -> bool
_execute_in_sandbox(code: str, timeout: int, memory_limit: int) -> dict
```

**Test Coverage:** 95%  
**Files:**
- `backend/app/agents/python/agent.py` - Main agent implementation
- `backend/app/agents/python/schemas.py` - Execution schemas
- `backend/app/agents/python/tools.py` - Sandbox utilities

---

### 7. Security Agent (security_agent)

**Tier:** opus  
**Description:** Scans code and configurations for security vulnerabilities

**Specializations:**
- Secret scanning (GitLeaks, TruffleHog)
- SQL injection detection
- XSS vulnerability scanning
- Dependency vulnerability checking
- Security policy validation

**Key Methods:**
```python
async def acknowledge(brief: TaskBrief) -> Acknowledgement
async def execute(brief: TaskBrief, ack: Acknowledgement) -> AgentResult
_scan_secrets(target: str) -> list
_scan_sql_injection(code: str) -> list
_scan_xss(code: str) -> list
_check_dependencies(requirements: str) -> list
```

**Test Coverage:** 98%  
**Files:**
- `backend/app/agents/security/agent.py` - Main agent implementation
- `backend/app/agents/security/schemas.py` - Security schemas
- `backend/app/agents/security/tools.py` - Security utilities

---

## Agent Registry

The `AgentRegistry` manages all agent instances:

```python
from app.agents.base import registry

# List all agents
agents = registry.list_agents()

# Get agent info
info = registry.get_agent_info("sql_agent")

# Get agent instance
agent = registry.get_instance("sql_agent")

# Run agent
result = await agent.run(brief)
```

### Registry Methods
- `register(agent_class)` - Register an agent class
- `get(name)` - Get agent class by name
- `get_instance(name)` - Get or create agent instance
- `list_agents()` - List all registered agent names
- `get_agent_info(name)` - Get agent metadata

---

## Agent Testing

### Running Agent Tests
```bash
# Run all agent tests
pytest tests/unit/test_agents.py -v

# Run specific agent tests
pytest tests/unit/test_agents.py::TestSQLAgent -v
pytest tests/unit/test_ultra_agents.py::TestSQLAgent -v

# Run with coverage
pytest tests/unit/test_agents.py --cov=app.agents.sql --cov-report=term-missing
```

### Test Categories
1. **Unit Tests**: Individual method validation
2. **Integration Tests**: Agent interaction testing
3. **Benchmark Tests**: Performance measurement
4. **Security Tests**: Vulnerability scanning
5. **Golden Tests**: Statistical correctness

---

## Agent Configuration

### Model Tier Mapping
| Tier | Model | Use Case |
|------|-------|----------|
| opus | Claude Opus | Complex planning, security audit |
| sonnet | Claude Sonnet | Agent supervision, code generation |
| haiku | Claude Haiku | Simple classification, summarization |
| free | FreeLLM | Basic queries, validation |

### Resource Limits
```python
# Agent resource configuration
resource_limits = {
    "sql_agent": {"timeout": 30, "memory_mb": 512},
    "dashboard_agent": {"timeout": 60, "memory_mb": 1024},
    "data_quality_agent": {"timeout": 120, "memory_mb": 2048},
    "planning_agent": {"timeout": 30, "memory_mb": 1024},
    "viz_agent": {"timeout": 30, "memory_mb": 512},
    "python_agent": {"timeout": 60, "memory_mb": 1024},
    "security_agent": {"timeout": 120, "memory_mb": 2048}
}
```

---

*Last Updated: 2024-10-05*  
*Maintained by: DataMind-King Agent Team*
