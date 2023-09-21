from datetime import timedelta, datetime
from perry.api.authentication import (
    create_access_token,
    get_token_algorithm,
    decode_access_token,
)
from jose import jwt, JWTError
import pytest
import freezegun
from tests.conftest import get_mock_secret_key
from fastapi import HTTPException


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


def test_decode_access_token_returns_dict():
    data = {"sub": "test"}
    token = create_access_token(data)

    decoded_token = decode_access_token(token)
    assert isinstance(decoded_token, dict)
    assert decoded_token["sub"] == "test"


def test_decode_access_token_raises_error_if_invalid_token():
    with pytest.raises(HTTPException):
        decode_access_token("invalid_token")
