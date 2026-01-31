# Lotus Backend - Testing Suite Documentation

Comprehensive testing framework for the Lotus backend with 40+ tests covering unit, integration, end-to-end, and performance scenarios.

## Overview

The test suite ensures backend reliability, correctness, and performance with:
- **Unit Tests**: OpenAI API integration, batch processing, error handling
- **Integration Tests**: Vector search, cosine similarity, filtering, edge cases
- **End-to-End Tests**: Complete scan pipeline (OCR → Vector Search → LLM → Risk Score)
- **API Tests**: All endpoints with valid/invalid inputs, error responses, validation
- **Performance Tests**: Latency benchmarks, throughput, concurrent load, memory profiling

**Target Coverage**: >80% for core modules  
**Performance Targets**:
- Vector search: <50ms for 10 results
- Profile lookup: <10ms
- Complete scan pipeline: <5s
- Load test: 100 concurrent requests

## Quick Start

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run entire test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest backend/tests/test_embeddings.py -v

# Integration tests only
pytest backend/tests/test_vector_search.py -v

# End-to-end tests only
pytest backend/tests/test_scan_pipeline.py -v

# API tests only
pytest backend/tests/test_api_endpoints.py -v

# Performance tests only
pytest backend/tests/test_performance.py -v -m performance

# Slow tests
pytest -m slow -v
```

### Run with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"
```

## Test Structure

### File Organization

```
backend/tests/
├── __init__.py
├── conftest.py                      # Pytest configuration & fixtures
├── test_embeddings.py              # Unit tests (18 tests)
├── test_vector_search.py           # Integration tests (20 tests)
├── test_scan_pipeline.py           # End-to-end tests (18 tests)
├── test_api_endpoints.py           # API tests (26 tests)
├── test_performance.py             # Performance tests (15 tests)
├── fixtures/
│   ├── __init__.py
│   └── sample_image.py             # Mock image generation utilities
└── README.md                        # This file
```

## Fixtures (conftest.py)

### Pytest Configuration

```python
@pytest.fixture
def async_client():
    """FastAPI TestClient for integration tests"""
```

### Mocked External Dependencies

#### Supabase Client
```python
@pytest.fixture
def mock_supabase_client():
    """Mocked Supabase client for all database operations"""

@pytest.fixture
def patch_supabase_client(mock_supabase_client):
    """Patch get_supabase_client across entire codebase"""

@pytest.fixture
def supabase_with_profiles(mock_supabase_client):
    """Mocked Supabase with sample profile data"""

@pytest.fixture
def supabase_with_ingredients(mock_supabase_client):
    """Mocked Supabase with ingredient library"""
```

#### OpenAI API
```python
@pytest.fixture
def patch_openai_embeddings(mock_openai_embedding):
    """Patch OpenAI embeddings API"""

@pytest.fixture
def patch_openai_vision(mock_openai_vision_response):
    """Patch OpenAI vision API for OCR"""

@pytest.fixture
def patch_openai_chat(mock_openai_chat_response):
    """Patch OpenAI chat API for risk assessment"""

@pytest.fixture
def patch_all_openai(...):
    """Patch all OpenAI APIs simultaneously"""
```

### Test Data Fixtures

```python
@pytest.fixture
def test_user_profile():
    """Sample user profile with sensitivities"""

@pytest.fixture
def test_ingredients_data():
    """Sample ingredient data (5 ingredients)"""

@pytest.fixture
def test_scan_result():
    """Sample scan result with all required fields"""

@pytest.fixture
def test_image_file():
    """Mock JPEG image (1x1 pixel)"""

@pytest.fixture
def test_image_png():
    """Mock PNG image (1x1 pixel)"""
```

## Test Suites

### 1. test_embeddings.py (18 tests)

**Purpose**: Unit tests for OpenAI embedding generation  
**Coverage**: text-embedding-3-small API, batch processing, error handling, validation

#### Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestEmbeddingGeneration` | 6 | Basic embedding generation, dimension validation, unicode handling |
| `TestBatchEmbeddings` | 4 | Batch processing, deduplication, size limits |
| `TestErrorHandling` | 4 | Invalid API key, timeout, rate limiting, server errors |
| `TestEmbeddingConsistency` | 3 | Consistency verification, different texts produce different embeddings |
| `TestEmbeddingModel` | 1 | Verify correct model is used |
| `TestEmbeddingPerformance` | 2 | Latency validation, performance characteristics |

#### Key Tests

```python
# Test embedding dimension
assert len(embedding) == 1536

# Test batch processing
embeddings = [generate_embedding(text) for text in texts]

# Test error handling
with pytest.raises(APIError):
    client.embeddings.create(input="test", model="text-embedding-3-small")
```

