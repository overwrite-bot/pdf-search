#!/usr/bin/env python3
"""
extract-content-v4.py — Universal Content Type Detection + Raw Extraction

Identifies content type (Recipe/Technical/Narrative) and extracts raw content.
Pure heuristic, no LLM.
"""

import re
import json
from pathlib import Path

def identify_content_type(text):
    """
    Identify content type based on text structure.
    Returns: "recipe" | "technical" | "narrative"
    """
    lines = text.split('\n')
    
    # Count patterns
    recipe_patterns = 0
    technical_patterns = 0
    narrative_patterns = 0
    
    # Recipe patterns: Zutaten, Schritte, Messwerte
    if re.search(r'(Zutaten|Ingredients|Zutaten:)', text, re.IGNORECASE):
        recipe_patterns += 2
    if re.search(r'(Anleitung|Instructions|Schritte:|Steps:)', text, re.IGNORECASE):
        recipe_patterns += 2
    if re.search(r'\d+\s*(g|kg|ml|l|TL|EL|Stück)', text):  # Measurement patterns
        recipe_patterns += 2
    if re.search(r'^\d+\.\s+[A-Z]', text, re.MULTILINE):  # Numbered lists
        recipe_patterns += 1
    
    # Technical patterns: Code, Definitions, Lists ohne Messwerte
    if re.search(r'(def |class |function |import |return )', text):  # Code
        technical_patterns += 3
    if re.search(r'(Definition:|Konzept:|Key Point|Algorithmus|Parameter)', text, re.IGNORECASE):
        technical_patterns += 2
    if re.search(r'^[-•]\s+[A-Z][a-z]+.*:', text, re.MULTILINE):  # Concept lists
        technical_patterns += 1
    if re.search(r'(Machine Learning|Neural|Algorithm|API|Function|Method)', text):
        technical_patterns += 2
    
    # Narrative patterns: Fließtext, lange Absätze, keine Listen
    avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
    if avg_line_length > 60:  # Long lines = narrative
        narrative_patterns += 2
    
    list_lines = sum(1 for line in lines if re.match(r'^[-•0-9]\s+', line))
    if list_lines < len(lines) * 0.2:  # Few lists = narrative
        narrative_patterns += 1
    
    if len(text) > 500 and not re.search(r'(Zutaten|Ingredients)', text):
        narrative_patterns += 1  # Long text without recipe markers
    
    # Determine type
    max_score = max(recipe_patterns, technical_patterns, narrative_patterns)
    
    if max_score == 0:
        return "narrative"  # Default fallback
    
    if recipe_patterns >= max(technical_patterns, narrative_patterns):
        return "recipe"
    elif technical_patterns >= narrative_patterns:
        return "technical"
    else:
        return "narrative"


def extract_recipe(text):
    """Extract recipe structure from text."""
    content = {
        "name": None,
        "ingredients": [],
        "steps": [],
        "tips": None
    }
    
    # Find recipe name (first heading-like line)
    lines = text.split('\n')
    for line in lines:
        if len(line) > 5 and len(line) < 100 and not re.match(r'^[-•]', line):
            content["name"] = line.strip()
            break
    
    # Extract ingredients section
    ing_started = False
    ing_lines = []
    for line in lines:
        if re.search(r'(Zutaten|Ingredients):', line, re.IGNORECASE):
            ing_started = True
            continue
        if ing_started:
            if re.search(r'(Anleitung|Instructions|Schritte):', line, re.IGNORECASE):
                break
            if re.match(r'^[-•0-9]\s+', line) or re.search(r'\d+\s*(g|kg|ml|l)', line):
                ing_lines.append(line.strip())
    
    content["ingredients"] = ing_lines[:15]  # Max 15 ingredients
    
    # Extract steps
    step_started = False
    step_lines = []
    for line in lines:
        if re.search(r'(Anleitung|Instructions|Schritte):', line, re.IGNORECASE):
            step_started = True
            continue
        if step_started:
            if re.search(r'(Tipp|Hinweis|Note):', line, re.IGNORECASE):
                break
            if re.match(r'^\d+\.\s+', line) or re.match(r'^[-•]\s+', line):
                step_lines.append(line.strip())
    
    content["steps"] = step_lines[:20]  # Max 20 steps
    
    return content


