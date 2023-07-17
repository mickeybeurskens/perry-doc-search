from langchain.chains.conversation.memory import ConversationBufferMemory

from llama_index import VectorStoreIndex
from llama_index.bridge.langchain import AgentExecutor
from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig

from langchain.chat_models import ChatOpenAI


def create_vector_index_tool_configs(vector_indexes: dict[str, list[VectorStoreIndex]]) -> dict[str, IndexToolConfig]:
    """Create vector index tool configs."""
    index_tool_configs = {}
    for doc_name, vector_index in vector_indexes.items():
        query_engine = vector_index.as_query_engine(
            similarity_top_k=3,
        )
        index_tool_configs[doc_name] = IndexToolConfig(
            query_engine=query_engine,
            name=f"Vector Index {doc_name}",
            description=f"Aanbestedingsleidraad voor rijkswaterstaat opdrachten",
            tool_kwargs={"return_direct": True}
        )
    return index_tool_configs

def create_langchain_toolkit(index_tool_configs: dict[str, IndexToolConfig]) -> LlamaToolkit:
    """Create LangChain toolkit."""
    return LlamaToolkit(index_configs= list(index_tool_configs.values()))

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
