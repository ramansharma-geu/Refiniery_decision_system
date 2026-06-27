# VERCEL_DEPLOYMENT.md

## Vercel Deployment Guide

### Prerequisites

- GitHub repository with RDIS code
- Vercel account (free tier available)
- Node.js installed (for Vercel CLI)

### Step 1: Prepare Repository

Ensure your repository has:
- `vercel.json` (already created)
- `requirements.txt` (already created)
- `app.py` (main entry point)

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Production ready RDIS"
git push origin main
```

### Step 3: Import to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the Python project

### Step 4: Configure Environment Variables

In Vercel dashboard, go to Settings > Environment Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | (generate a secure random string) |
| `DATABASE_URL` | `sqlite:///refinery.db` |
| `LLM_PROVIDER` | `mock` |
| `OLLAMA_URL` | (if using Ollama) |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` |

### Step 5: Deploy

Click "Deploy" and wait for build to complete.

### Step 6: Verify

1. Open the deployed URL
2. Test all features
3. Check health endpoint: `/api/health`

### Limitations

- SQLite database is ephemeral (resets on redeploy)
- For persistent data, use external database (PostgreSQL)
- Serverless functions have cold start latency

### Alternative: Persistent Database

For persistent data, use:
- Vercel Postgres
- Supabase
- PlanetScale

Update `DATABASE_URL` accordingly.

## Vercel Configuration

The `vercel.json` file configures:
- Python runtime for backend
- Static file serving for frontend
- Route handling

## Troubleshooting

### Build Errors
- Check `requirements.txt` has all dependencies
- Ensure Python 3.11+ is specified

### Runtime Errors
- Check environment variables are set
- Verify database file exists

### Cold Starts
- First request may be slower
- Subsequent requests are faster
