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
from perry.db.models import Document as DBDocument, User as DBUser, Agent as DBAgent


class SubquestionConfig(BaseAgentConfig):
    """Configuration for the SubquestionAgent."""

    name: str
    language_model_name: str
    temperature: float


class SubquestionAgent(BaseAgent):
    """An agent that queries a set of indexed documents by posing subquestions."""

    def __init__(self, db_session: Session, config: SubquestionConfig, agent_id: int):
        self.config = config
        self.id = agent_id
        self._db_session = db_session

        agent_data = self._assert_db_data(db_session, agent_id)

    async def query(self, query: str) -> str:
        return "Echo: " + query

    def _on_save(self):
        pass

    @classmethod
    def _on_load(cls, db_session: Session, agent_id: int) -> BaseAgent:
        config = SubquestionConfig(name="SubquestionAgent",
                                    language_model_name="gpt3.5-turbo",
                                    temperature=0.3)
        return cls(db_session, config, agent_id)

