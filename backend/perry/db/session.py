import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from perry.db.models import Base


class DatabaseSessionManager:
    _db_name = "perry"
    _engine = None
    _SessionLocal = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            current_file_path = Path(__file__).resolve()
            target_directory = current_file_path.parents[1]

            if not target_directory.exists():
                raise FileNotFoundError(f"The directory {target_directory} does not exist.")
            if not os.access(target_directory, os.W_OK):
                raise PermissionError(f"No write permission for directory {target_directory}")

            db_path = target_directory / f"{cls._db_name}.db"
            cls._engine = create_engine(f"sqlite:///{db_path}")
            
            Base.metadata.create_all(bind=cls._engine)
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

        return cls._SessionLocal()
