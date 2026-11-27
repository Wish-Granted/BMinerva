import json
import os

from cryptography.fernet import Fernet, InvalidToken

_fernet = None

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("COOKIE_ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("COOKIE_ENCRYPTION_KEY is not set")
        _fernet = Fernet(key.encode())
    return _fernet

def encrypt_json(data) -> str:
    return _get_fernet().encrypt(json.dumps(data).encode()).decode()

def decrypt_json(token: str):
    #returns None if the token is invalid/tampered (caller treats as logged out).
    try:
        return json.loads(_get_fernet().decrypt(token.encode()))
    except (InvalidToken, ValueError, AttributeError):
        return None