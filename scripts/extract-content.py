#!/usr/bin/env python3
"""
Universal PDF Content Extraction Framework
Identifies and extracts: recipes, how-to guides, reference material, data, technical content
"""

import sys
import json
import re
from pathlib import Path
from enum import Enum

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


class ContentType(Enum):
    """Supported content types"""
    RECIPE = "recipe"
    HOWTO = "howto"
    REFERENCE = "reference"
    DATA = "data"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"


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


def detect_content_type(text, query=""):
    """
    Detect the type of content in the text.
    Returns ContentType enum.
    """
    text_lower = text.lower()
    query_lower = query.lower()
    
    # Recipe detection
    recipe_keywords = ['zutaten', 'rezept', 'zubereitung', 'ingredient', 'recipe', 'gericht', 'garzeit', 'portionen', 'servings']
    if sum(1 for kw in recipe_keywords if kw in text_lower) >= 2:
        return ContentType.RECIPE
    
    # How-To detection
    howto_keywords = ['schritt', 'anleitung', 'wie', 'instruction', 'step', 'vorbereitung', 'preparation', 'voraussetzung']
    if sum(1 for kw in howto_keywords if kw in text_lower) >= 2:
        return ContentType.HOWTO
    
    # Data detection
    data_keywords = ['tabelle', 'table', 'liste', 'list', 'temperatur', 'daten', 'data', 'statistik', 'wert', 'value']
    if sum(1 for kw in data_keywords if kw in text_lower) >= 2:
        return ContentType.DATA
    
    # Technical detection
    tech_keywords = ['config', 'befehl', 'command', 'code', 'kalibrierung', 'setup', 'installation', 'parameter']
    if sum(1 for kw in tech_keywords if kw in text_lower) >= 2:
        return ContentType.TECHNICAL
    
    # Reference detection
    ref_keywords = ['definition', 'erklär', 'definition', 'explain', 'charakteristik', 'eigenschaft', 'property', 'merkmal']
    if sum(1 for kw in ref_keywords if kw in text_lower) >= 1:
        return ContentType.REFERENCE
    
    return ContentType.UNKNOWN


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
        print("Usage: extract-content.py <pdf_path> [query]")
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
    
    # Detect content type
    content_type = detect_content_type(text, query)
    print(f"   Content type detected: {content_type.value}", file=sys.stderr)
    
    # Find contextual info if query provided
    contexts = extract_contextual_info(text, query) if query else []
    
    # Extract based on content type
    extracted_data = {}
    
    if content_type == ContentType.RECIPE:
        recipes = find_recipe_sections(text)
        extracted_data['recipes'] = recipes
        extracted_data['count'] = len(recipes)
    else:
        # For non-recipe types, use contextual extraction as foundation
        extracted_data['sections'] = contexts
        extracted_data['count'] = len(contexts)
    
    # Output as JSON
    output = {
        'pdf': Path(pdf_path).name,
        'content_type': content_type.value,
        'extracted_data': extracted_data,
        'contextual_snippets': contexts if contexts else [],
        'confidence': 0.8 if (extracted_data.get('count', 0) > 0) else 0.3
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
