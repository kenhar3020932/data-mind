"""Budget management for DataMind-King."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class BudgetState:
    """Current budget state."""
    daily_limit_usd: float = 10.0
    monthly_limit_usd: float = 200.0
    spent_today_usd: float = 0.0
    spent_month_usd: float = 0.0
    last_reset_date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")


class BudgetGuard:
    """Prevent overspending on LLM calls."""

    def __init__(self) -> None:
        self.state = BudgetState()

    def check_budget(self, estimated_cost: float) -> bool:
        """Check if the estimated cost is within budget."""
        remaining_daily = self.state.daily_limit_usd - self.state.spent_today_usd
        remaining_monthly = self.state.monthly_limit_usd - self.state.spent_month_usd
        return estimated_cost <= min(remaining_daily, remaining_monthly)

    def record_cost(self, cost_usd: float) -> None:
        """Record a cost against the budget."""
        self.state.spent_today_usd += cost_usd
        self.state.spent_month_usd += cost_usd

    def reset_daily(self) -> None:
        """Reset daily spending counter."""
        self.state.spent_today_usd = 0.0
        self.state.last_reset_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")


# Module-level singleton
budget = BudgetGuard()
