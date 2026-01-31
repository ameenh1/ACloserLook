# Barcode Implementation Setup Guide

## Prerequisites
- Supabase project with `products` and `ingredients_library` tables
- Products table populated with barcode data
- Backend running with updated dependencies

---

## Step 1: Backend Setup

### 1.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Make sure these are included in `requirements.txt`:
- `fastapi`
- `uvicorn`
- `supabase` (supabase-py)
- `python-dotenv`
- `pydantic`
- `openai` (for optional risk assessment)

### 1.2 Environment Variables
Ensure `.env` has these configured:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_key (for /api/scan/barcode/assess)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 1.3 Start Backend Server
```bash
cd backend
python main.py
# Or with uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server should start at `http://localhost:8000`

---

## Step 2: Frontend Setup

### 2.1 Install Dependencies
```bash
cd frontend
npm install
```

### 2.2 Configure API URL
Update `frontend/vite.config.ts` or create `.env.local`:
```
VITE_API_URL=http://localhost:8000
```

Or ensure the fetch call in `ProductResultScreen.tsx` points to your backend:
```typescript
const response = await fetch(`${import.meta.env.VITE_API_URL}/api/scan/barcode`, {
```

### 2.3 Start Frontend Dev Server
```bash
npm run dev
# Frontend should run at http://localhost:5173 or http://localhost:3000
```

---

## Step 3: Database Setup

### 3.1 Verify Products Table Has Barcode Column
In Supabase SQL Editor, run:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;
```

Should show:
- `id` (integer)
- `brand_name` (text)
- `barcode` (text) ← Must exist
- `ingredients` (integer[])
- `product_type` (text)
- etc.

### 3.2 Create Index on Barcode Column
For performance, add index:
```sql
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
```

### 3.3 Seed Test Product
```sql
INSERT INTO products (brand_name, barcode, ingredients, product_type, coverage_score, research_count)
VALUES (
  'Test Brand',
  '012345678901',
  ARRAY[1, 2, 3],
  'tampon',
  0.85,
  12
);
```

---

## Step 4: Test Barcode Lookup

### 4.1 Test with cURL
```bash
curl -X POST http://localhost:8000/api/scan/barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode": "012345678901", "user_id": null}'
```

Expected response:
```json
{
  "found": true,
  "product": {
    "id": 1,
    "brand_name": "Test Brand",
    "barcode": "012345678901",
    "ingredients": ["Ingredient1", "Ingredient2", "Ingredient3"],
    "product_type": "tampon",
    "coverage_score": 0.85,
    "research_count": 12
  }
}
```

### 4.2 Test with Postman
1. Create POST request to `http://localhost:8000/api/scan/barcode`
2. Body (JSON):
```json
{
  "barcode": "012345678901"
}
```
3. Send and verify response

### 4.3 Test with Frontend
1. Open `http://localhost:5173` (or 3000)
2. Navigate to scanner
3. Use browser's barcode/QR simulator or physical barcode
4. Verify product details display correctly

---

## Step 5: Optional - Risk Assessment Endpoint

To enable personalized health risk assessment:

### 5.1 Create Test User Profile
```sql
INSERT INTO profiles (id, user_id, sensitivities, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'test-user-123',
  ARRAY['Sensitive Skin', 'Allergies'],
  NOW(),
  NOW()
);
```

### 5.2 Test Risk Assessment Endpoint
```bash
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "012345678901",
    "user_id": "test-user-123"
  }'
```

Expected response includes:
- `overall_risk_level`: "Low Risk" | "Caution" | "High Risk"
- `risky_ingredients`: [] (list of concerning ingredients)
- `explanation`: 2-sentence assessment

---

## Troubleshooting

### Issue: Barcode not found (404)
**Solution:**
- Verify barcode exists in database: `SELECT * FROM products WHERE barcode='...'`
- Check barcode format matches exactly (case-sensitive, whitespace)
- Ensure index is created for performance

### Issue: Ingredient names showing as "Unknown"
**Solution:**
- Verify ingredient IDs in products.ingredients array exist in ingredients_library
- Check: `SELECT * FROM ingredients_library WHERE id IN (1,2,3)`
- Ensure data type is `integer[]` not `text[]`

### Issue: CORS error from frontend
**Solution:**
- Add frontend URL to `CORS_ORIGINS` in backend config
- Example: `CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]`
- Restart backend after changing config

### Issue: Connection pooling errors
**Solution:**
- Check Supabase connection is active
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Test with: `curl http://localhost:8000/health`

---

## Performance Tips

1. **Add Barcode Index** (already recommended)
2. **Cache Results** - Store lookups for 1 hour (future enhancement)
3. **Batch Queries** - Support multiple barcode lookups at once (future)
4. **Denormalize Ingredient Names** - Store ingredient names directly in products table instead of resolving via join (optimization)

---

## API Contract Summary

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/api/scan/barcode` | POST | Lookup product by barcode | `{barcode, user_id?}` | `{found, product}` |
| `/api/scan/barcode/assess` | POST | Lookup + risk assessment | `{barcode, user_id}` | `{scan_id, product, risk_level, risky_ingredients, explanation}` |
| `/api/scan/barcode/health` | GET | Health check | - | `{status, service, version}` |

---

## Next Steps

1. ✅ Backend implementation complete
2. ✅ Frontend component updated
3. ⏳ Test with real barcode data in your database
4. ⏳ Deploy to production (Vercel for frontend, Render/Railway for backend)
5. ⏳ Monitor performance and implement caching if needed

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
