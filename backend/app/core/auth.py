"""Authentication and authorization for DataMind-King.

JWT-based auth with Argon2id password hashing (preferred) or bcrypt fallback.
Uses settings from core.settings.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _HAS_ARGON2 = True
except ImportError:  # pragma: no cover
    _HAS_ARGON2 = False

from .settings import Settings, settings

# Use argon2id if available, otherwise fall back to bcrypt via passlib
if _HAS_ARGON2:
    pwd_context = PasswordHasher()
else:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")  # type: ignore[assignment]


def hash_password(password: str) -> str:
    """Hash a password using argon2id (preferred) or bcrypt."""
    if _HAS_ARGON2:
        return pwd_context.hash(password)
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a hash."""
    if _HAS_ARGON2:
        try:
            pwd_context.verify(hashed, plain)
            return True
        except VerifyMismatchError:
            return False
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token. Raises on invalid tokens."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


def create_token_pair(user_id: str) -> dict[str, str]:
    """Create both access and refresh tokens for a user."""
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
