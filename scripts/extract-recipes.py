#!/usr/bin/env python3
"""
Extract recipes from PDFs using pdfplumber.
Identifies recipe patterns (Zutaten, Zubereitung, ingredients, instructions)
"""

import sys
import json
import re
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract_text_from_pdf(pdf_path, max_pages=20):
    """Extract text content from PDF, limited to first max_pages"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:max_pages]):
                text += page.extract_text() or ""
                text += "\n--- PAGE BREAK ---\n"
            return text
    except Exception as e:
        print(f"ERROR reading {pdf_path}: {e}", file=sys.stderr)
        return ""


def find_recipe_sections(text):
    """
    Find recipe-like sections in text using keyword patterns.
    
    Returns list of recipe dictionaries with extracted sections.
    """
    recipes = []
    
    # Patterns for recipe headers (German & English)
    recipe_patterns = [
        r'(?:Rezept|Recipe|Gericht).*?:\s*([^\n]+)',
        r'(?:Gericht|Dish)\s+(?:.*?):\s*([^\n]+)',
    ]
    
    # Patterns for sections
    ingredient_pattern = r'(?:Zutaten|Ingredients|Komponenten).*?:(.*?)(?=(?:Zubereitung|Instructions|Vorbereitung|Preparation)|(?:\n[A-Z][a-z]+.*?:)|$)'
    instruction_pattern = r'(?:Zubereitung|Instructions|Vorbereitung|Preparation).*?:(.*?)(?=(?:Tipps|Tips|Hinweise|Notes|Nährwerte|Nutrition)|(?:\n[A-Z][a-z]+.*?:)|$)'
    timing_pattern = r'(?:Zeit|Time|Dauer|Duration|Garzeit).*?:?\s*([^\n]+)'
    servings_pattern = r'(?:Portionen|Servings|Für|For)\s+(\d+)\s*(?:Personen|Gäste|people|servings)?'
    
    # Try to find recipe blocks
    # Split by common recipe delimiters
    sections = re.split(r'\n(?=[A-Z]{2,}.*?:)', text, flags=re.MULTILINE)
    
    for section in sections:
        if len(section.strip()) < 100:  # Skip very short sections
            continue
        
        # Check if section looks like a recipe
        has_ingredients = 'Zutat' in section or 'ingredient' in section.lower()
        has_instructions = 'Zubereitung' in section or 'instruction' in section.lower() or 'vorbereitung' in section.lower()
        
        if not (has_ingredients or has_instructions):
            continue
        
        recipe = {}
        
        # Extract title (look for first line or pattern match)
        lines = section.split('\n')
        potential_title = lines[0].strip() if lines else "Untitled Recipe"
        
        # Clean up title
        potential_title = re.sub(r'^(?:Rezept|Recipe).*?:\s*', '', potential_title).strip()
        if potential_title:
            recipe['title'] = potential_title[:100]
        
        # Extract ingredients
        ing_match = re.search(ingredient_pattern, section, re.IGNORECASE | re.DOTALL)
        if ing_match:
            ingredients_text = ing_match.group(1)
            # Parse ingredient lines (usually "- quantity item" or "qty item")
            ingredients = []
            for line in ingredients_text.split('\n'):
                line = line.strip()
                if line and len(line) > 5 and not line.isupper():
                    ingredients.append(line)
            if ingredients:
                recipe['ingredients'] = ingredients[:20]  # Limit to 20 ingredients
        
        # Extract instructions
        inst_match = re.search(instruction_pattern, section, re.IGNORECASE | re.DOTALL)
        if inst_match:
            instructions_text = inst_match.group(1)
            # Parse numbered or bullet-point instructions
            steps = []
            for line in instructions_text.split('\n'):
                line = line.strip()
                if line and len(line) > 10 and not line.isupper():
                    steps.append(line)
            if steps:
                recipe['instructions'] = steps[:15]  # Limit to 15 steps
        
        # Extract timing
        time_match = re.search(timing_pattern, section, re.IGNORECASE)
        if time_match:
            recipe['timing'] = time_match.group(1).strip()
        
        # Extract servings
        servings_match = re.search(servings_pattern, section, re.IGNORECASE)
        if servings_match:
            recipe['servings'] = servings_match.group(0).strip()
        
        # Only add if we found meaningful content
        if recipe and ('ingredients' in recipe or 'instructions' in recipe):
            recipes.append(recipe)
    
    return recipes


def extract_contextual_info(text, query):
    """
    Extract sections that relate to the user's query.
    E.g., if query is "Schweinenacken", find all paragraphs mentioning Schwein/Fleisch.
    """
    contexts = []
    
    # Split by paragraphs
    paragraphs = re.split(r'\n\n+', text)
    
    keywords = query.lower().split()
    
    for para in paragraphs:
        # Check if paragraph matches query keywords
        para_lower = para.lower()
        matches = sum(1 for kw in keywords if kw in para_lower)
        
        if matches >= 1 and len(para) > 50:  # At least one keyword match, min length
            contexts.append({
                'text': para[:500],  # Limit to 500 chars
                'relevance': matches
            })
    
    # Sort by relevance and return top 5
    return sorted(contexts, key=lambda x: x['relevance'], reverse=True)[:5]


def main():
    if len(sys.argv) < 2:
        print("Usage: extract-recipes.py <pdf_path> [query]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not Path(pdf_path).exists():
        print(f"ERROR: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📖 Extracting from: {Path(pdf_path).name}", file=sys.stderr)
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("ERROR: Could not extract text from PDF", file=sys.stderr)
        sys.exit(1)
    
    # Find recipes
    recipes = find_recipe_sections(text)
    
    # Find contextual info if query provided
    contexts = extract_contextual_info(text, query) if query else []
    
    # Output as JSON
    output = {
        'pdf': Path(pdf_path).name,
        'recipes_found': len(recipes),
        'recipes': recipes,
        'contextual_snippets': contexts if contexts else []
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
