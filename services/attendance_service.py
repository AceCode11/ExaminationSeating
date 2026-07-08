from dataclasses import dataclass
from core.database import DatabaseManager
from repositories.student_repository import StudentRepository, NORRepository
from repositories.base_repository import BaseRepository
from core.models import ExamSession
from utils.excel_reader import ExcelReader
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ImportResult:
    valid_count: int
    nor_count: int
    total_processed: int
    session_id: int

class AttendanceService:
    def __init__(self, student_repo: StudentRepository, nor_repo: NORRepository, session_repo: BaseRepository, db_manager: DatabaseManager):
        self._student_repo = student_repo
        self._nor_repo = nor_repo  
        self._session_repo = session_repo
        self._db = db_manager
    
    def import_from_excel(self, file_path: str, sheet_name: str, session_id: int) -> ImportResult:
        """Import attendance data from Excel into database."""
        logger.info(f"Importing attendance from {file_path} (sheet: {sheet_name})")
        
        valid_students, nor_rolls = ExcelReader.read_attendance_data(file_path, sheet_name)
        
        with self._db.session_scope() as session:
            # Delete old data for this session to replace
            session.execute(self._student_repo.model_class.__table__.delete().where(self._student_repo.model_class.session_id == session_id))
            session.execute(self._nor_repo.model_class.__table__.delete().where(self._nor_repo.model_class.session_id == session_id))
        
        # Bulk inserts
        if valid_students:
            self._student_repo.bulk_insert(valid_students, session_id)
        if nor_rolls:
            self._nor_repo.bulk_insert(nor_rolls, session_id)
            
        logger.info(f"Import complete: {len(valid_students)} valid, {len(nor_rolls)} NOR.")
        return ImportResult(
            valid_count=len(valid_students),
            nor_count=len(nor_rolls),
            total_processed=len(valid_students) + len(nor_rolls),
            session_id=session_id
        )
    
    def get_students_for_room(self, room_number: str, session_id: int) -> list[dict]:
        """Get students allocated to a room."""
        # For attendance PDF, we just need roll_number and student_name
        # The allocation_repo gets this, but since attendance service handles this task
        # we can fetch students directly if needed, or rely on the caller to provide rolls.
        # Actually, best to fetch via student repo given roll numbers
        pass
        
    def get_nor_rolls(self, session_id: int) -> list[str]:
        return self._nor_repo.get_by_session(session_id)
    
    def get_student_count(self, session_id: int) -> int:
        with self._db.session_scope() as session:
            return session.query(self._student_repo.model_class).filter_by(session_id=session_id).count()
    
    def get_all_students_sorted(self, session_id: int) -> list[dict]:
        """Return all students sorted by roll number as list of dicts."""
        students = self._student_repo.get_by_session(session_id)
        sorted_students = sorted(students, key=lambda s: s.roll_number)
        return [{'roll_number': s.roll_number, 'student_name': s.student_name} for s in sorted_students]
