import pathlib
from llama_index.schema import Document
from llama_index.indices.base import BaseIndex
from perry.messages import MessageHistory, Message
from perry.agents.base import Agent
from perry.agents.indexing import load_documents_with_unstructured, create_file_indices, save_indices
from perry.agents.utils import create_document_index_tool_configs, create_langchain_toolkit, create_langchain_chat_agent

class SingleDirectoryVectorAgent(Agent):
    """ Transforms the documents of a single directory to a single vector index. """
    def __init__(self, document_directory: str):
        self.document_directory = document_directory
        self.name = "Single Directory Vector Agent"
        self.description = "Transforms the documents of a single directory to a single vector index."
        self.message_history = MessageHistory()
        self.message_index = 0

    def _set_up_agent(self) -> None:
        docs, metadata = load_documents_with_unstructured(self.document_directory)
        indices = create_file_indices(docs)
        save_indices(indices, [self._get_index_save_directory()])
        tool_configs = create_document_index_tool_configs(indices, metadata)
        toolkit = create_langchain_toolkit(tool_configs)
        self.agent = create_langchain_chat_agent(toolkit)

    def answer_query(self, query: str) -> str:
        """ Answers a query. """
        query_message = Message(
            index=self.message_index,
            user="user",
            message=query,
        )
        self.message_index += 1

        response = self.agent.run(query)
        response_message = Message(
            index=self.message_index,
            user="perry",
            message=response,
        )
        self.message_index += 1
        self.message_history.add_message(query_message)
        self.message_history.add_message(response_message)
        return response

    def _get_index_save_directory(self) -> pathlib.Path:
        save_dir = self.document_directory / "single_directory_vector_agent" / "indices"
        if not save_dir.exists():
            save_dir.mkdir()
        return save_dir