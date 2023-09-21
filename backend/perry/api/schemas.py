from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRegister(BaseModel):
    username: str
    password: str


class APIUser(BaseModel):
    username: str
    email: str | None = None
