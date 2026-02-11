# DevSEO Frontend-Backend Integration Checklist

**Last Updated:** February 11, 2026
**Status:** Ready for Integration

---

## ✅ Pre-Integration Checklist

### Backend Setup
- [x] Backend running on http://localhost:8000
- [x] Database migrations applied
- [x] All API endpoints implemented
- [x] CORS configured for frontend URLs
- [x] API documentation available at /docs
- [x] Health endpoint responding
- [x] Clerk authentication configured

### Frontend Setup
- [ ] Frontend running (Lovable building)
- [ ] React Router configured
- [ ] Clerk SDK installed
- [ ] React Query (TanStack Query) setup
- [ ] Environment variables configured
- [ ] API client created

---

## 🔌 Integration Steps

### Step 1: Environment Setup (15 minutes)

**Backend `.env` file:**
```bash
# Already configured ✅
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
CLERK_SECRET_KEY=sk_test_...
DEBUG=True
```

**Frontend `.env.local` file:**
```bash
# Create this in insight-navigator repo
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

**Get Clerk Keys:**
1. Go to https://dashboard.clerk.com
2. Select your project
3. Go to API Keys
4. Copy:
   - Publishable Key → Frontend `.env.local`
   - Secret Key → Backend `.env`

---

### Step 2: Test Backend (5 minutes)

**Start Backend:**
```bash
cd C:\Users\User\devseo\backend
venv\Scripts\activate
python -m app.main
```

**Verify:**
- [ ] Backend starts without errors
- [ ] See: "Application startup complete"
- [ ] Visit: http://localhost:8000/docs
- [ ] API documentation loads

**Test Health Endpoint:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T...",
  "version": "1.0.0"
}
```

---

### Step 3: Test Frontend (5 minutes)

**Wait for Lovable to finish building**, then:

**Clone Frontend Repo (if not done):**
```bash
cd C:\Users\User
git clone https://github.com/kurdim12/insight-navigator.git
cd insight-navigator
```

**Install Dependencies:**
```bash
npm install
```

**Create `.env.local`:**
```bash
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

**Start Frontend:**
```bash
npm run dev
```

**Verify:**
- [ ] Frontend starts on http://localhost:5173
- [ ] No console errors
- [ ] App loads in browser

---

### Step 4: Test CORS (5 minutes)

**Open browser console on http://localhost:5173**

**Test 1: Health Endpoint (No Auth)**
```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

**Expected:** No CORS errors, see `{ status: "healthy" }`

**If CORS Error:**
1. Check backend is running
2. Check backend/app/config.py CORS_ORIGINS includes "http://localhost:5173"
3. Restart backend

---

### Step 5: Test Authentication (10 minutes)

**Sign up in Frontend:**
1. Click Sign Up
2. Create test account
3. Verify Clerk login works

**Get Auth Token in Console:**
```javascript
// In browser console
const token = await window.Clerk.session.getToken()
console.log(token)
```

**Test Authenticated Endpoint:**
```javascript
const token = await window.Clerk.session.getToken()

fetch('http://localhost:8000/api/v1/websites', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(r => r.json())
  .then(console.log)
```

**Expected:**
- No CORS errors
- Returns empty array `[]` (no websites yet)
- Status 200

**If 401 Error:**
- Check CLERK_SECRET_KEY in backend/.env
- Restart backend
- Check token is being sent

---

### Step 6: Test Create Website (10 minutes)

**In Frontend UI:**
1. Click "Add Website" button
2. Enter URL: `https://example.com`
3. Click Submit

**Or via Console:**
```javascript
const token = await window.Clerk.session.getToken()

fetch('http://localhost:8000/api/v1/websites', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ url: 'https://example.com' })
})
  .then(r => r.json())
  .then(console.log)
```

**Expected:**
```json
{
  "id": "uuid-here",
  "url": "https://example.com",
  "domain": "example.com",
  "verified": false,
  "created_at": "..."
}
```

**Check Database:**
```bash
# In backend terminal
python
>>> from app.database import get_db
>>> # Website should be in database
```

---

### Step 7: Test Start Scan (10 minutes)

**Get Website ID from previous step**

**Start Scan via Console:**
```javascript
const token = await window.Clerk.session.getToken()
const websiteId = 'uuid-from-previous-step'

fetch('http://localhost:8000/api/v1/crawls', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    website_id: websiteId,
    max_pages: 10
  })
})
  .then(r => r.json())
  .then(console.log)
```

**Expected:**
```json
{
  "id": "scan-uuid",
  "status": "pending",
  "message": "Scan started successfully"
}
```

**Monitor Scan Progress:**
```javascript
const scanId = 'scan-uuid-from-above'
const token = await window.Clerk.session.getToken()

// Poll every 3 seconds
setInterval(async () => {
  const res = await fetch(`http://localhost:8000/api/v1/crawls/${scanId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  const data = await res.json()
  console.log('Status:', data.status, 'Score:', data.seo_score)
}, 3000)
```

**Expected:**
- Status changes: pending → running → completed
- SEO score appears when completed
- Pages scanned count increases

---

### Step 8: Test Content Optimizer (5 minutes)

**In Frontend or Console:**
```javascript
const token = await window.Clerk.session.getToken()

fetch('http://localhost:8000/api/v1/content/optimize', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'This is a short article about SEO. SEO is important for websites.',
    target_keyword: 'SEO'
  })
})
  .then(r => r.json())
  .then(console.log)
```

**Expected:**
- 3 title suggestions
- Meta description
- Readability score
- Keyword density analysis

---

### Step 9: Test Domain Verification (5 minutes)

**Get Verification Token:**
```javascript
const token = await window.Clerk.session.getToken()
const websiteId = 'your-website-uuid'

