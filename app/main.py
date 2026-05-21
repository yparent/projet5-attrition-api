# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime


from app.models import EmployeeInput, PredictionOutput, HealthResponse
from app.predict import predict_attrition
from app.auth import verify_api_key
from app.database import get_db, engine
from app.db_models import Base, PredictionLog
from sqlalchemy.orm import Session


# Creer les tables au demarrage
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API Prediction Attrition - TechNova Partners",
    description="API REST pour predire le risque d'attrition des employes",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc alternative
)


# CORS : autoriser les requetes depuis d'autres domaines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=['*'],
    allow_headers=['*'],
)




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
    Envoie les donnees d'un employe et recoit la prediction
    d'attrition avec le niveau de risque.
    """
    # Faire la prediction
    result = predict_attrition(employee.model_dump())
    
    # Logger la prediction en base de donnees
    log = PredictionLog(
        input_data=employee.model_dump(),
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
    """Recuperer l'historique des predictions loguees."""
    predictions = db.query(PredictionLog).offset(skip).limit(limit).all()
    return predictions
