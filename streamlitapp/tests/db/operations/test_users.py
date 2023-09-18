import pytest
from perry.db.operations.users import *
from perry.db.models import pwd_context, User


@pytest.fixture(scope="function")
def test_user(test_db):
    new_user = User(username="test")
    new_user.set_password("test")
    test_db.add(new_user)
    test_db.commit()
    test_db.refresh(new_user)
    yield new_user
    test_db.delete(new_user)
    test_db.commit()


def test_create_user(test_db):
    username = "john"
    password = "doe"

    created_user_id = create_user(test_db, username, password)
    created_user = test_db.query(User).filter_by(id=created_user_id).first()

    assert created_user.id is not None
    assert created_user.username == username
    assert pwd_context.verify(password, created_user._password)


def test_get_user(test_db, create_user_in_db):
    username = "arthur"
    password = "dent"
    created_user_id = create_user_in_db(username, password)

    retrieved_user = get_user(test_db, created_user_id)

    assert retrieved_user.id == created_user_id
    assert retrieved_user.username == username
    assert pwd_context.verify(password, retrieved_user._password)


def test_get_user_by_username_should_return_existing_user(test_db, create_user_in_db):
    username = "ford"
    password = "prefect"
    created_user_id = create_user_in_db(username, password)

    retrieved_user = get_user_by_username(test_db, username)

    assert retrieved_user.id == created_user_id
    assert retrieved_user.username == username
    assert pwd_context.verify(password, retrieved_user._password)


def test_should_return_none_if_user_not_found(test_db):
    assert update_user(test_db, 1000) is None


def test_should_update_username(test_db, test_user):
    update_user(test_db, test_user.id, username="new_test")
    assert test_user.username == "new_test"


def test_should_update_password(test_db, test_user):
    update_user(test_db, test_user.id, password="new_password")
    assert test_user.verify_password("new_password")


def test_should_update_email(test_db, test_user):
    email = "brain@flyingcircus.com"
    update_user(test_db, test_user.id, email=email)
    assert test_user._email == email


@pytest.mark.parametrize(
    "email",
    [
        "john.doe@gmail.com",
        "john+spam@gmail.com",
        "john_doe@sub.example.com",
        "john_doe@EXAMPLE.COM",
    ],
)
def test_update_email_should_work_with_valid_email(test_db, email, create_user_in_db):
    test_user_id = create_user_in_db(email, "test")
    test_user = get_user(test_db, test_user_id)
    update_user(test_db, test_user.id, email=email)
    assert test_user._email == email


@pytest.mark.parametrize(
    "email",
    [
        "john.doe",
        "john.doe@",
        "john.doe@.com",
        "@example.com",
        "john.doe@com",
        "john doe@example.com",
    ],
)
def test_invalid_emails_should_raise_error(test_db, email, create_user_in_db):
    test_user_id = create_user_in_db(email, "test")
    with pytest.raises(ValueError):
        update_user(test_db, test_user_id, email=email)


def test_update_email_should_raise_error_if_invalid_email(test_db, test_user):
    with pytest.raises(ValueError):
        update_user(test_db, test_user.id, email="invalid_email")


def test_should_update_all_settings(test_db, test_user):
    user = "john"
    password = "cleese"
    email = "john@flyingcircus.com"
    update_user(
        test_db,
        test_user.id,
        username=user,
        password=password,
        email=email,
    )
    assert test_user.username == user
    assert test_user.verify_password(password)
    assert test_user._email == email


def test_should_not_update_if_no_new_data(test_db, test_user):
    update_user(test_db, test_user.id)
    assert test_user.username == "test"
    assert test_user.verify_password("test")


def test_jwt_payload_correctly_returned(test_user):
    payload = test_user.to_jwt_payload()
    assert payload["sub"] == test_user.id
    assert payload["username"] == test_user.username


def test_authenticate_should_return_user_if_authenticated(test_db, create_user_in_db):
    username = "trantor"
    password = "foundation"
    user_id = create_user_in_db(username, password)
    test_user = get_user(test_db, user_id)
    assert user_id == test_user.id


def test_authenticate_should_return_none_if_user_does_not_exist(test_db):
    assert authenticate_user(test_db, "non_existing_user", "password") is None


def test_authenticate_should_return_none_if_password_wrong(test_db, create_user_in_db):
    username = "terminus"
    password = "foundation"
    create_user_in_db(username, password)
    assert authenticate_user(test_db, username, "wrong_password") is None
