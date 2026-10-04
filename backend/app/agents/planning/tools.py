"""Planning Agent Tools for DataMind-King - Ultra God Mode Edition."""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any

logger = logging.getLogger(__name__)

# Cost per hour for different model tiers (approximate)
AGENT_COSTS = {
    "opus": 15.0,
    "sonnet": 3.0,
    "haiku": 0.25,
    "default": 1.0
}


def validate_and_build_dag(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build and validate a DAG from step definitions with advanced checks.
    
    Args:
        steps: List of step dictionaries with 'step_id', 'depends_on', etc.
        
    Returns:
        Dict with validation status, topological order, parallel groups, and errors.
    """
    if not steps:
        return {"valid": False, "error": "No steps provided", "order": [], "parallel_groups": []}

    # 1. Index steps by ID
    step_map = {s["step_id"]: s for s in steps}
    step_ids = set(step_map.keys())
    
    # 2. Build adjacency list and in-degree map
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Initialize all nodes
    for sid in step_ids:
        if sid not in in_degree:
            in_degree[sid] = 0
            
    # Build edges
    for step in steps:
        sid = step["step_id"]
        deps = step.get("depends_on", [])
        for dep in deps:
            if dep not in step_ids:
                return {
                    "valid": False, 
                    "error": f"Step '{sid}' depends on unknown step '{dep}'",
                    "order": [],
                    "parallel_groups": []
                }
            graph[dep].append(sid)
            in_degree[sid] += 1

    # 3. Topological Sort (Kahn's Algorithm) + Parallel Grouping
    queue = deque([node for node in step_ids if in_degree[node] == 0])
    order = []
    parallel_groups = []
    
    while queue:
        # All nodes in current queue can run in parallel
        current_level = list(queue)
        parallel_groups.append(current_level)
        
        for _ in range(len(queue)):
            node = queue.popleft()
            order.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    # 4. Cycle Detection
    has_cycle = len(order) != len(step_ids)
    if has_cycle:
        missing = step_ids - set(order)
        return {
            "valid": False,
            "error": f"Cycle detected involving steps: {missing}",
            "order": [],
            "parallel_groups": []
        }

    # 5. Calculate Critical Path Duration
    critical_path_duration = _calculate_critical_path(steps, order)

    return {
        "valid": True,
        "order": order,
        "parallel_groups": parallel_groups,
        "critical_path_duration_seconds": critical_path_duration,
        "total_steps": len(steps),
        "max_parallelism": max(len(g) for g in parallel_groups) if parallel_groups else 1
    }


def _calculate_critical_path(steps: list[dict], topo_order: list[str]) -> float:
    """Calculate the longest path (critical path) in the DAG."""
    step_map = {s["step_id"]: s for s in steps}
    earliest_finish = {}
    
    for sid in topo_order:
        step = step_map[sid]
        duration = step.get("estimated_duration_seconds", 0.0)
        deps = step.get("depends_on", [])
        
        # Earliest start is the max finish time of all dependencies
        earliest_start = max([earliest_finish.get(dep, 0.0) for dep in deps], default=0.0)
        earliest_finish[sid] = earliest_start + duration
        
    return max(earliest_finish.values(), default=0.0)


def estimate_plan_cost_and_resources(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Estimate total cost, tokens, and duration for the plan.
    
    Args:
        steps: List of step dictionaries with 'agent', 'estimated_duration_seconds', etc.
        
    Returns:
        Dict with total cost, duration, and resource estimates.
    """
    total_cost = 0.0
    total_tokens = 0
    total_duration_raw = 0.0
    
    for step in steps:
        agent_name = step.get("agent", "default").lower()
        duration = step.get("estimated_duration_seconds", 0.0)
        tokens = step.get("estimated_tokens", 0)
        
        # Determine model tier from agent name or metadata
        tier = "sonnet"  # Default
        if "opus" in agent_name or "deep" in agent_name:
            tier = "opus"
        elif "haiku" in agent_name or "fast" in agent_name:
            tier = "haiku"
            
        # Cost calculation: (Cost/Hour) * (Duration/3600)
        hourly_rate = AGENT_COSTS.get(tier, AGENT_COSTS["default"])
        step_cost = hourly_rate * (duration / 3600.0)
        
        total_cost += step_cost
        total_tokens += tokens
        total_duration_raw += duration

    return {
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "total_duration_raw_seconds": round(total_duration_raw, 2),
        "average_cost_per_step": round(total_cost / max(len(steps), 1), 4)
    }


def generate_optimization_tips(steps: list[dict], dag_info: dict) -> list[str]:
    """Generate specific tips to optimize the plan."""
    tips = []
    
    # 1. Check for long sequential chains
    if dag_info.get("max_parallelism", 1) == 1 and len(steps) > 3:
        tips.append("Plan is highly sequential. Identify independent steps to enable parallel execution.")
        
    # 2. Check for expensive agents on simple tasks
    for step in steps:
        if "opus" in step.get("agent", "").lower() and step.get("estimated_duration_seconds", 0) < 5:
            tips.append(f"Step '{step['step_id']}' uses Opus for a short task. Consider downgrading to Sonnet/Haiku to save cost.")
            
    # 3. Check for missing fallbacks
    no_fallback = [s for s in steps if not s.get("fallback_strategy")]
    if no_fallback:
        tips.append(f"{len(no_fallback)} steps are missing fallback strategies. Add them for resilience.")
        
    # 4. Check for large parallel groups (resource contention)
    if dag_info.get("max_parallelism", 0) > 5:
        tips.append("High parallelism detected. Ensure your infrastructure can handle concurrent agent loads.")
        
    return tips
