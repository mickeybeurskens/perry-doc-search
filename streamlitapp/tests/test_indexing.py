import tempfile
from llama_index.llms import MockLLM
from llama_index import ListIndex
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


def test_create_vector_indices_should_return_indices():
    """Create vector indices should return indices."""
    service_context = ServiceContext.from_defaults()
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
        docs = load_documents_with_unstructured(tmp_dir_path)
        indices = create_vector_indices(docs.values(), ListIndex, service_context)
        assert len(indices) == len(docs)


def test_save_and_load_indices_should_be_the_same():
    """Save indices should save indices and storage context and load them."""
    service_context = ServiceContext.from_defaults()
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
        docs = load_documents_with_unstructured(tmp_dir_path)
        indices = create_vector_indices(docs.values(), ListIndex, service_context)
        save_indices(indices, docs.keys())
        loaded_indices = load_indices(docs.keys())
        assert len(indices) == len(loaded_indices)
        for index, loaded_index in zip(indices, loaded_indices):
            assert type(index) == type(loaded_index)