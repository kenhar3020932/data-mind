"""TOTP 2FA for DataMind-King."""

from __future__ import annotations

import base64
import qrcode
from io import BytesIO
from typing import Optional

import pyotp


class TOTPService:
    """Two-factor authentication service using TOTP."""

    def __init__(self, secret_length: int = 32) -> None:
        self.secret_length = secret_length

    def generate_secret(self) -> str:
        """Generate a new TOTP secret (minimum 160 bits = 32 base32 chars)."""
        return pyotp.random_base32(self.secret_length)

    def get_totp_uri(self, secret: str, user_email: str, issuer: str = "DataMind-King") -> str:
        """Get the OTP URI for QR code generation."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=issuer)

    def verify_token(self, secret: str, token: str) -> bool:
        """Verify a TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

    def generate_qr_code(self, secret: str, user_email: str) -> bytes:
        """Generate QR code image as bytes."""
        uri = self.get_totp_uri(secret, user_email)
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def get_current_time_based_code(self, secret: str) -> str:
        """Get current time-based OTP code for testing."""
        totp = pyotp.TOTP(secret)
        return totp.now()


# Module-level singleton
totp_service = TOTPService()


def generate_2fa_secret(user_email: str) -> dict:
    """Generate 2FA secret and QR code for a user."""
    secret = totp_service.generate_secret()
    qr_bytes = totp_service.generate_qr_code(secret, user_email)
    return {
        "secret": secret,
        "qr_code_data_uri": f"data:image/png;base64,{base64.b64encode(qr_bytes).decode()}",
    }


def verify_2fa_token(secret: str, token: str) -> bool:
    """Verify a 2FA token against the secret."""
    return totp_service.verify_token(secret, token)