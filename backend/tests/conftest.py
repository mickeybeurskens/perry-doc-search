import os
import tempfile
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from perry.db.models import Base
from perry.db.operations.agents import create_agent, update_agent
from perry.db.operations.conversations import create_conversation
from perry.db.operations.documents import create_document, update_document
from perry.db.operations.users import create_user
from perry.db.operations.messages import create_message
from perry.db.session import DatabaseSessionManager


@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Session:
    """Setup a temporary database for testing."""
    DatabaseSessionManager._db_name = "test_db"
    session = DatabaseSessionManager.get_db_session()
    clear_db(session)
    return session


@pytest.fixture(scope="function", autouse=True)
def mock_get_secret_key(monkeypatch):
    monkeypatch.setattr("perry.api.authentication.get_secret_key", get_mock_secret_key)


@pytest.fixture(scope="function", autouse=True)
def test_db(create_test_db, monkeypatch) -> Session:
    """Empty database before each test and return."""
    clear_db(create_test_db)
    monkeypatch.setattr(
        "perry.db.session.DatabaseSessionManager._SessionLocal", lambda: create_test_db
    )
    return create_test_db


@pytest.fixture(scope="function")
def add_agent_to_db(test_db) -> int:
    """Add an agent to the database and return its ID."""

    def _add_agent_to_db():
        return create_agent(test_db)

    return _add_agent_to_db


@pytest.fixture(scope="function")
def add_conversation_to_db(test_db) -> int:
    """Add a conversation to the database and return its ID."""

    def _add_conversation_to_db():
        return create_conversation(test_db)

    return _add_conversation_to_db


@pytest.fixture(scope="function")
def add_message_to_db(test_db) -> list[int]:
    """Add a message to the database and return its ID."""

    def _add_message_to_db(num_messages: int):
        message_id = create_message(test_db, 1, "user", "test message")
        return message_id

    return _add_message_to_db


@pytest.fixture(scope="function")
def create_user_in_db(test_db) -> int:
    """Add a user to the database and return its ID."""

    def _create_user_in_db(username: str, password: str):
        return create_user(test_db, username, password)

    return _create_user_in_db


@pytest.fixture(scope="function")
def add_document_to_db(test_db) -> int:
    """Add a document to the database and return its ID."""

    def _add_document_to_db():
        return create_document(test_db)

    return _add_document_to_db


@pytest.fixture(scope="function")
def add_connected_agent_conversation_to_db(test_db) -> tuple[int, int]:
    """Add an agent and conversation to the database and return their IDs."""

    def _add_connected_agent_conversation_to_db():
        agent_id = create_agent(test_db)
        conversation_id = create_conversation(test_db)
        update_agent(test_db, agent_id, conversation_id=conversation_id)
        return agent_id, conversation_id

    return _add_connected_agent_conversation_to_db


@pytest.fixture(scope="function")
def add_documents_with_file_names(test_db):
    def _add_documents_with_file_names(file_paths: list[str]):
        doc_ids = []
        for file_path in file_paths:
            doc_id = create_document(test_db)
            update_document(test_db, doc_id, file_path=file_path)
            doc_ids.append(doc_id)
        return doc_ids

    return _add_documents_with_file_names


@pytest.fixture(scope="function")
def temp_files(request):
    """Create temporary files and return their details.

    Usage:
    @pytest.mark.parametrize("temp_files", [
        [{'name': 'file1', 'contents': 'file1 contents', 'suffix': '.tmp'}],
        [{'name': 'file2', 'contents': 'file2 contents', 'suffix': '.tmp'}],
        [{'name': 'file3', 'contents': 'file3 contents', 'suffix': '.tmp'}],
    ], indirect=True)
    """
    file_configs = request.param
    temp_file_details = []

    for config in file_configs:
        file_name = config.get("name", "temp_file")
        contents = config.get("contents", "")
        suffix = config.get("suffix", ".tmp")

        fd, path = tempfile.mkstemp(suffix=suffix)

        with open(path, "w") as f:
            f.write(contents)

        temp_file_details.append({"path": path, "name": file_name, "suffix": suffix})

    yield temp_file_details

    for file_detail in temp_file_details:
        path = file_detail["path"]
        if os.path.exists(path):
            os.remove(file_detail["path"])


def clear_db(db_session: Session):
    # Reflect existing tables to metadata
    metadata = MetaData()
    metadata.reflect(bind=db_session.get_bind())

    # Delete records one by one from each table
    for table in reversed(metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


def get_mock_secret_key():
    return "supersecrettestkey"
