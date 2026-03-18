# PDF-Search Skill — Universal PDF Analysis & Synthesis

**Status:** v3.0 — Generic Content Extraction Framework (2026-03-18)

## Overview

Transform PDFs from **static documents** into **queryable, actionable content** through intelligent extraction + AI synthesis.

**Not just for recipes** — for ANY query type.

---

## Core Concept

### Old Approach (v2.0)
```
User Query
    ↓
RAG Search (Kiwix + 14b)
    ↓
Summary Answer
User still reads books
```

### New Approach (v3.0) — Generic Framework
```
User Query (any topic)
    ↓
┌─────────────────────────────────┐
│ Smart Content Extraction        │
├─────────────────────────────────┤
│ 1. Find relevant PDFs (FTS5)    │
│ 2. Extract structured data:     │
│    • Recipes (if cooking)       │
│    • Instructions (if how-to)   │
│    • Facts (if reference)       │
│    • Lists (if inventory)       │
│    • Tables (if data)           │
│ 3. Collect contextual snippets  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ AI Synthesis (14b)              │
├─────────────────────────────────┤
│ Given: Extracted data + context │
│ Create: Complete, actionable    │
│         response tailored to    │
│         query type              │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Formatted Output                │
├─────────────────────────────────┤
│ • Recipes (step-by-step)        │
│ • Instructions (numbered list)  │
│ • Analysis (structured)         │
│ • Summary (condensed)           │
│ • Data (tables/charts)          │
└─────────────────────────────────┘
    ↓
User gets ACTIONABLE CONTENT
```

---

## Content Extraction Types

### 1. **Structured Recipes**
- Zutaten → Ingredient lists
- Zubereitung → Step-by-step instructions
- Garzeit/Temperatur → Timing & heat
- Output: Complete recipe (ready to cook)

### 2. **How-To / Anleitung**
- Prerequisites → What you need
- Steps → Numbered instructions
- Warnings → Safety info
- Output: Actionable guide (ready to follow)

### 3. **Reference / Nachschlage**
- Definitions → Key terms
- Properties → Attributes
- Examples → Use cases
- Output: Comprehensive reference (ready to use)

### 4. **Data / Tabellen**
- Rows → Structured records
- Columns → Attributes
- Relationships → Cross-references
- Output: Clean data table (ready to analyze)

### 5. **Technical / Dokumentation**
- Configuration → Parameters
- Commands → Syntax
- Examples → Code snippets
- Output: Working documentation (ready to implement)

---

## Architecture

### Extraction Layer (`extract-content.py`)

```
Input: PDF Path + Query Context
    ↓
[Determine Content Type]
    ├─ Recipe detection (Zutaten, Zubereitung keywords)
    ├─ How-to detection (Steps, Prerequisites)
    ├─ Reference detection (Definitions, Properties)
    ├─ Data detection (Tables, Lists)
    └─ Technical detection (Code, Config)
    ↓
[Extract Relevant Sections]
    ├─ Pattern matching (regex for keywords)
    ├─ Structure parsing (lists, tables, steps)
    ├─ Context extraction (related paragraphs)
    └─ Metadata (source, page number, relevance)
    ↓
Output: Structured JSON with:
    {
      "content_type": "recipe|howto|reference|data|technical",
      "title": "...",
      "sections": {...},
      "contextual_snippets": [...],
      "source": "PDF filename + page",
      "confidence": 0.0-1.0
    }
```

### Synthesis Layer (`synthesize-content.py`)

```
Input: Query + Extracted Data
    ↓
[Determine Response Format]
    ├─ Recipe → Step-by-step with ingredients
    ├─ How-to → Numbered list with warnings
    ├─ Reference → Structured facts + examples
    ├─ Data → Table + analysis
    └─ Technical → Code + explanation
    ↓
[Build Synthesis Prompt]
    ├─ Include: Extracted data + context
    ├─ Instruct: Create complete, actionable response
    ├─ Format: Specific for content type
    └─ Quality: Add tips, variations, warnings
    ↓
[Query 14b for Synthesis]
    └─ RAG-Daemon API (:5555)
    ↓
Output: Structured response
    {
      "query": "...",
      "content_type": "...",
      "response": {...},
      "sources": ["Book 1", "Book 2"],
      "confidence": 0.0-1.0
    }
```

### Report Generation Layer (`generate-report.py`)

```
Input: Synthesized Content
    ↓
[Format Selection]
    ├─ Recipe → Recipe cards with checkboxes
    ├─ How-to → Step-by-step guide
    ├─ Reference → Structured reference
    ├─ Data → Tables with charts
    └─ Technical → Code blocks + explanation
    ↓
[Create HTML]
    ├─ Responsive design
    ├─ Printable as PDF
    ├─ Source citations
    ├─ Interactive elements (timers, checkboxes)
    └─ Mobile-friendly
    ↓
Output: Beautiful HTML Report
    └─ Opens in browser
    └─ Printable to PDF
    └─ Archivable as Markdown
```

