def _import_reportlab():
    """Lazy import of reportlab components to save memory on startup."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            Frame, PageTemplate, BaseDocTemplate, PageBreak
        )
        from reportlab.lib import colors
        from reportlab.lib.units import inch, mm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        return locals()
    except ImportError:
        raise ImportError("Error: 'reportlab' dependency not found. Please install it using 'pip install reportlab'.")

class PDFStyleFactory:
    _styles = None
    
    @classmethod
    def get_styles(cls):
        if cls._styles is None:
            rl = _import_reportlab()
            styles = rl['getSampleStyleSheet']()
            cls._styles = {
                'header': rl['ParagraphStyle']('Header', parent=styles['Normal'], fontSize=11, leading=14, alignment=rl['TA_CENTER']),
                'sub_header': rl['ParagraphStyle']('SubHeader', parent=styles['Normal'], fontSize=9, leading=11, alignment=rl['TA_CENTER']),
                'ref': rl['ParagraphStyle']('RefNo', parent=styles['Normal'], fontSize=9, leading=12),
                'ay': rl['ParagraphStyle']('AY', parent=styles['Normal'], fontSize=9, leading=12, alignment=rl['TA_CENTER']),
                'title': rl['ParagraphStyle']('SheetTitle', parent=styles['Normal'], fontSize=14, leading=18, alignment=rl['TA_CENTER']),
                'detail_key': rl['ParagraphStyle']('DetailKey', parent=styles['Normal'], fontSize=10, leading=14, fontName='Helvetica-Bold'),
                'detail_val': rl['ParagraphStyle']('DetailValue', parent=styles['Normal'], fontSize=10, leading=14),
                'totals': rl['ParagraphStyle']('Totals', parent=styles['Normal'], fontSize=10),
                'signature': rl['ParagraphStyle']('Signature', parent=styles['Normal'], fontSize=9, alignment=rl['TA_CENTER']),
            }
        return cls._styles

def build_college_header(college_name: str) -> list:
    """Build the standard college header elements."""
    rl = _import_reportlab()
    styles = PDFStyleFactory.get_styles()
    elements = []
    header_college = college_name if college_name else ''
    elements.append(rl['Paragraph'](f'<b>{header_college}</b>', styles['header']))
    elements.append(rl['Paragraph']('<i>(PROFESSIONAL DEGREE COURSES)</i>', styles['sub_header']))
    elements.append(rl['Paragraph']('Approved by Govt. of Maharashtra, Affiliated to University of Mumbai', styles['sub_header']))
    elements.append(rl['Paragraph']("NAAC Accredited Grade 'A' (1st cycle), & ISO 9001:2015 (Certified)", styles['sub_header']))
    elements.append(rl['Paragraph']('(Institute Code No. 1019)', styles['sub_header']))
    elements.append(rl['Spacer'](1, 0.08 * rl['inch']))
    return elements

def build_ref_section(title: str = "Attendance Sheet") -> list:
    rl = _import_reportlab()
    styles = PDFStyleFactory.get_styles()
    elements = []
    elements.append(rl['Paragraph']('<b>Ref. No.</b> - TSDC/IP/03/FRM/06', styles['ref']))
    elements.append(rl['Paragraph']('<b>Sem.</b> - I/II/III/IV/ V/VI <b>Internal/ External/ ATKT/ Examination First/ Second Half of</b>', styles['ref']))
    elements.append(rl['Paragraph']('<b>A.Y. 2025-26</b>', styles['ay']))
    elements.append(rl['Spacer'](1, 0.08 * rl['inch']))
    elements.append(rl['Paragraph'](f'<u><b>{title}</b></u>', styles['title']))
    elements.append(rl['Spacer'](1, 0.12 * rl['inch']))
    return elements

def build_details_table(details_rows: list) -> 'Table':
    """Build the exam details table (3 columns)."""
    rl = _import_reportlab()
    detail_table = rl['Table'](details_rows, colWidths=[2.1 * rl['inch']] * 3)
    detail_table.setStyle(rl['TableStyle']([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    return detail_table

def build_nor_section(nor_rolls: list) -> list:
    rl = _import_reportlab()
    styles = PDFStyleFactory.get_styles()
    nor_text = ', '.join(nor_rolls) if nor_rolls else 'None'
    return [
        rl['Paragraph'](f'<b>NOR:</b> {nor_text}', styles['detail_key']),
        rl['Spacer'](1, 0.12 * rl['inch'])
    ]

def build_totals_block() -> list:
    rl = _import_reportlab()
    styles = PDFStyleFactory.get_styles()
    totals_data = [[
        rl['Paragraph']('<b>Total No. of Students Present:</b> ____________', styles['totals']),
        rl['Paragraph']('<b>Total No. of Students Absent:</b> ____________', styles['totals'])
    ]]
    totals_table = rl['Table'](totals_data, colWidths=[3.25 * rl['inch']] * 2)
    totals_table.setStyle(rl['TableStyle']([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return [totals_table, rl['Spacer'](1, 0.12 * rl['inch'])]

def build_signature_block() -> list:
    rl = _import_reportlab()
    styles = PDFStyleFactory.get_styles()
    sig_lines = [
        [rl['Paragraph']('Name: ____________________', styles['signature']),
         rl['Paragraph']('Junior Supervisor/s', styles['signature']),
         rl['Paragraph']('Senior Supervisor', styles['signature'])],
        [rl['Paragraph']('Signature: ____________________', styles['signature']),
         rl['Paragraph']('(Name & Sign. with date)', styles['signature']),
         rl['Paragraph']('', styles['signature'])]
    ]
    sig_table = rl['Table'](sig_lines, colWidths=[1.8 * rl['inch'], 2.0 * rl['inch'], 2.0 * rl['inch']])
    sig_table.setStyle(rl['TableStyle']([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return [sig_table]
