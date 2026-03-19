#!/usr/bin/env python3
"""
Enhance markdown with Wikipedia section.
Direct Python integration (no bash wrapper needed).
"""

import sys
import json
import subprocess
from pathlib import Path

def add_wikipedia_to_md(query: str, md_file: str, timeout: int = 30):
    """
    Fetch Wikipedia article and add to markdown file.
    
    Args:
        query: Search query
        md_file: Path to markdown file
        timeout: Max seconds to wait
    """
    
    md_path = Path(md_file)
    if not md_path.exists():
        return False
    
    script_dir = Path(__file__).parent.parent
    
    # Fetch Wikipedia using kiwix-fetch.py
    try:
        result = subprocess.run(
            [str(script_dir / ".venv" / "bin" / "python3"),
             str(script_dir / "kiwix-fetch.py"),
             query],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return False
        
        # Extract JSON
        output = result.stdout
        json_start = output.find("---JSON---")
        if json_start == -1:
            return False
        
        json_text = output[json_start + len("---JSON---"):].strip()
        wiki_data = json.loads(json_text)
        
    except Exception as e:
        print(f"⚠️  Wikipedia fetch failed: {e}", file=sys.stderr)
        return False
    
    title = wiki_data.get('title', '')
    summary = wiki_data.get('summary', '')
    content = wiki_data.get('content', '')
    
    if not title:
        return False
    
    # Use full content if available (more comprehensive)
    wiki_text = content if content else summary
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create Wikipedia section
    wiki_section = f"""## 🌐 Wikipedia-Ergänzung (Kiwix Offline)

**{title}**

{wiki_text}

_Quelle: Wikipedia (Kiwix Offline)_

---

"""
    
    # Insert before "## 📊 Metadaten"
    if "## 📊 Metadaten" in md_content:
        md_content = md_content.replace(
            "## 📊 Metadaten",
            wiki_section + "## 📊 Metadaten",
            1
        )
    else:
        # Fallback
        md_content = md_content.rstrip() + "\n\n" + wiki_section
    
    # Write back
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: enhance-md-with-wikipedia.py <query> <md-file>")
        sys.exit(1)
    
    query = sys.argv[1]
    md_file = sys.argv[2]
    
    success = add_wikipedia_to_md(query, md_file)
    sys.exit(0 if success else 1)
