import pathlib
from llama_index.schema import Document
from llama_index.indices.base import BaseIndex
from llama_index.composability import ComposableGraph
from llama_index import StorageContext, ServiceContext, load_index_from_storage
from perry.utils import get_file_paths_from_dir
from perry.loaders.unstructured import UnstructuredReader
from perry.documents import DocumentMetadata, load_metadata_from_document_path


def load_documents_with_unstructured(data_dir: pathlib.Path) -> tuple[list[Document], list[DocumentMetadata]]:
    """Load documents for indexing from file path."""
    loader = UnstructuredReader()
    docs = []
    metadata = []
    for doc_path in get_file_paths_from_dir(data_dir):
        docs.append(loader.load_data(doc_path))
        metadata.append(load_metadata_from_document_path(doc_path))
    return (docs, metadata)


def create_file_indices(
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


def create_dir_index(
        documents: list[Document], 
        index_type: BaseIndex,
        service_context: ServiceContext
    ) -> BaseIndex:
    """ Index documents so they can be queried by a large language model. """

    storage_context = StorageContext.from_defaults()
    index = index_type.from_documents(
        documents,
        service_context=service_context,
        storage_context=storage_context
    )
    return index



# def create_directory_graph(
#         document_indices: list[BaseIndex],
#         document_metadata: list[DocumentMetadata],
#         index_type: BaseIndex,
#         service_context: ServiceContext,
#     ) -> ComposableGraph:
#     """Create a directory graph, composed of individual document indices."""
#     storage_context = StorageContext.from_defaults()
#     graph = ComposableGraph.from_indices(
#         index_type,
#         document_indices,
#         index_summaries=[doc_meta.summary for doc_meta in document_metadata],
#         service_context=service_context,
#         storage_context=storage_context
#     )
#     return graph


def save_indices(indices: list[BaseIndex], file_paths: list[pathlib.Path]) -> None:
    """Save vector indices."""
    for file_path, index in zip(file_paths, indices):
        index.storage_context.persist(persist_dir=file_path.parent)


def load_indices(file_paths: list[pathlib.Path]) -> list[BaseIndex]:
    """Load vector indices from a directory."""
    vector_indexes = []
    for file_path in file_paths:
        storage_context = StorageContext.from_defaults(persist_dir=file_path.parent)
        vector_index = load_index_from_storage(storage_context=storage_context)
        vector_indexes.append(vector_index)
    return vector_indexes
