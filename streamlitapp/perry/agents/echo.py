from perry.agents.base import BaseAgent, BaseAgentConfig
from sqlalchemy.orm import Session
from perry.db.models import Agent


class EchoAgent(BaseAgent):
    """ An agent that echoes the query. """
    def __init__(self, config: BaseAgentConfig, agent_id: int, db_session: Session):
        self.config = config
        self.id = agent_id
        self._db_session = db_session

    async def query(self, query: str) -> str:
        return "Echo: " + query

    def save(self):
        pass

    @classmethod
    def load(cls, db_session: Session, agent_id: int) -> BaseAgent:
        cls._load_agent_db_data(db_session, agent_id)

        base_config = BaseAgentConfig(name="EchoAgent")
        return cls(base_config, agent_id, db_session)