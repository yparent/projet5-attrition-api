"""
Tests du module de prediction (app/predict.py).

Verifie que :
- La structure du resultat est correcte
- Les probabilites somment a 1
- Le niveau de risque est coherent avec la probabilite
- Le preprocessing encode correctement les variables
- Le feature engineering calcule les bonnes valeurs
"""

from app.predict import predict_attrition, preprocess
import pandas as pd


def test_predict_returns_valid_structure(sample_employee):
    """Le resultat doit contenir les 4 cles attendues."""
    result = predict_attrition(sample_employee)
    assert "prediction" in result
    assert "probability_stay" in result
    assert "probability_leave" in result
    assert "risk_level" in result


def test_predict_probability_sum(sample_employee):
    """La somme des probabilites (rester + partir) doit valoir ~1.0."""
    result = predict_attrition(sample_employee)
    total = result["probability_stay"] + result["probability_leave"]
    assert abs(total - 1.0) < 0.01


def test_predict_risk_level_coherent(sample_employee):
    """Le risk_level doit correspondre aux seuils definis (0.5/0.3)."""
    result = predict_attrition(sample_employee)
    if result["probability_leave"] > 0.5:
        assert result["risk_level"] == "High"
    elif result["probability_leave"] > 0.3:
        assert result["risk_level"] == "Medium"
    else:
        assert result["risk_level"] == "Low"


def test_predict_returns_binary(sample_employee):
    """La prediction doit etre 0 (reste) ou 1 (part)."""
    result = predict_attrition(sample_employee)
    assert result["prediction"] in [0, 1]


def test_preprocess_binary_encoding():
    """Heures sup, genre et voyage doivent etre encodes en 0/1."""
    df = pd.DataFrame([{"heures_supplementaires": "Oui", "genre": "Femme", "voyage_affaire": "Non"}])
    result = preprocess(df)
    assert result["heures_supplementaires"].iloc[0] == 1  # Oui -> 1
    assert result["genre"].iloc[0] == 0                    # Femme -> 0
    assert result["voyage_affaire"].iloc[0] == 0           # Non -> 0


def test_preprocess_ordinal_encoding():
    """Niveau etude doit etre encode en ordinal (Bac=1, ..., Doctorat=4)."""
    df = pd.DataFrame([{"niveau_etude": "Master"}])
    result = preprocess(df)
    assert result["niveau_etude"].iloc[0] == 3  # Master -> 3


def test_preprocess_feature_engineering():
    """Les features derivees doivent etre calculees correctement."""
    df = pd.DataFrame([{"salaire_mensuel": 6000, "annee_experience_totale": 9,
                         "anciennete": 5, "annee_poste_actuel": 2}])
    result = preprocess(df)
    # ratio = 6000 / (9 + 1) = 600.0
    if "ratio_salaire_experience" in result.columns:
        assert result["ratio_salaire_experience"].iloc[0] == 600.0
    # anciennete_vs_poste = 5 - 2 = 3
    if "anciennete_vs_poste" in result.columns:
        assert result["anciennete_vs_poste"].iloc[0] == 3
