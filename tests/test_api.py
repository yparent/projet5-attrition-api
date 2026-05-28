"""
Tests des endpoints de l'API (app/main.py).

Couvre les 3 endpoints :
- GET  /            : health check
- POST /predict     : prediction d'attrition (succes, erreurs, auth)
- GET  /predictions : historique (succes, auth)
"""


def test_health_check(client):
    """GET / doit retourner status=ok et model_loaded=True."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_predict_success(client, api_headers, sample_employee):
    """POST /predict avec donnees valides doit retourner une prediction."""
    response = client.post("/predict", json=sample_employee, headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability_leave"] <= 1
    assert 0 <= data["probability_stay"] <= 1
    assert data["risk_level"] in ["Low", "Medium", "High"]


def test_predict_without_api_key(client, sample_employee):
    """POST /predict sans header X-API-Key doit retourner 401."""
    response = client.post("/predict", json=sample_employee)
    assert response.status_code == 401


def test_predict_invalid_api_key(client, sample_employee):
    """POST /predict avec une mauvaise cle doit retourner 401."""
    response = client.post("/predict", json=sample_employee, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_predict_invalid_data(client, api_headers):
    """POST /predict avec age negatif doit retourner 422 (validation Pydantic)."""
    bad = {"age": -5, "anciennete": 5, "salaire_mensuel": 4500.0,
           "satisfaction_travail": 3, "satisfaction_environnement": 3,
           "satisfaction_relation": 4, "equilibre_vie_travail": 3,
           "heures_supplementaires": "Non", "distance_domicile": 10,
           "annee_experience_totale": 12}
    response = client.post("/predict", json=bad, headers=api_headers)
    assert response.status_code == 422


def test_predict_missing_field(client, api_headers):
    """POST /predict avec champs obligatoires manquants doit retourner 422."""
    response = client.post("/predict", json={"age": 35}, headers=api_headers)
    assert response.status_code == 422


def test_predictions_history(client, api_headers, sample_employee):
    """GET /predictions doit retourner l'historique apres une prediction."""
    # D'abord creer une prediction
    client.post("/predict", json=sample_employee, headers=api_headers)
    # Puis verifier qu'elle apparait dans l'historique
    response = client.get("/predictions", headers=api_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_predictions_requires_auth(client):
    """GET /predictions sans cle API doit retourner 401."""
    response = client.get("/predictions")
    assert response.status_code == 401
