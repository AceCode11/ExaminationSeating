from typing import List, Dict
from core.models import Allocation, Student, Room
from core.database import DatabaseManager
from repositories.base_repository import BaseRepository
from sqlalchemy.orm import joinedload

class AllocationRepository(BaseRepository[Allocation]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, Allocation)

    def get_allocations_by_room(self, room_id: int) -> List[Allocation]:
        with self._db.session_scope() as session:
            allocations = session.query(Allocation).options(joinedload(Allocation.student))\
                                 .filter(Allocation.room_id == room_id).all()
            for a in allocations:
                session.expunge(a)
                session.expunge(a.student)
            return allocations

    def get_all_allocations_grouped(self, session_id: int) -> Dict[str, List[str]]:
        with self._db.session_scope() as session:
            allocations = session.query(Allocation, Room.room_number, Student.roll_number)\
                                 .join(Room, Allocation.room_id == Room.id)\
                                 .join(Student, Allocation.student_id == Student.id)\
                                 .filter(Room.session_id == session_id)\
                                 .order_by(Room.room_number, Student.roll_number).all()
            
            grouped = {}
            for _, room_number, roll_number in allocations:
                if room_number not in grouped:
                    grouped[room_number] = []
                grouped[room_number].append(roll_number)
            return grouped

    def get_students_for_room(self, room_number: str, session_id: int) -> List[Student]:
        with self._db.session_scope() as session:
            students = session.query(Student)\
                              .join(Allocation, Allocation.student_id == Student.id)\
                              .join(Room, Allocation.room_id == Room.id)\
                              .filter(Room.room_number == room_number, Room.session_id == session_id)\
                              .order_by(Student.roll_number).all()
            for s in students:
                session.expunge(s)
            return students

    def clear_allocations(self, session_id: int) -> None:
        with self._db.session_scope() as session:
            # Delete all allocations where room_id belongs to the session_id
            room_ids_query = session.query(Room.id).filter(Room.session_id == session_id)
            session.query(Allocation).filter(Allocation.room_id.in_(room_ids_query)).delete(synchronize_session=False)

    def bulk_allocate(self, allocations_data: List[dict]) -> None:
        with self._db.session_scope() as session:
            allocations = [
                Allocation(room_id=data['room_id'], student_id=data['student_id'])
                for data in allocations_data
            ]
            session.add_all(allocations)

    def get_allocated_room_numbers(self, session_id: int) -> List[str]:
        with self._db.session_scope() as session:
            room_numbers = session.query(Room.room_number)\
                                  .join(Allocation, Allocation.room_id == Room.id)\
                                  .filter(Room.session_id == session_id)\
                                  .distinct().order_by(Room.room_number).all()
            return [r[0] for r in room_numbers]
