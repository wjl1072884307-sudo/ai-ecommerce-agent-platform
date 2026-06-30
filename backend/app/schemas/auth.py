from pydantic import BaseModel

from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserRead(ORMModel):
    id: int
    username: str
    display_name: str
    role: str
    status: str

