"""Pydantic v2 request/response schemas for all API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    total: int
    limit: int
    offset: int


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    data: T | None = None
    message: str = "OK"
    request_id: str = ""


class BaseError(BaseModel):
    """Base error response."""
    detail: str
    error_code: str = Field(pattern=r"^[A-Z][A-Z0-9_]{2,}$")


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until access token expiry")


class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    org_id: str = Field(..., min_length=1, max_length=36, pattern=r"^[a-f0-9\-]{36}$")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class DatasetCreate(BaseModel):
    """Dataset registration request."""
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    file_size_bytes: int = Field(ge=1)
    storage_key: str = Field(min_length=1, max_length=500)
    checksum: str | None = None


class JobResult(BaseModel):
    """Job execution result."""
    job_id: str
    status: str
    agent_name: str
    result: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float | None = None
    tokens_used: int | None = None
    cost_usd: float | None = None


model_config = ConfigDict(
    json_schema_extra={
        "examples": [
            {"detail": "Invalid input", "error_code": "INVALID_INPUT"},
        ]
    }
)
