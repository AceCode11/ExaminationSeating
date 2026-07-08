from typing import TypeVar, Generic, Type, List, Optional
from core.database import DatabaseManager

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Generic base repository for CRUD operations."""
    
    def __init__(self, db_manager: DatabaseManager, model_class: Type[T]):
        self._db = db_manager
        self.model_class = model_class

    def add(self, entity: T) -> T:
        with self._db.session_scope() as session:
            session.add(entity)
            # Need to flush to get ID before expunging
            session.flush()
            session.expunge(entity)
            return entity

    def add_bulk(self, entities: List[T]) -> None:
        with self._db.session_scope() as session:
            session.add_all(entities)

    def get_by_id(self, entity_id: int) -> Optional[T]:
        with self._db.session_scope() as session:
            entity = session.query(self.model_class).get(entity_id)
            if entity:
                session.expunge(entity)
            return entity

    def get_all(self) -> List[T]:
        with self._db.session_scope() as session:
            entities = session.query(self.model_class).all()
            for entity in entities:
                session.expunge(entity)
            return entities

    def delete(self, entity_id: int) -> bool:
        with self._db.session_scope() as session:
            entity = session.query(self.model_class).get(entity_id)
            if entity:
                session.delete(entity)
                return True
            return False

    def delete_all(self) -> None:
        with self._db.session_scope() as session:
            session.query(self.model_class).delete()

    def count(self) -> int:
        with self._db.session_scope() as session:
            return session.query(self.model_class).count()
