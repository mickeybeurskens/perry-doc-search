# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from perry.db.models import Base
from tests.conftest import test_db

# test_user_operations.py
from perry.db.operations.users import create_user, get_user
from perry.db.models import pwd_context

def test_create_user(test_db):
    username = "john"
    password = "doe"
    
    created_user = create_user(test_db, username, password)
    
    assert created_user.id is not None
    assert created_user.username == username
    assert pwd_context.verify(password, created_user._password)

def test_get_user(test_db):
    username = "jane"
    password = "doe"
    created_user = create_user(test_db, username, password)
    
    retrieved_user = get_user(test_db, created_user.id)
    
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == username
    assert pwd_context.verify(password, retrieved_user._password)

from perry.db.operations.messages import create_message, get_messages_by_user

def test_create_message(test_db):
    username = "lancelot"
    password = "blue"
    user = create_user(test_db, username, password)
    role = "user"
    message_text = "Hello, world!"

    created_message = create_message(test_db, user.id, role, message_text)

    assert created_message.id is not None
    assert created_message.user_id == user.id
    assert created_message.role == role
    assert created_message.message == message_text

def test_get_messages_by_user(test_db):
    username = "arthur"
    password = "grail"
    role = "user"
    user = create_user(test_db, username, password)
    create_message(test_db, user.id, role, "Hello, world!")
    create_message(test_db, user.id, role, "Hello again!")

    messages = get_messages_by_user(test_db, user.id)

    assert len(messages) == 2
    for message in messages:
        assert message.user_id == user.id

from perry.db.operations.documents import *
from perry.db.operations.users import create_user

def test_create_document(test_db):
    created_document = create_document(test_db)
    test_db.commit()
    
    assert created_document.id is not None

def test_get_document(test_db):
    created_document = create_document(test_db)
    
    retrieved_document = get_document(test_db, created_document.id)

    assert retrieved_document.id == created_document.id

def test_delete_document(test_db):
    created_document = create_document(test_db)
    
    delete_document(test_db, created_document.id)
    retrieved_document = get_document(test_db, created_document.id)
    
    assert retrieved_document is None

def test_add_user_to_document(test_db):
    username = "robin"
    password = "brave"
    created_document = create_document(test_db)
    created_user = create_user(test_db, username, password)
    
    add_user_to_document(test_db, created_user.id, created_document.id)
    
    assert created_user in created_document.users

def test_remove_user_from_document(test_db):
    username = "galahad"
    password = "wise"
    created_document = create_document(test_db)
    created_user = create_user(test_db, username, password)
    add_user_to_document(test_db, created_user.id, created_document.id)
    
    assert created_user in created_document.users

    remove_user_from_document(test_db, created_user.id, created_document.id)
    
    assert created_user not in created_document.users

def test_update_document_description(test_db):
    description = "The Holy Grail is the mighty chalice of legend. This document describes its history."
    created_document = create_document(test_db)
    
    updated_document = update_document_description(test_db, created_document.id, description)
    
    assert updated_document.id == created_document.id
    assert updated_document.description == description

def test_update_document_title(test_db):
    title = "The Holy Grail"
    created_document = create_document(test_db)
    
    updated_document = update_document_title(test_db, created_document.id, title)
    
    assert updated_document.id == created_document.id
    assert updated_document.title == title

def test_update_document_file_path(test_db):
    file_path = "/path/to/document.pdf"
    new_file_path = "/path/to/updated_document.pdf"
    created_document = create_document(test_db)
    
    updated_document = update_document_file_path(test_db, created_document.id, new_file_path)
    
    assert updated_document.id == created_document.id
    assert updated_document.file_path == new_file_path