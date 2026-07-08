import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtGui import QIcon, QFont
from core.constants import APP_NAME, APP_VERSION, DEFAULT_COLLEGE_NAME, DEFAULT_PROGRAM_NAME, DEFAULT_EXAM_NAME, DEFAULT_DIVISION
from core.path_resolver import get_resource_path
from ui.student_tab import StudentTab
from ui.timetable_tab import TimetableTab
from ui.classroom_tab import ClassroomTab
from ui.sticker_tab import StickerTab
from ui.reports_tab import ReportsTab
from ui.styles import AppStyles
from ui.manual_tab import ManualTab

class MainWindow(QMainWindow):
    def __init__(self, services: dict, session_id: int):
        super().__init__()
        self.services = services
        self.session_id = session_id
        self.settings = services['settings']
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(AppStyles.MAIN_STYLE)
        
        # Set application icon
        icon_path = get_resource_path('logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header for Global Settings
        settings_group = QGroupBox("Global Exam Details")
        settings_layout = QHBoxLayout()
        
        self.txt_college = QLineEdit()
        self.txt_college.setPlaceholderText("College Name")
        self.txt_program = QLineEdit()
        self.txt_program.setPlaceholderText("Program Name")
        self.txt_exam = QLineEdit()
        self.txt_exam.setPlaceholderText("Exam Name")
        self.txt_div = QLineEdit()
        self.txt_div.setPlaceholderText("Division")
        
        btn_save_settings = QPushButton("Save Settings")
        btn_save_settings.clicked.connect(self._save_settings)
        
        btn_reset_settings = QPushButton("Reset Settings")
        btn_reset_settings.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; } QPushButton:hover { background-color: #c0392b; }")
        btn_reset_settings.clicked.connect(self._reset_settings)
        
        settings_layout.addWidget(QLabel("College:"))
        settings_layout.addWidget(self.txt_college)
        settings_layout.addWidget(QLabel("Program:"))
        settings_layout.addWidget(self.txt_program)
        settings_layout.addWidget(QLabel("Exam:"))
        settings_layout.addWidget(self.txt_exam)
        settings_layout.addWidget(QLabel("Div:"))
        settings_layout.addWidget(self.txt_div)
        settings_layout.addWidget(btn_save_settings)
        settings_layout.addWidget(btn_reset_settings)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Initialize Tabs
        self.tab_student = StudentTab(self.services['attendance'], self.session_id)
        self.tab_timetable = TimetableTab(self.services['timetable'], self.session_id)
        self.tab_classroom = ClassroomTab(self.services['seating'], self.services['attendance'], self.session_id)
        self.tab_sticker = StickerTab(self.services['sticker'], self.session_id)
        self.tab_reports = ReportsTab(
            self.services['seating'], self.services['attendance'], 
            self.services['timetable'], self.services['report'],
            self.settings, self.session_id
        )
        
        self.tabs.addTab(self.tab_student, "1. Student Attendance")
        self.tabs.addTab(self.tab_timetable, "2. Timetable")
        self.tabs.addTab(self.tab_classroom, "3. Classroom Allocation")
        self.tabs.addTab(self.tab_sticker, "4. Stickers")
        self.tabs.addTab(self.tab_reports, "5. Reports")
        
        self.tab_manual = ManualTab()
        self.tabs.addTab(self.tab_manual, "6. User Manual")

    def _load_settings(self):
        self.txt_college.setText(self.settings.get('college_name'))
        self.txt_program.setText(self.settings.get('program_name'))
        self.txt_exam.setText(self.settings.get('exam_name'))
        self.txt_div.setText(self.settings.get('division'))

    def _save_settings(self):
        self.settings.set('college_name', self.txt_college.text())
        self.settings.set('program_name', self.txt_program.text())
        self.settings.set('exam_name', self.txt_exam.text())
        self.settings.set('division', self.txt_div.text())
        QMessageBox.information(self, "Success", "Global settings saved successfully.")
        
        # Update current session
        session_repo = self.services['session_repo']
        with self.services['db'].session_scope() as sess:
            db_session = sess.query(session_repo.model_class).get(self.session_id)
            if db_session:
                db_session.college_name = self.txt_college.text()
                db_session.program_name = self.txt_program.text()
                db_session.exam_name = self.txt_exam.text()
                db_session.division = self.txt_div.text()

    def _reset_settings(self):
        """Reset all settings to their default values."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.txt_college.setText(DEFAULT_COLLEGE_NAME)
            self.txt_program.setText(DEFAULT_PROGRAM_NAME)
            self.txt_exam.setText(DEFAULT_EXAM_NAME)
            self.txt_div.setText(DEFAULT_DIVISION)
            self._save_settings()
            QMessageBox.information(self, "Reset", "Settings have been reset to defaults.")
