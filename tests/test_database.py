from app.db_models import Employee, PredictionLog


def test_create_employee(db_session):
    emp = Employee(employee_id=1, age=30, genre="M", departement="R&D",
                   poste="Dev", revenu_mensuel=5000.0,
                   annees_dans_l_entreprise=3, heure_supplementaires="Non",
                   a_quitte_l_entreprise=0)
    db_session.add(emp)
    db_session.commit()
    result = db_session.query(Employee).first()
    assert result is not None
    assert result.employee_id == 1
    assert result.age == 30


def test_create_prediction_log(db_session):
    log = PredictionLog(input_data='{"age": 35}', prediction=0,
                        probability_leave=0.18, risk_level="Low")
    db_session.add(log)
    db_session.commit()
    result = db_session.query(PredictionLog).first()
    assert result.prediction == 0
    assert result.risk_level == "Low"


def test_query_by_department(db_session):
    for i in range(3):
        db_session.add(Employee(employee_id=100+i, departement="R&D",
                                age=30+i, revenu_mensuel=4000))
    db_session.add(Employee(employee_id=200, departement="RH",
                            age=28, revenu_mensuel=3500))
    db_session.commit()
    assert db_session.query(Employee).filter(Employee.departement == "R&D").count() == 3


def test_prediction_log_text_storage(db_session):
    import json
    data = json.dumps({"age": 42, "departement": "Commercial"})
    log = PredictionLog(input_data=data, prediction=1,
                        probability_leave=0.65, risk_level="High")
    db_session.add(log)
    db_session.commit()
    result = db_session.query(PredictionLog).first()
    assert json.loads(result.input_data)["age"] == 42

def test_get_db_generator():
    """Tester le generateur get_db (lignes manquantes de database.py)."""
    from app.database import get_db
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass

def test_get_db_generator():
    """Couvrir le generateur get_db."""
    from app.database import get_db
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass


def test_database_postgresql_branch(monkeypatch):
    """Couvrir la branche non-SQLite de database.py."""
    import importlib
    import app.database

    # Simuler une URL PostgreSQL
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")

    # Recharger le module pour re-executer le if/else
    importlib.reload(app.database)

    # Verifier que connect_args est vide (pas de check_same_thread)
    assert app.database.connect_args == {}

    # Remettre SQLite pour ne pas casser les autres tests
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    importlib.reload(app.database)