# Database Optimization & Setup Guide

This guide covers Supabase PostgreSQL setup, migrations, RPC functions, and performance optimization strategies for Phase 5.

## Quick Start

### 1. Run Migrations in Supabase SQL Editor

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy and paste the contents of `migrations.sql`
6. Click **Run**

Expected output: All CREATE statements should complete without errors.

### 2. Deploy RPC Functions

1. In SQL Editor, click **New Query**
2. Copy and paste the contents of `functions.sql`
3. Click **Run**

Expected output: All function and grant statements execute successfully.

---

## Table Schema Documentation

### `profiles` Table
Stores user preferences and sensitivity data.

**Columns:**
- `id` (UUID): Primary key, auto-generated
- `user_id` (TEXT): Unique identifier from auth provider
- `sensitivities` (TEXT[]): Array of user sensitivity tags
- `created_at` (TIMESTAMP): Account creation time
- `updated_at` (TIMESTAMP): Last profile update

**Indexes:**
- `idx_profiles_user_id`: B-tree index on `user_id` for rapid lookups during authentication

**Query Pattern:**
```sql
SELECT * FROM profiles WHERE user_id = 'auth_user_123';
```

**Estimated Latency:** < 5ms with index

---

### `ingredients_library` Table
Master ingredient database with vector embeddings for semantic search.

**Columns:**
- `id` (SERIAL): Auto-incrementing primary key
- `name` (TEXT): Ingredient name (unique)
- `description` (TEXT): Ingredient details and warnings
- `risk_level` (TEXT): 'low', 'medium', or 'high'
- `embedding` (vector[1536]): OpenAI Ada embedding for similarity search
- `created_at` (TIMESTAMP): Record creation time

**Indexes:**
- `idx_ingredients_name`: B-tree on `name` for exact matches
- `idx_ingredients_risk_level`: B-tree on `risk_level` for filtering
- `idx_ingredients_embedding`: IVFFlat index with `vector_cosine_ops` for approximate nearest neighbor search

**Query Pattern (Vector Search):**
```sql
SELECT match_ingredients(
  query_embedding,
  match_threshold := 0.7,
  match_count := 10
);
```

**Estimated Latency:** 15-30ms for 10 nearest neighbors (with IVFFlat index)

---

### `scans` Table
Stores scan history for user analytics and risk tracking.

**Columns:**
- `id` (UUID): Primary key, auto-generated
- `user_id` (TEXT): Foreign key to `profiles.user_id`
- `overall_risk_level` (TEXT): 'low', 'medium', or 'high'
- `ingredients_found` (TEXT[]): Array of detected ingredient names
- `created_at` (TIMESTAMP): Scan timestamp

**Indexes:**
- `idx_scans_user_id`: B-tree on `user_id` for user history queries
- `idx_scans_created_at`: B-tree on `created_at DESC` for recent scan queries
- `idx_scans_user_created`: Composite index on `(user_id, created_at DESC)` for combined queries

**Foreign Key Constraint:**
- `user_id` references `profiles.user_id` with `ON DELETE CASCADE`

**Query Pattern:**
```sql
SELECT * FROM scans 
WHERE user_id = 'auth_user_123'
ORDER BY created_at DESC
LIMIT 50;
```

**Estimated Latency:** 8-15ms for 50 records with composite index

---

## RPC Functions

### `match_ingredients(query_embedding, match_threshold, match_count)`

Performs vector similarity search using cosine distance.

**Parameters:**
- `query_embedding` (vector[1536]): Query vector (typically from ingredient name embedding)
- `match_threshold` (float): Similarity cutoff [0.0-1.0], recommended 0.7+
- `match_count` (int): Number of results (default: 10)

**Returns:**
```
id (int) | name (text) | description (text) | risk_level (text) | similarity (float)
```

**Example Usage:**
```python
# In Python using Supabase client
result = supabase.rpc(
    'match_ingredients',
    {
        'query_embedding': query_vector,
        'match_threshold': 0.7,
        'match_count': 10
    }
).execute()
```

**Performance:** 15-30ms for 10 results (IVFFlat index)

---

### `get_user_scan_history(p_user_id, p_limit, p_offset)`

Retrieves scan history with pagination support.

