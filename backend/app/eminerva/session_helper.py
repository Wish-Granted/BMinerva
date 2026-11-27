from flask import session, jsonify
import requests

from ..auth.eminerva_client import build_session
from ..utils.crypto import decrypt_json

def get_eminerva_session() -> requests.Session | None:
    encrypted = session.get("eminerva_cookies")
    eminerva_cookies = decrypt_json(encrypted) if encrypted else None
    
    if not eminerva_cookies:
        return None
    
    return build_session(eminerva_cookies)
