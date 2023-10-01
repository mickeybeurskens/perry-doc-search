from perry.db.session import DatabaseSessionManager


def get_db():
    db = DatabaseSessionManager.get_db_session()
    try:
        yield db
    finally:
        db.close()
