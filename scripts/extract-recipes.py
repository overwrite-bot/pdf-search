#!/usr/bin/env python3
"""
Extract actual recipes (ingredients, instructions) from PDF content.
Uses regex patterns to find recipe structures.
"""

import sys
import re
import json
from pathlib import Path

def extract_recipes_from_text(text: str) -> list:
    """
    Find recipe patterns in extracted PDF text.
    Looks for: Zutaten, Anleitung, Portionen, Zubereitung
    """
    
    recipes = []
    
    # Split by common recipe markers
    recipe_markers = [
        r'(?:rezept|anleitung|zubereitung|zutaten|ingredients)',
    ]
    
    # Look for sections with Zutaten/Anleitung
    pattern = r'(.*?(?:Zutaten|Ingredients|Zutat).*?(?:Anleitung|Instructions|Zubereitung).*?)(?=\n\n|\Z)'
    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        recipe_text = match.group(1)
        
        # Extract title (usually first line or after food name)
        title_match = re.search(r'(?:Rezept|Recipe)[\s:]*([^\n]+)', recipe_text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Unbenanntes Rezept"
        
        # Extract ingredients
        ingredients_match = re.search(
            r'(?:Zutaten|Ingredients)[\s:]*\n(.*?)(?:\n\n|Anleitung|Instructions|Zubereitung)',
            recipe_text,
            re.IGNORECASE | re.DOTALL
        )
        
        ingredients = []
        if ingredients_match:
            ingredient_lines = ingredients_match.group(1).split('\n')
            for line in ingredient_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Clean up ingredient line
                    line = re.sub(r'^[-•*]\s*', '', line)  # Remove bullets
                    if line and len(line) > 3:
                        ingredients.append(line)
        
        # Extract instructions
        instructions_match = re.search(
            r'(?:Anleitung|Instructions|Zubereitung)[\s:]*\n(.*?)(?:\n\n|\Z)',
            recipe_text,
            re.IGNORECASE | re.DOTALL
        )
        
        instructions = []
        if instructions_match:
            instruction_lines = instructions_match.group(1).split('\n')
            for i, line in enumerate(instruction_lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Clean up instruction
                    line = re.sub(r'^[-•*\d.]+\s*', '', line)  # Remove bullets/numbers
                    if line and len(line) > 3:
                        instructions.append(f"{i}. {line}")
        
        # Extract servings/time if available
        servings_match = re.search(r'(?:Portionen|Servings|Personen)[\s:]*(\d+)', recipe_text, re.IGNORECASE)
        servings = servings_match.group(1) if servings_match else None
        
        time_match = re.search(r'(?:Zeit|Zeit|Dauer|Cooking time)[\s:]*(\d+\s*(?:min|Minuten|hours|h))', recipe_text, re.IGNORECASE)
        cooking_time = time_match.group(1) if time_match else None
        
        # Only add if we found ingredients AND instructions
        if ingredients and instructions:
            recipe = {
                'title': title,
                'servings': servings,
                'cooking_time': cooking_time,
                'ingredients': ingredients[:15],  # Max 15 ingredients
                'instructions': instructions[:10]  # Max 10 steps
            }
            recipes.append(recipe)
    
    return recipes

def format_recipes_markdown(recipes: list, title: str = "Rezepte") -> str:
    """Format extracted recipes as markdown."""
    
    if not recipes:
        return f"## 🍽️ {title}\n\nKeine Rezepte gefunden.\n"
    
    md = f"## 🍽️ {title}\n\n"
    
    for i, recipe in enumerate(recipes, 1):
        md += f"### Rezept {i}: {recipe['title']}\n"
        
        if recipe['servings']:
            md += f"**Portionen:** {recipe['servings']}\n"
        if recipe['cooking_time']:
            md += f"**Zubereitungszeit:** {recipe['cooking_time']}\n"
        
        md += f"\n**Zutaten:**\n"
        for ingredient in recipe['ingredients']:
            md += f"- {ingredient}\n"
        
        md += f"\n**Anleitung:**\n"
        for instruction in recipe['instructions']:
            md += f"{instruction}\n"
        
        md += "\n---\n\n"
    
    return md

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract-recipes.py <text_file>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    if not Path(text_file).exists():
        print(f"❌ File not found: {text_file}")
        sys.exit(1)
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    recipes = extract_recipes_from_text(text)
    
    if recipes:
        print(f"✅ Found {len(recipes)} recipes")
        markdown = format_recipes_markdown(recipes)
        print(markdown)
    else:
        print("⚠️  No recipes found in text")
