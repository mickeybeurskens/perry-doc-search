from sqlalchemy import create_engine
from perry.db.models import Base


def init_db():
    engine = create_engine("sqlite:.//./perry.db")
    Base.metadata.create_all(bind=engine)
