import re
import pandas as pd
from typing import Optional, List, Tuple
from core.constants import (
    ROLL_KEYWORDS, NAME_KEYWORDS, DATE_KEYWORDS, TIME_KEYWORDS, 
    SUBJECT_CODE_KEYWORDS, SUBJECT_NAME_KEYWORDS
)
from core.exceptions import ExcelImportError

class SmartColumnDetector:
    """Detects column names in Excel using keyword matching."""
    
    @staticmethod
    def detect(df: pd.DataFrame, keywords_map: dict) -> Optional[dict]:
        actual_cols = {}
        standardized_cols = {
            re.sub(r'\W+', '', str(col).lower()): col
            for col in df.columns
        }
        
        for required_key, keywords in keywords_map.items():
            found_col = None
            for keyword in keywords:
                clean_keyword = re.sub(r'\W+', '', keyword.lower())
                for standardized_name, original_name in standardized_cols.items():
                    if clean_keyword and clean_keyword in standardized_name:
                        found_col = original_name
                        break
                if found_col:
                    break
                    
            if found_col is None:
                if required_key in ['RollNumber', 'SubjectCode', 'Date', 'Time', 'SubjectName']:
                    return None  # Critical column missing
                if required_key == 'StudentName':
                    continue  # Optional/Special handling
            actual_cols[required_key] = found_col
            
        return actual_cols

class ExcelReader:
    """Reads and processes Excel files for the application."""
    
    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        try:
            xls = pd.ExcelFile(file_path)
            names = xls.sheet_names
            xls.close()
            return names
        except Exception as e:
            raise ExcelImportError(f"Failed to read Excel file '{file_path}': {e}")
            
    @staticmethod
    def _extract_roll(raw_value: any) -> str:
        matches = re.findall(r'[\w]+', str(raw_value).strip())
        if matches:
            return matches[-1].upper()
        return str(raw_value).strip().upper()

    @staticmethod
    def read_attendance_data(file_path: str, sheet_name: str = None) -> Tuple[List[dict], List[str]]:
        """Returns (valid_students_list, nor_rolls_list)"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name) if sheet_name else pd.read_excel(file_path)
        except Exception as e:
            raise ExcelImportError(f"Failed to read sheet '{sheet_name}': {e}")
            
        keywords_map = {
            'RollNumber': ROLL_KEYWORDS,
            'StudentName': NAME_KEYWORDS
        }
        
        cols = SmartColumnDetector.detect(df, keywords_map)
        if cols is None or 'RollNumber' not in cols:
            raise ExcelImportError("Could not find a column containing 'roll', 'seatno', or 'seat_no'.")
            
        # Clean roll numbers
        df['RollNumber_Raw'] = df[cols['RollNumber']].astype(str)
        df['RollNumber'] = df['RollNumber_Raw'].apply(ExcelReader._extract_roll)
        
        if 'StudentName' in cols and cols['StudentName'] in df.columns:
            df['StudentName'] = df[cols['StudentName']].astype(str)
        else:
            df['StudentName'] = pd.NA
            
        df['StudentName'] = df['StudentName'].replace({'None': pd.NA, 'nan': pd.NA, '': pd.NA})
        
        # NOR students
        nor_df = df[df['StudentName'].isna()]
        nor_rolls = nor_df['RollNumber'].astype(str).tolist()
        
        # Valid students
        valid_df = df[df['StudentName'].notna()].copy()
        if not valid_df.empty:
            valid_df['RollNumber'] = valid_df['RollNumber'].astype(str).str.strip()
            valid_df['StudentName'] = valid_df['StudentName'].astype(str).str.strip()
            
        if valid_df.empty and not nor_rolls:
            raise ExcelImportError("All records were removed or invalid (no roll/name found).")
            
        valid_df = valid_df.rename(columns={'RollNumber': 'roll_number', 'StudentName': 'student_name'})
        valid_students = valid_df[['roll_number', 'student_name']].to_dict(orient='records')
        
        return valid_students, nor_rolls

    @staticmethod  
    def read_timetable_data(file_path: str, sheet_name: str = None) -> List[dict]:
        """Returns list of timetable entries."""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name) if sheet_name else pd.read_excel(file_path)
        except Exception as e:
            raise ExcelImportError(f"Failed to read sheet '{sheet_name}': {e}")
            
        keywords_map = {
            'Date': DATE_KEYWORDS,
            'Time': TIME_KEYWORDS,
            'SubjectCode': SUBJECT_CODE_KEYWORDS,
            'SubjectName': SUBJECT_NAME_KEYWORDS
        }
        
        cols = SmartColumnDetector.detect(df, keywords_map)
        if cols is None or any(k not in cols for k in ['Date', 'Time', 'SubjectCode', 'SubjectName']):
            raise ExcelImportError("Could not find required columns (Date, Time, SubjectCode, SubjectName) in the Timetable sheet.")
            
        df_clean = df[[cols['Date'], cols['Time'], cols['SubjectCode'], cols['SubjectName']]].copy()
        df_clean.columns = ['Date', 'Time', 'SubjectCode', 'SubjectName']
        
        return df_clean.to_dict(orient='records')
