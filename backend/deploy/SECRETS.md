# Secrets Management Guide - Lotus Backend

## Overview

This guide explains how to securely manage sensitive information (API keys, database credentials) for production deployment on Vercel.

**Golden Rule**: Never commit secrets to Git. Always use Vercel's Environment Variables feature.

---

## What Are Secrets?

Secrets are sensitive credentials that must not be exposed publicly:

| Secret | Example | Risk |
|--------|---------|------|
| `OPENAI_API_KEY` | `sk-...` | $$ Cost if exposed; API abuse |
| `SUPABASE_KEY` | `eyJhbGciOi...` | Database access; data theft |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOi...` | Full database control |
| `SENTRY_DSN` | `https://xxx@sentry.io/yyy` | Project insights exposed |

---

## Secure Secrets Workflow

### Development Locally

**1. Create local `.env` file (NEVER commit to Git)**

```bash
cd backend
cat > .env << 'EOF'
SUPABASE_URL=your-dev-supabase-url
SUPABASE_KEY=your-dev-supabase-key
OPENAI_API_KEY=sk-your-dev-key
ENVIRONMENT=development
EOF
```

**2. Add `.env` to `.gitignore`**

```bash
# In .gitignore
.env
.env.local
.env.*.local
*.key
*.pem
```

Verify it's ignored:
```bash
git check-ignore .env
# Output: .env (if properly ignored)
```

**3. Load secrets when running locally**

```bash
# Backend automatically loads from .env
python -m uvicorn main:app --reload

# Or explicitly:
export $(cat .env | xargs) && python -m uvicorn main:app --reload
```

---

### Production on Vercel

**1. Never commit `.env` to GitHub**

Verify before pushing:
```bash
# Check git staging area
git status

# Make sure .env is NOT listed
# If it is, remove it:
git rm --cached .env
git add .gitignore
git commit -m "Remove .env from repo"
```

**2. Add secrets to Vercel Dashboard**

Go to Vercel → Project Settings → Environment Variables

For each secret:
1. Click **"Add New"**
2. **Name**: (e.g., `OPENAI_API_KEY`)
3. **Value**: (e.g., `sk-your-api-key`)
4. **Select Environments**: Check `Production`
5. Click **"Save"**

**Example - Adding OPENAI_API_KEY:**

```
Name: OPENAI_API_KEY
Value: sk-proj-xxxxxxx...
Environments: [✓] Production [ ] Preview [ ] Development
Click: Save
```

**3. Redeploy to apply changes**

```bash
# Trigger redeploy in Vercel Dashboard
# Or via Git:
git commit --allow-empty -m "Trigger Vercel redeploy with secrets"
git push origin main
```

---

## Setting Up Each Service's Secrets

### OpenAI API Key

