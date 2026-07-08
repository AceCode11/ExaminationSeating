import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt
from ui.workers import AllocationWorker
from services.validation_service import ValidationService
from core.exceptions import ExamAutomationError

class ClassroomTab(QWidget):
    def __init__(self, seating_service, attendance_service, current_session_id):
        super().__init__()
        self.seating_service = seating_service
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

        # Input Group
        input_group = QGroupBox("Add Classroom")
        input_layout = QHBoxLayout()
        
        self.txt_room = QLineEdit()
        self.txt_room.setPlaceholderText("Room Number (e.g. 101)")
        
        self.txt_capacity = QLineEdit()
        self.txt_capacity.setPlaceholderText("Capacity (e.g. 30)")
        
        btn_add = QPushButton("Add/Update Room")
        btn_add.clicked.connect(self._add_room)
        
        input_layout.addWidget(QLabel("Room:"))
        input_layout.addWidget(self.txt_room)
        input_layout.addWidget(QLabel("Capacity:"))
        input_layout.addWidget(self.txt_capacity)
        input_layout.addWidget(btn_add)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Actions
        action_layout = QHBoxLayout()
        btn_allocate = QPushButton("Allocate Students")
        btn_allocate.clicked.connect(self._allocate_students)
        btn_clear = QPushButton("Clear All Rooms")
        btn_clear.clicked.connect(self._clear_rooms)
        
        action_layout.addWidget(btn_allocate)
        action_layout.addWidget(btn_clear)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.lbl_status = QLabel("Status: Ready")
        layout.addWidget(self.lbl_status)

        # Rooms Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Room Number", "Capacity", "Allocated"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.lbl_summary = QLabel("Total Rooms: 0 | Total Capacity: 0")
        layout.addWidget(self.lbl_summary)

    def _add_room(self):
        try:
            room_no, capacity = ValidationService.validate_room_input(self.txt_room.text(), self.txt_capacity.text())
            self.seating_service.add_room(room_no, capacity, self.current_session_id)
            self.txt_room.clear()
            self.txt_capacity.clear()
            self.txt_room.setFocus()
            self._load_data()
        except ExamAutomationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def _clear_rooms(self):
        reply = QMessageBox.question(self, "Confirm Clear", "Are you sure you want to clear all rooms and allocations?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.seating_service.clear_rooms(self.current_session_id)
            self._load_data()

    def _allocate_students(self):
        student_count = self.attendance_service.get_student_count(self.current_session_id)
        rooms = self.seating_service.get_rooms(self.current_session_id)
        
        try:
            ValidationService.validate_allocation_readiness(bool(rooms), student_count > 0)
        except ExamAutomationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return

        self.lbl_status.setText("Status: Allocating...")
        self.worker = AllocationWorker(self.seating_service.allocate_students, self.current_session_id)
        self.worker.finished.connect(self._on_allocation_success)
        self.worker.error.connect(self._on_allocation_error)
        self.worker.start()

    def _on_allocation_success(self, result):
        self.lbl_status.setText("Status: Allocation Complete")
        msg = f"Allocated: {result.allocated_count}\nUnallocated: {result.unallocated_count}\nTotal Students: {result.total_students}"
        if result.unallocated_count > 0:
            QMessageBox.warning(self, "Allocation Complete with Warnings", msg)
        else:
            QMessageBox.information(self, "Success", msg)
        self._load_data()

    def _on_allocation_error(self, error_msg):
        self.lbl_status.setText("Status: Allocation Failed")
        QMessageBox.critical(self, "Allocation Error", str(error_msg))

    def _load_data(self):
        rooms = self.seating_service.get_rooms(self.current_session_id)
        allocations = {item['room_number']: item['student_count'] 
                      for item in self.seating_service.get_allocation_summary(self.current_session_id)}
        
        total_capacity = 0
        self.table.setRowCount(0)
        for row, room in enumerate(rooms):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(room['room_number']))
            self.table.setItem(row, 1, QTableWidgetItem(str(room['capacity'])))
            allocated = allocations.get(room['room_number'], 0)
            self.table.setItem(row, 2, QTableWidgetItem(str(allocated)))
            total_capacity += room['capacity']
            
        self.lbl_summary.setText(f"Total Rooms: {len(rooms)} | Total Capacity: {total_capacity}")
