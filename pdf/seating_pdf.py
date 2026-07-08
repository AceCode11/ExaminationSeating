from dataclasses import dataclass
from typing import List
from pdf.base_pdf import _import_reportlab, PDFStyleFactory
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SeatingPDFData:
    college_name: str
    program_name: str
    exam_name: str
    room_number: str
    date: str
    time: str
    subject_code: str
    subject_name: str
    students_rolls: List[str]

def generate(data: SeatingPDFData, filename: str) -> bool:
    try:
        rl = _import_reportlab()
        styles = rl['getSampleStyleSheet']()
        
        doc = rl['SimpleDocTemplate'](
            filename, pagesize=rl['A4'], 
            rightMargin=36, leftMargin=36, 
            topMargin=36, bottomMargin=36
        )
        
        h_style = rl['ParagraphStyle']('Header', parent=styles['Normal'], fontSize=12, leading=16, alignment=1)
        s_style = rl['ParagraphStyle']('SubHeader', parent=styles['Normal'], fontSize=10, leading=14)
        
        elements = []
        
        elements.append(rl['Paragraph']("<b>UNIVERSITY OF MUMBAI</b>", h_style))
        elements.append(rl['Paragraph'](f"{data.college_name}", h_style))
        elements.append(rl['Paragraph'](f"<b>Seating Arrangement for {data.program_name} - {data.exam_name}</b>", h_style))
        elements.append(rl['Spacer'](1, 0.1 * rl['inch']))
        
        data_details = [
            [rl['Paragraph'](f"<b>Room No:</b> {data.room_number}", s_style), rl['Paragraph'](f"<b>Total Students:</b> {len(data.students_rolls)}", s_style)],
            [rl['Paragraph'](f"<b>Paper Code:</b> {data.subject_code}", s_style), rl['Paragraph'](f"<b>Date:</b> {data.date}", s_style)],
            [rl['Paragraph'](f"<b>Paper Name:</b> {data.subject_name}", s_style), rl['Paragraph'](f"<b>Time:</b> {data.time}", s_style)]
        ]
        
        detail_table = rl['Table'](data_details, colWidths=[3.5*rl['inch'], 3.5*rl['inch']])
        detail_table.setStyle(rl['TableStyle']([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(detail_table)
        elements.append(rl['Spacer'](1, 0.1 * rl['inch']))
        
        ROLLS_PER_ROW = 10
        sorted_rolls = sorted(data.students_rolls)
        roll_rows = [sorted_rolls[i:i + ROLLS_PER_ROW] for i in range(0, len(sorted_rolls), ROLLS_PER_ROW)]
        
        table_data = []
        for row in roll_rows:
            padded_row = row + [""] * (ROLLS_PER_ROW - len(row))
            table_data.append([str(r) for r in padded_row])
            
        table_style = rl['TableStyle']([
            ('GRID', (0, 0), (-1, -1), 0.5, rl['colors'].black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWHEIGHT', (0, 0), (-1, -1), 0.3*rl['inch'])
        ])
        
        col_widths = [7.5 / ROLLS_PER_ROW * rl['inch']] * ROLLS_PER_ROW
        t = rl['Table'](table_data, colWidths=col_widths)
        t.setStyle(table_style)
        elements.append(t)
        
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Seating PDF Generation Error: {e}")
        return False
