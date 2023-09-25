import pytest
from perry.db.session import DatabaseSessionManager


def test_singleton_behavior(monkeypatch):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    engine1 = DatabaseSessionManager.get_engine()
    engine2 = DatabaseSessionManager.get_engine()

    assert engine1 is engine2

    session_local1 = DatabaseSessionManager.get_session_local()
    session_local2 = DatabaseSessionManager.get_session_local()

    assert session_local1 is session_local2


def test_lazy_initialization(monkeypatch):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    DatabaseSessionManager._engine = None
    DatabaseSessionManager._SessionLocal = None

    assert DatabaseSessionManager._engine is None
    assert DatabaseSessionManager._SessionLocal is None

    DatabaseSessionManager.get_engine()
    DatabaseSessionManager.get_session_local()

    assert DatabaseSessionManager._engine is not None
    assert DatabaseSessionManager._SessionLocal is not None


def test_session_properties(monkeypatch):
    monkeypatch.setattr("perry.db.session.create_engine", lambda x: "fake_engine")

    DatabaseSessionManager._SessionLocal = None
    session_local = DatabaseSessionManager.get_session_local()

    assert session_local.kw["autocommit"] is False
    assert session_local.kw["autoflush"] is False
