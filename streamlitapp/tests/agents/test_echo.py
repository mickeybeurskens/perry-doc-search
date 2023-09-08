from perry.agents.base import BaseAgentConfig
from perry.agents.echo import EchoAgent


def test_query():
    config = BaseAgentConfig(name="TestAgent")
    agent = EchoAgent(config, 1)
    response = agent.query("some_query")
    assert response == "Echo: some_query"


def test_save():
    config = BaseAgentConfig(name="TestAgent")
    agent = EchoAgent(config, 1)
    agent.save()


def test_load():
    loaded_agent = EchoAgent.load(1)
    assert loaded_agent is None
