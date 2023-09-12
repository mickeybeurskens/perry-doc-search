from perry.db.operations.agents import *
from perry.db.models import Agent

def test_create_agent(test_db):
    new_id = create_agent(test_db)
    conv = test_db.query(Agent).filter_by(id=new_id).first()
    assert isinstance(conv, Agent)

def test_read_agent(test_db):
    new_id = create_agent(test_db)
    conv = read_agent(test_db, new_id)
    assert conv is not None
    assert conv.id == new_id
    assert isinstance(conv, Agent)

def test_delete_agent(test_db):
    new_id = create_agent(test_db)
    assert delete_agent(test_db, new_id) is True
    conv = read_agent(test_db, new_id)
    assert conv is None

def test_delete_nonexistent_conversation(test_db):
    assert delete_agent(test_db, 9999) is None

def test_read_nonexistent_conversation(test_db):
    assert read_agent(test_db, 9999) is None
