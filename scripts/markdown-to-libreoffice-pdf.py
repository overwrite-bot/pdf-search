#!/usr/bin/env python3
"""
Convert Markdown to LibreOffice ODT, then to PDF.
Professional formatting matching LAMM-REPORT style.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

def markdown_to_libreoffice_pdf(md_file: str, output_pdf: str) -> bool:
    """
    Convert Markdown to professional PDF via LibreOffice.
    
    Steps:
    1. Read Markdown
    2. Generate ODT (using pandoc or LibreOffice Writer)
    3. Export ODT to PDF via LibreOffice
    
    Args:
        md_file: Path to markdown file
        output_pdf: Path to output PDF
    
    Returns:
        True if successful
    """
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"❌ Markdown file not found: {md_file}")
        return False
    
    # Check for pandoc (preferred for MD → ODT)
    try:
        result = subprocess.run(
            ["which", "pandoc"],
            capture_output=True,
            text=True
        )
        has_pandoc = result.returncode == 0
    except:
        has_pandoc = False
    
    # Step 1: Create temporary ODT
    with tempfile.NamedTemporaryFile(suffix=".odt", delete=False) as tmp:
        odt_file = tmp.name
    
    try:
        if has_pandoc:
            # Use pandoc for clean conversion
            print("📝 Converting Markdown → ODT (pandoc)...")
            result = subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "odt",
                 "-o", odt_file, str(md_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"⚠️  Pandoc failed, trying HTML fallback...")
                has_pandoc = False
        
        if not has_pandoc:
            # Fallback: HTML → PDF directly via LibreOffice
            print("📝 Converting Markdown → HTML → PDF (LibreOffice)...")
            
            # Create HTML from Markdown
            html_content = markdown_to_html(str(md_path))
            
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tmp_html:
                tmp_html.write(html_content)
                html_file = tmp_html.name
            
            try:
                # Direct HTML to PDF (more reliable)
                result = subprocess.run(
                    ["/snap/bin/libreoffice", "--headless", "--convert-to", "pdf",
                     "--outdir", os.path.dirname(output_pdf), html_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # LibreOffice outputs with .html → .pdf conversion
                    expected_pdf = os.path.join(
                        os.path.dirname(output_pdf),
                        Path(html_file).stem + ".pdf"
                    )
                    
                    if os.path.exists(expected_pdf) and expected_pdf != output_pdf:
                        subprocess.run(["mv", expected_pdf, output_pdf])
                    
                    if os.path.exists(output_pdf):
                        file_size = os.path.getsize(output_pdf) / 1024  # KB
                        print(f"✅ PDF created: {output_pdf} ({file_size:.1f} KB)")
                        return True
                    
                print(f"⚠️  LibreOffice conversion: {result.stderr}")
                return False
            finally:
                try:
                    os.remove(html_file)
                except:
                    pass
        
        # If pandoc succeeded, continue with ODT → PDF
        if has_pandoc:
        
        # Step 2: Convert ODT to PDF via LibreOffice
        print("📄 Converting ODT → PDF (LibreOffice)...")
        
        result = subprocess.run(
            ["/snap/bin/libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", os.path.dirname(output_pdf), odt_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ LibreOffice PDF conversion failed: {result.stderr}")
            return False
        
        # LibreOffice outputs to same dir as input, rename if needed
        expected_pdf = os.path.join(
            os.path.dirname(odt_file),
            Path(odt_file).stem + ".pdf"
        )
        
        if os.path.exists(expected_pdf) and expected_pdf != output_pdf:
            subprocess.run(["mv", expected_pdf, output_pdf])
        
        if os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf) / 1024  # KB
            print(f"✅ PDF created: {output_pdf} ({file_size:.1f} KB)")
            return True
        else:
            print(f"❌ PDF not found at: {output_pdf}")
            return False
    
    finally:
        # Cleanup temporary ODT
        try:
            os.remove(odt_file)
        except:
            pass

def markdown_to_html(md_file: str) -> str:
    """
    Simple Markdown to HTML conversion (fallback).
    Uses basic regex patterns.
    """
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Basic HTML wrapper with CSS styling
    html = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report</title>
    <style>
        body {
            font-family: 'Liberation Serif', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
            background: #fff;
        }
        h1 { font-size: 28px; margin: 20px 0; color: #1a1a1a; border-bottom: 3px solid #007acc; padding-bottom: 10px; }
        h2 { font-size: 22px; margin: 15px 0 10px 0; color: #333; }
        h3 { font-size: 18px; margin: 12px 0 8px 0; color: #555; }
        p { margin: 10px 0; text-align: justify; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f5f5f5; font-weight: bold; }
        tr:nth-child(even) { background: #f9f9f9; }
        ul, ol { margin: 10px 0; padding-left: 20px; }
        li { margin: 5px 0; }
        strong { color: #007acc; }
        em { font-style: italic; color: #666; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Liberation Mono', monospace; }
        .metadata { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }
        .metadata p { margin: 3px 0; }
    </style>
</head>
<body>
"""
    
    # Basic markdown conversion
    lines = md_content.split('\n')
    in_code_block = False
    
    for line in lines:
        if line.startswith('```'):
            in_code_block = not in_code_block
            html += '<pre><code>' if in_code_block else '</code></pre>'
            continue
        
        if in_code_block:
            html += line + '\n'
            continue
        
        # Headers
        if line.startswith('# '):
            html += f'<h1>{line[2:]}</h1>\n'
        elif line.startswith('## '):
            html += f'<h2>{line[3:]}</h2>\n'
        elif line.startswith('### '):
            html += f'<h3>{line[4:]}</h3>\n'
        # Lists
        elif line.startswith('- '):
            html += f'<li>{line[2:]}</li>\n'
        elif line.startswith('* '):
            html += f'<li>{line[2:]}</li>\n'
        # Tables (skip, too complex)
        elif line.startswith('|'):
            html += f'<p><code>{line}</code></p>\n'
        # Paragraphs
        elif line.strip():
            # Basic inline formatting
            line = line.replace('**', '<strong>').replace('**', '</strong>')
            line = line.replace('*', '<em>').replace('*', '</em>')
            line = line.replace('`', '<code>').replace('`', '</code>')
            html += f'<p>{line}</p>\n'
        else:
            html += '\n'
    
    html += """
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: markdown-to-libreoffice-pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_pdf = sys.argv[2]
    
    success = markdown_to_libreoffice_pdf(md_file, output_pdf)
    sys.exit(0 if success else 1)
