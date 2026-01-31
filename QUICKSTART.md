# Quick Start: Testing Barcode Lookup

## 5-Minute Setup

### Step 1: Seed Test Data (Choose One Method)

**Option A: SQL Script (Fastest)**
1. Go to Supabase Dashboard → SQL Editor → New Query
2. Copy entire contents of [`backend/database/seed_test_barcodes.sql`](backend/database/seed_test_barcodes.sql:1)
3. Paste and click **Run**
4. ✅ 5 test products inserted with barcodes

**Option B: Python Script**
```bash
cd backend
python scripts/seed_test_products.py seed
```

### Step 2: Start Backend
```bash
cd backend
python main.py
# Should see: "✓ Application startup completed"
```

### Step 3: Start Frontend
```bash
cd frontend
npm run dev
# Should see: "Local: http://localhost:5173"
```

### Step 4: Test Barcode Endpoint

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/scan/barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode": "012345678901"}'
```

**Expected Response:**
```json
{
  "found": true,
  "product": {
    "id": 1,
    "brand_name": "Pure Care Organic",
    "barcode": "012345678901",
    "ingredients": ["Organic Cotton", "Viscose", "Rayon"],
    "product_type": "tampon",
    "coverage_score": 0.95,
    "research_count": 15
  }
}
```

### Step 5: Test in Browser (Optional)

1. Open `http://localhost:5173`
2. Click "Scan Product"
3. Use browser's QR code simulator or print a QR with barcode `012345678901`
4. Verify product details display

---

## Test Barcodes

Copy these for testing:

```
012345678901  →  Pure Care Organic (tampon)
054321987654  →  Nature Choice (pad)
123456789012  →  EcoFlow Tampons (tampon)
987654321098  →  Comfort Plus (pad)
555666777888  →  Gentle Wave (tampon)
```

---

## Troubleshooting

**404 Product Not Found**
- Check barcode exists: `SELECT * FROM products WHERE barcode='012345678901'`
- Verify exact barcode match (case-sensitive, no spaces)

**No Ingredients Showing**
- Verify ingredient IDs exist: `SELECT * FROM ingredients_library WHERE id IN (1,2,3)`
- Check data type is `integer[]` not `text[]`

**CORS Error**
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart backend

**Connection Error**
- Test connection: `curl http://localhost:8000/health`
- Check `.env` has `SUPABASE_URL` and `SUPABASE_KEY`

---

## What's Working

✅ Barcode scanner captures barcode string  
✅ Frontend sends barcode to backend API  
✅ Backend queries products table by barcode  
✅ Ingredient IDs resolved to names  
✅ Product details displayed in UI  
✅ Error handling for missing products  
✅ Optional risk assessment with user sensitivities  

---

## Next: Deployment

After testing locally:

1. **Backend** - Deploy to Render/Railway/Vercel
2. **Frontend** - Deploy to Vercel (update `VITE_API_URL` to production backend)
3. **Database** - Supabase hosted (already in cloud)
4. **Testing** - Run e2e tests with real barcodes

---

**Questions?** Check [`plans/SETUP_GUIDE.md`](plans/SETUP_GUIDE.md:1) for detailed setup instructions.
