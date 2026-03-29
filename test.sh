#!/bin/bash

echo "🧪 PDF-Search Skill v2.0 - Test Suite"
echo "======================================="
echo ""

# Test 1: Standard Suche
echo "Test 1: Standard PDF-Suche"
node index.js search "python" > /tmp/test1.out 2>&1
if grep -q "Bionische Regeneration" /tmp/test1.out; then
  echo "✅ PASSED"
else
  echo "❌ FAILED"
  cat /tmp/test1.out | head -5
fi
echo ""

# Test 2: TOC-optimierte Suche
echo "Test 2: TOC-optimierte Suche"
node index.js search-toc "meditation" > /tmp/test2.out 2>&1
if grep -q "Ajahn Brahm" /tmp/test2.out; then
  echo "✅ PASSED"
else
  echo "❌ FAILED"
  cat /tmp/test2.out | head -5
fi
echo ""

# Test 3: Zitat-Suche
echo "Test 3: Zitat-Suche"
node index.js quote "meditation" > /tmp/test3.out 2>&1
if grep -q "💬" /tmp/test3.out || grep -q "Zitat" /tmp/test3.out; then
  echo "✅ PASSED"
else
  echo "❌ FAILED"
  cat /tmp/test3.out | head -5
fi
echo ""

# Test 4: TOC anzeigen
echo "Test 4: Inhaltsverzeichnis"
node index.js toc 4193 > /tmp/test4.out 2>&1
if grep -q "Kapitel" /tmp/test4.out || grep -q "📑" /tmp/test4.out; then
  echo "✅ PASSED"
else
  echo "❌ FAILED"
  cat /tmp/test4.out | head -5
fi
echo ""

# Test 5: PDF-Inhalt
echo "Test 5: PDF-Inhalt abrufen"
node index.js content 2221 > /tmp/test5.out 2>&1
if grep -q "Python\|Bibliographische" /tmp/test5.out; then
  echo "✅ PASSED"
else
  echo "❌ FAILED"
  cat /tmp/test5.out | head -5
fi
echo ""

echo "======================================="
echo "✅ Alle Tests abgeschlossen!"
