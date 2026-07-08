import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.workers import ExcelImportWorker

class StudentTab(QWidget):
    def __init__(self, attendance_service, current_session_id):
        super().__init__()
        self.attendance_service = attendance_service
        self.current_session_id = current_session_id
        self.worker = None
        self._data_loaded = False
        self._setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._data_loaded:
            self._data_loaded = True
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Top Bar
        top_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import Attendance Excel")
        self.btn_import.clicked.connect(self._import_excel)
        self.lbl_status = QLabel("Status: Ready")
        top_layout.addWidget(self.btn_import)
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Roll Number", "Student Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Summary
        self.lbl_summary = QLabel("Total Students: 0 | NOR Students: 0")
        layout.addWidget(self.lbl_summary)

    def _import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Attendance Excel", "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return

        self.btn_import.setEnabled(False)
        self.lbl_status.setText("Status: Importing...")
        
        self.worker = ExcelImportWorker(
            self.attendance_service.import_from_excel, 
            file_path, None, self.current_session_id
        )
        self.worker.finished.connect(self._on_import_success)
        self.worker.error.connect(self._on_import_error)
        self.worker.start()

    def _on_import_success(self, result):
        self.btn_import.setEnabled(True)
        self.lbl_status.setText("Status: Import Successful")
        QMessageBox.information(self, "Success", f"Imported {result.valid_count} students.\n{result.nor_count} NOR entries found.")
        self._load_data()

    def _on_import_error(self, error_msg):
        self.btn_import.setEnabled(True)
        self.lbl_status.setText("Status: Import Failed")
        QMessageBox.critical(self, "Import Error", str(error_msg))

    def _load_data(self):
        students = self.attendance_service.get_all_students_sorted(self.current_session_id)
        nor_count = len(self.attendance_service.get_nor_rolls(self.current_session_id))
        
        self.table.setRowCount(0)
        for row, student in enumerate(students):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student['roll_number']))
            self.table.setItem(row, 1, QTableWidgetItem(str(student.get('student_name', ''))))
            
        self.lbl_summary.setText(f"Total Students: {len(students)} | NOR Students: {nor_count}")
