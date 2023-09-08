import pytest
import pathlib
import io
import tempfile
from unittest.mock import Mock, patch
from perry.db.operations.documents import save_file, remove_file  

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
