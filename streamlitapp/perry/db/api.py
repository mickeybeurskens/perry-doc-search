from sqlalchemy.orm import Session
from perry.db.models import Agent, Conversation


def connect_agent_to_conversation(session: Session, agent_id: int, conversation_id: int):
    agent = session.query(Agent).filter_by(id=agent_id).first()
    conversation = session.query(Conversation).filter_by(id=conversation_id).first()

    if agent and conversation:
      agent.conversation_id = conversation_id
      session.commit()
      return True
    return False
