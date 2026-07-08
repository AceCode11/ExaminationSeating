import os
import re

def ensure_directory(path: str) -> str:
    """Ensures a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def safe_filename(name: str) -> str:
    """Sanitizes a string to be used as a safe filename on Windows/Linux."""
    # Remove invalid characters
    clean_name = re.sub(r'[\\/*?:"<>|]', "", name)
    return clean_name.strip()

def get_attendance_filename(subject_code: str, date: str, room_no: str) -> str:
    date_clean = date.replace('-', '_')
    return f"Attendance_{safe_filename(subject_code)}_{date_clean}_Room{safe_filename(room_no)}.pdf"

def get_seating_filename(subject_code: str, date: str, room_no: str) -> str:
    date_clean = date.replace('-', '_')
    return f"Seating_{safe_filename(subject_code)}_{date_clean}_Room{safe_filename(room_no)}.pdf"

def get_sticker_filename(year: str, dept: str) -> str:
    return f"Stickers_{safe_filename(year)}_{safe_filename(dept)}.pdf"

def get_reports_filename(subject_code: str, date: str, room_no: str) -> str:
    date_clean = date.replace('-', '_')
    return f"Reports_{safe_filename(subject_code)}_{date_clean}_Room{safe_filename(room_no)}.pdf"
