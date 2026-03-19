#!/usr/bin/env python3
"""
formatter-v4.py — HTML + Markdown Report Generation

Converts synthesized content into beautiful HTML and Markdown reports.
Supports 3 content types: Recipe, Technical, Narrative.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def format_recipe_html(item, index):
    """Format recipe content as HTML."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    html = f"""
    <section class="recipe">
        <h2>🍳 Rezept {index}: {ext.get('name', 'Unnamed Recipe')}</h2>
        <div class="recipe-content">
"""
    
    # Ingredients
    if ext.get("ingredients"):
        html += '<div class="ingredients"><h3>Zutaten</h3><ul>'
        for ing in ext["ingredients"]:
            html += f'<li>{ing}</li>'
        html += '</ul></div>'
    
    # Steps
    if ext.get("steps"):
        html += '<div class="steps"><h3>Anleitung</h3><ol>'
        for step in ext["steps"]:
            html += f'<li>{step}</li>'
        html += '</ol></div>'
    
    source_link = f'<a href="file://{pdf_path}">{pdf_name}</a>' if pdf_path else pdf_name
    html += f"""
        </div>
        <p class="source">📄 Quelle: {source_link}</p>
    </section>
"""
    
    return html


def format_technical_html(item, index):
    """Format technical content as HTML."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    html = f"""
    <section class="concept">
        <h2>🧠 Konzept {index}: {ext.get('title', 'Technical Content')}</h2>
        <div class="concept-content">
"""
    
    # Definitions
    if ext.get("definitions"):
        html += '<div class="definitions"><h3>Definitionen</h3>'
        for defn in ext["definitions"]:
            html += f'<p>{defn}</p>'
        html += '</div>'
    
    # Key Points
    if ext.get("key_points"):
        html += '<div class="key-points"><h3>Wichtige Punkte</h3><ul>'
        for point in ext["key_points"]:
            html += f'<li>{point}</li>'
        html += '</ul></div>'
    
    source_link = f'<a href="file://{pdf_path}">{pdf_name}</a>' if pdf_path else pdf_name
    html += f"""
        </div>
        <p class="source">📄 Quelle: {source_link}</p>
    </section>
"""
    
    return html


def format_narrative_html(item, index):
    """Format narrative content as HTML."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    html = f"""
    <section class="essay">
        <h2>📝 Essay {index}: {ext.get('title', 'Narrative Content')}</h2>
        <div class="essay-content">
"""
    
    # Summary
    if ext.get("summary"):
        html += f'<div class="summary"><h3>Zusammenfassung</h3><p>{ext["summary"]}</p></div>'
    
    # Quotes
    if ext.get("quotes"):
        html += '<div class="quotes"><h3>Zitate</h3>'
        for quote in ext["quotes"]:
            html += f'<blockquote>"{quote}"</blockquote>'
        html += '</div>'
    
    # Concepts
    if ext.get("concepts"):
        html += '<div class="concepts"><h3>Schlüsselkonzepte</h3><ul>'
        for concept in ext["concepts"]:
            html += f'<li>{concept}</li>'
        html += '</ul></div>'
    
    source_link = f'<a href="file://{pdf_path}">{pdf_name}</a>' if pdf_path else pdf_name
    html += f"""
        </div>
        <p class="source">📄 Quelle: {source_link}</p>
    </section>
"""
    
    return html


def format_recipe_md(item, index):
    """Format recipe content as Markdown."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    md = f"## 🍳 Rezept {index}: {ext.get('name', 'Unnamed Recipe')}\n\n"
    
    # Ingredients
    if ext.get("ingredients"):
        md += "### Zutaten\n"
        for ing in ext["ingredients"]:
            md += f"- {ing}\n"
        md += "\n"
    
    # Steps
    if ext.get("steps"):
        md += "### Anleitung\n"
        for i, step in enumerate(ext["steps"], 1):
            md += f"{i}. {step}\n"
        md += "\n"
    
    # Source with optional link
    if pdf_path:
        source_text = f"[{pdf_name}]({pdf_path})"
    else:
        source_text = pdf_name
    
    md += f"**📄 Quelle:** {source_text}\n\n---\n\n"
    
    return md


