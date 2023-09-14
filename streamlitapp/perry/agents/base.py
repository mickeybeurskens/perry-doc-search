from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session
from perry.db.models import Agent as DBAgent
from perry.db.operations.agents import read_agent, update_agent


class BaseAgentConfig(BaseModel):
    name: str


class BaseAgent(ABC):
    def __init__(self, db_session: Session, config: BaseAgentConfig, agent_id: int):
        self.config = config
        self.id = agent_id
        self._db_session = db_session
        self._agent_data = self._load_agent_data(db_session, agent_id)
        self._assert_conversation_data(self._agent_data)
        self._setup()

    @abstractmethod
    def _setup(self):
        """Agent specific setup logic."""

    @abstractmethod
    async def query(self, query: str) -> str:
        """Query the agent and get a response."""

    @abstractmethod
    def _on_save(self):
        """Agent specific save logic."""

    def save(self):
        """Save the state of the agent."""
        update_agent(self._db_session, self.id, config_data=self.config.dict())
        self._on_save()

    @classmethod
    @abstractmethod
    def _on_load(
        cls, db_session: Session, config: BaseAgentConfig, agent_id: int
    ) -> BaseAgent:
        """Agent specific loading logic."""

    @classmethod
    def load(cls, db_session: Session, agent_id: int) -> BaseAgent:
        """Load the agent state and return an instance of the agent."""
        config = cls._get_saved_config(db_session, agent_id)

        return cls._on_load(db_session, config, agent_id)

    @classmethod
    def _load_agent_data(cls, db_session: Session, agent_id: int) -> DBAgent:
        db_agent = read_agent(db_session, agent_id)
        if db_agent is None:
            raise ValueError(f"No agent found with ID {agent_id} in database.")
        return db_agent

    @classmethod
    def _get_saved_config(cls, db_session: Session, agent_id: int) -> BaseAgentConfig:
        agent_data = cls._load_agent_data(db_session, agent_id)
        cls._assert_conversation_data(agent_data)
        cls._assert_config_data(agent_data)
        return agent_data.config

    @staticmethod
    def _assert_conversation_data(db_agend: DBAgent):
        conversation_id = db_agend.conversation_id
        if conversation_id is None:
            raise ValueError(
                f"Agent with id {db_agend.id} not connected to a conversation."
            )

    @staticmethod
    def _assert_config_data(db_agend: DBAgent):
        agent_config = db_agend.config
        if agent_config is None:
            raise ValueError(f"Agent with id {db_agend.id} has no config.")


class AgentRegistry:
    _instance = None

    def __new__(cls) -> AgentRegistry:
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._agent_registry: Dict[str, Type[BaseAgent]] = {}
        return cls._instance

    def register_agent(self, agent_type: str, agent_class: Type[BaseAgent]):
        self._agent_registry[agent_type] = agent_class

    def create_agent(
        self, agent_type: str, config: BaseModel, agent_id: int
    ) -> BaseAgent:
        agent_class = self._agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent type {agent_type} not found.")
        return agent_class(config, agent_id)

    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        agent_class = self._agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent type {agent_type} not found.")
        return agent_class
