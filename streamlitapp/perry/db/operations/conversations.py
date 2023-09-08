from sqlalchemy.orm import Session
from perry.db.models import Conversation


def create_conversation(session: Session, user_id):
    new_conversation = Conversation(user_id=user_id)
    session.add(new_conversation)
    session.commit()
    return new_conversation.id

def read_conversation(session: Session, conversation_id):
    return session.query(Conversation).filter_by(id=conversation_id).first()

def update_conversation(session: Session, conversation_id, user_id=None):
    conversation = session.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        return None
    if user_id:
        conversation.user_id = user_id
    session.commit()
    return conversation

def delete_conversation(session: Session, conversation_id):
    conversation = session.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        return None
    session.delete(conversation)
    session.commit()
    return True
