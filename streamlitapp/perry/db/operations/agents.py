from sqlalchemy.orm import Session
from perry.db.models import Agent


def create_agent(session: Session):
    new_agent = Agent()
    session.add(new_agent)
    session.commit()
    return new_agent.id

def read_agent(session: Session, agent_id):
    return session.query(Agent).filter_by(id=agent_id).first()

def delete_agent(session: Session, agent_id):
    agent = session.query(Agent).filter_by(id=agent_id).first()
    if not agent:
        return None
    session.delete(agent)
    session.commit()
    return True