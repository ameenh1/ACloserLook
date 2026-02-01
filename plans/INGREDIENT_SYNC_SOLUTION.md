# Ingredient Sync Issue - Solution Guide

## Problem

You have **45 ingredients in Supabase** but `ingredients.json` shows fewer. The 15 new ingredients you added to Supabase:
- ❌ Are NOT in `backend/data/ingredients.json`
- ❌ May be missing embeddings
- ❌ Won't work with vector search until they have embeddings

## Root Cause

**Two separate data sources:**
1. **ingredients.json** - Local file used by `embed_ingredients.py`
2. **Supabase ingredients_library table** - Database used by your app

When you manually add ingredients to Supabase, they bypass the JSON file and don't get embeddings automatically.

## Solution: Sync Script

I've created [`backend/scripts/sync_ingredients_from_supabase.py`](../backend/scripts/sync_ingredients_from_supabase.py) that:

1. ✅ Fetches ALL 45 ingredients from Supabase
2. ✅ Checks which ones are missing embeddings
3. ✅ Generates embeddings for any missing ones
4. ✅ Updates `ingredients.json` to match Supabase (source of truth)
5. ✅ Creates export file for manual review

---

## How to Run

### Step 1: Run the Sync Script

```bash
cd backend
python scripts/sync_ingredients_from_supabase.py
```

### Expected Output:

```
======================================================================
INGREDIENT SYNC PROCESS STARTED
======================================================================
Fetching all ingredients from Supabase...
Found 45 ingredients in Supabase
Loading local ingredients.json from backend/data/ingredients.json
Found 30 ingredients in local JSON
Checking for ingredients with missing embeddings...
Found 15 ingredients without embeddings

Generating embedding 1/15: New Ingredient Name
✅ Updated embedding for 'New Ingredient Name'
...
✅ Generated 15 new embeddings

Re-fetching ingredients with updated embeddings...
Found 45 ingredients in Supabase
✅ Saved 45 ingredients to backend/data/ingredients.json

======================================================================
INGREDIENT SYNC COMPLETED
Total ingredients in Supabase: 45
Embeddings generated: 15
Local JSON updated: backend/data/ingredients.json
======================================================================
✅ All ingredients have embeddings!

Exporting ingredients for manual review...
✅ Exported to backend/data/ingredients_supabase_export.json
Supabase has 45 ingredients
Local JSON has 45 ingredients
```

---

## What This Script Does

### 1. Fetches from Supabase (Source of Truth)

```python
# Queries Supabase for ALL ingredients
SELECT id, name, description, risk_level, embedding, created_at
FROM ingredients_library
ORDER BY id
```

### 2. Identifies Missing Embeddings

```python
# Checks each ingredient
for ingredient in supabase_ingredients:
    if not ingredient.get('embedding'):
        # This ingredient needs an embedding!
        missing_embeddings.append(ingredient)
```

### 3. Generates Missing Embeddings

```python
# For each ingredient without embedding:
text = f"{ingredient.name}: {ingredient.description}"
embedding = OpenAI.embeddings.create(input=text, model="text-embedding-3-small")

# Updates Supabase
UPDATE ingredients_library 
SET embedding = <vector>
WHERE id = <ingredient_id>
```

### 4. Updates Local JSON

```python
# Overwrites ingredients.json with Supabase data
{
  "ingredients": [
    {
      "id": 1,
      "name": "Fragrance",
      "description": "...",
      "risk_level": "High"
    },
    # ... all 45 ingredients
  ]
}
```

---

## After Running the Script

### Verify Everything Works

**1. Check ingredients.json was updated:**
```bash
# Should now show 45 ingredients
wc -l backend/data/ingredients.json
```

**2. Check the export file:**
```bash
cat backend/data/ingredients_supabase_export.json
```

This shows:
- How many ingredients are in Supabase
- How many are in local JSON
- Which ones have embeddings

**3. Test vector search:**
```python
# Test that embeddings work
from utils.vector_search import search_similar_ingredients

results = await search_similar_ingredients("fragrance", limit=5)
print(f"Found {len(results)} similar ingredients")
```

