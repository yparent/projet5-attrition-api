"""
Module de prediction d'attrition.

Charge le modele XGBoost serialise (joblib) et la liste des colonnes
attendues (columns.json). Reproduit exactement le meme preprocessing
que le notebook du Projet 4 pour garantir la coherence des predictions.

Pipeline :
    1. Recevoir un dict (donnees employe)
    2. Convertir en DataFrame pandas
    3. Appliquer le preprocessing (encodage + feature engineering)
    4. Aligner les colonnes sur celles du modele
    5. Predire avec predict_proba() et predict()
    6. Retourner prediction + probabilites + niveau de risque
"""

import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins vers les fichiers du modele (relatifs a la racine du projet)
# ---------------------------------------------------------------------------
MODEL_DIR = Path(__file__).parent.parent / 'model'
MODEL_PATH = MODEL_DIR / 'xgboost_model.joblib'
COLUMNS_PATH = MODEL_DIR / 'columns.json'

# ---------------------------------------------------------------------------
# Chargement du modele et des colonnes au demarrage de l'application
# (une seule fois, puis reutilises pour chaque requete — pas de rechargement)
# ---------------------------------------------------------------------------
model = joblib.load(MODEL_PATH)
with open(COLUMNS_PATH, 'r') as f:
    expected_columns = json.load(f)


# ===========================================================================
# FONCTION PRINCIPALE DE PREDICTION
# ===========================================================================
def predict_attrition(data: dict) -> dict:
    """
    Predit l'attrition pour un employe.

    Args:
        data: dictionnaire contenant les caracteristiques de l'employe
              (memes noms de colonnes que le dataset d'origine).

    Returns:
        dict avec les cles :
            - prediction (int)       : 0 = reste, 1 = part
            - probability_stay (float) : probabilite de rester (0-1)
            - probability_leave (float): probabilite de partir (0-1)
            - risk_level (str)       : "High", "Medium" ou "Low"
    """
    # Construire un DataFrame a une ligne a partir du dictionnaire
    df = pd.DataFrame([data])

    # Appliquer le meme preprocessing que dans le notebook P4
    df = preprocess(df)

    # Aligner les colonnes sur celles attendues par le modele.
    # Les colonnes manquantes sont remplies a 0 (One-Hot absent = categorie
    # non representee), les colonnes en trop sont ignorees.
    df = df.reindex(columns=expected_columns, fill_value=0)

    # Prediction : proba[0] = rester, proba[1] = partir
    proba = model.predict_proba(df)[0]
    prediction = int(model.predict(df)[0])

    # Determiner le niveau de risque selon les seuils definis
    return {
        "prediction": prediction,
        "probability_stay": round(float(proba[0]), 4),
        "probability_leave": round(float(proba[1]), 4),
        "risk_level": "High" if proba[1] > 0.5 else
                      "Medium" if proba[1] > 0.3 else "Low"
    }


# ===========================================================================
# PREPROCESSING — doit reproduire EXACTEMENT le notebook P4
# ===========================================================================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les memes transformations que le notebook du Projet 4 :
    1. Encodage binaire (heures sup, voyage, genre)
    2. Encodage ordinal (niveau etude, implication travail)
    3. One-Hot Encoding automatique sur les colonnes object restantes
    4. Feature engineering (ratio salaire/experience, anciennete vs poste)

    Args:
        df: DataFrame pandas contenant les donnees brutes d'un employe.

    Returns:
        DataFrame transforme, pret pour la prediction.
    """
    # --- 1. Encodage binaire ---
    # Convertir les colonnes Oui/Non et Homme/Femme en 0/1
    binary_map = {
        'heures_supplementaires': {'Oui': 1, 'Non': 0},
        'voyage_affaire': {'Oui': 1, 'Non': 0},
        'genre': {'Homme': 1, 'Femme': 0},
    }
    for col, mapping in binary_map.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)

    # --- 2. Encodage ordinal ---
    # Convertir les niveaux d'etude et d'implication en valeurs numeriques ordonnees
    ordinal_maps = {
        'niveau_etude': {'Bac': 1, 'Licence': 2, 'Master': 3, 'Doctorat': 4},
        'implication_travail': {'Faible': 1, 'Moyen': 2, 'Fort': 3, 'Tres fort': 4},
    }
    for col, mapping in ordinal_maps.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(1).astype(int)

    # --- 3. One-Hot Encoding ---
    # Encoder automatiquement toutes les colonnes textuelles restantes
    # drop_first=True pour eviter la multicolinearite (meme que le notebook)
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    # --- 4. Feature engineering ---
    # Ratio salaire/experience : indicateur de valorisation salariale
    if 'salaire_mensuel' in df.columns and 'annee_experience_totale' in df.columns:
        df['ratio_salaire_experience'] = (
            df['salaire_mensuel'] / (df['annee_experience_totale'] + 1)
        )
    # Anciennete vs poste : temps dans l'entreprise moins temps au poste actuel
    if 'anciennete' in df.columns and 'annee_poste_actuel' in df.columns:
        df['anciennete_vs_poste'] = df['anciennete'] - df['annee_poste_actuel']

    return df
