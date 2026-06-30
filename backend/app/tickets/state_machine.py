from enum import Enum


class TicketStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


LEGACY_STATUS_MAP = {
    "open": TicketStatus.PENDING,
}

ALLOWED_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.PENDING: {TicketStatus.PROCESSING, TicketStatus.CANCELLED},
    TicketStatus.PROCESSING: {
        TicketStatus.WAITING_CUSTOMER,
        TicketStatus.RESOLVED,
        TicketStatus.CANCELLED,
    },
    TicketStatus.WAITING_CUSTOMER: {TicketStatus.PROCESSING, TicketStatus.RESOLVED},
    TicketStatus.RESOLVED: {TicketStatus.CLOSED, TicketStatus.PROCESSING},
    TicketStatus.CLOSED: set(),
    TicketStatus.CANCELLED: set(),
}

TERMINAL_STATUSES = {TicketStatus.CLOSED, TicketStatus.CANCELLED}


def normalize_ticket_status(status: str | TicketStatus) -> TicketStatus:
    if isinstance(status, TicketStatus):
        return status
    normalized = LEGACY_STATUS_MAP.get(status, status)
    try:
        return TicketStatus(normalized)
    except ValueError as exc:
        raise ValueError(f"Unknown ticket status: {status}") from exc


def is_valid_transition(from_status: str | TicketStatus, to_status: str | TicketStatus) -> bool:
    current = normalize_ticket_status(from_status)
    target = normalize_ticket_status(to_status)
    return target in ALLOWED_TRANSITIONS[current]


def validate_transition(from_status: str | TicketStatus, to_status: str | TicketStatus) -> None:
    current = normalize_ticket_status(from_status)
    target = normalize_ticket_status(to_status)
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Illegal ticket status transition: {current.value} -> {target.value}")
