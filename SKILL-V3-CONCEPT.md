# PDF-Search v3.0 — Concept: Recipe Extraction & Synthesis

## Vision

Transform pdf-search from **"just answering questions"** to **"extracting & creating actionable recipes"**.

### Current (v2.0)
```
Query → RAG Search → 14b Summary → HTML Report
(Info only, no actionable content)
```

### Target (v3.0)
```
Query → RAG Search + PDF Content Extraction → 14b Recipe Synthesis → Complete Recipes + Instructions
(Full recipes ready to cook from)
```

---

## Core Changes

### 1. PDF Content Extraction (NEW)

Instead of just summarizing, **extract raw content** from top PDFs:
- Ingredient lists
- Cooking instructions
- Temperature/timing info
- Chef notes & tips

**Tool:** `pdfplumber` (Python) for text extraction

```python
pdf = pdfplumber.open(pdf_path)
for page in pdf.pages:
    text = page.extract_text()
    # Extract structured data (recipes, lists, etc.)
```

### 2. RAG-Daemon Enhanced Query (NEW)

**Current:** "What are meat recipes?"
**New:** "Extract all meat recipe names, ingredients, and cooking methods"

More specific prompts → Better extraction → More actionable content

### 3. Recipe Synthesis (14b)

**Input:** 
- Extracted recipes from PDFs
- User query context

**Output:**
- 2-3 complete recipes (real from books + synthesized from contexts)
- Full ingredient lists
- Step-by-step instructions
- Cooking times, temperatures
- Chef tips & substitutions

---

## Report Structure (v3.0)

```
# Fleischrezepte Report

## 🔍 Suchanfrage
fleischrezepte

## 📚 Gefundene Quellen
4 Bücher mit Fleischrezepten

## 🍳 REZEPT 1: Traditioneller Schweinenacken im Ofen
Quelle: Das Vermächtnis unserer Nahrung (Enig & Fallon)

### 📋 Zutaten (4 Personen)
- 1,5 kg Schweinenacken
- 2 EL Schweineschmalz
- 4 Karotten
- ... (complete list)

### 👨‍🍳 Zubereitung
1. Ofen auf 160°C vorheizen
2. Fleisch säubern...
   (step-by-step instructions)

### ⏱️ Timing
- Vorbereitung: 15 min
- Garzeit: 3-4 Stunden
- Gesamtzeit: 3h 45 min

### 💡 Tipps
- Fleisch vor Garen Raumtemperatur annehmen
- Low & Slow: Nicht über 160°C
- ... (extracted from book context)

---

## 🍳 REZEPT 2: Schweinenacken Low-Carb Variante
Quelle: Abnehmen ohne Kohlenhydrate (Andrea Fischer)
Synthese: 14b kombiniert Enig & Fischer

### 📋 Zutaten
... (complete)

### 👨‍🍳 Zubereitung
... (complete)

---

## 🍳 REZEPT 3: Keto Schweinenacken-Gulasch
Quelle: Mein Keto-Kochbuch (Bruce Fife)
Synthese: 14b erweitert mit Keto-Aspekten

---

## 📊 Metadaten & Quellen
```

---

## Implementation Plan

### Phase 1: Enhanced RAG Query (Week 1)

```bash
# Instead of:
curl http://127.0.0.1:5555/ask \
  -d '{"query": "fleischrezepte"}'

# New:
curl http://127.0.0.1:5555/ask \
  -d '{
    "query": "fleischrezepte",
    "extraction_mode": "recipes",
    "fields": ["ingredients", "instructions", "timing", "tips"]
  }'
```

### Phase 2: PDF Content Extraction (Week 1)

Create `extract-recipes.py`:
```python
import pdfplumber
import json

def extract_recipes(pdf_path):
    """Extract recipe-like content from PDF"""
    recipes = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Pattern matching for recipes
            # - "Zutaten:" / "Ingredients:"
            # - "Zubereitung:" / "Instructions:"
            # - Lists of items with quantities
            
            recipes.extend(parse_recipes(text))
    
    return recipes
```

### Phase 3: Recipe Synthesis (14b) (Week 1)

```python
def synthesize_recipe(query, extracted_recipes, pdf_contexts):
    """Ask 14b to create complete recipes"""
    
    prompt = f"""
    User wants: {query}
    
    I found these recipe fragments from multiple books:
    {extracted_recipes}
    
    Please create 3 complete, actionable recipes:
    1. Direct from the books (if found)
    2. Synthesized combining best practices
    3. Modern variation (e.g., Low-Carb version)
    
    For each recipe provide:
    - Full ingredient list with quantities
    - Step-by-step instructions
    - Cooking time & temperature
    - Tips & variations
    - Nutritional notes (if relevant)
    """
    
    return ollama.generate(prompt, model="qwen3:14b")
```

### Phase 4: Report Generation (Week 1)

Enhanced HTML with:
- Recipe cards (printable)
- Ingredient checkboxes
- Timer integration (HTML5)
- PDF source links
- Shopping list generator

---

## Technical Components

### New Scripts

1. **extract-recipes.py** (200 lines)
   - PDF content extraction
   - Pattern matching for recipes
   - Structured data output

2. **synthesize-recipes.py** (150 lines)
   - RAG query with extraction mode
   - 14b synthesis
   - Output formatting

3. **pdf-search-v3.sh** (updated)
   - Calls new Python scripts
   - Better HTML generation
   - Recipe-focused report

### Modified RAG-Daemon

Add extraction mode endpoint:
```
POST /ask/extract
{
  "query": "...",
  "extraction_mode": "recipes|ingredients|methods",
  "fields": ["..."]
}
```

---

## Benefits

| Aspect | v2.0 | v3.0 |
|--------|------|------|
| **Usability** | Info only | Ready to cook |
| **Actionable** | Summaries | Complete recipes |
| **Source** | Book names | Exact excerpts |
| **Variations** | None | 2-3 per query |
| **Time to cooking** | Read books | 5 min to start |

---

## Examples

### Query: "fleischrezepte"

**v2.0 Output:**
```
Bruce Fife's Keto cookbook has meat recipes with portions...
```

**v3.0 Output:**
```
🍳 REZEPT: Schweinenacken im Ofen
(source: Enig & Fallon, Das Vermächtnis)

Zutaten:
- 1,5 kg Schweinenacken
- 2 EL Schweineschmalz
- ...

Zubereitung:
1. Ofen auf 160°C
2. ...

Garzeit: 3-4 Stunden
```

---

## Timeline

**Implementation: 1-2 days** (once approved)

1. Create extract-recipes.py (2 hours)
2. Create synthesize-recipes.py (2 hours)
3. Update pdf-search.sh (1 hour)
4. Enhanced HTML report (1 hour)
5. Testing & refinement (2 hours)

---

## Questions for Andreas

1. **Priority:** Should v3.0 replace v2.0 or run in parallel?
2. **Scope:** Only cooking recipes, or also brewing/fermentation?
3. **Report detail:** How many recipes per report? (current: 3, could be 5+)
4. **Ingredients:** Should report generate shopping lists?
5. **Dietary:** Should reports include nutritional info (calories, carbs, etc.)?

---

**Status:** CONCEPT READY  
**Next:** Approval + Implementation  
**Complexity:** Medium (new Python modules, RAG enhancement)  
**Value:** High (transforms reports from read-only to actionable)