**Running**: `pytest backend/tests/test_embeddings.py -v`

---

### 2. test_vector_search.py (20 tests)

**Purpose**: Integration tests for vector search functionality  
**Coverage**: Search algorithm, similarity computation, filtering, edge cases, performance

#### Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestVectorSearchBasics` | 4 | Basic search, ranking by similarity, limit parameter |
| `TestCosineSimilarity` | 5 | Cosine similarity edge cases (identical, orthogonal, opposite) |
| `TestSearchFiltering` | 4 | Risk level filtering (High, Medium, Low) |
| `TestEdgeCases` | 5 | Empty query, no results, long query, invalid parameters |
| `TestPerformanceWithLargeDataset` | 2 | Search with 100+ and 1000+ ingredients |
| `TestVectorSearchIntegration` | 1 | Integration with risk scorer |
| `TestSearchFallback` | 1 | Fallback search mechanism when RPC unavailable |

#### Key Tests

```python
# Test ranking
assert results[0]["similarity_score"] > results[1]["similarity_score"]

# Test filtering by risk level
filtered = [r for r in results if r["risk_level"] == "High"]

# Test cosine similarity
similarity = dot_product / (mag1 * mag2)
assert similarity <= 1.0
```

**Running**: `pytest backend/tests/test_vector_search.py -v`

---

### 3. test_scan_pipeline.py (18 tests)

**Purpose**: End-to-end tests for complete scan pipeline  
**Coverage**: Full flow (image → OCR → search → LLM → risk), personalization, all risk levels

#### Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestScanPipelineFlow` | 3 | Low/Caution/High risk products |
| `TestOCRStep` | 3 | OCR extraction, invalid image handling, blank images |
| `TestVectorSearchStep` | 2 | Vector search for each ingredient, deduplication |
| `TestPersonalizationStep` | 3 | PCOS sensitivity, multiple sensitivities, no sensitivities |
| `TestLLMAssessmentStep` | 2 | Valid responses, error handling |
| `TestRiskClassification` | 4 | Low/Caution/High classification, normalization |
| `TestErrorHandling` | 5 | Missing user, invalid image, empty OCR, vector search failure |
| `TestScanResultFormat` | 4 | Required fields, UUID validation, ISO8601 timestamp |
| `TestPipelineIntegration` | 2 | Data flow through stages, component integration |

#### Key Tests

```python
# Test complete pipeline
ingredients = mock_ocr(image)
sensitivities = mock_fetch_sensitivities(user_id)
assessment = mock_llm(ingredients, sensitivities, vector_data)
assert assessment["overall_risk_level"] in ["Low Risk", "Caution", "High Risk"]

# Test result format
assert all(field in scan_result for field in required_fields)
```

**Running**: `pytest backend/tests/test_scan_pipeline.py -v`

---

### 4. test_api_endpoints.py (26 tests)

**Purpose**: API endpoint tests for all routes  
**Coverage**: Valid/invalid inputs, error responses, validation, all endpoints

#### Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestScanEndpoint` | 8 | POST /api/scan with various inputs, validations, file handling |
| `TestProfileEndpoints` | 7 | POST/GET /api/profiles, profile creation/retrieval, 404s |
| `TestIngredientsEndpoints` | 8 | GET /api/ingredients, pagination, filtering, ingredient details |
| `TestHealthEndpoint` | 2 | Health check endpoints |
| `TestErrorResponses` | 3 | 400/404/422 response formats |
| `TestInputValidation` | 2 | Whitespace trimming, type validation, pagination boundaries |

#### Key Tests

```python
# Test POST /api/scan
response = client.post("/api/scan?user_id=test", files={"file": (name, data, type)})
assert response.status_code == 200

# Test GET /api/profiles/{user_id}
response = client.get("/api/profiles/user_123")
assert response.status_code in [200, 404]

# Test error handling
response = client.post("/api/scan")  # Missing user_id
assert response.status_code == 422
```

#### Endpoints Tested

| Endpoint | Method | Tests |
|----------|--------|-------|
| `/api/scan` | POST | Valid image, missing user_id, invalid file type, oversized file, empty file |
| `/api/profiles` | POST | Create profile, missing fields, empty sensitivities, duplicates |
| `/api/profiles/{user_id}` | GET | Valid retrieval, not found, empty user_id |
| `/api/ingredients` | GET | Pagination, filtering by risk level, invalid parameters |
| `/api/ingredients/{ingredient_id}` | GET | Valid retrieval, not found, invalid ID |
| `/health` | GET | Health check response format |
| `/api/scan/health` | GET | Scan service health check |

**Running**: `pytest backend/tests/test_api_endpoints.py -v`

---

### 5. test_performance.py (15 tests)

