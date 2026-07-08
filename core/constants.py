"""
Application constants and configuration defaults.

Centralizes all magic numbers, default values, and configuration
constants used throughout the Exam Automation application.
"""
import os
from core.path_resolver import get_app_dir

# Application metadata
APP_VERSION: str = '2.0.0'
APP_NAME: str = 'Exam Automation'
DB_NAME: str = 'exam_automation.db'

# Default exam session values
DEFAULT_COLLEGE_NAME: str = ''
DEFAULT_PROGRAM_NAME: str = ''
DEFAULT_EXAM_NAME: str = 'EXTERNAL'
DEFAULT_DIVISION: str = 'A'
DIVISIONS: list[str] = ['A', 'B', 'C', 'NA']

# Excel column detection keywords (lowercase matching)
ROLL_KEYWORDS: list[str] = ['roll', 'seatno', 'seat_no', 'seat', 'id', 'studentid', 'prn', 'enrollment', 'enrollmentno', 'regno', 'registration']
NAME_KEYWORDS: list[str] = ['name', 'fullname', 'studentname', 'student']
DATE_KEYWORDS: list[str] = ['date']
TIME_KEYWORDS: list[str] = ['time']
SUBJECT_CODE_KEYWORDS: list[str] = ['code', 'subject code', 'subjectcode', 'papercode']
SUBJECT_NAME_KEYWORDS: list[str] = ['subject name', 'subject', 'subjectname', 'paper', 'papername']

# PDF layout constants - Attendance sheets
ATTENDANCE_PAGE_SIZE: int = 40
ATTENDANCE_LEFT_SIDE_COUNT: int = 20

# PDF layout constants - Seating charts
SEATING_ROLLS_PER_ROW: int = 10

# PDF layout constants - Sticker dimensions (millimeters)
DEFAULT_STICKER_WIDTH_MM: float = 52.5
DEFAULT_STICKER_HEIGHT_MM: float = 24.75

# Sticker font sizes: label -> (font_size, cell_height)
STICKER_FONT_SIZES: dict[str, tuple[int, int]] = {
    'Small': (8, 18),
    'Medium': (10, 24),
    'Large': (12, 30),
}

# Roll number display formats
ROLL_FORMATS: list[str] = [
    'Only Roll Number',
    'Year+Roll',
    'Dept+Year+Roll vertically aligned',
]

# Academic year options
YEAR_OPTIONS: list[str] = ['FY', 'SY', 'TY', 'None']

# College header lines printed on PDF reports
COLLEGE_HEADER_LINES: list[str] = [
    '(PROFESSIONAL DEGREE COURSES)',
    'Approved by Govt. of Maharashtra, Affiliated to University of Mumbai',
    "NAAC Accredited Grade 'A' (1st cycle), & ISO 9001:2015 (Certified)",
    '(Institute Code No. 1019)',
]

# Reference number for printed documents
REF_NO: str = 'TSDC/IP/03/FRM/06'

# Logging configuration
LOG_DIR: str = os.path.join(get_app_dir(), 'logs')
LOG_FILE: str = 'app.log'
LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT: int = 5

# Database batch operations
BATCH_SIZE: int = 1000
