from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session
from perry.db.models import Agent as DBAgent
from perry.db.operations.agents import read_agent


class BaseAgentConfig(BaseModel):
    name: str


class BaseAgent(ABC):

    def __init__(self, config: BaseAgentConfig, agent_id: int, db_session: Session):
        self.config = config
        self.id = agent_id
        self._db_session = db_session

    @abstractmethod
    async def query(self, query: str) -> str:
        """ Query the agent and get a response. """

    @abstractmethod
    def save(self):
        """ Save the agent state. """

    @classmethod
    @abstractmethod
    def load(cls, agent_id: int) -> BaseAgent:
        """ Load the agent state. """

    @staticmethod
    def _load_agent_db_data(db_session: Session, agent_id: int) -> DBAgent:
        agent_data = read_agent(db_session, agent_id)

        if agent_data is None:
            raise ValueError(f"No agent found with ID {agent_id} in database.")
        
        conversation_id = agent_data.conversation_id
        if conversation_id is None:
            raise ValueError(f"Agent with id {agent_data.id} not connected to a conversation.")


class AgentRegistry:
    _instance = None

    def __new__(cls) -> AgentRegistry:
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._agent_registry: Dict[str, Type[BaseAgent]] = {}
        return cls._instance

    def register_agent(self, agent_type: str, agent_class: Type[BaseAgent]):
        self._agent_registry[agent_type] = agent_class

    def create_agent(self, agent_type: str, config: BaseModel, agent_id: int) -> BaseAgent:
        agent_class = self._agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent type {agent_type} not found.")
        return agent_class(config, agent_id)
    
    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        agent_class = self._agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent type {agent_type} not found.")
        return agent_class
