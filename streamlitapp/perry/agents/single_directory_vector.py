import pathlib
from llama_index import ServiceContext, VectorStoreIndex
from perry.messages import MessageHistory, Message
from perry.agents.base import Agent
from perry.agents.indexing import load_documents_with_unstructured, create_file_indices, save_indices
from perry.agents.utils import create_document_index_tool_configs, create_langchain_toolkit, create_langchain_chat_agent
from perry.utils import load_openai_api_key, get_production_env_path


class SingleDirectoryVectorAgent(Agent):
    """ Transforms the documents of a single directory to a single vector index. """
    def __init__(self, document_directory: str):
        load_openai_api_key(get_production_env_path())
        self.document_directory = document_directory
        self.name = "Single Directory Vector Agent"
        self.description = "Transforms the documents of a single directory to a single vector index."
        self.message_history = MessageHistory(index=0, messages=[])
        self.message_index = 0
        self._set_up_agent()

    def _set_up_agent(self) -> None:
        docs, metadata = load_documents_with_unstructured(self.document_directory)
        self.service_context = ServiceContext.from_defaults()
        indices = create_file_indices(docs, VectorStoreIndex, self.service_context)
        save_indices(indices, [self._get_index_save_directory()])
        tool_configs = create_document_index_tool_configs(indices, metadata)
        self.meta = metadata
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
            user="assistant",
            message=response,
        )

        self.message_index += 1

        old_message_history_messages = self.message_history.messages
        new_message_history_messages = old_message_history_messages + [query_message, response_message]
        self.message_history = MessageHistory(messages=new_message_history_messages, index=0)
        return response

    def _get_index_save_directory(self) -> pathlib.Path:
        save_dir = self.document_directory / "single_directory_vector_agent" / "indices"
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        return save_dir
    

if __name__ == "__main__":
    import pathlib
    from perry.documents import DocumentMetadata, save_document_metadata
    meta = DocumentMetadata(
        title="test_1.txt",
        summary="This document contains a password.",
        file_path=pathlib.Path(__file__).parent.parent.parent / "storage" / "test_1.txt",
    )
    save_document_metadata(meta)
    agent = SingleDirectoryVectorAgent(pathlib.Path(__file__).parent.parent.parent / "storage")
    agent.answer_query("Retrieve the password mentioned in the file.")