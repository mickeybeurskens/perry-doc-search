from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type
from threading import Lock
from functools import wraps
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from perry.db.models import Agent as DBAgent
from perry.db.operations.agents import read_agent, update_agent


def busy_toggle(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._busy_lock:
            self.busy = True
        try:
            result = func(self, *args, **kwargs)
        finally:
            with self._busy_lock:
                self.busy = False
        return result

    return wrapper


class BaseAgentConfig(BaseModel):
    name: str = Field(
        type="string",
        title="Agent Name",
    )


class BaseAgent(ABC):
    def __init__(self, db_session: Session, config: dict, agent_id: int):
        self.config = self._get_config_instance(config)
        self.id = agent_id
        self.busy = False
        self._busy_lock = Lock()
        self._db_session = db_session
        self._agent_data = self._load_agent_data(db_session, agent_id)
        self._setup()

    @abstractmethod
    def _setup(self):
        """Agent specific setup logic."""

    @abstractmethod
    async def _on_query(self, query: str) -> str:
        """Query the agent and get a response."""

    @busy_toggle
    async def query(self, query: str) -> str:
        """Query the agent and get a response."""
        response = await self._on_query(query)
        return response

    @abstractmethod
    def _on_save(self):
        """Agent specific save logic."""

    @busy_toggle
    def save(self):
        """Save the state of the agent."""
        update_agent(
            self._db_session,
            self.id,
            config_data=self.config.dict(),
            agent_type=self.__class__.__name__,
        )
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
        config_dict = cls._get_saved_config(db_session, agent_id)
        return cls._on_load(db_session, config_dict, agent_id)

    @classmethod
    def _load_agent_data(cls, db_session: Session, agent_id: int) -> DBAgent:
        db_agent = read_agent(db_session, agent_id)
        if db_agent is None:
            raise ValueError(f"No agent found with ID {agent_id} in database.")
        return db_agent

    @classmethod
    @abstractmethod
    def _get_config_class(cls) -> type[BaseAgentConfig]:
        """Return the config class used."""

    @classmethod
    def _get_config_instance(cls, config_data: dict) -> BaseAgentConfig:
        """Return the config class used."""
        return cls._get_config_class()(**config_data)

    @classmethod
    def _get_saved_config(cls, db_session: Session, agent_id: int) -> BaseAgentConfig:
        agent_data = cls._load_agent_data(db_session, agent_id)
        cls._assert_config_data(agent_data)
        return agent_data.config

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

    def register_agent(self, agent_class: Type[BaseAgent]):
        self._agent_registry[agent_class.__name__] = agent_class

    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        agent_class = self._agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent type {agent_type} not found.")
        return agent_class

    def get_agent_types(self):
        return list(self._agent_registry.keys())

    def get_agent_settings_schema(self, agent_type: str):
        agent_class = self.get_agent_class(agent_type)
        return agent_class._get_config_class().schema()["properties"]

    def reset(self):
        self._instance = None
