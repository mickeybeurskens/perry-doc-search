import pytest
from perry.agents.echo import EchoAgent
from perry.agents.base import BaseAgentConfig, BaseAgent
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from perry.db.api import connect_agent_to_conversation

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
    test_db, agent_class, config, add_agent_to_db, add_conversation_to_db
):
    agent_id = add_agent_to_db()
    conversation_id = add_conversation_to_db()
    connect_agent_to_conversation(test_db, agent_id, conversation_id)
    agent_instance = agent_class(test_db, config, agent_id)
    response = await agent_instance.query("test query")
    assert isinstance(response, str)


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_return_agent_instance(
    agent_class, test_db, config, add_agent_to_db, add_conversation_to_db
):
    agent_id = add_agent_to_db()
    conversation_id = add_conversation_to_db()
    connect_agent_to_conversation(test_db, agent_id, conversation_id)
    agent = agent_class(test_db, config, agent_id)
    agent.save()
    loaded_agent = agent_class.load(test_db, agent.id)

    assert isinstance(loaded_agent, agent_class)
    assert loaded_agent.config == agent.config


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_init_should_raise_value_error_when_agent_not_found(
    agent_class, config, test_db
):
    with pytest.raises(ValueError):
        agent_class(test_db, config, -1)


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_init_should_raise_value_error_when_agent_not_connected_to_conversation(
    agent_class, config, test_db, add_agent_to_db
):
    with pytest.raises(ValueError):
        agent_class(test_db, config, add_agent_to_db())


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_raise_value_error_when_agent_not_found(
    agent_class, config, test_db
):
    with pytest.raises(ValueError):
        agent_class.load(test_db, -1)


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_raise_value_error_when_agent_not_connected_to_conversation(
    agent_class: BaseAgent, config, test_db, add_agent_to_db
):
    agent_id = add_agent_to_db()
    with pytest.raises(ValueError):
        agent_class.load(test_db, agent_id)
