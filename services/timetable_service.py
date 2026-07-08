from dataclasses import dataclass
from typing import List
from core.database import DatabaseManager
from core.models import TimetableEntry
from repositories.timetable_repository import TimetableRepository
from utils.excel_reader import ExcelReader
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass 
class SubjectDetails:
    subject_code: str
    subject_name: str
    date: str
    time: str
    date_display: str

class TimetableService:
    def __init__(self, timetable_repo: TimetableRepository, db_manager: DatabaseManager):
        self._timetable_repo = timetable_repo
        self._db = db_manager
    
    def import_timetable(self, file_path: str, sheet_name: str, session_id: int) -> int:
        """Import timetable from Excel. Returns number of entries imported."""
        import pandas as pd
        logger.info(f"Importing timetable from {file_path} (sheet: {sheet_name})")
        entries_data = ExcelReader.read_timetable_data(file_path, sheet_name)
        
        with self._db.session_scope() as session:
            self._timetable_repo.clear_entries(session_id)
            
            entries = [
                TimetableEntry(
                    date=str(data['Date']),
                    time=str(data['Time']),
                    subject_code=str(data['SubjectCode']),
                    subject_name=str(data['SubjectName']),
                    session_id=session_id
                ) for data in entries_data
            ]
            session.add_all(entries)
            
        count = len(entries_data)
        logger.info(f"Imported {count} timetable entries.")
        return count
    
    def get_entries(self, session_id: int) -> List[dict]:
        entries = self._timetable_repo.get_by_session(session_id)
        return [
            {
                'Date': e.date,
                'Time': e.time,
                'SubjectCode': e.subject_code,
                'SubjectName': e.subject_name
            } for e in entries
        ]
    
    def get_subjects_list(self, session_id: int) -> List[str]:
        """Return list of 'CODE - NAME' strings for dropdown."""
        subjects = self._timetable_repo.get_subjects(session_id)
        return [f"{code} - {name}" for code, name in subjects]
    
    def get_subject_details(self, subject_code: str, session_id: int) -> SubjectDetails:
        """Get full details for a subject. Format date as DD-MM-YYYY."""
        entry = self._timetable_repo.get_entry_by_code(subject_code, session_id)
        if not entry:
            return None
            
        date_display = str(entry.date)
        try:
            import pandas as pd
            date_display = pd.to_datetime(entry.date).strftime('%d-%m-%Y')
        except Exception:
            pass
            
        return SubjectDetails(
            subject_code=entry.subject_code,
            subject_name=entry.subject_name,
            date=entry.date,
            time=entry.time,
            date_display=date_display
        )