def format_technical_md(item, index):
    """Format technical content as Markdown."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    md = f"## 🧠 Konzept {index}: {ext.get('title', 'Technical Content')}\n\n"
    
    # Definitions
    if ext.get("definitions"):
        md += "### Definitionen\n"
        for defn in ext["definitions"]:
            md += f"{defn}\n\n"
    
    # Key Points
    if ext.get("key_points"):
        md += "### Wichtige Punkte\n"
        for point in ext["key_points"]:
            md += f"- {point}\n"
        md += "\n"
    
    # Source with optional link
    if pdf_path:
        source_text = f"[{pdf_name}]({pdf_path})"
    else:
        source_text = pdf_name
    
    md += f"**📄 Quelle:** {source_text}\n\n---\n\n"
    
    return md


def format_narrative_md(item, index):
    """Format narrative content as Markdown."""
    ext = item.get("extracted", {})
    pdf_name = item.get('pdf_name', 'Unknown')
    pdf_path = item.get('pdf_path', '')
    
    md = f"## 📝 Essay {index}: {ext.get('title', 'Narrative Content')}\n\n"
    
    # Summary
    if ext.get("summary"):
        md += f"### Zusammenfassung\n{ext['summary']}\n\n"
    
    # Quotes
    if ext.get("quotes"):
        md += "### Zitate\n"
        for quote in ext["quotes"]:
            md += f"> \"{quote}\"\n\n"
    
    # Concepts
    if ext.get("concepts"):
        md += "### Schlüsselkonzepte\n"
        for concept in ext["concepts"]:
            md += f"- {concept}\n"
        md += "\n"
    
    # Source with optional link
    if pdf_path:
        source_text = f"[{pdf_name}]({pdf_path})"
    else:
        source_text = pdf_name
    
    md += f"**📄 Quelle:** {source_text}\n\n---\n\n"
    
    return md


def generate_html_report(query, synthesized_list):
    """Generate complete HTML report."""
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report: {query}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{ max-width: 900px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; margin-bottom: 10px; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; margin-bottom: 15px; }}
        h3 {{ color: #7f8c8d; margin-top: 15px; margin-bottom: 10px; }}
        .metadata {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 30px; font-size: 14px; }}
        section {{ margin-bottom: 40px; padding: 20px; background: #fafafa; border-left: 4px solid #3498db; }}
        ul, ol {{ margin-left: 20px; margin-top: 10px; }}
        li {{ margin-bottom: 8px; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; margin: 15px 0; font-style: italic; color: #555; }}
        .source {{ margin-top: 15px; font-size: 12px; color: #999; font-style: italic; }}
        .source a {{ color: #3498db; text-decoration: none; }}
        .source a:hover {{ text-decoration: underline; }}
        .recipe {{ border-left-color: #27ae60; }}
        .concept {{ border-left-color: #e74c3c; }}
        .essay {{ border-left-color: #f39c12; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Report: {query}</h1>
        <div class="metadata">
            <p>Suchanfrage: <strong>{query}</strong></p>
            <p>Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>PDFs durchsucht: <strong>{len(synthesized_list)}</strong></p>
        </div>
"""
    
    recipe_idx = 1
    technical_idx = 1
    narrative_idx = 1
    
    for item in synthesized_list:
        content_type = item.get("content_type")
        
        if content_type == "recipe":
            html += format_recipe_html(item, recipe_idx)
            recipe_idx += 1
        elif content_type == "technical":
            html += format_technical_html(item, technical_idx)
            technical_idx += 1
        elif content_type == "narrative":
            html += format_narrative_html(item, narrative_idx)
            narrative_idx += 1
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def generate_markdown_report(query, synthesized_list):
    """Generate complete Markdown report."""
    md = f"# 📊 Report: {query}\n\n"
    md += f"**Suchanfrage:** {query}  \n"
    md += f"**Zeitstempel:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    md += f"**PDFs durchsucht:** {len(synthesized_list)}\n\n"
    md += "---\n\n"
    
    recipe_idx = 1
    technical_idx = 1
    narrative_idx = 1
    
    for item in synthesized_list:
        content_type = item.get("content_type")
        
        if content_type == "recipe":
            md += format_recipe_md(item, recipe_idx)
            recipe_idx += 1
        elif content_type == "technical":
            md += format_technical_md(item, technical_idx)
            technical_idx += 1
        elif content_type == "narrative":
            md += format_narrative_md(item, narrative_idx)
            narrative_idx += 1
    
    return md


def main():
    """
    Main entry point.
    Usage: formatter-v4.py <json_input> <query> <output_dir>
    """
    if len(sys.argv) < 4:
        print("Usage: formatter-v4.py <json_input> <query> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    query = sys.argv[2]
    output_dir = sys.argv[3]
    
    try:
        with open(input_file) as f:
            data = json.load(f)
        
        synthesized_list = data.get("results", [])
        
        # Generate reports
        html_report = generate_html_report(query, synthesized_list)
        md_report = generate_markdown_report(query, synthesized_list)
        
        # Write files
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        html_file = output_path / f"REPORT-{query}-{timestamp}.html"
        md_file = output_path / f"REPORT-{query}-{timestamp}.md"
        pdf_file = output_path / f"REPORT-{query}-{timestamp}.pdf"
        
        with open(html_file, 'w') as f:
            f.write(html_report)
        with open(md_file, 'w') as f:
            f.write(md_report)
        
        print(f"✓ HTML Report: {html_file}")
        print(f"✓ Markdown Report: {md_file}")
        
        # Convert HTML to PDF using wkhtmltopdf (preferred)
        try:
            import subprocess
            subprocess.run([
                "/usr/bin/wkhtmltopdf",
                "--quiet",
                str(html_file),
                str(pdf_file)
            ], check=False, timeout=30, capture_output=True)
            if pdf_file.exists():
                print(f"✓ PDF Report: {pdf_file}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback: use pandoc
            try:
                subprocess.run([
                    "pandoc",
                    str(md_file),
                    "-o", str(pdf_file),
                    "--pdf-engine=pdflatex",
                    "--metadata", "title=Report"
                ], check=False, timeout=30, capture_output=True)
                if pdf_file.exists():
                    print(f"✓ PDF Report (pandoc): {pdf_file}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Final fallback: LibreOffice
                try:
                    subprocess.run([
                        "libreoffice",
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", str(output_path),
                        str(md_file)
                    ], check=False, timeout=30)
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass  # PDF conversion failed, markdown is OK
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
