import pytest
from perry.db.session import DatabaseSessionManager


@pytest.fixture(scope="function")
def mock_session_manager_db():
    db_name = "mock_test_db"
    DatabaseSessionManager._db_name = db_name
    yield


def test_singleton_behavior(monkeypatch, mock_session_manager_db):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    engine1 = DatabaseSessionManager.get_engine()
    engine2 = DatabaseSessionManager.get_engine()

    assert engine1 is engine2

    session_local1 = DatabaseSessionManager.get_session_local()
    session_local2 = DatabaseSessionManager.get_session_local()

    assert session_local1 is session_local2


def test_lazy_initialization(monkeypatch, mock_session_manager_db):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    DatabaseSessionManager._engine = None
    DatabaseSessionManager._SessionLocal = None

    assert DatabaseSessionManager._engine is None
    assert DatabaseSessionManager._SessionLocal is None

    DatabaseSessionManager.get_engine()
    DatabaseSessionManager.get_session_local()

    assert DatabaseSessionManager._engine is not None
    assert DatabaseSessionManager._SessionLocal is not None


def test_session_properties(monkeypatch, mock_session_manager_db):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    session_local = DatabaseSessionManager.get_session_local()

    assert session_local.kw["autocommit"] is False
    assert session_local.kw["autoflush"] is False


def test_session_closure(monkeypatch, mock_session_manager_db):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    db_session_gen = DatabaseSessionManager.get_db_session()
    db_session = next(db_session_gen)
    db_session.close = lambda: "closed"

    assert next(db_session_gen, "closed") == "closed"
