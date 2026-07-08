import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QFileDialog, QMessageBox, QGroupBox, QListWidget, QAbstractItemView
)
from ui.workers import PDFGenerationWorker
from services.validation_service import ValidationService
from core.exceptions import ExamAutomationError
from utils.file_helpers import get_attendance_filename, get_seating_filename, get_reports_filename
import pdf.attendance_pdf
import pdf.seating_pdf
import pdf.reports_pdf

class ReportsTab(QWidget):
    def __init__(self, seating_service, attendance_service, timetable_service, report_service, settings, current_session_id):
        super().__init__()
        self.seating_service = seating_service
        self.attendance_service = attendance_service
        self.timetable_service = timetable_service
        self.report_service = report_service
        self.settings = settings
        self.current_session_id = current_session_id
        self.worker = None
        self.workers = []  # Keep refs to prevent gc if multiple
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Subject Selection
        sub_group = QGroupBox("Select Subject")
        sub_layout = QVBoxLayout()
        self.cmb_subject = QComboBox()
        btn_refresh = QPushButton("Refresh Subjects & Rooms")
        btn_refresh.clicked.connect(self._load_data)
        sub_layout.addWidget(self.cmb_subject)
        sub_layout.addWidget(btn_refresh)
        sub_group.setLayout(sub_layout)
        layout.addWidget(sub_group)

        # Room Selection
        room_group = QGroupBox("Select Rooms for PDF Generation")
        room_layout = QVBoxLayout()
        self.list_rooms = QListWidget()
        self.list_rooms.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        room_layout.addWidget(self.list_rooms)
        
        btn_sel_all = QPushButton("Select All Rooms")
        btn_sel_all.clicked.connect(self.list_rooms.selectAll)
        room_layout.addWidget(btn_sel_all)
        room_group.setLayout(room_layout)
        layout.addWidget(room_group)

        # Actions
        action_group = QGroupBox("Generate PDFs")
        action_layout = QHBoxLayout()
        
        btn_att = QPushButton("Generate Attendance Sheets")
        btn_att.clicked.connect(lambda: self._generate_pdfs("attendance"))
        
        btn_seat = QPushButton("Generate Seating Arrangements")
        btn_seat.clicked.connect(lambda: self._generate_pdfs("seating"))
        
        btn_rep = QPushButton("Generate Jr. Supervisor Reports")
        btn_rep.clicked.connect(lambda: self._generate_pdfs("reports"))
        
        btn_all = QPushButton("Generate All")
        btn_all.clicked.connect(lambda: self._generate_pdfs("all"))
        
        action_layout.addWidget(btn_att)
        action_layout.addWidget(btn_seat)
        action_layout.addWidget(btn_rep)
        action_layout.addWidget(btn_all)
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)

        self.lbl_status = QLabel("Status: Ready")
        layout.addWidget(self.lbl_status)
        
    def showEvent(self, event):
        super().showEvent(event)
        self._load_data()

    def _load_data(self):
        subjects = self.timetable_service.get_subjects_list(self.current_session_id)
        self.cmb_subject.clear()
        self.cmb_subject.addItems(subjects)

        rooms = self.seating_service.get_allocated_rooms(self.current_session_id)
        self.list_rooms.clear()
        self.list_rooms.addItems(rooms)

    def _generate_pdfs(self, report_type: str):
        try:
            subject_code, _ = ValidationService.validate_subject_selection(self.cmb_subject.currentText())
        except ExamAutomationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return
            
        selected_items = self.list_rooms.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Validation Error", "Please select at least one room.")
            return
            
        rooms = [item.text() for item in selected_items]
        
        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not out_dir:
            return

        total_expected_pdfs = len(rooms) * (3 if report_type == "all" else 1)
        self.lbl_status.setText(f"Status: Generating {total_expected_pdfs} PDFs...")
        self.workers.clear()

        # Batch preparation could be optimized, but generating serially for simplicity here,
        # or launch one worker that does all rooms. Let's make a single worker for the batch.
        
        def _batch_generate():
            success_count = 0
            for room in rooms:
                # Get data based on type
                if report_type in ("attendance", "all"):
                    from pdf.attendance_pdf import AttendancePDFData
                    # Gather data...
                    # This logic belongs in a service method, but for brevity we adapt here:
                    report_data = self.report_service.prepare_report_data(self.current_session_id, subject_code, room, room)
                    rolls = self.seating_service.get_allocated_rolls_for_room(room, self.current_session_id)
                    students = [s for s in report_data.students if s['roll_number'] in rolls]
                    
                    data = AttendancePDFData(
                        college_name=report_data.college_name, program_name=report_data.program_name,
                        exam_name=report_data.exam_name, division=report_data.division,
                        subject_code=report_data.subject_code, subject_name=report_data.subject_name,
                        date=report_data.date, time=report_data.time, block_number=room,
                        roll_no_from=students[0]['roll_number'] if students else "",
                        roll_no_to=students[-1]['roll_number'] if students else "",
                        students=students, nor_rolls=report_data.nor_rolls
                    )
                    filename = get_attendance_filename(subject_code, report_data.date, room)
                    if pdf.attendance_pdf.generate(data, os.path.join(out_dir, filename)):
                        success_count += 1
                        
                if report_type in ("seating", "all"):
                    from pdf.seating_pdf import SeatingPDFData
                    report_data = self.report_service.prepare_report_data(self.current_session_id, subject_code, room, room)
                    rolls = self.seating_service.get_allocated_rolls_for_room(room, self.current_session_id)
                    data = SeatingPDFData(
                        college_name=report_data.college_name, program_name=report_data.program_name,
                        exam_name=report_data.exam_name, room_number=room,
                        date=report_data.date, time=report_data.time,
                        subject_code=report_data.subject_code, subject_name=report_data.subject_name,
                        students_rolls=rolls
                    )
                    filename = get_seating_filename(subject_code, report_data.date, room)
                    if pdf.seating_pdf.generate(data, os.path.join(out_dir, filename)):
                        success_count += 1
                        
                if report_type in ("reports", "all"):
                    report_data = self.report_service.prepare_report_data(self.current_session_id, subject_code, room, room)
                    rolls = self.seating_service.get_allocated_rolls_for_room(room, self.current_session_id)
                    students = [s for s in report_data.students if s['roll_number'] in rolls]
                    report_data.students = students
                    
                    filename = get_reports_filename(subject_code, report_data.date, room)
                    if pdf.reports_pdf.generate(report_data, os.path.join(out_dir, filename)):
                        success_count += 1
                        
            return success_count

        self.worker = PDFGenerationWorker(_batch_generate)
        self.worker.finished.connect(lambda count: self._on_batch_complete(count, total_expected_pdfs))
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_batch_complete(self, success_count, total):
        self.lbl_status.setText("Status: Ready")
        if success_count == total:
            QMessageBox.information(self, "Success", f"Successfully generated {success_count} PDFs.")
        else:
            QMessageBox.warning(self, "Partial Success", f"Generated {success_count} of {total} PDFs.")

    def _on_error(self, error_msg):
        self.lbl_status.setText("Status: Error")
        QMessageBox.critical(self, "Error", str(error_msg))