def extract_technical(text):
    """Extract technical content (concepts, definitions, key points)."""
    content = {
        "title": None,
        "definitions": [],
        "key_points": [],
        "concepts": []
    }
    
    lines = text.split('\n')
    
    # Find title
    for line in lines:
        if len(line) > 10 and len(line) < 150 and re.match(r'^[A-Z]', line):
            content["title"] = line.strip()
            break
    
    # Extract definitions
    for i, line in enumerate(lines):
        if re.search(r'Definition:', line, re.IGNORECASE):
            # Take this line + next 2 lines
            definition = '\n'.join(lines[i:min(i+3, len(lines))])
            content["definitions"].append(definition[:200])
    
    # Extract lists as key points / concepts
    current_list = []
    in_list = False
    for line in lines:
        if re.match(r'^[-•]\s+', line):
            if not in_list:
                in_list = True
            item = re.sub(r'^[-•]\s+', '', line).strip()
            current_list.append(item)
        elif in_list and line.strip() == '':
            if current_list:
                content["key_points"].extend(current_list[:10])
            current_list = []
            in_list = False
    
    if current_list:
        content["key_points"].extend(current_list[:10])
    
    return content


def extract_narrative(text):
    """Extract narrative content (essays, summaries)."""
    content = {
        "title": None,
        "summary": None,
        "quotes": [],
        "concepts": []
    }
    
    lines = text.split('\n')
    
    # Find title (first non-empty line that looks like a title)
    for line in lines:
        if len(line) > 5 and len(line) < 100 and re.match(r'^[A-Z]', line):
            content["title"] = line.strip()
            break
    
    # Extract first 3 paragraphs as summary (or first 300 chars)
    text_clean = ' '.join(line for line in lines if line.strip())
    content["summary"] = text_clean[:400].strip()
    
    # Extract quotes (lines in quotation marks)
    for line in lines:
        if '"' in line or '„' in line:
            quote = re.search(r'[„"]([^„"]+)[„"]', line)
            if quote:
                content["quotes"].append(quote.group(1)[:150])
    
    # Extract concepts from bullet lists
    for line in lines:
        if re.match(r'^[-•]\s+', line):
            concept = re.sub(r'^[-•]\s+', '', line).strip()
            if len(concept) > 5 and len(concept) < 100:
                content["concepts"].append(concept)
    
    return content


def extract_from_pdf_text(pdf_text, pdf_name, pdf_path=None):
    """
    Extract content from raw PDF text.
    Returns: {pdf_name, pdf_path, content_type, raw_content}
    """
    # Skip more metadata/TOC (first 2000 chars more aggressive)
    # Then take next 5000 chars (more content, less metadata)
    # Total: up to 5000 chars per PDF (even better content coverage)
    # H1 Experiment: Longer extraction window for better relevance
    text = pdf_text[2000:7000] if len(pdf_text) > 2000 else pdf_text
    
    content_type = identify_content_type(text)
    
    if content_type == "recipe":
        extracted = extract_recipe(text)
    elif content_type == "technical":
        extracted = extract_technical(text)
    else:  # narrative
        extracted = extract_narrative(text)
    
    return {
        "pdf_name": pdf_name,
        "pdf_path": pdf_path,
        "content_type": content_type,
        "extracted": extracted
    }


def main():
    """
    Main entry point.
    Usage: extract-content-v4.py <json_input>
    Input JSON: {pdfs: [{name, text}, ...]}
    Output: JSON with extracted content
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: extract-content-v4.py <json_input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file) as f:
            data = json.load(f)
        
        results = []
        for pdf in data.get("pdfs", []):
            extracted = extract_from_pdf_text(
                pdf["text"],
                pdf["name"],
                pdf.get("path")  # Get PDF path if available
            )
            results.append(extracted)
        
        output = {
            "extracted_count": len(results),
            "results": results
        }
        
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
