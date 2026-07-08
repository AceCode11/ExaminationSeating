from typing import Tuple
from core.exceptions import ValidationError
from utils.validators import validate_positive_integer

class ValidationService:
    @staticmethod
    def validate_room_input(room_no: str, capacity_text: str) -> Tuple[str, int]:
        room_no = room_no.strip()
        if not room_no:
            raise ValidationError('Room number cannot be empty.')
        
        try:
            capacity = validate_positive_integer(capacity_text, 'Room capacity')
        except ValidationError as e:
            raise e
            
        return room_no, capacity
    
    @staticmethod
    def validate_subject_selection(subject_text: str) -> Tuple[str, str]:
        if not subject_text:
            raise ValidationError('Please select a subject.')
        parts = subject_text.split(' - ', 1)
        if len(parts) != 2:
            raise ValidationError('Invalid subject format.')
        return parts[0].strip(), parts[1].strip()
    
    @staticmethod
    def validate_sticker_config(width_text: str, height_text: str, cols_text: str, 
                                dept: str, year: str, roll_format: str) -> Tuple[float, float, int, str]:
        try:
            width = float(width_text)
            height = float(height_text)
            cols = int(cols_text)
            if width <= 0 or height <= 0 or cols <= 0:
                raise ValueError()
        except ValueError:
            raise ValidationError("Dimensions and column count must be positive numbers.")
            
        prefix_parts = []
        if year and year != "None":
            prefix_parts.append(year)
        if dept and dept.strip():
            prefix_parts.append(dept.strip().upper())
            
        prefix_text = " ".join(prefix_parts)
        
        if roll_format != 'Only Roll Number' and not prefix_text:
            raise ValidationError("Please enter Department and/or select Year for the chosen Roll Format.")
            
        return width, height, cols, prefix_text
    
    @staticmethod
    def validate_allocation_readiness(has_rooms: bool, has_students: bool) -> None:
        if not has_rooms:
            raise ValidationError('Please add rooms and capacities first.')
        if not has_students:
            raise ValidationError('No valid student data found. Upload attendance list first.')