**Purpose**: Performance benchmarks and load tests  
**Coverage**: Latency targets, throughput, concurrent requests, memory usage

#### Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestVectorSearchLatency` | 2 | Search <50ms, percentile benchmarks |
| `TestProfileLookupLatency` | 1 | Profile lookup <10ms |
| `TestScanPipelineLatency` | 1 | Complete pipeline <5s |
| `TestEmbeddingGenerationLatency` | 2 | Single embedding, batch throughput |
| `TestConcurrentRequests` | 2 | 100 concurrent scans, concurrent profile operations |
| `TestMemoryUsage` | 2 | Memory limits, no memory leaks |
| `TestLatencyPercentiles` | 2 | p50/p95/p99 percentile benchmarks |
| `TestThroughput` | 1 | Requests per second measurement |
| `TestResponseTimeDistribution` | 1 | Response time distribution analysis |

#### Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| Vector search latency (p50) | <30ms | `test_search_latency_percentiles` |
| Vector search latency (p95) | <100ms | `test_search_latency_percentiles` |
| Vector search latency (p99) | <150ms | `test_search_latency_percentiles` |
| Profile lookup | <10ms | `test_profile_lookup_under_10ms` |
| Scan pipeline | <5s | `test_scan_pipeline_under_5_seconds` |
| Single embedding | <1s | `test_single_embedding_latency` |
| Batch throughput | >10/sec | `test_batch_embedding_throughput` |
| Concurrent requests | 100 successful | `test_100_concurrent_scan_requests` |
| Memory usage | <500MB | `test_memory_usage_with_large_dataset` |
| Memory leak | <50MB growth | `test_memory_leak_with_repeated_operations` |

#### Key Tests

```python
# Test latency target
start = time.time()
result = search_similar_ingredients(query, limit=10)
elapsed = time.time() - start
assert elapsed < 0.050  # 50ms

# Test percentiles
p95 = sorted_latencies[int(len(latencies) * 0.95)]
assert p95 < 0.100  # p95 < 100ms

# Test concurrent load
tasks = [simulate_scan(i) for i in range(100)]
await asyncio.gather(*tasks)
assert success_count == 100
```

**Running**: 
```bash
# All performance tests
pytest backend/tests/test_performance.py -v -m performance

# Slow performance tests only
pytest backend/tests/test_performance.py -v -m slow
```

---

## Mocking Strategy

### Supabase Mocking

All database operations are mocked to avoid real Supabase calls:

```python
# In conftest.py
@pytest.fixture
def patch_supabase_client(mock_supabase_client):
    with patch('utils.supabase_client.get_supabase_client', 
               return_value=mock_supabase_client):
        with patch('routers.profiles.get_supabase_client',
                   return_value=mock_supabase_client):
            yield mock_supabase_client

# Usage in tests
def test_profile_retrieval(patch_supabase_client):
    response = client.get("/api/profiles/user_123")
    assert response.status_code == 200
```

### OpenAI API Mocking

Vision and chat API calls are mocked to avoid costs:

```python
# Mock OCR response
@pytest.fixture
def mock_openai_vision_response():
    mock = MagicMock()
    mock.content = [MagicMock(text='["Fragrance", "Rayon"]')]
    return mock

# Mock LLM response
@pytest.fixture
def mock_openai_chat_response():
    response_data = {
        "overall_risk_level": "Caution (Irritating)",
        "explanation": "Assessment here",
        "ingredient_details": []
    }
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(response_data))]
    return mock
```

### Benefits of Mocking

✅ **No API Costs**: Avoid OpenAI and Supabase charges  
✅ **Fast Execution**: Mock operations are instant  
✅ **Deterministic**: Same results every test run  
✅ **Isolated**: Tests don't depend on external services  
✅ **CI/CD Ready**: No credentials needed in pipeline  

---

## Coverage Metrics

### Generate Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### Coverage Targets by Module

| Module | Target | Status |
|--------|--------|--------|
| `utils/vector_search.py` | 85% | ✓ |
| `utils/ocr.py` | 80% | ✓ |
| `utils/risk_scorer.py` | 85% | ✓ |
| `routers/scan.py` | 90% | ✓ |
| `routers/profiles.py` | 85% | ✓ |
| `routers/ingredients.py` | 80% | ✓ |
| **Overall** | **>80%** | ✓ |

---

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Local CI/CD Simulation

```bash
# Run full test suite with coverage
cd backend
pytest --cov=. --cov-report=html --cov-report=term

# Run only fast tests
pytest -v -m "not slow"

# Run tests matching pattern
pytest -v -k "test_scan"
```

---

## Performance Benchmark Interpretation

### Understanding Percentiles