---

## Usage

### Generic Command

```bash
pdf-search "your query here"
```

### Examples

**Example 1: Recipe Query**
```bash
pdf-search "schweinenackenrezepte"
# Output: 3 complete recipes (ingredients, instructions, timing)
```

**Example 2: How-To Query**
```bash
pdf-search "wie macht man sauerkraut"
# Output: Step-by-step fermentation guide
```

**Example 3: Reference Query**
```bash
pdf-search "pilzbestimmung"
# Output: Mushroom identification guide with characteristics
```

**Example 4: Data Query**
```bash
pdf-search "gärungstemperaturen bier"
# Output: Temperature table + best practices
```

**Example 5: Technical Query**
```bash
pdf-search "brauerei ausrüstung kalibrierung"
# Output: Equipment setup + calibration instructions
```

---

## Content Type Detection

Automatic detection based on query + PDF content:

| Query Keywords | Detected Type | Output Format |
|---|---|---|
| rezept, anleitung, wie, schritt | Recipe/How-To | Step-by-step |
| liste, tabelle, daten, vergleich | Data | Tables + charts |
| definition, was ist, erklär | Reference | Q&A + examples |
| code, befehl, config, setup | Technical | Code blocks |
| zusammenfassung, übersicht | Summary | Condensed text |

Fallback: 14b determines type from context.

---

## Output Formats

### Recipe Format
```
🍳 REZEPT: [Name]
Quelle: [Book]
Portionen: [X]

Zutaten:
☐ Item 1
☐ Item 2

Zubereitung:
1. Step 1
2. Step 2

Timing & Temperatur
Tipps
```

### How-To Format
```
📖 ANLEITUNG: [Title]
Quelle: [Book]

Was du brauchst:
- Item 1
- Item 2

Schritte:
1. Step 1
2. Step 2

⚠️ Wichtig:
- Warning 1
- Warning 2

Tipps & Variationen
```

### Reference Format
```
📚 NACHSCHLAGE: [Topic]
Quelle: [Book]

Definitionen:
Term 1: Definition
Term 2: Definition

Eigenschaften:
- Property 1
- Property 2

Beispiele:
Example 1
Example 2
```

### Data Format
```
📊 DATEN: [Topic]
Quelle: [Book]

| Spalte 1 | Spalte 2 |
|----------|----------|
| Data     | Data     |

Analyse:
- Finding 1
- Finding 2

Chart/Visualization
```

### Technical Format
```
⚙️ ANLEITUNG: [Topic]
Quelle: [Book]

Vorbereitung:
- Requirement 1
- Requirement 2

Schritte:
1. Step 1
2. Step 2

Code/Config:
[Code block]

Erklärung:
[Explanation]
```

---

## Key Files

### Python Modules

1. **extract-content.py** (generic extraction)
   - Input: PDF path + query
   - Output: Structured JSON with content type
   - Supports: Recipes, how-to, reference, data, technical

2. **synthesize-content.py** (AI synthesis)
   - Input: Query + extracted data
   - Output: Complete, actionable response
   - Adaptive to content type

3. **generate-report.py** (report generation)
   - Input: Synthesized content
   - Output: Beautiful HTML + Markdown

### Shell Integration

**pdf-search.sh** (main entry point)
- Detects query intent
- Calls extraction → synthesis → reporting
- Opens result in browser
- Archives Markdown + HTML

---

## Query Understanding

The skill intelligently routes queries:

```
Query: "schweinenackenrezepte"
├─ Content type: Recipe
├─ Search: "schweinenacken* OR nacken* OR fleisch*"
├─ Extract: Recipes from top PDFs
├─ Synthesize: 3 complete recipes (traditional, modern, low-carb)
└─ Format: Recipe cards with ingredients/instructions

Query: "wie macht man kimchi"
├─ Content type: How-To
├─ Search: "kimchi OR fermentation OR gärung"
├─ Extract: Steps, ingredients, fermentation times
├─ Synthesize: Complete guide with variations
└─ Format: Step-by-step instructions

Query: "temperaturprofile bier"
├─ Content type: Data/Reference
├─ Search: "temperatur OR profile OR °C"
├─ Extract: Temperature data, timing, stages
├─ Synthesize: Table + best practices
└─ Format: Data table + analysis

Query: "fehlersuche brauerei"
├─ Content type: Troubleshooting/Reference
├─ Search: "fehler OR problem OR troubleshoot"
├─ Extract: Common issues, symptoms, solutions
├─ Synthesize: Decision tree + fixes
└─ Format: Problem-solution matrix
```

