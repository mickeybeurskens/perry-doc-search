from typing import Annotated
from datetime import timedelta
from fastapi import HTTPException, APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from perry.db.models import User
from perry.db.operations.users import (
    get_user,
    create_user,
    get_user_by_username,
    authenticate_user,
)
from perry.db.session import get_db_session
from perry.api.authentication import Token, create_access_token


user_router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str


@user_router.post("/register")
async def register(user: UserCreate):
    db_user = get_user_by_username(get_db_session, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(get_db_session, user.username, user.password)
    return {"username": user.username}


@user_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_id = authenticate_user(get_db_session, form_data.username, form_data.password)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(get_db_session, user_id)
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data=user.to_jwt_payload(), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
