#!/usr/bin/env python3
"""
PDF Categorization using German BERT (dbmdz/bert-base-german-uncased)
Replaces keyword-based categorization with neural embeddings + classification.

Categories: tech, cooking, health, philosophy, esoterik, general
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("❌ Missing dependencies: pip install sentence-transformers")
    sys.exit(1)

# Model: German BERT (multilingual, optimized for German)
# Alternative: "distiluse-base-multilingual-cased-v2" (faster, 40% smaller)
MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"

# Category definitions (for label embeddings)
CATEGORY_DEFINITIONS = {
    "tech": "Python C++ Java JavaScript programming software computer linux security database network algorithm developer system administration code",
    "cooking": "Rezept Kochen Backen Fermentieren Käse Fleisch Wurst Pilze Kräuter Zutaten Zubereitung Einmachen Brauerei Gärung Hefe recipe food fermentation",
    "health": "Medizin Therapie Heilung Gesundheit Yoga Wellness Ernährung Vitamin Massage Naturheilkunde Heilpflanze Ayurveda medicine healing health nutrition",
    "philosophy": "Philosophie Metaphysik Bewusstsein Existenz Ethik Kant Hegel Plato Nietzsche Logik philosophy metaphysics consciousness existence",
    "esoterik": "Spiritualität Meditation Mystik Chakra Aura Seele Erleuchtung Wiedergeburt Tarot Reiki Astrologie Okkult Bewusstsein spirituality mysticism occult",
    "general": "allgemein gemischt verschiedenes uncategorized reference knowledge"
}

class PDFCategorizer:
    def __init__(self, model_name: str = MODEL_NAME, db_path: Path = None):
        """Initialize BERT model and database connection"""
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        self.db_path = db_path or Path("/media/overwrite/Datenplatte 2/pdf-index.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Pre-compute category embeddings
        print("Computing category embeddings...")
        self.category_embeddings = {}
        for category, definition in CATEGORY_DEFINITIONS.items():
            embedding = self.model.encode(definition, convert_to_tensor=False)
            self.category_embeddings[category] = embedding
        
        print(f"✅ Model ready. {len(self.category_embeddings)} categories defined.")
    
    def categorize_pdf(self, filename: str, content: str = "", top_k: int = 1, threshold: float = 0.0) -> Tuple[str, float]:
        """
        Categorize single PDF using semantic similarity.
        
        Args:
            filename: PDF filename
            content: PDF content (first 500 chars)
            top_k: Return top K predictions
            threshold: Minimum confidence threshold (0.0 = always pick top-1)
        
        Returns:
            (category, confidence_score)
        """
        # Combine filename + content for better context
        text = f"{filename} {content[:300]}"
        text_embedding = self.model.encode(text, convert_to_tensor=False)
        
        # Compute cosine similarity to each category
        scores = {}
        for category, cat_embedding in self.category_embeddings.items():
            similarity = np.dot(text_embedding, cat_embedding) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(cat_embedding) + 1e-10
            )
            scores[category] = float(similarity)
        
        # Sort by score (always pick top-1, no threshold)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_category, best_score = ranked[0]
        
        return best_category, best_score
    
    def categorize_all_pdfs(self, batch_size: int = 100, dry_run: bool = False) -> Dict[str, int]:
        """
        Categorize all PDFs in database using BERT.
        
        Args:
            batch_size: Process N PDFs before committing
            dry_run: Don't update DB, just analyze
        
        Returns:
            Statistics dict
        """
        cursor = self.conn.cursor()
        
        # Get all PDFs
        cursor.execute("SELECT id, filename, content FROM pdf_index")
        pdfs = cursor.fetchall()
        
        print(f"Categorizing {len(pdfs)} PDFs...")
        
        # Statistics
        stats = {category: 0 for category in CATEGORY_DEFINITIONS.keys()}
        changes = 0
        batch = 0
        
        for i, pdf in enumerate(pdfs, 1):
            pdf_id = pdf["id"]
            filename = pdf["filename"]
            content = pdf["content"] or ""
            
            # Categorize
            category, confidence = self.categorize_pdf(filename, content)
            stats[category] += 1
            
            # Update DB (if not dry-run)
            if not dry_run:
                cursor.execute(
                    "UPDATE pdf_index SET category = ?, bert_confidence = ? WHERE id = ?",
                    (category, confidence, pdf_id)
                )
                changes += 1
            
            # Print progress
            if i % 100 == 0:
                print(f"  [{i:4d}/{len(pdfs)}] {filename[:50]:50s} → {category} ({confidence:.3f})")
            
            # Batch commit
            if i % batch_size == 0 and not dry_run:
                self.conn.commit()
                batch += 1
                print(f"  ✓ Batch {batch} committed ({changes} updates)")
        
        # Final commit
        if not dry_run:
            self.conn.commit()
            print(f"✅ All {changes} PDFs updated in database")
        else:
            print(f"📊 Dry-run complete (0 updates to DB)")
        
        return stats
    
    def test_sample(self, n_samples: int = 10) -> List[Dict]:
        """Test categorization on random samples"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, filename, content FROM pdf_index ORDER BY RANDOM() LIMIT {n_samples}")
        samples = cursor.fetchall()
        
        results = []
        for pdf in samples:
            filename = pdf["filename"]
            content = pdf["content"] or ""
            category, confidence = self.categorize_pdf(filename, content)
            results.append({
                "filename": filename,
                "bert_category": category,
                "confidence": confidence
            })
        
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BERT-based PDF Categorization")
    parser.add_argument("--dry-run", action="store_true", help="Don't update DB")
    parser.add_argument("--test", type=int, default=0, help="Test on N random samples")
    parser.add_argument("--db", type=Path, default=None, help="PDF index database path")
    
    args = parser.parse_args()
    
    categorizer = PDFCategorizer(db_path=args.db)
    
    if args.test:
        print(f"\n🧪 Testing on {args.test} random samples:\n")
        samples = categorizer.test_sample(args.test)
        for sample in samples:
            print(f"  {sample['filename'][:60]:60s}")
            print(f"    → {sample['bert_category']:10s} (confidence: {sample['confidence']:.3f})\n")
    else:
        # Categorize all
        stats = categorizer.categorize_all_pdfs(dry_run=args.dry_run, batch_size=200)
        
        print("\n📊 Final Statistics:")
        total = sum(stats.values())
        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {category:12s}: {count:5d} ({pct:5.1f}%)")
        print(f"  {'TOTAL':12s}: {total:5d} (100.0%)")
    
    categorizer.close()

if __name__ == "__main__":
    main()
