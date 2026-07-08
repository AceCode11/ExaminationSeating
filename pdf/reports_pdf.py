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
class ReportsPDFData:
    college_name: str
    program_name: str
    exam_name: str
    division: str
    subject_code: str
    subject_name: str
    date: str
    time: str
    block_number: str
    room_number: str
    students: List[dict]  # [{'roll_number': '123', 'student_name': 'abc'}]
    nor_rolls: List[str]

def generate(data: ReportsPDFData, filename: str) -> bool:
    try:
        rl = _import_reportlab()
        styles = PDFStyleFactory.get_styles()
        
        doc = rl['SimpleDocTemplate'](
            filename, pagesize=rl['A4'], 
            rightMargin=72, leftMargin=72, 
            topMargin=50, bottomMargin=50
        )
        
        elements = []
        
        rolls = [s['roll_number'] for s in data.students]
        PAGE_SIZE = 40
        left_side_count = 20
        
        pages = [
            rolls[i:i+PAGE_SIZE] for i in range(0, len(rolls), PAGE_SIZE)
        ]
        
        # Hollow Circle representation
        hollow_circle = u'\u25EF'
        normal_styles = rl['getSampleStyleSheet']()
        circle_style = rl['ParagraphStyle']('CircleStyle', parent=normal_styles['Normal'], alignment=rl['TA_CENTER'], fontSize=12, leading=14)
        circle_content = rl['Paragraph'](f"&nbsp;{hollow_circle}&nbsp;", circle_style)
        
        # Get sorting info
        if data.students:
            roll_no_from = data.students[0]['roll_number']
            roll_no_to = data.students[-1]['roll_number']
        else:
            roll_no_from = "____"
            roll_no_to = "____"
        
        for page_index, page_rolls in enumerate(pages):
            if page_index > 0:
                elements.append(rl['PageBreak']())
                
            elements.extend(build_college_header(data.college_name))
            elements.extend(build_ref_section("Reports Sheet"))
            
            data_details = [
                [rl['Paragraph']("Day: __________________", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Class:</b> {data.division}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Programme:</b> {data.program_name}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Date:</b> {data.date}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Course:</b> {data.program_name}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Paper:</b> {data.subject_name}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Time:</b> {data.time}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Block No.:</b> {data.block_number}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Room No.:</b> {data.room_number}", styles['detail_key'])],
                 
                [rl['Paragraph'](f"<b>Roll No's: From</b> {roll_no_from}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>To</b> {roll_no_to}", styles['detail_key']), 
                 rl['Paragraph'](f"<b>Total:</b> {len(data.students)}", styles['detail_key'])]
            ]
            
            elements.append(build_details_table(data_details))
            elements.append(rl['Spacer'](1, 0.06 * rl['inch']))
            
            if page_index == 0:
                elements.extend(build_nor_section(data.nor_rolls))
                
            table_data = [
                ["SrNo", "Seat No./ Roll No.", "P", "A", "M",
                 "SrNo", "Seat No./ Roll No.", "P", "A", "M"]
            ]
            
            left_rolls = page_rolls[:left_side_count]
            right_rolls = page_rolls[left_side_count:]
            right_rolls += [""] * (left_side_count - len(right_rolls))
            
            for i in range(left_side_count):
                if i < len(left_rolls) and left_rolls[i] != "":
                    l_sr = page_index * PAGE_SIZE + (i + 1)
                    l_roll = left_rolls[i]
                    l_a, l_m = circle_content, circle_content
                else:
                    l_sr = l_roll = l_a = l_m = ""
                    
                r_roll = right_rolls[i]
                if r_roll != "":
                    r_sr = page_index * PAGE_SIZE + (left_side_count + i + 1)
                    r_a, r_m = circle_content, circle_content
                else:
                    r_sr = r_a = r_m = ""
                    
                table_data.append([str(l_sr), l_roll, "", l_a, l_m, str(r_sr), r_roll, "", r_a, r_m])
                
            col_widths = [
                0.4 * rl['inch'], 1.4 * rl['inch'], 0.7 * rl['inch'], 0.7 * rl['inch'], 0.7 * rl['inch'],
                0.4 * rl['inch'], 1.4 * rl['inch'], 0.7 * rl['inch'], 0.7 * rl['inch'], 0.7 * rl['inch']
            ]
            
            reports_table = rl['Table'](table_data, colWidths=col_widths)
            reports_table.setStyle(rl['TableStyle']([
                ('GRID', (0,0),(-1,-1), 0.4, rl['colors'].black),
                ('FONTNAME', (0,0),(-1,0),'Helvetica-Bold'),
                ('BACKGROUND', (0,0),(-1,0),rl['colors'].lightgrey),
                ('ALIGN', (0,0),(-1,0),'CENTER'),
                ('ALIGN', (0,1),(-1,-1),'CENTER'),
                ('VALIGN', (0,1),(-1,-1),'MIDDLE'),
                ('FONTSIZE', (0,0),(-1,-1), 9),
                ('ROWHEIGHT', (0,1),(-1,-1), 20),
            ]))
            
            elements.append(reports_table)
            elements.append(rl['Spacer'](1, 0.12 * rl['inch']))
            
            elements.extend(build_totals_block())
            elements.extend(build_signature_block())
            
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Reports PDF Generation Error: {e}")
        return False
