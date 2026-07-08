import os
from typing import Tuple
from core.exceptions import ValidationError

def validate_positive_integer(value: str, field_name: str) -> int:
    """Validates that a string is a positive integer."""
    value = value.strip()
    if not value:
        raise ValidationError(f"{field_name} cannot be empty.")
    if not value.isdigit() or int(value) <= 0:
        raise ValidationError(f"{field_name} must be a positive integer.")
    return int(value)

def validate_file_path(path: str, allowed_extensions: list[str]) -> str:
    """Validates that a file path exists and has an allowed extension."""
    if not path or not os.path.exists(path):
        raise ValidationError("File path does not exist.")
    
    ext = os.path.splitext(path)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Invalid file extension. Expected one of: {', '.join(allowed_extensions)}")
    return path

def validate_sticker_dimensions(width: str, height: str, cols: str) -> Tuple[float, float, int]:
    """Validates sticker dimension inputs."""
    try:
        w = float(width)
        h = float(height)
        c = int(cols)
        if w <= 0 or h <= 0 or c <= 0:
            raise ValueError()
        return w, h, c
    except ValueError:
        raise ValidationError("Sticker dimensions must be positive numbers and columns must be a positive integer.")

def validate_room_input(room_no: str, capacity: str) -> Tuple[str, int]:
    """Validates room number and capacity inputs."""
    room_no = room_no.strip()
    if not room_no:
        raise ValidationError("Room number cannot be empty.")
    
    cap = validate_positive_integer(capacity, "Room capacity")
    return room_no, cap
