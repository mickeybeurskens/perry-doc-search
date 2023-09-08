import pytest
import pathlib
import io
from unittest.mock import Mock, patch
from perry.db.operations.documents import *
from perry.db.operations.users import create_user


@pytest.fixture
def mock_bytes_obj():
    return io.BytesIO(b"Some binary data here")

@pytest.fixture
def mock_file_path(tmp_path):
    return pathlib.Path(tmp_path / "1.txt")

def test_save_file_success(mock_bytes_obj, mock_file_path, test_db, tmpdir):
  with patch('perry.db.operations.documents.get_file_storage_path', return_value=str(tmpdir)):
    doc = save_file(
        db_session=test_db,
        bytes_obj=mock_bytes_obj,
        suffix="txt"
    )

    assert doc.file_path == str(mock_file_path)
    assert pathlib.Path(doc.file_path).exists() 

from unittest.mock import patch, Mock

def test_remove_file_success(test_db, tmpdir):
    # Setup: Mock the database object and file path
    with patch('perry.db.operations.documents.get_document') as mock_get_document, \
         patch('perry.db.operations.documents.delete_document') as mock_delete_document:
        
        # Mock the document object to return a valid file path
        mock_document = Mock()
        temp_file_path = tmpdir / "temp_file.txt"
        mock_document.file_path = str(temp_file_path)
        mock_get_document.return_value = mock_document

        # Create an actual temporary file
        with open(temp_file_path, 'w') as f:
            f.write("temporary file content")

        # Action: Remove the file and document record
        remove_file(db_session=test_db, document_id=1)

        # Verify: File should be deleted, and document should be removed from the database
        assert not temp_file_path.exists()
        mock_delete_document.assert_called_with(test_db, 1)

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