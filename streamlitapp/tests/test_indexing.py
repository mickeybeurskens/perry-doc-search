import tempfile
from llama_index.llms import MockLLM
from perry.indexing import *


def test_load_documents_should_return_files_in_dir():
    """Load documents should return all files in a directory."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
        docs = load_documents_with_unstructured(tmp_dir_path)
        for path in docs:
            assert path in file_paths


# TODO: Test create_vector_indices
