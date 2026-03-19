#!/usr/bin/env python3
"""
Simple extraction tests (no pytest required).
Tests the extract-content-v4.py pipeline.
"""

import sys
import json
import subprocess
from pathlib import Path

def test_utf8_handling():
    """Test UTF-8 encoding handling."""
    test_input = {
        "pdfs": [
            {
                "name": "test.pdf",
                "path": "/tmp/test.pdf",
                "text": "Ädäl Ümlaut Ñandú café"
            }
        ]
    }
    
    # Write test input
    test_file = Path("/tmp/test_input.json")
    test_file.write_text(json.dumps(test_input))
    
    # Run extraction
    result = subprocess.run([
        "python3",
        "/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/scripts/extract-content-v4.py",
        str(test_file)
    ], capture_output=True, text=True)
    
    # Check output
    if result.returncode == 0:
        print("✅ UTF-8 Handling: PASS")
        return True
    else:
        print(f"❌ UTF-8 Handling: FAIL — {result.stderr}")
        return False

def test_content_type_detection():
    """Test content type detection."""
    test_cases = [
        {
            "name": "recipe.pdf",
            "text": "Zutaten: 2 Eier, 100g Butter, 1 TL Zucker. Anleitung: Rühren, backen.",
            "expected": "recipe"
        },
        {
            "name": "essay.pdf",
            "text": "Der Mensch ist ein Wesen der Vernunft. Dies haben bereits Aristoteles und Kant erkannt.",
            "expected": "narrative"
        },
        {
            "name": "technical.pdf",
            "text": "Definition: Eine Klasse ist ein Objekt, das Attribute und Methoden enthält.",
            "expected": "technical"
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        test_input = {"pdfs": [test_case]}
        test_file = Path("/tmp/test_type.json")
        test_file.write_text(json.dumps(test_input))
        
        result = subprocess.run([
            "python3",
            "/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/scripts/extract-content-v4.py",
            str(test_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            detected_type = output["results"][0]["content_type"]
            if detected_type == test_case["expected"]:
                passed += 1
                print(f"✅ Content Type Detection ({test_case['name']}): {detected_type}")
            else:
                print(f"⚠️  Content Type Detection ({test_case['name']}): expected {test_case['expected']}, got {detected_type}")
        else:
            print(f"❌ Content Type Detection ({test_case['name']}): ERROR")
    
    success = passed == len(test_cases)
    print(f"Content Type Detection: {passed}/{len(test_cases)} PASS")
    return success

def test_path_inclusion():
    """Test that pdf_path is included in output."""
    test_input = {
        "pdfs": [
            {
                "name": "test.pdf",
                "path": "/tmp/test.pdf",
                "text": "Sample content"
            }
        ]
    }
    
    test_file = Path("/tmp/test_path.json")
    test_file.write_text(json.dumps(test_input))
    
    result = subprocess.run([
        "python3",
        "/home/overwrite/.openclaw/workspace/skills/pdf_zusammenfassung/scripts/extract-content-v4.py",
        str(test_file)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        output = json.loads(result.stdout)
        if "pdf_path" in output["results"][0] and output["results"][0]["pdf_path"] == "/tmp/test.pdf":
            print("✅ Path Inclusion: PASS")
            return True
        else:
            print("❌ Path Inclusion: pdf_path not found or incorrect")
            return False
    else:
        print(f"❌ Path Inclusion: ERROR — {result.stderr}")
        return False

if __name__ == '__main__':
    print("Running simple extraction tests...\n")
    
    tests = [
        test_utf8_handling(),
        test_content_type_detection(),
        test_path_inclusion()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total*100):.0f}%")
    
    sys.exit(0 if passed == total else 1)
