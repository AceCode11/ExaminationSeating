from dataclasses import dataclass
from typing import List
from pdf.base_pdf import _import_reportlab
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class StickerPDFData:
    rolls: List[str]
    prefix_text: str
    roll_format: str
    sticker_width_mm: float
    sticker_height_mm: float
    cols_per_row: int
    font_size_choice: str

def generate(data: StickerPDFData, filename: str) -> bool:
    try:
        rl = _import_reportlab()
        
        width = data.sticker_width_mm * rl['mm']
        height = data.sticker_height_mm * rl['mm']
        cols = int(data.cols_per_row)
        
        if data.font_size_choice == "Small":
            prefix_font_size, roll_font_size = 8, 18
        elif data.font_size_choice == "Medium":
            prefix_font_size, roll_font_size = 10, 24
        else:
            prefix_font_size, roll_font_size = 12, 30
            
        P_STYLE = rl['ParagraphStyle']('RollPrefix', alignment=rl['TA_CENTER'], fontSize=prefix_font_size, leading=prefix_font_size + 2)
        R_STYLE = rl['ParagraphStyle']('RollNumber', alignment=rl['TA_CENTER'], fontSize=roll_font_size, fontName='Helvetica-Bold')
        
        doc = rl['BaseDocTemplate'](
            filename, pagesize=rl['A4'], 
            leftMargin=0, rightMargin=0, 
            topMargin=0, bottomMargin=0
        )
        doc.title = "Roll Number Stickers"
        
        page_width, page_height = rl['A4']
        rows_per_page = int(page_height / height) if height > 0 else 1
        
        stickers_width_total = cols * width
        stickers_height_total = rows_per_page * height
        x_start = (page_width - stickers_width_total) / 2
        
        def create_sticker_content(roll):
            content = []
            if data.roll_format == 'Only Roll Number':
                content.append(rl['Spacer'](1, height / 2 - roll_font_size / 2))
                content.append(rl['Paragraph'](str(roll), R_STYLE))
            elif data.roll_format == 'Year+Roll':
                content.append(rl['Spacer'](1, height * 0.2))
                content.append(rl['Paragraph'](data.prefix_text, P_STYLE))
                content.append(rl['Spacer'](1, 0.1 * height))
                content.append(rl['Paragraph'](str(roll), R_STYLE))
            elif data.roll_format == 'Dept+Year+Roll vertically aligned':
                text = f'<font size="{prefix_font_size}">{data.prefix_text}</font><br/><font size="{roll_font_size}" face="Helvetica-Bold">{str(roll)}</font>'
                content.append(rl['Spacer'](1, height * 0.3))
                content.append(rl['Paragraph'](text, rl['ParagraphStyle'](name='CombinedRollStyle', parent=R_STYLE, leading=roll_font_size + 2)))
            content.append(rl['Spacer'](1, 0.01 * rl['mm']))
            return content
            
        frames = []
        for r in range(rows_per_page):
            for c in range(cols):
                frame_x = x_start + c * width
                frame_y = page_height - (page_height - stickers_height_total) / 2 - (r + 1) * height
                frame = rl['Frame'](
                    frame_x, frame_y, width, height,
                    leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0,
                    showBoundary=0
                )
                frames.append(frame)
                
        template = rl['PageTemplate'](frames=frames)
        doc.addPageTemplates([template])
        
        sorted_rolls = sorted(data.rolls)
        elements = []
        for roll in sorted_rolls:
            elements.extend(create_sticker_content(roll))
            
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Sticker PDF Generation Error: {e}")
        return False
