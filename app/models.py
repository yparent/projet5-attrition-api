"""
Schemas Pydantic pour la validation des donnees entrantes et sortantes.

Pydantic verifie automatiquement les types et les contraintes (age >= 18,
salaire > 0, satisfaction entre 1 et 4, etc.). Si une requete ne respecte
pas le schema, l'API renvoie une erreur 422 avec un message explicite
— sans qu'on ait besoin d'ecrire du code de verification manuellement.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Enumeration des niveaux d'etude acceptes
# ---------------------------------------------------------------------------
class NiveauEtude(str, Enum):
    """Niveaux d'etude reconnus par le modele (encodage ordinal)."""
    BAC = "Bac"
    LICENCE = "Licence"
    MASTER = "Master"
    DOCTORAT = "Doctorat"


# ===========================================================================
# Schema d'entree : donnees d'un employe pour la prediction
# ===========================================================================
class EmployeeInput(BaseModel):
    """
    Caracteristiques d'un employe envoyees a l'API pour prediction.

    Les champs obligatoires (...) doivent etre fournis dans chaque requete.
    Les champs optionnels ont une valeur par defaut et peuvent etre omis.
    Les contraintes (ge, le, gt) sont verifiees automatiquement par Pydantic.
    """

    # --- Donnees personnelles ---
    age: int = Field(..., ge=18, le=70,
        description="Age de l'employe")

    # --- Donnees professionnelles ---
    anciennete: int = Field(..., ge=0,
        description="Nombre d'annees dans l'entreprise")
    salaire_mensuel: float = Field(..., gt=0,
        description="Salaire mensuel en euros")
    distance_domicile: int = Field(..., ge=0,
        description="Distance domicile-travail en km")
    annee_experience_totale: int = Field(..., ge=0,
        description="Annees d'experience totale")
    heures_supplementaires: str = Field(...,
        description="Oui ou Non")
    nombre_entreprises_precedentes: int = Field(default=0, ge=0)
    annee_poste_actuel: int = Field(default=0, ge=0)
    annee_derniere_promotion: int = Field(default=0, ge=0)
    annee_meme_manager: int = Field(default=0, ge=0)

    # --- Satisfaction (echelle 1 a 4) ---
    satisfaction_travail: int = Field(..., ge=1, le=4,
        description="Niveau de satisfaction (1-4)")
    satisfaction_environnement: int = Field(..., ge=1, le=4,
        description="Satisfaction environnement (1-4)")
    satisfaction_relation: int = Field(..., ge=1, le=4,
        description="Satisfaction relations (1-4)")
    equilibre_vie_travail: int = Field(..., ge=1, le=4,
        description="Equilibre vie/travail (1-4)")

    # --- Champs optionnels ---
    niveau_etude: Optional[str] = Field(default='Licence')
    departement: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)

    class Config:
        """Exemple de requete affiche dans la doc Swagger."""
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


# ===========================================================================
# Schema de sortie : resultat de la prediction
# ===========================================================================
class PredictionOutput(BaseModel):
    """Resultat renvoye par l'endpoint /predict."""

    prediction: int = Field(
        description="0 = reste, 1 = part")
    probability_stay: float = Field(
        description="Probabilite de rester (0 a 1)")
    probability_leave: float = Field(
        description="Probabilite de partir (0 a 1)")
    risk_level: str = Field(
        description="Niveau de risque : Low / Medium / High")


# ===========================================================================
# Schema du health check
# ===========================================================================
class HealthResponse(BaseModel):
    """Reponse de l'endpoint de sante GET /."""

    status: str = "ok"
    model_loaded: bool = True
    version: str = "1.0.0"
