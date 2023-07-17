import pathlib
from llama_index.schema import Document
from llama_index.llms.base import LLM
from llama_index.indices.base import BaseIndex
from llama_index import StorageContext, ServiceContext, load_index_from_storage
from perry.utils import get_file_paths_from_dir
from perry.loaders.unstructured import UnstructuredReader


def load_documents_with_unstructured(data_dir: pathlib.Path) -> dict[pathlib.Path, list[Document]]:
    """Load documents for indexing from file path."""
    loader = UnstructuredReader()
    docs = {}
    for doc_path in get_file_paths_from_dir(data_dir):
        docs[doc_path] = loader.load_data(doc_path)
    return docs


def create_vector_indices(
        documents: list[Document], 
        index_type: BaseIndex,
        service_context: ServiceContext
    ) -> list[BaseIndex]:
    """ Index documents so they can be queried by a large language model. """
    indices = []
    for doc in documents:
        storage_context = StorageContext.from_defaults()
        index = index_type.from_documents(
            doc,
            service_context=service_context,
            storage_context=storage_context
        )
        indices.append(index)
    return indices


def save_indices(indices: list[BaseIndex], file_paths: list[pathlib.Path]) -> None:
    """Save vector indices."""
    for file_path, index in zip(file_paths, indices):
        index.storage_context.persist(persist_dir=file_path.parent)


def load_indices(file_paths: list[pathlib.Path]) -> list[BaseIndex]:
    """Load vector indices."""
    vector_indexes = []
    for file_path in file_paths:
        storage_context = StorageContext.from_defaults(persist_dir=file_path.parent)
        vector_index = load_index_from_storage(storage_context=storage_context)
        vector_indexes.append(vector_index)
    return vector_indexes
