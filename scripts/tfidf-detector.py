#!/usr/bin/env python3
"""
H3 Experiment: TF-IDF based content type detection
Better than simple heuristics for mixed-content PDFs
"""

import re
import math
from collections import Counter

# Keyword dictionaries (German + English)
RECIPE_KEYWORDS = {
    'zutat': 5, 'ingredient': 5, 'anleitung': 5, 'instruction': 5,
    'zubereitung': 4, 'rezept': 5, 'recipe': 5, 'backen': 4, 'bake': 4,
    'kochen': 4, 'cook': 4, 'braten': 4, 'fry': 4, 'gramm': 3, 'liter': 3,
    'esslöffel': 3, 'teelöffel': 3, 'ml': 2, 'g': 1, 'l': 1, 'kg': 2,
    'minuten': 2, 'grad': 2, 'ofen': 2, 'pfanne': 2, 'topf': 2
}

TECHNICAL_KEYWORDS = {
    'definition': 4, 'klasse': 5, 'methode': 5, 'funktion': 5,
    'parameter': 4, 'return': 4, 'api': 5, 'exception': 4,
    'algorithmus': 5, 'datenstruktur': 5, 'implementation': 4,
    'interface': 4, 'class': 5, 'function': 5, 'method': 4, 'def': 4,
    'import': 4, 'code': 3, 'programmierung': 5, 'variable': 4,
    'schnittstelle': 5, 'objekt': 3, 'modul': 4
}

NARRATIVE_KEYWORDS = {
    'geschichte': 4, 'erzählung': 4, 'roman': 5, 'protagonist': 5,
    'handlung': 4, 'szene': 4, 'dialog': 4, 'kapitel': 3,
    'beschreibung': 3, 'gedanke': 3, 'gefühl': 3, 'charakter': 4,
    'essay': 4, 'artikel': 3, 'reflektiert': 3, 'argumente': 3,
    'meinung': 3, 'diskussion': 3, 'perspektive': 3
}

def tfidf_score(text, keywords):
    """
    Calculate TF-IDF score for keyword set.
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    word_count = Counter(words)
    total_words = len(words)
    
    if total_words == 0:
        return 0
    
    # TF-IDF calculation
    score = 0
    for keyword, weight in keywords.items():
        count = word_count.get(keyword, 0)
        if count > 0:
            # TF = count / total
            # IDF = 1 + log(1 + weight) — keyword weight acts as inverse frequency
            tf = count / total_words
            idf = 1 + math.log(1 + weight)
            score += tf * idf
    
    return score * 100  # Scale to 0-100


def detect_type_tfidf(text):
    """
    Detect content type using TF-IDF scoring.
    H3 Experiment: Better accuracy than simple heuristics
    """
    recipe_score = tfidf_score(text, RECIPE_KEYWORDS)
    technical_score = tfidf_score(text, TECHNICAL_KEYWORDS)
    narrative_score = tfidf_score(text, NARRATIVE_KEYWORDS)
    
    max_score = max(recipe_score, technical_score, narrative_score)
    
    if max_score == 0:
        return "narrative", {"recipe": 0, "technical": 0, "narrative": 0}
    
    scores = {
        "recipe": recipe_score,
        "technical": technical_score,
        "narrative": narrative_score
    }
    
    if recipe_score >= max(technical_score, narrative_score):
        return "recipe", scores
    elif technical_score >= narrative_score:
        return "technical", scores
    else:
        return "narrative", scores


if __name__ == '__main__':
    # Test
    test_texts = [
        ("Zutaten: 2 Eier, Butter. Anleitung: Mischen und backen.", "recipe"),
        ("Definition: Klasse ist ein Objekt. Parameter sind wichtig.", "technical"),
        ("Der Protagonist betrat das Zimmer. Es war dunkel und geheimnisvoll.", "narrative"),
    ]
    
    for text, expected in test_texts:
        detected, scores = detect_type_tfidf(text)
        print(f"Text: {text[:40]}...")
        print(f"Expected: {expected}, Got: {detected}")
        print(f"Scores: {scores}\n")
