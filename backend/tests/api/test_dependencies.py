from perry.api.dependencies import get_db


def test_get_db_yields_db_session(test_db):
    db = next(get_db())
    assert db is test_db
    assert db.is_active is True
