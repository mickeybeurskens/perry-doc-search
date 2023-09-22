import pytest
from perry.agents.base import BaseAgent, BaseAgentConfig, AgentRegistry
from unittest.mock import Mock, patch
from tests.agents.fixtures import DummyAgent


def test_agent_registry_singleton():
    registry1 = AgentRegistry()
    registry2 = AgentRegistry()
    assert registry1 is registry2


def test_register_agent():
    registry = AgentRegistry()
    MockAgent = Mock(spec=BaseAgent)
    registry.register_agent("mock", MockAgent)
    assert "mock" in registry._agent_registry
    assert registry._agent_registry["mock"] == MockAgent


def test_get_registered_agent_class():
    registry = AgentRegistry()
    registry.register_agent("dummy", DummyAgent)

    retrieved_class = registry.get_agent_class("dummy")

    assert retrieved_class == DummyAgent


def test_get_unregistered_agent_class_raises_value_error():
    registry = AgentRegistry()

    with pytest.raises(ValueError) as e_info:
        registry.get_agent_class("nonexistent_type")

    assert str(e_info.value) == "Agent type nonexistent_type not found."
