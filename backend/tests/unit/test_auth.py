"""Unit tests for authentication module."""

from __future__ import annotations

import pytest
from jose import jwt

from app.core.auth import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


class TestAuth:
    """Test suite for authentication utilities."""

    def test_hash_and_verify_password(self) -> None:
        """Test password hashing works correctly (argon2id or bcrypt)."""
        pwd = "testpass"
        hashed = hash_password(pwd)
        assert hashed  # Not empty
        assert verify_password(pwd, hashed)
        assert not verify_password("wrongpass", hashed)

    def test_hash_is_unique(self) -> None:
        """Test that hashing same password produces different salts."""
        pwd = "testpass"
        hashed1 = hash_password(pwd)
        hashed2 = hash_password(pwd)
        assert hashed1 != hashed2

    def test_password_too_short_rejected_by_validator(self) -> None:
        """Test that short passwords are rejected by schema validation."""
        from app.api.v1.schemas import UserCreate
        with pytest.raises(Exception):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="short",
                org_id="org-123",
            )

    def test_create_and_decode_access_token(self) -> None:
        """Test JWT access token creation and decoding."""
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_and_decode_refresh_token(self) -> None:
        """Test JWT refresh token creation and decoding."""
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_invalid_token_rejected(self) -> None:
        """Test that invalid tokens raise ValueError."""
        with pytest.raises(ValueError):
            decode_token("invalid.token.here")

    def test_tampered_token_rejected(self) -> None:
        """Test that tampered tokens are rejected."""
        token = create_access_token("user-123")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError):
            decode_token(tampered)

    def test_different_secret_rejects_token(self) -> None:
        """Test that tokens signed with wrong secret are rejected."""
        from app.core.settings import settings as settings_module
        original = settings_module.secret_key

        # Create token with original secret
        token = jwt.encode(
            {"sub": "user-123", "exp": 9999999999, "type": "access"},
            original,
            algorithm=settings_module.algorithm,
        )

        # Change secret and verify token is rejected
        settings_module.secret_key = "different-secret-key-that-is-long-enough-32chars!!"
        with pytest.raises(Exception):  # jwt.InvalidSignatureError
            jwt.decode(token, settings_module.secret_key, algorithms=[settings_module.algorithm])

        # Restore original
        settings_module.secret_key = original