**Parameters:**
- `p_user_id` (text): User identifier
- `p_limit` (int): Records per page (default: 50)
- `p_offset` (int): Pagination offset (default: 0)

**Returns:**
```
id (uuid) | overall_risk_level (text) | ingredients_found (text[]) | created_at (timestamp) | days_ago (int)
```

**Example Usage:**
```python
result = supabase.rpc(
    'get_user_scan_history',
    {
        'p_user_id': user_id,
        'p_limit': 50,
        'p_offset': 0
    }
).execute()
```

**Performance:** 8-12ms for 50 records (composite index)

---

### `record_scan(p_user_id, p_overall_risk_level, p_ingredients_found)`

Atomically records a scan and creates profile if needed.

**Parameters:**
- `p_user_id` (text): User identifier
- `p_overall_risk_level` (text): 'low', 'medium', or 'high'
- `p_ingredients_found` (text[]): Array of ingredient names

**Returns:**
```
scan_id (uuid) | success (boolean) | message (text)
```

**Performance:** 5-8ms (single insert with atomic profile creation)

---

### `get_risk_statistics(p_user_id)`

Generates risk statistics for user dashboard.

**Returns:**
```
total_scans (int) | high_risk_scans (int) | medium_risk_scans (int) | 
low_risk_scans (int) | last_scan_date (timestamp) | average_risk_level (text)
```

**Performance:** 20-30ms (aggregate query)

---

## Index Strategy

### Why These Indexes?

1. **`idx_profiles_user_id`** - B-tree index
   - Auth lookups are frequent
   - User ID is unique
   - Provides O(log n) lookup

2. **`idx_ingredients_name`** - B-tree index
   - Exact match searches on ingredient names
   - Used for manual lookups and filtering

3. **`idx_ingredients_risk_level`** - B-tree index
   - Filter results by risk category
   - Low cardinality (3 values: low, medium, high)

4. **`idx_ingredients_embedding`** - IVFFlat index with vector_cosine_ops
   - Approximate nearest neighbor search
   - 1536-dimensional vectors require specialized index
   - IVFFlat configured with `lists=100` for optimal performance/accuracy tradeoff
   - Lists parameter: higher = more accurate but slower; lower = faster but less accurate

5. **`idx_scans_user_id`** - B-tree index
   - Most common query: scans by user
   - Enables rapid filtering

6. **`idx_scans_created_at`** - B-tree DESC index
   - Get recent scans efficiently
   - DESC order matches common query pattern

7. **`idx_scans_user_created`** - Composite index
   - Optimizes combined queries: user + time range
   - Eliminates need for separate sorts

### Index Maintenance

Supabase automatically maintains indexes. Monitor index size in Supabase dashboard:
- Navigate to **Database** → **Indexes**
- Indexes should typically be 20-30% of table size
- IVFFlat index uses approximately 2-3x table data size

---

## Connection Pooling

### PgBouncer Configuration (Handled by Supabase)

Supabase provides connection pooling via PgBouncer:

**Session Mode (Default):**
- Each connection from client gets its own backend connection
- Better for most applications
- Slight overhead but simpler connection management

**Transaction Mode (Available):**
- Connection is bound only for the duration of a transaction
- Lower overhead for high-concurrency scenarios
- Requires careful management of prepared statements

### Pool Settings in Supabase

1. Go to **Project Settings** → **Database**
2. Under **Connection Pooling**, enable if not already enabled
3. Set pool mode to **Session** for standard API usage
4. Default pool size: 3-10 connections

### Python Connection Pooling (db_helpers.py)

The `db_helpers.py` utility provides:
- Async connection pool initialization
- Pooled connection retrieval with retry logic
- Health checks and performance benchmarking

```python
from backend.utils.db_helpers import setup_connection_pool, get_pooled_connection

# Initialize pool on app startup
await setup_connection_pool()

# Get connection for queries
async with get_pooled_connection() as conn:
    result = await conn.query("SELECT * FROM profiles WHERE user_id = ?")
```

**Recommended Pool Size:** 10-20 for typical production load

---

## Performance Targets

### Query Latency Goals

