#!/usr/bin/env python3
"""
Smart recipe extraction with multiple format support.
Handles: numbered lists, bullets, tables, structured recipes.
"""

import re
from typing import List, Dict

def extract_recipes_smart(text: str) -> List[Dict]:
    """
    Extract recipes from text with multiple format patterns.
    Looks for: Rezept, Zutaten, Anleitung, Zubereitung
    """
    
    recipes = []
    
    # Split by recipe headers
    recipe_blocks = re.split(
        r'\n(?:Rezept|Recipe|##|###|\*\*Rezept)',
        text,
        flags=re.IGNORECASE
    )
    
    for block in recipe_blocks:
        if len(block) < 100:  # Skip too short blocks
            continue
        
        recipe = {}
        
        # 1. Extract title (first line or after "Rezept:")
        lines = block.split('\n')
        title_line = lines[0].strip() if lines else ""
        
        # Clean title
        title = re.sub(r'^[#\*\-•]+\s*', '', title_line).strip()
        title = re.sub(r'[*_]+', '', title)
        
        if not title or len(title) < 3:
            title = "Unbenanntes Rezept"
        
        recipe['title'] = title[:80]
        
        # 2. Extract ingredients section
        ing_match = re.search(
            r'(?:zutaten|ingredients|zutat)[\s:\n]+(.+?)(?=\n(?:anleitung|instructions|zubereitung|vorbereitung|schritte)|$)',
            block,
            re.IGNORECASE | re.DOTALL
        )
        
        ingredients = []
        if ing_match:
            ing_text = ing_match.group(1)
            # Split by newlines, bullets, numbers
            ing_lines = re.split(r'\n', ing_text)
            
            for line in ing_lines:
                line = line.strip()
                # Remove bullets, numbers, hyphens
                line = re.sub(r'^[\d\.\)\-•*+]\s*', '', line)
                line = re.sub(r'^\[.\]\s*', '', line)  # [ ] checkboxes
                
                # Clean up excess whitespace
                line = re.sub(r'\s+', ' ', line)
                
                if line and len(line) > 2 and not line.startswith('#'):
                    ingredients.append(line)
        
        # 3. Extract instructions section
        instr_match = re.search(
            r'(?:anleitung|instructions|zubereitung|vorbereitung|schritte)[\s:\n]+(.+?)(?:\n\n|\Z)',
            block,
            re.IGNORECASE | re.DOTALL
        )
        
        instructions = []
        if instr_match:
            instr_text = instr_match.group(1)
            instr_lines = re.split(r'\n', instr_text)
            
            step_num = 0
            for line in instr_lines:
                line = line.strip()
                # Remove existing numbers/bullets
                line = re.sub(r'^[\d\.\)\-•*+]\s*', '', line)
                line = re.sub(r'^\[.\]\s*', '', line)
                
                line = re.sub(r'\s+', ' ', line)
                
                if line and len(line) > 3 and not line.startswith('#'):
                    step_num += 1
                    instructions.append(f"{step_num}. {line}")
        
        # 4. Extract metadata
        servings_match = re.search(
            r'(?:portionen|servings|personen|for)[\s:]*(\d+)',
            block,
            re.IGNORECASE
        )
        recipe['servings'] = servings_match.group(1) if servings_match else None
        
        time_match = re.search(
            r'(?:zeit|time|dauer|cooking time|duration)[\s:]*(\d+)\s*(?:min|minuten|minute)',
            block,
            re.IGNORECASE
        )
        recipe['time'] = time_match.group(1) if time_match else None
        
        # 5. Only add if we have ingredients OR instructions
        if (ingredients and len(ingredients) > 2) or (instructions and len(instructions) > 2):
            recipe['ingredients'] = ingredients[:20]  # Max 20
            recipe['instructions'] = instructions[:15]  # Max 15
            recipes.append(recipe)
        
        if len(recipes) >= 8:  # Max 8 recipes per PDF
            break
    
    return recipes

def format_recipes_markdown(recipes: List[Dict], source: str = "") -> str:
    """Format recipes as structured markdown."""
    
    if not recipes:
        return ""
    
    md = f"### 🍽️  Rezepte aus {source}\n\n"
    
    for i, recipe in enumerate(recipes, 1):
        md += f"#### {i}. {recipe['title']}\n\n"
        
        # Metadata row
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
        print("Usage: extract-recipes-smart.py <text_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
    
    recipes = extract_recipes_smart(text)
    
    if recipes:
        print(f"✅ Found {len(recipes)} recipes")
        markdown = format_recipes_markdown(recipes, "Source")
        print(markdown)
    else:
        print("⚠️  No recipes found")
