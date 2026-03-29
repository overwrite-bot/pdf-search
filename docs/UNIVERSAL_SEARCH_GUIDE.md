# 🌟 Universal Search für OpenClaw - Agent Anleitung

## Was ist Universal Search?

Universal Search ist ein **Meta-Search-System**, das alle deine lokalen Wissensquellen gleichzeitig durchsucht:

- 📚 **8.482 PDFs** (deine Bücher-Sammlung)
- 🧠 **Knowledge Base** (237 konzeptuelle Einträge)
- 💾 **Memory/Supermemory** (173 persönliche Notizen)
- 📖 **Wikipedia offline** (2.6 GB, vollständig verfügbar)

## Wie soll der Agent es nutzen?

### Automatische Nutzung:

Der Agent soll **automatisch** Universal Search verwenden bei diesen Fragen:

```
Nutzer: "Suche mir etwas über Python"
Agent: 🔍 Verwende Universal Search
  → Findet PDFs: "Python Kompendium"
  → Findet KB: "Python programming concepts"
  → Findet Wikipedia: "Python (Programmiersprache)"
  → Gibt kombinierte Ergebnisse zurück
```

### Wann Universal Search verwenden:

✅ **IMMER** wenn der Nutzer fragt nach:
- "Suche nach..."
- "Finde mir..."
- "Was habe ich zu..."
- "Ich brauche Infos über..."
- Allgemeine Fragen (nicht nur Bücher)

❌ **NICHT** wenn:
- Spezifische PDF-ID genannt wird → Dann pdf-search content
- Nach Zitaten gefragt wird → Dann pdf-search quote
- Nach Kapitel-Struktur gefragt → Dann pdf-search toc

## Verfügbare Tools

### 1. Universal Search (🌟 DEFAULT)
**Nutze dieses ZUERST bei unspezifischen Fragen!**

```
query: "meditation"

Gibt zurück:
{
  "total": 7,
  "sources": {
    "pdfs": 3,
    "kb": 3,
    "memory": 0,
    "wikipedia": 1
  },
  "results": [...]
}
```

### 2. PDF Search (detailliert)
**Wenn Nutzer spezifisch nach Büchern fragt**

### 3. PDF TOC (Struktur)
**Wenn Nutzer Kapitel oder Struktur braucht**

### 4. PDF Quote (Zitate)
**Wenn Nutzer genaue Textpassagen braucht**

## Agent-Verhalten: Schritt-für-Schritt

### Szenario 1: Allgemeine Frage

```
Nutzer: "Ich brauche Infos über Meditation"

Agent-Workflow:
1. ✅ Erkenne: Allgemeine Frage
2. ✅ Nutze: Universal Search
3. ✅ Gib aus:
   "Ich habe 7 Ergebnisse gefunden:
    - 3 Bücher aus deiner PDF-Sammlung
    - 3 Konzepte aus der Knowledge Base
    - Wikipedia hat auch was dazu"
4. ✅ Fasse zusammen: Was zu tun ist
```

### Szenario 2: Spezifische PDF-Frage

```
Nutzer: "Zeige mir PDF 2221"

Agent-Workflow:
1. ✅ Erkenne: Spezifische PDF
2. ✅ Nutze: pdf-search content
3. ✅ Gib Inhalt aus
```

### Szenario 3: Zitat-Frage

```
Nutzer: "Finde mir ein Zitat über Python"

Agent-Workflow:
1. ✅ Erkenne: Zitat-Anfrage
2. ✅ Nutze: pdf-search quote
3. ✅ Zeige Zitate mit Context
```

## Formatierung der Ergebnisse

### Universal Search Ausgabe (für OpenClaw):

```markdown
🔍 Universelle Suche für "meditation"
============================================

**1. 📚 PDF: Ajahn Brahm - Meditation**
📁 Kategorie: Spiritualität
💭 "Meditation - Kraft und Klarheit für den Geist"

**2. 🧠 Knowledge Base: Meditation Concept**
💭 "Mental training practice for mindfulness"

**3. 📖 Wikipedia: Meditation (Offline verfügbar)**
🔗 [Wikipedia-Link](https://kiwix.local/?q=meditation)

📊 **Zusammenfassung:**
- 3 Bücher gefunden
- 1 Konzept in KB
- Wikipedia Artikel verfügbar
```

