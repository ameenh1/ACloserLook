# Recent Scans Feature - Testing Guide

## Overview
This guide will help you test the newly implemented Recent Scans feature that allows users to view their scan history and quickly re-access previously scanned products.

---

## Prerequisites

### 1. Database Setup
First, you need to create the `scan_history` table in your Supabase database.

**Step 1: Open Supabase SQL Editor**
- Go to your Supabase project dashboard
- Click on "SQL Editor" in the left sidebar
- Click "New query"

**Step 2: Run the SQL Script**
- Copy the contents of [`backend/database/create_scan_history_table.sql`](../backend/database/create_scan_history_table.sql)
- Paste it into the SQL editor
- Click "Run" to execute

**Step 3: Verify Table Creation**
```sql
-- Check if table exists and view structure
SELECT * FROM information_schema.tables 
WHERE table_name = 'scan_history';

-- Check if policies are enabled
SELECT * FROM pg_policies 
WHERE tablename = 'scan_history';
```

### 2. Backend Setup
Ensure your backend is running with the updated code.

```bash
# Navigate to backend directory
cd backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
Ensure your frontend is running with the updated components.

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if needed)
npm install

# Run the development server
npm run dev
```

### 4. Environment Variables
Make sure your environment variables are set:

**Backend** (`.env`):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Frontend** (`.env`):
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## Testing Workflow

### Phase 1: Database Verification ✅

#### Test 1.1: Table Structure
```sql
-- View scan_history table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'scan_history'
ORDER BY ordinal_position;
```

**Expected Output:**
- `id` (bigint, PRIMARY KEY)
- `scan_id` (uuid, NOT NULL, UNIQUE)
- `user_id` (text, NOT NULL)
- `product_id` (integer, NOT NULL)
- `barcode` (text, NOT NULL)
- `risk_level` (text, NOT NULL)
- `risk_score` (integer, nullable)
- `risky_ingredients` (jsonb, nullable)
- `explanation` (text, nullable)
- `scanned_at` (timestamp with time zone)

#### Test 1.2: Indexes
```sql
-- Check indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'scan_history';
```

**Expected Indexes:**
- `idx_scan_history_user_id`
- `idx_scan_history_scan_id`
- `idx_scan_history_barcode`

#### Test 1.3: Row Level Security
```sql
-- Check RLS policies
SELECT policyname, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'scan_history';
```

**Expected Policies:**
- `Users can view their own scan history` (SELECT)
- `Users can insert their own scans` (INSERT)

---

### Phase 2: Backend API Testing 🔧

#### Test 2.1: Scan Assessment Saves History

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "037000818052",
    "user_id": "test-user-123"
  }'
```

**Expected Response:**
```json
{
  "scan_id": "uuid-here",
  "user_id": "test-user-123",
  "product": {
    "id": 1,
    "brand_name": "Always",
    "barcode": "037000818052",
    "ingredients": [...],
    "product_type": "pad"
  },
  "overall_risk_level": "Caution",
  "risk_score": 65,
  "risky_ingredients": [...],
  "explanation": "...",
  "timestamp": "2026-02-01T05:00:00.000Z"
}
```

**Verify in Database:**
```sql
-- Check if scan was saved
SELECT * FROM scan_history 
WHERE user_id = 'test-user-123' 
ORDER BY scanned_at DESC 
LIMIT 1;
```

#### Test 2.2: GET Scan History Endpoint

**Test with curl:**
```bash
curl -X GET "http://localhost:8000/api/scan/history?user_id=test-user-123&limit=5"
```

**Expected Response:**
```json
{
  "scans": [
    {
      "scan_id": "uuid-here",
      "barcode": "037000818052",
      "brand_name": "Always",
      "product_type": "pad",
      "risk_level": "Caution",
      "risk_score": 65,
      "scanned_at": "2026-02-01T05:00:00.000Z"
    }
  ],
  "count": 1
}
```

#### Test 2.3: Empty History
```bash
curl -X GET "http://localhost:8000/api/scan/history?user_id=nonexistent-user&limit=5"
```

**Expected Response:**
```json
{
  "scans": [],
  "count": 0
}
```

#### Test 2.4: Invalid User ID
```bash
curl -X GET "http://localhost:8000/api/scan/history?user_id=&limit=5"
```

**Expected Response:**
```json
{
  "detail": "user_id is required"
}
```

---

### Phase 3: Frontend Testing 🖥️

#### Test 3.1: User Login
1. Open the app in browser: `http://localhost:5173`
2. Click "Get Started"
3. Login or create an account
4. You should be redirected to the homepage

