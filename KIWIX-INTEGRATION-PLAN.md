# Kiwix Wikipedia Integration Plan (Dual-Synthesis Option A)

## Goal
Every query searches BOTH PDF + Wikipedia → better, more complete answers.

**Example:**
```
Query: "fermentation"
  ├─ PDFs: "Fermentieren für Anfänger" (practical)
  ├─ Wikipedia: "Fermentation" article (theory)
  └─ Report: Combines both sources
```

## Current Status
- ✅ Kiwix running on port 8080
- ✅ Wikipedia offline (49 GB, German)
- ✅ kiwix-search.py started (HTML parsing issues)
- ❌ Full integration: Blocked by Kiwix HTML complexity

## Implementation Options

### Option 1: RAG-Daemon Extension (RECOMMENDED)
**Best approach:** Modify RAG-Daemon to query Kiwix directly

**File:** `~/brauerei-automation/rag-daemon.py`

**Changes:**
```python
# In prepare_context():
context = ""

# 1. PDFs (existing)
pdf_context = search_pdfs(query, category)
context += f"PDFs:\n{pdf_context}\n\n"

# 2. Kiwix (NEW)
wiki_context = search_kiwix(query)
context += f"Wikipedia:\n{wiki_context}\n\n"

# 3. Memory/KB (existing)
# ...

return context
```

**Kiwix Helper Function:**
```python
def search_kiwix(query: str, limit: int = 3) -> str:
    """Query Kiwix Wikipedia"""
    import subprocess
    try:
        # Use mwclient or direct Wikipedia parsing
        # OR: Simple curl to Kiwix API
        result = subprocess.run(
            ["curl", "-s", f"http://localhost:8080/search?pattern={query}"],
            capture_output=True, text=True
        )
        return parse_wikipedia_results(result.stdout)
    except:
        return ""
```

**Effort:** ~1-2 hours  
**Benefit:** ⭐⭐⭐⭐⭐ (Massively better answers)

---

### Option 2: Hybrid Search Extension
**Modify:** `hybrid_search.py`

**Add Kiwix as 3rd search source:**
```python
class HybridSearch:
    def search(self, query, sources=['pdf', 'wikipedia', 'memory']):
        results = {}
        
        if 'pdf' in sources:
            results['pdf'] = self.search_pdf(query)
        
        if 'wikipedia' in sources:
            results['wikipedia'] = self.search_kiwix(query)
        
        # Combine + rank by relevance
        combined = self.combine_results(results)
        return combined
```

**Effort:** ~1 hour  
**Benefit:** ⭐⭐⭐⭐ (Good, modular)

---

### Option 3: Post-Process PDF Reports
**Easiest:** Add Wikipedia links to final PDF report

**Changes in `pdf-search.sh`:**
```bash
# After generating markdown:
# Append Wikipedia reference
echo "## 📚 Wikipedia Reference" >> "$REPORT_FILE.md"
echo "Learn more: http://localhost:8080/search?pattern=$QUERY" >> "$REPORT_FILE.md"
```

**Effort:** ~15 minutes  
**Benefit:** ⭐⭐⭐ (Minimal, but helps)

---

## Blockers & Solutions

### Blocker 1: Kiwix HTML Parsing
**Problem:** Kiwix search returns complex HTML, regex parsing unreliable  
**Solutions:**
- Use BeautifulSoup (more robust)
- Use `mwclient` library (MediaWiki protocol, if Kiwix supports)
- Parse JSON from Kiwix API (if available)
- Direct Wikipedia URL construction (assuming predictable slugs)

### Blocker 2: Kiwix Service Management
**Problem:** kiwix.service crashed (wrong path)  
**Solution:** Fix `/etc/systemd/system/kiwix.service`
```ini
[Service]
ExecStart=/usr/bin/kiwix-serve --port 8080 "/media/overwrite/Datenplatte 1/wikipedia/wikipedia_de_all_maxi_2026-01.zim"
```

### Blocker 3: Integration Complexity
**Problem:** RAG-Daemon modifies need careful testing  
**Solution:** Test in isolation first, then merge

---

## Recommended Path (Quick Win)

1. **Today (15 min):** Option 3 (Wikipedia links in reports)
   - Easy, low-risk
   - Users can click through

2. **Later (1-2 hours):** Option 1 (RAG-Daemon extension)
   - Full dual-synthesis
   - Best quality

---

## Files Involved

- `~/brauerei-automation/rag-daemon.py` — Main integration point
- `/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/kiwix-search.py` — Search wrapper
- `/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/scripts/pdf-search.sh` — Output formatting
- `/etc/systemd/system/kiwix.service` — Service config

---

## Testing Plan

```bash
# 1. Test Kiwix is running
curl http://localhost:8080/ | head -1

# 2. Test search
curl "http://localhost:8080/search?pattern=fermentation"

# 3. Test new feature
pdf-search "fermentation" cooking
# Should show Wikipedia link

# 4. Full integration test
pdf-search "pilze" esoterik
# Should combine PDF + Wikipedia in report
```

---

## Priority

**Next Step:** Option 3 (15 min) — Add Wikipedia links to reports  
**Future:** Option 1 (1-2 hours) — Full RAG-Daemon integration
