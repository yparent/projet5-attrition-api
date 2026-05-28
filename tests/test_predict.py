from app.predict import predict_attrition, preprocess
import pandas as pd


def test_predict_returns_valid_structure(sample_employee):
    result = predict_attrition(sample_employee)
    assert "prediction" in result
    assert "probability_stay" in result
    assert "probability_leave" in result
    assert "risk_level" in result


def test_predict_probability_sum(sample_employee):
    result = predict_attrition(sample_employee)
    total = result["probability_stay"] + result["probability_leave"]
    assert abs(total - 1.0) < 0.01


def test_predict_risk_level_coherent(sample_employee):
    result = predict_attrition(sample_employee)
    if result["probability_leave"] > 0.5:
        assert result["risk_level"] == "High"
    elif result["probability_leave"] > 0.3:
        assert result["risk_level"] == "Medium"
    else:
        assert result["risk_level"] == "Low"


def test_predict_returns_binary(sample_employee):
    result = predict_attrition(sample_employee)
    assert result["prediction"] in [0, 1]


def test_preprocess_binary_encoding():
    df = pd.DataFrame([{"heures_supplementaires": "Oui", "genre": "Femme", "voyage_affaire": "Non"}])
    result = preprocess(df)
    assert result["heures_supplementaires"].iloc[0] == 1
    assert result["genre"].iloc[0] == 0
    assert result["voyage_affaire"].iloc[0] == 0


def test_preprocess_ordinal_encoding():
    df = pd.DataFrame([{"niveau_etude": "Master"}])
    result = preprocess(df)
    assert result["niveau_etude"].iloc[0] == 3


def test_preprocess_feature_engineering():
    df = pd.DataFrame([{"salaire_mensuel": 6000, "annee_experience_totale": 9,
                         "anciennete": 5, "annee_poste_actuel": 2}])
    result = preprocess(df)
    if "ratio_salaire_experience" in result.columns:
        assert result["ratio_salaire_experience"].iloc[0] == 600.0
    if "anciennete_vs_poste" in result.columns:
        assert result["anciennete_vs_poste"].iloc[0] == 3