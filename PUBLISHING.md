# Publishing Guide — pdf-zusammenfassung v3.2.0

## Status
- ✅ Skill complete & production-ready
- ✅ Git repository: https://github.com/overwrite-bot/pdf-search
- ✅ Version tag: v3.2.0
- ✅ package.json: Ready for clawhub
- ⏳ clawhub publishing: Awaiting browser auth

## Publishing to clawhub.com

### Step 1: Authenticate
```bash
clawhub login
# Opens browser: https://clawhub.ai/cli/auth
# (Requires GitHub account)
```

### Step 2: Publish
```bash
clawhub publish /home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung \
  --slug pdf-zusammenfassung \
  --name "PDF Search + Wikipedia Synthesis" \
  --version 3.2.0 \
  --changelog "Full Wikipedia integration with dual-synthesis. Kiwix articles auto-fetched and summarized with 14b. BERT categorization for 8482 PDFs. Production-ready."
```

### Step 3: Verify
```bash
clawhub search "pdf-zusammenfassung"
clawhub info pdf-zusammenfassung
```

## After Publishing

Others can install:
```bash
clawhub install pdf-zusammenfassung
# or
clawhub install pdf-zusammenfassung --version 3.2.0
```

## Requirements for Users

### System Dependencies
- bash >= 5.0
- curl, sqlite3, jq, python3

### Services (must be running)
1. **RAG-Daemon** (http://127.0.0.1:5555)
   - ~/brauerei-automation/rag-daemon.py
   - systemctl start rag-daemon

2. **Kiwix** (http://localhost:8080)
   - /usr/bin/kiwix-serve
   - systemctl start kiwix

### Python Dependencies
```bash
pip install beautifulsoup4 lxml requests reportlab
```

### Data Files
- PDF Index: `/media/.../pdf-index.db` (FTS5)
- PDFs: Must be indexed (pdf-index.sh)
- Wikipedia: Kiwix offline (49 GB German)

## Directory Structure

```
~/.openclaw/workspace/skills/pdf_zusammenfassung/
├── SKILL.md                          # Skill definition
├── package.json                      # clawhub metadata
├── README.md                         # User docs
├── KIWIX-INTEGRATION-PLAN.md        # Implementation notes
├── kiwix-fetch.py                   # Wikipedia fetcher + 14b
├── scripts/
│   ├── pdf-search.sh                # Main entry point
│   ├── extract-content.py           # PDF text extraction
│   ├── synthesize-content.py        # RAG synthesis
│   ├── add-wikipedia.sh             # Wikipedia integration
│   └── enhance-with-wikipedia.py    # Report enhancement
├── .venv/                           # Python environment
└── .git/                            # Version control
```

## Git Commits

- `1a2366c` — chore: Add package.json for clawhub publishing (v3.2.0)
- `515e91a` — feat: Full Wikipedia integration with 14b summarization
- `e775a7c` — feat: Kiwix Wikipedia integration (phase 1 - links)
- `c7c9d3b` — feat: BERT-based PDF categorization (v3.1.1)

## Version History

### v3.2.0 (2026-03-19)
- Full Wikipedia integration
- Dual-synthesis (PDFs + Wikipedia)
- 14b summarization for Wikipedia
- Production-ready

### v3.1.1
- BERT categorization
- 8482 PDFs re-indexed

### v3.1
- Hybrid search (80/20 BM25/Semantic)
- Merge pdf-search + hybrid_search

## Support

**Issues:** https://github.com/overwrite-bot/pdf-search/issues  
**Discussions:** https://discord.com/invite/clawd  
**docs:** https://clawhub.com (coming soon)
