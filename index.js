#!/usr/bin/env node

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const TOOL_PATH = "/home/overwrite/.openclaw/tools/pdf-search-tool.py";
const TOOL_ENHANCED_PATH = "/home/overwrite/.openclaw/tools/pdf-search-enhanced.py";

// Cache für häufige Anfragen (30 Sekunden)
const searchCache = new Map();
const CACHE_DURATION = 30000;

/**
 * Cache-Wrapper für Suchanfragen
 */
function getCachedSearch(cacheKey, fetchFn) {
  if (searchCache.has(cacheKey)) {
    const cached = searchCache.get(cacheKey);
    if (Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    } else {
      searchCache.delete(cacheKey);
    }
  }

  const result = fetchFn();
  if (!result.error) {
    searchCache.set(cacheKey, { data: result, timestamp: Date.now() });
  }
  return result;
}

/**
 * Führt das Python-Suchtool aus
 */
function executePdfTool(command, query) {
  try {
    const escapedQuery = query ? `"${query.replace(/"/g, '\\"')}"` : "";
    const result = execSync(
      `python3 "${TOOL_PATH}" ${command} ${escapedQuery}`,
      { encoding: "utf-8", maxBuffer: 50 * 1024 * 1024, timeout: 10000 }
    );
    return JSON.parse(result);
  } catch (error) {
    return {
      error: `PDF-Tool Fehler: ${error.message}`,
      code: error.code,
    };
  }
}

/**
 * Führt das Enhanced Python-Suchtool aus
 */
function executeEnhancedTool(command, query) {
  try {
    const escapedQuery = query ? `"${query.replace(/"/g, '\\"')}"` : "";
    const result = execSync(
      `python3 "${TOOL_ENHANCED_PATH}" ${command} ${escapedQuery}`,
      { encoding: "utf-8", maxBuffer: 50 * 1024 * 1024, timeout: 10000 }
    );
    return JSON.parse(result);
  } catch (error) {
    return {
      error: `Enhanced-Tool Fehler: ${error.message}`,
      code: error.code,
    };
  }
}

/**
 * Sucht in PDFs nach Büchern/Themen
 * @param {string} query - Suchtext
 * @returns {object} - Suchergebnisse
 */
function searchPdfs(query) {
  if (!query) {
    return { error: "Suchtext erforderlich" };
  }

  const cacheKey = `search:${query}`;
  return getCachedSearch(cacheKey, () => {
    return executePdfTool("search", query);
  });
}

/**
 * Sucht nach genauen Zitaten in PDFs
 * @param {string} query - Zitat/Text zum Suchen
 * @returns {object} - Zitate mit Context
 */
function findQuote(query) {
  if (!query) {
    return { error: "Suchtext erforderlich" };
  }
  return executePdfTool("quote", query);
}

/**
 * Holt den kompletten Inhalt eines PDFs
 * @param {number} pdfId - ID des PDFs aus der Datenbank
 * @returns {object} - PDF-Inhalt
 */
function getPdfContent(pdfId) {
  if (!pdfId) {
    return { error: "PDF-ID erforderlich" };
  }
  return executePdfTool("content", pdfId.toString());
}

/**
 * Enhanced Search mit TOC-Priorität
 * @param {string} query - Suchtext
 * @returns {object} - Suchergebnisse mit TOC-Awareness
 */
function searchWithToc(query) {
  if (!query) {
    return { error: "Suchtext erforderlich" };
  }

  const cacheKey = `toc:${query}`;
  return getCachedSearch(cacheKey, () => {
    return executeEnhancedTool("search", query);
  });
}

/**
 * Holt TOC (Table of Contents) eines PDFs
 * @param {number} pdfId - PDF-ID
 * @returns {object} - TOC-Zusammenfassung mit Kapiteln
 */
