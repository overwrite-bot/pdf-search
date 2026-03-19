#!/bin/bash

# pdf-search.sh — Universal Content Extraction (v4.0)
# Supports: Recipes, Technical Content, Narratives
# Uses: FTS5 + extract-content-v4 + synthesize-content-v4 (14b) + formatter-v4

set -e

QUERY="$1"
CATEGORY="${2:-general}"
DOKUMENTE="$HOME/Dokumente"

[[ -z "$QUERY" ]] && {
    echo "Usage: pdf-search \"query\" [category]"
    exit 1
}

# File paths
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="${DOKUMENTE}/REPORT-$(echo "$QUERY" | tr ' ' '-' | cut -c1-40)-${TIMESTAMP}"
PDF_DB="/media/overwrite/Datenplatte 2/pdf-index.db"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ===== STEP 0: Validate Dependencies =====
command -v pdftotext &>/dev/null || { echo "❌ pdftotext not found"; exit 1; }
command -v sqlite3 &>/dev/null || { echo "❌ sqlite3 not found"; exit 1; }
command -v python3 &>/dev/null || { echo "❌ python3 not found"; exit 1; }

# ===== STEP 1: FTS5 Query =====
echo "🔍 Query: '$QUERY'"
echo "📂 Kategorie: $CATEGORY"
echo "📊 Searching via FTS5 PDF Index..."
echo ""

# Build FTS5 query
FTS5_QUERY=$(echo "$QUERY" | tr ' ' '\n' | grep -v '^$' | sed 's/*/\\*/' | tr '\n' ' ' | sed 's/ / OR /g' | sed 's/ OR $//')

