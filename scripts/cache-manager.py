#!/usr/bin/env python3
"""
H4 Experiment: Synthesis result caching
Cache 14b synthesis results by content hash (1h TTL)
Avoids re-synthesizing identical content
"""

import hashlib
import json
import time
from pathlib import Path

CACHE_DIR = Path("/tmp/pdf-search-cache")
CACHE_TTL = 3600  # 1 hour

class SynthesisCache:
    def __init__(self, cache_dir=CACHE_DIR, ttl=CACHE_TTL):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
    
    def _hash_content(self, content):
        """Create hash of content for cache key"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get(self, content):
        """Get cached synthesis result (if valid)"""
        hash_key = self._hash_content(content)
        cache_file = self.cache_dir / f"{hash_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file) as f:
                data = json.load(f)
            
            # Check TTL
            age = time.time() - data.get('timestamp', 0)
            if age > self.ttl:
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data.get('result')
        except Exception as e:
            print(f"⚠️  Cache read error: {e}")
            return None
    
    def set(self, content, result):
        """Store synthesis result in cache"""
        hash_key = self._hash_content(content)
        cache_file = self.cache_dir / f"{hash_key}.json"
        
        try:
            data = {
                'timestamp': time.time(),
                'result': result
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"⚠️  Cache write error: {e}")
            return False
    
    def cleanup(self):
        """Remove expired cache files"""
        now = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                age = now - data.get('timestamp', 0)
                if age > self.ttl:
                    cache_file.unlink()
            except:
                pass


if __name__ == '__main__':
    # Test
    cache = SynthesisCache()
    
    test_content = "Zutaten: Eier, Butter"
    test_result = {"type": "recipe", "summary": "Ein Test-Rezept"}
    
    # Write to cache
    cache.set(test_content, test_result)
    print(f"✅ Cached: {test_content[:30]}...")
    
    # Read from cache
    cached = cache.get(test_content)
    print(f"✅ Retrieved: {cached}")
    
    # Cleanup
    cache.cleanup()
    print("✅ Cleanup done")
