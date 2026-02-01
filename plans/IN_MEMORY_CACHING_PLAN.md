# In-Memory Caching Strategy (No External Services)

## Overview

Implement lightweight in-memory caching using Python's built-in `functools.lru_cache` and `cachetools` library (simple pip install, no external service).

**Benefits:**
- ✅ No Redis or external service required
- ✅ Zero configuration - works out of the box
- ✅ Automatic memory management
- ✅ Thread-safe
- ✅ Easy to implement
- ✅ Can save 80-90% on repeat scans

---

## Solution 1: Use Python's Built-in LRU Cache

### What to Cache

#### 1. **Ingredient Embeddings** (Highest Impact)
- Cache the embedding for each ingredient name
- Ingredients don't change, so cache can be long-lived
- Eliminates OpenAI API calls for common ingredients

#### 2. **Vector Search Results**
- Cache vector search results per ingredient
- Ingredients database changes rarely
- Can use TTL of 1 hour or more

#### 3. **Product Risk Assessments** (Optional)
- Cache complete risk assessment per product + user combo
- Invalidate when user profile changes
- Most valuable for popular products

---

## Implementation Plan

### Option A: `functools.lru_cache` (Built-in, Zero Dependencies)

**Pros:**
- Built into Python standard library
- Zero external dependencies
- Automatic size management
- Very simple to implement

**Cons:**
- No TTL (time-to-live) support
- Cache persists only during process lifetime
- Less flexible than cachetools

**Best for**: Embedding cache (embeddings never change)

### Option B: `cachetools` (Lightweight Library)

**Pros:**
- Supports TTL (time-based expiration)
- Multiple cache strategies (LRU, LFU, TTL)
- Still simple, no external service
- Better for data that can become stale

**Cons:**
- Requires pip install (but very lightweight)
- Slightly more complex than functools

**Best for**: Vector search and risk assessment caching

---

## Implementation Strategy

### 1. Cache Ingredient Embeddings

**Location**: [`backend/utils/vector_search.py`](backend/utils/vector_search.py:34)

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def _generate_embedding_sync(query: str) -> tuple:
    """Cached version - converts to tuple for hashability"""
    response = client.embeddings.create(
        input=query.strip(),
        model=EMBEDDING_MODEL
    )
    # Convert list to tuple for caching (lists aren't hashable)
    return tuple(response.data[0].embedding)

async def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding with caching"""
    # Call cached version and convert back to list
    embedding_tuple = _generate_embedding_sync(query)
    return list(embedding_tuple)
```

**Impact:**
- First call: 200ms (OpenAI API)
- Cached calls: <1ms (memory lookup)
- **99.5% faster for cached ingredients**

---

### 2. Cache Vector Search Results

**Location**: [`backend/utils/vector_search.py`](backend/utils/vector_search.py:70)

Using `cachetools` with TTL:

```python
from cachetools import TTLCache
import threading

# Thread-safe cache with 1-hour TTL, max 500 entries
_vector_search_cache = TTLCache(maxsize=500, ttl=3600)
_cache_lock = threading.Lock()

async def search_similar_ingredients(
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    risk_level_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search with caching"""
    
    # Create cache key
    cache_key = f"{query}:{limit}:{risk_level_filter}"
    
    # Check cache first
    with _cache_lock:
        if cache_key in _vector_search_cache:
            logger.debug(f"Cache HIT for ingredient: {query}")
            return _vector_search_cache[cache_key]
    
    logger.debug(f"Cache MISS for ingredient: {query}")
    
    # ... existing search logic ...
    results = # ... search results ...
    
    # Store in cache
    with _cache_lock:
        _vector_search_cache[cache_key] = results
    
    return results
```

**Impact:**
- First scan: 200ms per ingredient
- Subsequent scans: ~5ms (cache hit)
- **97% faster for repeat ingredients**

---

### 3. Cache Complete Risk Assessments (Optional)

**Location**: [`backend/utils/risk_scorer.py`](backend/utils/risk_scorer.py:472)

```python
from cachetools import TTLCache
import hashlib

# Cache assessments for 30 minutes
_assessment_cache = TTLCache(maxsize=100, ttl=1800)