const res = await fetch(`http://localhost:8000/api/v1/websites/${websiteId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
})
const website = await res.json()
console.log('Verification Token:', website.verification_token)
```

**Test Verification (will fail for example.com, that's OK):**
```javascript
const token = await window.Clerk.session.getToken()

fetch(`http://localhost:8000/api/v1/websites/${websiteId}/verify`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ method: 'dns' })
})
  .then(r => r.json())
  .then(console.log)
```

**Expected:**
```json
{
  "verified": false,
  "message": "DNS verification failed...",
  "instructions": "Add TXT record..."
}
```

---

## 🧪 Frontend-Specific Tests

### React Query Integration

**Check in DevTools:**
1. Open React Query DevTools
2. See queries: `['websites']`, `['scans']`, etc.
3. Check cache status
4. Verify refetching works

### UI Component Tests

**Dashboard:**
- [ ] Stats cards display correctly
- [ ] Website count shows
- [ ] Recent scans table loads
- [ ] "Add Website" button works

**Websites Page:**
- [ ] Website list displays
- [ ] Add website form works
- [ ] Delete website works
- [ ] Verification status shows

**Scan Report:**
- [ ] SEO score displays prominently
- [ ] Issues list shows
- [ ] Plain English toggle works
- [ ] Readability score displays
- [ ] Pages table loads

**Content Optimizer:**
- [ ] Text input works
- [ ] URL input works
- [ ] Results display correctly
- [ ] Copy buttons work

**Settings:**
- [ ] Language switcher works (EN/AR)
- [ ] Report mode toggle saves
- [ ] Email preferences save

---

## 🚨 Common Issues & Solutions

### Issue: CORS Error
**Symptom:** "Access-Control-Allow-Origin" error in console
**Solution:**
1. Check backend is running
2. Verify CORS_ORIGINS includes frontend URL
3. Restart backend after CORS changes

### Issue: 401 Unauthorized
**Symptom:** All API calls return 401
**Solution:**
1. Check Clerk token is being sent
2. Verify CLERK_SECRET_KEY in backend .env
3. Check token format: `Bearer <token>`
4. Ensure user is logged in

### Issue: Scan Stays "Running"
**Symptom:** Scan status never changes to completed
**Solution:**
1. Check backend console for errors
2. Verify crawler is running (BackgroundTasks)
3. Check target website is accessible
4. Look for Python errors

### Issue: Frontend Can't Connect
**Symptom:** Network errors, "Failed to fetch"
**Solution:**
1. Verify backend is running on port 8000
2. Check VITE_API_URL in frontend .env.local
3. Try: `curl http://localhost:8000/health`
4. Restart both backend and frontend

### Issue: Database Errors
**Symptom:** 500 errors, "database" in error message
**Solution:**
1. Check DATABASE_URL is correct
2. Run migrations: `alembic upgrade head`
3. Verify PostgreSQL is running
4. Check database exists

---

## 📊 Integration Success Criteria

### All Green ✅ Means Ready!

**Authentication:**
- [x] User can sign up with Clerk
- [x] User can log in
- [x] JWT token sent to backend
- [x] Backend validates token

**Websites:**
- [ ] User can add website
- [ ] User can view website list
- [ ] User can delete website
- [ ] Domain verification works (shows instructions)

**Scans:**
- [ ] User can start scan
- [ ] Scan progresses (pending → running → completed)
- [ ] Results display correctly
- [ ] SEO score shows
- [ ] Issues list populates

**Content Optimizer:**
- [ ] User can input text or URL
- [ ] Results return quickly
- [ ] Title suggestions display
- [ ] Readability score shows

**UI/UX:**
- [ ] No console errors
- [ ] Loading states show
- [ ] Error messages display
- [ ] Success toasts work
- [ ] Mobile responsive

**Performance:**
- [ ] API responses < 1s
- [ ] Page loads < 3s
- [ ] No memory leaks
- [ ] Smooth animations

---

## 🎯 Next Steps After Integration

### Week 2 Tasks:
1. **Arabic Language Support**
   - Add next-intl
   - Create translations
   - Test RTL layout

2. **Polish & Bug Fixes**
   - Fix any integration bugs
   - Improve error handling
   - Add loading skeletons

3. **Advanced Features**
   - Scheduled scans
   - Email notifications
   - PDF reports

4. **Testing**
   - End-to-end tests
   - User acceptance testing
   - Performance testing

---

## 📞 Get Help

**Backend Issues:**
- Check backend console
- Look at `backend/logs/` (if logging enabled)
- Visit http://localhost:8000/docs for API testing

**Frontend Issues:**
- Check browser console
- Check Network tab for API calls
- Use React DevTools
- Use React Query DevTools

**Integration Issues:**
- Verify both services running
- Check CORS configuration
- Verify authentication flow
- Test endpoints in Postman first

---

## 🎉 Integration Complete!

When all checklist items are ✅:

1. **Commit Both Repos:**
   ```bash
   # Backend
   cd devseo
   git add -A
   git commit -m "feat: Integration-ready backend"
   git push

   # Frontend
   cd insight-navigator
   git add -A
   git commit -m "feat: Backend integration complete"
   git push
   ```

2. **Document Issues:**
   - Create GitHub issues for bugs
   - Tag them: `integration`, `bug`, `enhancement`

3. **Plan Next Sprint:**
   - Arabic language support
   - Payment system
   - Advanced features

4. **Celebrate! 🎊**
   - You've connected frontend to backend
   - Full-stack app is working
   - Ready for feature development

---

**Last Updated:** February 11, 2026
**Integration Status:** Ready to Test
**Next Review:** After Lovable finishes building