| Query Type | Index Used | Target Latency | Measurement |
|-----------|-----------|----------------|------------|
| Profile lookup | idx_profiles_user_id | < 5ms | Single row |
| Ingredient exact match | idx_ingredients_name | < 5ms | Single row |
| Vector search (10 results) | idx_ingredients_embedding | 15-30ms | IVFFlat |
| Scan history (50 rows) | idx_scans_user_created | 8-12ms | Multi-row |
| Risk statistics | composite | 20-30ms | Aggregate |

### Achieving Sub-100ms Production Latency

1. **Connection Pooling** (10-20 connections)
   - Eliminates connection overhead: ~5-10ms savings per query

2. **Index Strategy** (7 specialized indexes)
   - Optimized query plans: ~10-20ms savings per query

3. **RPC Functions** (server-side logic)
   - Eliminates client-server round trips: ~30-50ms savings

4. **Caching** (optional)
   - Cache ingredient library in memory for 1 hour
   - Cache user sensitivity preferences for 24 hours

---

## Performance Benchmarking Guide

### 1. Using Supabase Query Performance Tool

1. Navigate to **SQL Editor**
2. Run a query and click **Explain** to see query plan
3. Look for "Sequential Scan" (bad) vs "Index Scan" (good)
4. Analyze execution time in bottom panel

### 2. Benchmarking from Python

```python
import time
from backend.utils.db_helpers import test_connection_performance

# Run benchmark
stats = await test_connection_performance(
    query="SELECT * FROM profiles WHERE user_id = ?",
    params=["user_123"],
    iterations=100
)

print(f"Min latency: {stats['min_ms']:.2f}ms")
print(f"Max latency: {stats['max_ms']:.2f}ms")
print(f"Average: {stats['avg_ms']:.2f}ms")
print(f"P95: {stats['p95_ms']:.2f}ms")
```

### 3. Load Testing

Use Apache JMeter or `locust` to simulate concurrent users:

```python
# locustfile.py example
from locust import HttpUser, task

class ScanUser(HttpUser):
    @task
    def scan_image(self):
        self.client.post("/api/scan", json={...})
```

Run with: `locust -f locustfile.py --host=http://localhost:8000`

### 4. Monitoring in Production

- **Supabase Dashboard**: Real-time query statistics
- **Python logging**: Log slow queries (> 100ms)
- **APM tools**: New Relic, Datadog, or similar for tracing

---

## Troubleshooting

### Vector Search Returning No Results

**Problem:** `match_ingredients()` returns empty results

**Solution:**
1. Verify embeddings are populated: `SELECT COUNT(*) FROM ingredients_library WHERE embedding IS NOT NULL;`
2. Lower `match_threshold` from 0.7 to 0.5
3. Ensure query embedding uses same model (OpenAI Ada-002)

### High Query Latency

**Problem:** Queries exceed 100ms consistently

**Solution:**
1. Check index health: `SELECT * FROM pg_stat_user_indexes WHERE idx_blks_read > 10000;`
2. Run VACUUM: `VACUUM ANALYZE ingredients_library;` (through Supabase SQL editor)
3. Verify connection pool is configured
4. Check for table bloat: Compare table size to index size

### Connection Pool Exhaustion

**Problem:** "Connection pool exhausted" errors

**Solution:**
1. Increase pool size in Supabase settings
2. Reduce long-running queries
3. Use connection timeouts in Python client
4. Implement circuit breaker pattern

---

## Deployment Checklist

- [ ] Run `migrations.sql` in Supabase SQL Editor
- [ ] Run `functions.sql` in Supabase SQL Editor
- [ ] Verify tables with: `\dt` in SQL editor
- [ ] Verify functions with: `\df` in SQL editor
- [ ] Test vector search with sample query
- [ ] Enable Row Level Security (RLS) policies are enforced
- [ ] Configure `db_helpers.py` in Python application
- [ ] Update `supabase_client.py` with pooling initialization
- [ ] Run performance benchmark on all queries
- [ ] Monitor first 24 hours in Supabase dashboard
- [ ] Set up alerts for slow queries (> 100ms)

---

## Additional Resources

- [Supabase PostgreSQL Docs](https://supabase.com/docs/guides/database)
- [PgVector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes.html)
- [Query Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