function getTocSummary(pdfId) {
  if (!pdfId) {
    return { error: "PDF-ID erforderlich" };
  }
  const pythonPath = "/home/overwrite/.openclaw/tools/pdf-search-enhanced.py";
  try {
    const result = execSync(
      `python3 "${pythonPath}" toc ${pdfId}`,
      { encoding: "utf-8", maxBuffer: 50 * 1024 * 1024 }
    );
    return JSON.parse(result);
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Universal Meta-Search über alle Quellen
 * @param {string} query - Suchtext
 * @returns {object} - Ergebnisse von PDFs, KB, Memory, Wikipedia
 */
function universalSearch(query) {
  if (!query) {
    return { error: "Suchtext erforderlich" };
  }

  const cacheKey = `universal:${query}`;
  return getCachedSearch(cacheKey, () => {
    return executeUniversalTool(query);
  });
}

/**
 * Führt das Universal-Search-Tool aus
 */
function executeUniversalTool(query) {
  try {
    const escapedQuery = query ? `"${query.replace(/"/g, '\\"')}"` : "";
    const result = execSync(
      `python3 "/home/overwrite/.openclaw/tools/universal-search.py" ${escapedQuery}`,
      { encoding: "utf-8", maxBuffer: 50 * 1024 * 1024, timeout: 10000 }
    );
    return JSON.parse(result);
  } catch (error) {
    return {
      error: `Universal-Search Fehler: ${error.message}`,
      code: error.code,
    };
  }
}

/**
 * Formatiert Suchergebnisse für OpenClaw (bessere Markdown-Formatierung)
 */
function formatSearchResults(results) {
  if (!results || !Array.isArray(results) || results.length === 0) {
    return "❌ Keine Ergebnisse gefunden.";
  }

  let output = `📚 **${results.length} Ergebnis(se) gefunden:**\n\n`;

  results.forEach((result, i) => {
    output += `**${i + 1}. ${result.filename}**\n`;
    if (result.category) {
      output += `   📁 Kategorie: *${result.category}*\n`;
    }
    const snippet = result.snippet.substring(0, 120).replace(/\n/g, " ").trim();
    output += `   💭 \"${snippet}...\"\n\n`;
  });

  return output;
}

/**
 * Formatiert Zitate für OpenClaw (bessere Markdown-Formatierung)
 */
function formatQuotes(quotes) {
  if (!quotes || quotes.length === 0) {
    return "❌ Kein passendes Zitat gefunden.";
  }

  let output = `💬 **${quotes.length} Zitat(e) gefunden:**\n\n`;

  quotes.forEach((quote, i) => {
    output += `**${i + 1}. ${quote.filename}**\n`;
    output += "```\n";
    const text = quote.quote.substring(0, 250).trim();
    output += text;
    if (quote.quote.length > 250) {
      output += " ...";
    }
    output += "\n```\n\n";
  });

  return output;
}

// OpenClaw Tool Export
const tools = {
  "pdf-search:search": {
    label: "PDF durchsuchen",
    description: "Sucht in deiner PDF-Sammlung nach Büchern/Themen",
    handler: (query) => {
      const results = searchPdfs(query);
      if (results.error) return `Fehler: ${results.error}`;
      return formatSearchResults(results.results);
    }
  },
  "pdf-search:quote": {
    label: "Zitat suchen",
    description: "Sucht nach genauen Zitaten in deinen PDFs",
    handler: (query) => {
      const quotes = findQuote(query);
      if (quotes.error) return `Fehler: ${quotes.error}`;
      return formatQuotes(quotes.quotes);
    }
  },
  "pdf-search:content": {
    label: "PDF-Inhalt abrufen",
    description: "Holt den kompletten Inhalt eines spezifischen PDFs",
    handler: (pdfId) => {
      const content = getPdfContent(parseInt(pdfId));
      if (content.error) return `Fehler: ${content.error}`;
      return `📖 **${content.filename}**\n\n${content.content}`;
    }
  },
  "pdf-search:search-toc": {
    label: "Intelligente PDF-Suche (mit TOC)",
    description: "Sucht mit Priorität auf Inhaltsverzeichnis - bessere Relevanz!",
    handler: (query) => {
      const results = searchWithToc(query);
      if (results.error) return `❌ ${results.error}`;
      if (!results.results || results.results.length === 0) {
        return `❌ Keine Ergebnisse für: "${query}"`;
      }
      let output = `🎯 **Intelligente PDF-Suche** für "${query}"\n`;
      output += `📚 **${results.results.length} Ergebnis(se)** gefunden (TOC-optimiert):\n\n`;
      results.results.forEach((r, i) => {
        const tocMark = r.has_toc ? '📑 ' : '';
        output += `**${i + 1}. ${tocMark}${r.filename}**\n`;
        output += `   📁 *${r.category || 'allgemein'}* | Relevanz: ${r.score}/10\n`;
        const snippet = r.snippet.substring(0, 120).replace(/\n/g, " ").trim();
        output += `   💭 \"${snippet}...\"\n\n`;
      });
      return output;
    }
  },
  "pdf-search:toc": {
    label: "Inhaltsverzeichnis anzeigen",
    description: "Zeigt Kapitel-Überblick eines PDFs",
    handler: (pdfId) => {
      const toc = getTocSummary(parseInt(pdfId));
      if (toc.error) return `❌ ${toc.error}`;
      if (!toc.has_toc) {
        return `⚠️ **${toc.filename}**\nKein Inhaltsverzeichnis in dieser PDF verfügbar.`;
      }
      let output = `📑 **Inhaltsverzeichnis**\n`;
      output += `📄 *${toc.filename}*\n\n`;
      output += `**Kapitel (${toc.chapters.length} / ${toc.total_lines}):**\n\n`;
      toc.chapters.forEach((ch, i) => {
        // Entferne übermäßige Punkte
        const cleaned = ch.replace(/\.{3,}/g, "...");
        output += `${i + 1}. ${cleaned}\n`;
      });
      return output;
    }
  },
  "pdf-search:universal": {
    label: "Universelle Metasuche",
    description: "Durchsucht ALLES: PDFs, Wikipedia, Knowledge Base, Memory",
    handler: (query) => {
      const results = universalSearch(query);
      if (results.error) return `❌ ${results.error}`;
      return results.formatted || "Keine Ergebnisse";
    }
  }
};

// Export für Node.js require/import
module.exports = {
  searchPdfs,
  findQuote,
  getPdfContent,
  searchWithToc,
  getTocSummary,
  universalSearch,
  formatSearchResults,
  formatQuotes,
  tools
};

// CLI-Nutzung
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const query = args.slice(1).join(" ");

  if (command === "universal") {
    const results = universalSearch(query);
    if (results.error) {
      console.error("Fehler:", results.error);
    } else {
      console.log(results.formatted || "Keine Ergebnisse");
      console.log(`\n📊 Quellen: PDFs: ${results.sources?.pdfs || 0} | KB: ${results.sources?.kb || 0} | Memory: ${results.sources?.memory || 0} | Wikipedia: ${results.sources?.wikipedia || 0}`);
    }
  } else if (command === "search") {
    const results = searchPdfs(query);
    if (!results) {
      console.error("Fehler: Keine Ergebnisse");
    } else if (results.error) {
      console.error("Fehler:", results.error);
    } else {
      console.log(formatSearchResults(results.results));
    }
  } else if (command === "search-toc") {
    const results = searchWithToc(query);
    if (results.error) {
      console.error("Fehler:", results.error);
    } else if (!results.results || results.results.length === 0) {
      console.log(`Keine Ergebnisse für: ${query}`);
    } else {
      console.log(`📚 ${results.results.length} Ergebnis(se) (TOC-optimiert):\n`);
      results.results.forEach((r, i) => {
        console.log(`${i + 1}. ${r.filename} ${r.has_toc ? "📑" : ""}`);
        console.log(`   Kategorie: ${r.category || "unbekannt"}`);
        console.log(`   Score: ${r.score}, TOC: ${r.has_toc}`);
        console.log(`   Auszug: ${r.snippet.substring(0, 150)}...\n`);
      });
    }
  } else if (command === "quote") {
    const quotes = findQuote(query);
    if (!quotes) {
      console.error("Fehler: Keine Zitate gefunden");
    } else if (quotes.error) {
      console.error("Fehler:", quotes.error);
    } else {
      console.log(formatQuotes(quotes.quotes));
    }
  } else if (command === "toc") {
    const toc = getTocSummary(parseInt(query));
    if (toc.error) {
      console.error("Fehler:", toc.error);
    } else if (!toc.has_toc) {
      console.log(`⚠️ ${toc.filename} - Kein Inhaltsverzeichnis`);
    } else {
      console.log(`📑 ${toc.filename}\n`);
      console.log(`Kapitel (${toc.chapters.length} von ${toc.total_lines}):\n`);
      toc.chapters.forEach((ch, i) => {
        console.log(`${i + 1}. ${ch}`);
      });
    }
  } else if (command === "content") {
    const content = getPdfContent(parseInt(query));
    if (!content) {
      console.error("Fehler: PDF nicht gefunden");
    } else if (content.error) {
      console.error("Fehler:", content.error);
    } else {
      console.log(`📖 ${content.filename}\n\n${content.content}`);
    }
  } else {
    console.log("🔍 PDF-Search Skill v2.1 - Universal Meta-Search");
    console.log("==================================================");
    console.log("Verwendung:");
    console.log("  node index.js search <query>        - Sucht nach PDFs");
    console.log("  node index.js search-toc <query>    - Sucht mit TOC-Priorität");
    console.log("  node index.js universal <query>     - 🌟 ALLES durchsuchen (PDFs+KB+Memory+Wiki)");
    console.log("  node index.js quote <text>          - Sucht nach Zitaten");
    console.log("  node index.js toc <id>              - Zeigt Inhaltsverzeichnis");
    console.log("  node index.js content <id>          - Holt PDF-Inhalt");
  }
}
