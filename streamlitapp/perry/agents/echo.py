from perry.agents.base import BaseAgent, BaseAgentConfig
from sqlalchemy.orm import Session
from perry.db.models import Agent


class EchoAgent(BaseAgent):
    """ An agent that echoes the query. """
    def __init__(self, db_session: Session, config: BaseAgentConfig, agent_id: int):
        self.config = config
        self.id = agent_id
        self._db_session = db_session
        self._agent_data = self._assert_db_data(db_session, agent_id)

    async def query(self, query: str) -> str:
        return "Echo: " + query

    def _on_save(self):
        pass

    @classmethod
    def _on_load(cls, db_session: Session, agent_id: int) -> BaseAgent:
        cls._assert_db_data(db_session, agent_id)

        base_config = BaseAgentConfig(name="EchoAgent")
        return cls(db_session, base_config, agent_id)