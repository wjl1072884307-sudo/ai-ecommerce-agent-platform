from datetime import datetime

from app.schemas.common import ORMModel


class TicketStatusLogRead(ORMModel):
    id: int
    ticket_id: int
    from_status: str
    to_status: str
    operator_id: int
    reason: str
    created_at: datetime
