from dataclasses import dataclass
from typing import List
from core.database import DatabaseManager
from repositories.student_repository import StudentRepository
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class StickerConfig:
    rolls: List[str]
    prefix_text: str
    roll_format: str
    sticker_width_mm: float
    sticker_height_mm: float
    cols_per_row: int
    font_size_choice: str

class StickerService:
    def __init__(self, student_repo: StudentRepository, db_manager: DatabaseManager):
        self._student_repo = student_repo
        self._db = db_manager
    
    def prepare_sticker_data(self, session_id: int, dept: str, year: str,
                             roll_format: str, width_mm: float, height_mm: float,
                             cols_per_row: int, font_size_choice: str) -> StickerConfig:
        """Prepare all data needed for sticker PDF generation."""
        logger.info("Preparing sticker data.")
        
        rolls = self._student_repo.get_rolls_sorted(session_id)
        
        # Validation of prefix text happened in validation_service, so we just construct it
        prefix_parts = []
        if year and year != "None":
            prefix_parts.append(year)
        if dept and dept.strip():
            prefix_parts.append(dept.strip().upper())
            
        prefix_text = " ".join(prefix_parts)
        
        return StickerConfig(
            rolls=rolls,
            prefix_text=prefix_text,
            roll_format=roll_format,
            sticker_width_mm=width_mm,
            sticker_height_mm=height_mm,
            cols_per_row=cols_per_row,
            font_size_choice=font_size_choice
        )
