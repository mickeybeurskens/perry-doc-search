import tempfile
from llama_index.llms import MockLLM
from llama_index import ListIndex, TreeIndex, load_graph_from_storage
from perry.documents import save_document_metadata
from perry.agents.indexing import *


def test_load_documents_should_return_files_in_dir():
    """Load documents should return all files in a directory."""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
            meta = DocumentMetadata(
                title=file_path.name,
                file_path=file_path,
                summary="test",
            )
            save_document_metadata(meta)

        docs, metadata = load_documents_with_unstructured(tmp_dir_path)
        for meta in metadata:
            assert meta.file_path in file_paths


def test_create_vector_indices_should_return_indices():
    """Create vector indices should return indices."""
    service_context = ServiceContext.from_defaults()
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
            meta = DocumentMetadata(
                title=file_path.name,
                file_path=file_path,
                summary="test",
            )
            save_document_metadata(meta)
        docs, metadata = load_documents_with_unstructured(tmp_dir_path)
        indices = create_file_indices(docs, ListIndex, service_context)
        assert len(indices) == len(docs)


def test_save_and_load_indices_should_be_the_same():
    """Save indices should save indices and storage context and load them."""
    service_context = ServiceContext.from_defaults()
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name)
        file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
        for file_path in file_paths:
            file_path.touch()
            meta = DocumentMetadata(
                title=file_path.name,
                file_path=file_path,
                summary="test",
            )
            save_document_metadata(meta)
        docs, metadata = load_documents_with_unstructured(tmp_dir_path)
        indices = create_file_indices(docs, ListIndex, service_context)
        save_indices(indices, [meta.file_path for meta in metadata])
        loaded_indices = load_indices([meta.file_path for meta in metadata])
        assert len(indices) == len(loaded_indices)
        for index, loaded_index in zip(indices, loaded_indices):
            assert type(index) == type(loaded_index)


# def test_create_directory_index_contains_file_indices():
#     """ A directory index should contain the file indices that it was created from. """
#     service_context = ServiceContext.from_defaults()
#     with tempfile.TemporaryDirectory() as tmp_dir_name:
#         tmp_dir_path = pathlib.Path(tmp_dir_name)
#         file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
#         metadata = [DocumentMetadata(title=path.stem, summary="sum", file_path=path) for path in file_paths]
#         for file_path in file_paths:
#             file_path.touch()
#         docs = load_documents_with_unstructured(tmp_dir_path)
#         indices = create_file_indices(docs.values(), ListIndex, service_context)
#         directory_index = create_directory_graph(indices, metadata, TreeIndex, service_context)
#         assert len(directory_index.all_indices.values()) - 1 == len(indices)
#         for index in indices:
#             assert index in directory_index.all_indices.values()


# def test_save_and_load_directory_index_should_be_same():
#     """Save directory index should save directory index and storage context and load them."""
#     service_context = ServiceContext.from_defaults()
#     with tempfile.TemporaryDirectory() as tmp_dir_name:
#         tmp_dir_path = pathlib.Path(tmp_dir_name)
#         file_paths = [tmp_dir_path / "test_file_1.txt", tmp_dir_path / "test_file_2.txt"]
#         metadata = [DocumentMetadata(title=path.stem, summary="sum", file_path=path) for path in file_paths]
#         for file_path in file_paths:
#             file_path.touch()
#         docs = load_documents_with_unstructured(tmp_dir_path)
#         indices = create_file_indices(docs.values(), ListIndex, service_context)
#         for index in indices:
#             index.storage_context.persist(tmp_dir_path)
#         directory_graph = create_directory_graph(indices, metadata, TreeIndex, service_context)
#         directory_graph.storage_context.persist(tmp_dir_path)
#         loaded_directory_graph = load_graph_from_storage(
#             root_id=directory_graph.root_id,
#             storage_context=directory_graph.storage_context,
#             service_context=directory_graph.service_context)
#         assert len(directory_graph.all_indices.values()) == len(loaded_directory_graph.all_indices.values())
#         for index, loaded_index in zip(directory_graph.all_indices.values(), loaded_directory_graph.all_indices.values()):
#             assert type(index) == type(loaded_index)