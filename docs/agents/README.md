# DataMind-King Agent Documentation

Detailed documentation for each specialized agent in the DataMind-King fleet.

---

## Agent Base Class

All agents extend `BaseAgent` which defines the standard interface:

```python
class BaseAgent(ABC):
    """Abstract base class for all DataMind-King agents."""
    
    name: str = "base_agent"
    description: str = ""
    prompt_version: str = "v1.0"
    model_tier: str = "sonnet"
    
    @abstractmethod
    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        """Acknowledge a task and provide execution estimate."""
    
    @abstractmethod
    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        """Execute the agent's core functionality."""
```

---

## SQL Agent

### Purpose
Executes SQL queries against selected data engines with dynamic routing, AST-based validation, tenant isolation enforcement, and self-healing optimization.

### Features
- **Dynamic Engine Selection**: Automatically chooses DuckDB, ClickHouse, or Spark based on data size
- **SQL Gate Validation**: Prevents SQL injection and destructive operations
- **Self-Healing**: LLM-based query optimization on failure
- **Tenant Isolation**: Enforces org_id in all queries
- **Confidence Scoring**: Evidence-based confidence calculation

### Usage
```python
from app.agents.sql.agent import SQLAgent
from app.agents.base import TaskBrief

agent = SQLAgent()
brief = TaskBrief(
    task_id="sql-1",
    org_id="org-123",
    context={
        "query": "SELECT * FROM users WHERE org_id = 'org-123'",
        "size_bytes": 100 * 1024 * 1024  # 100MB
    }
)

ack = await agent.acknowledge(brief)
result = await agent.execute(brief, ack)

print(f"Engine: {result.output['engine']}")
print(f"Rows: {result.output['row_count']}")
print(f"Confidence: {result.confidence}")
```

### Configuration
```python
# SQL Agent settings
model_tier = "sonnet"  # Uses Sonnet for query optimization
max_attempts = 3       # Retry attempts on failure
query_timeout = 30     # Query timeout in seconds
```

---

## Dashboard Agent

### Purpose
Provisions BI dashboards in Superset, Metabase, or Vega-Lite with dynamic tool selection and validation.

### Features
- **Multi-Tool Support**: Superset, Metabase, Vega-Lite
- **Widget Management**: Automatic widget generation
- **Layout Optimization**: Responsive dashboard layouts
- **Data Source Configuration**: Automatic datasource setup
- **Validation**: Dashboard functionality testing

### Usage
```python
from app.agents.dashboard.agent import DashboardAgent
from app.agents.base import TaskBrief

agent = DashboardAgent()
brief = TaskBrief(
    task_id="dash-1",
    org_id="org-123",
    context={
        "widgets": [
            {"type": "line", "query": "SELECT date,SUM(revenue) FROM sales GROUP BY date"},
            {"type": "bar", "query": "SELECT region,SUM(revenue) FROM sales GROUP BY region"}
        ],
        "layout": [{"x": 0, "y": 0, "w": 6, "h": 4}],
        "tool": "superset"  # Optional: superset, metabase, vega_lite
    }
)

result = await agent.execute(brief, ack)
print(f"Dashboard ID: {result.output['dashboard_id']}")
print(f"URL: {result.output['url']}")
```

---

## Data Quality Agent

### Purpose
Profiles datasets with dynamic tool selection, real data processing, self-healing capabilities, and comprehensive audit logging.

### Features
- **Dynamic Tool Selection**: Polars, Pandas, or Great Expectations
- **Statistical Profiling**: Distribution analysis, null detection, outlier finding
- **Quality Validation**: Rule-based data quality checks
- **Issue Detection**: Automatic data quality issue identification
- **Confidence Scoring**: Multi-signal confidence calculation

### Usage
```python
from app.agents.data_quality.agent import DataQualityAgent
from app.agents.base import TaskBrief

agent = DataQualityAgent()
brief = TaskBrief(
    task_id="dq-1",
    org_id="org-123",
    context={
        "dataset_id": "sales-2024",
        "profile_level": "full",  # quick, standard, full
        "has_complex_patterns": True
    }
)

result = await agent.execute(brief, ack)
print(f"Tool: {result.output['tool']}")
print(f"Metrics: {result.output['metrics']}")
print(f"Issues: {len(result.output['issues_found'])}")
```

---

## Planning Agent

### Purpose
Creates validated execution plans (PlanDAG) with LLM-based generation, PlanCritic validation, cycle detection, parallel step identification, and self-healing capabilities.

### Features
- **LLM-Based Generation**: Natural language to structured plan
- **DAG Validation**: Cycle detection using Kahn's algorithm
- **Parallel Grouping**: Identifies parallelizable steps
- **PlanCritic Integration**: Independent plan review
- **Self-Healing**: Refinement based on critic feedback

