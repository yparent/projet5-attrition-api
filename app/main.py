"""
Point d'entree de l'API FastAPI — TechNova Partners.

Endpoints :
    GET  /             -> Health check (verifie que l'API est operationnelle)
    POST /predict      -> Prediction d'attrition pour un employe
    GET  /predictions  -> Historique des predictions enregistrees

L'API utilise :
- Pydantic pour la validation automatique des entrees/sorties
- SQLAlchemy pour le logging des predictions en base de donnees
- Une cle API (header X-API-Key) pour securiser les endpoints
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

from app.models import EmployeeInput, PredictionOutput, HealthResponse
from app.predict import predict_attrition
from app.auth import verify_api_key
from app.database import get_db, engine
from app.db_models import Base, PredictionLog
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Creation des tables au demarrage (si elles n'existent pas encore)
# Base.metadata.create_all() est idempotent : il ne recree pas les tables
# deja existantes.
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Initialisation de l'application FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="API Prediction Attrition - TechNova Partners",
    description="API REST pour predire le risque d'attrition des employes",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI accessible a /docs
    redoc_url="/redoc",    # Documentation ReDoc alternative a /redoc
)

# ---------------------------------------------------------------------------
# Middleware CORS — autorise les appels depuis n'importe quel domaine
# (acceptable pour un projet pedagogique ; en production, restreindre
# allow_origins aux domaines autorises)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=['*'],
    allow_headers=['*'],
)


# ===========================================================================
# ENDPOINTS
# ===========================================================================


@app.get("/", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Endpoint de sante : verifie que l'API fonctionne."""
    return HealthResponse()


@app.post("/predict",
    response_model=PredictionOutput,
    tags=["Prediction"],
    summary="Predire l'attrition d'un employe"
)
def predict(
    employee: EmployeeInput,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Recoit les donnees d'un employe et retourne la prediction d'attrition
    avec le niveau de risque (Low / Medium / High).

    Les donnees sont validees automatiquement par Pydantic. La prediction
    est enregistree dans la table prediction_logs pour tracabilite.
    """
    # Appeler le module de prediction avec les donnees de l'employe
    result = predict_attrition(employee.model_dump())

    # Enregistrer la prediction en base de donnees pour tracabilite
    # Note : input_data est serialise en JSON (str) car la colonne est Text
    log = PredictionLog(
        input_data=json.dumps(employee.model_dump()),
        prediction=result['prediction'],
        probability_leave=result['probability_leave'],
        risk_level=result['risk_level'],
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()

    return PredictionOutput(**result)


@app.get("/predictions",
    tags=["Prediction"],
    summary="Historique des predictions"
)
def get_predictions(
    skip: int = 0,
    limit: int = 50,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Recupere l'historique des predictions enregistrees.

    Parametres de pagination :
    - skip  : nombre d'entrees a ignorer (defaut 0)
    - limit : nombre maximum d'entrees retournees (defaut 50)
    """
    predictions = db.query(PredictionLog).offset(skip).limit(limit).all()
    return predictions
