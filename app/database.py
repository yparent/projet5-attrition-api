"""
Configuration de la connexion a la base de donnees.

Utilise SQLAlchemy comme ORM. La variable DATABASE_URL est lue depuis
l'environnement (.env en local, secrets GitHub en CI, variables HF en prod).

Exemples de DATABASE_URL :
    PostgreSQL (Neon) : postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
    SQLite (tests CI) : sqlite:///./test.db
    Fallback (dev)    : sqlite:///./fallback.db
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# URL de connexion — lue depuis l'environnement, avec fallback SQLite
# pour le developpement local sans base PostgreSQL configuree
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./fallback.db')

# ---------------------------------------------------------------------------
# Parametre specifique a SQLite : check_same_thread=False est necessaire
# car FastAPI utilise plusieurs threads, ce que SQLite n'autorise pas
# par defaut. Ce parametre n'est PAS necessaire pour PostgreSQL.
# ---------------------------------------------------------------------------
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {'check_same_thread': False}

# ---------------------------------------------------------------------------
# Moteur SQLAlchemy — point d'entree pour toutes les operations BDD
# ---------------------------------------------------------------------------
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# ---------------------------------------------------------------------------
# Fabrique de sessions — chaque requete API obtient sa propre session
# autocommit=False : on gere les transactions manuellement (db.commit())
# autoflush=False  : pas de flush automatique avant chaque requete
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Classe de base pour les modeles SQLAlchemy (Employee, PredictionLog)
# Tous les modeles heritent de Base pour etre detectes par create_all()
# ---------------------------------------------------------------------------
Base = declarative_base()


def get_db():
    """
    Generateur de session BDD — utilise comme dependance FastAPI.

    Cree une session, la fournit a l'endpoint via `yield`, puis la ferme
    automatiquement apres la reponse (meme en cas d'erreur).

    Usage dans un endpoint :
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
