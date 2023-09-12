import pytest
from perry.agents.echo import EchoAgent
from perry.agents.base import BaseAgentConfig
from perry.db.operations.agents import create_agent


agents_to_test = [
    (EchoAgent, BaseAgentConfig(name='EchoAgent')),
    # Add other agents and their configurations here
]

@pytest.mark.asyncio
@pytest.mark.parametrize('agent_class, config', agents_to_test)
async def test_agent_query_returns_string(agent_class, config, test_db):
    agent_instance = agent_class(config, 1, test_db)
    response = await agent_instance.query("test query") 
    assert isinstance(response, str)

@pytest.mark.asyncio
@pytest.mark.parametrize('agent_class, config', agents_to_test)
async def test_load_should_return_agent_instance(agent_class, config, test_db):
    agent_id = create_agent(test_db)
    loaded_agent = agent_class.load(agent_id, test_db)
    assert isinstance(loaded_agent, agent_class)