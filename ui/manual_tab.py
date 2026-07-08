from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

class ManualTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Exam Automation - User Manual</h2>
        
        <h3>1. Global Exam Details</h3>
        <p>Start by filling out the global settings at the top of the window. This includes College Name, Program Name, Exam Name, Year, and Division. These details will be printed on all generated PDF reports.</p>
        
        <h3>2. Import Attendance</h3>
        <p>Go to the <b>Student Management</b> tab and click <b>Import Attendance Excel</b>. Your Excel file should contain columns for the student's Roll Number (or PRN, ID, Seat No, Enrollment No) and Name. The system will automatically detect these columns.</p>
        
        <h3>3. Import Timetable</h3>
        <p>Go to the <b>Timetable</b> tab and click <b>Import Timetable Excel</b>. The Excel file must contain Date, Time, Subject Code, and Subject Name.</p>
        
        <h3>4. Manage Classrooms</h3>
        <p>Go to the <b>Classrooms</b> tab to add the rooms available for the exam. You can specify the capacity (number of rows/columns) for each room. Only enabled rooms will be used for seating allocation.</p>
        
        <h3>5. Generate Seating & Stickers</h3>
        <p>Once students, timetable, and rooms are set up, go to the <b>Stickers</b> tab to generate PDF stickers for student answer sheets. You can also go to the <b>Reports</b> tab to generate Attendance Sheets and Seating Charts for each room.</p>
        
        <h3>Rules & Tips</h3>
        <ul>
            <li>Ensure Excel files are not open in another program while importing.</li>
            <li>If a student's name is empty in the Excel sheet, they will be treated as NOR (Not On Roll).</li>
            <li>Generated PDFs are saved in the <b>output</b> folder within the application directory.</li>
            <li>Dark mode is enabled by default to reduce eye strain.</li>
        </ul>
        """
        browser.setHtml(html_content)
        layout.addWidget(browser)
