# pdf-zusammenfassung v3.2.0

**Local PDF search + Wikipedia synthesis with AI summarization**

Search across your entire PDF library + Wikipedia knowledge base. Automatically fetch relevant Wikipedia articles and combine with PDF insights — all summarized by a local 14b language model.

## Features

✅ **Dual-Source Synthesis**
- PDFs from your library (indexed with BERT categorization)
- Wikipedia articles (Kiwix offline, German)
- Both sources combined in single report

✅ **Intelligent Search**
- Hybrid search (80% keyword BM25 + 20% semantic similarity)
- Category filtering (tech, cooking, esoterik, philosophy, health)
- 8,482+ PDFs pre-indexed with FTS5

✅ **AI Summarization**
- Local qwen3:14b model (0$ cost, no API)
- Summarizes PDFs, Wikipedia articles, and synthesizes both
- Consistent tone & formatting

✅ **Offline-First**
- Kiwix Wikipedia (49 GB German offline)
- RAG-Daemon local API
- No external cloud services
- Works without internet after initial setup

✅ **Professional Reports**
- Markdown + PDF output
- Wikipedia context sections
- PDF source citations
- Metadata + timestamps

## Quick Start

### Installation

```bash
# Via clawhub (when published)
clawhub install pdf-zusammenfassung

# Or manually
git clone https://github.com/overwrite-bot/pdf-search.git
cd pdf-search
python3 -m venv .venv
source .venv/bin/activate
pip install -q beautifulsoup4 lxml requests reportlab
```

### Usage

```bash
pdf-search "meditation yoga" esoterik
# Output: ~/Dokumente/REPORT-meditation-yoga-YYYYMMDD-HHMMSS.pdf
```

### Categories

```
all          # All PDFs
tech         # Technology, engineering, science
cooking      # Recipes, food, culinary
esoterik     # Spirituality, philosophy, wellness
philosophy   # Philosophy, ethics, theory
health       # Health, medicine, nutrition
```

## Architecture

```
Query Input
    ↓
RAG-Daemon v0.5
├─ Hybrid Search (BM25 + Semantic)
├─ Category Filtering (BERT)
├─ FTS5 PDF Index (8,482 PDFs)
├─ PDF Content Extraction
├─ Wikipedia Fetching (Kiwix)
└─ qwen3:14b Summarization (GPU)
    ↓
Report Generation
├─ Markdown (structured)
├─ PDF (professional output)
├─ Wikipedia sections
└─ Metadata + timestamps
    ↓
evince Display (optional)
```

## Requirements

### System

- bash >= 5.0
- curl, sqlite3, jq, python3
- 8 GB RAM minimum (14b model)
- GPU recommended (NVIDIA RTX series)

### Services (must be running)

```bash
# Start RAG-Daemon
sudo systemctl start rag-daemon
curl http://127.0.0.1:5555/health

# Start Kiwix
sudo systemctl start kiwix
curl http://localhost:8080/ | head -1
```

### Data

- **PDF Index:** `/media/.../pdf-index.db` (FTS5, ~500 MB)
- **PDFs:** Must be indexed by `pdf-index.sh`
- **Wikipedia:** Kiwix offline (49 GB German)

### Python

```bash
pip install beautifulsoup4 lxml requests reportlab
```

## Configuration

Edit paths in `scripts/pdf-search.sh`:

```bash
DOKUMENTE="/home/user/Dokumente"        # Output directory
PDF_DB="/path/to/pdf-index.db"          # Index database
RAG_URL="http://127.0.0.1:5555"         # RAG-Daemon URL
KIWIX_URL="http://localhost:8080"       # Kiwix URL
```

## Examples

### Example 1: Pilz-Bestimmung
```bash
pdf-search "pilze bestimmung" esoterik
```

**Output:**
- PDF-based summaries from *Lexikon der Pilze*, *BLV Pilzführer*
- Wikipedia section: *Speisepilz* article (14b-summarized)
- Combined report with safe/toxic identification

### Example 2: Fermentation für Brauerei
```bash
pdf-search "gärung fermentation temperatur" cooking
```

**Output:**
- PDF-based recipes & techniques
- Wikipedia: *Gärung* article (chemistry + history)
- Report combines practical + theoretical knowledge

### Example 3: Meditation & Yoga
```bash
pdf-search "meditation yoga" esoterik
```

**Output:**
- PDFs: *Michael Schaper — Yoga & Meditation*, *Yin Yoga*, etc.
- Wikipedia: *Yoga* + *Meditation* articles
- Single report with practice guidance + historical context

## Performance

| Metric | Value |
|--------|-------|
| First search | 8-12s (RAG-Daemon + PDF extraction) |
| Wikipedia fetch | 3-5s (Kiwix + 14b summary) |
| Report generation | 2-3s (Markdown + PDF) |
| Total | 15-20s per query |
| Cost | €0 (100% local) |

## Troubleshooting

### RAG-Daemon not responding
```bash
sudo systemctl status rag-daemon
sudo journalctl -u rag-daemon -f
```

### Kiwix not responding
```bash
sudo systemctl status kiwix
curl -v http://localhost:8080/search?pattern=test
```

### PDFs not found
```bash
# Check index
sqlite3 /media/.../pdf-index.db "SELECT COUNT(*) FROM pdf_index;"

# Re-index if needed
bash pdf-index.sh /path/to/PDFs/
```

### Wikipedia article not summarized
```bash
# Test kiwix-fetch.py directly
python3 kiwix-fetch.py "Gärung"
```

## Development

### Project Structure

```
scripts/
├── pdf-search.sh              # Main entry point
├── extract-content.py         # PDF text extraction
├── synthesize-content.py      # RAG synthesis
└── add-wikipedia.sh           # Wikipedia integration

kiwix-fetch.py                 # Wikipedia fetcher + 14b
SKILL.md                       # Skill definition
package.json                   # clawhub metadata
```

### Testing

```bash
# Test single query
./scripts/pdf-search.sh "pilze"

# Test with category
./scripts/pdf-search.sh "meditation" esoterik

# Test Wikipedia fetch
python3 kiwix-fetch.py "Fermentation" --full
```

### Contributing

1. Fork: https://github.com/overwrite-bot/pdf-search
2. Branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: ..."`
4. Push: `git push origin feature/your-feature`
5. PR: Create pull request

## License

MIT — Use freely, attribute optionally

## Support

- **Issues:** https://github.com/overwrite-bot/pdf-search/issues
- **Discussions:** https://discord.com/invite/clawd
- **OpenClaw Docs:** https://docs.openclaw.ai

## Thanks

- OpenClaw team (framework + tools)
- Ollama community (qwen3:14b)
- Kiwix (offline Wikipedia)
- BeautifulSoup (HTML parsing)
