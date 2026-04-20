# Deployment Guide: Cloud Run + Neon PostgreSQL

This guide walks through deploying your calendar application to Google Cloud Run with Neon PostgreSQL.

## Prerequisites

### 1. Google Cloud Account
- Create a free account at https://cloud.google.com
- Free tier includes: 2M Cloud Run requests/month, generous Cloud Build minutes

### 2. Install Google Cloud CLI

**macOS (using Homebrew):**
```bash
brew install --cask google-cloud-sdk
```

**Or download from:** https://cloud.google.com/sdk/docs/install

### 3. Verify Installation
```bash
gcloud --version
```

---

## Step 1: Google Cloud Setup

### 1.1 Authenticate
```bash
gcloud auth login
```
This opens a browser window to sign in with your Google account.

### 1.2 Create or Select Project
```bash
# Create a new project (replace PROJECT_ID with something unique)
gcloud projects create PROJECT_ID --name="Calendar App"

# Or list existing projects
gcloud projects list

# Set the project
gcloud config set project PROJECT_ID
```

**Example:**
```bash
gcloud projects create ahilbers-calendar --name="Calendar App"
gcloud config set project ahilbers-calendar
```

### 1.3 Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
```

This takes 1-2 minutes and enables:
- **Cloud Build** - builds your Docker container
- **Cloud Run** - hosts your application
- **Artifact Registry** - stores container images

---

## Step 2: Deploy to Cloud Run

### 2.1 Get Your Environment Variables

You'll need these values from your `.env` file:
- `FLASK_KEY` - your Flask secret key
- `DATABASE_URL` - your Neon PostgreSQL connection string

### 2.2 Deploy with Single Command

From your project directory, run:

```bash
gcloud run deploy calendar-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_KEY="YOUR_FLASK_KEY" \
  --set-env-vars DATABASE_URL="YOUR_DATABASE_URL"
```

**Replace:**
- `YOUR_FLASK_KEY` with your actual Flask key
- `YOUR_DATABASE_URL` with your Neon connection string

**Example:**
```bash
gcloud run deploy calendar-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_KEY="QSzNiKWBhyq61uaFVS98Q4JMpJpo_JzGo4Aw2i-riTEyLRaEBIJoqtHkWIIsUj0f" \
  --set-env-vars DATABASE_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
```

### 2.3 What Happens

1. **Uploads code** - sends your files to Cloud Build
2. **Builds container** - creates Docker image from your Dockerfile
3. **Pushes to registry** - stores image in Artifact Registry
4. **Deploys to Cloud Run** - launches your app
5. **Returns URL** - gives you public URL like `https://calendar-app-xxx.run.app`

**This takes 2-5 minutes on first deploy.**

### 2.4 Deployment Prompts

You may be asked:
- **Allow unauthenticated invocations?** → Yes (makes app public)
- **Region:** → us-central1 (or choose closest to your users)

---

## Step 3: Test Your Deployment

### 3.1 Get Your URL
After deployment completes, you'll see:
```
Service URL: https://calendar-app-xxxxx-uc.a.run.app
```

### 3.2 Test It
- Open the URL in your browser
- Add a person
- Add a trip
- Verify data persists after refresh
- **Share the URL** - anyone can access it now!

---

## Step 4: Make Updates

When you change your code:

```bash
gcloud run deploy calendar-app \
  --source . \
  --region us-central1
```

No need to re-specify environment variables - they persist between deployments.

---

## Common Commands

### View Deployment Info
```bash
gcloud run services describe calendar-app --region us-central1
```

### View Logs (Real-time)
```bash
gcloud run services logs tail calendar-app --region us-central1
```

### Delete Deployment
```bash
gcloud run services delete calendar-app --region us-central1
```

### Update Environment Variables
```bash
gcloud run services update calendar-app \
  --region us-central1 \
  --update-env-vars FLASK_KEY="new-key"
```

---

## Troubleshooting

### Build Fails
- Check Cloud Build logs: `gcloud builds list`
- View specific build: `gcloud builds log BUILD_ID`
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Syntax errors in code
  - Dockerfile errors

### App Crashes at Startup
- View logs: `gcloud run services logs tail calendar-app --region us-central1`
- Common issues:
  - Wrong DATABASE_URL format
  - Missing FLASK_KEY
  - Database connection errors

### 502 Bad Gateway
- Container not listening on correct port (should be 8080)
- App crashes on startup
- Check logs for details

### Environment Variables Not Working
- Verify they're set: `gcloud run services describe calendar-app --region us-central1`
- Re-deploy with correct values
- Check for quotes in connection string

---

## Cost Estimation

### Cloud Run (Free Tier: 2M requests/month)
- **Your usage:** ~100 requests/month → **FREE**
- After free tier: $0.40 per million requests
- Always-on small app: ~$5-10/month if you exceed free tier

### Neon PostgreSQL
- **Free tier:** 0.5GB storage, reasonable compute
- **Your usage:** ~10MB, minimal compute → **FREE**

### Total Expected Cost
**$0/month** if you stay within free tiers (very likely for hobby project)

---

## Security Notes

### Environment Variables
- Never commit `.env` to git (already in `.gitignore`)
- Environment variables in Cloud Run are encrypted at rest
- Only accessible to your Cloud Run service

### Database
- Neon uses SSL by default (`sslmode=require`)
- Connection encrypted in transit
- Keep DATABASE_URL secret

### Access Control
- App is currently public (`--allow-unauthenticated`)
- To restrict: remove this flag and use Cloud IAM

---

## Next Steps

✅ **You're live!** Your app is now accessible worldwide.

**Optional improvements:**
- Add custom domain (requires Google Cloud DNS)
- Set up monitoring/alerts
- Add CI/CD with GitHub Actions
- Increase Cloud Run resources if needed
- Add Redis for session storage

---

## Support

- **Cloud Run docs:** https://cloud.google.com/run/docs
- **Neon docs:** https://neon.tech/docs
- **View this project's code:** Check `Dockerfile`, `main.py`, `app_with_calendar.py`
