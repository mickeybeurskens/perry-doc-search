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
from perry.db.operations import create_user, get_user
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