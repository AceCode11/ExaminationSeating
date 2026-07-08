from typing import List, Tuple, Optional
from core.models import TimetableEntry
from core.database import DatabaseManager
from repositories.base_repository import BaseRepository

class TimetableRepository(BaseRepository[TimetableEntry]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, TimetableEntry)

    def get_by_session(self, session_id: int) -> List[TimetableEntry]:
        with self._db.session_scope() as session:
            entries = session.query(TimetableEntry).filter(TimetableEntry.session_id == session_id).all()
            for e in entries:
                session.expunge(e)
            return entries

    def get_subjects(self, session_id: int) -> List[Tuple[str, str]]:
        with self._db.session_scope() as session:
            subjects = session.query(TimetableEntry.subject_code, TimetableEntry.subject_name)\
                              .filter(TimetableEntry.session_id == session_id).all()
            return [(s[0], s[1]) for s in subjects]

    def get_entry_by_code(self, subject_code: str, session_id: int) -> Optional[TimetableEntry]:
        with self._db.session_scope() as session:
            entry = session.query(TimetableEntry).filter(
                TimetableEntry.subject_code == subject_code,
                TimetableEntry.session_id == session_id
            ).first()
            if entry:
                session.expunge(entry)
            return entry

    def clear_entries(self, session_id: int) -> None:
        with self._db.session_scope() as session:
            session.query(TimetableEntry).filter(TimetableEntry.session_id == session_id).delete()
