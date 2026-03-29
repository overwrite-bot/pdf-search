# PDF Search Skill

Durchsucht deine PDF-Sammlung (8.482 Bücher) und findet Zitate, Informationen und Inhalte.

## Überblick

Dieses Skill bietet Zugriff auf eine indizierte PDF-Datenbank mit über 8.000 Büchern. Du kannst:
- 📚 Nach Büchern und Themen suchen
- 💬 Genaue Zitate und Textpassagen finden
- 📖 Komplette PDF-Inhalte abrufen

## Installation

Das Skill ist bereits in OpenClaw aktiviert. Keine zusätzliche Installation nötig.

## Verfügbare Tools

### 1. PDF durchsuchen (Standard)
Sucht nach Büchern/Themen in der PDF-Sammlung
- **Kommando:** `search <query>`
- **Beispiel:** `pdf-search search "python"`

### 2. Intelligente PDF-Suche (TOC-optimiert) ⭐
Sucht mit Priorität auf Inhaltsverzeichnis — bessere Relevanz!
- **Kommando:** `search-toc <query>`
- **Beispiel:** `pdf-search search-toc "meditation"`
- **Vorteile:** Findet relevante Treffer zuerst basierend auf TOC

### 3. Zitat suchen
Sucht nach genauen Zitaten und Textpassagen
- **Kommando:** `quote <text>`
- **Beispiel:** `pdf-search quote "neural networks"`

### 4. Inhaltsverzeichnis anzeigen
Zeigt Kapitel-Überblick eines PDFs
- **Kommando:** `toc <pdf-id>`
- **Beispiel:** `pdf-search toc 4193`

### 5. PDF-Inhalt abrufen
Holt den kompletten Inhalt eines PDFs
- **Kommando:** `content <pdf-id>`
- **Beispiel:** `pdf-search content 2221`

## Durch OpenClaw-Agent

Der Agent nutzt alle Tools automatisch bei Fragen wie:

```
"Suche ein Buch über Machine Learning"
"Finde mir ein Zitat über Meditation"
"Zeige mir die Kapitel von PDF 4193"
"Was habe ich über Blockchain?"
```

## Kommandozeile

```bash
# Standard-Suche
pdf-search search "python"

# TOC-optimierte Suche (empfohlen!)
pdf-search search-toc "meditation"

# Nach Zitaten suchen
pdf-search quote "neural networks"

# Inhaltsverzeichnis anzeigen
pdf-search toc 4193

# PDF-Inhalt abrufen
pdf-search content 2221
```

## Datenbank

- **Pfad:** `/media/overwrite/Datenplatte 2/pdf-index.db`
- **PDFs:** 8.482 indexierte Bücher
- **Quelle:** `/media/overwrite/Datenplatte 1/Bücher/`

## Kategorien

- `health` — Gesundheit, Medizin, Wellness
- `tech` — Technologie, Programmierung, IT
- `philosophy` — Philosophie, Psychologie, Spiritualität
- `esoterik` — Esoterik, Okkultismus
- `cooking` — Kochen, Ernährung

## Ausgabe-Format

### Search
```json
{
  "results": [
    {
      "id": 2221,
      "filename": "Schmitt, Sarah - Python Kompendium.pdf",
      "path": "/media/overwrite/...",
      "category": "tech",
      "snippet": "..."
    }
  ]
}
```

### Quote
```json
{
  "quotes": [
    {
      "filename": "...",
      "quote": "...",
      "position": 1234
    }
  ]
}
```

## Technologie

- **Index:** SQLite FTS5 (Full Text Search)
- **API:** Node.js / Python
- **Kompression:** Zlib (für PDF-Inhalte)

## Performance

- **Suchen:** < 1 Sekunde (FTS5 optimiert)
- **Zitate:** < 2 Sekunden
- **Inhalte:** < 500ms pro PDF
