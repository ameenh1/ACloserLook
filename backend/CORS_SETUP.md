# CORS Setup Guide - Lotus Backend

## What is CORS?

**CORS** (Cross-Origin Resource Sharing) is a browser security feature that controls which websites can make requests to your backend API.

When your frontend (running on `https://your-frontend.vercel.app`) makes a request to your backend (running on `https://your-backend.vercel.app`), the browser checks:

1. Is the frontend origin allowed to access this API?
2. Does the request method (GET, POST, etc.) have permission?
3. Are the headers valid?

If CORS is not configured correctly, you'll see browser errors like:
```
Access to XMLHttpRequest at 'https://api.example.com/scan' from origin 
'https://frontend.example.com' has been blocked by CORS policy
```

---

## CORS Configuration

### Development Environment (Local Testing)

For local development with frontend on `localhost:3000` and backend on `localhost:8000`:

#### Backend `.env` (Development)

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000
```

#### Testing CORS Locally

```bash
# Start backend
cd backend
python -m uvicorn main:app --reload

# Start frontend (in another terminal)
cd frontend
npm run dev

# Test CORS with curl
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:8000/api/scan
```

Expected response headers:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-ID
Access-Control-Max-Age: 3600
```

---

### Production Environment (Vercel Deployment)

When you deploy to Vercel, update CORS for your production domain:

#### Step 1: Get Your Frontend URL

From Vercel Dashboard:
- Go to your frontend project
- Copy the deployment URL (usually `https://your-project-name.vercel.app`)
- Also get your custom domain if you have one (e.g., `https://your-domain.com`)

#### Step 2: Configure Backend CORS

In Vercel Dashboard for your backend project:

1. Go to **Settings** → **Environment Variables**
2. Find or create `CORS_ORIGINS` variable
3. Set value: `https://your-frontend.vercel.app,https://your-domain.com`
4. Click **Save** or **Update**
5. **Redeploy** for changes to take effect

Example:
```
CORS_ORIGINS=https://lotus-frontend.vercel.app,https://lotus-health.com,https://www.lotus-health.com
```

#### Step 3: Verify CORS Configuration

After redeployment, test from your frontend:

```javascript
// In your frontend React component or JavaScript
const response = await fetch('https://your-api.vercel.app/api/scan', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ /* scan data */ })
});

// Check if successful (no CORS error in console)
const data = await response.json();
console.log(data);
```

Or with curl:
```bash
curl -i -X POST https://your-api.vercel.app/api/scan \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Content-Type: application/json" \
  -d '{}'

# Should see in response headers:
# Access-Control-Allow-Origin: https://your-frontend.vercel.app
```

---

## CORS Configuration Troubleshooting

### Issue: "Access to XMLHttpRequest blocked by CORS policy"

**Cause**: Frontend origin not in `CORS_ORIGINS`

**Solution**:
1. Check frontend URL in browser address bar
2. Add that exact URL to `CORS_ORIGINS`
3. Redeploy backend
4. Clear browser cache (Ctrl+Shift+Delete)
5. Retry request

Example:
```
# If frontend is at: https://lotus.vercel.app
# Add to CORS_ORIGINS:
CORS_ORIGINS=https://lotus.vercel.app
```

### Issue: CORS works on localhost but not in production

**Cause**: `CORS_ORIGINS` configured only for localhost

**Solution**:
```env
# BEFORE (development only)
CORS_ORIGINS=http://localhost:3000

# AFTER (development + production)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

### Issue: Custom domain shows CORS error

**Cause**: Only Vercel default URL configured, not custom domain

**Solution**:
```env
# Add ALL domains that should access your API
CORS_ORIGINS=https://lotus.vercel.app,https://lotus-health.com,https://www.lotus-health.com
```

---

## Advanced CORS Configuration

### Updating CORS in Code (If Needed)

Instead of environment variables, you can hardcode in [`backend/main.py`](./main.py):

```python
# Find this section in main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Uses env variable
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    max_age=3600,
)

# You can also manually specify origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lotus-frontend.vercel.app",
        "https://lotus-health.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    max_age=3600,
)
```

### Allow All Origins (NOT Recommended for Production)

Only for testing - **DO NOT use in production**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ DANGEROUS - allows any origin
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Understanding CORS Headers

**Request headers** (sent by browser):
```
Origin: https://your-frontend.vercel.app
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

**Response headers** (sent by backend):
```
Access-Control-Allow-Origin: https://your-frontend.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-ID
Access-Control-Max-Age: 3600
Access-Control-Allow-Credentials: true
```

---

## Frontend Implementation

### React/Next.js Example

```javascript
// src/services/api.ts
const BACKEND_URL = process.env.REACT_APP_API_URL || 'https://your-api.vercel.app';

export async function scanProduct(file: File, userId: string) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/scan?user_id=${userId}`, {
      method: 'POST',
      credentials: 'include', // Include cookies if needed
      body: formData,
      headers: {
        'X-Request-ID': crypto.randomUUID(), // Optional: for request tracing
      },
      // Content-Type is automatically set when using FormData
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('CORS or API error:', error);
    throw error;
  }
}
```

### Environment Variables (Frontend)

Create `.env.local` in your frontend project:

```env
# Development
REACT_APP_API_URL=http://localhost:8000

# Or production:
REACT_APP_API_URL=https://your-backend-api.vercel.app
```

---

## Testing CORS with Different Tools

### Using curl

```bash
# Preflight request (OPTIONS)
curl -i -X OPTIONS https://your-api.vercel.app/api/scan \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"

# Actual POST request
curl -i -X POST https://your-api.vercel.app/api/scan \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Using Postman

1. Open Postman
2. Create new POST request to `https://your-api.vercel.app/api/scan`
3. Go to **Headers** tab
4. Add: `Origin: https://your-frontend.vercel.app`
5. Send request
6. Check response headers for `Access-Control-Allow-Origin`

### Using Browser DevTools

1. Open frontend in browser
2. Open DevTools (F12)
3. Go to **Network** tab
4. Make API request from frontend
5. Click request in Network tab
6. Go to **Response Headers** section
7. Look for `Access-Control-Allow-Origin`

---

## CORS Checklist

Before deploying frontend + backend:

- [ ] Frontend deployed to Vercel (note the URL)
- [ ] Backend deployed to Vercel (note the URL)
- [ ] `CORS_ORIGINS` environment variable set in backend
- [ ] Includes frontend URL (e.g., `https://frontend.vercel.app`)
- [ ] Backend has been redeployed after CORS change
- [ ] Browser cache cleared
- [ ] Tested with curl or Postman first
- [ ] Tested from frontend in browser
- [ ] No CORS errors in browser console
- [ ] API requests complete successfully

---

## Common CORS Origins

| Environment | Frontend URL | Backend CORS |
|---|---|---|
| Local Dev | `http://localhost:3000` | `http://localhost:3000` |
| Local Fullstack | `http://localhost:3000` | `http://localhost:8000` |
| Vercel Frontend | `https://app.vercel.app` | `https://app.vercel.app` |
| Vercel Both | `https://frontend.vercel.app` | `https://frontend.vercel.app` |
| Custom Domain | `https://app.com` | `https://app.com` |
| With www | `https://www.app.com` | `https://www.app.com,https://app.com` |

---

## References

- **MDN CORS Guide**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- **FastAPI CORS**: https://fastapi.tiangolo.com/tutorial/cors/
- **Vercel Environment Variables**: https://vercel.com/docs/environment-variables

---

**Last Updated**: 2026-01-31
**Lotus Backend Version**: 0.1.0
