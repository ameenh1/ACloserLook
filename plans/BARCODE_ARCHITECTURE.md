# Barcode-Based Product Identification Architecture

## Overview
The system has been refactored to use barcode-based product identification instead of OCR on product images. This improves speed, reliability, and user experience.

---

## Architecture

### Frontend Flow
1. User opens [`BarcodeScannerScreen`](frontend/src/components/BarcodeScannerScreen.tsx)
2. Barcode scanner uses `Html5Qrcode` library to detect barcode
3. On successful scan, barcode string is passed to `onScanSuccess()`
4. App navigates to [`ProductResultScreen`](frontend/src/components/ProductResultScreen.tsx) with barcode
5. ProductResultScreen calls backend API to lookup product

### Backend Flow
1. Frontend sends POST request to `/api/scan/barcode`
2. [`scan.py`](backend/routers/scan.py) routes to `scan_barcode()` endpoint
3. [`barcode_lookup.py`](backend/utils/barcode_lookup.py) queries `products` table by barcode
4. Database returns product data with ingredient IDs
5. Ingredient IDs are resolved to names from `ingredients_library` table
6. Response returned to frontend with full product details

---

## API Endpoints

### 1. Barcode Lookup (Simple)
**Endpoint:** `POST /api/scan/barcode`

**Request:**
```json
{
  "barcode": "012345678901",
  "user_id": null
}
```

**Response (Success - 200):**
```json
{
  "found": true,
  "product": {
    "id": 1,
    "brand_name": "Pure Care",
    "barcode": "012345678901",
    "ingredients": ["Organic Cotton", "Viscose"],
    "product_type": "tampon",
    "coverage_score": 0.85,
    "research_count": 12
  }
}
```

**Response (Not Found - 404):**
```json
{
  "detail": "Product not found for barcode: 012345678901"
}
```

---

### 2. Barcode Lookup with Risk Assessment
**Endpoint:** `POST /api/scan/barcode/assess`

**Request:**
```json
{
  "barcode": "012345678901",
  "user_id": "user_123"
}
```

**Response (Success - 200):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "product": {
    "id": 1,
    "brand_name": "Pure Care",
    "barcode": "012345678901",
    "ingredients": ["Organic Cotton", "Viscose"],
    "product_type": "tampon",
    "coverage_score": 0.85,
    "research_count": 12
  },
  "overall_risk_level": "Low Risk",
  "risky_ingredients": [],
  "explanation": "This product is made with safe, natural materials.",
  "timestamp": "2026-01-31T22:55:00Z"
}
```

---

## Database Schema

### Products Table
```
id (integer, PK)
brand_name (text)
barcode (text, indexed) ← LOOKUP KEY
ingredients (integer[]) ← IDs referencing ingredients_library
product_type (text)
coverage_score (float)
research_count (integer)
created_at (timestamp)
updated_at (timestamp)
status (text)
```

### Ingredients Library Table
```
id (integer, PK)
name (text)
description (text)
risk_level (text)
embedding (vector(1536))
created_at (timestamp)
```

---

## Implementation Files

### Backend
- **Router:** [`backend/routers/scan.py`](backend/routers/scan.py) - Two endpoints for barcode scanning
- **Utility:** [`backend/utils/barcode_lookup.py`](backend/utils/barcode_lookup.py) - Database queries and ingredient resolution
- **Risk Scorer:** [`backend/utils/risk_scorer.py`](backend/utils/risk_scorer.py) - New `generate_risk_score_for_product()` function
- **Schemas:** [`backend/models/schemas.py`](backend/models/schemas.py) - New Pydantic models:
  - `BarcodeProduct` - Product details
  - `BarcodeLookupRequest` - Request body
  - `BarcodeLookupResponse` - Response body

### Frontend
- **Component:** [`frontend/src/components/ProductResultScreen.tsx`](frontend/src/components/ProductResultScreen.tsx) - Updated to:
  - Fetch product data from `/api/scan/barcode`
  - Display loading/error/success states
  - Show real product details from database

---

## Key Changes from Previous Implementation

### Removed
- ❌ OCR image upload endpoint
- ❌ Image file validation (JPEG, PNG, WebP size limits)
- ❌ `extract_ingredients_from_image()` function calls
- ❌ Product image as input

### Added
- ✅ Barcode string as input
- ✅ Direct database lookup (instant, no LLM call needed for basic lookup)
- ✅ Ingredient ID to name resolution
- ✅ Optional risk assessment endpoint (uses LLM + user sensitivities)

---

## Data Flow Diagram

```
┌─────────────────────────────────────┐
│  User scans barcode with phone      │
│  (BarcodeScannerScreen)             │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Html5Qrcode detects│
        │ barcode string     │
        └────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ ProductResultScreen        │
    │ POST /api/scan/barcode     │
    │ {barcode: "..."}           │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Backend: scan.py                   │
    │ scan_barcode() endpoint            │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Backend: barcode_lookup.py         │
    │ lookup_product_by_barcode()        │
    │ 1. Query products table by barcode │
    │ 2. Resolve ingredient IDs → names  │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Database Query:                    │
    │ - products table WHERE barcode=?   │
    │ - ingredients_library WHERE id in []
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │ Response: ProductResultScreen  │
    │ displays product details       │
    │ - brand_name                   │
    │ - ingredients list             │
    │ - product_type                 │
    │ - research_count               │
    └────────────────────────────────┘
```

---

## Testing Checklist

- [ ] Create test product in Supabase with barcode
- [ ] Call `/api/scan/barcode` with valid barcode → should return 200 + product
- [ ] Call `/api/scan/barcode` with invalid barcode → should return 404
- [ ] Call `/api/scan/barcode` with empty barcode → should return 400
- [ ] Call `/api/scan/barcode/assess` with valid barcode + user_id → should return risk assessment
- [ ] Verify ingredient resolution (IDs → names) works correctly
- [ ] Test frontend loading/error/success states
- [ ] Test end-to-end: scan barcode → see product data displayed

---

## Future Enhancements

1. **Barcode Caching** - Cache lookup results for 1 hour
2. **Batch Lookup** - Support multiple barcodes in single request
3. **Barcode Validation** - Validate barcode format/check digit before lookup
4. **Product Suggestions** - If barcode not found, suggest similar products
5. **Barcode History** - Track which barcodes have been scanned by user

---

**Last Updated:** 2026-01-31
