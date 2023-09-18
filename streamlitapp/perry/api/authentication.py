from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import JWTError, jwt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def get_secret_key():
    return "secret"


def get_token_algorithm():
    return "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, get_secret_key(), algorithm=get_token_algorithm()
    )
    return encoded_jwt
