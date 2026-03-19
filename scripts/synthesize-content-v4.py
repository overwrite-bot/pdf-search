#!/usr/bin/env python3
"""
synthesize-content-v4.py — Ollama qwen3:14b Content Synthesis

Takes raw extracted content and enhances it using local Ollama LLM.
Type-specific prompts for Recipe / Technical / Narrative.
"""

import json
import sys
import subprocess
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"

def call_ollama(prompt, max_tokens=300):
    """
    Call Ollama qwen3:14b for content synthesis.
    Returns: LLM output text
    """
    try:
        cmd = [
            "curl",
            "-X", "POST",
            OLLAMA_URL,
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # Lower temperature for consistency
                "num_predict": max_tokens
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None
        
        response = json.loads(result.stdout)
        return response.get("response", "").strip()
    
    except Exception as e:
        print(f"Ollama error: {e}", file=sys.stderr)
        return None


def synthesize_recipe(extracted):
    """Enhance recipe using 14b."""
    if not extracted.get("steps"):
        return extracted  # No steps to enhance
    
    steps_text = "\n".join(extracted["steps"])
    
    prompt = f"""Bitte verdeutliche und verbessere folgende Kochschritte. 
Mache sie detailliert, professionell und anfängerfreundlich.
Antworte nur mit den verbesserten Schritten, keine Vorrede.

Original-Schritte:
{steps_text}

Verbesserte Schritte:"""
    
    enhanced_steps = call_ollama(prompt)
    
    if enhanced_steps:
        # Parse steps back to list
        step_list = [s.strip() for s in enhanced_steps.split('\n') if s.strip()]
        extracted["steps"] = step_list[:15]
    
    return extracted


def synthesize_technical(extracted):
    """Extract and enhance key concepts using 14b."""
    if not extracted.get("key_points") and not extracted.get("definitions"):
        return extracted
    
    points_text = "\n".join(extracted.get("key_points", [])[:10])
    defs_text = "\n".join(extracted.get("definitions", [])[:3])
    
    prompt = f"""Analysiere folgende technische Konzepte und extrahiere klare, prägnante Key Points.
Antworte mit einer strukturierten Liste von maximal 5 Key Points.

Konzepte:
{points_text}

Definitionen:
{defs_text}

Key Points (strukturiert):"""
    
    enhanced = call_ollama(prompt)
    
    if enhanced:
        key_points = [p.strip() for p in enhanced.split('\n') if p.strip()]
        extracted["key_points"] = key_points[:5]
    
    return extracted


def synthesize_narrative(extracted):
    """Summarize and extract key quotes using 14b."""
    summary_text = extracted.get("summary", "")
    
    if not summary_text or len(summary_text) < 50:
        return extracted
    
    prompt = f"""Schreibe eine prägnante Zusammenfassung in maximal 3 Sätzen.
Extrahiere auch 1-2 Schlüsselkonzepte aus dem Text.

Original-Text:
{summary_text}

Zusammenfassung:"""
    
    enhanced = call_ollama(prompt)
    
    if enhanced:
        lines = enhanced.split('\n')
        # First lines = summary
        summary_lines = [l for l in lines[:3] if l.strip()]
        extracted["summary"] = ' '.join(summary_lines)
        
        # Extract concepts from the response
        concept_prompt = f"""Extrahiere aus diesem Text die 3 wichtigsten Konzepte/Begriffe als stichwortliste.
Text:
{enhanced}

Konzepte:"""
        
        concepts = call_ollama(concept_prompt, max_tokens=100)
        if concepts:
            concept_list = [c.strip() for c in concepts.split('\n') if c.strip()]
            extracted["concepts"] = concept_list[:3]
    
    return extracted


def synthesize_content(extracted_content):
    """
    Synthesize extracted content using Ollama.
    Input: List of extracted content objects
    Output: Enhanced content objects
    """
    results = []
    
    for item in extracted_content:
        content_type = item.get("content_type")
        extracted = item.get("extracted", {})
        
        # Skip if no extracted content
        if not extracted:
            results.append(item)
            continue
        
        # Type-specific synthesis
        if content_type == "recipe":
            enhanced = synthesize_recipe(extracted)
        elif content_type == "technical":
            enhanced = synthesize_technical(extracted)
        elif content_type == "narrative":
            enhanced = synthesize_narrative(extracted)
        else:
            enhanced = extracted
        
        item["extracted"] = enhanced
        results.append(item)
    
    return results


def main():
    """
    Main entry point.
    Usage: synthesize-content-v4.py <json_input_file> [output_file]
    Input: JSON from extract-content-v4.py
    Output: Enhanced JSON with synthesis
    """
    if len(sys.argv) < 2:
        print("Usage: synthesize-content-v4.py <json_input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Load extracted content
        with open(input_file) as f:
            data = json.load(f)
        
        extracted_list = data.get("results", [])
        
        # Synthesize
        synthesized = synthesize_content(extracted_list)
        
        output = {
            "synthesized_count": len(synthesized),
            "results": synthesized
        }
        
        # Output
        output_json = json.dumps(output, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_json)
            print(f"✓ Synthesized output written to {output_file}")
        else:
            print(output_json)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
