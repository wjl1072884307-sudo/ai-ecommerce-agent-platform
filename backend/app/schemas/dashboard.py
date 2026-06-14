from pydantic import BaseModel


class DashboardSummary(BaseModel):
    session_count: int
    product_count: int
    order_count: int
    pending_review_count: int
    open_ticket_count: int
    agent_run_count: int
    agent_success_rate: float


class StatItem(BaseModel):
    name: str
    value: int

