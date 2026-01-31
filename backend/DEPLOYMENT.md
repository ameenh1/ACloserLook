# Lotus Backend - Production Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Architecture](#deployment-architecture)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Environment Variables & Secrets](#environment-variables--secrets)
6. [Database Migrations](#database-migrations)
7. [Health Check Verification](#health-check-verification)
8. [Monitoring & Error Tracking](#monitoring--error-tracking)
9. [Scaling & Performance](#scaling--performance)
10. [Troubleshooting](#troubleshooting)
11. [Rollback Procedures](#rollback-procedures)
12. [Production Checklist](#production-checklist)

---

## Overview

Lotus Backend is deployed as **Vercel Functions** - serverless FastAPI on Vercel's infrastructure. This provides:

- ✅ Free tier with generous limits (100GB bandwidth/month)
- ✅ Automatic GitHub integration and CI/CD
- ✅ Same platform as frontend (unified dashboard)
- ✅ Global edge network for low latency
- ✅ Automatic scaling for traffic spikes

**Deployment Stack:**
- **Compute**: Vercel Functions (serverless)
- **Database**: Supabase PostgreSQL + Vector Search
- **Frontend**: Vercel (Next.js/React)
- **Error Tracking**: Sentry (optional but recommended)

---

## Prerequisites

Before deployment, ensure you have:

### 1. **Supabase Account** ✓
- [ ] Create free account at https://supabase.com
- [ ] Create new project
- [ ] Note: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Database tables and functions initialized (from Phase 1-6)
- [ ] Vector search embeddings populated

### 2. **OpenAI API Key** ✓
- [ ] Create account at https://platform.openai.com
- [ ] Generate API key from https://platform.openai.com/account/api-keys
- [ ] Note: `OPENAI_API_KEY`

### 3. **Vercel Account** ✓
- [ ] Create free account at https://vercel.com
- [ ] Link GitHub account for automatic deployments
- [ ] Note: Your GitHub repo must be connected

### 4. **GitHub Repository** ✓
- [ ] Push code to GitHub
- [ ] Repository contains entire project structure
- [ ] `.gitignore` excludes `.env` files

### 5. **Sentry Account** (Optional but recommended) ✓
- [ ] Create free account at https://sentry.io
- [ ] Create new project for Python/FastAPI
- [ ] Note: `SENTRY_DSN`

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Vercel Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Frontend Next.js│         │ Backend FastAPI  │          │
│  │  (React App)     │◄───────►│  (Functions)     │          │
│  │  :3000 (local)   │         │  /api routes     │          │
│  └──────────────────┘         └──────────────────┘          │
│                                      │                       │
│                                      │                       │
└──────────────────────────────────────┼───────────────────────┘
                                       │ HTTPS
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
         ┌────▼────┐            ┌──────▼───────┐        ┌──────▼──────┐
         │ Supabase │            │ OpenAI API  │        │   Sentry    │
         │PostgreSQL◄────────────┤ (embeddings)│        │  (errors)   │
         │+ pgvector│            │             │        │             │
         └──────────┘            └─────────────┘        └─────────────┘
```

---

## Step-by-Step Deployment

### Step 1: Prepare Local Repository

```bash
cd /path/to/ACloserLook

# Ensure all changes are committed
git status

# If needed, stage and commit changes
git add .
git commit -m "Phase 7: Production deployment configuration"

# Push to GitHub
git push origin main
```

### Step 2: Connect Vercel Project

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import from GitHub → Select your `ACloserLook` repository
4. Configure project:
   - **Framework Preset**: Other (Python)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: Leave empty (Vercel auto-detects)
   - **Install Command**: `pip install -r requirements.txt`

### Step 3: Configure Environment Secrets

1. In Vercel Dashboard, go to project **Settings** → **Environment Variables**
2. Add the following secrets (from your `.env.production` template):

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=sk-your-openai-key
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
DATABASE_POOL_SIZE=10
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

**Important**: Each environment variable must be added individually through the Vercel dashboard UI.

### Step 4: Set Up Deployment Trigger

1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest commit
3. Wait for deployment to complete (2-3 minutes)
4. Monitor build logs for errors

### Step 5: Verify Deployment

```bash
# Get your Vercel backend URL from the deployment dashboard
# Format: https://your-project-name.vercel.app

# Test health endpoint
curl https://your-project-name.vercel.app/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Lotus Backend",
#   "version": "0.1.0",
#   "environment": "production",
#   "timestamp": "2026-01-31T18:00:00Z"
# }

# Test readiness endpoint
curl https://your-project-name.vercel.app/ready

# Test CORS from frontend
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     https://your-project-name.vercel.app/health
```

---

## Environment Variables & Secrets

### Development Environment (`.env`)

Used locally for testing:

```
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DEBUG=true
```

### Production Environment (Vercel Dashboard)

**Critical Secrets** (get from services):

| Variable | Source | Required |
|----------|--------|----------|
| `SUPABASE_URL` | https://app.supabase.com/project/[id]/settings/api | ✓ |
| `SUPABASE_KEY` | Supabase Dashboard → API Keys | ✓ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → API Keys | ✓ |
| `OPENAI_API_KEY` | https://platform.openai.com/account/api-keys | ✓ |
| `SENTRY_DSN` | https://sentry.io/settings/account/projects | Optional |

**Configuration Variables** (set in Vercel dashboard):

```
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
DATABASE_POOL_SIZE=10
DATABASE_POOL_TIMEOUT=30
ENABLE_REQUEST_LOGGING=true
REQUEST_TIMEOUT_SECONDS=30
```

### Secrets Security Best Practices

1. **Never commit secrets** to Git
2. **Use Vercel Secrets** for all sensitive data
3. **Rotate API keys** quarterly
4. **Use read-only keys** where possible (e.g., Supabase anon key for frontend)
5. **Enable IP whitelisting** on OpenAI API
6. **Monitor usage** for suspicious activity

---

## Database Migrations

### Pre-Deployment Database Check

Before deploying, verify Supabase is configured:

```bash
# Test Supabase connection
curl -H "Authorization: Bearer YOUR_SUPABASE_KEY" \
     https://your-project.supabase.co/rest/v1/ingredients_library?select=count \
     | head -20
```

### Running Migrations

Migrations are configured to run automatically:

1. **On deployment**: Vercel runs migration scripts
2. **Manual execution** (if needed):

```bash
# SSH into Vercel deployment and run:
python -m backend.database.migrations
```

### Database Connection Pooling

Production configuration automatically adjusts:

- **Development**: Pool size = 2 (minimal)
- **Production**: Pool size = 10 (optimized for concurrency)

Monitor connection usage in Supabase Dashboard → Database → Connections.

---

## Health Check Verification

### Automated Health Checks

Vercel automatically monitors:

- **Endpoint**: `GET /health`
- **Timeout**: 10 seconds
- **Interval**: 30 seconds
- **Failure threshold**: 5 consecutive failures

### Manual Health Monitoring

Monitor these endpoints regularly:

```bash
# Health status (is service running?)
curl https://your-project-name.vercel.app/health

# Readiness status (is database connected?)
curl https://your-project-name.vercel.app/ready

# Logs endpoint
curl https://your-project-name.vercel.app/api/docs (if DEBUG=true)
```

### Response Examples

**Healthy Response:**
```json
{
  "status": "healthy",
  "service": "Lotus Backend",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2026-01-31T18:00:00Z"
}
```

**Ready Response:**
```json
{
  "ready": true,
  "service": "Lotus Backend",
  "database": "connected",
  "timestamp": "2026-01-31T18:00:00Z"
}
```

**Not Ready Response:**
```json
{
  "ready": false,
  "service": "Lotus Backend",
  "database": "disconnected",
  "error": "Connection refused",
  "timestamp": "2026-01-31T18:00:00Z"
}
```

---

## Monitoring & Error Tracking

### Sentry Configuration (Recommended)

1. **Create Sentry Project**:
   - Go to https://sentry.io
   - Create new project for Python/FastAPI
   - Copy DSN

2. **Add to Vercel Secrets**:
   ```
   SENTRY_DSN=https://xxxxx@sentry.io/yyyyy
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE_RATE=0.1
   SENTRY_PROFILES_SAMPLE_RATE=0.1
   ```

3. **Verify Integration**:
   - Trigger test error: `curl https://your-api.vercel.app/api/test-error`
   - Check Sentry Dashboard for error event

### Logging

All requests are logged with:

- **Method & Path**: `POST /api/scan`
- **Status & Duration**: `200 (1.23s)`
- **Request ID**: Unique identifier for tracing
- **User/Session**: From headers if available

View logs in:
- **Vercel Dashboard**: Deployments → Logs
- **Real-time**: `vercel logs` CLI command

### Performance Metrics

Monitor in Vercel Dashboard:

- **Execution Time**: Should be < 5 seconds
- **Memory Usage**: Should be < 200MB
- **Cold Starts**: Track degradation over time
- **Error Rate**: Should be < 1%

### Alerting Setup

Create alerts in Vercel for:

- Deployment failures
- High error rates (> 5% of requests)
- Slow response times (> 10 seconds)
- Function timeouts

---

## Scaling & Performance

### Vercel Functions Limits

| Metric | Free Tier | Pro Tier |
|--------|-----------|----------|
| Bandwidth | 100GB/month | 500GB/month |
| Build time | 45 min/month | Unlimited |
| Functions | Unlimited | Unlimited |
| Execution timeout | 10 seconds | 60 seconds |
| Memory | 128MB | 3GB |
| Cold starts | Normal | Reduced |

### Optimization Strategies

1. **Reduce Cold Starts**:
   - Minimize dependencies in `requirements.txt`
   - Use lightweight alternatives (e.g., httpx instead of requests)
   - Consider pre-warming functions

2. **Optimize Vector Search**:
   - Use Supabase RPC for server-side similarity search
   - Cache frequent queries in-function
   - Limit result sets (max_results = 20)

3. **Connection Pooling**:
   - `DATABASE_POOL_SIZE=10` for production
   - Connections reused across function invocations
   - Monitor connection exhaustion in Supabase

4. **Request Optimization**:
   - Compress responses with gzip
   - Implement caching headers
   - Batch requests where possible

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: 502 Bad Gateway

**Cause**: Function execution failed or exceeded timeout

**Solution**:
1. Check logs: `vercel logs`
2. Verify environment variables are set
3. Check Supabase connection
4. Reduce payload size if OCR processing

```bash
vercel logs --follow
```

#### Issue: CORS Error (Frontend can't call backend)

**Cause**: `CORS_ORIGINS` not configured correctly

**Solution**:
```bash
# Add your frontend URL to Vercel environment variables
CORS_ORIGINS=https://your-frontend.vercel.app

# Test CORS:
curl -i -X OPTIONS https://your-api.vercel.app/api/scan \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST"

# Should return headers:
# Access-Control-Allow-Origin: https://your-frontend.vercel.app
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

#### Issue: 401 Unauthorized (Supabase)

**Cause**: Invalid or expired API keys

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in Vercel dashboard
2. Check Supabase project is active (not deleted)
3. Regenerate keys if compromised: Supabase → Settings → API

#### Issue: Slow OCR Processing (> 10 second timeout)

**Cause**: Image too large or OCR processing slow

**Solution**:
1. Compress image before upload (< 500KB)
2. Optimize OCR: Use Tesseract with language hints
3. Consider async processing with job queue (future enhancement)

#### Issue: Out of Memory (Function exceeded 128MB)

**Cause**: Loading too much data or memory leak

**Solution**:
1. Reduce embeddings batch size
2. Stream large responses
3. Profile memory usage with `/metrics` endpoint
4. Upgrade to Pro tier if necessary

### Debug Mode (Temporary)

For troubleshooting, enable debug logging temporarily:

1. Vercel Dashboard → Environment Variables
2. Set: `DEBUG=true` and `LOG_LEVEL=DEBUG`
3. Redeploy
4. Check logs for detailed information
5. **Important**: Disable before committing to production!

### Useful Commands

```bash
# View recent deployments
vercel list

# View specific deployment logs
vercel logs [deployment-url]

# Real-time logs
vercel logs --follow

# View environment variables (non-secret)
vercel env list

# Check build configuration
vercel inspect [deployment-url]
```

---

## Rollback Procedures

### Immediate Rollback (< 5 minutes)

1. **Vercel Dashboard** → **Deployments**
2. Find previous stable deployment
3. Click **"Redeploy"**
4. Wait for new deployment to complete
5. Verify health check

### Partial Rollback (Database only)

If database migration caused issues:

1. **Supabase Dashboard** → **SQL Editor**
2. Run rollback SQL:
   ```sql
   -- Reverse migration
   DROP TABLE IF EXISTS new_table;
   ALTER TABLE backup_table RENAME TO ingredients_library;
   ```

### Full Rollback Procedure

1. **Stop current deployment**:
   - Vercel Dashboard → Settings → Deployments
   - Unlink GitHub temporarily

2. **Revert Git commit**:
   ```bash
   git revert HEAD
   git push origin main
   ```

3. **Redeploy from previous commit**:
   - Link GitHub again
   - Vercel auto-deploys from latest commit

### Backup Strategy

Before deploying major changes:

```bash
# Backup Supabase
pg_dump -U postgres postgresql://...supabase.co:5432/postgres > backup.sql

# Store securely
gsutil cp backup.sql gs://your-backup-bucket/backup-$(date +%Y%m%d).sql
```

---

## Production Checklist

### Pre-Deployment ✓

- [ ] All tests passing locally (`pytest -v`)
- [ ] No linting errors (`pylint backend/`)
- [ ] Environment variables documented
- [ ] Secrets never committed to Git
- [ ] Git history clean and descriptive
- [ ] Database migrations tested locally
- [ ] Supabase account set up and funded
- [ ] OpenAI API key verified working
- [ ] Vercel project created and configured
- [ ] GitHub repository linked
- [ ] Sentry project created (optional)

### Deployment ✓

- [ ] Vercel secrets configured correctly
- [ ] CORS origins updated for production frontend
- [ ] Build completes without errors
- [ ] No warnings in deployment logs
- [ ] Health check endpoint responding

### Post-Deployment ✓

- [ ] Health check (`/health`) returns 200
- [ ] Readiness check (`/ready`) returns true
- [ ] Frontend can successfully call backend
- [ ] Scan endpoint processes images correctly
- [ ] Vector search returns results
- [ ] Errors appear in Sentry dashboard (if enabled)
- [ ] No unexpected error messages in logs
- [ ] Database connection pool monitored
- [ ] Performance within acceptable thresholds

### Ongoing Monitoring ✓

- [ ] Set up daily health check alerts
- [ ] Monitor error rates in Sentry
- [ ] Review function execution times weekly
- [ ] Check Supabase connection metrics
- [ ] Monitor OpenAI API usage/costs
- [ ] Review Vercel build times trending
- [ ] Rotate secrets quarterly
- [ ] Run security audit monthly

---

## Cost Estimation

### Free Tier Costs

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Vercel Functions | 100GB bandwidth, unlimited invocations | $0 |
| Supabase | 500MB database, 2GB bandwidth | $0 |
| OpenAI API | Pay-as-you-go | $2-10* |
| Sentry | 5,000 errors/month | $0 |
| **Total** | | **$2-10** |

*Depends on scan volume (1 scan ≈ $0.01 with embeddings)

### Pro Tier Scaling

When you outgrow free tier:

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Vercel | Pro | $20 |
| Supabase | Pro | $25 |
| OpenAI | Usage-based | $50-100+ |
| Sentry | Team | $29/month |
| **Total** | | **$124-174+** |

---

## Support & Documentation

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Supabase Docs**: https://supabase.com/docs
- **OpenAI API**: https://platform.openai.com/docs
- **Sentry Docs**: https://docs.sentry.io

---

**Last Updated**: 2026-01-31
**Version**: 1.0
