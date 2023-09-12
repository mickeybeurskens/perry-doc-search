import pytest
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from perry.db.models import Base
from tests.fixtures import *

@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Session:
    """Setup a temporary database for testing."""
    engine = create_engine("sqlite:///test_db.sqlite")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

@pytest.fixture(scope="function", autouse=True)
def test_db(create_test_db) -> Session:
    """Empty database before each test and return."""
    
    # Reflect existing tables to metadata
    metadata = MetaData()
    metadata.reflect(bind=create_test_db.get_bind())

    # Delete records one by one from each table
    for table in reversed(metadata.sorted_tables):
        create_test_db.execute(table.delete())
    create_test_db.commit()

    return create_test_db
