from perry.agents.base import BaseAgent, BaseAgentConfig
from sqlalchemy.orm import Session


class EchoAgent(BaseAgent):
    """An agent that echoes the query."""

    def _setup(self):
        pass

    async def _on_query(self, query: str) -> str:
        return "Echo: " + query

    def _on_save(self):
        pass

    @classmethod
    @staticmethod
    def _get_config_class() -> type[BaseAgentConfig]:
        return BaseAgentConfig

    @classmethod
    def _on_load(
        cls, db_session: Session, config: BaseAgentConfig, agent_id: int
    ) -> BaseAgent:
        return cls(db_session, config, agent_id)