**Where to get it:**
1. Go to https://platform.openai.com/account/api-keys
2. Click **"+ Create new secret key"**
3. Copy the key (won't be shown again)
4. Click **"Reveal"** if needed

**Security best practices:**
- Rotate every 3 months
- Use separate keys for dev/prod
- Set usage limits: https://platform.openai.com/account/billing/limits
- Monitor usage: https://platform.openai.com/account/billing/overview

**To rotate:**
```bash
# 1. Generate new key in OpenAI dashboard
# 2. Update Vercel Environment Variable with new key
# 3. Keep old key for 24 hours in case of issues
# 4. Verify new key works in production
# 5. Delete old key
```

### Supabase Credentials

**Where to get them:**

1. Go to https://app.supabase.com/project/[project-id]/settings/api
2. Find:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_KEY`
   - `service_role` → `SUPABASE_SERVICE_ROLE_KEY`

**Keys explained:**

| Key | Scope | Use Case |
|-----|-------|----------|
| `SUPABASE_KEY` (anon) | Limited by RLS | Frontend, public queries |
| `SUPABASE_SERVICE_ROLE_KEY` | Full database access | Backend only, migrations |

**Security best practices:**
- Never expose `SERVICE_ROLE_KEY` to frontend
- Use RLS (Row Level Security) policies
- Rotate keys if compromised
- Monitor access logs

**To rotate Supabase keys:**
1. Go to Supabase Dashboard → Settings → API
2. Click **"Rotate keys"** next to each key
3. New keys generated
4. Update Vercel environment variables
5. Redeploy backend
6. Monitor for errors
7. If all good, old keys automatically revoked after 24h

---

## Emergency: Revoked or Exposed Secret

### If You Accidentally Commit a Secret to GitHub

⚠️ **Act immediately** (even if you delete the file in next commit):

1. **Revoke the secret immediately**:
   - OpenAI: Delete key at https://platform.openai.com/account/api-keys
   - Supabase: Rotate keys in Settings → API
   - Sentry: Regenerate DSN

2. **Remove from Git history** (if already pushed):
   ```bash
   # Option 1: Using git filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --replace-text <(echo "sk-your-old-key==>")
   
   # Option 2: Using BFG Repo-Cleaner
   bfg --replace-text .env
   
   # Force push (dangerous - only if solo project)
   git push --force-all
   ```

3. **Generate new secrets** with the service
4. **Update Vercel environment variables**
5. **Redeploy**

### If Someone Gets Your API Key

1. **Check usage**:
   - OpenAI: https://platform.openai.com/account/billing/overview
   - Supabase: Dashboard → Usage

2. **Revoke immediately**
3. **Generate new key**
4. **Update Vercel**
5. **Monitor for suspicious activity**
6. **If charged**: Contact support for refund

---

## Secrets Rotation Schedule

Implement this rotation schedule:

| Secret | Frequency | Reason |
|--------|-----------|--------|
| OpenAI API Key | Quarterly (90 days) | Best security practice |
| Supabase Keys | Quarterly | Best security practice |
| Database passwords | Annually | Compliance |
| Service tokens | As needed | After employee changes |

**Automated Rotation** (future):
- Set calendar reminders for rotation dates
- Document each rotation in shared spreadsheet
- Test new keys before revoking old ones

---

## Environment-Specific Secrets

### Development Secrets (Local `.env`)

```bash
SUPABASE_URL=http://localhost:54321  # Local Supabase
SUPABASE_KEY=eyJ...  # Dev key (lower security)
OPENAI_API_KEY=sk-dev-key-with-low-limits
ENVIRONMENT=development
```

### Staging Secrets (Vercel Preview)

```
SUPABASE_URL=https://staging-project.supabase.co
SUPABASE_KEY=staging-key
OPENAI_API_KEY=sk-staging-key-with-quotas
SENTRY_ENVIRONMENT=staging
```

### Production Secrets (Vercel Production)

```
SUPABASE_URL=https://production-project.supabase.co
SUPABASE_KEY=prod-key-with-RLS
OPENAI_API_KEY=sk-prod-key-with-strict-limits
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
```

---

## Accessing Secrets in Code

### How Backend Accesses Secrets

**In `backend/config.py`:**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    SUPABASE_URL: str = Field(..., description="Supabase URL")
    
    class Config:
        env_file = ".env"  # Loads from .env locally
        # In Vercel, env vars come from environment automatically

# Usage
settings = Settings()
print(settings.OPENAI_API_KEY)  # Loaded from .env or Vercel env vars
```

### Development vs. Production

```python
# main.py
from config import settings

if settings.ENVIRONMENT == 'production':
    # Use production secrets
    openai_key = settings.OPENAI_API_KEY
    db_url = settings.SUPABASE_URL
else:
    # Use development secrets (from .env)
    openai_key = settings.OPENAI_API_KEY
    db_url = settings.SUPABASE_URL
```

---

## Monitoring Secret Usage

### Track API Usage

**OpenAI:**
- Monthly usage: https://platform.openai.com/account/billing/overview
- Set budget: https://platform.openai.com/account/billing/limits
- Get alerts at 50%, 80%, 100% of budget

**Supabase:**
- Dashboard → Usage → Real-time stats
- Check database connections
- Monitor storage usage

### Audit Logs

**Vercel audit logs:**
1. Team Settings → Audit Log
2. See all environment variable changes
3. Who changed what and when

**Supabase audit logs:**
1. Project → Logs → Postgres Logs
2. See database access
3. Find suspicious queries

---

## Secrets Checklist

### Local Development
- [ ] `.env` file created with all secrets
- [ ] `.env` added to `.gitignore`
- [ ] Never committed to Git
- [ ] Verified with `git check-ignore .env`

### Before Deploying to Vercel
- [ ] All secrets removed from code
- [ ] `.env` NOT in git staging area
- [ ] Verified: `git status` shows `.env` not listed
- [ ] Ready to push to GitHub

### Vercel Production Setup
- [ ] Vercel project created
- [ ] GitHub connected to Vercel
- [ ] All environment variables added to Vercel dashboard:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] `OPENAI_API_KEY`
  - [ ] `SENTRY_DSN` (if using)
- [ ] All marked for `Production` environment
- [ ] Backend redeployed with new secrets
- [ ] Health check passes
- [ ] No errors in Vercel logs

### Ongoing Maintenance
- [ ] Secrets rotation scheduled (quarterly)
- [ ] Audit logs reviewed monthly
- [ ] Usage limits set on all APIs
- [ ] Alerts configured for suspicious activity
- [ ] Team notified of secret rotation dates

---

## Troubleshooting

### Issue: "Environment variable not found"

**Symptom:**
```
Error: OPENAI_API_KEY environment variable not found
```

**Solution:**
1. Check Vercel Dashboard → Environment Variables
2. Verify variable name exactly (case-sensitive)
3. Ensure marked for `Production` environment
4. Redeploy: `git commit --allow-empty -m "Redeploy" && git push`

### Issue: Wrong secret loaded locally

**Symptom:**
```
Using production API key in development (wrong!)
```

**Solution:**
1. Check `.env` file has dev keys
2. Verify `.env` in same directory as config.py
3. Restart Python process: `Ctrl+C` then rerun
4. Check: `python -c "from config import settings; print(settings.OPENAI_API_KEY[:10])"`

### Issue: Secret changed but still using old value

**Symptom:**
```
OpenAI error: Invalid API key
```

**Solution:**
1. Verify new secret in Vercel dashboard
2. Wait 30 seconds for cache invalidation
3. Manually redeploy: Vercel Dashboard → Deployments → Redeploy
4. Clear any local caches: `vercel env pull`

---

## References

- **OpenAI API Keys**: https://platform.openai.com/account/api-keys
- **Supabase API Settings**: https://app.supabase.com/project/[id]/settings/api
- **Vercel Environment Variables**: https://vercel.com/docs/environment-variables
- **git-filter-repo**: https://github.com/newren/git-filter-repo

---

**Last Updated**: 2026-01-31
**Lotus Backend Version**: 0.1.0
