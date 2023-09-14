import pytest
from perry.db.models import Agent, Conversation
from perry.db.api import connect_agent_to_conversation
from perry.db.operations.conversations import create_conversation, read_conversation
from perry.db.operations.agents import create_agent


@pytest.mark.usefixtures("test_db")
class TestConnectAgentToConversation:
    def test_connect_when_both_exist(self, test_db):
        agent = Agent(id=1)
        conversation = Conversation(id=1)
        test_db.add(agent)
        test_db.add(conversation)
        test_db.commit()

        assert connect_agent_to_conversation(test_db, 1, 1)

        updated_agent = test_db.query(Agent).filter_by(id=1).first()
        assert updated_agent.conversation_id == 1

    def test_connect_when_agent_not_found(self, test_db):
        create_conversation(test_db)

        assert not connect_agent_to_conversation(test_db, 9999, 1)

    def test_connect_when_conversation_not_found(self, test_db):
        create_agent(test_db)

        assert not connect_agent_to_conversation(test_db, 1, 9999)

    def test_connect_when_both_not_found(self, test_db):
        assert not connect_agent_to_conversation(test_db, 9999, 9999)
