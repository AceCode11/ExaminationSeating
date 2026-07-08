import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from ui.workers import ExcelImportWorker

class TimetableTab(QWidget):
    def __init__(self, timetable_service, current_session_id):
        super().__init__()
        self.timetable_service = timetable_service
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

        top_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import Timetable Excel")
        self.btn_import.clicked.connect(self._import_excel)
        self.lbl_status = QLabel("Status: Ready")
        top_layout.addWidget(self.btn_import)
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Time", "Subject Code", "Subject Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.lbl_summary = QLabel("Total Entries: 0")
        layout.addWidget(self.lbl_summary)

    def _import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Timetable Excel", "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return

        self.btn_import.setEnabled(False)
        self.lbl_status.setText("Status: Importing...")
        
        self.worker = ExcelImportWorker(
            self.timetable_service.import_timetable, 
            file_path, None, self.current_session_id
        )
        self.worker.finished.connect(self._on_import_success)
        self.worker.error.connect(self._on_import_error)
        self.worker.start()

    def _on_import_success(self, count):
        self.btn_import.setEnabled(True)
        self.lbl_status.setText("Status: Import Successful")
        QMessageBox.information(self, "Success", f"Imported {count} timetable entries.")
        self._load_data()

    def _on_import_error(self, error_msg):
        self.btn_import.setEnabled(True)
        self.lbl_status.setText("Status: Import Failed")
        QMessageBox.critical(self, "Import Error", str(error_msg))

    def _load_data(self):
        entries = self.timetable_service.get_entries(self.current_session_id)
        
        self.table.setRowCount(0)
        for row, entry in enumerate(entries):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry['Date']))
            self.table.setItem(row, 1, QTableWidgetItem(entry['Time']))
            self.table.setItem(row, 2, QTableWidgetItem(entry['SubjectCode']))
            self.table.setItem(row, 3, QTableWidgetItem(entry['SubjectName']))
            
        self.lbl_summary.setText(f"Total Entries: {len(entries)}")
