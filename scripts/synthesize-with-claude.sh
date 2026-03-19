#!/bin/bash

# Nutze Claude Code um Raw PDF-Inhalte zu strukturieren + professionelle Reports zu bauen

MARKDOWN_INPUT="$1"
OUTPUT_MD="$2"

if [[ ! -f "$MARKDOWN_INPUT" ]]; then
    echo "❌ Input file not found: $MARKDOWN_INPUT"
    exit 1
fi

# Prepare prompt for Claude Code
PROMPT="Strukturiere diese rohen PDF-Inhalte in einen professionellen Rezept-Report:

1. **Identifiziere echte Rezepte** aus dem Text (Titel, Zutaten, Anleitung)
2. **Formatiere strukturiert**:
   - Rezept-Titel (# Rezept: Name)
   - 👥 Portionen / ⏱️ Zeit (falls vorhanden)
   - **Zutaten:** mit Checkboxen (- [ ])
   - **Anleitung:** nummeriert (1. 2. 3...)
3. **Gruppiere nach Gericht-Typ** (z.B. Braten, Eintopf, etc.)
4. **Füge Quellen hinzu** (welches PDF)
5. **Bau professionellen Markdown-Report** mit:
   - Schöner Überschrift
   - Zusammenfassung oben
   - Alle Rezepte strukturiert
   - Footer mit Metadaten

INPUT:
---
$(cat "$MARKDOWN_INPUT")
---

OUTPUT: Strukturiertes Markdown (für PDF-Konvertierung), maximal 2000 Zeilen.
"

# Nutze Claude Code
echo "🤖 Claude Code strukturiert die Rezepte..."

STRUCTURED=$(claude --permission-mode bypassPermissions --print "$PROMPT" 2>/dev/null)

if [[ -z "$STRUCTURED" ]]; then
    echo "⚠️  Claude Code failed, using raw content"
    cat "$MARKDOWN_INPUT" > "$OUTPUT_MD"
else
    echo "$STRUCTURED" > "$OUTPUT_MD"
    echo "✅ Strukturiert mit Claude Code"
fi

echo "📝 Output: $OUTPUT_MD"