- **p50 (Median)**: 50% of requests faster than this
- **p95**: 95% of requests faster than this (95th percentile)
- **p99**: 99% of requests faster than this (99th percentile)

### Example Interpretation

```
Search Latency Benchmark:
- p50: 25ms   → Half of searches complete in 25ms or less
- p95: 75ms   → 95% of searches complete in 75ms or less
- p99: 120ms  → 99% of searches complete in 120ms or less
```

### Acceptable Thresholds

| Component | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| Vector Search | 30ms | 100ms | 150ms |
| Profile Lookup | 5ms | 15ms | 25ms |
| API Endpoint | 200ms | 500ms | 1000ms |

---

## Debugging Failed Tests

### Common Issues

#### 1. Mock Not Patching Correctly

```python
# ❌ Wrong - patches wrong import
with patch('openai.OpenAI'):
    ...

# ✓ Correct - patches where it's used
with patch('utils.ocr.OpenAI'):
    ...
```

#### 2. Async Test Failures

```python
# ❌ Missing marker
def test_async_function():
    result = await async_function()

# ✓ Correct - use pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
```

#### 3. Fixture Not Provided

```python
# ❌ Fixture not in function signature
def test_with_client():
    response = client.get("/health")

# ✓ Correct - add fixture parameter
def test_with_client(async_client):
    response = async_client.get("/health")
```

### Debug Techniques

```bash
# Print debug output during test
pytest -v -s backend/tests/test_file.py::test_function

# Run single test with full traceback
pytest -vv backend/tests/test_file.py::test_function

# Run with logging
pytest -v --log-cli-level=DEBUG

# Stop at first failure
pytest -x

# Drop into debugger on failure
pytest --pdb
```

---

## Test Data

### Sample Ingredients

```python
test_ingredients_data = [
    IngredientData(
        id=1,
        name="Fragrance",
        risk_level="High",
        related_ingredients=["Phthalates", "BPA"]
    ),
    IngredientData(
        id=3,
        name="Cotton",
        risk_level="Low",
        related_ingredients=[]
    )
]
```

### Sample User Profile

```python
test_user_profile = UserProfile(
    user_id="test_user_123",
    sensitivities=["PCOS", "Sensitive Skin"],
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

### Sample Images

See `backend/tests/fixtures/sample_image.py` for:
- Minimal JPEG/PNG images
- Images with text overlay
- Product label images
- Invalid/corrupted images
- Batch image generation

---

## Best Practices

### Writing Tests

✅ **Clear Naming**: `test_scan_with_valid_image_returns_200`  
✅ **Focused Scope**: One assertion per test ideally  
✅ **Arrange-Act-Assert**: Setup → Execute → Verify  
✅ **Mocking External**: Always mock API calls  
✅ **Error Cases**: Test both success and failure paths  

```python
# ✓ Good test structure
@pytest.mark.asyncio
async def test_vector_search_returns_ranked_results():
    # Arrange
    mock_results = [
        {"id": 1, "similarity": 0.95},
        {"id": 2, "similarity": 0.85}
    ]
    
    # Act
    results = await search_similar_ingredients("query")
    
    # Assert
    assert results[0]["similarity"] > results[1]["similarity"]
```

### Fixture Usage

✅ Use existing fixtures from `conftest.py`  
✅ Create focused fixtures for specific needs  
✅ Use fixture scope appropriately (function/session)  
✅ Clean up resources in teardown  

---

## Continuous Improvement

### Monitoring Test Health

```bash
# Run tests regularly
pytest --tb=short  # Short traceback for CI

# Track coverage over time
pytest --cov=. --cov-report=term-missing

# Performance regression detection
pytest backend/tests/test_performance.py -v
```

### Adding New Tests

When adding features, add tests:
1. **Unit Tests** for individual functions
2. **Integration Tests** for component interactions
3. **API Tests** for endpoint validation
4. **Performance Tests** if latency-sensitive

---

## Support & Troubleshooting

### Common Commands

```bash
# Full test suite
pytest

# Verbose with output
pytest -vv -s

# Specific file
pytest backend/tests/test_embeddings.py

# Specific test
pytest backend/tests/test_embeddings.py::TestEmbeddingGeneration::test_generate_valid_embedding

# All tests matching pattern
pytest -k "embedding"

# With coverage
pytest --cov=. --cov-report=html

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

---

## Test Statistics

- **Total Tests**: 40+
- **Unit Tests**: 18
- **Integration Tests**: 20
- **End-to-End Tests**: 18
- **API Tests**: 26
- **Performance Tests**: 15
- **Target Coverage**: >80%
- **Est. Runtime**: <30 seconds (fast suite), <2 minutes (with slow tests)

---

**Last Updated**: 2026-01-31  
**Version**: 1.0.0