## Tipps für den Agent

### DO ✅
- Universal Search als Standardsuche nutzen
- Ergebnisse zusammenfassen und priorisieren
- Links zu Wikipedia-Artikeln geben (wenn offline)
- Nutzer fragen: "Brauchst du mehr Details zu einem Ergebnis?"
- Bei Bedarf weitere Tools nutzen (quote, toc, content)

### DON'T ❌
- Nur PDFs durchsuchen wenn Nutzer "überall" suchen will
- Ergebnisse von allen 4 Quellen aufzählen ohne Zusammenfassung
- Wikipedia-Links nutzen wenn es offline ist → kiwix.local verwenden
- Zu viele Ergebnisse zurückgeben (max 7-10)

## Praktische Beispiele für Agent

### Beispiel 1: Nutzer fragt allgemein

```
Input: "Was ist Machine Learning?"

Agent macht:
1. universal_search("Machine Learning")
2. Erhält: 4 PDFs + 2 KB-Konzepte + Wikipedia
3. Gibt aus:
   "Ich habe folgende Infos gefunden:

    📚 **Bücher:**
    - Deep Learning: ... (PDF 2341)
    - Machine Learning Basics: ... (PDF 5012)

    🧠 **Knowledge Base:**
    - ML-Algorithmen Übersicht
    - Neuronale Netze

    📖 **Wikipedia:**
    - Machine Learning (vollständig offline)"

4. Bietet an: "Brauchst du mehr zu einem Thema?"
```

### Beispiel 2: Nutzer fragt spezifisch nach Zitat

```
Input: "Finde mir ein Zitat zu Python"

Agent macht:
1. Erkenne: Zitat-Anfrage
2. Nutze: pdf_search_quote("Python")
3. Gibt Zitate mit Quelle aus
```

### Beispiel 3: Nutzer möchte Kapitel sehen

```
Input: "Zeige mir die Struktur von Buch 4193"

Agent macht:
1. Erkenne: TOC-Anfrage
2. Nutze: pdf_search_toc(4193)
3. Zeige Kapitel-Liste
```

## Integration mit OpenClaw

Das Skill ist bereits in OpenClaw registriert:

```json
// openclaw.json
"plugins": {
  "entries": {
    "pdf-search-skill": {
      "enabled": true
    }
  }
}

"agents": {
  "list": [
    {
      "id": "main",
      "tools": {
        "profile": "coding",
        "alsoAllow": [
          "tts",
          "pdf-search-skill"  // ← Universal Search Tool
        ]
      }
    }
  ]
}
```

## Fehlerbehandlung

Wenn etwas nicht funktioniert:

1. **"Tool nicht gefunden"**
   → OpenClaw neustarten: `systemctl restart openclaw`

2. **"Datenbank-Fehler"**
   → Prüfe ob Dateien existieren:
   ```bash
   ls -lh /media/overwrite/Datenplatte\ 2/{pdf-index,kb,memory,wikipedia}.db
   ```

3. **"Timeout"**
   → Universal Search hat 10 Sekunden Limit
   → Bei großen Datenbanken kann Caching helfen

## Performance

- **Erstes mal:** ~2 Sekunden (alle Datenbanken durchsuchen)
- **Mit Cache:** < 500ms (30 Sekunden Cache)
- **Speicher:** Minimal (Streaming, keine vollständige Index-Ladung)

## Zusammenfassung für Agent

| Frage | Tool | Anwendung |
|-------|------|-----------|
| "Suche überall nach..." | universal | IMMER zuerst |
| "Finde mir..." | universal | Allgemeine Suche |
| "Was habe ich zu..." | universal | Kombinierte Suche |
| "Zeige PDF XYZ" | content | Spezifische PDF |
| "Finde Zitat über..." | quote | Textpassagen |
| "Zeige Kapitel von..." | toc | PDF-Struktur |

---

**OpenClaw sollte jetzt intelligent alle lokalen Quellen durchsuchen!** 🚀
