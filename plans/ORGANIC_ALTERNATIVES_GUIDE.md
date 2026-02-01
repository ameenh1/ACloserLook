# Adding Organic Alternative Products - Quick Guide

## Overview
This guide shows how to add organic and non-toxic alternative products that will be displayed when users scan products like Always pads or Tampax tampons.

---

## Step 1: Run the SQL Script in Supabase

### Open Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Click "SQL Editor" in the left sidebar
3. Click "New query"

### Execute the Script
1. Copy the contents of [`backend/database/add_organic_alternatives.sql`](../backend/database/add_organic_alternatives.sql)
2. Paste into the SQL editor
3. Click "Run" to execute

### What Gets Added

#### **Organic Pads (3 products):**
- ✅ Rael Organic Cotton Cover Pads
- ✅ Cora Organic Ultra Thin Period Pads
- ✅ Organyc Heavy Night Pads

#### **Organic Tampons (3 products):**
- ✅ Organyc Compact Tampons Super 16 Count
- ✅ Cora The Comfort Fit Organic Cotton Tampons
- ✅ The Honey Pot Duo Pack Tampons

---

## Step 2: Verify Products Were Added

Run this query in Supabase SQL Editor:

```sql
-- Check all organic alternatives
SELECT id, brand_name, product_type, barcode
FROM products
WHERE brand_name IN (
    'Rael Organic Cotton Cover Pads',
    'Cora Organic Ultra Thin Period Pads',
    'Organyc Heavy Night Pads',
    'Organyc Compact Tampons Super 16 Count',
    'Cora The Comfort Fit Organic Cotton Tampons',
    'The Honey Pot Duo Pack Tampons'
)
ORDER BY product_type, brand_name;
```

**Expected Result:** 6 rows (3 pads, 3 tampons)

---

## Step 3: How Alternatives Are Displayed

The alternatives display logic is in [`ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx:539):

### Current Logic (lines 128-130, 539-570)
```typescript
// If product is risky, fetch alternatives
if (data.overall_risk_level === "High Risk" || data.overall_risk_level === "Caution") {
    fetchAlternatives(data.product.product_type);
}
```

### How It Works:
1. User scans Always pads (barcode: `037000818052`)
2. Risk assessment returns "Caution" or "High Risk"
3. Frontend queries Supabase for products with `product_type = 'pad'`
4. Displays up to 3 alternatives
5. Shows with green "Safe" badge

---

## Step 4: Test the Alternatives Display

### Test with Always Pads
1. **Scan barcode:** `037000818052` (Always pads)
2. **Expected result:**
   - Risk level shows "Caution" or "High Risk"
   - Scroll down to see "Safer Alternatives" section
   - Should display:
     - Rael Organic Cotton Cover Pads
     - Cora Organic Ultra Thin Period Pads
     - Organyc Heavy Night Pads
   - Each shows green shield icon with "Safe" label

### Test with Tampax Tampons
1. **Scan barcode:** `073010719743` (Tampax Pearl)
2. **Expected result:**
   - Risk level shows "Caution" or "High Risk"
   - "Safer Alternatives" section appears
   - Should display:
     - Organyc Compact Tampons Super 16 Count
     - Cora The Comfort Fit Organic Cotton Tampons
     - The Honey Pot Duo Pack Tampons

---

## Step 5: Customize the Display (Optional)

If you want to customize how alternatives are displayed, edit [`ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx:539):

### Current Display (lines 539-570)
```typescript
{/* Alternative Products (only if assessment available and not safe) */}
{assessmentData && !isSafe && alternatives.length > 0 && (
  <div className="bg-[#5a3d6b]/50 border border-[#a380a8]/40 rounded-[16px] p-5 mb-4">
    <div className="flex items-center gap-2 mb-4">
      <ShieldCheck size={20} className="text-[#a380a8]" />
      <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
        Safer Alternatives
      </h3>
    </div>
    <div className="space-y-3">
      {alternatives.map((alt) => (
        <div key={alt.id} className="bg-[#3a2849]/60 border border-[#a380a8]/20 rounded-[12px] p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
                {alt.brand_name}
              </p>
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white tracking-[-0.6px]">
                {alt.product_type}
              </p>
            </div>
            <div className="flex items-center gap-1 bg-green-500/20 px-2 py-1 rounded-full">
              <ShieldCheck size={12} className="text-green-400" />
              <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-green-400">
                Safe
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
)}
```

---

## Troubleshooting

### Issue: Alternatives not showing
**Possible causes:**
1. Products not added to database
   - **Solution:** Re-run the SQL script
2. Product type doesn't match
   - **Solution:** Verify `product_type` is exactly 'pad' or 'tampon'
3. Risk level is "Low Risk"
   - **Expected:** Alternatives only show for Caution/High Risk

### Issue: Wrong alternatives showing
**Solution:** Check the query in [`ProductResultScreen.tsx`](../frontend/src/components/ProductResultScreen.tsx:142):
```typescript
const { data, error } = await supabase
    .from('products')
    .select('id, brand_name, product_type')
    .eq('product_type', productType || 'general')
    .limit(3);
```

---

## Adding More Alternatives

To add more alternative products in the future:

```sql
-- Template for new alternative
INSERT INTO products (brand_name, product_type, ingredients, barcode)
VALUES (
    'Brand Name Here',
    'pad',  -- or 'tampon', 'liner', etc.
    ARRAY[
        'Ingredient 1',
        'Ingredient 2',
        'Ingredient 3'
    ],
    'UNIQUE-BARCODE-HERE'
)
ON CONFLICT (barcode) DO NOTHING;
```

---

## Quick Commands

```bash
# Connect to Supabase and verify products
# Run in Supabase SQL Editor:

-- Count products by type
SELECT product_type, COUNT(*) as count
FROM products
GROUP BY product_type;

-- View all pads
SELECT brand_name FROM products WHERE product_type = 'pad';

-- View all tampons
SELECT brand_name FROM products WHERE product_type = 'tampon';
```

---

## Success Criteria

✅ **Alternatives Working When:**
- [ ] 6 new products added to database (3 pads, 3 tampons)
- [ ] Scanning Always pads shows 3 pad alternatives
- [ ] Scanning Tampax tampons shows 3 tampon alternatives
- [ ] Each alternative has green "Safe" badge
- [ ] Alternatives only appear for Caution/High Risk products
- [ ] UI displays correctly with product names

---

## Next Steps

After adding alternatives:
1. ✅ Run the SQL script in Supabase
2. ✅ Verify products were added
3. ✅ Test by scanning Always pads
4. ✅ Test by scanning Tampax tampons
5. ✅ Verify alternatives display with correct styling

The organic alternatives feature is now complete! 🌱
