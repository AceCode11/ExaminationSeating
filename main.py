import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox

# Setup logging first
from utils.logger import setup_logging, get_logger
setup_logging()
logger = get_logger("main")

from core.database import DatabaseManager
from core.settings import AppSettings
from core.models import ExamSession

# Repositories
from repositories.student_repository import StudentRepository, NORRepository, SessionRepository
from repositories.room_repository import RoomRepository
from repositories.timetable_repository import TimetableRepository
from repositories.allocation_repository import AllocationRepository

# Services
from services.attendance_service import AttendanceService
from services.seating_service import SeatingService
from services.timetable_service import TimetableService
from services.sticker_service import StickerService
from services.report_service import ReportService

# UI
from ui.main_window import MainWindow

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catch unhandled exceptions and log them."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    app = QApplication.instance()
    if app:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Critical Error")
        msg.setText(f"An unexpected error occurred:\n{exc_value}")
        msg.setDetailedText("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        msg.exec()

def main():
    sys.excepthook = global_exception_handler
    app = QApplication(sys.argv)
    
    # 1. Initialize Database
    try:
        db_manager = DatabaseManager()
        db_manager.create_tables()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        QMessageBox.critical(None, "Database Error", f"Failed to initialize database:\n{e}")
        return 1
        
    # 2. Get/Create Session
    session_repo = SessionRepository(db_manager)
    current_session = session_repo.get_latest_session()
    if not current_session:
        current_session = ExamSession()
        current_session = session_repo.add(current_session)
        logger.info(f"Created new ExamSession ID: {current_session.id}")
        
    session_id = current_session.id
    
    # 3. Initialize Settings
    settings = AppSettings(db_manager)
    
    # 4. Initialize Repositories
    student_repo = StudentRepository(db_manager)
    nor_repo = NORRepository(db_manager)
    room_repo = RoomRepository(db_manager)
    timetable_repo = TimetableRepository(db_manager)
    allocation_repo = AllocationRepository(db_manager)
    
    # 5. Initialize Services (Dependency Injection)
    attendance_service = AttendanceService(student_repo, nor_repo, session_repo, db_manager)
    seating_service = SeatingService(room_repo, student_repo, allocation_repo, db_manager)
    timetable_service = TimetableService(timetable_repo, db_manager)
    sticker_service = StickerService(student_repo, db_manager)
    report_service = ReportService(student_repo, nor_repo, timetable_repo, session_repo, db_manager)
    
    services = {
        'db': db_manager,
        'settings': settings,
        'session_repo': session_repo,
        'attendance': attendance_service,
        'seating': seating_service,
        'timetable': timetable_service,
        'sticker': sticker_service,
        'report': report_service
    }
    
    # 6. Launch Main Window
    window = MainWindow(services, session_id)
    window.show()
    
    logger.info("Application started successfully.")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())