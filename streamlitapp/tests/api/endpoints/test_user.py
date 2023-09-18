from fastapi.testclient import TestClient
import pytest
from perry.db.models import User


@pytest.fixture
def test_client():
    from perry.api.app import app

    with TestClient(app) as client:
        yield client


def test_should_check_endpoint_availability(test_client):
    response = test_client.post(
        "/register", json={"username": "test", "password": "test"}
    )
    assert response.status_code != 404


def test_should_register_new_user(test_client, test_db):
    response = test_client.post(
        "/register", json={"username": "new_user", "password": "new_password"}
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
        "/register", json={"username": username, "password": password}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}
