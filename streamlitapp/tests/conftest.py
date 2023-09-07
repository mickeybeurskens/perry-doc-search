import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from perry.db.models import Base

@pytest.fixture(scope="module")
def test_db():
    """Setup a temporary database for testing."""
    engine = create_engine("sqlite:///test_db.sqlite")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal()  # This is where the testing happens
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