# Get top 10 PDFs
PDF_SOURCES=$(sqlite3 "$PDF_DB" "
SELECT p.filename 
FROM pdf_fts fts
JOIN pdf_index p ON fts.rowid = p.rowid
WHERE pdf_fts MATCH '$FTS5_QUERY'
ORDER BY rank
LIMIT 10;" 2>/dev/null || echo "")

SOURCE_COUNT=$(echo "$PDF_SOURCES" | grep -c . || echo 0)
echo "📚 PDFs found: $SOURCE_COUNT"
echo ""

[[ $SOURCE_COUNT -eq 0 ]] && {
    echo "⚠️  No PDFs found for: $QUERY"
    exit 1
}

# ===== STEP 2: Extract PDF Text =====
echo "🍽️  Extracting text from top PDFs..."
echo ""

PDF_JSON_INPUT="/tmp/pdf-input-$TIMESTAMP.json"
PDF_JSON_ARRAY="["

PDF_COUNT=0
while IFS= read -r pdf_name; do
    [[ -z "$pdf_name" ]] && continue
    
    # Get full path
    pdf=$(sqlite3 "$PDF_DB" "SELECT fullpath FROM pdf_index WHERE filename = '${pdf_name//\'/\'\'}' LIMIT 1;" 2>/dev/null)
    
    [[ -z "$pdf" ]] || ! [[ -f "$pdf" ]] && continue
    
    PDF_COUNT=$((PDF_COUNT + 1))
    PDF_NAME=$(basename "$pdf")
    echo "  [$PDF_COUNT] Analyzing: $PDF_NAME..."
    
    # Extract PDF text (7000 chars = even better coverage, skip first 2000 chars metadata)
    # Use iconv to fix encoding issues
    # H1 Experiment: Longer extraction window
    PDF_TEXT=$(pdftotext "$pdf" - 2>/dev/null | \
        iconv -f UTF-8 -t UTF-8 -c | \
        head -c 7000 || echo "")
    
    [[ -z "$PDF_TEXT" ]] && {
        echo "      ⚠️  Could not extract text"
        continue
    }
    
    # Escape for JSON (with error handling for malformed UTF-8)
    PDF_TEXT_ESCAPED=$(echo "$PDF_TEXT" | python3 -c "import sys, json; text = sys.stdin.read(); print(json.dumps(text))" 2>/dev/null || echo '""')
    
    # Add to array (include full path for source links)
    [[ $PDF_COUNT -gt 1 ]] && PDF_JSON_ARRAY+=","
    PDF_PATH_ESCAPED=$(python3 -c "import json; print(json.dumps('$pdf'))")
    PDF_JSON_ARRAY+="{\"name\": \"$PDF_NAME\", \"path\": $PDF_PATH_ESCAPED, \"text\": $PDF_TEXT_ESCAPED}"
    
    [[ $PDF_COUNT -ge 10 ]] && break
    
done <<< "$PDF_SOURCES"

PDF_JSON_ARRAY+="]"
echo "{\"pdfs\": $PDF_JSON_ARRAY}" > "$PDF_JSON_INPUT"
echo ""

# ===== STEP 3: Extract Content (Heuristic) =====
echo "🔄 Phase 1: Content Type Detection & Extraction..."
EXTRACTED_JSON="/tmp/extracted-$TIMESTAMP.json"
python3 "$SCRIPT_DIR/scripts/extract-content-v4.py" "$PDF_JSON_INPUT" > "$EXTRACTED_JSON" 2>/dev/null || {
    echo "❌ Extraction failed"
    rm -f "$PDF_JSON_INPUT"
    exit 1
}
echo "✅ Content types identified"

# ===== STEP 4: Synthesize with Ollama (14b) =====
echo "🔄 Phase 2: Synthesizing with Ollama qwen3:14b..."
SYNTHESIZED_JSON="/tmp/synthesized-$TIMESTAMP.json"
python3 "$SCRIPT_DIR/scripts/synthesize-content-v4.py" "$EXTRACTED_JSON" "$SYNTHESIZED_JSON" 2>/dev/null || {
    echo "⚠️  Synthesis timed out, using extracted content"
    cp "$EXTRACTED_JSON" "$SYNTHESIZED_JSON"
}
echo "✅ Content synthesized"

# ===== STEP 5: Format Report (HTML + Markdown) =====
echo "🔄 Phase 3: Generating Reports..."
python3 "$SCRIPT_DIR/scripts/formatter-v4.py" "$SYNTHESIZED_JSON" "$QUERY" "$DOKUMENTE" 2>/dev/null || {
    echo "❌ Formatting failed"
    exit 1
}

# Find generated reports
GENERATED_HTML=$(ls -t "${DOKUMENTE}"/REPORT-*.html 2>/dev/null | head -1)
GENERATED_MD=$(ls -t "${DOKUMENTE}"/REPORT-*.md 2>/dev/null | head -1)

echo ""
echo "✅ REPORT COMPLETE:"
[[ -n "$GENERATED_HTML" ]] && echo "   📄 HTML: $(basename $GENERATED_HTML)"
[[ -n "$GENERATED_MD" ]] && echo "   📝 Markdown: $(basename $GENERATED_MD)"
echo "   📂 Location: $DOKUMENTE"

# Open in viewer (prefer PDF, fallback to HTML in browser)
GENERATED_PDF=$(ls -t "${DOKUMENTE}"/REPORT-*.pdf 2>/dev/null | head -1)

if [[ -n "$GENERATED_PDF" ]]; then
    # PDF exists, open in evince
    if command -v evince &>/dev/null; then
        DISPLAY=:1 evince "$GENERATED_PDF" >/dev/null 2>&1 &
        echo "📺 Opening PDF Report in evince..."
        sleep 1
    fi
elif [[ -n "$GENERATED_HTML" ]]; then
    # Fallback to HTML in browser
    if command -v firefox &>/dev/null; then
        DISPLAY=:1 firefox "$GENERATED_HTML" >/dev/null 2>&1 &
        echo "📺 Opening HTML Report in Firefox..."
        sleep 1
    elif command -v chromium &>/dev/null; then
        DISPLAY=:1 chromium "$GENERATED_HTML" >/dev/null 2>&1 &
        echo "📺 Opening HTML Report in Chromium..."
        sleep 1
    fi
fi

# Cleanup
rm -f "$PDF_JSON_INPUT" "$EXTRACTED_JSON" "$SYNTHESIZED_JSON" 2>/dev/null

echo "✅ Done"
