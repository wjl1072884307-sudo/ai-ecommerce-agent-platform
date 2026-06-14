from pydantic import BaseModel


class ReviewAction(BaseModel):
    reviewer_id: int | None = None
    review_comment: str | None = None
    final_reply: str | None = None