### Usage
```python
from app.agents.planning.agent import PlanningAgent
from app.agents.base import TaskBrief

agent = PlanningAgent()
brief = TaskBrief(
    task_id="plan-1",
    org_id="org-123",
    context={
        "task": "Analyze sales data by region and generate quarterly report",
        "complexity": "high",
        "available_agents": ["sql_agent", "data_quality_agent", "viz_agent"]
    }
)

result = await agent.execute(brief, ack)
print(f"Steps: {len(result.output['steps'])}")
print(f"Parallel Groups: {result.output['parallel_groups']}")
print(f"Critic Score: {result.output['critic_score']}")
```

---

## Visualization Agent

### Purpose
Generates charts and visualizations from query results with automatic chart type selection and responsive layouts.

### Features
- **Auto Chart Selection**: Optimal chart type based on data characteristics
- **Vega-Lite Specs**: Production-ready visualization specifications
- **Theme Support**: Multiple visualization themes
- **Export Formats**: PNG, SVG, PDF, interactive HTML
- **Responsive Design**: Mobile-friendly layouts

### Usage
```python
from app.agents.viz.agent import VizAgent
from app.agents.base import TaskBrief

agent = VizAgent()
brief = TaskBrief(
    task_id="viz-1",
    org_id="org-123",
    context={
        "data": [{"date": "2024-01", "value": 100}, ...],
        "type": "auto",  # auto, line, bar, pie, scatter
        "title": "Sales Trend"
    }
)

result = await agent.execute(brief, ack)
print(f"Chart Type: {result.output['chart_type']}")
print(f"Spec: {result.output['spec']}")
```

---

## Python Agent

### Purpose
Executes Python code in a sandboxed environment with security validation and resource limits.

### Features
- **Code Validation**: Syntax and security checks
- **Sandbox Execution**: gVisor/nsjail isolation
- **Resource Limits**: CPU, memory, and time restrictions
- **Result Serialization**: Safe output handling
- **Error Isolation**: Crash containment

### Usage
```python
from app.agents.python.agent import PythonAgent
from app.agents.base import TaskBrief

agent = PythonAgent()
brief = TaskBrief(
    task_id="py-1",
    org_id="org-123",
    context={
        "code": """
import pandas as pd
df = pd.read_csv('sales.csv')
result = df.groupby('region')['revenue'].sum()
print(result.to_json())
""",
        "timeout": 30,
        "memory_limit_mb": 512
    }
)

result = await agent.execute(brief, ack)
print(f"Output: {result.output['stdout']}")
print(f"Errors: {result.output.get('stderr', '')}")
```

---

## Security Agent

### Purpose
Scans code and configurations for security vulnerabilities including secret detection, SQL injection, XSS, and dependency vulnerabilities.

### Features
- **Secret Scanning**: GitLeaks, TruffleHog integration
- **SQL Injection Detection**: AST-based vulnerability scanning
- **XSS Prevention**: Output encoding validation
- **Dependency Scanning**: Safety, Bandit integration
- **Policy Validation**: Security policy compliance checking

### Usage
```python
from app.agents.security.agent import SecurityAgent
from app.agents.base import TaskBrief

agent = SecurityAgent()
brief = TaskBrief(
    task_id="sec-1",
    org_id="org-123",
    context={
        "target": "backend/",
        "scan_type": "full",  # secrets, sqli, xss, deps
        "severity": "medium"  # low, medium, high, critical
    }
)

result = await agent.execute(brief, ack)
print(f"Findings: {len(result.output['findings'])}")
for finding in result.output['findings']:
    print(f"  - {finding['severity']}: {finding['description']}")
```

---

## Agent Registry

### Discovery
```python
from app.agents.base import registry

# List all agents
agents = registry.list_agents()
print(f"Registered agents: {agents}")

# Get agent info
info = registry.get_agent_info("sql_agent")
print(f"Agent: {info['name']}")
print(f"Model: {info['model_tier']}")
```

### Instantiation
```python
# Get agent instance
agent = registry.get_instance("sql_agent")

# Run agent
result = await agent.run(brief)
```

---

## Agent Testing

### Unit Tests
Each agent has comprehensive unit tests covering:
- Normal execution paths
- Error handling
- Edge cases
- Security validation
- Performance benchmarks

### Integration Tests
Integration tests verify:
- Agent-to-agent communication
- Shared state management
- Orchestration flows
- Audit logging

### Benchmark Tests
Performance benchmarks measure:
- Execution time
- Resource utilization
- Cost per operation
- Confidence accuracy

---

*Last Updated: 2024-10-05*  
*Maintained by: DataMind-King Agent Team*
