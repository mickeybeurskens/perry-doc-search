import pathlib
from llama_index.schema import Document
from llama_index.indices.base import BaseIndex
from perry.messages import MessageHistory
from perry.agents.base import Agent
from perry.agents.indexing import load_documents_with_unstructured, create_dir_index, save_indices


class SingleDirectoryVectorAgent(Agent):
    """ Transforms the documents of a single directory to a single vector index. """
    def __init__(self, document_directory: str):
        self.document_directory = document_directory
        self.name = "Single Directory Vector Agent"
        self.description = "Transforms the documents of a single directory to a single vector index."
        self.message_history = MessageHistory()

    def _set_up_agent(self) -> None:
        doc_lists = load_documents_with_unstructured(self.document_directory)
        index = create_dir_index(doc_lists.values())
        save_indices([index], [self._get_index_save_directory()])

    def answer_query(self, query: str) -> str:
        """ Answers a query. """
        return "Hello World!"

    def _get_index_save_directory(self) -> pathlib.Path:
        save_dir = self.document_directory / "single_directory_vector_agent" / "indices"
        if not save_dir.exists():
            save_dir.mkdir()
        return save_dir