# DevSEO Deployment Guide

**Last Updated:** February 11, 2026

This guide covers deploying both frontend and backend of the DevSEO platform.

---

## 🎯 Quick Summary

- **Frontend**: Already auto-deploys via Lovable from GitHub
- **Backend**: Can deploy to Render, Railway, or Vercel
- **Database**: PostgreSQL (managed service recommended)
- **Redis**: Required for caching and Celery

---

## 📦 Frontend Deployment (Lovable)

### Status: ✅ Already Configured

The frontend repository (insight-navigator) is connected to Lovable and auto-deploys on every push to `main`.

**Repository:** https://github.com/kurdim12/insight-navigator.git

### How It Works

1. Push changes to `main` branch
2. Lovable detects the push
3. Builds the React/Vite project
4. Deploys automatically
5. Live at: `https://insight-navigator.lovable.app`

### Environment Variables (Set in Lovable Dashboard)

```bash
VITE_API_URL=https://your-backend-api.onrender.com
VITE_CLERK_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
```

**Important:** Update `VITE_API_URL` after backend deployment!

---

## 🚀 Backend Deployment

### Option 1: Render (Recommended) ⭐

**Why Render:**
- Free tier available
- Auto-deploys from GitHub
- Managed PostgreSQL included
- Easy environment variables
- Built-in health checks

#### Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect to GitHub: `kurdim12/DEV-SEO`
   - Select the repository

3. **Configure Service**
   - Name: `devseo-api`
   - Region: Oregon (or closest to you)
   - Branch: `main`
   - Root Directory: `backend`
   - Environment: Python 3
   - Build Command: `./build.sh`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free

4. **Add Environment Variables**

   Required:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/devseo
   REDIS_URL=redis://host:6379
   SECRET_KEY=your-secret-key-here
   CLERK_SECRET_KEY=sk_live_YOUR_KEY
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY
   ENVIRONMENT=production
   ```

   Optional:
   ```bash
   SENTRY_DSN=https://your-sentry-dsn
   STRIPE_SECRET_KEY=sk_live_YOUR_KEY
   SENDGRID_API_KEY=SG.YOUR_KEY
   AWS_ACCESS_KEY_ID=YOUR_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_SECRET
   ```

5. **Create PostgreSQL Database**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Name: `devseo-db`
   - Plan: Free
   - Copy the "Internal Database URL"
   - Paste into web service as `DATABASE_URL`

6. **Create Redis Instance**
   - In Render dashboard: "New +" → "Redis"
   - Name: `devseo-redis`
   - Plan: Free
   - Copy the "Internal Redis URL"
   - Paste into web service as `REDIS_URL`

7. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - First deploy takes ~5-10 minutes

8. **Verify Deployment**
   - Visit: `https://devseo-api.onrender.com/health`
   - Should return: `{"status": "healthy"}`
   - API docs: `https://devseo-api.onrender.com/docs`

#### Using render.yaml (Alternative)

If you prefer infrastructure-as-code:

1. The `render.yaml` file is already in the repo
2. In Render: "New +" → "Blueprint"
3. Connect to your repo
4. Render reads `render.yaml` and creates all services
5. Set environment variables manually after creation

---

### Option 2: Railway

**Why Railway:**
- Simple deployment
- Good free tier
- PostgreSQL + Redis included
- Git-based deploys

#### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Deploy from Backend Directory**
   ```bash
   cd backend
   railway init
   railway up
   ```

4. **Add PostgreSQL**
   ```bash
   railway add --postgres
   ```

5. **Add Redis**
   ```bash
   railway add --redis
   ```

6. **Set Environment Variables**
   ```bash
   railway variables set SECRET_KEY="your-secret"
   railway variables set CLERK_SECRET_KEY="sk_live_..."
   railway variables set ANTHROPIC_API_KEY="sk-ant-..."
   railway variables set ENVIRONMENT="production"
   ```

7. **Get Public URL**
   ```bash
   railway domain
   ```

---

### Option 3: Vercel (API Routes Only)

**Note:** Vercel is serverless, so Celery workers won't work. Use for API-only deployment.

#### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd backend
   vercel --prod
   ```

3. **Set Environment Variables**
   - In Vercel dashboard: Settings → Environment Variables
   - Add all required variables

**Limitation:** No background tasks (Celery). For full functionality, use Render or Railway.

---

## 🔧 Post-Deployment Setup

### 1. Run Database Migrations

Migrations should run automatically via `build.sh`, but if needed manually:

**Render:**
- Go to service → Shell tab
- Run: `python -m alembic upgrade head`

**Railway:**
```bash
railway run python -m alembic upgrade head
```

### 2. Update Frontend Environment Variables

In Lovable dashboard, update:
```bash
VITE_API_URL=https://your-actual-backend-url.onrender.com
```

### 3. Test the Connection

1. Visit frontend: `https://insight-navigator.lovable.app`
2. Open browser console
3. Try adding a website
4. Check Network tab for API calls
5. Verify requests go to production backend

### 4. Set Up Celery Workers (Optional)

For background tasks (scheduled scans, email notifications):

**Render:**
- Create new "Background Worker" service
- Same repo, same environment variables
- Start command: `celery -A app.celery_app worker --loglevel=info`

