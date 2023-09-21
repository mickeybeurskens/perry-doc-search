import jwt
import pytest
import freezegun
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from perry.db.operations.users import get_user
from tests.conftest import get_mock_secret_key


@pytest.fixture(scope="function")
def test_client():
    from perry.api.app import app

    with TestClient(app) as client:
        yield client


def get_mocked_date():
    return datetime(2021, 1, 1)


@pytest.fixture(scope="function")
def mocked_valid_token(test_db, create_user_in_db):
    with freezegun.freeze_time(get_mocked_date()):
        user_id = create_user_in_db("test_user", "test_password")
        user = get_user(test_db, user_id)
        data = user.to_jwt_payload()
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {"exp": expiration, **data}, get_mock_secret_key(), algorithm="HS256"
        )
        return token, user_id


@pytest.fixture(scope="function")
def mocked_invalid_token():
    token = "blablablae30.xE2BSc2xC8qWaOYEf9CcxpwaQpMNIxDnzrQmIphI3-k"
    return token


@pytest.fixture(scope="function")
def mocked_expired_token(test_db, create_user_in_db):
    with freezegun.freeze_time(get_mocked_date()):
        user_id = create_user_in_db("test_user", "test_password")
        user = get_user(test_db, user_id)
        data = user.to_jwt_payload()
        expiration = datetime.utcnow() - timedelta(hours=2)
        token = jwt.encode(
            {"exp": expiration, **data}, get_mock_secret_key(), algorithm="HS256"
        )
        return token, user_id


@pytest.fixture(scope="function", autouse=True)
def mock_get_db_session(monkeypatch, test_db):
    """Mock get_db_session to return test_db."""
    monkeypatch.setattr(
        "perry.db.session.DatabaseSessionManager.get_db_session", test_db
    )
