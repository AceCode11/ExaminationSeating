from dataclasses import dataclass
from typing import List
from pdf.base_pdf import (
    _import_reportlab, PDFStyleFactory, build_college_header, 
    build_ref_section, build_details_table, build_nor_section, 
    build_totals_block, build_signature_block
)
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AttendancePDFData:
    college_name: str
    program_name: str
    exam_name: str
    division: str
    subject_code: str
    subject_name: str
    date: str
    time: str
    block_number: str
    roll_no_from: str
    roll_no_to: str
    students: List[dict]  # [{'roll_number': '123', 'student_name': 'abc'}]
    nor_rolls: List[str]

def generate(data: AttendancePDFData, filename: str) -> bool:
    try:
        rl = _import_reportlab()
        styles = PDFStyleFactory.get_styles()
        
        doc = rl['SimpleDocTemplate'](
            filename, pagesize=rl['A4'], 
            rightMargin=72, leftMargin=72, 
            topMargin=50, bottomMargin=50
        )
        
        elements = []
        
        # Build multi-page content
        rolls = [s['roll_number'] for s in data.students]
        PAGE_SIZE = 40
        left_side_count = 20
        
        pages = [
            rolls[i:i+PAGE_SIZE] for i in range(0, len(rolls), PAGE_SIZE)
        ]
        
        for page_index, page_rolls in enumerate(pages):
            if page_index > 0:
                elements.append(rl['PageBreak']())
                
            elements.extend(build_college_header(data.college_name))
            elements.extend(build_ref_section("Attendance Sheet"))
            
            # Details Table
            data_details = [
                [rl['Paragraph']("Day: __________________", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Class:</b> {data.division}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Programme:</b> {data.program_name}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Date:</b> {data.date}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Course:</b> {data.program_name}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Paper:</b> {data.subject_name}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Time:</b> {data.time}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Block No.:</b> {data.block_number}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Room No.:</b> {data.block_number}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Roll No's: From</b> {data.roll_no_from}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>To</b> {data.roll_no_to}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Total:</b> {len(data.students)}", styles['detail_key'])]
            ]
            
            elements.append(build_details_table(data_details))
            elements.append(rl['Spacer'](1, 0.06 * rl['inch']))
            
            # NOR section only on first page
            if page_index == 0:
                elements.extend(build_nor_section(data.nor_rolls))
                
            # 8-column table
            table_data = [
                ["SrNo", "Seat No./ Roll No.", "Student's Signature", "No of Suppl",
                 "SrNo", "Seat No./ Roll No.", "Student's Signature", "No of Suppl"]
            ]
            
            left_rolls = page_rolls[:left_side_count]
            right_rolls = page_rolls[left_side_count:]
            right_rolls += [""] * (left_side_count - len(right_rolls))
            
            for i in range(left_side_count):
                if i < len(left_rolls) and left_rolls[i] != "":
                    l_sr = page_index * PAGE_SIZE + (i + 1)
                    l_roll = left_rolls[i]
                else:
                    l_sr = l_roll = ""
                    
                r_roll = right_rolls[i]
                if r_roll != "":
                    r_sr = page_index * PAGE_SIZE + (left_side_count + i + 1)
                else:
                    r_sr = ""
                    
                table_data.append([str(l_sr), l_roll, "", "", str(r_sr), r_roll, "", ""])
                
            col_widths = [
                0.45 * rl['inch'], 1.0 * rl['inch'], 1.4 * rl['inch'], 1.0 * rl['inch'],
                0.45 * rl['inch'], 1.0 * rl['inch'], 1.4 * rl['inch'], 1.0 * rl['inch']
            ]
            
            attendance_table = rl['Table'](table_data, colWidths=col_widths)
            attendance_table.setStyle(rl['TableStyle']([
                ('GRID', (0,0),(-1,-1), 0.35, rl['colors'].black),
                ('FONTNAME', (0,0),(-1,0),'Helvetica-Bold'),
                ('BACKGROUND', (0,0),(-1,0),rl['colors'].lightgrey),
                ('ALIGN', (0,0),(-1,0),'CENTER'),
                ('ALIGN', (0,1),(-1,-1),'CENTER'),
                ('VALIGN', (0,1),(-1,-1),'MIDDLE'),
                ('FONTSIZE', (0,0),(-1,-1), 9),
                ('ROWHEIGHT', (0,1),(-1,-1), 20),
            ]))
            
            elements.append(attendance_table)
            elements.append(rl['Spacer'](1, 0.12 * rl['inch']))
            
            elements.extend(build_totals_block())
            elements.extend(build_signature_block())
            
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Attendance PDF Generation Error: {e}")
        return False
