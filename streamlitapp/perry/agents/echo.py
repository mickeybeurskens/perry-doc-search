from perry.agents.base import BaseAgent, BaseAgentConfig


class EchoAgent(BaseAgent):
    def __init__(self, config: BaseAgentConfig, agent_id: int):
        self.config = config
        self.id = agent_id

    def query(self, query: str) -> str:
        return "Echo: " + query

    def save(self):
        pass

    @classmethod
    def load(cls, agent_id: int) -> BaseAgent:
        pass