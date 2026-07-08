import os
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from core.models import Base
from core.constants import DB_NAME
from core.exceptions import DatabaseError
from core.path_resolver import get_app_dir

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Place the DB next to the executable (or main.py when running from source)
            db_path = os.path.join(get_app_dir(), DB_NAME)
        
        self.db_url = f"sqlite:///{db_path}"
        
        # SQLite needs connect_args={'check_same_thread': False} if used across threads
        # We also enable WAL mode for better concurrency
        self.engine = create_engine(
            self.db_url,
            connect_args={'check_same_thread': False},
            pool_size=5,
            max_overflow=10
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Enable WAL mode in SQLite for better performance
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))

    def create_tables(self):
        """Creates all tables defined in models.py."""
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            raise DatabaseError(f"Failed to create database tables: {e}")

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Database error occurred: {e}")
        finally:
            session.close()
