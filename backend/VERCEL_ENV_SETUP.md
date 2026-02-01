# 🔐 Vercel Environment Variables Setup Guide

## Overview

Environment variables must be set in the **Vercel Dashboard** before deployment. The [`vercel.json`](vercel.json) file no longer references secrets with `@` syntax - instead, set them directly through the Vercel web interface.

---

## 📋 Step-by-Step Setup

### Step 1: Access Environment Variables

1. Go to https://vercel.com/dashboard
2. Select your project (or create new project)
3. Navigate to: **Settings** → **Environment Variables**

### Step 2: Add Required Variables

Add each variable individually using the "Add New" button:

#### **Required Backend Variables:**

| Variable Name | Value | Where to Get It |
|---------------|-------|-----------------|
| `SUPABASE_URL` | `https://[project-id].supabase.co` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_KEY` | `eyJhbGc...` (long token) | Supabase Dashboard → Settings → API → anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGc...` (long token) | Supabase Dashboard → Settings → API → service_role key (⚠️ Keep secret!) |
| `OPENAI_API_KEY` | `sk-proj-...` | https://platform.openai.com/api-keys |
| `ENVIRONMENT` | `production` | Static value |
| `LOG_LEVEL` | `INFO` | Static value |
| `DEBUG` | `false` | Static value |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Your frontend URL (update after frontend deployment) |

#### **Optional but Recommended:**

| Variable Name | Value | Purpose |
|---------------|-------|---------|
| `DATABASE_POOL_SIZE` | `10` | Optimizes Supabase connection pooling |
| `SENTRY_DSN` | `https://...@sentry.io/...` | Error tracking (get from Sentry.io) |
| `SENTRY_ENVIRONMENT` | `production` | Labels errors in Sentry |
| `ENABLE_REQUEST_LOGGING` | `true` | Logs all API requests |
| `REQUEST_TIMEOUT_SECONDS` | `30` | Max request duration |

### Step 3: Configure Environment Scope

For each variable, select the environment(s):
- ✅ **Production** - Live deployment
- ⚠️ **Preview** - Optional (for branch previews)
- ❌ **Development** - Not needed (use local `.env`)

### Step 4: Save and Redeploy

1. Click **"Save"** after adding all variables
2. Vercel will prompt to redeploy
3. Click **"Redeploy"** to apply changes

---

## 🔄 Common Issues & Solutions

### Issue: "Environment Variable references Secret which does not exist"

**Cause:** Old [`vercel.json`](vercel.json) used `@secret_name` syntax which requires Vercel CLI setup.

**Solution:** Remove the `env` block from [`vercel.json`](vercel.json) and set variables through the dashboard instead (already fixed in latest version).

### Issue: "Configuration failed to load"

**Cause:** Missing required environment variables.

**Solution:** Check [`config.py`](config.py) for required fields. All variables marked with `Field(...)` without `default` are required.

### Issue: "CORS error from frontend"

**Cause:** `CORS_ORIGINS` doesn't include your frontend URL.

**Solution:** 
1. Deploy frontend first to get its URL
2. Update `CORS_ORIGINS` in backend settings
3. Redeploy backend

---

## 🧪 Verify Setup

After setting all variables:

```bash
# Test health endpoint
curl https://your-backend.vercel.app/health

# Expected: {"status":"healthy","environment":"production"}

# Test readiness (checks database connection)
curl https://your-backend.vercel.app/ready

# Expected: {"ready":true,"database":"connected"}
```

---

## 📝 Environment Variable Reference

### How Environment Variables are Loaded:

1. **Vercel Dashboard** → Sets system environment variables
2. **[`config.py`](config.py)** → Loads and validates using Pydantic
3. **FastAPI** → Uses validated settings throughout app

### Example: How SUPABASE_URL flows

```
Vercel Dashboard (SUPABASE_URL=https://...)
           ↓
     config.py loads from os.environ
           ↓
   Settings class validates it exists
           ↓
     supabase_client.py uses settings.SUPABASE_URL
           ↓
        Connects to Supabase
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Set secrets only in Vercel Dashboard
- Use `SUPABASE_KEY` (anon) for frontend
- Use `SUPABASE_SERVICE_ROLE_KEY` only in backend
- Rotate API keys quarterly
- Enable 2FA on Vercel, Supabase, OpenAI accounts

### ❌ DON'T:
- Commit `.env` or `.env.production` to git
- Share `SUPABASE_SERVICE_ROLE_KEY` with frontend
- Use production keys in local development
- Hard-code secrets in code
- Log sensitive environment variables

---

## 📊 Quick Checklist

Before deployment, verify:

- [ ] All required variables set in Vercel Dashboard
- [ ] Variables scoped to "Production" environment
- [ ] `SUPABASE_URL` is accessible (test in browser)
- [ ] `SUPABASE_KEY` and `SUPABASE_SERVICE_ROLE_KEY` are different
- [ ] `OPENAI_API_KEY` starts with `sk-proj-` or `sk-`
- [ ] `CORS_ORIGINS` will be updated after frontend deployment
- [ ] No secrets committed to git (run `git status`)
- [ ] `.env.example` files don't contain real secrets

---

## 🚀 Next Steps

After setting environment variables:

1. **Deploy Backend:**
   ```bash
   git add .
   git commit -m "fix: Remove env block from vercel.json, add setup guide"
   git push origin main
   ```

2. **In Vercel Dashboard:**
   - Import GitHub repository
   - Set root directory to `backend`
   - Environment variables should already be configured
   - Click "Deploy"

3. **Verify Deployment:**
   - Check `/health` endpoint returns 200
   - Check `/ready` endpoint shows database connected
   - Monitor logs for errors

4. **Deploy Frontend** (separate Vercel project)

5. **Update `CORS_ORIGINS`** with frontend URL and redeploy backend

---

## 📚 Additional Resources

- [Vercel Environment Variables Docs](https://vercel.com/docs/projects/environment-variables)
- [Supabase API Keys Guide](https://supabase.com/docs/guides/api/api-keys)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Sentry Setup](https://docs.sentry.io/platforms/python/guides/fastapi/)

---

**Last Updated:** 2026-02-01  
**Status:** Ready for deployment with dashboard-based environment variables
