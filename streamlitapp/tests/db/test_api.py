import pytest
from perry.db.models import Agent, Conversation
from perry.db.api import connect_agent_to_conversation


@pytest.mark.usefixtures("test_db")
class TestConnectAgentToConversation:

    def test_connect_when_both_exist(self, test_db):
        # Setup: Create Agent and Conversation in test_db
        agent = Agent(id=1)
        conversation = Conversation(id=1)
        test_db.add(agent)
        test_db.add(conversation)
        test_db.commit()
        
        # Execute: Connect the agent to the conversation
        assert connect_agent_to_conversation(test_db, 1, 1)
        
        # Verify: Check if agent's conversation_id was updated
        updated_agent = test_db.query(Agent).filter_by(id=1).first()
        assert updated_agent.conversation_id == 1

    def test_connect_when_agent_not_found(self, test_db):
        # Setup: Create only Conversation in test_db
        conversation = Conversation(id=1)
        test_db.add(conversation)
        test_db.commit()

        # Execute and Verify
        assert not connect_agent_to_conversation(test_db, 1, 1)

    def test_connect_when_conversation_not_found(self, test_db):
        # Setup: Create only Agent in test_db
        agent = Agent(id=1)
        test_db.add(agent)
        test_db.commit()

        # Execute and Verify
        assert not connect_agent_to_conversation(test_db, 1, 1)

    def test_connect_when_both_not_found(self, test_db):
        # No setup required as both Agent and Conversation are not found
        
        # Execute and Verify
        assert not connect_agent_to_conversation(test_db, 1, 1)
