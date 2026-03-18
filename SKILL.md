---
name: pdf-search
description: Generate AI-powered PDF research reports with beautiful formatting. Use when: (1) User asks for recipe searches, research synthesis, or information gathering from local PDF collections, (2) Need to summarize multiple PDFs and combine findings, (3) Want readable formatted reports (HTML/PDF) with source citations. Outputs: HTML reports (browser-viewable, print-to-PDF compatible) with AI summaries per PDF, synthesized insights, and source paths. RAG-Daemon backend (qwen3:14b on GPU).
---

# PDF-Search Skill

Generate comprehensive research reports from local PDF collections with AI-powered summaries.

## What It Does

`pdf-search` queries your local knowledge base (PDFs + InfluxDB metadata) via RAG-Daemon and produces:

1. **Quick summary** (14b LLM response)
2. **Per-PDF analysis** (14b reads top 5 PDFs, generates detailed summaries)
3. **Synthesis** (combined insights + actionable recommendations)
4. **Beautiful HTML report** (print-to-PDF compatible, styled, with source citations)

Example:
```bash
pdf-search "rezepte mit lamm und pilzen"
```

→ Generates `/home/overwrite/Dokumente/REPORT-rezepte-mit-lamm-und-pilzen-20260318-193239.html`

## Quick Start

### Basic Usage

```bash
/home/overwrite/brauerei-automation/pdf-search.sh "your query here"
```

### Output

Reports go to: `~/Dokumente/REPORT-<query>-<timestamp>.html`

- **HTML file**: Immediately viewable in browser, printable as PDF
- **Markdown file**: Source markdown (for archiving or re-processing)

### Requirements

- **RAG-Daemon** running on `localhost:5555` (auto-starts via systemd)
- **Kiwix server** on `localhost:8080` (Wikipedia offline)
- **Desktop display** (DISPLAY=:1) for browser auto-open
- **curl**, **jq**, **date** (standard Unix tools)

## How It Works

### Query Flow

```
User Query
    ↓
RAG-Daemon (POST /ask)
    ├─ Searches: Kiwix (Wikipedia) + memory.db + kb.db + pdf-index.db (FTS5)
    ├─ Aggregates context
    └─ Calls Ollama qwen3:14b (GPU)
    ↓
[Quick Summary] + [Top 5 PDFs Found]
    ↓
[For each PDF]: Query 14b for detailed analysis
    ↓
[Combine all analyses] + Generate styled HTML
    ↓
Report saved & opens in browser
```

### Performance Expectations

| Metric | Value |
|--------|-------|
| **First query** | 10-15s (RAG search + 14b inference) |
| **Cached query** | <1s (LRU cache in RAG-Daemon) |
| **HTML generation** | 2-3s |
| **Per-PDF analysis** | +5-8s per PDF |
| **Total end-to-end** | 30-60s for 5 PDFs |

## Example Output

When you query `"rezepte mit lamm und pilzen"`, you get:

### HTML Structure

```html
<h1>Report: Rezepte Mit Lamm Und Pilzen</h1>

<h2>Suchanfrage</h2>
rezepte mit lamm und pilzen

<h2>Kurzzusammenfassung (14b)</h2>
[Quick 2-3 line answer from RAG-Daemon]

<h2>Detaillierte Analyse aus 5 PDFs</h2>
[For each PDF found]:
  - Full title
  - AI-generated summary (14b analyzed the PDF context)
  - Key insights & findings
  - Source path to PDF file

<h2>Synthesized Recipe / Recommendations</h2>
[Combined insights across all PDFs]

<h2>Metadaten</h2>
[Query latency, PDF count, tool version, timestamp]
```

## Customization

### Change Output Directory

Edit `DOKUMENTE` variable in `/home/overwrite/brauerei-automation/pdf-search.sh`:

```bash
DOKUMENTE="/your/path/here"
```

### Change Browser

The script uses `xdg-open` (system default). To force a specific browser:

```bash
DISPLAY=:1 firefox /home/overwrite/Dokumente/REPORT-*.html
```

### Maximum PDFs Analyzed

By default, the script analyzes top 5 PDFs. To change:

```bash
# In the script, find the while loop:
PDF_COUNT=0
# ...and add a limit:
if [[ $PDF_COUNT -ge 3 ]]; then break; fi  # max 3 PDFs
```

## Troubleshooting

### RAG-Daemon Not Running

```bash
sudo systemctl status rag-daemon
sudo systemctl start rag-daemon
sudo journalctl -u rag-daemon -f  # view logs
```

### No PDFs Found

- Check `/media/overwrite/Datenplatte\ 2/pdf-index.db` exists (FTS5 index)
- Run: `curl http://127.0.0.1:5555/health` (should return `{"status": "ok"}`)
- Check query latency < 100ms (means RAG-Daemon responded)

### Browser Not Opening

Set DISPLAY manually:
```bash
DISPLAY=:1 xdg-open /home/overwrite/Dokumente/REPORT-*.html
```

Or check: `ls -la /tmp/.X11-unix/` (should have X1 socket)

## Integration with Brauerei-Automation

This skill is part of the **Unified PDF-Search Workflow v2.0**:

- **Script location**: `~/brauerei-automation/pdf-search.sh`
- **RAG backend**: `~/brauerei-automation/rag-daemon.py` (running as systemd service)
- **CLI wrapper**: `~/brauerei-automation/rag-cli.sh` (direct API testing)
- **Data sources**: 8481 PDFs indexed in `/media/overwrite/Datenplatte\ 2/pdf-index.db`

## Advanced: Batch Queries

To run multiple queries and save reports:

```bash
for query in "pilze" "rezepte lamm" "fermentation"; do
  /home/overwrite/brauerei-automation/pdf-search.sh "$query"
  sleep 5
done
```

All reports go to `~/Dokumente/`, timestamped & unique.

## Technical Details

### Dependencies

- **curl**: HTTP client for RAG-Daemon API
- **jq**: JSON parsing (extract answer, sources, latency)
- **bash**: Script runtime (GNU compatible)
- **python3**: HTML generation (built-in libs only: no dependencies)
- **xdg-open**: Desktop integration (Linux standard)

### Architecture

```
pdf-search.sh
├─ POST /ask → RAG-Daemon :5555
│  └─ Response: {answer, latency_ms, sources: [pdfs...]}
├─ For each PDF:
│  └─ POST /ask → RAG-Daemon :5555 (detailed analysis query)
├─ Generate HTML (Python one-liner)
└─ Open in browser (xdg-open)
```

No external LLM calls, all local GPU (qwen3:14b on RTX 5080).

## Monitoring & Logs

### RAG-Daemon Logs

```bash
sudo journalctl -u rag-daemon --since "1 hour ago" -f
```

### Query Cache Stats

```bash
curl http://127.0.0.1:5555/stats | jq
# Returns: total queries, cache hits, avg latency
```

### PDF Index Status

```bash
ls -lh /media/overwrite/Datenplatte\ 2/pdf-index.db
# Should be 400-500 MB (FTS5 with 8481 PDFs)
```

---

**Tool Version**: v2.0  
**Last Updated**: 2026-03-18  
**Maintainer**: Overwrite (KI-Assistant)
