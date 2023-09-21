import pytest
import freezegun
from datetime import timedelta
from perry.api.authentication import (
    create_access_token,
    get_token_algorithm,
    decode_access_token,
    get_current_user,
)
from jose import jwt, JWTError
from fastapi import HTTPException
from perry.db.operations.users import get_user, delete_user
from tests.conftest import get_mock_secret_key
from tests.api.fixtures import *


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

    with freezegun.freeze_time("2022-01-01"):
        decoded_token = jwt.decode(
            token, get_mock_secret_key(), algorithms=[get_token_algorithm()]
        )
        assert decoded_token["sub"] == "test"

    with freezegun.freeze_time("2022-01-01 00:30:00"):
        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, get_mock_secret_key(), algorithms=[get_token_algorithm()])


def test_invalid_secret_key_raises_error():
    data = {"sub": "test"}
    token = create_access_token(data)

    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(token, "wrong_secret_key", algorithms=[get_token_algorithm()])


def test_decode_access_token_returns_dict():
    data = {"sub": "test"}
    token = create_access_token(data)

    decoded_token = decode_access_token(token)
    assert isinstance(decoded_token, dict)
    assert decoded_token["sub"] == "test"


def test_decode_access_token_raises_error_if_invalid_token():
    with pytest.raises(HTTPException):
        decode_access_token("invalid_token")


@pytest.mark.asyncio
async def test_should_return_user_when_token_is_valid(test_db, mocked_valid_token):
    token, user_id = mocked_valid_token
    with freezegun.freeze_time(get_mocked_date()):
        result = await get_current_user(token)
        assert result.username == get_user(test_db, user_id).username


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_invalid(mocked_invalid_token):
    with pytest.raises(HTTPException):
        await get_current_user(mocked_invalid_token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_token_is_expired(mocked_expired_token):
    token, _ = mocked_expired_token
    with pytest.raises(HTTPException):
        await get_current_user(token)


@pytest.mark.asyncio
async def test_should_raise_http_exception_when_user_not_found(
    test_db, mocked_valid_token
):
    token, user_id = mocked_valid_token
    delete_user(test_db, user_id)
    with pytest.raises(HTTPException):
        await get_current_user(token)
