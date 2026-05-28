"""
Fixtures Pytest partagees entre tous les fichiers de test.

Fournit :
- db_session  : session SQLAlchemy connectee a une base SQLite de test
- client      : client HTTP FastAPI avec la BDD de test injectee
- api_headers : headers d'authentification valides
- sample_employee : jeu de donnees employe type pour les tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

# ---------------------------------------------------------------------------
# Base de donnees de test — SQLite locale, isolee de la prod (Neon)
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine_test = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    """
    Cree une base de donnees propre pour chaque test.

    - create_all : cree les tables avant le test
    - yield      : fournit la session au test
    - drop_all   : nettoie les tables apres le test (isolation)
    """
    Base.metadata.create_all(bind=engine_test)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Client HTTP de test avec injection de la BDD de test.

    Remplace la dependance get_db de FastAPI par notre session de test
    pour que les endpoints utilisent SQLite au lieu de Neon.
    """
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    """Headers d'authentification valides pour les endpoints proteges."""
    return {"X-API-Key": "dev-key-technova-2026", "Content-Type": "application/json"}


@pytest.fixture
def sample_employee():
    """
    Jeu de donnees employe type pour les tests.

    Correspond exactement au schema EmployeeInput de models.py
    avec des valeurs realistes.
    """
    return {
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
        "role": "Data Scientist",
    }
