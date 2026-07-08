from core.models import AppSetting
from core.constants import (
    DEFAULT_COLLEGE_NAME,
    DEFAULT_PROGRAM_NAME,
    DEFAULT_EXAM_NAME,
    DEFAULT_DIVISION
)

class AppSettings:
    """Manages application settings stored in the database."""
    
    def __init__(self, db_manager):
        self._db = db_manager
        self._cache = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Populate database with default settings if they don't exist."""
        defaults = {
            'college_name': DEFAULT_COLLEGE_NAME,
            'program_name': DEFAULT_PROGRAM_NAME,
            'exam_name': DEFAULT_EXAM_NAME,
            'division': DEFAULT_DIVISION
        }
        
        with self._db.session_scope() as session:
            for key, default_value in defaults.items():
                setting = session.query(AppSetting).filter_by(key=key).first()
                if not setting:
                    setting = AppSetting(key=key, value=default_value)
                    session.add(setting)
                self._cache[key] = setting.value

    def get(self, key: str, default: str = None) -> str:
        """Get a setting value, falling back to default."""
        if key in self._cache:
            return self._cache[key]
            
        with self._db.session_scope() as session:
            setting = session.query(AppSetting).filter_by(key=key).first()
            if setting:
                self._cache[key] = setting.value
                return setting.value
        return default

    def set(self, key: str, value: str):
        """Set a setting value."""
        with self._db.session_scope() as session:
            setting = session.query(AppSetting).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = AppSetting(key=key, value=value)
                session.add(setting)
            self._cache[key] = value
