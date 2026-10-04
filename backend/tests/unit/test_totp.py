"""Unit tests for TOTP 2FA."""

from __future__ import annotations

import pytest

from app.core.totp import TOTPService, generate_2fa_secret, verify_2fa_token


class TestTOTP:
    """Test suite for TOTP 2FA."""

    def setup_method(self) -> None:
        self.service = TOTPService()

    def test_generate_secret(self) -> None:
        """Test secret generation is at least 160 bits (32 base32 chars)."""
        secret = self.service.generate_secret()
        assert len(secret) == 32
        assert secret.isalnum()

    def test_verify_valid_token(self) -> None:
        """Test verification of valid TOTP token."""
        secret = self.service.generate_secret()
        token = self.service.get_current_time_based_code(secret)
        assert self.service.verify_token(secret, token) is True

    def test_verify_invalid_token(self) -> None:
        """Test that invalid tokens are rejected."""
        secret = self.service.generate_secret()
        assert self.service.verify_token(secret, "000000") is False

    def test_generate_qr_code(self) -> None:
        """Test QR code generation returns valid PNG."""
        secret = self.service.generate_secret()
        qr_bytes = self.service.generate_qr_code(secret, "test@example.com")
        assert isinstance(qr_bytes, bytes)
        assert len(qr_bytes) > 0
        # PNG signature: \x89PNG\r\n\x1a\n
        assert qr_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_totp_uri_format(self) -> None:
        """Test TOTP URI format."""
        secret = self.service.generate_secret()
        uri = self.service.get_totp_uri(secret, "user@example.com")
        assert uri.startswith("otpauth://totp/")
        assert "user%40example.com" in uri  # @ is URL-encoded
        assert "DataMind-King" in uri


class TestTOTPFunctons:
    """Test convenience functions."""

    def test_generate_2fa_secret(self) -> None:
        """Test 2FA secret generation."""
        result = generate_2fa_secret("user@example.com")
        assert "secret" in result
        assert "qr_code_data_uri" in result
        assert len(result["secret"]) == 32
        assert result["qr_code_data_uri"].startswith("data:image/png;base64,")

    def test_verify_2fa_token(self) -> None:
        """Test token verification with known secret."""
        secret = "JBSWY3DPEHPK3PXP"
        from app.core.totp import totp_service
        code = totp_service.get_current_time_based_code(secret)
        assert verify_2fa_token(secret, code) is True

    def test_verify_2fa_invalid_token(self) -> None:
        """Test that invalid 2FA tokens are rejected."""
        secret = "JBSWY3DPEHPK3PXP"
        assert verify_2fa_token(secret, "000000") is False