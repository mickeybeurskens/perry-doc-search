import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from perry.db.models import Base
from perry.db.operations.agents import create_agent
from perry.db.operations.conversations import create_conversation
from perry.db.operations.users import create_user
from perry.db.api import connect_agent_to_conversation

@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Session:
    """Setup a temporary database for testing."""
    engine = create_engine("sqlite:///test_db.sqlite")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    clear_db(session)
    return session

@pytest.fixture(scope="function", autouse=True)
def test_db(create_test_db) -> Session:
    """Empty database before each test and return."""
    clear_db(create_test_db)

    return create_test_db

@pytest.fixture(scope="function")
def add_agent_to_db(test_db) -> int:
    """Add an agent to the database and return its ID."""
    return create_agent(test_db)

@pytest.fixture(scope="function")
def add_conversation_to_db(test_db) -> int:
    """Add a conversation to the database and return its ID."""
    return create_conversation(test_db)

@pytest.fixture(scope="function")
def add_connected_agent_and_conversation_to_db(test_db, add_agent_to_db, add_conversation_to_db) -> tuple[int, int]:
    """Add an agent and a conversation to the database, connect them and return their IDs."""
    connect_agent_to_conversation(test_db, add_agent_to_db, add_conversation_to_db)
    return add_agent_to_db, add_conversation_to_db

@pytest.fixture(scope="function")
def create_user_in_db():
    """Add a user to the database and return its ID."""
    def _create_user_in_db(test_db, username: str, password: str):
        return create_user(test_db, username, password)
    return _create_user_in_db

def clear_db(db_session: Session):
    # Reflect existing tables to metadata
    metadata = MetaData()
    metadata.reflect(bind=db_session.get_bind())

    # Delete records one by one from each table
    for table in reversed(metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()