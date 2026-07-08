from dataclasses import dataclass
from typing import Dict, List
from core.database import DatabaseManager
from core.models import Room
from repositories.room_repository import RoomRepository
from repositories.student_repository import StudentRepository
from repositories.allocation_repository import AllocationRepository
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AllocationResult:
    total_students: int
    allocated_count: int
    unallocated_count: int
    room_allocations: Dict[str, int]  # room_no -> count

class SeatingService:
    def __init__(self, room_repo: RoomRepository, student_repo: StudentRepository, 
                 allocation_repo: AllocationRepository, db_manager: DatabaseManager):
        self._room_repo = room_repo
        self._student_repo = student_repo
        self._allocation_repo = allocation_repo
        self._db = db_manager
    
    def add_room(self, room_number: str, capacity: int, session_id: int) -> None:
        if self._room_repo.room_exists(room_number, session_id):
            # Update capacity if exists
            with self._db.session_scope() as session:
                room = session.query(Room).filter_by(room_number=room_number, session_id=session_id).first()
                room.capacity = capacity
        else:
            self._room_repo.add(Room(room_number=room_number, capacity=capacity, session_id=session_id))
    
    def get_rooms(self, session_id: int) -> List[dict]:
        rooms = self._room_repo.get_sorted_rooms(session_id)
        return [{'room_number': r.room_number, 'capacity': r.capacity} for r in rooms]
    
    def clear_rooms(self, session_id: int) -> None:
        self._allocation_repo.clear_allocations(session_id)
        self._room_repo.clear_rooms(session_id)
    
    def allocate_students(self, session_id: int) -> AllocationResult:
        """Sequential greedy allocation: sort rooms by number, fill each to capacity."""
        logger.info(f"Starting seating allocation for session {session_id}")
        
        # 1. Clear existing allocations
        self._allocation_repo.clear_allocations(session_id)
        
        # 2. Get students and rooms
        students = self._student_repo.get_by_session(session_id)
        sorted_students = sorted(students, key=lambda s: s.roll_number)
        sorted_rooms = self._room_repo.get_sorted_rooms(session_id)
        
        remaining_students = sorted_students[:]
        allocated_count = 0
        room_allocations = {}
        allocations_to_insert = []
        
        # 3. Allocate sequentially
        for room in sorted_rooms:
            if not remaining_students:
                break
                
            to_allocate_count = min(room.capacity, len(remaining_students))
            allocated_to_room = remaining_students[:to_allocate_count]
            remaining_students = remaining_students[to_allocate_count:]
            
            room_allocations[room.room_number] = len(allocated_to_room)
            allocated_count += len(allocated_to_room)
            
            for student in allocated_to_room:
                allocations_to_insert.append({
                    'room_id': room.id,
                    'student_id': student.id
                })
                
        # 4. Insert records
        if allocations_to_insert:
            self._allocation_repo.bulk_allocate(allocations_to_insert)
            
        unallocated_count = len(remaining_students)
        logger.info(f"Allocation complete: {allocated_count} allocated, {unallocated_count} unallocated.")
        
        return AllocationResult(
            total_students=len(sorted_students),
            allocated_count=allocated_count,
            unallocated_count=unallocated_count,
            room_allocations=room_allocations
        )
    
    def get_allocation_summary(self, session_id: int) -> List[dict]:
        """Return [{room_number, student_count, sample_rolls: list[str]}]"""
        grouped = self._allocation_repo.get_all_allocations_grouped(session_id)
        summary = []
        for room_no, rolls in grouped.items():
            summary.append({
                'room_number': room_no,
                'student_count': len(rolls),
                'sample_rolls': rolls[:10]  # first 10
            })
        return summary
    
    def get_allocated_rooms(self, session_id: int) -> List[str]:
        return self._allocation_repo.get_allocated_room_numbers(session_id)
    
    def get_allocated_rolls_for_room(self, room_number: str, session_id: int) -> List[str]:
        students = self._allocation_repo.get_students_for_room(room_number, session_id)
        return [s.roll_number for s in students]
