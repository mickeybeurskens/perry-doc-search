# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from perry.db.models import Base

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///test_db.sqlite")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal()  # This is where the testing happens
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

# test_user_operations.py
from perry.db.operations.users import create_user, get_user
from perry.db.models import pwd_context

def test_create_user(test_db):
    # Arrange
    username = "john"
    password = "doe"
    
    # Act
    created_user = create_user(test_db, username, password)
    
    # Assert
    assert created_user.id is not None
    assert created_user.username == username
    assert pwd_context.verify(password, created_user._password)

def test_get_user(test_db):
    # Arrange
    username = "jane"
    password = "doe"
    created_user = create_user(test_db, username, password)
    
    # Act
    retrieved_user = get_user(test_db, created_user.id)
    
    # Assert
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == username
    assert pwd_context.verify(password, retrieved_user._password)

from perry.db.operations.messages import create_message, get_messages_by_user

def test_create_message(test_db):
    # Arrange
    username = "lancelot"
    password = "blue"
    user = create_user(test_db, username, password)
    role = "user"
    message_text = "Hello, world!"

    # Act
    created_message = create_message(test_db, user.id, role, message_text)

    # Assert
    assert created_message.id is not None
    assert created_message.user_id == user.id
    assert created_message.role == role
    assert created_message.message == message_text

def test_get_messages_by_user(test_db):
    # Arrange
    username = "arthur"
    password = "grail"
    role = "user"
    user = create_user(test_db, username, password)
    create_message(test_db, user.id, role, "Hello, world!")
    create_message(test_db, user.id, role, "Hello again!")

    # Act
    messages = get_messages_by_user(test_db, user.id)

    # Assert
    assert len(messages) == 2
    for message in messages:
        assert message.user_id == user.id

from perry.db.operations.documents import *
from perry.db.operations.users import create_user

def test_create_document(test_db):
    file_path = "/path/to/document.pdf"
    
    created_document = create_document(test_db, file_path)
    
    assert created_document.id is not None
    assert created_document.file_path == file_path

def test_get_document(test_db):
    file_path = "/path/to/document.pdf"
    created_document = create_document(test_db, file_path)
    
    retrieved_document = get_document(test_db, created_document.id)

    assert retrieved_document.id == created_document.id
    assert retrieved_document.file_path == file_path

def test_delete_document(test_db):
    file_path = "/path/to/document.pdf"
    created_document = create_document(test_db, file_path)
    
    delete_document(test_db, created_document.id)
    retrieved_document = get_document(test_db, created_document.id)
    
    assert retrieved_document is None

def test_add_user_to_document(test_db):
    file_path = "/path/to/document.pdf"
    username = "robin"
    password = "brave"
    created_document = create_document(test_db, file_path)
    created_user = create_user(test_db, username, password)
    
    add_user_to_document(test_db, created_user.id, created_document.id)
    
    assert created_user in created_document.users

def test_remove_user_from_document(test_db):
    file_path = "/path/to/document.pdf"
    username = "galahad"
    password = "wise"
    created_document = create_document(test_db, file_path)
    created_user = create_user(test_db, username, password)
    add_user_to_document(test_db, created_user.id, created_document.id)
    
    assert created_user in created_document.users

    remove_user_from_document(test_db, created_user.id, created_document.id)
    
    assert created_user not in created_document.users

def test_update_document_description(test_db):
    file_path = "/path/to/document.pdf"
    description = "The Holy Grail is the mighty chalice of legend. This document describes its history."
    created_document = create_document(test_db, file_path)
    
    updated_document = update_document_description(test_db, created_document.id, description)
    
    assert updated_document.id == created_document.id
    assert updated_document.description == description
    assert updated_document.file_path == file_path

def test_update_document_title(test_db):
    file_path = "/path/to/document.pdf"
    title = "The Holy Grail"
    created_document = create_document(test_db, file_path)
    
    updated_document = update_document_title(test_db, created_document.id, title)
    
    assert updated_document.id == created_document.id
    assert updated_document.title == title
    assert updated_document.file_path == file_path