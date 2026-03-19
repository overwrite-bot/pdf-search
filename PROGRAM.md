# PROGRAM.md — pdf_zusammenfassung Optimization

## Goal
Improve pdf_zusammenfassung skill quality and performance through autonomous iteration.

## Key Metrics to Optimize

1. **Extraction Quality** (0-100)
   - Does the extracted content match the actual PDF content?
   - Are recipes detected correctly?
   - Are essay summaries relevant?
   - Measured via: test suite pass rate, manual spot checks

2. **Link Validity** (0-100)
   - Do source links work correctly?
   - Are file:// URLs properly formed?
   - Measured via: link_test.py (checks 5 random PDFs)

3. **Processing Speed** (ms)
   - How fast is the full pipeline?
   - Extract → Synthesize → Format
   - Target: <120s per query (currently ~110s average)

4. **PDF Generation Success Rate** (0-100)
   - Does wkhtmltopdf succeed consistently?
   - Fallbacks working?
   - Measured via: pdf_test.py

## Test Suite

### Core Tests
- **test_extraction.py**: Checks extraction logic (content, length, encoding)
- **test_synthesize.py**: Checks 14b synthesis (relevance, structure)
- **test_formatting.py**: Checks HTML/MD/PDF output (structure, links)
- **test_categorization.py**: Checks BERT categorization (accuracy on known samples)

### Measurement Command
```bash
cd ~/.openclaw/workspace/skills/pdf_zusammenfassung
python -m pytest tests/ -v --tb=short > test_results.log 2>&1
python tests/parse_metrics.py test_results.log
```

This outputs:
```
METRIC: extraction_quality=95 link_validity=100 speed_ms=110000 pdf_success=98
```

## Hypotheses to Test

### H1: Longer extraction window
**Current:** Skip first 1000 chars, take 5000 total (chars 1000-5000)
**Hypothesis:** Skip more metadata, take chars 2000-7000 for better content

### H2: Better UTF-8 handling
**Current:** iconv -f UTF-8 -t UTF-8 -c (lossy)
**Hypothesis:** Use chardet to auto-detect encoding before converting

### H3: Smarter content type detection
**Current:** Simple heuristics (count keywords)
**Hypothesis:** Use TF-IDF + more category keywords

### H4: Cache synthesized outputs
**Current:** Hits 14b every time
**Hypothesis:** Cache synthesis results by hash(content) for 1h

### H5: Parallel PDF processing
**Current:** Sequential extraction (pdf1, pdf2, pdf3...)
**Hypothesis:** Use parallel pdftotext calls (max 4 concurrent)

## Core Logic File

**File to modify:** `scripts/extract-content-v4.py`

Key functions:
- `extract_from_pdf_text()` — Main extraction logic
- `identify_content_type()` — Type detection
- Implement improvements here only

## Branching Strategy

```
master (v4.0 stable)
  └── skill-improver/extraction-optimization (YOUR BRANCH)
        ├── commit: h1-longer-window
        ├── commit: h2-better-utf8
        └── commit: h3-tfidf-detection
```

If an experiment succeeds, keep commit on this branch. At the end, PR → master.

## Success Criteria

- **Extraction Quality:** Increase from 95 → 98+
- **Link Validity:** Stay at 100
- **Speed:** Stay <120s (accept slight increase for better quality)
- **PDF Success:** Maintain 98+

## How to Start

1. Run baseline tests:
   ```bash
   python -m pytest tests/ -v
   ```

2. Extract baseline metric:
   ```bash
   python tests/parse_metrics.py test_results.log > baseline.txt
   ```

3. Create results.tsv:
   ```
   commit	metric	status	description
   940ebc6	extraction=95,link=100,speed=110000,pdf=98	keep	v4.0 baseline
   ```

4. Start with H1 (longest window) — simplest change with likely impact

5. Commit, test, log, decide → repeat

## Notes

- Only modify scripts/extract-content-v4.py during optimization
- Don't change tests or SKILL.md
- Use git commit messages like: "exp: h1-longer-extraction-window"
- If a test breaks → git revert immediately, document failure
- Aim for 5-10 iterations per session
