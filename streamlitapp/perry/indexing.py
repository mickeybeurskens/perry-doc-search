import pathlib
from llama_index.schema import Document
from llama_index.llms.base import LLM
from llama_index.indices.base import BaseIndex
from llama_index import VectorStoreIndex, StorageContext, ServiceContext, load_index_from_storage
from perry.utils import get_file_paths_from_dir
from perry.loaders.unstructured import UnstructuredReader


def load_documents_with_unstructured(data_dir: pathlib.Path) -> dict[pathlib.Path, list[Document]]:
    """Load documents for indexing from file path."""
    loader = UnstructuredReader()
    docs = {}
    for doc_path in get_file_paths_from_dir(data_dir):
        docs[doc_path] = loader.load_data(doc_path)
    return docs


def create_vector_indices(documents: list[Document], llm: LLM = None) -> list[VectorStoreIndex]:
    """Create and store vector indices."""
    if llm:
      service_context = ServiceContext.from_defaults(llm=llm)
    else:
      service_context = ServiceContext.from_defaults(chunk_size=512)

    vector_indices = []
    for doc in documents:
        storage_context = StorageContext.from_defaults()
        vector_index = VectorStoreIndex.from_documents(
            doc,
            service_context=service_context,
            storage_context=storage_context
        )
        vector_indices.append(vector_index)
    return vector_indices


def save_indices(indices: list[BaseIndex], file_paths: list[pathlib.Path]) -> None:
    """Save vector indices."""
    for file_path, index in zip(file_paths, indices):
        index.storage_context.persist(persist_dir=file_path)


def load_indices(file_paths: list[pathlib.Path]) -> list[VectorStoreIndex]:
    """Load vector indices."""
    vector_indexes = []
    for file_path in file_paths:
        storage_context = StorageContext.from_defaults(persist_dir=file_path)
        vector_index = load_index_from_storage(storage_context=storage_context)
        vector_indexes.append(vector_index)
    return vector_indexes
