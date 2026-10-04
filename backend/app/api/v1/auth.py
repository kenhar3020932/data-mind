"""Authentication routes for DataMind-King."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_token_pair, decode_token, hash_password, verify_password
from app.core.db import get_db
from app.core.settings import settings
from app.models.user import User
from .schemas import TokenResponse, UserCreate, UserLogin

router = APIRouter(prefix="", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token."""
    if credentials is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing authorization")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(exc)) from exc

    user_id: str = payload.get("sub", "")
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="User not found or inactive")
    return user


@router.post("/login", response_model=TokenResponse, tags=["auth-login"])
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    user = (await db.execute(
        select(User).where(User.email == body.email)
    )).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid credentials")
    pair = create_token_pair(user.id)
    return TokenResponse(**pair)


@router.post("/register", response_model=TokenResponse, tags=["auth-register"])
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new user and return JWT tokens."""
    existing = (await db.execute(
        select(User).where((User.email == body.email) | (User.username == body.username))
    )).scalars().all()
    if existing:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Email or username already taken")
    user = User(
        id="",  # Will be set by calling code
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        org_id=body.org_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    pair = create_token_pair(user.id)
    return TokenResponse(**pair)


@router.get("/me", tags=["auth-me"])
async def me(user: User = Depends(get_current_user)) -> dict:
    """Return the current user's profile."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "org_id": user.org_id,
    }


@router.post("/refresh", response_model=TokenResponse, tags=["auth-refresh"])
async def refresh(body: dict, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Refresh an access token using a valid refresh token."""
    refresh_token = body.get("refresh_token", "")
    try:
        payload = decode_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(exc)) from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token type")
    user_id = payload.get("sub", "")
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="User not found or inactive")
    pair = create_token_pair(user.id)
    return TokenResponse(**pair)
