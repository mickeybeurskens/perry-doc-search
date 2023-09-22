import pytest
from unittest.mock import PropertyMock
from perry.agents.echo import EchoAgent
from perry.agents.base import BaseAgentConfig, BaseAgent
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from perry.db.operations.agents import update_agent
from tests.agents.fixtures_subquestion import *

agents_to_test = [
    (EchoAgent, BaseAgentConfig(name="EchoAgentTest").dict()),
    (
        SubquestionAgent,
        SubquestionConfig(
            name="SubquestionAgentTest",
            language_model_name="gpt3.5-turbo",
            temperature=0.3,
        ).dict(),
    )
    # Add other agents and their configurations here
]


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_class, config", agents_to_test)
async def test_agent_query_returns_string(
    test_db, agent_class, config, add_agent_to_db, add_conversation_to_db, monkeypatch
):
    agent_id = add_agent_to_db()
    conversation_id = add_conversation_to_db()
    update_agent(test_db, agent_id, conversation_id=conversation_id)
    agent_instance = agent_class(test_db, config, agent_id)

    response = await agent_instance.query("test query")
    assert isinstance(response, str)


@pytest.mark.parametrize("agent_class, config", agents_to_test)
def test_load_should_return_agent_instance(
    agent_class, test_db, config, add_agent_to_db, add_conversation_to_db
):
    agent_id = add_agent_to_db()
    conversation_id = add_conversation_to_db()
    update_agent(test_db, agent_id, conversation_id=conversation_id)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_class, config", agents_to_test)
async def test_busy_toggle_decorator_is_called(
    agent_class, config, test_db, add_agent_to_db, add_conversation_to_db, monkeypatch
):
    agent_id = add_agent_to_db()
    conversation_id = add_conversation_to_db()
    update_agent(test_db, agent_id, conversation_id=conversation_id)

    async def mock_query(self, query):
        return "test response"

    mock_busy = PropertyMock(return_value=False)
    agent_class.busy = mock_busy
    agent_class._on_query = mock_query
    agent_class._on_save = lambda self: None

    agent_instance = agent_class(test_db, config, agent_id)
    mock_busy.call_count == 3

    mock_busy.reset_mock()

    agent_instance.save()
    assert mock_busy.call_count == 2

    mock_busy.reset_mock()

    await agent_instance.query("test query")
    assert mock_busy.call_count == 2
