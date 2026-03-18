#!/usr/bin/env python3
"""
Synthesize complete, actionable recipes from:
1. Extracted recipe fragments from PDFs
2. Contextual information from books
3. User query context

Uses RAG-Daemon + qwen3:14b to create 2-3 complete recipes ready to cook.
"""

import sys
import json
import requests
from pathlib import Path


def query_rag_daemon(query, context=""):
    """Query RAG-Daemon for recipe synthesis"""
    try:
        payload = {
            "query": f"{query}\n\nContext:\n{context}",
        }
        response = requests.post(
            "http://127.0.0.1:5555/ask",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('answer', '')
    except Exception as e:
        print(f"ERROR querying RAG-Daemon: {e}", file=sys.stderr)
        return ""


def synthesize_recipes(query, extracted_recipes, pdf_contexts):
    """
    Ask 14b to synthesize complete recipes from extracted data.
    
    Returns: List of recipe dictionaries with full content
    """
    
    # Build context from extractions
    context_text = ""
    
    if extracted_recipes:
        context_text += "## Extracted Recipe Fragments:\n"
        for rec in extracted_recipes:
            context_text += f"\n### {rec.get('title', 'Untitled')}\n"
            if 'ingredients' in rec:
                context_text += "Ingredients:\n" + "\n".join(rec['ingredients'][:10]) + "\n"
            if 'instructions' in rec:
                context_text += "Instructions:\n" + "\n".join(rec['instructions'][:5]) + "\n"
    
    if pdf_contexts:
        context_text += "\n## Related Information from Books:\n"
        for ctx in pdf_contexts[:3]:
            context_text += f"\n{ctx.get('text', '')}\n"
    
    # Create synthesis prompt
    prompt = f"""
Based on the following extracted recipe data and context, create {3} complete, actionable recipes for: {query}

{context_text}

For EACH recipe, provide in this EXACT format:

===RECIPE START===
TITLE: [Recipe Name]
SOURCE: [Which book/context this comes from]
SERVINGS: [number of people]

INGREDIENTS:
[Complete list with quantities, one per line]
- 500g Fleisch
- 2 EL Öl
etc.

INSTRUCTIONS:
[Step-by-step, numbered]
1. Prep: ...
2. Heat: ...
3. Cook: ...
etc.

TIMING:
Prep Time: X minutes
Cook Time: Y minutes
Total: Z minutes
Temperature: ABC°C

TIPS:
- Tip 1
- Tip 2
===RECIPE END===

Focus on:
1. Complete ingredient lists with quantities
2. Clear step-by-step instructions
3. Realistic cooking times and temperatures
4. Practical tips for success
5. Variations or modern twists

Create recipes that are READY TO COOK from the information provided.
"""
    
    print(f"🔄 Synthesizing recipes...", file=sys.stderr)
    
    # Query RAG-Daemon for synthesis
    synthesis = query_rag_daemon(prompt, context_text)
    
    if not synthesis:
        print(f"WARNING: No synthesis returned from RAG-Daemon", file=sys.stderr)
        return []
    
    # Parse synthesized recipes
    recipes = []
    recipe_blocks = synthesis.split('===RECIPE')
    
    for block in recipe_blocks:
        if 'START' not in block:
            continue
        
        recipe = parse_recipe_block(block)
        if recipe:
            recipes.append(recipe)
    
    return recipes


def parse_recipe_block(block):
    """Parse a ===RECIPE START/END block into structured data"""
    
    recipe = {}
    
    # Extract title
    title_match = re.search(r'TITLE:\s*(.+)', block)
    if title_match:
        recipe['title'] = title_match.group(1).strip()
    
    # Extract source
    source_match = re.search(r'SOURCE:\s*(.+)', block)
    if source_match:
        recipe['source'] = source_match.group(1).strip()
    
    # Extract servings
    servings_match = re.search(r'SERVINGS:\s*(.+)', block)
    if servings_match:
        recipe['servings'] = servings_match.group(1).strip()
    
    # Extract ingredients section
    ingredients_section = re.search(r'INGREDIENTS:(.*?)(?=INSTRUCTIONS:|$)', block, re.DOTALL)
    if ingredients_section:
        ingredients_text = ingredients_section.group(1)
        ingredients = []
        for line in ingredients_text.split('\n'):
            line = line.strip()
            if line and not line.isupper():
                ingredients.append(line)
        recipe['ingredients'] = ingredients
    
    # Extract instructions section
    instructions_section = re.search(r'INSTRUCTIONS:(.*?)(?=TIMING:|$)', block, re.DOTALL)
    if instructions_section:
        instructions_text = instructions_section.group(1)
        instructions = []
        for line in instructions_text.split('\n'):
            line = line.strip()
            if line and not line.isupper() and not line.startswith('=='):
                instructions.append(line)
        recipe['instructions'] = instructions
    
    # Extract timing
    timing_section = re.search(r'TIMING:(.*?)(?=TIPS:|===|$)', block, re.DOTALL)
    if timing_section:
        timing_text = timing_section.group(1)
        recipe['timing'] = [line.strip() for line in timing_text.split('\n') if line.strip()]
    
    # Extract tips
    tips_section = re.search(r'TIPS:(.*?)(?====|$)', block, re.DOTALL)
    if tips_section:
        tips_text = tips_section.group(1)
        recipe['tips'] = [line.strip().lstrip('-').strip() for line in tips_text.split('\n') if line.strip() and '-' in line]
    
    return recipe if recipe.get('title') else None


def main():
    if len(sys.argv) < 2:
        print("Usage: synthesize-recipes.py <query> [extracted_json_file]")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Load extracted recipes if provided
    extracted_recipes = []
    pdf_contexts = []
    
    if len(sys.argv) > 2:
        json_file = sys.argv[2]
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                extracted_recipes = data.get('recipes', [])
                pdf_contexts = data.get('contextual_snippets', [])
        except Exception as e:
            print(f"WARNING: Could not load {json_file}: {e}", file=sys.stderr)
    
    # Synthesize recipes
    recipes = synthesize_recipes(query, extracted_recipes, pdf_contexts)
    
    # Output as JSON
    output = {
        'query': query,
        'recipes_synthesized': len(recipes),
        'recipes': recipes
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    import re
    main()
