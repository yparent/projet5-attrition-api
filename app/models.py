# app/models.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum




class NiveauEtude(str, Enum):
    BAC = "Bac"
    LICENCE = "Licence"
    MASTER = "Master"
    DOCTORAT = "Doctorat"




class EmployeeInput(BaseModel):
    """Schema d'entree pour la prediction d'attrition."""
    age: int = Field(..., ge=18, le=70,
        description="Age de l'employe")
    anciennete: int = Field(..., ge=0,
        description="Nombre d'annees dans l'entreprise")
    salaire_mensuel: float = Field(..., gt=0,
        description="Salaire mensuel en euros")
    satisfaction_travail: int = Field(..., ge=1, le=4,
        description="Niveau de satisfaction (1-4)")
    satisfaction_environnement: int = Field(..., ge=1, le=4,
        description="Satisfaction environnement (1-4)")
    satisfaction_relation: int = Field(..., ge=1, le=4,
        description="Satisfaction relations (1-4)")
    equilibre_vie_travail: int = Field(..., ge=1, le=4,
        description="Equilibre vie/travail (1-4)")
    heures_supplementaires: str = Field(...,
        description="Oui ou Non")
    distance_domicile: int = Field(..., ge=0,
        description="Distance domicile-travail en km")
    annee_experience_totale: int = Field(..., ge=0,
        description="Annees d'experience totale")
    nombre_entreprises_precedentes: int = Field(default=0, ge=0)
    annee_poste_actuel: int = Field(default=0, ge=0)
    annee_derniere_promotion: int = Field(default=0, ge=0)
    annee_meme_manager: int = Field(default=0, ge=0)
    niveau_etude: Optional[str] = Field(default='Licence')
    departement: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)


    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "anciennete": 5,
                "salaire_mensuel": 4500.0,
                "satisfaction_travail": 3,
                "satisfaction_environnement": 3,
                "satisfaction_relation": 4,
                "equilibre_vie_travail": 3,
                "heures_supplementaires": "Non",
                "distance_domicile": 10,
                "annee_experience_totale": 12,
                "nombre_entreprises_precedentes": 2,
                "annee_poste_actuel": 3,
                "annee_derniere_promotion": 1,
                "annee_meme_manager": 3,
                "niveau_etude": "Master",
                "departement": "R&D",
                "role": "Data Scientist"
            }
        }




class PredictionOutput(BaseModel):
    """Schema de sortie de la prediction."""
    prediction: int = Field(
        description="0 = reste, 1 = part")
    probability_stay: float = Field(
        description="Probabilite de rester")
    probability_leave: float = Field(
        description="Probabilite de partir")
    risk_level: str = Field(
        description="Low / Medium / High")




class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool = True
    version: str = "1.0.0"
