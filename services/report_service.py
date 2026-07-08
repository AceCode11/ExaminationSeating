from dataclasses import dataclass
from typing import List
from core.database import DatabaseManager
from repositories.student_repository import StudentRepository, NORRepository
from repositories.timetable_repository import TimetableRepository
from repositories.base_repository import BaseRepository
from core.models import ExamSession

@dataclass
class ReportData:
    college_name: str
    program_name: str
    exam_name: str
    division: str
    subject_code: str
    subject_name: str
    date: str
    time: str
    block_number: str
    room_number: str
    students: List[dict]
    nor_rolls: List[str]

class ReportService:
    def __init__(self, student_repo: StudentRepository, nor_repo: NORRepository, 
                 timetable_repo: TimetableRepository, session_repo: BaseRepository, 
                 db_manager: DatabaseManager):
        self._student_repo = student_repo
        self._nor_repo = nor_repo
        self._timetable_repo = timetable_repo
        self._session_repo = session_repo
        self._db = db_manager
    
    def prepare_report_data(self, session_id: int, subject_code: str,
                           block_no: str, room_no: str) -> ReportData:
        """Gather all data needed for reports PDF generation."""
        
        # Get metadata
        session = self._session_repo.get_by_id(session_id)
        
        # Get timetable entry
        entry = self._timetable_repo.get_entry_by_code(subject_code, session_id)
        date_display = str(entry.date)
        try:
            import pandas as pd
            date_display = pd.to_datetime(entry.date).strftime('%d-%m-%Y')
        except Exception:
            pass
            
        # Get students
        students = self._student_repo.get_by_session(session_id)
        sorted_students = sorted(students, key=lambda s: s.roll_number)
        student_dicts = [{'roll_number': s.roll_number, 'student_name': s.student_name} for s in sorted_students]
        
        # Get NORs
        nor_rolls = self._nor_repo.get_by_session(session_id)
        
        return ReportData(
            college_name=session.college_name,
            program_name=session.program_name,
            exam_name=session.exam_name,
            division=session.division,
            subject_code=entry.subject_code,
            subject_name=entry.subject_name,
            date=date_display,
            time=entry.time,
            block_number=block_no,
            room_number=room_no,
            students=student_dicts,
            nor_rolls=nor_rolls
        )
