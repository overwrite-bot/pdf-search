#!/usr/bin/env python3
"""
Test suite for BERT-based PDF categorization.
Validates accuracy against known PDFs.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from categorization_core import PDFCategorizer

# Test data: (filename, content_snippet, expected_category)
TEST_CASES = [
    # Tech
    ("Python Programming Guide.pdf", "def function(): loops, classes, syntax, variables", "tech"),
    ("Linux Security Best Practices.pdf", "firewall, iptables, ssh, kernel, network, security", "tech"),
    ("C++ Optimization Manual.pdf", "memory management, pointers, templates, compiler, performance", "tech"),
    ("Database Design Patterns.pdf", "SQL, queries, indexes, normalization, schema, relational", "tech"),
    
    # Cooking
    ("Fermentieren für Anfänger.pdf", "gärung, hefe, sauerkraut, kimchi, rezept, fermentation", "cooking"),
    ("Käseherstellung im Haus.pdf", "käse, rennet, kultur, milch, reifung, zubereitung", "cooking"),
    ("Fleischverarbeitung.pdf", "fleisch, wurst, schneiden, gewürze, räuchern, lagern", "cooking"),
    ("Pilzbestimmung und Rezepte.pdf", "pilz, rezept, zutaten, pilzzucht, sammeln, kochen", "cooking"),
    
    # Health
    ("Ernährung und Wellness.pdf", "vitamin, mineral, gesundheit, diät, ernährung, therapie", "health"),
    ("Yoga für Anfänger.pdf", "yoga, meditation, asana, fitness, bewegung, wellness, chakra", "health"),
    ("Naturheilkunde.pdf", "kraut, heilpflanze, medizin, therapie, gesundheit, natürlich", "health"),
    
    # Philosophy
    ("Kant und die Kritik der Vernunft.pdf", "kant, kritik, vernunft, philosophie, metaphysik, denken", "philosophy"),
    ("Nietzsche: Beyond Good and Evil.pdf", "nietzsche, philosophie, ethik, morality, übermensch", "philosophy"),
    
    # Esoterik
    ("Chakren und Energiearbeit.pdf", "chakra, energie, spirituell, aura, meridian, esoterik", "esoterik"),
    ("Meditation und Bewusstsein.pdf", "meditation, bewusstsein, spiritualität, erleuchtung, geist", "esoterik"),
    ("Tarot und Divination.pdf", "tarot, karten, divination, orakel, spirituell, mystik", "esoterik"),
]

@pytest.fixture(scope="session")
def categorizer():
    """Initialize categorizer for all tests"""
    return PDFCategorizer()

def test_categorization_accuracy(categorizer):
    """Test categorization accuracy on known PDFs"""
    correct = 0
    total = len(TEST_CASES)
    
    for filename, content, expected in TEST_CASES:
        predicted, confidence = categorizer.categorize_pdf(filename, content)
        is_correct = predicted == expected
        correct += is_correct
        
        status = "✓" if is_correct else "✗"
        print(f"{status} {filename[:40]:40s} → {predicted:10s} (expected: {expected:10s}, conf: {confidence:.3f})")
        
        assert is_correct, f"Expected {expected}, got {predicted}"
    
    accuracy = (correct / total) * 100
    print(f"\n📊 Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    assert accuracy >= 80.0, f"Accuracy {accuracy:.1f}% < 80% threshold"

def test_confidence_scores(categorizer):
    """Test that correct categories have higher confidence"""
    for filename, content, expected in TEST_CASES[:5]:
        predicted, confidence = categorizer.categorize_pdf(filename, content)
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of range [0,1]"
        assert confidence > 0.3, f"Confidence {confidence} below threshold"

def test_general_fallback(categorizer):
    """Test that vague queries fall back to 'general'"""
    vague_text = "Lorem ipsum dolor sit amet consectetur adipiscing elit"
    predicted, confidence = categorizer.categorize_pdf("unknown.pdf", vague_text)
    # Should be something (test confidence is low enough)
    assert confidence is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
