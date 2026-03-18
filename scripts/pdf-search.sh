#!/bin/bash

# PDF-Search v3.0 — Universal PDF Analysis & Content Synthesis
# Supports: Recipes, How-To Guides, References, Data Tables, Technical Documentation
# Usage: pdf-search "your query here"

set -e

QUERY="$1"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "$QUERY" ]]; then
    echo "Usage: pdf-search 'query'"
    echo "Examples:"
    echo "  pdf-search 'Schweinenackenrezepte'"
    echo "  pdf-search 'Wie macht man Kimchi'"
    echo "  pdf-search 'Pilzbestimmung'"
    echo "  pdf-search 'Gärungstemperaturen'"
    echo "  pdf-search 'Brauerei-Kalibrierung'"
    exit 1
fi

# Directories
DOKUMENTE="${HOME}/Dokumente"
mkdir -p "$DOKUMENTE"

# Timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFE_QUERY=$(echo "$QUERY" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
REPORT_FILE="${DOKUMENTE}/REPORT-${SAFE_QUERY}-${TIMESTAMP}"
TEMP_EXTRACT="${DOKUMENTE}/.extract-${TIMESTAMP}.json"
TEMP_SYNTHESIS="${DOKUMENTE}/.synthesis-${TIMESTAMP}.json"

echo "🔍 Query: '$QUERY'"
echo "📊 Searching via RAG-Daemon (14b + PDF Index)..."

# ============================================================================
# PHASE 1: RAG-Daemon Query (find relevant PDFs)
# ============================================================================

RAG_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" || echo "{\"answer\": \"Error contacting RAG-Daemon\", \"sources\": [], \"latency_ms\": 0}")

ANSWER=$(echo "$RAG_RESPONSE" | jq -r '.answer // "Keine Antwort"')
LATENCY=$(echo "$RAG_RESPONSE" | jq -r '.latency_ms // "?"')
SOURCES=$(echo "$RAG_RESPONSE" | jq -r '.sources[]?' 2>/dev/null || echo "")
SOURCE_COUNT=$(echo "$RAG_RESPONSE" | jq '.sources | length' 2>/dev/null || echo 0)

echo "⏱️  Latency: ${LATENCY}ms"
echo "📚 PDFs found: $SOURCE_COUNT"

# ============================================================================
# PHASE 2: Content Extraction (all types)
# ============================================================================

echo ""
echo "📖 Extracting content from top PDFs..."

ALL_EXTRACTIONS="{\"extractions\": []}"
PDF_COUNT=0

while IFS= read -r pdf; do
    if [[ -z "$pdf" ]] || ! [[ -f "$pdf" ]]; then
        continue
    fi
    
    PDF_COUNT=$((PDF_COUNT + 1))
    [[ $PDF_COUNT -gt 5 ]] && break  # Limit to top 5
    
    PDF_NAME=$(basename "$pdf")
    echo "  [$PDF_COUNT] Extracting: $PDF_NAME..."
    
    # Call extract-content.py
    if extraction_json=$(python3 "${SKILL_DIR}/scripts/extract-content.py" "$pdf" "$QUERY" 2>/dev/null); then
        # Parse and add to all extractions
        content_type=$(echo "$extraction_json" | jq -r '.content_type // "unknown"')
        confidence=$(echo "$extraction_json" | jq '.confidence // 0.5')
        echo "      Type: $content_type (confidence: $confidence)"
        
        # Add to extraction collection
        ALL_EXTRACTIONS=$(echo "$ALL_EXTRACTIONS" | jq \
          --argjson item "$(echo "$extraction_json")" \
          '.extractions += [$item]')
    fi
done <<< "$SOURCES"

echo "$ALL_EXTRACTIONS" > "$TEMP_EXTRACT"

# ============================================================================
# PHASE 3: Content Synthesis (type-specific)
# ============================================================================

echo ""
echo "🧠 Synthesizing content with 14b..."

SYNTHESIS=$(python3 "${SKILL_DIR}/scripts/synthesize-content.py" \
  "$QUERY" "$TEMP_EXTRACT" 2>/dev/null || echo "$(jq -n --arg q "$QUERY" '{query: $q, synthesis: "Synthesis failed", content_type: "unknown", confidence: 0.0}')")

# Extract synthesis details
CONTENT_TYPE=$(echo "$SYNTHESIS" | jq -r '.content_type // "unknown"')
SYNTHESIZED_CONTENT=$(echo "$SYNTHESIS" | jq -r '.synthesis // ""')
SYNTHESIS_CONFIDENCE=$(echo "$SYNTHESIS" | jq '.confidence // 0.5')

echo "   Content Type: $CONTENT_TYPE"
echo "   Confidence: $SYNTHESIS_CONFIDENCE"

