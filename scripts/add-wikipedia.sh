#!/bin/bash
# Add Wikipedia summary to markdown report
# Usage: add-wikipedia.sh "query" "output-file.md"

QUERY="$1"
MD_FILE="$2"

[[ -z "$QUERY" || -z "$MD_FILE" ]] && { echo "Usage: add-wikipedia.sh 'query' 'report.md'"; exit 1; }

# Fetch Wikipedia using kiwix-fetch.py
VENV="/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/.venv"
SCRIPT_DIR="/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung"

source "$VENV/bin/activate" 2>/dev/null

# Get Wikipedia content as JSON
WIKI_JSON=$(python3 "$SCRIPT_DIR/kiwix-fetch.py" "$QUERY" 2>/dev/null | grep -A 100 "^---JSON---" | tail -n +2)

if [[ -n "$WIKI_JSON" ]]; then
    WIKI_TITLE=$(echo "$WIKI_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('title', ''))" 2>/dev/null)
    WIKI_SUMMARY=$(echo "$WIKI_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('summary', ''))" 2>/dev/null)
    
    if [[ -n "$WIKI_TITLE" ]]; then
        # Insert Wikipedia section before "Metadaten"
        {
            echo ""
            echo "## 🌐 Wikipedia-Ergänzung (Kiwix Offline)"
            echo ""
            echo "**${WIKI_TITLE}**"
            echo ""
            echo "$WIKI_SUMMARY"
            echo ""
            echo "_Quelle: Wikipedia (Kiwix Offline)_"
        } | sed -i '/^## 📊 Metadaten/e cat' "$MD_FILE"
    fi
fi
