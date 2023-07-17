import json
import tempfile
from llama_index.readers import JSONReader
from perry.indexing import *


def test_load_documents_should_return_files_in_dir():
    """Load documents should return all files in a directory."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        with open(tmp_dir_path / "test_file_1.txt", "w") as f:
            file_content_1 = {"test": "test file 1"}
            f.write(json.dumps(file_content_1))
        with open(tmp_dir_path / "test_file_2.txt", "w") as f:
            file_content_2 = {"test": "test file 2"}
            f.write(json.dumps(file_content_2))

        documents = load_documents(tmp_dir_path, JSONReader())
        assert len(documents) == 2
        for path in documents.keys():
            assert len(documents[path]) == 1
            doc = documents[path][0]
            if path.stem == "test_file_1":
                assert json.loads(doc.text) == file_content_1
            elif path.stem == "test_file_2":
                assert json.loads(doc.text) == file_content_2
            else:
                raise ValueError("Unexpected file name.")