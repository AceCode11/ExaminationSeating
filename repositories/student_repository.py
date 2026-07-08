from typing import List
from core.models import Student, NORRecord, ExamSession
from core.database import DatabaseManager
from repositories.base_repository import BaseRepository
from core.constants import BATCH_SIZE

class StudentRepository(BaseRepository[Student]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, Student)

    def get_by_session(self, session_id: int) -> List[Student]:
        with self._db.session_scope() as session:
            students = session.query(Student).filter(Student.session_id == session_id).all()
            for s in students:
                session.expunge(s)
            return students

    def get_rolls_sorted(self, session_id: int) -> List[str]:
        with self._db.session_scope() as session:
            rolls = session.query(Student.roll_number).filter(Student.session_id == session_id).order_by(Student.roll_number).all()
            return [r[0] for r in rolls]

    def bulk_insert(self, students_data: List[dict], session_id: int) -> None:
        with self._db.session_scope() as session:
            for i in range(0, len(students_data), BATCH_SIZE):
                batch = students_data[i:i + BATCH_SIZE]
                students = [
                    Student(
                        roll_number=data['roll_number'],
                        student_name=data['student_name'],
                        session_id=session_id
                    ) for data in batch
                ]
                session.add_all(students)

    def get_students_by_rolls(self, roll_numbers: List[str], session_id: int) -> List[Student]:
        with self._db.session_scope() as session:
            students = session.query(Student).filter(
                Student.session_id == session_id,
                Student.roll_number.in_(roll_numbers)
            ).all()
            for s in students:
                session.expunge(s)
            return students

class NORRepository(BaseRepository[NORRecord]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, NORRecord)

    def get_by_session(self, session_id: int) -> List[str]:
        with self._db.session_scope() as session:
            records = session.query(NORRecord.roll_number).filter(NORRecord.session_id == session_id).all()
            return [r[0] for r in records]

    def bulk_insert(self, roll_numbers: List[str], session_id: int) -> None:
        with self._db.session_scope() as session:
            records = [NORRecord(roll_number=roll, session_id=session_id) for roll in roll_numbers]
            session.add_all(records)

class SessionRepository(BaseRepository[ExamSession]):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager, ExamSession)
        
    def get_latest_session(self) -> ExamSession:
        with self._db.session_scope() as session:
            exam_session = session.query(ExamSession).order_by(ExamSession.created_at.desc()).first()
            if exam_session:
                session.expunge(exam_session)
            return exam_session
