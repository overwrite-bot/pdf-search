# PDF Search Skill für OpenClaw

Ein vollständig integriertes PDF-Suchtool für OpenClaw mit TOC (Table of Contents) Optimierung, Caching und intelligenter Relevanzberechnung.

## 🎯 Features

- **5 Integrierte Tools** für OpenClaw
- **TOC-Optimierte Suche** — Kapitel-Aware für bessere Relevanz
- **Performance-Caching** — 30 Sekunden Cache für häufige Anfragen
- **8.482 PDFs** vollständig indiziert
- **95% Datenqualität** (>5KB Content pro PDF)
- **Intelligente Formatierung** — Optimiert für OpenClaw/WhatsApp

## 📦 Installation

Das Skill ist bereits in OpenClaw unter `/home/overwrite/.openclaw/extensions/pdf-search-skill/` installiert.

## 🔧 Verfügbare Tools

### 1. PDF durchsuchen (Standard)
Sucht nach Büchern/Themen in der PDF-Sammlung.

**OpenClaw:** Der Agent nutzt dieses Tool automatisch
**CLI:** `pdf-search search "python"`

### 2. Intelligente PDF-Suche (TOC-optimiert) ⭐
Sucht mit Priorität auf Inhaltsverzeichnis — bessere Relevanz!

**Besonderheit:** Findet relevante Treffer zuerst, basierend auf:
- Treffer in der TOC-Struktur (höchste Priorität)
- Treffer im Dateinamen
- Treffer im Inhalt

**OpenClaw:** Automatisch bei allgemeinen PDF-Anfragen
**CLI:** `pdf-search search-toc "meditation"`

### 3. Zitat suchen
Sucht nach genauen Zitaten und Textpassagen in PDFs.

**OpenClaw:** `"Finde mir ein Zitat über Quantenmechanik"`
**CLI:** `pdf-search quote "neural networks"`

### 4. Inhaltsverzeichnis anzeigen
Zeigt Kapitel-Struktur eines PDFs (wenn vorhanden).

**OpenClaw:** `"Zeige mir die Kapitel von PDF 4193"`
**CLI:** `pdf-search toc 4193`

### 5. PDF-Inhalt abrufen
Holt den kompletten Inhalt eines PDFs (max. 2000 Zeichen).

**OpenClaw:** `"Zeige mir das Inhaltsverzeichnis von..."`
**CLI:** `pdf-search content 2221`

## 📊 Index-Statistiken

```
Total PDFs: 8.482
PDFs mit Content: 8.482 (100%)
PDFs mit TOC: 5.050 (59.5%)

Content-Qualität:
  ✅ > 5KB: 8.061 (95.0%)
  ⚠️  500-5KB: 92 (1.1%)
  ❌ < 500B: 329 (3.9%)

Kategorien:
  tech: 6.873
  general: 817
  health: 405
  cooking: 214
  esoterik: 90
  philosophy: 83
```

## 🚀 Performance

- **Suche:** < 1 Sekunde (FTS5 optimiert)
- **Caching:** 30 Sekunden für häufige Anfragen
- **TOC-Suche:** < 2 Sekunden
- **Timeout:** 10 Sekunden pro Operation

## 🛠️ Technologie

- **Backend:** Node.js + Python 3
- **Datenbank:** SQLite mit FTS5 (Full-Text-Search)
- **Indexierung:** `/media/overwrite/Datenplatte 2/pdf-index.db`
- **Tools:**
  - `pdf-search-tool.py` — Standard-Suche
  - `pdf-search-enhanced.py` — TOC-optimierte Suche

## 📋 Architektur

```
OpenClaw Agent
    ↓
pdf-search-skill/index.js (5 Tools)
    ↓
┌─────────────────────────────┐
│ Python Tools                │
├─────────────────────────────┤
│ • pdf-search-tool.py        │ (Standard)
│ • pdf-search-enhanced.py    │ (TOC-aware)
└─────────────────────────────┘
    ↓
SQLite FTS5 Database
/media/overwrite/Datenplatte 2/pdf-index.db
    ↓
8.482 PDFs
```

## 🔍 Beispiele

### Suche nach "Meditation"

**CLI:**
```bash
pdf-search search-toc "meditation"
```

**Ausgabe:**
```
🎯 Intelligente PDF-Suche für "meditation"
📚 5 Ergebnis(se) gefunden (TOC-optimiert):

1. 📑 Ajahn Brahm - Meditation Kraft und Klarheit für den Geist.pdf
   📁 tech | Relevanz: 7/10
   💭 "MEDITATION Kraft und Klarheit für den Geist..."

2. Aleister Crowley - Meditation.pdf
   📁 tech | Relevanz: 7/10
   💭 "BOOK 4 MEDITATION THE WAY OF ATTAINMENT..."
```

### Inhaltsverzeichnis abrufen

**CLI:**
```bash
pdf-search toc 4193
```

**Ausgabe:**
```
📑 Inhaltsverzeichnis
📄 Dion Fortune - Die Seepriesterin.pdf

Kapitel (15 / 33):

1. Kapitel 1........................................................................................................................... 3
2. Kapitel 2......................................................................................................................... 10
...
```

## 🔐 Sicherheit

- ✅ Timeouts für alle Python-Operationen (10s)
- ✅ Input-Escaping für Shell-Commands
- ✅ Error-Handling für korrupte PDFs
- ✅ Maximal 50MB Buffer pro Operation

## 📝 Bash-Alias

```bash
# Standard-Suche
pdf-search search "python"

# TOC-optimierte Suche (empfohlen!)
pdf-search search-toc "meditation"

# Zitat-Suche
pdf-search quote "neural networks"

# Inhaltsverzeichnis
pdf-search toc 4193

# PDF-Inhalt
pdf-search content 2221
```

Die Aliases sind in `~/.bash_aliases` definiert.

## 🔄 Reboot-Stabilität

Das Skill ist vollständig reboot-stabil:
- ✅ OpenClaw startet automatisch (@reboot)
- ✅ PDF-Index ist persistent
- ✅ Cache wird bei jedem Start gelöscht
- ✅ Alle Abhängigkeiten sind verfügbar

## 📞 Support

Bei Fehlern:
1. Prüfe ob OpenClaw läuft: `ps aux | grep openclaw`
2. Prüfe PDF-Datenbank: `ls -l /media/overwrite/Datenplatte\ 2/pdf-index.db`
3. Teste direktes Tool: `python3 /home/overwrite/.openclaw/tools/pdf-search-tool.py search "test"`

## 📄 Lizenz

MIT

---

**Letztes Update:** März 2026
**Kompatibilität:** OpenClaw 2026.3+
