import os
import tempfile
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from perry.db.models import Base
from perry.db.operations.agents import create_agent
from perry.db.operations.conversations import create_conversation, update_conversation
from perry.db.operations.documents import create_document
from perry.db.operations.users import create_user


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
def create_user_in_db(test_db):
    """Add a user to the database and return its ID."""
    def _create_user_in_db(username: str, password: str):
        return create_user(test_db, username, password)

    return _create_user_in_db

@pytest.fixture(scope="function")
def add_document_to_db(test_db):
    """Add a document to the database and return its ID."""
    def _add_document_to_db():
        return create_document(test_db)
    return _add_document_to_db

# @pytest.fixture(scope="function")
# @pytest.mark.parametrize("temp_files", [
#     [{'name': 'file1', 'contents': 'file1 contents', 'suffix': '.pdf'}],
#     [{'name': 'file2', 'contents': 'file2 contents', 'suffix': '.pdf'}],
#     [{'name': 'file3', 'contents': 'file3 contents', 'suffix': '.pdf'}],
# ], indirect=True)
# def create_connected_agent_conversation_in_db_with_docs(
#     create_connected_agent_conversation_in_db, create_user_in_db, temp_files, test_db
# ):
#     agent_id, conversation_id = create_connected_agent_conversation_in_db
#     user_id = create_user_in_db(test_db, 'test_user', 'test_password')
#     for file_path in temp_files:
#         doc_id = create_document(test_db)
#         doc_id = update_document()



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
        file_name = config.get('name', 'temp_file')
        contents = config.get('contents', '')
        suffix = config.get('suffix', '.tmp')

        fd, path = tempfile.mkstemp(suffix=suffix)

        with open(path, 'w') as f:
            f.write(contents)

        temp_file_details.append({'path': path, 'name': file_name, 'suffix': suffix})
    
    yield temp_file_details

    for file_detail in temp_file_details:
        path = file_detail['path']
        if os.path.exists(path):
            os.remove(file_detail['path'])


def clear_db(db_session: Session):
    # Reflect existing tables to metadata
    metadata = MetaData()
    metadata.reflect(bind=db_session.get_bind())

    # Delete records one by one from each table
    for table in reversed(metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
