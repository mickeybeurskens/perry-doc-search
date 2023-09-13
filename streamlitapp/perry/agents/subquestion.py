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

    def _setup(self):
        pass

    async def query(self, query: str) -> str:
        return "Echo: " + query

    def _on_save(self):
        pass

    @classmethod
    def _on_load(cls, db_session: Session, config: SubquestionConfig, agent_id: int) -> BaseAgent:
        return cls(db_session, config, agent_id)