async def generate_risk_score_for_product(
    product_id: int,
    product_name: str,
    ingredients: list,
    user_id: str
) -> dict:
    """Generate risk score with caching"""
    
    # Create cache key from product + user + ingredients
    ingredients_str = ','.join(sorted(ingredients))
    cache_key = hashlib.md5(
        f"{product_id}:{user_id}:{ingredients_str}".encode()
    ).hexdigest()
    
    # Check cache
    if cache_key in _assessment_cache:
        logger.info(f"Cache HIT for product assessment: {product_name}")
        return _assessment_cache[cache_key]
    
    logger.info(f"Cache MISS for product assessment: {product_name}")
    
    # ... existing assessment logic ...
    response = # ... assessment result ...
    
    # Cache the result
    _assessment_cache[cache_key] = response
    
    return response
```

**Impact:**
- First scan: 1,200ms
- Repeat scan (same product + user): ~50ms
- **96% faster for repeat scans**

---

## Cache Management

### Memory Usage Estimates

```python
# Embedding cache: 1000 ingredients × 1536 floats × 8 bytes = ~12 MB
# Vector search cache: 500 entries × ~5KB each = ~2.5 MB
# Assessment cache: 100 entries × ~10KB each = ~1 MB
# ────────────────────────────────────────────────────────
# Total: ~15.5 MB
```

**Conclusion**: Very lightweight, suitable for serverless (Vercel has 1GB memory limit)

### Cache Invalidation Strategy

1. **Embedding cache**: Never invalidate (embeddings don't change)
2. **Vector search cache**: TTL of 1 hour (ingredient data rarely changes)
3. **Assessment cache**: TTL of 30 minutes (balance freshness vs performance)

### Clearing Cache (if needed)

```python
# Admin endpoint to clear caches
@router.post("/admin/cache/clear", include_in_schema=False)
async def clear_caches():
    """Clear all in-memory caches"""
    with _cache_lock:
        _vector_search_cache.clear()
    _assessment_cache.clear()
    return {"status": "caches_cleared"}
```

---

## Installation

### If using cachetools:
```bash
cd backend
pip install cachetools
```

Add to `requirements.txt`:
```
cachetools==5.3.2
```

---

## Performance Comparison

### Without Caching (Current with Parallelization)
```
First scan: 1,200ms
Second scan (same product): 1,200ms
Third scan (same product): 1,200ms
```

### With In-Memory Caching
```
First scan: 1,200ms
Second scan (same product): ~50-100ms  (96% faster)
Third scan (same product): ~50-100ms   (96% faster)
Fourth scan (different user, same product): ~500ms (embeddings + vector cached)
```

---

## Deployment Considerations

### ⚠️ Important: Vercel Serverless Functions

**Issue**: Vercel serverless functions are **stateless** - each request may hit a different instance.

**Impact on caching:**
- ✅ Caching works within a single instance
- ❌ Cache not shared across instances
- ✅ Popular products will likely hit cached instances (due to instance reuse)
- ✅ Still provides value - Vercel reuses warm instances

**Mitigation**: 
- Cache is still valuable for instance reuse (Vercel keeps instances warm)
- Even 30-50% cache hit rate = significant improvement
- Zero cost solution vs Redis

**Better solution for Vercel**: Use Vercel KV (but that's an external service)

---

## Recommendation

### Immediate Implementation (No External Service)

**Priority 1**: Cache ingredient embeddings
- Use `functools.lru_cache`
- Built-in, zero config
- Works great even in serverless
- Save 99% on embedding generation for repeat ingredients

**Priority 2**: Cache vector search results
- Use `cachetools` with 1-hour TTL
- pip install cachetools (lightweight)
- Good value even with serverless limitations

**Priority 3**: Skip full assessment caching (for now)
- Less valuable in serverless environment
- Better to do if you add Redis later

---

## Implementation Order

1. **Start with embedding cache** (5 minutes to implement)
   - Biggest impact
   - Zero dependencies
   - Works everywhere

2. **Add vector search cache** (10 minutes)
   - Install cachetools
   - Good secondary benefit
   - Simple implementation

3. **Monitor cache hit rates** in logs
   - See actual performance improvement
   - Decide if full assessment caching is worth it

---

## Code Changes Required

1. **`backend/utils/vector_search.py`**:
   - Add embedding cache (10 lines)
   - Add vector search cache (20 lines)

2. **`backend/requirements.txt`**:
   - Add `cachetools==5.3.2`

3. **No other changes needed**

---

## Expected Overall Performance

### Current (With Parallelization)
- First scan: 1,200ms
- Repeat scan: 1,200ms

### With In-Memory Caching
- First scan: 1,200ms
- Second scan: 100-200ms (80-90% cache hits)
- Popular products: 50-100ms (95%+ cache hits)

**Net improvement**: **5-20x faster for repeat scans**, zero infrastructure cost.
