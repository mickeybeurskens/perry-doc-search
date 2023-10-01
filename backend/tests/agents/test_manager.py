import pytest
from unittest.mock import Mock
from perry.agents.manager import AgentManager
from perry.agents.base import AgentRegistry
from perry.db.operations.agents import read_agent
from tests.agents.fixtures import DummyAgent
from datetime import datetime, timedelta
import freezegun


def mock_time():
    return datetime(2021, 1, 1)


@pytest.fixture
def manager():
    yield AgentManager()
    AgentManager.reset()


@pytest.fixture
def dummy_agent(test_db, add_agent_to_db, monkeypatch):
    with freezegun.freeze_time(mock_time()):
        agent_id = add_agent_to_db()
        db_agent = read_agent(test_db, agent_id)
        monkeypatch.setattr("perry.agents.manager.read_agent", lambda db, id: db_agent)

        AgentRegistry().register_agent(DummyAgent)
        agent = DummyAgent(test_db, {"name": "dummy"}, agent_id)
        agent.save()
        monkeypatch.setattr("perry.agents.base.BaseAgent.load", lambda db, id: agent)

        return agent


def test_load_agent_populates_dict(test_db, dummy_agent, manager, monkeypatch):
    test_id = 1
    agent = manager.load_agent(test_db, test_id)
    assert test_id in manager.agent_dict
    assert manager.agent_dict[test_id]["agent"] == agent


def test_load_agent_raises_error_on_missing_agent(test_db, manager, monkeypatch):
    monkeypatch.setattr("perry.db.operations.agents.read_agent", lambda db, id: None)

    with pytest.raises(ValueError):
        manager.load_agent(test_db, -1)


def test_id_should_be_int(test_db, manager):
    with pytest.raises(ValueError):
        manager.load_agent(test_db, "not_an_int")


def test_remove_agent_deletes_from_dict(test_db, dummy_agent, manager, monkeypatch):
    test_id = 1
    manager.load_agent(test_db, test_id)
    assert test_id in manager.agent_dict
    manager._remove_agent(test_id)
    assert test_id not in manager.agent_dict


def test_reset_should_reset_state(test_db, dummy_agent, manager, monkeypatch):
    AgentManager.agent_dict = {1: "dummy"}
    AgentManager.expiry_queue = "dummy"
    AgentManager.lock = "dummy"
    AgentManager._cleanup_timeout = "dummy"

    manager.reset()

    assert manager.agent_dict == {}
    assert manager.expiry_queue.empty()
    assert manager.lock is not None
    assert isinstance(manager._cleanup_timeout, timedelta)


def test_remove_agent_does_not_delete_busy_agent(
    test_db, dummy_agent, manager, monkeypatch
):
    test_id = 1
    agent = manager.load_agent(test_db, test_id)
    agent.busy = True
    manager._remove_agent(test_id)
    assert test_id in manager.agent_dict


def test_cleanup_removes_expired_agents(test_db, dummy_agent, manager, monkeypatch):
    mock_timer = Mock()
    monkeypatch.setattr("perry.agents.manager.Timer", mock_timer)

    test_id = 1
    with freezegun.freeze_time(mock_time()):
        manager.load_agent(test_db, test_id)
    with freezegun.freeze_time(
        mock_time() + manager._cleanup_timeout + timedelta(seconds=1)
    ):
        manager._cleanup()
        assert test_id not in manager.agent_dict
        assert mock_timer.call_count == 1


def test_cleanup_keeps_unexpired_agents(test_db, dummy_agent, manager, monkeypatch):
    mock_timer = Mock()
    monkeypatch.setattr("perry.agents.manager.Timer", mock_timer)

    test_id = 1
    with freezegun.freeze_time(mock_time()):
        manager.load_agent(test_db, test_id)
    with freezegun.freeze_time(
        mock_time() + manager._cleanup_timeout - timedelta(seconds=1)
    ):
        manager._cleanup()
        assert test_id in manager.agent_dict
        assert mock_timer.call_count == 1
