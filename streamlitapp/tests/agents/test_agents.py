import pytest
from perry.agents.echo import EchoAgent
from perry.agents.base import BaseAgentConfig
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig


agents_to_test = [
    (EchoAgent, BaseAgentConfig(name="EchoAgentTest")),
    (
        SubquestionAgent,
        SubquestionConfig(
            name="SubquestionAgentTest",
            language_model_name="gpt3.5-turbo",
            temperature=0.3,
        ),
    )
    # Add other agents and their configurations here
]


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_class, config", agents_to_test)
async def test_agent_query_returns_string(
    agent_class, config, test_db, add_connected_agent_and_conversation_to_db
):
    agent_id, conversation_id = add_connected_agent_and_conversation_to_db
    agent_instance = agent_class(test_db, config, agent_id)
    response = await agent_instance.query("test query")
    assert isinstance(response, str)


# TODO: Fix saving and loading generally
# TODO: Use fixtures to create agents and conversations
@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_return_agent_instance(agent_class, config, test_db, add_connected_agent_and_conversation_to_db):
    agent_id, conversation_id = add_connected_agent_and_conversation_to_db
    agent = agent_class(test_db, config, agent_id)
    agent.save()
    # loaded_agent = agent_class.load(test_db, agent_id)
    # assert isinstance(loaded_agent, agent_class)
    # assert loaded_agent.config == agent.config


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_raise_value_error_when_agent_not_found(
    agent_class, config, test_db
):
    with pytest.raises(ValueError):
        agent_class.load(test_db, -1)


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_raise_value_error_when_agent_not_connected_to_conversation(
    agent_class, config, test_db, add_agent_to_db
):
    with pytest.raises(ValueError):
        agent_class.load(test_db, add_agent_to_db)
