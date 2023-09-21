from datetime import timedelta
import freezegun
from perry.db.models import User
from perry.db.operations.users import get_user, delete_user
from perry.db.operations.users import get_user
from tests.api.fixtures import *


class FakeUser:
    def __init__(self, user_id):
        self.id = user_id

    def to_jwt_payload(self):
        return {"sub": str(self.id), "username": "test_user"}


def users_url():
    return "/users"


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
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_for_access_token_empty_values_should_error(test_client):
    response = test_client.post(
        users_url() + "/token", data={"username": "", "password": ""}
    )
    assert response.status_code == 422


def test_read_user_info_should_error_on_invalid_token(test_client):
    response = test_client.get(users_url() + "/info")
    assert response.status_code == 401


def test_read_user_info_should_error_if_user_gone(
    test_db, test_client, mocked_valid_token
):
    token, user_id = mocked_valid_token
    delete_user(test_db, user_id)
    response = test_client.get(
        users_url() + "/info", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_read_user_info_should_return_user(test_db, test_client, mocked_valid_token):
    token, user_id = mocked_valid_token
    username = get_user(test_db, user_id).username
    with freezegun.freeze_time(get_mocked_date()):
        response = test_client.get(
            users_url() + "/info", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert response.json() == {"username": username, "email": None}


def test_generated_token_should_allow_get_user_info(
    test_db, test_client, mocked_valid_token
):
    token, user_id = mocked_valid_token
    username = get_user(test_db, user_id).username
    with freezegun.freeze_time(get_mocked_date()):
        response = test_client.get(
            users_url() + "/info", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert response.json()["username"] == username
    assert response.json()["email"] is None


def test_generated_but_outdated_token_should_refuse_get_user_info(
    test_db, test_client, mocked_valid_token
):
    token, _ = mocked_valid_token
    with freezegun.freeze_time(get_mocked_date() + timedelta(days=8)):
        response = test_client.get(
            users_url() + "/info", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Could not validate credentials"}