#### Test 3.2: Initial State - No Scans
1. On the homepage, look for the "Recent Scans" card
2. **Expected:** The card should be collapsed by default
3. Click on "Recent Scans" to expand it
4. **Expected:** Should show "No products scanned yet"

#### Test 3.3: Scan a Product
1. Click the "Scan Product" button
2. Allow camera permissions (or use test barcode if available)
3. Scan a product barcode (e.g., `037000818052` for Always pads)
4. **Expected:** 
   - Product info loads
   - Risk assessment displays with circular score
   - Product details shown

#### Test 3.4: View Recent Scans
1. Click "Back to Home" to return to homepage
2. Click on "Recent Scans" to expand the dropdown
3. **Expected:**
   - Loading indicator appears briefly
   - Previously scanned product appears in the list
   - Shows risk icon (green ✓, yellow ⚠, or red ✕)
   - Shows product name
   - Shows time ago (e.g., "2m ago")
   - Shows risk score (if available)

#### Test 3.5: Click Recent Scan
1. In the Recent Scans dropdown, click on a previously scanned product
2. **Expected:**
   - Dropdown closes
   - Navigates to Product Result Screen
   - Shows the same product details
   - Performs a fresh assessment

#### Test 3.6: Multiple Scans
1. Scan 3-5 different products
2. Return to homepage after each scan
3. Open Recent Scans dropdown
4. **Expected:**
   - All scanned products appear in reverse chronological order (newest first)
   - Each shows correct risk level and score
   - Time stamps are accurate
   - List is scrollable if more than 5 items

#### Test 3.7: Recent Scans Dropdown UI
Check the following UI elements:
- ✅ Header with clock icon and "Recent Scans" text
- ✅ Chevron icon (down when closed, up when open)
- ✅ Smooth expand/collapse animation
- ✅ Hover effects on items
- ✅ Risk icons colored correctly:
  - Green for "Low Risk"
  - Yellow for "Caution"
  - Red for "High Risk"
- ✅ Product names don't overflow (truncated with ellipsis)
- ✅ Scrollable if more than ~5 items

---

### Phase 4: Edge Cases & Error Handling 🛡️

#### Test 4.1: Network Error
1. Stop the backend server
2. Open Recent Scans dropdown
3. **Expected:** "Could not load scan history" error message

