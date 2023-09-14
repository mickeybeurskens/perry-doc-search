from perry.db.operations.agents import *
from perry.db.models import Agent

def test_should_create_agent_and_return_agent_instance(test_db):
    agent_id = create_agent(test_db)
    agent = test_db.query(Agent).filter_by(id=agent_id).first()
    assert isinstance(agent, Agent)
    assert agent.config is None

def test_should_return_agent_given_valid_agent_id(test_db, add_agent_to_db):
    agent_id = add_agent_to_db()
    agent = read_agent(test_db, agent_id)
    assert agent is not None
    assert agent.id == agent_id
    assert isinstance(agent, Agent)

def test_should_delete_agent_given_valid_agent_id(test_db, add_agent_to_db):
    agent_id = add_agent_to_db()
    assert delete_agent(test_db, agent_id) is True
    agent = read_agent(test_db, agent_id)
    assert agent is None

def test_should_return_none_when_trying_to_delete_nonexistent_agent(test_db):
    assert delete_agent(test_db, 9999) is None

def test_should_return_none_when_trying_to_read_nonexistent_agent(test_db):
    assert read_agent(test_db, 9999) is None

def test_should_update_agent_config_given_valid_agent_id(test_db, add_agent_to_db):
    config_metadata = {"key": "value"}
    agent_id = add_agent_to_db()
    assert update_config(test_db, agent_id, config_metadata) is True
    agent = read_agent(test_db, agent_id)
    assert agent.config == config_metadata

def test_should_return_none_when_updating_config_for_nonexistent_agent(test_db):
    config_metadata = {"key": "value"}
    assert update_config(test_db, -1, config_metadata) is None