**4. Test risk assessment:**
```bash
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{"barcode": "012345678901", "user_id": "test_user"}'
```

Should now include your new ingredients in the vector search results.

---

## Best Practices Going Forward

### Option 1: Supabase as Source of Truth (Recommended)

**Workflow:**
1. Add new ingredients directly to Supabase (via SQL or admin interface)
2. Run `sync_ingredients_from_supabase.py` to generate embeddings and update JSON
3. Commit updated `ingredients.json` to git

**Pros:**
- Supabase is your live database (single source of truth)
- Script handles embedding generation automatically
- JSON stays in sync

**Setup:**
```bash
# Add to your deployment/update process
cd backend
python scripts/sync_ingredients_from_supabase.py
git add data/ingredients.json
git commit -m "Sync ingredients from Supabase"
git push
```

---

### Option 2: JSON as Source of Truth

**Workflow:**
1. Add new ingredients to `ingredients.json`
2. Run `embed_ingredients.py` to generate embeddings and upsert to Supabase
3. Commit changes

**Pros:**
- Version controlled ingredient data
- Easier to review changes in git diffs
- More traditional

**Cons:**
- Two-way sync can cause conflicts
- Manual additions to Supabase bypass JSON

---

## Recommended: Use Supabase as Source

Since you're already adding ingredients directly to Supabase, I recommend:

**Make this your standard workflow:**

```bash
# 1. Add ingredient to Supabase (manually or via SQL)
# Example SQL:
INSERT INTO ingredients_library (id, name, description, risk_level)
VALUES (46, 'New Ingredient', 'Description here', 'Medium');

# 2. Run sync script to generate embedding and update JSON
cd backend
python scripts/sync_ingredients_from_supabase.py

# 3. Verify
cat data/ingredients_supabase_export.json

# 4. Commit updated JSON
git add data/ingredients.json data/ingredients_supabase_export.json
git commit -m "Add new ingredient: New Ingredient"
```

---

## Troubleshooting

### Issue: "No ingredients found in Supabase"

**Fix:**
```python
# Check Supabase connection
from utils.supabase_client import get_supabase_client
supabase = get_supabase_client()
response = supabase.table('ingredients_library').select('count').execute()
print(response.data)
```

### Issue: "OpenAI API error"

**Fix:**
```bash
# Check API key is set
echo $OPENAI_API_KEY
# or in Python
import os
print(os.getenv('OPENAI_API_KEY'))
```

### Issue: "Some ingredients still missing embeddings"

**Reasons:**
- Empty description (can't generate meaningful embedding)
- API rate limit hit (script stops early)
- Network error during generation

**Fix:**
```bash
# Run script again - it will only process missing ones
python scripts/sync_ingredients_from_supabase.py
```

### Issue: "ingredients.json not updating"

**Fix:**
```bash
# Check file permissions
ls -la backend/data/ingredients.json

# Check path
python -c "from pathlib import Path; print(Path(__file__).parent.parent / 'data' / 'ingredients.json')"
```

---

## Quick Commands

```bash
# Run sync
cd backend && python scripts/sync_ingredients_from_supabase.py

# Check count in Supabase
python -c "from utils.supabase_client import get_supabase_client; s = get_supabase_client(); print(len(s.table('ingredients_library').select('id').execute().data))"

# Check count in JSON
python -c "import json; print(len(json.load(open('backend/data/ingredients.json'))['ingredients']))"

# View export
cat backend/data/ingredients_supabase_export.json | python -m json.tool
```

---

## Summary

**Problem:** Mismatch between Supabase (45 ingredients) and JSON (30 ingredients)

**Solution:** Run [`sync_ingredients_from_supabase.py`](../backend/scripts/sync_ingredients_from_supabase.py)

**Result:**
- ✅ All 45 ingredients have embeddings
- ✅ `ingredients.json` updated to match Supabase
- ✅ Vector search works for all ingredients
- ✅ Risk assessment can use all ingredients

**Going Forward:** Add ingredients to Supabase → Run sync script → Commit JSON

---

**Created:** 2026-02-01  
**Status:** Ready to run
