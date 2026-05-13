# app/predict.py
import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path


# Chemins vers les fichiers du modele
MODEL_DIR = Path(__file__).parent.parent / 'model'
MODEL_PATH = MODEL_DIR / 'xgboost_model.joblib'
COLUMNS_PATH = MODEL_DIR / 'columns.json'


# Charger le modele et les colonnes au demarrage
model = joblib.load(MODEL_PATH)
with open(COLUMNS_PATH, 'r') as f:
    expected_columns = json.load(f)




def predict_attrition(data: dict) -> dict:
    """Predire l'attrition pour un employe."""
    df = pd.DataFrame([data])
    
    # Appliquer le meme encodage que dans le notebook
    df = preprocess(df)
    
    # S'assurer que les colonnes correspondent
    df = df.reindex(columns=expected_columns, fill_value=0)
    
    # Prediction
    proba = model.predict_proba(df)[0]
    prediction = int(model.predict(df)[0])
    
    return {
        "prediction": prediction,
        "probability_stay": round(float(proba[0]), 4),
        "probability_leave": round(float(proba[1]), 4),
        "risk_level": "High" if proba[1] > 0.5 else
                      "Medium" if proba[1] > 0.3 else "Low"
    }




def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Appliquer les memes transformations que le notebook P4."""
    # Encodage binaire
    binary_map = {
        'heures_supplementaires': {'Oui': 1, 'Non': 0},
        'voyage_affaire': {'Oui': 1, 'Non': 0},
        'genre': {'Homme': 1, 'Femme': 0},
    }
    for col, mapping in binary_map.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)
    
    # Encodage ordinal
    ordinal_maps = {
        'niveau_etude': {'Bac': 1, 'Licence': 2, 'Master': 3, 'Doctorat': 4},
        'implication_travail': {'Faible': 1, 'Moyen': 2, 'Fort': 3, 'Tres fort': 4},
    }
    for col, mapping in ordinal_maps.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(1).astype(int)
    
    # One-Hot encoding (meme que pd.get_dummies avec drop_first)
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    # Feature engineering (meme que le notebook P4)
    if 'salaire_mensuel' in df.columns and 'annee_experience_totale' in df.columns:
        df['ratio_salaire_experience'] = (
            df['salaire_mensuel'] / (df['annee_experience_totale'] + 1)
        )
    if 'anciennete' in df.columns and 'annee_poste_actuel' in df.columns:
        df['anciennete_vs_poste'] = df['anciennete'] - df['annee_poste_actuel']
    
    return df