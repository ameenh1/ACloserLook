# Vercel Secrets Setup - Required for CI/CD Pipeline

This guide explains how to configure GitHub Actions secrets for the automated deployment pipeline.

## GitHub Repository Secrets

Go to **GitHub Repository → Settings → Secrets and variables → Actions** and add:

### 1. Vercel Authentication

#### `VERCEL_TOKEN`
**Purpose**: Authenticate with Vercel API for deployments

**How to get**:
1. Go to https://vercel.com/account/tokens
2. Click **"Create"** 
3. Name: `GitHub Actions`
4. Scope: Full Account
5. Copy token
6. Add to GitHub Secrets

#### `VERCEL_ORG_ID`
**Purpose**: Identify your Vercel organization

**How to get**:
1. Go to https://vercel.com/dashboard/settings/general
2. Find **"Team ID"** (or **"Org ID"**)
3. Copy the value
4. Add to GitHub Secrets

#### `VERCEL_PROJECT_ID`
**Purpose**: Identify your Vercel project (production backend)

**How to get**:
1. Go to https://vercel.com/dashboard
2. Click on backend project
3. Go to **Settings → General**
4. Find **"Project ID"**
5. Copy the value
6. Add to GitHub Secrets

#### `VERCEL_PROJECT_ID_PREVIEW`
**Purpose**: Identify your Vercel preview project (optional, for develop branch)

**How to get**:
1. Same as `VERCEL_PROJECT_ID` but for a separate preview project
2. Or use same ID if you only have one project
3. Add to GitHub Secrets

#### `VERCEL_DEPLOYMENT_URL`
**Purpose**: URL to check health after deployment

**Example**: `lotus-backend.vercel.app` (without `https://`)

### 2. Supabase (Testing)

For running tests with real Supabase connection:

#### `SUPABASE_URL_TEST`
**Purpose**: Supabase project URL for tests

**How to get**:
1. Go to https://app.supabase.com/project/[id]/settings/api
2. Copy **Project URL**
3. Add to GitHub Secrets

#### `SUPABASE_KEY_TEST`
**Purpose**: Supabase anon key for tests

**How to get**:
1. Go to https://app.supabase.com/project/[id]/settings/api
2. Copy **anon public** key
3. Add to GitHub Secrets

#### `SUPABASE_SERVICE_ROLE_KEY_TEST`
**Purpose**: Supabase service role key for tests

**How to get**:
1. Go to https://app.supabase.com/project/[id]/settings/api
2. Copy **service_role** key
3. Add to GitHub Secrets

### 3. OpenAI API

#### `OPENAI_API_KEY_TEST`
**Purpose**: OpenAI key for tests (use separate testing key with low limits)

**How to get**:
1. Go to https://platform.openai.com/account/api-keys
2. Create new API key specifically for testing
3. Set usage limit: $1-5/month (in case of accidents)
4. Copy key
5. Add to GitHub Secrets

### 4. Optional: Notifications

#### `SLACK_WEBHOOK_URL` (Optional)
**Purpose**: Send deployment notifications to Slack

**How to set up**:
1. Go to https://api.slack.com/apps
2. Create New App → From scratch
3. Name: "Lotus Deployments"
4. Workspace: Your workspace
5. Go to **Incoming Webhooks**
6. Click **"Add New Webhook to Workspace"**
7. Select channel: #deployments (or create new)
8. Copy **Webhook URL**
9. Add to GitHub Secrets

---

## Complete Secrets Checklist

```markdown
### GitHub Secrets Configuration

#### Vercel Authentication (REQUIRED)
- [ ] VERCEL_TOKEN
- [ ] VERCEL_ORG_ID
- [ ] VERCEL_PROJECT_ID
- [ ] VERCEL_PROJECT_ID_PREVIEW
- [ ] VERCEL_DEPLOYMENT_URL

#### Testing Services (REQUIRED)
- [ ] SUPABASE_URL_TEST
- [ ] SUPABASE_KEY_TEST
- [ ] SUPABASE_SERVICE_ROLE_KEY_TEST
- [ ] OPENAI_API_KEY_TEST

#### Notifications (OPTIONAL)
- [ ] SLACK_WEBHOOK_URL
```

---

## Verify Secrets Configuration

After adding all secrets:

1. Go to **Repository Settings → Secrets and variables → Actions**
2. Verify all required secrets are listed (values hidden with ●●●●●●)
3. Check workflow file: `.github/workflows/vercel-deploy.yml` references correct secret names

---

## Secret Values Reference

| Secret | Format | Example |
|--------|--------|---------|
| `VERCEL_TOKEN` | Random string | `VercelAuthTokenHere...` |
| `VERCEL_ORG_ID` | Team ID | `team_abc123def456` |
| `VERCEL_PROJECT_ID` | Project ID | `prj_xyz789abc123` |
| `VERCEL_DEPLOYMENT_URL` | Domain | `lotus-backend.vercel.app` |
| `SUPABASE_URL_TEST` | URL | `https://abc123.supabase.co` |
| `SUPABASE_KEY_TEST` | Base64 string | `eyJhbGciOiJIUzI1NiIs...` |
| `OPENAI_API_KEY_TEST` | Prefixed string | `sk-proj-...` |
| `SLACK_WEBHOOK_URL` | URL | `https://hooks.slack.com/...` |

---

## Test the Pipeline

After setting up secrets:

1. **Push to a branch**:
   ```bash
   git add .
   git commit -m "Test CI/CD pipeline"
   git push origin main
   ```

2. **Monitor GitHub Actions**:
   - Go to **Repository → Actions**
   - Watch workflow run
   - Check logs for errors

3. **Common issues**:
   - ❌ `VERCEL_TOKEN: not found` → Check secret name exactly
   - ❌ `401 Unauthorized` → Token expired, regenerate
   - ❌ Tests fail → Check Supabase test connection

---

## Security Best Practices

1. **Never log secrets** - GitHub Actions automatically redacts them
2. **Rotate tokens** quarterly
3. **Use separate test keys** - Never use production keys in tests
4. **Limit scope** - Only grant necessary permissions
5. **Review access** - Regularly check who has repository access
6. **Audit logs** - Monitor deployment history

---

## Troubleshooting

### Secret not found in workflow

**Error**:
```
Unrecognized named-value: 'secrets.VERCEL_TOKEN'
```

**Solution**:
1. Check spelling: `VERCEL_TOKEN` (case-sensitive)
2. Verify in GitHub Settings → Secrets
3. Redeploy workflow

### Tests fail with "Connection refused"

**Cause**: Supabase test credentials invalid

**Solution**:
1. Verify Supabase project is running
2. Check credentials are current (not rotated)
3. Test locally first: `python -m pytest`

### Deployment succeeds but health check fails

**Cause**: Backend not responding on `/health` endpoint

**Solution**:
1. Check Vercel logs for errors
2. Verify environment variables set in Vercel
3. Manually test: `curl https://your-domain.vercel.app/health`

---

**Last Updated**: 2026-01-31
