from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, unique=True, index=True)
    age = Column(Integer)
    genre = Column(String(10))
    departement = Column(String(100))
    poste = Column(String(100))
    revenu_mensuel = Column(Float)
    annees_dans_l_entreprise = Column(Integer)
    heure_supplementaires = Column(String(10))
    a_quitte_l_entreprise = Column(Integer)


class PredictionLog(Base):
    __tablename__ = 'prediction_logs'
    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(Text)
    prediction = Column(Integer)
    probability_leave = Column(Float)
    risk_level = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
