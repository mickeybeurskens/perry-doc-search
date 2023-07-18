from langchain.chains.conversation.memory import ConversationBufferMemory

from llama_index import VectorStoreIndex
from llama_index.bridge.langchain import AgentExecutor
from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig

from langchain.chat_models import ChatOpenAI
from perry.documents import DocumentMetadata


def create_document_index_tool_configs(vector_indexes: list[VectorStoreIndex], metadata: list[DocumentMetadata]) -> dict[str, IndexToolConfig]:
    """Create vector index tool configs."""
    index_tool_configs = []
    for doc_meta, vector_index in zip(metadata, vector_indexes):
        query_engine = vector_index.as_query_engine(
            similarity_top_k=3,
        )
        index_tool_configs.append(IndexToolConfig(
            query_engine=query_engine,
            name=f"Document: {doc_meta.file_path.name}",
            description=doc_meta.summary,
            tool_kwargs={"return_direct": True}
        ))
    return index_tool_configs

def create_langchain_toolkit(index_tool_configs: list[IndexToolConfig]) -> LlamaToolkit:
    """Create LangChain toolkit."""
    return LlamaToolkit(index_configs= index_tool_configs)

def create_langchain_chat_agent(toolkit: LlamaToolkit) -> AgentExecutor:
    """Create LangChain chat agent."""
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm=ChatOpenAI(temperature=0, model_name="gpt-4")
    return create_llama_chat_agent(
        toolkit,
        llm,
        memory=memory,
        verbose=True
    )
