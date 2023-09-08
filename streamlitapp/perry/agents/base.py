from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type
from pydantic import BaseModel


class BaseAgentConfig(BaseModel):
    name: str


class BaseAgent(ABC):

    def __init__(self, config: BaseAgentConfig, agent_id: int):
        self.config = config
        self.id = agent_id

    @abstractmethod
    def query(self, query: str) -> str:
        """ Query the agent and get a response. """

    @abstractmethod
    def save(self):
        """ Save the agent state. """

    @abstractmethod
    def load(self, agent_id: int):
        """ Load the agent state. """


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
