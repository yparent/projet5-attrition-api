# app/auth.py
import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_KEY", "dev-key-technova-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)




def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifier la cle API dans le header."""
    if api_key is None or api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Cle API invalide ou manquante. Ajoutez le header X-API-Key."
        )
    return api_key
