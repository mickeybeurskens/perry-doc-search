from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from perry.db.models import User
from perry.api.endpoints.user import get_username_from_token
from perry.db.operations.users import get_user, delete_user
from perry.db.operations.users import get_user
from tests.conftest import get_mock_secret_key


class FakeUser:
    def __init__(self, user_id):
        self.id = user_id

    def to_jwt_payload(self):
        return {"sub": str(self.id), "username": "test_user"}


def users_url():
    return "/users"


@pytest.fixture
def test_client():
    from perry.api.app import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def mocked_valid_token(test_db, create_user_in_db):
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


def test_should_check_endpoint_availability(test_client):
    response = test_client.post(
        users_url() + "/register", json={"username": "test", "password": "test"}
    )
    assert response.status_code != 404


def test_should_register_new_user(test_client, test_db):
    response = test_client.post(
        users_url() + "/register",
        json={"username": "new_user", "password": "new_password"},
    )
    assert response.status_code == 200
    assert response.json() == {"username": "new_user"}

    db_user = test_db.query(User).filter(User.username == "new_user").first()
    assert db_user is not None
    assert db_user.verify_password("new_password")


def test_should_not_register_duplicate_username(test_client, create_user_in_db):
    username = "existing_user"
    password = "existing_password"
    create_user_in_db(username, password)

    response = test_client.post(
        users_url() + "/register", json={"username": username, "password": password}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}


def test_login_for_access_token_valid_user(test_client, create_user_in_db):
    username = "valid_user"
    password = "valid_pass"
    create_user_in_db(username, password)
    response = test_client.post(
        users_url() + "/token",
        data={"username": "valid_user", "password": "valid_pass"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_for_access_token_invalid_user_should_error(test_client):
    response = test_client.post(
        users_url() + "/token",
        data={"username": "invalid_user", "password": "invalid_pass"},
    )
    assert response.status_code == 401


def test_login_for_access_token_empty_values_should_error(test_client):
    response = test_client.post(
        users_url() + "/token", data={"username": "", "password": ""}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_return_user_when_token_is_valid(test_db, mocked_valid_token):
    token, user_id = mocked_valid_token
    result = await get_username_from_token(test_db, token)
    assert result == get_user(test_db, user_id).username


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_invalid(
    test_db, mocked_invalid_token
):
    with pytest.raises(HTTPException):
        await get_username_from_token(test_db, mocked_invalid_token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_expired(
    test_db, mocked_expired_token
):
    token, _ = mocked_expired_token
    with pytest.raises(HTTPException):
        await get_username_from_token(test_db, token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_user_not_found(
    test_db, mocked_valid_token
):
    token, user_id = mocked_valid_token
    delete_user(test_db, user_id)
    with pytest.raises(HTTPException):
        await get_username_from_token(test_db, token)
