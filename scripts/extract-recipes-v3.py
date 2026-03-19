#!/usr/bin/env python3
"""
Extract REAL recipes only (v3) - smarter context detection.
Ignores: Introductions, tables, seasonal charts, random text.
Finds: Actual recipe blocks with Title + Zutaten + Anleitung together.
"""

import re
from typing import List, Dict

def extract_recipes_v3(text: str) -> List[Dict]:
    """
    Extract only REAL recipe blocks.
    Criteria:
    1. Must have a title (starts recipe block)
    2. Must have "Zutaten" section with items
    3. Must have "Anleitung" section with steps
    4. All three must be within 500 chars of each other (same recipe)
    """
    
    recipes = []
    
    # Split by recipe title patterns (most reliable marker)
    # Common patterns: "### Recipe", "**Recipe Title**", "## Recipe", "Rezept:", numbers with recipe
    recipe_patterns = [
        r'(?:^|\n)(?:###|##|####)\s+(.+?)(?=\n|$)',  # Markdown headers
        r'(?:^|\n)\*\*([^*]{10,80}?)\*\*(?:\n|$)',   # Bold title
        r'(?:^|\n)(?:Rezept|REZEPT)[\s:]+([^:\n]{10,80})',  # Explicit "Rezept:"
    ]
    
    # Find all potential recipe starts
    recipe_starts = []
    for pattern in recipe_patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            start_pos = match.start()
            title = match.group(1).strip()
            
            # Clean title
            title = re.sub(r'[*_#`]+', '', title)
            
            # Skip non-recipe headers
            if any(skip in title.lower() for skip in [
                'inhaltsverzeichnis', 'index', 'kapitel', 'vorwort',
                'impressum', 'copyright', 'seite', 'table of',
                'saisonal', 'jahres', 'kalender', 'übersicht'
            ]):
                continue
            
            recipe_starts.append((start_pos, title))
    
    # Sort by position
    recipe_starts.sort()
    
    # For each potential recipe start, look for Zutaten + Anleitung nearby
    for idx, (start_pos, title) in enumerate(recipe_starts):
        # Look ahead 500 chars for ingredients + instructions
        end_search = min(start_pos + 1000, len(text))
        recipe_block = text[start_pos:end_search]
        
        # Find Zutaten section
        zutaten_match = re.search(
            r'(?:zutaten|ingredients|zutat)[\s:\n]+(.+?)(?=anleitung|instructions|zubereitung|vorbereitung|schritte|\n\n|$)',
            recipe_block,
            re.IGNORECASE | re.DOTALL
        )
        
        # Find Anleitung section
        anleitung_match = re.search(
            r'(?:anleitung|instructions|zubereitung|vorbereitung|schritte)[\s:\n]+(.+?)(?=\n\n|rezept|recipe|\Z)',
            recipe_block,
            re.IGNORECASE | re.DOTALL
        )
        
        # Only proceed if BOTH sections found (real recipe!)
        if not zutaten_match or not anleitung_match:
            continue
        
        # Extract ingredients
        ingredients = []
        zutaten_text = zutaten_match.group(1)
        
        for line in zutaten_text.split('\n'):
            line = line.strip()
            # Skip empty or comment lines
            if not line or line.startswith('#') or line.startswith('|'):
                continue
            
            # Remove bullets/numbers
            line = re.sub(r'^[\d\.\)\-•*+]\s*', '', line)
            line = re.sub(r'^\[.\]\s*', '', line)
            line = re.sub(r'\s+', ' ', line)
            
            # Filter: ingredient must look like "X g/ml/... Ingredient" or just ingredient
            # NOT descriptions, NOT random text
            if len(line) > 3 and len(line) < 120:
                # Relax validation: accept most ingredient-like lines
                has_number = any(c.isdigit() for c in line)
                is_short = len(line.split()) <= 6
                
                if has_number or is_short:
                    ingredients.append(line)
        
        # Extract instructions
        instructions = []
        anleitung_text = anleitung_match.group(1)
        
        step_num = 0
        for line in anleitung_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('|'):
                continue
            
            # Remove existing numbers/bullets
            line = re.sub(r'^[\d\.\)\-•*+]\s*', '', line)
            line = re.sub(r'^\[.\]\s*', '', line)
            line = re.sub(r'\s+', ' ', line)
            
            # Filter: instruction should be 5-200 chars
            if 5 < len(line) < 200:
                # Check if it's actual instruction (avoid tables, metadata)
                if not line.startswith('|') and not any(skip in line.lower() for skip in ['seite', 'page', 'kapitel']):
                    step_num += 1
                    instructions.append(f"{step_num}. {line}")
        
        # Only add if we have MEANINGFUL ingredients + instructions
        # Lowered threshold: 2+ ingredients (was 3), 1+ instructions (was 2)
        if len(ingredients) >= 2 and len(instructions) >= 1:
            recipe = {
                'title': title[:80],
                'ingredients': ingredients[:20],
                'instructions': instructions[:15],
                'servings': extract_servings(recipe_block),
                'time': extract_time(recipe_block)
            }
            recipes.append(recipe)
        
        if len(recipes) >= 8:
            break
    
    return recipes

def extract_servings(text: str) -> str:
    """Extract servings if available."""
    match = re.search(
        r'(?:portionen|servings|personen|für)[\s:]*(\d+)',
        text,
        re.IGNORECASE
    )
    return match.group(1) if match else None

def extract_time(text: str) -> str:
    """Extract cooking time if available."""
    match = re.search(
        r'(?:zeit|time|dauer|cooking time)[\s:]*(\d+)\s*(?:min|minuten|minute|h|hour)',
        text,
        re.IGNORECASE
    )
    return match.group(1) if match else None

def format_recipes_markdown(recipes: List[Dict], source: str = "") -> str:
    """Format recipes as markdown."""
    
    if not recipes:
        return ""
    
    md = f"### 🍽️  Rezepte aus {source}\n\n"
    
    for i, recipe in enumerate(recipes, 1):
        md += f"#### {i}. {recipe['title']}\n\n"
        
        # Metadata
        metadata = []
        if recipe.get('servings'):
            metadata.append(f"👥 {recipe['servings']} Portionen")
        if recipe.get('time'):
            metadata.append(f"⏱️  {recipe['time']} Min")
        
        if metadata:
            md += f"{' | '.join(metadata)}\n\n"
        
        # Ingredients
        if recipe.get('ingredients'):
            md += "**Zutaten:**\n"
            for ing in recipe['ingredients']:
                md += f"- [ ] {ing}\n"
            md += "\n"
        
        # Instructions
        if recipe.get('instructions'):
            md += "**Anleitung:**\n"
            for instr in recipe['instructions']:
                md += f"{instr}\n"
            md += "\n"
        
        md += "---\n\n"
    
    return md

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: extract-recipes-v3.py <text_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
    
    recipes = extract_recipes_v3(text)
    
    if recipes:
        print(f"✅ Found {len(recipes)} real recipes")
        markdown = format_recipes_markdown(recipes, "Source")
        print(markdown)
    else:
        print("⚠️  No real recipes found (too strict)")