# ============================================================================
# PHASE 4: Generate Report
# ============================================================================

echo ""
echo "📝 Generating report..."

# Create markdown report — ONLY the direct RAG answer
cat > "${REPORT_FILE}.md" << EOF
# 📋 Report: $(echo "$QUERY" | head -c 60)

## 🔍 Suchanfrage
\`\`\`
$QUERY
\`\`\`

---

## 💡 Antwort

$ANSWER

---

## 📊 Metadaten

| Metric | Wert |
|--------|------|
| **Latenz** | ${LATENCY} ms |
| **PDFs durchsucht** | ${SOURCE_COUNT} |
| **Generiert** | $(date '+%Y-%m-%d %H:%M UTC') |
| **Tool** | RAG-Daemon v0.5 + qwen3:14b |

---

_Automatisch generiert mit PDF-Search v3.0._
EOF

echo "✅ Markdown created: ${REPORT_FILE}.md"

# ============================================================================
# PHASE 5: HTML Generation
# ============================================================================

python3 << PYTHON_INLINE
import os
md_file = "${REPORT_FILE}.md"
html_file = "${REPORT_FILE}.html"

with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Research Report - {os.path.basename(md_file)}</title>
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
    max-width: 1100px;
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
    word-break: break-word;
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

p, li {{
    margin: 12px 0;
    text-align: justify;
}}

ul, ol {{
    line-height: 2;
    margin: 15px 0;
    padding-left: 25px;
}}

strong {{
    color: #1565c0;
    font-weight: 600;
}}

em {{
    color: #666;
    font-style: italic;
}}

code {{
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.95em;
    color: #d73a49;
}}

pre {{
    background: #f5f5f5;
    padding: 15px;
    border-left: 4px solid #1976d2;
    overflow-x: auto;
    line-height: 1.4;
    border-radius: 4px;
    font-size: 0.9em;
}}

blockquote {{
    border-left: 4px solid #ddd;
    margin: 15px 0;
    padding-left: 15px;
    color: #666;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 0.95em;
}}

th {{
    background: #1976d2;
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    border: 1px solid #ccc;
}}

td {{
    border: 1px solid #ddd;
    padding: 10px 12px;
}}

tr:nth-child(even) {{
    background: #f9f9f9;
}}

tr:hover {{
    background: #f0f7ff;
}}

.footer {{
    margin-top: 60px;
    padding-top: 30px;
    border-top: 2px solid #ddd;
    font-size: 0.9em;
    color: #666;
    text-align: center;
}}

.metadata {{
    background: #e3f2fd;
    padding: 15px;
    border-radius: 4px;
    margin: 20px 0;
    border-left: 4px solid #1976d2;
}}

.badge {{
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.85em;
    font-weight: bold;
    margin: 0 5px 0 0;
}}

.badge-recipe {{
    background: #fff3e0;
    color: #e65100;
}}

.badge-howto {{
    background: #e8f5e9;
    color: #2e7d32;
}}

.badge-reference {{
    background: #f3e5f5;
    color: #6a1b9a;
}}

.badge-data {{
    background: #e0f2f1;
    color: #00695c;
}}

.badge-technical {{
    background: #fce4ec;
    color: #c2185b;
}}

hr {{
    border: none;
    border-top: 2px solid #ddd;
    margin: 40px 0;
}}

</style>
</head>
<body>
<div class="container">

{md_content}

<div class="footer">
<p><strong>✅ Dieser Report wurde automatisch mit PDF-Search v3.0 generiert.</strong></p>
<p>Intelligente Inhaltsextraktion + Synthese mit lokaler 14b-KI (RAG-Daemon).</p>
<p>Keine externen Cloud-Dienste verwendet. 100% Privacy. 0% Kosten.</p>
</div>

</div>
</body>
</html>
"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML: {html_file}")

PYTHON_INLINE

# ============================================================================
# PHASE 6: Output & Display
# ============================================================================

echo ""
echo "✅ REPORT COMPLETE:"
ls -lh "${REPORT_FILE}".{md,html} 2>/dev/null || echo "(Files may not exist if there was an error)"

echo ""
echo "📂 Saved to: $DOKUMENTE"
echo "   📝 Markdown: $(basename ${REPORT_FILE}.md)"
echo "   📄 HTML:     $(basename ${REPORT_FILE}.html)"

# Open in browser
if [[ -f "${REPORT_FILE}.html" ]]; then
    DISPLAY=:1 xdg-open "${REPORT_FILE}.html" &
    echo "   🌐 Opening in browser..."
fi

# Cleanup temp files
rm -f "$TEMP_EXTRACT" "$TEMP_SYNTHESIS" 2>/dev/null

echo ""
echo "✅ Done (v3.0 framework)"
