---
title: Prediction Attrition API
emoji: 🔮
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# API Prediction d'Attrition — Futurisys

API REST deployee en production pour predire le risque d'attrition des employes de Futurisys, basee sur un modele XGBoost entraine sur des donnees RH historiques (Projet 4).

## Architecture technique

| Composant | Technologie |
|-----------|-------------|
| **API** | FastAPI (Python 3.11) |
| **Modele ML** | XGBoost (serialise avec joblib) |
| **Base de donnees** | PostgreSQL via Neon (SQLAlchemy ORM) |
| **Tests** | Pytest + pytest-cov (couverture 97%) |
| **CI/CD** | GitHub Actions |
| **Deploiement** | Hugging Face Spaces (Docker) |

## Installation locale

### Prerequis

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommande) ou pip
- Git

### Etapes

```bash
# 1. Cloner le depot
git clone https://github.com/yparent/projet5-attrition-api.git
cd projet5-attrition-api

# 2. Installer les dependances
uv init && uv add -r requirements.txt
# ou avec pip :
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec votre DATABASE_URL (Neon) et API_KEY

# 4. Creer les tables et inserer les donnees
uv run python scripts/create_db.py
uv run python scripts/insert_data.py

# 5. Lancer l'API
uv run uvicorn app.main:app --reload
```

L'API est accessible sur **http://localhost:8000/docs** (Swagger UI).

## Authentification

L'API utilise une cle API transmise dans le header HTTP `X-API-Key`.

Chaque requete vers les endpoints proteges doit inclure ce header. La cle est stockee en variable d'environnement (jamais en dur dans le code).

### Bonnes pratiques de securite

- Les secrets (DATABASE_URL, API_KEY, HF_TOKEN) ne sont jamais commites dans le code
- En local : fichier `.env` (present dans `.gitignore`)
- En CI/CD : GitHub Secrets
- En production : Hugging Face Spaces Secrets
- Les mots de passe et cles sont transmis via des variables d'environnement uniquement

## Endpoints

| Methode | URL | Auth | Description |
|---------|-----|------|-------------|
| `GET` | `/` | Non | Health check |
| `POST` | `/predict` | Oui | Prediction d'attrition |
| `GET` | `/predictions` | Oui | Historique des predictions |
| `GET` | `/docs` | Non | Documentation Swagger |
| `GET` | `/redoc` | Non | Documentation ReDoc |

### Exemple de requete

```bash
curl -X POST https://yparent-prediction-attrition.hf.space/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -d '{
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
  }'
```

### Exemple de reponse

```json
{
  "prediction": 1,
  "probability_stay": 0.1027,
  "probability_leave": 0.8973,
  "risk_level": "High"
}
```

## Base de donnees

PostgreSQL heberge sur [Neon](https://neon.tech) (serverless).

### Schema UML

```
+-------------------+      +---------------------+
|    employees      |      |  prediction_logs    |
+-------------------+      +---------------------+
| id (PK, auto)     |      | id (PK, auto)       |
| employee_id (UQ)  |      | input_data (TEXT)    |
| age               |      | prediction           |
| genre             |      | probability_leave    |
| departement       |      | risk_level           |
| poste             |      | timestamp            |
| revenu_mensuel    |      +---------------------+
| annees_dans_ent.  |
| heure_suppl.      |
| a_quitte_entr.    |
+-------------------+
```

### Processus de gestion des donnees

1. Les donnees brutes proviennent de 3 fichiers CSV (extrait_sirh, extrait_eval, extrait_sondage)
2. Le script `scripts/insert_data.py` fusionne les 3 CSV et insere les donnees dans la table `employees`
3. Chaque appel a `/predict` est logge dans la table `prediction_logs` avec les entrees, le resultat et le timestamp
4. L'endpoint `/predictions` permet de consulter l'historique des predictions

### Besoins analytiques

La table `prediction_logs` permet de :
- Suivre le volume d'utilisation de l'API dans le temps
- Analyser la distribution des niveaux de risque predits
- Detecter une eventuelle derive du modele (monitoring)
- Produire des tableaux de bord RH sur l'attrition

## Tests

```bash
# Lancer tous les tests avec rapport de couverture
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Generer un rapport HTML
uv run pytest tests/ -v --cov=app --cov-report=html
# Ouvrir htmlcov/index.html
```

### Organisation des tests

- **test_api.py** : tests fonctionnels des endpoints (health, predict, auth, validation, historique)
- **test_predict.py** : tests unitaires de la prediction (structure, probabilites, risk level, encodage)
- **test_database.py** : tests CRUD sur les modeles SQLAlchemy (insertion, requetes, stockage JSON)

## CI/CD

Pipeline GitHub Actions (`.github/workflows/ci-cd.yml`) :

1. **Push sur main/develop** : tests automatiques avec pytest + couverture
2. **Tests OK + push sur main** : deploiement automatique sur Hugging Face Spaces

### Gestion des environnements

| Environnement | BDD | Secrets |
|---------------|-----|---------|
| **Dev** (local) | Neon PostgreSQL | `.env` |
| **Test** (CI) | SQLite en memoire | Variables GitHub Actions |
| **Prod** (HF Spaces) | Neon PostgreSQL | Secrets Hugging Face |

## Deploiement

L'API est deployee automatiquement sur Hugging Face Spaces via Docker.

**API en production** : https://yparent-prediction-attrition.hf.space/docs

### Deploiement manuel

```bash
pip install huggingface_hub
hf upload yparent/prediction-attrition . . --repo-type space
```

## Structure du projet

```
projet5-attrition-api/
├── app/
│   ├── __init__.py
│   ├── main.py            # Point d'entree FastAPI
│   ├── models.py           # Schemas Pydantic
│   ├── database.py         # Configuration SQLAlchemy
│   ├── db_models.py        # Modeles de tables SQL
│   ├── predict.py          # Logique de prediction
│   └── auth.py             # Authentification API Key
├── tests/
│   ├── conftest.py          # Fixtures Pytest
│   ├── test_api.py          # Tests des endpoints
│   ├── test_predict.py      # Tests du modele
│   └── test_database.py     # Tests de la BDD
├── model/
│   ├── xgboost_model.joblib # Modele XGBoost serialise
│   └── columns.json         # Colonnes attendues par le modele
├── scripts/
│   ├── create_db.py         # Creation des tables Neon
│   └── insert_data.py       # Insertion du dataset
├── data/                    # CSV du Projet 4
├── .github/workflows/
│   └── ci-cd.yml            # Pipeline CI/CD
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Auteur

**Yohan Parent** — OpenClassrooms, Parcours AI Engineer (2026)
