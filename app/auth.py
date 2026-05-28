"""
Authentification par cle API (header X-API-Key).

Mecanisme simple mais efficace pour un contexte interne :
- Le client envoie sa cle dans le header HTTP "X-API-Key"
- Le serveur compare avec la cle stockee en variable d'environnement
- Si la cle est absente ou invalide -> erreur 401 Unauthorized

La cle n'est jamais ecrite en dur dans le code : elle est lue depuis
la variable d'environnement API_KEY (definie dans .env ou secrets GitHub).
"""

import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (ignore si absent)
load_dotenv()

# ---------------------------------------------------------------------------
# Cle API lue depuis l'environnement (avec valeur par defaut pour le dev)
# ---------------------------------------------------------------------------
API_KEY = os.getenv("API_KEY", "dev-key-technova-2026")

# ---------------------------------------------------------------------------
# Definition du header attendu par FastAPI
# auto_error=False : on gere nous-memes le message d'erreur (401)
# au lieu du 403 par defaut de FastAPI
# ---------------------------------------------------------------------------
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Dependance FastAPI : verifie la cle API dans le header.

    Utilisee avec Depends(verify_api_key) sur les endpoints proteges.
    Renvoie la cle si valide, leve une HTTPException 401 sinon.

    Args:
        api_key: valeur du header X-API-Key, extraite automatiquement
                 par FastAPI grace a APIKeyHeader.

    Returns:
        La cle API (str) si elle est valide.

    Raises:
        HTTPException 401: si la cle est absente ou ne correspond pas.
    """
    if api_key is None or api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Cle API invalide ou manquante. Ajoutez le header X-API-Key."
        )
    return api_key
