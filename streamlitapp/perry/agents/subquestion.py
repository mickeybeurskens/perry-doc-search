import asyncio
from pathlib import Path
from llama_index import (
    Document,
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    Prompt,
)
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
import openai
from sqlalchemy.orm import Session

from perry.agents.base import BaseAgent, BaseAgentConfig
from perry.db.models import Document as PerryDocument, User, Agent
from perry.db.operations.agents import read_agent

class SubquestionConfig(BaseAgentConfig):
    """Configuration for the SubquestionAgent."""

    name: str
    subquestions: list
    language_model_name: str
    temperature: float


class SubquestionAgent(BaseAgent):
    """An agent that queries a set of indexed documents by posing subquestions."""

    def __init__(self, config: SubquestionConfig, agent_id: int, db_session: Session):
        self.config = config
        self.id = agent_id
        self._db_session = db_session

        self._init_agent()

    def _init_agent(self):
        self._agent = read_agent(self._db_session, self.id)
        if self._agent is None:
            raise ValueError(f"Agent with id {self.id} not found in database.")
        
        self._conversation_id = self._agent.conversation_id
        if self._conversation_id is None:
            raise ValueError(f"Agent with id {self.id} not connected to a conversation.")


    def query(self, query: str) -> str:
        return "Echo: " + query

    def save(self):
        pass

    @classmethod
    def load(cls, agent_id: int) -> BaseAgent:
        pass
