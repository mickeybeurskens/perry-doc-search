from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


class DatabaseSessionManager:
    _db_name = "perry"
    _engine = None
    _SessionLocal = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._engine = create_engine(f"sqlite:///./{cls._db_name}.db")
        return cls._engine

    @classmethod
    def get_session_local(cls):
        if cls._SessionLocal is None:
            cls._SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=cls.get_engine()
            )
        return cls._SessionLocal

    @classmethod
    def get_db_session(cls) -> Session:
        if cls._SessionLocal is None:
            cls.get_session_local()

        db = cls._SessionLocal()
        try:
            yield db
        finally:
            db.close()