**Railway:**
- Create new service from same repo
- Set start command to Celery worker command

### 5. Set Up Celery Beat (Optional)

For scheduled tasks:

**Render:**
- Create another "Background Worker" service
- Start command: `celery -A app.celery_app beat --loglevel=info`

**Railway:**
- Create another service
- Set start command to Celery beat command

---

## 🧪 Testing Production Deployment

### Backend Health Check

```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### API Documentation

Visit: `https://your-backend-url.onrender.com/docs`

### Test API Endpoints

```bash
# Test website creation (requires auth token)
curl -X POST https://your-backend-url.onrender.com/api/v1/websites \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Frontend Integration Test

1. Sign up at frontend
2. Add a website
3. Start a scan
4. Check browser Network tab
5. Verify API calls succeed

---

## 🐛 Troubleshooting

### Build Fails on Render

**Error:** "Exited with status 1"

**Possible causes:**
1. Missing system dependencies (weasyprint requires libpango, etc.)
2. Python version mismatch
3. Database connection issues during build

**Solutions:**
- Check Render logs: Service → Logs
- Verify `Dockerfile` has all system dependencies
- Ensure `build.sh` is executable: `chmod +x build.sh`
- Check `PYTHON_VERSION` environment variable

### Database Connection Failed

**Error:** "Could not connect to database"

**Solutions:**
- Verify `DATABASE_URL` is set correctly
- Check database is running
- Ensure database allows connections from web service
- For Render: Use "Internal Database URL" not "External"

### Redis Connection Failed

**Error:** "Could not connect to Redis"

**Solutions:**
- Verify `REDIS_URL` is set
- Check Redis instance is running
- For Render: Use "Internal Redis URL"

### CORS Errors in Frontend

**Error:** "Access-Control-Allow-Origin"

**Solutions:**
- Verify backend `config.py` has correct CORS origins
- Add frontend URL to `CORS_ORIGINS`
- Restart backend service

### Migrations Not Running

**Error:** "Table does not exist"

**Solutions:**
- SSH into service and run: `python -m alembic upgrade head`
- Check `build.sh` is executing
- Verify `DATABASE_URL` is available during build

### Frontend Not Updated

**Issue:** Changes not visible

**Solutions:**
- Verify changes pushed to GitHub: `git log origin/main`
- Check Lovable build logs
- Clear browser cache
- Try incognito/private browsing
- Wait 2-3 minutes for Lovable to rebuild

---

## 📊 Monitoring

### Application Logs

**Render:**
- Dashboard → Service → Logs
- Real-time log streaming
- Filter by severity

**Railway:**
```bash
railway logs
```

### Error Tracking (Sentry)

If `SENTRY_DSN` is set:
- Errors auto-reported to Sentry
- Visit: https://sentry.io
- View error traces and stack traces

### Database Monitoring

**Render:**
- Dashboard → PostgreSQL → Metrics
- Connection count, CPU, memory

**Railway:**
- Dashboard → PostgreSQL → Metrics

---

## 🔐 Security Checklist

### Before Going Live:

- [ ] Change all default secrets
- [ ] Use strong `SECRET_KEY` (32+ random chars)
- [ ] Enable HTTPS only
- [ ] Set `DEBUG=False` in production
- [ ] Restrict CORS to actual frontend domain
- [ ] Set up Sentry for error tracking
- [ ] Enable rate limiting (already configured)
- [ ] Review environment variables (no secrets in code)
- [ ] Set up database backups
- [ ] Configure Redis persistence

---

## 💰 Estimated Costs

### Free Tier (Good for MVP)

- **Frontend (Lovable):** $0 (auto-deploys)
- **Backend (Render):** $0 (free tier)
- **Database (Render):** $0 (free tier, 90 days then $7/month)
- **Redis (Render):** $0 (free tier, 90 days then $7/month)

**Total:** $0 for first 90 days, then ~$14/month

### Production Tier (Recommended)

- **Frontend (Lovable):** $0 (included)
- **Backend (Render):** $7/month (starter)
- **Database (Render):** $7/month (starter)
- **Redis (Render):** $7/month (starter)
- **Celery Worker:** $7/month (starter)

**Total:** ~$28/month

### Scaling

As you grow:
- Upgrade Render plans ($25, $85, custom)
- Add more workers
- Upgrade database storage
- Add CDN (Cloudflare free tier)

---

## 🎯 Next Steps After Deployment

1. **Monitor First Week**
   - Watch error logs
   - Check performance
   - Verify email delivery
   - Test all features

2. **Set Up Analytics**
   - Google Analytics
   - Mixpanel/PostHog for events
   - Sentry for errors

3. **User Testing**
   - Invite beta users
   - Collect feedback
   - Fix critical bugs

4. **Marketing**
   - Update landing page with real URL
   - Share on social media
   - Submit to directories

5. **Iterate**
   - Add missing features
   - Improve UI/UX based on feedback
   - Optimize performance

---

## 📞 Support

**Issues:** https://github.com/kurdim12/DEV-SEO/issues

**Deployment Platforms:**
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Lovable Support: support@lovable.dev

---

**Created:** February 11, 2026
**Status:** Ready for Production Deployment

Made with ❤️ for DevSEO
