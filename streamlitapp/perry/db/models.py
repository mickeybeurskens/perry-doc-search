import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum as ENUM
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext


Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def to_db_enum(enum_class) -> ENUM:
    return ENUM(enum_class, name=enum_class.__name__)


class MessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    _password = Column("password", String)
    
    def set_password(self, password: str):
        self._password = pwd_context.hash(password)
        
    def verify_password(self, password: str):
        return pwd_context.verify(password, self._password)
    

class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(to_db_enum(MessageRoleEnum))
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now)