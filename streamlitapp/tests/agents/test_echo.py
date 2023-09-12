import pytest
from perry.agents.base import BaseAgentConfig
from perry.agents.echo import EchoAgent
from perry.db.operations.agents import create_agent
from perry.db.operations.conversations import create_conversation
from perry.db.api import connect_agent_to_conversation


@pytest.mark.asyncio
async def test_query(test_db):
    config = BaseAgentConfig(name="TestAgent")
    agent_id = create_agent(test_db)
    agent = EchoAgent(config, agent_id, test_db)
    response = await agent.query("some_query")
    assert response == "Echo: some_query"


def test_save(test_db):
    config = BaseAgentConfig(name="TestAgent")
    agent_id = create_agent(test_db)
    agent = EchoAgent(config, agent_id, test_db)
    agent.save()


def test_load(test_db):
    agent_id = create_agent(test_db)
    conversation_id = create_conversation(test_db)
    connect_agent_to_conversation(test_db, agent_id, conversation_id)
    loaded_agent = EchoAgent.load(agent_id, test_db)
    assert isinstance(loaded_agent, EchoAgent)
