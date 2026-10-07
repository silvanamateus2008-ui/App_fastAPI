from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import CamelCaseSchema


class LoginRequest(CamelCaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenOut(CamelCaseSchema):
    access_token: str
    token_type: str = "bearer"
