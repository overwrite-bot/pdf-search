#!/usr/bin/env python3
"""
Test Hybrid Search Integration in pdf_zusammenfassung Skill
Vergleicht: FTS5-only vs. Hybrid Search Ergebnisse
"""

import sys
from pathlib import Path
import sqlite3
import logging

# Add script dir to path
sys.path.insert(0, str(Path(__file__).parent))

from hybrid_search import hybrid_search_pdf_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF_INDEX_DB = Path("/media/overwrite/Datenplatte 2/pdf-index.db")

def test_hybrid_vs_fts5(query: str):
    """Test Hybrid Search vs. FTS5-only"""
    
    print(f"\n{'='*70}")
    print(f"TEST: '{query}'")
    print('='*70)
    
    # 1. FTS5-only Search
    print("\n[1] FTS5-Only Search:")
    print("-" * 70)
    
    try:
        conn = sqlite3.connect(PDF_INDEX_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        fts5_query = " OR ".join([f"{word}*" for word in query.split()])
        cursor.execute("""
            SELECT filename, rank, snippet(pdf_fts, 2, '', '', ' [...] ', 32) AS snippet
            FROM pdf_fts
            WHERE pdf_fts MATCH ?
            ORDER BY rank
            LIMIT 5
        """, (fts5_query,))
        
        fts5_results = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(fts5_results)} FTS5 results:\n")
        for i, row in enumerate(fts5_results, 1):
            print(f"{i}. {row['filename']}")
            print(f"   Rank: {row['rank']}")
            print(f"   Snippet: {row['snippet'][:100]}...")
            print()
    
    except Exception as e:
        logger.error(f"FTS5 search error: {e}")
        fts5_results = []
    
    # 2. Hybrid Search
    print("\n[2] Hybrid Search (BM25 + Embeddings):")
    print("-" * 70)
    
    hybrid_results = hybrid_search_pdf_index(
        query=query,
        db_path=PDF_INDEX_DB,
        max_results=5,
        bm25_weight=0.5,
        semantic_weight=0.5,
        min_semantic_score=0.25
    )
    
    print(f"Found {len(hybrid_results)} Hybrid results:\n")
    for i, result in enumerate(hybrid_results, 1):
        print(f"{i}. {result['filename']}")
        print(f"   Hybrid:   {result['hybrid_score']:.3f}")
        print(f"   BM25:     {result['bm25_score']:.3f}")
        print(f"   Semantic: {result['semantic_score']:.3f}")
        print(f"   Snippet:  {result['content'][:100]}...")
        print()
    
    # 3. Comparison
    print("\n[3] Vergleich:")
    print("-" * 70)
    
    fts5_filenames = {row['filename'] for row in fts5_results}
    hybrid_filenames = {r['filename'] for r in hybrid_results}
    
    overlap = fts5_filenames & hybrid_filenames
    only_fts5 = fts5_filenames - hybrid_filenames
    only_hybrid = hybrid_filenames - fts5_filenames
    
    print(f"FTS5-only Results:    {len(fts5_filenames)}")
    print(f"Hybrid Results:       {len(hybrid_filenames)}")
    print(f"Overlap (beide):      {len(overlap)}")
    print(f"Nur FTS5:             {len(only_fts5)} {list(only_fts5)[:2]}")
    print(f"Nur Hybrid:           {len(only_hybrid)} {list(only_hybrid)[:2]}")
    
    if only_hybrid:
        print(f"\n✅ Hybrid found {len(only_hybrid)} additional semantically relevant PDFs!")
    if only_fts5:
        print(f"\n⚠️  FTS5-only found {len(only_fts5)} keyword matches missed by Hybrid")

if __name__ == "__main__":
    test_queries = [
        "pilzbestimmung giftig",
        "fermentation temperatur",
        "rezept huhn",
        "säuerung gärung",
        "bier herstellung",
    ]
    
    if len(sys.argv) > 1:
        test_queries = [" ".join(sys.argv[1:])]
    
    for query in test_queries:
        test_hybrid_vs_fts5(query)
    
    print("\n" + "="*70)
    print("✅ Test Complete")
    print("="*70)
