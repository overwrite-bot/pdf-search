#!/bin/bash

# pdf-search-v2.sh — Extract REAL recipes from PDFs + RAG synthesis
# Combines actual recipe content with AI context

set -e

QUERY="$1"
CATEGORY="${2:-general}"
DOKUMENTE="$HOME/Dokumente"

[[ -z "$QUERY" ]] && {
    echo "Usage: pdf-search-v2.sh \"query\" [category]"
    exit 1
}

# File paths
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="${DOKUMENTE}/REPORT-$(echo "$QUERY" | tr ' ' '-' | cut -c1-40)-${TIMESTAMP}"
PDF_DB="/media/overwrite/Datenplatte 2/pdf-index.db"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ===== STEP 1: RAG Query for context =====
echo "🔍 Query: '$QUERY'"
echo "📂 Kategorie: $CATEGORY"
echo "📊 Searching via RAG-Daemon (14b + Hybrid Search + PDF Index)..."

RAG_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/ask \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$QUERY\"}" || echo '{"answer":"","sources":[]}')

ANSWER=$(echo "$RAG_RESPONSE" | jq -r '.answer // "Keine Antwort"')
SOURCES=$(echo "$RAG_RESPONSE" | jq -r '.sources[]? // empty' | head -5)

LATENCY=$(echo "$RAG_RESPONSE" | jq -r '.latency // "?"')
echo "⏱️  Latency: ${LATENCY}ms"

SOURCE_COUNT=$(echo "$SOURCES" | wc -l | tr -d ' ')
echo "📚 PDFs found: $SOURCE_COUNT"
echo ""
echo "📋 Zusammenfassung (14b):"
echo "=============================================="
echo "$ANSWER"
echo "=============================================="
echo ""

# ===== STEP 2: Extract actual recipes from top PDFs =====
echo "🍽️  Extracting recipes from top PDFs..."
echo ""

RECIPES_SECTION=""
PDF_COUNT=0
RECIPE_TOTAL=0

while IFS= read -r pdf_name; do
    [[ -z "$pdf_name" ]] && continue
    
    # Get full path from database
    pdf=$(sqlite3 "$PDF_DB" "SELECT fullpath FROM pdf_index WHERE filename = '${pdf_name//\'/\'\'}' LIMIT 1;" 2>/dev/null)
    
    [[ -z "$pdf" ]] || ! [[ -f "$pdf" ]] && continue
    
    PDF_COUNT=$((PDF_COUNT + 1))
    PDF_NAME=$(basename "$pdf")
    echo "  [$PDF_COUNT] Analyzing: $PDF_NAME..."
    
    # Extract PDF text
    PDF_TEXT=$(pdftotext "$pdf" - 2>/dev/null || echo "")
    
    if [[ -z "$PDF_TEXT" ]]; then
        echo "      ⚠️  Could not extract text"
        continue
    fi
    
    # Try to find recipes in text
    # Look for keywords: Rezept, Zutaten, Anleitung, Zubereitung
    if echo "$PDF_TEXT" | grep -iE "(rezept|zutaten|anleitung|zubereitung)" > /dev/null; then
        
        # Extract sections with recipes
        RECIPE_SECTIONS=$(echo "$PDF_TEXT" | \
            grep -iA 20 -E "^(rezept|## |### |---)" | \
            head -150)
        
        if [[ -n "$RECIPE_SECTIONS" ]]; then
            RECIPE_TOTAL=$((RECIPE_TOTAL + 1))
            
            RECIPES_SECTION+="## 📖 $PDF_COUNT. $PDF_NAME

\`\`\`
$RECIPE_SECTIONS
\`\`\`

---

"
        fi
    fi
    
    [[ $PDF_COUNT -ge 5 ]] && break
    
done <<< "$SOURCES"

echo ""

# ===== STEP 3: Create comprehensive Markdown report =====
cat > "${REPORT_FILE}.md" << EOF
# 🍳 Report: $(echo "$QUERY" | head -c 60)

## 🔍 Suchanfrage
\`\`\`
$QUERY
\`\`\`

---

## ⚡ Zusammenfassung (RAG + qwen3:14b)

$ANSWER

---

## 🍽️  Rezepte & Details aus den Quellen

$RECIPES_SECTION

---

## 📊 Metadaten

- **Gesucht:** $QUERY
- **Kategorie:** $CATEGORY
- **PDFs analysiert:** $PDF_COUNT
- **Rezepte gefunden:** $RECIPE_TOTAL
- **Zeitstempel:** $(date '+%Y-%m-%d %H:%M:%S')
- **Quelle:** RAG-Daemon v0.5 + qwen3:14b + PDF-Index

EOF

echo "✅ Markdown-Report erstellt: ${REPORT_FILE}.md"

# ===== STEP 4: Convert to professional PDF =====
echo ""
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
