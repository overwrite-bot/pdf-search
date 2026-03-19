#!/usr/bin/env python3
"""
Professional PDF with colors, boxes, and better design.
Uses reportlab with styled tables and backgrounds.
"""

import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Frame, PageTemplate
)
from reportlab.pdfgen import canvas
from datetime import datetime

class ColoredNumberCanvas(canvas.Canvas):
    """Custom canvas for header/footer with colors."""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_page_decorations(page_num)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_num):
        """Draw header/footer with colors."""
        # Header background
        self.setFillColor(colors.HexColor('#007acc'))
        self.rect(0, A4[1]-0.8*cm, A4[0], 0.8*cm, fill=1, stroke=0)
        
        # Page number footer
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawString(1*cm, 0.5*cm, f"Seite {page_num}")

def create_professional_pdf(md_file, pdf_file):
    """Generate colorful, professional PDF from Markdown."""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create document with canvas
    doc = SimpleDocTemplate(
        pdf_file, 
        pagesize=A4, 
        topMargin=3*cm, 
        bottomMargin=1.5*cm,
        leftMargin=2*cm, 
        rightMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles with colors
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#007acc'),
        spaceAfter=20,
        spaceBefore=10,
        borderPadding=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=15,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#0066cc'),
        borderWidth=2,
        borderPadding=8,
        borderRadius=3
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        lineHeight=1.6,
        textColor=colors.HexColor('#444444')
    ))
    
    styles.add(ParagraphStyle(
        name='RecipeTitle',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#cc6600'),
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='RecipeMetadata',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        spaceAfter=8,
        fontName='Helvetica-Oblique'
    ))
    
    styles.add(ParagraphStyle(
        name='RecipeIngredient',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        textColor=colors.HexColor('#555555'),
        leftIndent=15
    ))
    
    styles.add(ParagraphStyle(
        name='RecipeInstruction',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5,
        textColor=colors.HexColor('#444444'),
        leftIndent=20,
        lineHeight=1.5
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.HexColor('#444444'),
        leftIndent=20
    ))
    
    story = []
    
    # Parse markdown
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('# '):
            # Title with colored box
            title = line[2:].strip()
            title_table = Table(
                [[(Paragraph(title, styles['CustomTitle']))]],
                colWidths=[A4[0]-4*cm]
            )
            title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f8ff')),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BORDER', (0, 0), (-1, -1), 2, colors.HexColor('#007acc')),
                ('ROUNDED', (0, 0), (-1, -1), 5),
            ]))
            story.append(title_table)
            story.append(Spacer(1, 0.5*cm))
            
        elif line.startswith('## '):
            # Section heading with color bar
            section = line[3:].strip()
            heading_table = Table(
                [[(Paragraph(section, styles['CustomHeading2']))]],
                colWidths=[A4[0]-4*cm]
            )
            heading_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f2ff')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('BORDER', (0, 0), (-1, -1), 2, colors.HexColor('#0066cc')),
            ]))
            story.append(Spacer(1, 0.3*cm))
            story.append(heading_table)
            story.append(Spacer(1, 0.2*cm))
            
        elif line.startswith('#### '):
            # Recipe title (4 hashes)
            recipe_title = line[5:].strip()
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(recipe_title, styles['RecipeTitle']))
            
        elif line.startswith('### '):
            # Section heading
            story.append(Paragraph(line[4:], styles['CustomHeading3']))
            
        elif line.startswith('**Zutaten:**'):
            # Ingredients header
            story.append(Spacer(1, 0.1*cm))
            story.append(Paragraph("🧂 <b>Zutaten:</b>", styles['CustomHeading3']))
            story.append(Spacer(1, 0.05*cm))
            
        elif line.startswith('**Anleitung:**'):
            # Instructions header
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph("👨‍🍳 <b>Anleitung:</b>", styles['CustomHeading3']))
            story.append(Spacer(1, 0.05*cm))
            
        elif line.startswith('- [ ] ') or line.startswith('- '):
            # Ingredient bullet with checkbox style
            ingredient = line.replace('- [ ] ', '').replace('- ', '').strip()
            if ingredient:
                story.append(Paragraph(f"☐ {ingredient}", styles['RecipeIngredient']))
            
        elif line and line[0].isdigit() and '. ' in line:
            # Numbered instruction
            story.append(Paragraph(line, styles['RecipeInstruction']))
            
        elif line.startswith('| '):
            # Skip table markers
            pass
            
        elif line.startswith('👥 ') or line.startswith('⏱️ '):
            # Metadata line (servings, time)
            story.append(Paragraph(line, styles['RecipeMetadata']))
            
        elif line.strip() and not line.startswith('|'):
            story.append(Paragraph(line, styles['CustomBody']))
        else:
            story.append(Spacer(1, 0.15*cm))
        
        i += 1
    
    # Add footer with timestamp
    story.append(Spacer(1, 1*cm))
    footer_text = f"Generiert: {datetime.now().strftime('%d. %B %Y um %H:%M')} | Seite <page/>"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))
    
    # Build PDF
    doc.build(story, canvasmaker=ColoredNumberCanvas)
    
    file_size = os.path.getsize(pdf_file) / 1024
    print(f"✅ PDF created: {pdf_file} ({file_size:.1f} KB)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pdf-design.py <input.md> <output.pdf>")
        sys.exit(1)
    
    try:
        create_professional_pdf(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"⚠️  Error: {e}")
        sys.exit(1)
