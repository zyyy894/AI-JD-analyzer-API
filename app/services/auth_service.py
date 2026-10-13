"""Password hashing and JWT verification using established libraries."""
import time
from typing import Any
import bcrypt
import jwt
from pwdlib import PasswordHash
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_SECRET_KEY

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        return password_hasher.verify(password, stored_hash)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str, role: str) -> str:
    now = int(time.time())
    return jwt.encode({"sub": user_id, "iat": now, "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60}, AUTH_SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, AUTH_SECRET_KEY, algorithms=["HS256"], options={"require": ["sub", "iat", "exp"]})
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid or expired token") from exc