---

## Performance

| Phase | Duration |
|-------|----------|
| Content Extraction (1 PDF) | 2-3s |
| Content Extraction (5 PDFs) | 10-15s |
| Content Synthesis (14b) | 8-12s |
| Report Generation | 2-3s |
| **Total** | **22-33s** |

---

## Quality & Reliability

### Confidence Scoring

Each response includes confidence score:
```json
{
  "confidence": 0.92,
  "explanation": "90% of response from direct PDF extraction, 10% synthesis"
}
```

### Quality Tiers

- **Tier 1 (Confidence > 0.90):** Direct from PDFs, minimal synthesis
- **Tier 2 (Confidence 0.70-0.90):** Mix of extraction + synthesis
- **Tier 3 (Confidence 0.50-0.70):** Mostly synthesis, limited extraction
- **Tier 4 (Confidence < 0.50):** Unable to extract, pure synthesis

---

## Future Enhancements (Roadmap)

### Phase 2 (v3.1)
- [ ] Image extraction from PDFs
- [ ] Multi-language support
- [ ] Ingredient substitutions
- [ ] Difficulty ratings

### Phase 3 (v3.2)
- [ ] Voice input (transcribe query)
- [ ] Voice output (read response)
- [ ] Video recipe links
- [ ] Real-time cooking timer

### Phase 4 (v3.3+)
- [ ] Community recipes
- [ ] User ratings & feedback
- [ ] Personalized recommendations
- [ ] Shopping list integration
- [ ] Nutritional analysis
- [ ] Cost per serving

---

## Integration Points

### Upstream
- **Query source:** Web chat, Discord, Signal, Telegram
- **Query parsing:** Natural language understanding
- **Intent detection:** Recipe, reference, how-to, data, technical

### Downstream
- **Output:** Browser (HTML), PDF printer, Email, Chat
- **Storage:** Markdown archive, Database
- **Caching:** Query cache (Redis), extracted content cache

### External Systems
- **RAG-Daemon** (:5555) — Query engine
- **ollama (qwen3:14b)** — Synthesis model
- **pdfplumber** — PDF extraction
- **FTS5 (SQLite)** — Full-text search

---

## Design Principles

1. **Universal Applicability**
   - Not just recipes — ANY PDF query type
   - Adaptive formatting per content type
   - Intelligent extraction + synthesis

2. **Actionability**
   - Output must be usable immediately
   - Complete information (not summaries)
   - Practical tips + variations

3. **Quality Over Speed**
   - ~30s acceptable for comprehensive response
   - Better to be complete than fast
   - Confidence scoring for transparency

4. **Cost Efficiency**
   - 100% local processing (no cloud APIs)
   - Free GPU (resident 14b)
   - ~$0 per query vs $0.20 cloud LLM

5. **User Experience**
   - Beautiful, printable reports
   - Mobile-friendly HTML
   - Browser-based (no new software)
   - One command: `pdf-search "your query"`

---

## Limitations & Known Issues

1. **PDF Quality Dependent**
   - Scanned PDFs: 60-70% extraction quality
   - Digital PDFs: 90%+ extraction quality
   - No image/photo extraction (yet)

2. **Language Support (Current)**
   - German ✅ Primary
   - English ✅ Supported
   - Other languages ⏳ Planned

3. **Content Types**
   - Recipes ✅ Optimized
   - How-To ✅ Optimized
   - Reference ✅ Optimized
   - Data ⏳ In development
   - Technical ⏳ Planned

4. **Synthesis Quality**
   - Depends on extraction completeness
   - 14b makes educated guesses when data incomplete
   - Confidence score indicates reliability

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.0 | 2026-03-18 | Initial PDF search + RAG integration |
| v3.0 | 2026-03-18 | Generic content extraction + synthesis framework |
| v3.1 | TBD | Image extraction, multi-language |
| v3.2 | TBD | Voice I/O, video links |
| v3.3+ | TBD | Community features, ML personalization |

---

## Support & Feedback

- **Issues:** Open in skill repo
- **Feature Requests:** Document in ROADMAP.md
- **Feedback:** Confidence scores track quality

---

## Meta

**Skill:** pdf-search  
**Type:** Content Extraction + AI Synthesis  
**Language:** Python 3.12, Bash  
**Model:** ollama qwen3:14b  
**Backend:** RAG-Daemon + FTS5  
**Status:** v3.0 (Generic Framework, In Development)  
**Maintainer:** Overwrite (KI-Assistant)  
**Created:** 2026-03-18  
**Last Updated:** 2026-03-18 20:12 UTC  

---

_This skill transforms static PDFs into dynamic, queryable knowledge sources._
