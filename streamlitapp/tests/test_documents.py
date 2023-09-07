import io
import pytest
from pathlib import Path
from perry.documents import save_file_to_storage, remove_file_from_storage, load_file_from_storage, load_bytes_from_file, get_file_storage_path
from perry.db.operations.documents import get_document


@pytest.mark.usefixtures("test_db")
class TestFileStorage:

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, test_db):
        self.session = test_db
        self.user_id = 1
        self.title = "Test Document"
        self.description = "This is a test document."
        self.suffix = "txt"
        self.bytes_obj = io.BytesIO(b"Hello World")
        

    def test_save_file_to_storage(self):
        # Call the function and get the document ID
        doc_id = save_file_to_storage(self.session, self.bytes_obj, self.title, self.description, self.user_id, self.suffix)
        
        # Assert that a document ID is returned
        assert doc_id is not None

        # Fetch the document from the database
        doc = get_document(self.session, doc_id)

        # Assert that the document exists and has the expected attributes
        assert doc is not None
        assert doc.title == self.title
        assert doc.description == self.description
        assert doc.file_path is Path(f"{get_file_storage_path()}", f"{doc_id}.{self.suffix}")

        # Check if the file exists on the disk
        assert Path(doc.file_path).is_file()

        # Read the saved file and compare its contents with the original bytes object
        saved_bytes_obj = load_bytes_from_file(Path(doc.file_path))
        self.bytes_obj.seek(0)  # reset cursor position in the original bytes object
        assert saved_bytes_obj.read() == self.bytes_obj.read()