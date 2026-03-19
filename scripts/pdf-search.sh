#!/bin/bash
# Unified PDF Search Tool v2.1 — AI-Powered Summaries with PDF Output
# Query → RAG-Daemon (14b) → Extract Top PDFs → 14b summarizes → PDF Report
set -e

QUERY="$1"
CATEGORY="${2:-all}"  # Optional: all, tech, cooking, esoterik, philosophy, health

[[ -z "$QUERY" ]] && { echo "Usage: pdf-search.sh 'query' [category]"; echo "Categories: all, tech, cooking, esoterik, philosophy, health"; exit 1; }

DOKUMENTE="/home/overwrite/Dokumente"
mkdir -p "$DOKUMENTE"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFE_QUERY=$(echo "$QUERY" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
REPORT_FILE="${DOKUMENTE}/REPORT-${SAFE_QUERY}-${TIMESTAMP}"

echo "🔍 Query: '$QUERY'"
[[ "$CATEGORY" != "all" ]] && echo "📂 Kategorie: $CATEGORY"
echo "📊 Searching via RAG-Daemon (14b + Hybrid Search + PDF Index)..."

# Enhanced RAG-Daemon call with hybrid search weights + optional category filter
# Weights: 80% Keywords, 20% Semantic (prioritize exact matches)
PAYLOAD="{\"query\": \"$QUERY\", \"hybrid_weights\": {\"bm25\": 0.8, \"semantic\": 0.2}}"
[[ "$CATEGORY" != "all" ]] && PAYLOAD="{\"query\": \"$QUERY\", \"category\": \"$CATEGORY\", \"hybrid_weights\": {\"bm25\": 0.8, \"semantic\": 0.2}}"

RAG_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

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
echo "📖 Reading top PDFs for detailed summaries..."
echo ""

DETAILED_SUMMARIES=""
PDF_COUNT=0
PDF_DB="/media/overwrite/Datenplatte 2/pdf-index.db"

while IFS= read -r pdf_name; do
    [[ -z "$pdf_name" ]] && continue
    
    pdf=$(sqlite3 "$PDF_DB" "SELECT fullpath FROM pdf_index WHERE filename = '${pdf_name//\'/\'\'}' LIMIT 1;" 2>/dev/null)
    
    [[ -z "$pdf" ]] || ! [[ -f "$pdf" ]] && continue
    
    PDF_COUNT=$((PDF_COUNT + 1))
    PDF_NAME=$(basename "$pdf")
    echo "  [$PDF_COUNT] Analyzing: $PDF_NAME..."
    
    SUMMARY_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"Zusammenfassung für '$QUERY' in diesem Buch: $PDF_NAME\"}" || echo "{\"answer\": \"Keine Details verfügbar\"}")
    
    SUMMARY=$(echo "$SUMMARY_RESPONSE" | jq -r '.answer // "Keine Zusammenfassung"')
    
    DETAILED_SUMMARIES+="## 📖 $PDF_COUNT. $PDF_NAME

$SUMMARY

**Pfad:** \`$pdf\`

---

"
done <<< "$SOURCES"

echo ""

# Create Markdown report
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
| **Workflow** | Unified PDF-Search v2.1 |

---

## 🌐 Zusätzliche Ressourcen

**Wikipedia offline (Kiwix):**
- [Suche nach \"$QUERY\"](http://localhost:8080/search?pattern=$(echo "$QUERY" | sed 's/ /+/g'))
- Verfügbar: Offline Wikipedia Deutsch (49 GB, aktuell)

---

_Dieser Report wurde automatisch generiert._  
_Die Zusammenfassungen basieren auf lokaler 14b-KI-Analyse (RAG-Daemon)._  
_Keine externen Cloud-Dienste verwendet._
EOF

echo "✅ Markdown-Report erstellt: ${REPORT_FILE}.md"

# Add Wikipedia summary using Python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
timeout 35 python3 "$SCRIPT_DIR/scripts/enhance-md-with-wikipedia.py" "$QUERY" "${REPORT_FILE}.md" 2>/dev/null &

# Convert to PDF via pdf-design.py (colorful, professional)
export REPORT_FILE
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$SCRIPT_DIR/scripts/pdf-design.py" "${REPORT_FILE}.md" "${REPORT_FILE}.pdf"

echo ""
echo "✅ REPORT COMPLETE:"
if [[ -f "${REPORT_FILE}.pdf" ]]; then
    ls -lh "${REPORT_FILE}.pdf"
    echo "   📋 PDF: ${REPORT_FILE}.pdf"
    DISPLAY=:1 evince "${REPORT_FILE}.pdf" 2>/dev/null &
    echo "📺 Opening PDF in evince..."
fi
echo "   📝 Markdown: ${REPORT_FILE}.md"
echo "   📂 Location: $DOKUMENTE"
