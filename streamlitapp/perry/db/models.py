from datetime import datetime
import re
from enum import Enum
from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    JSON,
    Enum as ENUM,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext


Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def to_db_enum(enum_class) -> ENUM:
    return ENUM(enum_class, name=enum_class.__name__)


class MessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


user_document_relation = Table(
    "user_document_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("document_id", Integer, ForeignKey("documents.id")),
)

conversation_document_relation = Table(
    "conversation_document_association",
    Base.metadata,
    Column("conversation_id", Integer, ForeignKey("conversations.id")),
    Column("document_id", Integer, ForeignKey("documents.id")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    _email = Column(String, unique=True, index=True)
    _password = Column("password", String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    documents = relationship(
        "Document", secondary=user_document_relation, back_populates="users"
    )
    conversations = relationship("Conversation", back_populates="user")

    def set_password(self, password: str):
        self._password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self._password)

    def set_email(self, email: str):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern, email):
            self._email = email
        else:
            raise ValueError("Invalid email format")

    def to_jwt_payload(self):
        return {"sub": str(self.username), "username": self.username}


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(to_db_enum(MessageRoleEnum))
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    users = relationship(
        "User", secondary=user_document_relation, back_populates="documents"
    )
    file_path = Column(String)
    title = Column(String, default="")
    description = Column(String, default="")
    conversations = relationship(
        "Conversation",
        secondary=conversation_document_relation,
        back_populates="documents",
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="conversations")

    agent = relationship("Agent", uselist=False, back_populates="conversation")

    messages = relationship("Message", back_populates="conversation")
    documents = relationship(
        "Document",
        secondary=conversation_document_relation,
        back_populates="conversations",
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)

    conversation = relationship("Conversation", back_populates="agent")
    config = Column(JSON)
