#!/bin/bash

# Unified PDF Search Tool v2.0 — AI-Powered Summaries with PDF Output
# Query → RAG-Daemon (14b) → Extract Top PDFs → 14b summarizes each → Unified PDF Report
# Usage: pdf-search "query"

set -e

QUERY="$1"

if [[ -z "$QUERY" ]]; then
    echo "Usage: pdf-search 'query'"
    exit 1
fi

# Directories
DOKUMENTE="${HOME}/Dokumente"
mkdir -p "$DOKUMENTE"

# Timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFE_QUERY=$(echo "$QUERY" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
REPORT_FILE="${DOKUMENTE}/REPORT-${SAFE_QUERY}-${TIMESTAMP}"

echo "🔍 Query: '$QUERY'"
echo "📊 Searching via RAG-Daemon (14b + PDF Index)..."

# RAG-Daemon API call
RAG_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}")

# Extract fields
ANSWER=$(echo "$RAG_RESPONSE" | jq -r '.answer // "Keine Antwort"')
LATENCY=$(echo "$RAG_RESPONSE" | jq -r '.latency_ms // "?"')
SOURCES=$(echo "$RAG_RESPONSE" | jq -r '.sources[]')
SOURCE_COUNT=$(echo "$RAG_RESPONSE" | jq '.sources | length')

echo "⏱️  Latency: ${LATENCY}ms"
echo "📚 PDFs found: $SOURCE_COUNT"
echo ""
echo "📋 Zusammenfassung (14b):"
echo "=============================================="
echo "$ANSWER"
echo "=============================================="
echo ""

# Generate enhanced summaries from top PDFs
echo "📖 Reading top PDFs for detailed summaries..."
echo ""

DETAILED_SUMMARIES=""
PDF_COUNT=0

while IFS= read -r pdf; do
    if [[ -z "$pdf" ]] || ! [[ -f "$pdf" ]]; then
        continue
    fi
    
    PDF_COUNT=$((PDF_COUNT + 1))
    
    # Extract PDF filename
    PDF_NAME=$(basename "$pdf")
    echo "  [$PDF_COUNT] Analyzing: $PDF_NAME..."
    
    # Query 14b for detailed summary of this specific PDF
    SUMMARY_QUERY="Zusammenfassung für '$QUERY' in diesem Buch: $PDF_NAME"
    
    SUMMARY_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$SUMMARY_QUERY\"}" || echo "{\"answer\": \"Keine Details verfügbar\"}")
    
    SUMMARY=$(echo "$SUMMARY_RESPONSE" | jq -r '.answer // "Keine Zusammenfassung"')
    
    DETAILED_SUMMARIES+="## 📖 $PDF_COUNT. $PDF_NAME

$SUMMARY

