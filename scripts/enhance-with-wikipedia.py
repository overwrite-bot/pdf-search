#!/usr/bin/env python3
"""
Post-process markdown report to add Wikipedia summary.
"""

import sys
import json
import subprocess
from pathlib import Path

def add_wikipedia_section(md_file: str, query: str):
    """Add Wikipedia section to markdown file"""
    
    # Get Wikipedia content
    try:
        script_dir = Path(__file__).parent.parent
        venv = script_dir / ".venv"
        
        result = subprocess.run(
            [str(venv / "bin" / "python3"), str(script_dir / "kiwix-fetch.py"), query],
            capture_output=True,
            text=True,
            timeout=45
        )
        
        if result.returncode != 0:
            return
        
        # Extract JSON
        output = result.stdout
        json_start = output.find("---JSON---")
        if json_start == -1:
            return
        
        json_text = output[json_start + len("---JSON---"):].strip()
        wiki_data = json.loads(json_text)
        
    except Exception as e:
        print(f"⚠️  Wikipedia not added: {e}", file=sys.stderr)
        return
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create Wikipedia section
    wiki_section = f"""
## 🌐 Wikipedia-Ergänzung (Kiwix Offline)

**{wiki_data.get('title', 'Wikipedia')}**

{wiki_data.get('summary', 'Zusammenfassung nicht verfügbar')}

_Quelle: {wiki_data.get('source', 'Wikipedia')}_

"""
    
    # Insert before "## 📊 Metadaten"
    if "## 📊 Metadaten" in md_content:
        md_content = md_content.replace(
            "## 📊 Metadaten",
            wiki_section + "\n## 📊 Metadaten"
        )
    else:
        # Fallback: add before final section
        md_content = md_content.rstrip() + "\n" + wiki_section
    
    # Write back
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Wikipedia section added", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: enhance-with-wikipedia.py <md-file> <query>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    query = sys.argv[2]
    
    add_wikipedia_section(md_file, query)
