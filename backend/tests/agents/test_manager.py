import pytest
from perry.agents.manager import AgentManager
from tests.agents.fixtures import DummyAgent
from datetime import datetime, timedelta
import freezegun


def mock_time():
    return datetime(2021, 1, 1)


@pytest.fixture
def manager(test_db):
    return AgentManager(test_db)


@pytest.fixture
def dummy_agent(test_db, add_agent_to_db):
    with freezegun.freeze_time(mock_time()):
        agent_id = add_agent_to_db()
        agent = DummyAgent(test_db, {"name": "dummy"}, agent_id)
        agent.save()
        return agent


def test_load_agent_populates_dict(dummy_agent, manager, monkeypatch):
    monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: True)
    monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: dummy_agent)

    agent = manager.load_agent("test_id")
    assert "test_id" in manager.agent_dict
    assert manager.agent_dict["test_id"]["agent"] == agent


def test_load_agent_raises_error_on_missing_agent(manager, monkeypatch):
    monkeypatch.setattr("perry.db.operations.agents.read_agent", lambda db, id: None)

    with pytest.raises(ValueError):
        manager.load_agent("missing_id")


def test_remove_agent_deletes_from_dict(dummy_agent, manager, monkeypatch):
    # Mock the read_agent and BaseAgent.load functions
    monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: True)
    monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: dummy_agent)

    agent = manager.load_agent("test_id")
    manager._remove_agent("test_id")
    assert "test_id" not in manager.agent_dict


def test_remove_agent_does_not_delete_busy_agent(dummy_agent, manager, monkeypatch):
    # Mock the read_agent and BaseAgent.load functions
    monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: True)
    monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: dummy_agent)

    agent = manager.load_agent("test_id")
    agent.busy = True
    manager._remove_agent("test_id")
    assert "test_id" in manager.agent_dict


def test_cleanup_removes_expired_agents(dummy_agent, manager, monkeypatch):
    # Mock the read_agent, BaseAgent.load, and time.time functions
    monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: True)
    monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: dummy_agent)

    agent = manager.load_agent("test_id")
    with freezegun.freeze_time(
        mock_time() + manager._cleanup_timeout + timedelta(seconds=1)
    ):
        manager._cleanup()
    assert "test_id" not in manager.agent_dict


def test_cleanup_keeps_unexpired_agents(dummy_agent, manager, monkeypatch):
    # Mock the read_agent, BaseAgent.load, and time.time functions
    monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: True)
    monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: dummy_agent)
    monkeypatch.setattr("time.time", lambda: 0)

    agent = manager.load_agent("test_id")
    monkeypatch.setattr("time.time", lambda: manager._cleanup_timeout - 1)
    manager._cleanup()
    assert "test_id" in manager.agent_dict
