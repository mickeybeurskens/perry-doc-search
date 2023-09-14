from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./perry.db")
db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
