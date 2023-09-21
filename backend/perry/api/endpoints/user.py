from typing import Annotated
from datetime import timedelta
from fastapi import HTTPException, APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from perry.db.operations.users import (
    get_user,
    create_user,
    get_user_by_username,
    authenticate_user,
)
from perry.db.session import DatabaseSessionManager
from perry.api.schemas import APIUser, UserRegister, Token
from perry.api.authentication import create_access_token, get_current_user


user_router = APIRouter()


@user_router.post("/register")
async def register(user: UserRegister):
    db = DatabaseSessionManager.get_db_session
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(db, user.username, user.password)
    return {"username": user.username}


@user_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    db = DatabaseSessionManager.get_db_session
    user_id = authenticate_user(db, form_data.username, form_data.password)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user(db, user_id)
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data=user.to_jwt_payload(), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/info", response_model=APIUser)
async def read_user_info(api_user: Annotated[str, Depends(get_current_user)]):
    return api_user