#### Test 4.2: Not Logged In
1. Clear browser storage/cookies (logout)
2. Somehow access homepage (this shouldn't normally happen)
3. Try to open Recent Scans
4. **Expected:** "Please log in to view scan history" message

#### Test 4.3: Multiple Users
1. Login as User A, scan products
2. Logout and login as User B, scan different products
3. Check Recent Scans for both users
4. **Expected:** Each user only sees their own scans (RLS working)

#### Test 4.4: Scan History Save Failure
1. Temporarily disable database access or simulate error
2. Scan a product
3. **Expected:**
   - Product assessment still completes
   - Backend logs warning about history save failure
   - User doesn't see error (non-blocking)

#### Test 4.5: Product Deleted from Database
1. Scan a product to save to history
2. Manually delete the product from `products` table
3. Open Recent Scans
4. **Expected:** May show "Unknown" or handle gracefully

---

### Phase 5: Performance Testing ⚡

#### Test 5.1: Large History
1. Create 50+ scan history records in database
```sql
-- Insert test data (adjust user_id and product_id as needed)
INSERT INTO scan_history (scan_id, user_id, product_id, barcode, risk_level, risk_score, explanation)
SELECT 
    gen_random_uuid(),
    'test-user-123',
    1,
    'TEST-' || generate_series,
    (ARRAY['Low Risk', 'Caution', 'High Risk'])[floor(random() * 3 + 1)],
    floor(random() * 100),
    'Test explanation'
FROM generate_series(1, 50);
```

2. Open Recent Scans dropdown
3. **Expected:**
   - Loads quickly (should query with LIMIT 5)
   - Shows only 5 most recent scans
   - Smooth scrolling

#### Test 5.2: Quick Successive Clicks
1. Rapidly click Recent Scans open/close multiple times
2. **Expected:** No duplicate API calls, smooth animation

---

## Manual Testing Checklist

### Database Setup ✅
- [ ] `scan_history` table created
- [ ] All columns present with correct types
- [ ] Indexes created (user_id, scan_id, barcode)
- [ ] RLS enabled with correct policies
- [ ] Foreign keys working (products, profiles)

### Backend Endpoints ✅
- [ ] POST `/api/scan/barcode/assess` saves to history
- [ ] GET `/api/scan/history` returns user's scans
- [ ] Empty history returns empty array
- [ ] Invalid user_id returns 400 error
- [ ] RLS prevents cross-user data access
- [ ] API includes `risk_score` in response

### Frontend Components ✅
- [ ] RecentScansDropdown component displays
- [ ] Opens/closes on click
- [ ] Fetches data on open
- [ ] Shows loading state
- [ ] Shows error states
- [ ] Shows empty state
- [ ] Displays scans with correct info
- [ ] Risk icons colored correctly
- [ ] Time formatting works (2m ago, 3h ago, etc.)
- [ ] Clicking scan navigates to product

### Navigation Flow ✅
- [ ] Scan button opens scanner (no barcode)
- [ ] Recent scan click goes to results (with barcode)
- [ ] Back button from results returns to homepage
- [ ] Scan another opens scanner

### User Experience ✅
- [ ] Scans appear immediately after scanning
- [ ] Dropdown closes after clicking item
- [ ] UI matches design (fonts, colors, spacing)
- [ ] Animations smooth
- [ ] Mobile responsive
- [ ] Accessible (keyboard navigation, screen readers)

---

## Common Issues & Solutions

### Issue 1: "scan_history table does not exist"
**Solution:** Run the SQL script in Supabase SQL Editor

### Issue 2: "RLS policy violation"
**Solution:** Ensure user is logged in with valid `auth.uid()`

### Issue 3: Recent scans not appearing
**Solutions:**
- Check backend logs for save errors
- Verify user_id matches between scan and history fetch
- Check browser console for API errors
- Ensure `VITE_API_URL` is correct in frontend `.env`

### Issue 4: "Could not load scan history"
**Solutions:**
- Verify backend is running
- Check network tab for 404/500 errors
- Ensure Supabase connection is working
- Check user authentication status

### Issue 5: Scans showing for wrong user
**Solution:** RLS policy issue - verify policies are enabled and correct

---

## Success Criteria

✅ **Feature Complete When:**
1. Users can see their recent scans in a dropdown
2. Scans are saved automatically after assessment
3. Clicking a recent scan navigates to product details
4. Each scan shows risk level, score, and time
5. Only user's own scans are visible (RLS working)
6. Error states handled gracefully
7. UI matches design specifications
8. Performance is smooth with many scans

---

## Next Steps After Testing

Once all tests pass:

1. **Deploy to Production**
   - Run SQL script on production Supabase
   - Deploy backend with updated code
   - Deploy frontend with new components

2. **Monitor**
   - Check backend logs for history save success rate
   - Monitor API response times for `/scan/history`
   - Track user engagement with Recent Scans

3. **Future Enhancements**
   - Add "Clear History" button
   - Add search/filter functionality
   - Add export history feature
   - Show scan statistics (most scanned products, average risk)

---

## Quick Test Commands Reference

```bash
# Backend: Test scan assessment
curl -X POST http://localhost:8000/api/scan/barcode/assess \
  -H "Content-Type: application/json" \
  -d '{"barcode": "037000818052", "user_id": "YOUR_USER_ID"}'

# Backend: Get scan history
curl -X GET "http://localhost:8000/api/scan/history?user_id=YOUR_USER_ID&limit=5"

# Database: Check scan history
# Run in Supabase SQL Editor:
SELECT sh.*, p.brand_name 
FROM scan_history sh
LEFT JOIN products p ON sh.product_id = p.id
WHERE sh.user_id = 'YOUR_USER_ID'
ORDER BY sh.scanned_at DESC;
```

---

## Files Modified Summary

### Backend
- ✅ [`backend/database/create_scan_history_table.sql`](../backend/database/create_scan_history_table.sql) - New table creation
- ✅ [`backend/routers/scan.py`](../backend/routers/scan.py) - Added save function and GET endpoint

### Frontend
- ✅ [`frontend/src/components/RecentScansDropdown.tsx`](../frontend/src/components/RecentScansDropdown.tsx) - New component
- ✅ [`frontend/src/components/HomePageScreen.tsx`](../frontend/src/components/HomePageScreen.tsx) - Use dropdown
- ✅ [`frontend/src/App.tsx`](../frontend/src/App.tsx) - Updated navigation logic

---

## Contact & Support

If you encounter issues during testing:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Ensure database migrations ran successfully
5. Review this guide for troubleshooting steps

**Happy Testing! 🎉**
