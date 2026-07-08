from typing import List
from core.models import Room
from core.database import DatabaseManager
from repositories.base_repository import BaseRepository
from sqlalchemy.sql import func

class RoomRepository(BaseRepository[Room]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, Room)

    def get_sorted_rooms(self, session_id: int) -> List[Room]:
        with self._db.session_scope() as session:
            # Sort alphabetically/lexicographically by room number as original code does
            rooms = session.query(Room).filter(Room.session_id == session_id).order_by(Room.room_number).all()
            for r in rooms:
                session.expunge(r)
            return rooms

    def get_total_capacity(self, session_id: int) -> int:
        with self._db.session_scope() as session:
            total = session.query(func.sum(Room.capacity)).filter(Room.session_id == session_id).scalar()
            return total or 0

    def clear_rooms(self, session_id: int) -> None:
        with self._db.session_scope() as session:
            session.query(Room).filter(Room.session_id == session_id).delete()

    def room_exists(self, room_number: str, session_id: int) -> bool:
        with self._db.session_scope() as session:
            count = session.query(Room).filter(
                Room.room_number == room_number,
                Room.session_id == session_id
            ).count()
            return count > 0
