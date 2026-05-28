"""
Modeles SQLAlchemy — definition des tables de la base de donnees.

Deux tables :
- employees        : stocke le dataset RH (importe depuis les CSV du P4)
- prediction_logs  : enregistre chaque appel a l'endpoint /predict
                     (tracabilite des predictions en production)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base


# ===========================================================================
# Table des employes — miroir du dataset CSV consolide
# ===========================================================================
class Employee(Base):
    """
    Table des employes importes depuis le SIRH.

    Stocke les donnees brutes des employes (age, genre, departement, etc.)
    pour consultation et analyse. La colonne a_quitte_l_entreprise
    indique si l'employe a quitte (1) ou est reste (0).
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, unique=True, index=True)  # Identifiant RH unique
    age = Column(Integer)
    genre = Column(String(10))                  # M ou F
    departement = Column(String(100))           # R&D, Commercial, RH
    poste = Column(String(100))                 # Intitule du poste
    revenu_mensuel = Column(Float)              # Salaire mensuel en euros
    annees_dans_l_entreprise = Column(Integer)  # Anciennete
    heure_supplementaires = Column(String(10))  # Oui / Non
    a_quitte_l_entreprise = Column(Integer)     # 0 = reste, 1 = parti


# ===========================================================================
# Journal des predictions — tracabilite des appels a /predict
# ===========================================================================
class PredictionLog(Base):
    """
    Journal des predictions — chaque appel a /predict cree une entree.

    Permet de tracer quel employe a ete evalue, quand, et quel resultat
    a ete retourne. Utile pour l'audit et le monitoring du modele
    en production.

    Note : input_data est stocke en Text (json.dumps) car SQLite
    ne supporte pas nativement le type JSON de PostgreSQL.
    """
    __tablename__ = 'prediction_logs'

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(Text)                   # Donnees d'entree (JSON serialise en str)
    prediction = Column(Integer)                # 0 = reste, 1 = part
    probability_leave = Column(Float)           # Probabilite de depart (0.0 a 1.0)
    risk_level = Column(String(20))             # Low / Medium / High
    timestamp = Column(DateTime, default=datetime.utcnow)  # Date/heure de la prediction
