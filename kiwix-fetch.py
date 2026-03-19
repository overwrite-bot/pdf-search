#!/usr/bin/env python3
"""
Kiwix Wikipedia Fetcher + 14b Summarizer
Fetch article + extract content + summarize with RAG-Daemon.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re
import urllib.parse

KIWIX_BASE = "http://localhost:8080"
KIWIX_CONTENT = "/content/wikipedia_de_all_maxi_2026-01"

def search_and_get_url(query: str) -> Optional[str]:
    """
    Search Kiwix Wikipedia and return first article URL.
    
    Args:
        query: Search query
    
    Returns:
        Article URL path or None
    """
    try:
        response = requests.get(
            f"{KIWIX_BASE}/search",
            params={
                "content": "wikipedia_de_all_maxi_2026-01",
                "pattern": query
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        # Parse HTML and find first <a href> link
        soup = BeautifulSoup(response.text, 'lxml')
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            # Look for content links
            if '/content/wikipedia_de_all_maxi_2026-01/' in href:
                return href
        
        return None
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

def fetch_article_content(article_url: str, max_chars: int = 3000) -> Optional[Dict]:
    """
    Fetch Wikipedia article content.
    
    Args:
        article_url: URL path (e.g., "/content/...Gärung")
        max_chars: Max characters to extract
    
    Returns:
        Dict with title, url, content or None
    """
    try:
        response = requests.get(
            f"{KIWIX_BASE}{article_url}",
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Remove script/style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get title
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "Wikipedia Artikel"
        
        # Extract paragraphs
        content = []
        for p in soup.find_all('p')[:12]:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                content.append(text)
        
        full_text = '\n\n'.join(content)
        
        if not full_text:
            return None
        
        return {
            "title": title,
            "url": article_url,
            "content": full_text[:max_chars],
            "source": "Wikipedia (Kiwix Offline)"
        }
    
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return None

def summarize_with_14b(text: str, query: str, title: str) -> str:
    """
    Use RAG-Daemon 14b to summarize Wikipedia article.
    """
    try:
        prompt = f"""Fasse diesen Wikipedia-Artikel zu "{query}" in 3-4 Sätzen zusammen.
Fokus: Definition, Kernaussagen, praktische Relevanz.

Artikel: {title}
Text:
{text[:1500]}"""
        
        response = requests.post(
            "http://127.0.0.1:5555/ask",
            json={"query": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("answer", "")
        
        return ""
    
    except Exception as e:
        print(f"⚠️  Summary failed: {e}")
        return ""

def fetch_and_summarize(query: str) -> Optional[Dict]:
    """
    Full pipeline: Search → Fetch → Summarize
    """
    # Search
    print(f"  🔍 Searching Kiwix...", end="", flush=True)
    article_url = search_and_get_url(query)
    
    if not article_url:
        print(" ❌ Not found")
        return None
    
    print(" ✅")
    
    # Fetch
    print(f"  📥 Fetching article...", end="", flush=True)
    article = fetch_article_content(article_url, max_chars=3000)
    
    if not article:
        print(" ❌ Failed")
        return None
    
    print(" ✅")
    
    # Summarize
    print(f"  🧠 Summarizing with 14b...", end="", flush=True)
    summary = summarize_with_14b(article['content'], query, article['title'])
    
    if summary:
        print(" ✅")
    else:
        print(" ⚠️  Using excerpt instead")
        summary = article['content'][:800]
    
    article['summary'] = summary
    return article

def main():
    """CLI interface"""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: kiwix-fetch.py <query> [--full]")
        sys.exit(1)
    
    query = sys.argv[1]
    full = "--full" in sys.argv
    
    print(f"📖 Fetching Wikipedia article for '{query}':\n")
    
    result = fetch_and_summarize(query)
    
    if not result:
        print("\n❌ No article found")
        sys.exit(1)
    
    print(f"\n📄 **{result['title']}**")
    print(f"   Quelle: {result['source']}\n")
    
    if full:
        print("**Volltext:**\n")
        print(result['content'])
    else:
        print("**Zusammenfassung (14b):**\n")
        print(result['summary'])
    
    # JSON output for integration
    print("\n---JSON---")
    print(json.dumps({
        "title": result['title'],
        "summary": result['summary'],
        "content": result['content'],
        "source": result['source']
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
