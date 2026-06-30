from pydantic import BaseModel


class TicketStatusUpdate(BaseModel):
    status: str
    reason: str
    resolution: str | None = None
