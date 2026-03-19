#!/bin/bash
# H5 Experiment: Parallel PDF extraction
# Extract from 4 PDFs concurrently instead of sequentially
# Usage: parallel-extractor.sh <pdf_list> <output_json>

PDF_LIST="$1"
OUTPUT_JSON="$2"
MAX_JOBS=4

if [[ -z "$PDF_LIST" ]] || [[ -z "$OUTPUT_JSON" ]]; then
    echo "Usage: parallel-extractor.sh <pdf_list_file> <output_json>"
    exit 1
fi

# Temp directory for parallel outputs
TMPDIR="/tmp/pdf-extract-$$"
mkdir -p "$TMPDIR"

# Function to extract single PDF (runs in parallel)
extract_single_pdf() {
    local pdf="$1"
    local output_dir="$2"
    local idx="$3"
    
    [[ ! -f "$pdf" ]] && return
    
    PDF_NAME=$(basename "$pdf")
    
    # Extract text
    PDF_TEXT=$(pdftotext "$pdf" - 2>/dev/null | \
        iconv -f UTF-8 -t UTF-8 -c | \
        head -c 7000 || echo "")
    
    [[ -z "$PDF_TEXT" ]] && return
    
    # Escape for JSON
    PDF_TEXT_ESCAPED=$(echo "$PDF_TEXT" | python3 -c "import sys, json; text = sys.stdin.read(); print(json.dumps(text))" 2>/dev/null || echo '""')
    PDF_PATH_ESCAPED=$(python3 -c "import json; print(json.dumps('$pdf'))")
    
    # Write to temp file
    echo "{\"name\": \"$PDF_NAME\", \"path\": $PDF_PATH_ESCAPED, \"text\": $PDF_TEXT_ESCAPED}" > "$output_dir/$idx.json"
}

export -f extract_single_pdf

# H5: Extract PDFs in parallel (max 4 concurrent jobs)
echo "🚀 Extracting PDFs in parallel (max $MAX_JOBS jobs)..."

xargs -I {} -P $MAX_JOBS bash -c "extract_single_pdf '{}' '$TMPDIR' $((++idx))" < "$PDF_LIST" 2>/dev/null

# Merge JSON outputs
JSON_ARRAY="["
FIRST=true

for json_file in "$TMPDIR"/*.json; do
    [[ ! -f "$json_file" ]] && continue
    
    if [[ "$FIRST" == true ]]; then
        FIRST=false
    else
        JSON_ARRAY+=","
    fi
    JSON_ARRAY+=$(cat "$json_file")
done

JSON_ARRAY+="]"

# Write final output
echo "{\"pdfs\": $JSON_ARRAY}" > "$OUTPUT_JSON"

# Cleanup
rm -rf "$TMPDIR"

echo "✅ Extraction complete: $OUTPUT_JSON"
