import pytest
from perry.agents.base import BaseAgent, BaseAgentConfig, AgentRegistry
from unittest.mock import Mock, patch
from tests.agents.fixtures import DummyAgent


@pytest.fixture
def create_registry():
    yield AgentRegistry()
    AgentRegistry._instance = None


def test_agent_registry_singleton():
    registry1 = AgentRegistry()
    registry2 = AgentRegistry()
    assert registry1 is registry2


def test_register_agent(create_registry):
    registry = create_registry
    MockAgent = Mock(spec=BaseAgent)
    registry.register_agent("mock", MockAgent)
    assert "mock" in registry._agent_registry
    assert registry._agent_registry["mock"] == MockAgent


def test_get_registered_agent_class(create_registry):
    registry = create_registry
    registry.register_agent("dummy", DummyAgent)

    retrieved_class = registry.get_agent_class("dummy")

    assert retrieved_class == DummyAgent


def test_get_unregistered_agent_class_raises_value_error(create_registry):
    registry = create_registry

    with pytest.raises(ValueError) as e_info:
        registry.get_agent_class("nonexistent_type")

    assert str(e_info.value) == "Agent type nonexistent_type not found."


def test_get_agent_types(create_registry):
    registry = create_registry
    names = ["agent1", "agent2", "agent3"]
    for name in names:
        registry.register_agent(name, DummyAgent)

    assert registry.get_agent_types() == names


def get_agent_settings_schema(create_registry):
    registry = create_registry
    registry.register_agent("dummy", DummyAgent)

    schema = registry.get_agent_settings_schema("dummy")

    assert schema == DummyAgent._get_config_class().schema()
