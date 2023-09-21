import pydantic
import datetime
from uuid import UUID
from enum import Enum


class User(pydantic.BaseModel):
    name: str
    username: str
    email: pydantic.EmailStr
    hashed_password: str


class Message(pydantic.BaseModel):
    message_id: UUID
    user: User
    role: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now()


class MessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"
