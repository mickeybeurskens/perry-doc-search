from perry.db.operations.agents import *
from perry.db.models import Agent

def test_create_agent(test_db):
    agent_id = create_agent(test_db)
    conv = test_db.query(Agent).filter_by(id=agent_id).first()
    assert isinstance(conv, Agent)

def test_read_agent(test_db, add_agent_to_db):
    conv = read_agent(test_db, add_agent_to_db)
    assert conv is not None
    assert conv.id == add_agent_to_db
    assert isinstance(conv, Agent)

def test_delete_agent(test_db, add_agent_to_db):
    assert delete_agent(test_db, add_agent_to_db) is True
    conv = read_agent(test_db, add_agent_to_db)
    assert conv is None

def test_delete_nonexistent_conversation(test_db):
    assert delete_agent(test_db, 9999) is None

def test_read_nonexistent_conversation(test_db):
    assert read_agent(test_db, 9999) is None
