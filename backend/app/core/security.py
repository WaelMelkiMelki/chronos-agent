"""Password hashing, JWT issuance, and symmetric encryption for OAuth tokens."""


from datetime import UTC, datetime, timedelta
from typing import Any, Literal


import jwt
from cryptography.fernet import Fernet, InvalidToken
from pwdlib import PasswordHash


from app.core.config import get_settings


_password_hash = PasswordHash.recommended()




# ─── Passwords ──────────────────────────────────
def hash_password(password: str) -> str:
    return _password_hash.hash(password)




def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)




# ─── JWT ────────────────────────────────────────
TokenType = Literal["access", "refresh"]




def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.app_secret_key, algorithm=settings.jwt_algorithm)




def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )




def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.jwt_refresh_token_expire_days),
    )




def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.app_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected {expected_type} token")
    return payload




# ─── Fernet (OAuth tokens at rest) ──────────────
def _fernet() -> Fernet:
    return Fernet(get_settings().fernet_key.encode())




def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()




def decrypt_secret(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as e:
        raise ValueError("Unable to decrypt secret (invalid FERNET_KEY?)") from e
