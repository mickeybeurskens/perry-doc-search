import pytest
from perry.db.operations.users import *
from perry.db.models import pwd_context, User


@pytest.fixture
def test_user(test_db):
    new_user = User(username="test")
    new_user.set_password("test")
    test_db.add(new_user)
    test_db.commit()
    test_db.refresh(new_user)
    return new_user


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
    updated_user = update_user(test_db, test_user.id, username="new_test")
    assert updated_user.username == "new_test"


def test_should_update_password(test_db, test_user):
    updated_user = update_user(test_db, test_user.id, password="new_password")
    assert updated_user.verify_password("new_password")


def test_should_update_username_and_password(test_db, test_user):
    updated_user = update_user(
        test_db, test_user.id, username="new_test", password="new_password"
    )
    assert updated_user.username == "new_test"
    assert updated_user.verify_password("new_password")


def test_should_not_update_if_no_new_data(test_db, test_user):
    updated_user = update_user(test_db, test_user.id)
    assert updated_user.username == "test"
    assert updated_user.verify_password("test")
