# PDF Categorization Improvement Program

## Goal
Replace keyword-based PDF categorization with German BERT embeddings for better accuracy.

**Target Accuracy:** >95% on test set of known PDFs
**Current Baseline:** ~75% (keyword-matching, known issues with "Apokalypse" → "Apokalypse" tagged as tech)

## Core File
**Location:** `categorization-core.py`

**Modifiable sections:**
1. `MODEL_NAME` — Which transformer model to use
2. `CATEGORY_DEFINITIONS` — Category label descriptions
3. `categorize_pdf()` — Similarity computation & threshold
4. `categorize_all_pdfs()` — Batch processing logic

## Test Suite
**Location:** `tests/test_categorization.py`

**15 known PDFs** with expected categories:
- Tech (4 PDFs): Programming, Linux, C++, Database
- Cooking (4 PDFs): Fermentation, Cheese, Meat, Mushrooms
- Health (3 PDFs): Nutrition, Yoga, Herbalism
- Philosophy (2 PDFs): Kant, Nietzsche
- Esoterik (2 PDFs): Chakras, Meditation, Tarot

**Run tests:**
```bash
cd ~/.openclaw/workspace/skills/pdf_zusammenfassung
python -m pytest tests/test_categorization.py -v
```

## Database
**Path:** `/media/overwrite/Datenplatte 2/pdf-index.db`

**Backup created:** `pdf-index.db.backup-keyword-20260319-123000`

**New columns added:**
- `bert_confidence` (FLOAT) — Confidence score from BERT model
- `category` (TEXT) — Existing column (updated in-place)

## Improvement Opportunities

### 1. Model Selection
- **Current:** `distiluse-base-multilingual-cased-v2` (130MB, fast)
- **Alternative 1:** `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (435MB, better accuracy)
- **Alternative 2:** Fine-tuned German BERT (`dbmdz/bert-base-german-uncased`)

**Metric:** Test accuracy on 15-PDF test set

### 2. Category Definitions
- Improve label descriptions (more specific keywords)
- Add category-specific examples
- Adjust for ambiguous cases (e.g., "Meditation" appears in Philosophy AND Esoterik)

**Metric:** Test accuracy on 15-PDF test set

### 3. Similarity Threshold
- Current threshold: 0.3 (if lower, classify as "general")
- Adjust per-category thresholds (e.g., tech requires 0.4, esoterik allows 0.25)

**Metric:** Test accuracy on 15-PDF test set

### 4. Content Window
- Current: Use filename + first 300 chars of content
- Try: Full first page, abstract, or TOC instead

**Metric:** Test accuracy on 15-PDF test set

### 5. Ensemble Methods
- Combine multiple models (BERT + lexical keywords)
- Vote-based categorization for ambiguous cases

**Metric:** Test accuracy on 15-PDF test set

## Workflow

1. **Hypothesis:** "Model X + Category Definition Y will improve accuracy to Z%"
2. **Modify:** `categorization-core.py`
3. **Run Tests:**
   ```bash
   pytest tests/test_categorization.py -v
   ```
4. **Measure:** Accuracy ≥80% to pass
5. **Log Results:** See results.tsv
6. **Decide:** Keep (commit) or discard (revert)
7. **Loop:** Go to step 1

## Baseline Results (Keyword-Matching)

```
Current Categorization (Keyword-Based):
  tech        :  6873 PDFs (81.0%)
  general     :   817 PDFs (9.6%)
  health      :   405 PDFs (4.8%)
  cooking     :   214 PDFs (2.5%)
  philosophy  :    83 PDFs (1.0%)
  esoterik    :    90 PDFs (1.1%)

Known Issues:
  ❌ Aleister Crowley books → tech (should be esoterik)
  ❌ Apokalypse books → tech (should be philosophy)
  ❌ C++ query → returns Apokalypse (semantic drift)
```

## Success Criteria
- ✅ Test accuracy ≥95% on 15-PDF test set
- ✅ No false positives for "Apokalypse" as tech
- ✅ "Chakra" books correctly labeled as esoterik
- ✅ All 8482 PDFs re-categorized in <5 min
- ✅ New bert_confidence scores in database

## Notes
- Backup exists: Always safe to revert
- Dry-run available: `--dry-run` flag
- Sample testing: `--test 10` to test on 10 random PDFs