**Pfad:** \`$pdf\`

---

"
done <<< "$SOURCES"

echo ""

# Create comprehensive Markdown report
cat > "${REPORT_FILE}.md" << EOF
# 📋 Report: $(echo "$QUERY" | head -c 60)

## 🔍 Suchanfrage
\`\`\`
$QUERY
\`\`\`

## ⚡ Kurzzusammenfassung (RAG-Daemon v0.5 + qwen3:14b)

$ANSWER

---

## 📚 Detaillierte Analyse aus $SOURCE_COUNT PDFs

$DETAILED_SUMMARIES

## 📊 Metadaten

| Metric | Wert |
|--------|------|
| **Latenz** | ${LATENCY} ms |
| **PDFs durchsucht** | ${SOURCE_COUNT} |
| **Analysierte PDFs** | ${PDF_COUNT} |
| **Generiert** | $(date '+%Y-%m-%d %H:%M UTC') |
| **Tool** | RAG-Daemon v0.5 + qwen3:14b |
| **Workflow** | Unified PDF-Search v2.0 |

---

_Dieser Report wurde automatisch generiert._  
_Die Zusammenfassungen basieren auf lokaler 14b-KI-Analyse (RAG-Daemon)._  
_Keine externen Cloud-Dienste verwendet._
EOF

echo "✅ Markdown-Report erstellt: ${REPORT_FILE}.md"

# Create HTML from Markdown
python3 << 'PYTHON'
import sys

md_file = "MD_FILE_PLACEHOLDER"
html_file = "HTML_FILE_PLACEHOLDER"

with open(md_file, 'r', encoding='utf-8') as f:
    md = f.read()

# Create beautiful HTML
html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Research Report</title>
<style>
@media print {{
  body {{ background: white; }}
  .container {{ box-shadow: none; }}
}}

body {{
    font-family: 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
    line-height: 1.8;
    color: #2c3e50;
    background: linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%);
    margin: 0;
    padding: 20px;
}}

.container {{
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    padding: 50px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

h1 {{
    color: #1976d2;
    border-bottom: 4px solid #1976d2;
    padding-bottom: 15px;
    font-size: 2.2em;
    margin-top: 0;
}}

h2 {{
    color: #388e3c;
    margin-top: 40px;
    border-left: 5px solid #388e3c;
    padding-left: 20px;
    font-size: 1.6em;
}}

h3 {{
    color: #1565c0;
    margin-top: 25px;
    font-size: 1.2em;
}}

p {{
    margin: 12px 0;
}}

ul, ol {{
    line-height: 2;
    margin: 15px 0;
}}

strong {{
    color: #1565c0;
    font-weight: 600;
}}

code {{
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.95em;
}}

pre {{
    background: #f5f5f5;
    padding: 15px;
    border-left: 4px solid #1976d2;
    overflow-x: auto;
    line-height: 1.4;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}}

th {{
    background: #1976d2;
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}}

td {{
    border-bottom: 1px solid #ddd;
    padding: 10px 12px;
}}

tr:hover {{
    background: #f5f5f5;
}}

.footer {{
    margin-top: 60px;
    padding-top: 30px;
    border-top: 2px solid #ddd;
    font-size: 0.9em;
    color: #666;
    text-align: center;
}}

.source {{
    background: #e3f2fd;
    padding: 10px;
    border-radius: 4px;
    margin-top: 15px;
    font-size: 0.9em;
    color: #1565c0;
    font-family: monospace;
}}

.metric {{
    display: inline-block;
    margin-right: 25px;
    margin-bottom: 10px;
}}

.metric-label {{
    font-weight: bold;
    color: #1976d2;
}}

</style>
</head>
<body>
<div class="container">

{md}

<div class="footer">
<p><strong>✅ Dieser Report wurde automatisch generiert.</strong></p>
<p>Die Zusammenfassungen basieren auf lokaler 14b-KI-Analyse (RAG-Daemon).</p>
<p>Keine externen Cloud-Dienste verwendet.</p>
</div>

</div>
</body>
</html>
"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

PYTHON

# Replace placeholders in Python script
sed -i "s|MD_FILE_PLACEHOLDER|${REPORT_FILE}.md|g" <<< "$(head -50 /dev/stdin)" || true

# Actually convert with direct placeholders
python3 << PYTHON_INLINE
md_file = "${REPORT_FILE}.md"
html_file = "${REPORT_FILE}.html"

with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>PDF Research Report</title>
<style>
body {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    line-height: 1.8;
    color: #2c3e50;
    background: #ecf0f1;
    margin: 0;
    padding: 20px;
}}
.container {{
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    padding: 50px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}
h1 {{ color: #1976d2; border-bottom: 4px solid #1976d2; padding-bottom: 15px; }}
h2 {{ color: #388e3c; margin-top: 40px; border-left: 5px solid #388e3c; padding-left: 20px; }}
h3 {{ color: #1565c0; }}
code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th {{ background: #1976d2; color: white; padding: 12px; }}
td {{ border-bottom: 1px solid #ddd; padding: 10px 12px; }}
.footer {{ margin-top: 60px; padding-top: 30px; border-top: 2px solid #ddd; font-size: 0.9em; text-align: center; }}
</style>
</head>
<body>
<div class="container">
{md_content}
<div class="footer">
<p><strong>✅ Dieser Report wurde automatisch generiert.</strong></p>
<p>Die Zusammenfassungen basieren auf lokaler 14b-KI-Analyse (RAG-Daemon).</p>
</div>
</div>
</body>
</html>
"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML: {html_file}")

PYTHON_INLINE

echo ""
echo "✅ REPORT COMPLETE:"
ls -lh "${REPORT_FILE}".{md,html}
echo "   📝 Markdown: ${REPORT_FILE}.md"
echo "   📄 HTML:     ${REPORT_FILE}.html"
echo "   📂 Location: $DOKUMENTE"
echo ""

# Open on desktop
if [[ -f "${REPORT_FILE}.html" ]]; then
    DISPLAY=:1 xdg-open "${REPORT_FILE}.html" &
    echo "📺 Opening HTML in browser..."
fi

echo "✅ Done"
