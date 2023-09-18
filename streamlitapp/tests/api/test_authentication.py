from datetime import timedelta, datetime
from perry.api.authentication import (
    create_access_token,
    get_token_algorithm,
    get_user_from_token,
)
from fastapi import HTTPException
from jose import jwt, JWTError
import pytest
import freezegun
from tests.conftest import get_mock_secret_key
from perry.db.operations.users import get_user, delete_user


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


def test_create_valid_access_token_should_succeed():
    data = {"sub": "test"}
    token = create_access_token(data)
    assert token is not None

    decoded_token = jwt.decode(
        token, get_mock_secret_key(), algorithms=[get_token_algorithm()]
    )
    assert decoded_token["sub"] == "test"


def test_token_expiration_should_raise_error():
    data = {"sub": "test"}
    with freezegun.freeze_time("2022-01-01"):
        token = create_access_token(data, expires_delta=timedelta(minutes=1))

    with freezegun.freeze_time("2022-01-01 00:00:30"):
        decoded_token = jwt.decode(
            token, get_mock_secret_key(), algorithms=[get_token_algorithm()]
        )
        assert decoded_token["sub"] == "test"

    with freezegun.freeze_time("2022-01-01 00:02:00"):
        with pytest.raises(JWTError):
            jwt.decode(token, get_mock_secret_key(), algorithms=[get_token_algorithm()])


def test_invalid_secret_key_raises_error():
    data = {"sub": "test"}
    token = create_access_token(data)

    with pytest.raises(JWTError):
        jwt.decode(token, "wrong_secret_key", algorithms=[get_token_algorithm()])


@pytest.mark.asyncio
async def test_should_return_user_when_token_is_valid(test_db, mocked_valid_token):
    token, user_id = mocked_valid_token
    result = await get_user_from_token(test_db, token)
    assert result == get_user(test_db, user_id)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_invalid(
    test_db, mocked_invalid_token
):
    with pytest.raises(HTTPException):
        await get_user_from_token(test_db, mocked_invalid_token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_expired(
    test_db, mocked_expired_token
):
    token, _ = mocked_expired_token
    with pytest.raises(HTTPException):
        await get_user_from_token(test_db, token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_user_not_found(
    test_db, mocked_valid_token
):
    token, user_id = mocked_valid_token
    delete_user(test_db, user_id)
    with pytest.raises(HTTPException):
        await get_user_from_token(test_db, token)
