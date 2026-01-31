# Data Ingestion and Barcode Scan Flow Architecture

## Overview
This document explains how data is ingested into the ACloserLook application and the complete flow that occurs when a user scans a barcode.

---

## Table of Contents
1. [Data Ingestion Pipeline](#data-ingestion-pipeline)
2. [Barcode Scan Flow](#barcode-scan-flow)
3. [Risk Assessment Pipeline](#risk-assessment-pipeline)
4. [Next Steps and Improvements](#next-steps-and-improvements)

---

## Data Ingestion Pipeline

### 1. Ingredient Data Source
**Location:** [`backend/data/ingredients.json`](../backend/data/ingredients.json)

The application starts with a curated ingredient library containing:
- **id**: Unique identifier for each ingredient
- **name**: Ingredient name (e.g., "Fragrance", "Organic Cotton")
- **description**: Detailed health impact information
- **risk_level**: "Low", "Medium", or "High"

**Current Status:** 185 ingredients in the library

### 2. Embedding Generation Process
**Script:** [`backend/scripts/embed_ingredients.py`](../backend/scripts/embed_ingredients.py)

This script performs the following steps:

```
┌─────────────────────────────────────────────────────────────┐
│ EMBEDDING PIPELINE                                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ 1. Load ingredients.json         │
        │    Parse 185 ingredient records  │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │ 2. Generate Embeddings                   │
        │    For each ingredient:                  │
        │    - Combine name + description          │
        │    - Call OpenAI text-embedding-3-small  │
        │    - Returns 1536-dim vector             │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │ 3. Batch Upsert to Supabase              │
        │    - Insert into ingredients_library     │
        │    - 20 records per batch                │
        │    - On conflict: update existing        │
        └──────────────────────────────────────────┘
```

**Key Features:**
- Retry logic for rate limiting (3 attempts with exponential backoff)
- Batch processing (20 ingredients at a time)
- Error logging and recovery
- Progress tracking

**Database Table:** `ingredients_library`
```sql
CREATE TABLE ingredients_library (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    risk_level TEXT,
    embedding VECTOR(1536),  -- OpenAI embeddings for semantic search
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Product Data Ingestion
**Database Table:** `products`

Products are manually seeded using SQL scripts in [`backend/database/`](../backend/database/):
- `seed_test_product.sql`
- `seed_always_pads.sql`
- `add_new_ingredients_and_product.sql`

**Product Schema:**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    brand_name TEXT NOT NULL,
    barcode TEXT UNIQUE NOT NULL,        -- Lookup key
    ingredients INTEGER[],                -- Array of ingredient IDs
    product_type TEXT,                    -- e.g., "tampon", "pad"
    coverage_score FLOAT,                 -- Research coverage 0-1
    research_count INTEGER,               -- Number of studies
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Important:** Ingredients are stored as **integer arrays** (IDs), not names. This enables:
- Efficient storage
- Consistent data across products
- Easy updates to ingredient information

---

## Barcode Scan Flow

### Complete User Journey

```
┌────────────────────────────────────────────────────────────────┐
│                    USER SCANS BARCODE                          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: BarcodeScannerScreen.tsx                             │
│ - Uses Html5Qrcode library                                     │
│ - Camera access with environment-facing mode                   │
│ - Detects barcode automatically (UPC, EAN, Code128, etc.)      │
│ - Returns barcode string (e.g., "012345678901")                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: Navigation                                            │
│ - Calls onScanSuccess(barcode)                                 │
│ - Routes to ProductResultScreen with barcode prop              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: ProductResultScreen.tsx                              │
│ - Shows loading spinner                                         │
│ - Calls API: POST /api/scan/barcode                            │
│ - Body: { barcode: "012345678901", user_id: null }             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: main.py                                                │
│ - FastAPI receives request                                     │
│ - CORS middleware validates origin                             │
│ - Request logging middleware tracks request                    │
│ - Routes to scan.router                                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: routers/scan.py                                        │
│ - Endpoint: scan_barcode()                                     │
│ - Validates barcode is not empty                               │
│ - Calls lookup_product_by_barcode()                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: utils/barcode_lookup.py                               │
│                                                                 │
│ Step 1: Query products table                                   │
│   SELECT id, brand_name, barcode, ingredients,                 │
│          product_type, coverage_score, research_count          │
│   FROM products                                                │
│   WHERE barcode = '012345678901'                               │
│                                                                 │
│ Step 2: Resolve ingredient IDs to names                        │
│   SELECT id, name                                              │
│   FROM ingredients_library                                     │
│   WHERE id IN (ingredient_ids_array)                           │
│                                                                 │
│ Step 3: Map IDs to names in order                              │
│   [3, 7, 16] → ["Polyester", "Cottonseed Oil", "Organic..."]  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: Response Construction                                 │
│ {                                                              │
│   "found": true,                                               │
│   "product": {                                                 │
│     "id": 1,                                                   │
│     "brand_name": "Always Infinity Pads",                      │
│     "barcode": "012345678901",                                 │
│     "ingredients": ["Polyester", "Rayon", "Fragrance"],        │
│     "product_type": "pad",                                     │
│     "coverage_score": 0.75,                                    │
│     "research_count": 8                                        │
│   }                                                            │
│ }                                                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: ProductResultScreen Display                          │
│ - Hides loading spinner                                        │
│ - Shows product details:                                       │
│   • Brand name in large heading                                │
│   • Product type badge                                         │
│   • Research coverage percentage                               │
│   • List of all ingredients with checkmarks                    │
│   • Research-backed indicator                                  │
│ - "Scan Another Product" button                                │
└─────────────────────────────────────────────────────────────────┘
```

### Error Handling

**404 - Product Not Found:**
```json
{
  "detail": "Product not found for barcode: 012345678901"
}
```
- Frontend shows error message with red X icon
- Offers "Try Another Barcode" button

**400 - Invalid Barcode:**
```json
{
  "detail": "Barcode cannot be empty"
}
```

**500 - Server Error:**
```json
{
  "detail": "Failed to lookup barcode: Database connection error"
}
```

---

## Risk Assessment Pipeline

### When to Use Risk Assessment?

The application provides TWO endpoints:

1. **Simple Lookup** - `/api/scan/barcode` (Current frontend implementation)
   - Fast, no LLM calls
   - Returns product details only
   - No personalization

2. **Risk Assessment** - `/api/scan/barcode/assess` (Available but not used yet)
   - Personalized health analysis
   - Requires user_id
   - Uses LLM for risk scoring

### Risk Assessment Flow (Advanced)

```
┌─────────────────────────────────────────────────────────────────┐
│ POST /api/scan/barcode/assess                                  │
│ { barcode: "...", user_id: "user_123" }                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Lookup Product (same as simple scan)                   │
│ - Query products table by barcode                              │
│ - Resolve ingredient names                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Fetch User Sensitivities                               │
│ utils/risk_scorer.py → _fetch_user_sensitivities()             │
│                                                                 │
│ Query:                                                         │
│   SELECT sensitivities FROM profiles WHERE id = 'user_123'     │
│                                                                 │
│ Returns: ["PCOS", "Sensitive Skin", "BV"]                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Vector Search for Ingredient Research                  │
│ utils/vector_search.py → search_similar_ingredients()          │
│                                                                 │
│ For each ingredient in product:                                │
│   1. Generate query embedding (OpenAI text-embedding-3-small)  │
│   2. Vector similarity search in Supabase                      │
│   3. Call RPC: search_ingredients(query_embedding, limit=3)    │
│   4. Returns top 3 similar ingredients with descriptions       │
│                                                                 │
│ Deduplicates results and returns enriched context              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: LLM Risk Assessment                                    │
│ utils/risk_scorer.py → _generate_llm_assessment()              │
│                                                                 │
│ Constructs prompt with:                                        │
│   - Scanned ingredients list                                   │
│   - User sensitivities                                         │
│   - Retrieved research context from vector search              │
│                                                                 │
│ Calls: OpenAI GPT-4o-mini                                      │
│ System prompt: HEALTH_EXPERT_SYSTEM_PROMPT                     │
│                                                                 │
│ LLM analyzes and returns JSON:                                 │
│ {                                                              │
│   "overall_risk_level": "Caution (Irritating)",               │
│   "explanation": "This product contains fragrances...",        │
│   "ingredient_details": [                                      │
│     {                                                          │
│       "name": "Fragrance",                                     │
│       "risk_level": "High Risk",                               │
│       "reason": "May trigger allergic reactions..."            │
│     }                                                          │
│   ]                                                            │
│ }                                                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Format and Return Response                             │
│ - Normalize risk level ("Caution (Irritating)" → "Caution")   │
│ - Extract risky ingredients (Medium/High risk only)            │
│ - Add scan_id, timestamp                                       │
│                                                                 │
│ Response:                                                      │
│ {                                                              │
│   "scan_id": "uuid",                                           │
│   "user_id": "user_123",                                       │
│   "product": { ...product details... },                        │
│   "overall_risk_level": "Caution",                             │
│   "risky_ingredients": [                                       │
│     { "name": "Fragrance", "risk_level": "High Risk", ... }    │
│   ],                                                           │
│   "explanation": "Personalized 2-sentence assessment",         │
│   "timestamp": "2026-01-31T23:30:00Z"                          │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Vector Search Technology

**Purpose:** Semantic search to find ingredient research and context

**How it Works:**
1. Each ingredient in the library has a 1536-dimensional embedding vector
2. When searching, query text is converted to same embedding space
3. Cosine similarity finds closest matches
4. Returns most relevant ingredient information

**Supabase RPC Function:** `search_ingredients`
- Performs efficient vector similarity search
- Uses pgvector extension
- Threshold: 0.1 minimum similarity

**Fallback:** If RPC fails, Python calculates cosine similarity manually

---

## Next Steps and Improvements

### Current State
✅ **Implemented:**
- Ingredient library with 185 entries
- Embedding generation and vector storage
- Product database with barcode lookup
- Frontend barcode scanner (Html5Qrcode)
- Simple product lookup endpoint
- Advanced risk assessment endpoint (backend ready)
- Error handling and logging

### What Needs to Be Done Next

#### 1. **Expand Product Database**
**Priority:** HIGH
**Current Issue:** Only a few test products exist

**Actions:**
- Create data collection process for real products
- Build admin interface for product entry
- Implement bulk import from product databases (Open Food Facts, etc.)
- Add product images and metadata
- Validate barcode formats (UPC-A, EAN-13, etc.)

**Implementation:**
- Create admin dashboard in frontend
- Build product CRUD endpoints in backend
- Add product seeding scripts
- Consider OCR fallback for products without barcodes

#### 2. **Integrate Risk Assessment in Frontend**
**Priority:** MEDIUM
**Current Issue:** Frontend only uses simple lookup, not personalized assessment

**Actions:**
- Update [`ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx) to:
  - Check if user is logged in
  - Call `/api/scan/barcode/assess` instead of `/api/scan/barcode`
  - Display risk level with color coding (Low=green, Caution=yellow, High=red)
  - Show risky ingredients list with expandable details
  - Display personalized explanation
- Add user authentication system
- Create user profile management screen

**UI Components Needed:**
- Risk level indicator (badge/alert)
- Risky ingredients accordion
- Personalized explanation card
- "Why this matters to you" section

#### 3. **User Profile System**
**Priority:** MEDIUM
**Current Issue:** No user authentication or profiles implemented

**Actions:**
- Implement authentication (Supabase Auth or custom)
- Create profile creation flow
- Build sensitivity selection interface
- Store user_id in frontend state
- Pass user_id to all risk assessment calls

**Database:**
- `profiles` table already exists in schema
- Needs: id, sensitivities[], created_at, updated_at

#### 4. **Enhance Ingredient Library**
**Priority:** MEDIUM
**Current Issue:** 185 ingredients may not cover all products

**Actions:**
- Research common period product ingredients
- Add scientific citations to descriptions
- Link to PubMed research articles
- Categorize ingredients (synthetic, natural, etc.)
- Add ingredient aliases (e.g., "Sodium Polyacrylate" = "SAP")

**Tools Available:**
- [`backend/auto_populate/ingredient_matcher.py`](../backend/auto_populate/ingredient_matcher.py)
- [`backend/auto_populate/pubmed_enricher.py`](../backend/auto_populate/pubmed_enricher.py)

#### 5. **Product Not Found Handling**
**Priority:** MEDIUM
**Current Issue:** No graceful fallback for unknown barcodes

**Actions:**
- Allow users to manually enter product info
- Submit unknown barcodes to admin queue
- Suggest similar products
- Offer OCR fallback for ingredient lists
- Crowdsource product data

**Implementation:**
- Create product submission form
- Admin review queue
- OCR integration with [`utils/ocr.py`](../backend/utils/ocr.py)

#### 6. **Caching and Performance**
**Priority:** LOW
**Current Issue:** Every scan hits database and potentially LLM

**Actions:**
- Cache barcode lookups (1 hour TTL)
- Cache ingredient resolutions
- Cache risk assessments per user+product combination
- Pre-compute risk scores for common sensitivities
- Add Redis or in-memory cache

**Tools:**
- Redis for distributed caching
- FastAPI's dependency injection for cache layer

#### 7. **Analytics and Tracking**
**Priority:** LOW

**Actions:**
- Track which products are scanned most
- Identify gaps in product database
- Monitor API response times
- Track user scan patterns
- A/B test risk explanations

#### 8. **Mobile App Enhancement**
**Priority:** LOW

**Actions:**
- Improve barcode scanner performance
- Add haptic feedback on successful scan
- Enable offline mode (cached products)
- Add scan history
- Support batch scanning

---

## Technical Architecture Summary

### Tech Stack
- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **Backend:** FastAPI (Python) + Uvicorn
- **Database:** Supabase (PostgreSQL + pgvector)
- **AI/ML:** OpenAI (GPT-4o-mini for analysis, text-embedding-3-small for vectors)
- **Barcode Scanner:** Html5Qrcode library
- **Deployment:** Vercel (backend), TBD (frontend)

### Data Flow Summary
```
Ingredients.json → Embeddings → Supabase (ingredients_library)
                                      ↓
Products (manual entry) → Supabase (products table)
                                      ↓
Barcode Scan → API Lookup → Ingredient Resolution → Frontend Display
                   ↓ (optional)
            User Profile + Vector Search + LLM → Risk Assessment
```

### Key Files Reference
| Component | File | Purpose |
|-----------|------|---------|
| Ingredient Data | [`backend/data/ingredients.json`](../backend/data/ingredients.json) | Source of truth for ingredient library |
| Embedding Script | [`backend/scripts/embed_ingredients.py`](../backend/scripts/embed_ingredients.py) | Generates and stores embeddings |
| Barcode Lookup | [`backend/utils/barcode_lookup.py`](../backend/utils/barcode_lookup.py) | Queries products by barcode |
| Risk Scoring | [`backend/utils/risk_scorer.py`](../backend/utils/risk_scorer.py) | LLM-based risk assessment |
| Vector Search | [`backend/utils/vector_search.py`](../backend/utils/vector_search.py) | Semantic ingredient search |
| Scanner UI | [`frontend/src/components/BarcodeScannerScreen.tsx`](../frontend/src/components/BarcodeScannerScreen.tsx) | Camera-based barcode scanner |
| Results UI | [`frontend/src/components/ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx) | Product details display |
| API Routes | [`backend/routers/scan.py`](../backend/routers/scan.py) | Scan endpoints |
| Schemas | [`backend/models/schemas.py`](../backend/models/schemas.py) | Pydantic models |

---

## Diagrams

### System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         USER DEVICE                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Frontend (TypeScript + Vite)                      │   │
│  │  - BarcodeScannerScreen (Html5Qrcode)                    │   │
│  │  - ProductResultScreen                                   │   │
│  │  - Profile Management (future)                           │   │
│  └─────────────────────┬────────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERCEL (Backend Host)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python)                                │   │
│  │  ├─ /api/scan/barcode         (simple lookup)           │   │
│  │  ├─ /api/scan/barcode/assess  (risk assessment)         │   │
│  │  ├─ /api/profiles/*            (user management)        │   │
│  │  └─ /api/ingredients/*         (ingredient library)     │   │
│  └─────────────────────┬────────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Supabase   │  │    OpenAI    │  │   Sentry     │
│  PostgreSQL  │  │   API Keys   │  │  Error       │
│  + pgvector  │  │  - GPT-4o    │  │  Tracking    │
│              │  │  - Embeddings│  │              │
│  Tables:     │  └──────────────┘  └──────────────┘
│  - products  │
│  - ingredients│
│  - profiles  │
└──────────────┘
```

---

**Last Updated:** 2026-01-31  
**Author:** System Architect  
**Status:** Active Development
