#!/usr/bin/env python3
"""
Universal Content Synthesis Framework
Takes extracted content + query, synthesizes complete, actionable responses
Adapts format based on content type (recipe, how-to, reference, data, technical)
"""

import sys
import json
import requests
from pathlib import Path


def query_rag_daemon(query, context=""):
    """Query RAG-Daemon for content synthesis"""
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


def synthesize_universal(query, content_type, extracted_data, contexts):
    """
    Universal synthesis framework.
    Adapts prompt and parsing based on content type.
    """
    
    # Build context from extractions
    context_text = ""
    
    if extracted_data:
        context_text += "## Extracted Content:\n"
        if 'recipes' in extracted_data:
            context_text += "\n### Recipes Found:\n"
            for rec in extracted_data['recipes'][:5]:
                context_text += f"\n**{rec.get('title', 'Untitled')}**\n"
                if 'ingredients' in rec:
                    context_text += "Ingredients:\n" + "\n".join(rec['ingredients'][:10]) + "\n"
                if 'instructions' in rec:
                    context_text += "Instructions:\n" + "\n".join(rec['instructions'][:5]) + "\n"
        elif 'sections' in extracted_data:
            context_text += "\n### Content Sections:\n"
            for sec in extracted_data['sections'][:5]:
                context_text += f"\n{sec.get('text', '')}\n"
    
    if contexts:
        context_text += "\n## Related Information:\n"
        for ctx in contexts[:3]:
            context_text += f"\n{ctx.get('text', '')}\n"
    
    # Create synthesis prompt based on content type
    if content_type == 'recipe':
        prompt = build_recipe_prompt(query, context_text)
    elif content_type == 'howto':
        prompt = build_howto_prompt(query, context_text)
    elif content_type == 'reference':
        prompt = build_reference_prompt(query, context_text)
    elif content_type == 'data':
        prompt = build_data_prompt(query, context_text)
    elif content_type == 'technical':
        prompt = build_technical_prompt(query, context_text)
    else:
        prompt = build_generic_prompt(query, context_text)
    
    print(f"🔄 Synthesizing {content_type} content...", file=sys.stderr)
    
    # Query RAG-Daemon for synthesis
    synthesis = query_rag_daemon(prompt, context_text)
    
    if not synthesis:
        print(f"WARNING: No synthesis returned from RAG-Daemon", file=sys.stderr)
        return None
    
    return synthesis


def build_recipe_prompt(query, context):
    """Prompt for recipe synthesis"""
    return f"""
Based on the extracted recipe data, create 3 complete, actionable recipes for: {query}

{context}

For EACH recipe, provide in this EXACT format:

===RECIPE START===
TITLE: [Recipe Name]
SOURCE: [Which book/source]
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

TIMING:
Prep Time: X minutes
Cook Time: Y minutes
Total: Z minutes
Temperature: ABC°C

TIPS:
- Tip 1
- Tip 2
===RECIPE END===

Create recipes that are READY TO COOK from the information provided.
"""


def build_howto_prompt(query, context):
    """Prompt for how-to guide synthesis"""
    return f"""
Based on the extracted information, create a complete how-to guide for: {query}

{context}

Format as a step-by-step guide with:

===HOWTO START===
TITLE: [Guide Title]
SOURCE: [Book/source]

WHAT YOU NEED:
- Requirement 1
- Requirement 2

STEPS:
1. Step 1 [detailed]
2. Step 2 [detailed]
3. Step 3 [detailed]

⚠️ IMPORTANT:
- Warning 1
- Warning 2

TIPS & VARIATIONS:
- Tip 1
- Tip 2
===HOWTO END===

Create a guide that is ready to follow step-by-step.
"""


def build_reference_prompt(query, context):
    """Prompt for reference material synthesis"""
    return f"""
Based on the extracted information, create a comprehensive reference for: {query}

{context}

Format as structured reference material:

===REFERENCE START===
TITLE: [Reference Title]
SOURCE: [Book/source]

DEFINITIONS:
Term 1: Clear definition
Term 2: Clear definition

KEY PROPERTIES:
- Property 1: Description
- Property 2: Description

EXAMPLES:
Example 1: Description
Example 2: Description

IMPORTANT NOTES:
- Note 1
- Note 2
===REFERENCE END===

Create a reference that is clear, organized, and immediately useful.
"""


def build_data_prompt(query, context):
    """Prompt for data/table synthesis"""
    return f"""
Based on the extracted information, create structured data for: {query}

{context}

Format as data presentation:

===DATA START===
TITLE: [Data Title]
SOURCE: [Book/source]

DATA:
[Create a clean table or structured list]
Column1 | Column2 | Column3
--------|---------|--------
Data    | Data    | Data

ANALYSIS:
- Finding 1
- Finding 2

INSIGHTS:
- Insight 1
- Insight 2
===DATA END===

Create data that is structured, clear, and analyzable.
"""


def build_technical_prompt(query, context):
    """Prompt for technical documentation synthesis"""
    return f"""
Based on the extracted information, create technical documentation for: {query}

{context}

Format as technical guide:

===TECHNICAL START===
TITLE: [Technical Title]
SOURCE: [Book/source]

REQUIREMENTS:
- Requirement 1
- Requirement 2

STEPS:
1. Step 1 [detailed]
2. Step 2 [detailed]
3. Step 3 [detailed]

CODE/CONFIG:
[Code block or configuration example]

EXPLANATION:
[Explanation of what each part does]

TROUBLESHOOTING:
- Problem 1: Solution
- Problem 2: Solution
===TECHNICAL END===

Create documentation that is working, implementable, and clear.
"""


def build_generic_prompt(query, context):
    """Generic fallback prompt"""
    return f"""
Based on the information provided, answer this question comprehensively: {query}

{context}

Provide a complete, actionable answer that covers:
- Main answer
- Key details
- Practical examples or applications
- Important notes or warnings
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: synthesize-content.py <query> [extracted_json_file]")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Load extracted content if provided
    extracted_data = {}
    contexts = []
    content_type = 'unknown'
    
    if len(sys.argv) > 2:
        json_file = sys.argv[2]
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content_type = data.get('content_type', 'unknown')
                extracted_data = data.get('extracted_data', {})
                contexts = data.get('contextual_snippets', [])
        except Exception as e:
            print(f"WARNING: Could not load {json_file}: {e}", file=sys.stderr)
    
    # Synthesize content
    synthesis = synthesize_universal(query, content_type, extracted_data, contexts)
    
    # Output as JSON
    output = {
        'query': query,
        'content_type': content_type,
        'synthesis': synthesis if synthesis else "No synthesis available",
        'confidence': 0.8 if synthesis else 0.3
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
