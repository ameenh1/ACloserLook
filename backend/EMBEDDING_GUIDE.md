# Embedding & Vector Search Guide

## Overview

This guide covers the data ingestion and embedding pipeline for the Lotus backend's ingredient database. The system uses OpenAI's `text-embedding-3-small` model to generate semantic embeddings stored in Supabase's vector database, enabling intelligent similarity search across ingredients.

**Key Components:**
- `backend/data/ingredients.json` - Ingredient dataset with risk levels and descriptions
- `backend/scripts/embed_ingredients.py` - Embedding generation and Supabase upsert script
- `backend/utils/vector_search.py` - Semantic search utilities for querying embeddings

---

## Data Format Specification

### Ingredients JSON Structure

The `backend/data/ingredients.json` file contains a comprehensive ingredient database with the following schema:

```json
{
  "ingredients": [
    {
      "id": 1,
      "name": "Fragrance",
      "description": "Synthetic fragrance compounds used to mask odors in period products. May contain undisclosed chemicals...",
      "risk_level": "High"
    }
  ]
}
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Yes | Unique identifier (1-30+) |
| `name` | String | Yes | Ingredient name (e.g., "Fragrance", "Rayon") |
| `description` | String | Yes | 2-3 sentence description of health impacts and concerns |
| `risk_level` | String | Yes | Risk classification: `Low`, `Medium`, or `High` |

**Risk Level Definitions:**

- **High Risk**: Ingredients with documented health concerns, carcinogens, or significant health impact potential
- **Medium Risk**: Ingredients with some concerns or data gaps requiring caution
- **Low Risk**: Natural or well-tested ingredients with minimal health risks

### Supabase Table Schema

The `ingredients_library` table must have the following structure:

```sql
CREATE TABLE ingredients_library (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  risk_level VARCHAR(10) NOT NULL,
  embedding VECTOR(1536) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for efficient similarity search
CREATE INDEX ON ingredients_library USING ivfflat (embedding vector_cosine_ops);

-- Optional: Create RPC function for vector search (Supabase-specific)
CREATE OR REPLACE FUNCTION search_ingredients(
  query_embedding VECTOR,
  match_limit INT,
  match_threshold FLOAT
) RETURNS TABLE (
  id INT,
  name VARCHAR,
  description TEXT,
  risk_level VARCHAR,
  similarity_score FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    ingredients_library.id,
    ingredients_library.name,
    ingredients_library.description,
    ingredients_library.risk_level,
    (1 - (ingredients_library.embedding <=> query_embedding)) as similarity_score
  FROM ingredients_library
  WHERE 1 - (ingredients_library.embedding <=> query_embedding) > match_threshold
  ORDER BY ingredients_library.embedding <=> query_embedding
  LIMIT match_limit;
END;
$$ LANGUAGE plpgsql;
```

---

## Running the Embedding Script

### Prerequisites

1. **Environment Setup:**
   ```bash
   # Ensure .env file is configured with:
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   OPENAI_API_KEY=your_openai_api_key
   ```

2. **Dependencies Installed:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Supabase Table Created:**
   - Ensure `ingredients_library` table exists with vector column
   - Run the schema creation SQL above

### Execution

**Option 1: Direct Script Execution**

```bash
cd backend
python scripts/embed_ingredients.py
```

**Option 2: From Project Root**

```bash
python backend/scripts/embed_ingredients.py
```

### Output

The script produces:

1. **Console Logging:** Real-time progress with:
   - Embedding generation status
   - Batch upsert progress
   - Error tracking and failed ingredients
   - Summary statistics

2. **Log File:** `embedding_process.log` contains:
   - Timestamp for each operation
   - Detailed error messages for debugging
   - Complete execution history

**Expected Output Example:**

```
2026-01-31 12:00:00 - IngredientEmbedder - INFO - ============================================================
2026-01-31 12:00:00 - IngredientEmbedder - INFO - EMBEDDING PIPELINE STARTED
2026-01-31 12:00:00 - IngredientEmbedder - INFO - ============================================================
2026-01-31 12:00:00 - IngredientEmbedder - INFO - Loading ingredients from backend/data/ingredients.json
2026-01-31 12:00:00 - IngredientEmbedder - INFO - Successfully loaded 30 ingredients
2026-01-31 12:00:00 - IngredientEmbedder - INFO - Generating embeddings for 30 ingredients
2026-01-31 12:00:02 - IngredientEmbedder - INFO - Progress: 5/30 embeddings generated
2026-01-31 12:00:04 - IngredientEmbedder - INFO - Progress: 10/30 embeddings generated
...
2026-01-31 12:00:15 - IngredientEmbedder - INFO - Upserting 30 ingredients to Supabase
2026-01-31 12:00:15 - IngredientEmbedder - INFO - Batch 1/2 upserted successfully (20 records)
2026-01-31 12:00:16 - IngredientEmbedder - INFO - Batch 2/2 upserted successfully (10 records)
2026-01-31 12:00:16 - IngredientEmbedder - INFO - ============================================================
2026-01-31 12:00:16 - IngredientEmbedder - INFO - EMBEDDING PIPELINE COMPLETED
2026-01-31 12:00:16 - IngredientEmbedder - INFO - Successfully embedded: 30
2026-01-31 12:00:16 - IngredientEmbedder - INFO - Failed: 0
2026-01-31 12:00:16 - IngredientEmbedder - INFO - ============================================================
```

### Configuration Parameters

Modify these constants in `embed_ingredients.py` to customize behavior:

```python
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI model
EMBEDDING_DIMENSION = 1536                   # Output vector size
BATCH_SIZE = 20                              # Records per upsert batch
RETRY_ATTEMPTS = 3                           # API retry attempts
RETRY_DELAY = 2                              # Initial retry delay (seconds)
```

---

## Vector Search Usage

### Basic Semantic Search

```python
from backend.utils.vector_search import search_similar_ingredients
import asyncio

# Async usage
async def find_similar():
    results = await search_similar_ingredients(
        query="fragrance effects on health",
        limit=5
    )
    for result in results:
        print(f"{result['name']}: {result['similarity_score']:.2%}")

asyncio.run(find_similar())
```

### Search by Name

```python
from backend.utils.vector_search import search_by_name
import asyncio

async def find_by_name():
    results = await search_by_name(
        name_query="rayon",
        limit=5
    )
    return results

asyncio.run(find_by_name())
```

### Search with Risk Level Filter

```python
from backend.utils.vector_search import search_similar_ingredients
import asyncio

async def high_risk_search():
    results = await search_similar_ingredients(
        query="synthetic chemicals",
        limit=10,
        risk_level_filter="High"  # Only high-risk ingredients
    )
    return results

asyncio.run(high_risk_search())
```

### Get Specific Ingredient

```python
from backend.utils.vector_search import get_ingredient_by_id
import asyncio

async def fetch_ingredient():
    ingredient = await get_ingredient_by_id(ingredient_id=1)
    return ingredient

asyncio.run(fetch_ingredient())
```

### Get All Ingredients

```python
from backend.utils.vector_search import get_all_ingredients
import asyncio

async def list_all():
    # All ingredients
    all_ingredients = await get_all_ingredients(limit=100)
    
    # Only low-risk ingredients
    safe_ingredients = await get_all_ingredients(
        limit=100,
        risk_level_filter="Low"
    )
    return safe_ingredients

asyncio.run(list_all())
```

### Synchronous Wrapper

For non-async contexts:

```python
from backend.utils.vector_search import search_sync

results = search_sync(
    query="synthetic fibers",
    limit=5,
    risk_level_filter="High"
)
```

### Integration in FastAPI Endpoints

```python
from fastapi import APIRouter, Query
from backend.utils.vector_search import search_similar_ingredients, get_all_ingredients

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

@router.get("/search")
async def search_ingredients(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    risk_level: str = Query(None)
):
    """Search for similar ingredients using semantic search"""
    results = await search_similar_ingredients(
        query=q,
        limit=limit,
        risk_level_filter=risk_level
    )
    return {"query": q, "results": results}

@router.get("/list")
async def list_ingredients(
    limit: int = Query(20, ge=1, le=100),
    risk_level: str = Query(None)
):
    """List all ingredients with optional filtering"""
    results = await get_all_ingredients(
        limit=limit,
        risk_level_filter=risk_level
    )
    return {"results": results}
```

---

## Return Value Format

### Search Results

All search functions return a list of dictionaries with:

```python
[
  {
    "id": 1,
    "name": "Fragrance",
    "description": "Synthetic fragrance compounds...",
    "risk_level": "High",
    "similarity_score": 0.87  # Only in vector search results (0-1)
  },
  ...
]
```

**Fields:**
- `id`: Unique ingredient identifier
- `name`: Ingredient name
- `description`: Health impact description
- `risk_level`: `Low`, `Medium`, or `High`
- `similarity_score`: (Vector search only) Relevance score 0-1, higher = more relevant

---

## Embedding Model Details

### Text Embedding 3 Small

**Model:** `text-embedding-3-small`
- **Dimensions:** 1536
- **Cost:** ~$0.02 per 1M tokens
- **Performance:** Optimized for cost without sacrificing quality
- **Use Case:** Large-scale semantic search applications

**Input Limitations:**
- Maximum 8,191 tokens per input
- Batch processing recommended for multiple texts
- Rate limits: Check OpenAI documentation for current limits

**Embedding Quality:**
- Captures semantic meaning of ingredient descriptions
- Enables cosine similarity matching
- Supports multi-language queries (if descriptions translated)

---

## Troubleshooting Guide

### Issue: `OPENAI_API_KEY not set`

**Solution:** Ensure `.env` file contains:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Run after setting environment variable:
```bash
python backend/scripts/embed_ingredients.py
```

### Issue: `Supabase credentials not configured`

**Solution:** Verify `.env` contains all required Supabase credentials:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anonymous-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Issue: `Rate limited. Retrying...`

**Cause:** OpenAI API rate limits exceeded
**Solution:** 
- Script automatically retries with exponential backoff (2s, 4s, 8s)
- If persisting, implement longer delays or batch fewer embeddings
- Check OpenAI rate limit status at platform.openai.com

### Issue: `Failed to upsert batch`

**Common Causes:**
1. **Vector dimension mismatch:** Ensure embedding is exactly 1536 dimensions
2. **Table doesn't exist:** Create `ingredients_library` table first
3. **Permission issues:** Use `SUPABASE_SERVICE_ROLE_KEY` for upserts
4. **Data type mismatch:** Verify all fields match schema (id: integer, name: string, etc.)

**Debug:**
```bash
# Check table structure
psql -h your-db-host -U postgres -c "\d ingredients_library"

# Verify row count after partial upsert
SELECT COUNT(*) FROM ingredients_library;
```

### Issue: `No similar ingredients found`

**Possible Causes:**
1. **Empty database:** Run embedding script to populate data
2. **Query too specific:** Try broader search terms
3. **Threshold too high:** Default threshold is 0.1 (10% similarity)

**Solution:**
```python
# Lower threshold for more results
async def lenient_search():
    results = await search_similar_ingredients(
        query="fibers",
        limit=10  # Increase limit
    )
```

### Issue: `Connection to Supabase failed`

**Checks:**
1. Verify internet connection
2. Confirm Supabase project is active
3. Check credentials haven't expired
4. Verify firewall isn't blocking Supabase
5. Test connection manually:

```python
from backend.utils.supabase_client import test_connection
import asyncio

result = asyncio.run(test_connection())
print(f"Connection successful: {result}")
```

### Issue: Memory errors with large batches

**Solution:** Reduce `BATCH_SIZE` in `embed_ingredients.py`:
```python
BATCH_SIZE = 10  # Reduce from 20
```

Then rerun:
```bash
python backend/scripts/embed_ingredients.py
```

### Issue: Duplicate embeddings in database

**Solution:** Script uses upsert with `on_conflict='id'`, so rerunning is safe:
```bash
# Safe to rerun - updates existing records
python backend/scripts/embed_ingredients.py
```

---

## Performance Optimization

### Batch Size Tuning

For optimal performance based on API quotas:

| Scenario | BATCH_SIZE | Notes |
|----------|-----------|-------|
| Free tier / Testing | 5-10 | Conservative, few timeouts |
| Standard ($5+/month) | 15-20 | Balanced throughput |
| Professional ($20+/month) | 25-50 | Maximize throughput |

### Query Optimization

```python
# Good: Specific queries
await search_similar_ingredients("chlorine byproducts toxic dioxin")

# Less effective: Generic queries
await search_similar_ingredients("chemicals")

# Best: Combined with risk filter
await search_similar_ingredients(
    "synthetic fibers",
    limit=5,
    risk_level_filter="High"
)
```

### Caching Search Results

For frequently accessed searches:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def cached_search(query: str, limit: int = 5):
    return await search_similar_ingredients(query, limit)
```

---

## Database Maintenance

### Monitoring Embedding Status

```sql
-- Check total ingredients
SELECT COUNT(*) as total_ingredients FROM ingredients_library;

-- Check for null embeddings
SELECT COUNT(*) as missing_embeddings 
FROM ingredients_library 
WHERE embedding IS NULL;

-- List all ingredients by risk level
SELECT risk_level, COUNT(*) as count 
FROM ingredients_library 
GROUP BY risk_level;
```

### Updating Embeddings

To refresh embeddings (e.g., after updating descriptions):

```bash
# Delete existing embeddings
# Then rerun embedding script
python backend/scripts/embed_ingredients.py
```

### Backup and Recovery

```bash
# Export ingredients data
pg_dump -h your-db-host -U postgres -d your-db -t ingredients_library > backup.sql

# Restore from backup
psql -h your-db-host -U postgres -d your-db < backup.sql
```

---

## Next Steps: Phase 3 Integration

The vector search utilities are ready for Phase 3 scan pipeline implementation:

1. **Ingredient Matching:** Use `search_similar_ingredients()` to match detected ingredients
2. **Risk Assessment:** Compare `risk_level` field to generate health scores
3. **Ingredient Analysis:** Display search results with similarity confidence

Example Phase 3 usage:
```python
from backend.utils.vector_search import search_similar_ingredients

async def analyze_scan_ingredients(detected_ingredients: List[str]):
    """Match detected ingredients to known database"""
    matches = []
    for ingredient_text in detected_ingredients:
        results = await search_similar_ingredients(
            query=ingredient_text,
            limit=1  # Get best match
        )
        if results:
            matches.append(results[0])
    return matches
```

---

## Support & Resources

- **OpenAI Embeddings Docs:** https://platform.openai.com/docs/guides/embeddings
- **Supabase Vector Search:** https://supabase.com/docs/guides/ai
- **Cosine Similarity:** https://en.wikipedia.org/wiki/Cosine_similarity
- **Project Issues:** Check `/backend/TODO.md` for known issues

---

**Last Updated:** 2026-01-31
**Phase:** Phase 2 - Data Ingestion & Embedding Pipeline
**Status:** Complete and ready for Phase 3 integration
