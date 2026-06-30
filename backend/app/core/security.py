import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return _encode_jwt(payload, settings.jwt_secret_key)


def decode_access_token(token: str) -> dict[str, Any] | None:
    settings = get_settings()
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError:
        return None

    signed = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = _sign(signed, settings.jwt_secret_key)
    actual_signature = _base64url_decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        return None

    try:
        payload = json.loads(_base64url_decode(payload_segment))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int) or expires_at < int(datetime.now(timezone.utc).timestamp()):
        return None
    return payload


def _encode_jwt(payload: dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signed = f"{header_segment}.{payload_segment}".encode("ascii")
    signature_segment = _base64url_encode(_sign(signed, secret))
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _sign(value: bytes, secret: str) -> bytes:
    return hmac.new(secret.encode("utf-8"), value, hashlib.sha256).digest()


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)

