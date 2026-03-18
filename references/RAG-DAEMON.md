# RAG-Daemon v0.5 Backend Reference

The pdf-search skill relies on RAG-Daemon (Retrieval-Augmented Generation) running locally.

## Architecture

```
pdf-search.sh
    ↓
[curl POST /ask] → RAG-Daemon :5555
    ↓
RAG-Daemon searches (in order):
  1. Kiwix (Wikipedia Offline) :8080
  2. memory.db (local notes)
  3. kb.db (knowledge base)
  4. pdf-index.db (FTS5, 8481 PDFs indexed)
    ↓
[Context aggregation]
    ↓
[Ollama qwen3:14b] (GPU: RTX 5080, 14GB VRAM)
    ↓
[JSON Response: {answer, latency_ms, sources}]
    ↓
pdf-search.sh parses & generates HTML
```

## API Reference

### POST /ask

**Endpoint:** `http://127.0.0.1:5555/ask`

**Request:**
```json
{
  "query": "Your question here"
}
```

**Response:**
```json
{
  "answer": "AI-generated answer",
  "latency_ms": 12.5,
  "sources": [
    "/path/to/pdf1.pdf",
    "/path/to/pdf2.pdf",
    ...
  ]
}
```

**Notes:**
- Latency includes search + LLM inference
- Cached queries return <1ms
- Returns up to 5 sources (top matches)

### GET /health

**Endpoint:** `http://127.0.0.1:5555/health`

**Response:**
```json
{
  "status": "ok",
  "kiwix": "ok",
  "ollama": "ok",
  "databases": "ok"
}
```

### GET /stats

**Endpoint:** `http://127.0.0.1:5555/stats`

**Response:**
```json
{
  "total_queries": 1523,
  "cache_hits": 897,
  "avg_latency_ms": 8.3,
  "uptime_seconds": 86400
}
```

## Data Sources (Priority Order)

### 1. Kiwix (Wikipedia Offline)

- **Port:** 8080
- **Source:** German Wikipedia dump (2026-01)
- **Size:** ~49 GB
- **File:** `/media/overwrite/Datenplatte\ 1/wikipedia/wikipedia_de_all_maxi_2026-01.zim`
- **Search method:** HTTP `/search?pattern=<query>`

### 2. memory.db (Local Notes)

- **Path:** `/media/overwrite/Datenplatte\ 2/memory.db`
- **Type:** SQLite
- **Content:** Daily notes, knowledge entries (~11.5k notes)
- **Search method:** Full-text search + LIKE queries
- **Schema:** `notes(id, date, content, tags)`

### 3. kb.db (Knowledge Base)

- **Path:** `/media/overwrite/Datenplatte\ 2/kb.db`
- **Type:** SQLite
- **Content:** Structured knowledge (recipes, techniques, etc.)
- **Search method:** Schema-aware queries
- **Schema:** Domain-specific tables (recipes, ingredients, etc.)

### 4. pdf-index.db (FTS5 Full-Text Index)

- **Path:** `/media/overwrite/Datenplatte\ 2/pdf-index.db`
- **Type:** SQLite FTS5
- **Content:** 8481 PDFs indexed (book collection)
- **Size:** ~494 MB
- **Search method:** Wildcard queries ("pilz*" → prefix matching)
- **Return:** Filenames + snippet (32-char context)

## Performance Tuning

### Cache Hit Rate

RAG-Daemon caches frequently queried results:

```bash
# Check cache efficiency
curl http://127.0.0.1:5555/stats | jq .cache_hits
```

Cache is LRU (Least Recently Used), 3600s TTL.

### Latency Bottlenecks

1. **Kiwix search:** ~2-3ms (fast)
2. **PDF FTS5:** ~1-2ms (index lookup)
3. **Ollama inference:** 5-10ms (on GPU)
4. **Total:** 10-15ms typical, <1ms cached

### GPU Utilization

- **Model:** qwen3:14b
- **GPU:** NVIDIA RTX 5080 (16 GB VRAM)
- **VRAM usage:** ~14 GB (model) + ~2 GB (context/batch)
- **GPU load:** 85-90% during inference
- **Throughput:** 3-5 tokens/second (reasonably fast)

## Systemd Services

### rag-daemon.service

```bash
# Check status
sudo systemctl status rag-daemon

# View live logs
sudo journalctl -u rag-daemon -f

# Restart
sudo systemctl restart rag-daemon
```

**Service file:** `/etc/systemd/system/rag-daemon.service`

**Auto-boot:** Enabled (starts on system boot)

**Restart policy:** on-failure (5 retries within 300s)

### kiwix.service

Runs before RAG-Daemon (dependency).

```bash
sudo systemctl status kiwix
sudo journalctl -u kiwix -f
```

## Troubleshooting

### RAG-Daemon Not Responding

```bash
# Check if service is running
sudo systemctl status rag-daemon

# Try manual start
sudo systemctl start rag-daemon

# View detailed logs
sudo journalctl -u rag-daemon -n 50

# Test connectivity
curl http://127.0.0.1:5555/health

# Check port
lsof -i :5555
```

### No Results Found

**Symptoms:** Query returns `answer: ""`, `sources: []`

**Diagnosis:**
1. Check Kiwix: `curl http://127.0.0.1:8080/search?pattern=test`
2. Check PDF index: `ls -lh /media/overwrite/Datenplatte\ 2/pdf-index.db`
3. Check memory/kb databases exist and readable

**Fix:**
```bash
# Verify mount
mount | grep Datenplatte

# If missing, remount
sudo mount /dev/sdc1 /media/overwrite/Datenplatte\ 2/

# Restart RAG-Daemon
sudo systemctl restart rag-daemon
```

### Slow Latency (>100ms)

**Causes:**
- GPU under other load
- Kiwix search slow
- Ollama model unloaded (cold start)

**Check:**
```bash
# GPU status
nvidia-smi

# Kiwix response time
time curl http://127.0.0.1:8080/search?pattern=test

# Ollama status
sudo systemctl status ollama
```

### Out of Memory

**Symptoms:** Ollama crashes, RAG-Daemon hangs

**Check GPU VRAM:**
```bash
nvidia-smi

# Should show ~14GB used by qwen3:14b
```

**Workaround:** Restart Ollama
```bash
sudo systemctl restart ollama
```

## Database Maintenance

### PDF Index Rebuild

If FTS5 index is corrupted:

```bash
# Backup current index
cp /media/overwrite/Datenplatte\ 2/pdf-index.db \
   /media/overwrite/Datenplatte\ 2/pdf-index.db.backup

# Trigger rebuild (via RAG-Daemon admin endpoint, if available)
# Or manually reinitialize with index_pdfs.py script
```

### Cache Clear

```bash
# RAG-Daemon cache can't be manually cleared (TTL: 3600s)
# To force clear: restart service
sudo systemctl restart rag-daemon
```

## Production Checklist

- [ ] RAG-Daemon running: `sudo systemctl status rag-daemon`
- [ ] Kiwix running: `sudo systemctl status kiwix`
- [ ] PDF index exists: `ls -lh /media/overwrite/Datenplatte\ 2/pdf-index.db`
- [ ] GPU available: `nvidia-smi | grep qwen`
- [ ] Health check passes: `curl http://127.0.0.1:5555/health`
- [ ] Sample query works: `curl -X POST http://127.0.0.1:5555/ask -d '{"query":"test"}'`

---

**Version:** 0.5  
**Last Updated:** 2026-03-18  
**Maintainer:** Overwrite (KI-Assistant)
