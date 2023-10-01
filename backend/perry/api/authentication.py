from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from perry.api.schemas import APIUser
from perry.db.session import DatabaseSessionManager
from perry.db.operations.users import (
    get_user_by_username,
    User as DBUser,
)
from perry.api.dependencies import get_db


def get_secret_key():
    return "secret-but-really-not-so-secret"


def get_token_algorithm():
    return "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def decode_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        payload = jwt.decode(
            token, get_secret_key(), algorithms=[get_token_algorithm()]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_db_user_from_token(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    username: str = payload.get("username")
    if username is None:
        raise credentials_exception
    db_user = get_user_by_username(db, username)
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_current_user(
    db_user: Annotated[DBUser, Depends(get_db_user_from_token)]
) -> APIUser:
    return APIUser(username=db_user.username)


async def get_current_user_id(
    db_user: Annotated[DBUser, Depends(get_db_user_from_token)]
) -> int:
    return db_user.id
