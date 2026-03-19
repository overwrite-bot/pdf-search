#!/bin/bash

# pdf-search-fts5.sh — Direct FTS5 + Recipes (no RAG-Daemon)
# Bypasses RAG for MORE RELIABLE results

set -e

QUERY="$1"
CATEGORY="${2:-general}"
DOKUMENTE="$HOME/Dokumente"

[[ -z "$QUERY" ]] && {
    echo "Usage: pdf-search-fts5.sh \"query\" [category]"
    exit 1
}

# File paths
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="${DOKUMENTE}/REPORT-$(echo "$QUERY" | tr ' ' '-' | cut -c1-40)-${TIMESTAMP}"
PDF_DB="/media/overwrite/Datenplatte 2/pdf-index.db"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ===== STEP 1: Direct FTS5 Query (No RAG) =====
echo "🔍 Query: '$QUERY'"
echo "📂 Kategorie: $CATEGORY"
echo "📊 Searching via FTS5 PDF Index (Direct)..."
echo ""

# Build FTS5 query: "word1 OR word2 OR word3"
FTS5_QUERY=$(echo "$QUERY" | tr ' ' '\n' | grep -v '^$' | tr '\n' ' ' | sed 's/ / OR /g' | sed 's/ OR $//')

# Get top 10 PDFs with FTS5 matches
PDF_SOURCES=$(sqlite3 "$PDF_DB" "
SELECT p.filename 
FROM pdf_fts fts
JOIN pdf_index p ON fts.rowid = p.rowid
WHERE pdf_fts MATCH '$FTS5_QUERY'
ORDER BY rank
LIMIT 10;" 2>/dev/null || echo "")

SOURCE_COUNT=$(echo "$PDF_SOURCES" | wc -l | tr -d ' ')
echo "📚 PDFs found: $SOURCE_COUNT"
echo ""

if [[ -z "$PDF_SOURCES" ]]; then
    echo "⚠️  No PDFs found for: $QUERY"
    exit 1
fi

# ===== STEP 2: Extract recipes from PDFs =====
echo "🍽️  Extracting recipes from top PDFs..."
echo ""

RECIPES_SECTION=""
PDF_COUNT=0
RECIPE_TOTAL=0

while IFS= read -r pdf_name; do
    [[ -z "$pdf_name" ]] && continue
    
    # Get full path
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
    
    # Extract recipe-like content
    RECIPE_SECTIONS=$(echo "$PDF_TEXT" | \
        grep -iA 8 -E "(rezept|zutaten|anleitung|zubereitung)" | \
        head -300)
    
    if [[ -n "$RECIPE_SECTIONS" ]]; then
        RECIPE_TOTAL=$((RECIPE_TOTAL + 1))
        
        RECIPES_SECTION+="## 📖 $PDF_COUNT. $PDF_NAME

\`\`\`
$RECIPE_SECTIONS
\`\`\`

---

"
    fi
    
    [[ $PDF_COUNT -ge 10 ]] && break
    
done <<< "$PDF_SOURCES"

echo ""

# ===== STEP 3: Build Raw Markdown Report =====
RAW_MARKDOWN_REPORT="# 🍳 Report: $QUERY

## 🔍 Suchanfrage
\`\`\`
$QUERY
\`\`\`

---

## ✅ Gefundene PDFs: $SOURCE_COUNT

$RECIPES_SECTION

---

*Generiert: $(date '+%d.%m.%Y um %H:%M')*
"

# Save raw markdown
echo "$RAW_MARKDOWN_REPORT" > "${REPORT_FILE}-raw.md"
echo "✅ Raw Markdown erstellt: ${REPORT_FILE}-raw.md"

# ===== STEP 4: Format recipes with recipe-formatter =====
echo "📝 Formatiere Rezepte..."
python3 "$SCRIPT_DIR/scripts/recipe-formatter.py" "${REPORT_FILE}-raw.md" "${REPORT_FILE}.md" 2>/dev/null || {
    echo "⚠️  Formatting failed, using raw markdown"
    cp "${REPORT_FILE}-raw.md" "${REPORT_FILE}.md"
}
echo "✅ Formatiert: ${REPORT_FILE}.md"

# ===== STEP 5: Convert to PDF =====
python3 "$SCRIPT_DIR/scripts/pdf-design.py" "${REPORT_FILE}.md" "${REPORT_FILE}.pdf" 2>/dev/null || {
    echo "⚠️  PDF conversion failed, using markdown only"
}

echo ""
echo "✅ REPORT COMPLETE:"
ls -lh "${REPORT_FILE}".* | awk '{print "   " $NF}'

# Open in viewer
if command -v evince &>/dev/null; then
    DISPLAY=:1 evince "${REPORT_FILE}.pdf" >/dev/null 2>&1 &
    echo "📺 Opening PDF in evince..."
    sleep 1
fi

echo "   📝 Markdown: ${REPORT_FILE}.md"
echo "   📂 Location: $DOKUMENTE"
