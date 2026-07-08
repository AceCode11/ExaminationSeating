import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QLineEdit, QGroupBox, QFileDialog, QMessageBox, QDoubleSpinBox, QSpinBox
)
from ui.workers import PDFGenerationWorker
from services.validation_service import ValidationService
from core.exceptions import ExamAutomationError
import pdf.sticker_pdf

class StickerTab(QWidget):
    def __init__(self, sticker_service, current_session_id):
        super().__init__()
        self.sticker_service = sticker_service
        self.current_session_id = current_session_id
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Config Group
        group = QGroupBox("Sticker Configuration")
        grid = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Department/Prefix:"))
        self.txt_dept = QLineEdit()
        row1.addWidget(self.txt_dept)
        
        row1.addWidget(QLabel("Year:"))
        self.cmb_year = QComboBox()
        self.cmb_year.addItems(['FY', 'SY', 'TY', 'None'])
        row1.addWidget(self.cmb_year)
        grid.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Format:"))
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(['Only Roll Number', 'Year+Roll', 'Dept+Year+Roll vertically aligned'])
        row2.addWidget(self.cmb_format)
        
        row2.addWidget(QLabel("Font Size:"))
        self.cmb_font = QComboBox()
        self.cmb_font.addItems(['Small', 'Medium', 'Large'])
        self.cmb_font.setCurrentText('Medium')
        row2.addWidget(self.cmb_font)
        grid.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Width (mm):"))
        self.spin_w = QDoubleSpinBox()
        self.spin_w.setRange(10, 200)
        self.spin_w.setValue(52.5)
        row3.addWidget(self.spin_w)
        
        row3.addWidget(QLabel("Height (mm):"))
        self.spin_h = QDoubleSpinBox()
        self.spin_h.setRange(10, 200)
        self.spin_h.setValue(24.75)
        row3.addWidget(self.spin_h)
        
        row3.addWidget(QLabel("Cols per Row:"))
        self.spin_c = QSpinBox()
        self.spin_c.setRange(1, 10)
        self.spin_c.setValue(4)
        row3.addWidget(self.spin_c)
        grid.addLayout(row3)

        group.setLayout(grid)
        layout.addWidget(group)

        # Actions
        btn_gen = QPushButton("Generate Stickers")
        btn_gen.clicked.connect(self._generate)
        layout.addWidget(btn_gen)
        
        self.lbl_status = QLabel("Status: Ready")
        layout.addWidget(self.lbl_status)
        layout.addStretch()

    def _generate(self):
        try:
            w, h, c, prefix = ValidationService.validate_sticker_config(
                str(self.spin_w.value()), str(self.spin_h.value()), str(self.spin_c.value()),
                self.txt_dept.text(), self.cmb_year.currentText(), self.cmb_format.currentText()
            )
        except ExamAutomationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not out_dir:
            return

        self.lbl_status.setText("Status: Generating...")
        
        data = self.sticker_service.prepare_sticker_data(
            self.current_session_id, self.txt_dept.text(), self.cmb_year.currentText(),
            self.cmb_format.currentText(), w, h, c, self.cmb_font.currentText()
        )
        
        from utils.file_helpers import get_sticker_filename
        filename = get_sticker_filename(self.cmb_year.currentText(), self.txt_dept.text())
        filepath = os.path.join(out_dir, filename)
        
        self.worker = PDFGenerationWorker(pdf.sticker_pdf.generate, data, filepath)
        self.worker.finished.connect(lambda res: self._on_gen_complete(res, filepath))
        self.worker.error.connect(self._on_gen_error)
        self.worker.start()

    def _on_gen_complete(self, result, filepath):
        if result:
            self.lbl_status.setText("Status: Generation Successful")
            QMessageBox.information(self, "Success", f"Stickers saved to:\n{filepath}")
        else:
            self.lbl_status.setText("Status: Generation Failed")
            QMessageBox.critical(self, "Error", "Failed to generate PDF.")

    def _on_gen_error(self, error_msg):
        self.lbl_status.setText("Status: Generation Error")
        QMessageBox.critical(self, "Error", str(error_msg))
