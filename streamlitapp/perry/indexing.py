import pathlib
from llama_index.schema import Document
from llama_index.llms.base import LLM
from llama_index.indices.base import BaseIndex
from llama_index.readers.base import BaseReader
from llama_index import VectorStoreIndex, StorageContext, ServiceContext, load_index_from_storage
from perry.utils import load_openai_api_key, get_file_paths_from_dir


def load_documents(data_dir: pathlib.Path, loader: BaseReader) -> dict[pathlib.Path ,list[Document]]:
    """Load documents for indexing from file path."""
    docs = {}
    for doc_path in get_file_paths_from_dir(data_dir):
        docs[doc_path] = loader.load_data(doc_path)
    return docs


def create_vector_indices(documents: list[Document], llm: LLM = None) -> list[VectorStoreIndex]:
    """Create and store vector indices."""
    load_openai_api_key()
    if llm:
      service_context = ServiceContext.from_defaults(llm=llm, chunk_size=512)
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
