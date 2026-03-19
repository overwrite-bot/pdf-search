#!/usr/bin/env python3
"""
Kiwix Wikipedia Search Wrapper
Queries local offline Wikipedia and returns structured results.
"""

import requests
import json
from typing import List, Dict
import re

KIWIX_URL = "http://localhost:8080"

def search_kiwix(query: str, limit: int = 5) -> List[Dict]:
    """
    Search Kiwix Wikipedia for query.
    
    Args:
        query: Search query
        limit: Max results to return
    
    Returns:
        List of result dicts with title, url, source
    """
    try:
        # Query Kiwix search endpoint
        response = requests.get(
            f"{KIWIX_URL}/search",
            params={"pattern": query},
            timeout=5
        )
        
        if response.status_code != 200:
            return []
        
        # Extract links using regex
        # Look for links in Kiwix search results
        pattern = r'<a href="([^"]+/wiki/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, response.text)
        
        results = []
        for url, title in matches[:limit]:
            results.append({
                "title": title.strip(),
                "url": url,
                "source": "Wikipedia (Kiwix)"
            })
        
        return results
    
    except Exception as e:
        print(f"❌ Kiwix search error: {e}")
        return []

def extract_kiwix_content(url: str, chars: int = 500) -> str:
    """Extract article content from Kiwix"""
    try:
        response = requests.get(f"{KIWIX_URL}{url}", timeout=5)
        if response.status_code != 200:
            return ""
        
        # Simple text extraction (strip HTML)
        text = response.text
        # Remove script/style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:chars]
    except Exception as e:
        print(f"❌ Content extraction error: {e}")
        return ""

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: kiwix-search.py <query> [--limit 5]")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = 5
    
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    
    print(f"🔍 Searching Wikipedia for: '{query}'...")
    results = search_kiwix(query, limit)
    
    print(f"\n📚 Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print()

if __name__ == "__main__":
    main()
