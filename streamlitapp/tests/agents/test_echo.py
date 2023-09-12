import pytest
from perry.agents.base import BaseAgentConfig
from perry.agents.echo import EchoAgent
from perry.db.operations.agents import create_agent


@pytest.mark.asyncio
async def test_query(test_db):
    config = BaseAgentConfig(name="TestAgent")
    agent = EchoAgent(config, 1, test_db)
    response = await agent.query("some_query")
    assert response == "Echo: some_query"


def test_save(test_db):
    config = BaseAgentConfig(name="TestAgent")
    agent = EchoAgent(config, 1, test_db)
    agent.save()


def test_load(test_db):
    agent_id = create_agent(test_db)
    loaded_agent = EchoAgent.load(agent_id, test_db)
    assert isinstance(loaded_agent, EchoAgent)
