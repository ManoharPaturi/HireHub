# Authentication helpers: passwords are compared using the stored format, and
# JWTs (signed login tokens) let later requests identify the signed-in account.
# Signing detects token changes; it does not encrypt the token contents.

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings

# Produce the existing sha256$ storage format used by this project.
# This is a fast, unsalted digest, not a password-specific slow hash.
def get_password_hash(password: str) -> str:
    # Preserve the existing SHA-256 format; all input bytes feed the digest.
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return f"sha256${hashed}"

# Recreate the stored digest for comparison. Older non-prefixed records
# use the legacy direct-string comparison branch.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("sha256$"):
        target_hash = f"sha256${hashlib.sha256(plain_password.encode('utf-8')).hexdigest()}"
        return target_hash == hashed_password
    # Fallback comparison for standard strings
    return plain_password == hashed_password

# Add an expiry time and sign the claims. The sub claim identifies the user;
# later requests send the resulting token in the Authorization header.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Verify the signature and expiry. Invalid or expired tokens return None
# so the calling authentication dependency can reject the request.
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
