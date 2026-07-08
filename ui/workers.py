import traceback
from PyQt6.QtCore import QThread, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)

class WorkerBase(QThread):
    """Base class for background workers."""
    finished = pyqtSignal(object)  # Emits result on success
    error = pyqtSignal(str)        # Emits error message on failure
    progress = pyqtSignal(str)     # Emits progress messages

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Worker error: {e}\n{traceback.format_exc()}")
            self.error.emit(str(e))

class ExcelImportWorker(WorkerBase):
    """Specific worker for importing Excel files (Attendance/Timetable)."""
    pass

class AllocationWorker(WorkerBase):
    """Specific worker for running the seating allocation algorithm."""
    pass

class PDFGenerationWorker(WorkerBase):
    """Specific worker for generating PDFs."""
    pass
