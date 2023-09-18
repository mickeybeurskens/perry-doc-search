from fastapi import HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from perry.db.models import User
from perry.db.operations.users import update_user, create_user, get_user_by_username
from perry.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
