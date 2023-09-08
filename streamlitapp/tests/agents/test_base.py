import pytest
from perry.agents.base import BaseAgent, BaseAgentConfig, AgentRegistry
from unittest.mock import Mock, patch

# Test that AgentRegistry is a Singleton
def test_agent_registry_singleton():
    registry1 = AgentRegistry()
    registry2 = AgentRegistry()
    assert registry1 is registry2

# Test registering an agent
def test_register_agent():
    registry = AgentRegistry()
    MockAgent = Mock(spec=BaseAgent)
    registry.register_agent("mock", MockAgent)
    assert "mock" in registry._agent_registry
    assert registry._agent_registry["mock"] == MockAgent

# Test creating an agent
def test_create_agent():
    registry = AgentRegistry()
    MockAgent = Mock(spec=BaseAgent)
    registry.register_agent("mock", MockAgent)
    
    config = BaseAgentConfig(name="TestAgent")
    agent = registry.create_agent("mock", config, 1)
    
    assert isinstance(agent, Mock)

# Test error scenario for unregistered agent type
def test_create_unregistered_agent():
    registry = AgentRegistry()
    with pytest.raises(ValueError):
        registry.create_agent("unregistered", BaseAgentConfig(name="Test"))
