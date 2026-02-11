# DevSEO API Reference for Frontend Integration

**Backend Base URL (Development):** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs` (Interactive Swagger UI)
**API Version:** v1
**Prefix:** `/api/v1`

---

## 🔐 Authentication

All API endpoints (except health check) require authentication via Clerk.

**Headers Required:**
```typescript
{
  "Authorization": "Bearer <clerk_jwt_token>",
  "Content-Type": "application/json"
}
```

**Getting Token in Frontend (React):**
```typescript
import { useAuth } from '@clerk/clerk-react'

const { getToken } = useAuth()
const token = await getToken()
```

---

## 📍 API Endpoints

### 1. Health Check

**GET** `/health`

Check if backend is running.

**No authentication required**

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T...",
  "version": "1.0.0"
}
```

---

### 2. Websites Management

#### List Websites
**GET** `/api/v1/websites`

Get all websites for the authenticated user.

**Response:**
```typescript
interface Website {
  id: string              // UUID
  url: string             // e.g., "https://example.com"
  domain: string          // e.g., "example.com"
  user_id: string         // UUID
  verified: boolean       // Domain verification status
  verified_at: string | null
  verification_token: string
  created_at: string
  updated_at: string
}

// Response is array of Website objects
Website[]
```

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/websites
```

---

#### Create Website
**POST** `/api/v1/websites`

Add a new website to monitor.

**Request Body:**
```typescript
{
  "url": string  // Full URL, e.g., "https://example.com"
}
```

**Response:**
```typescript
Website  // Same structure as above
```

**Validation:**
- URL must be valid HTTP/HTTPS
- Domain must be unique per user
- Cannot add localhost or internal IPs

---

#### Get Website Details
**GET** `/api/v1/websites/{website_id}`

Get detailed information about a specific website.

**Parameters:**
- `website_id`: UUID of the website

**Response:**
```typescript
Website & {
  crawl_jobs: CrawlJob[]  // Array of scan results
}
```

---

#### Update Website
**PUT** `/api/v1/websites/{website_id}`

Update website details.

**Request Body:**
```typescript
{
  "url"?: string  // Optional
}
```

**Response:**
```typescript
Website
```

---

#### Delete Website
**DELETE** `/api/v1/websites/{website_id}`

Delete a website and all its scan data.

**Response:**
```json
{
  "message": "Website deleted successfully"
}
```

---

#### Verify Domain Ownership
**POST** `/api/v1/websites/{website_id}/verify`

Verify domain ownership using one of three methods.

**Request Body:**
```typescript
{
  "method": "dns" | "meta_tag" | "file"
}
```

**Response (Success):**
```json
{
  "verified": true,
  "message": "Domain verified successfully via DNS",
  "verified_at": "2026-02-11T..."
}
```

**Response (Failure):**
```json
{
  "verified": false,
  "message": "DNS verification failed: TXT record not found",
  "instructions": "Add the following TXT record to your DNS:\n..."
}
```

**Verification Methods:**

**1. DNS TXT Record:**
- Add TXT record: `_devseo-verify.example.com` with value: `{verification_token}`
- Or add to root domain: `example.com` TXT record

**2. Meta Tag:**
- Add to homepage `<head>`: `<meta name="devseo-verification" content="{verification_token}">`

**3. File Upload:**
- Upload file to: `https://example.com/.well-known/devseo-verify.txt`
- File content: `{verification_token}`

---

### 3. Scans/Crawls

#### List All Scans
**GET** `/api/v1/crawls`

Get all scan results for the authenticated user.

**Query Parameters:**
- `website_id` (optional): Filter by website UUID
- `status` (optional): Filter by status ('pending', 'running', 'completed', 'failed')
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset

**Response:**
```typescript
interface CrawlJob {
  id: string
  website_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  seo_score: number | null        // 0-100
  performance_score: number | null // 0-100
  pages_scanned: number
  started_at: string
  completed_at: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}

CrawlJob[]
```

---

#### Start New Scan
**POST** `/api/v1/crawls`

Start a new SEO scan for a website.

**Request Body:**
```typescript
{
  "website_id": string,  // UUID
  "max_pages"?: number   // Optional, default: 100
}
```

**Response:**
```typescript
{
  "id": string,        // Crawl job UUID
  "status": "pending",
  "message": "Scan started successfully"
}
```

**Note:** Scan runs in background. Poll the status endpoint to check progress.

---

#### Get Scan Results
**GET** `/api/v1/crawls/{crawl_id}`

Get detailed results of a completed scan.

**Response:**
```typescript
interface ScanReport {
  // Basic info
  id: string
  website_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'

  // Scores
  seo_score: number           // 0-100
  performance_score: number   // 0-100

  // Stats
  pages_scanned: number
  issues_found: number

  // Timestamps
  started_at: string
  completed_at: string

  // Detailed results
  issues: Issue[]
  pages: PageResult[]
  recommendations: Recommendation[]
}

interface Issue {
  type: string              // e.g., "missing_title", "slow_response"
  severity: 'critical' | 'warning' | 'info'
  message: string           // Technical message
  simple_message: string    // Plain English version
  suggestion: string        // How to fix
  affected_pages: number
  page_urls: string[]       // URLs with this issue
}

interface PageResult {
  url: string
  status_code: number
  seo_score: number
  readability_score: number      // 0-100 (Flesch Reading Ease)
  readability_grade: string      // e.g., "8th-9th grade"
  response_time_ms: number
  issues_count: number
  title: string
  meta_description: string
  word_count: number
  h1_count: number
  created_at: string
}

interface Recommendation {
  priority: 'high' | 'medium' | 'low'
  category: string
  title: string
  description: string
  implementation_status: 'pending' | 'implemented' | 'ignored'
}
```

---

#### Get Scanned Pages
**GET** `/api/v1/crawls/{crawl_id}/pages`

Get list of all pages scanned in a crawl job.

**Query Parameters:**
- `limit` (optional): Number of results
- `offset` (optional): Pagination offset

**Response:**
```typescript
PageResult[]
```

---

### 4. Content Optimizer

#### Optimize Content
**POST** `/api/v1/content/optimize`

AI-powered content optimization.

**Request Body:**
```typescript
{
  text?: string           // Paste content directly (OR)
  url?: string            // Fetch content from URL
  target_keyword?: string // Optional SEO keyword
}
```

**Note:** Provide either `text` or `url`, not both.

**Response:**
```typescript
{
  // Title suggestions
  title_suggestions: {
    title: string
    character_count: number
    reasoning: string
  }[]

  // Meta description
  meta_description: {
    text: string
    character_count: number
  }

  // Readability
  readability: {
    score: number            // 0-100 (Flesch)
    grade_level: string      // e.g., "8th-9th grade"
    interpretation: string   // e.g., "Easy to read"
  }

  // Keyword density
  keyword_density: {
    keyword: string
    count: number
    density: number  // Percentage
  }[]

  // Content quality
  content_quality: {
    word_count: number
    suggestions: string[]
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/content/optimize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your content here...",
    "target_keyword": "SEO optimization"
  }'
```

---

### 5. User Profile

#### Get Current User
**GET** `/api/v1/users/me`

Get authenticated user's profile.

**Response:**
```typescript
interface User {
  id: string
  clerk_id: string
  email: string
  plan: 'free' | 'starter' | 'pro' | 'agency'
  usage_this_month: {
    scans: number
    websites: number
    optimizations: number
  }
  limits: {
    max_websites: number
    max_scans_monthly: number
    max_optimizations_monthly: number
  }
  created_at: string
  updated_at: string
}
```

---

#### Update User Profile
**PUT** `/api/v1/users/me`

Update user preferences.

**Request Body:**
```typescript
{
  email?: string
  preferences?: {
    language?: 'en' | 'ar'
    report_mode?: 'plain_english' | 'technical'
    email_notifications?: {
      scan_complete?: boolean
      scan_failed?: boolean
      weekly_summary?: boolean
    }
  }
}
```

**Response:**
```typescript
User
```

---

## 🔌 Frontend Integration Examples

### React Query Setup

```typescript
// lib/api.ts
import { useAuth } from '@clerk/clerk-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useApi = () => {
  const { getToken } = useAuth()

  const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
    const token = await getToken()

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'API Error')
    }

    return response.json()
  }

  return {
    get: (endpoint: string) => fetchApi(endpoint),
    post: (endpoint: string, data: any) =>
      fetchApi(endpoint, { method: 'POST', body: JSON.stringify(data) }),
    put: (endpoint: string, data: any) =>
      fetchApi(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (endpoint: string) =>
      fetchApi(endpoint, { method: 'DELETE' }),
  }
}
```

### Using React Query Hooks

```typescript
// hooks/useWebsites.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useApi } from '@/lib/api'

export const useWebsites = () => {
  const api = useApi()
  const queryClient = useQueryClient()

  // Fetch websites
  const { data: websites, isLoading } = useQuery({
    queryKey: ['websites'],
    queryFn: () => api.get('/api/v1/websites'),
  })

  // Create website
  const createWebsite = useMutation({
    mutationFn: (data: { url: string }) =>
      api.post('/api/v1/websites', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['websites'])
    },
  })

  return { websites, isLoading, createWebsite }
}
```

### Component Example

```typescript
// components/WebsiteList.tsx
import { useWebsites } from '@/hooks/useWebsites'
import { Button } from '@/components/ui/button'

export const WebsiteList = () => {
  const { websites, isLoading, createWebsite } = useWebsites()

  const handleAdd = () => {
    createWebsite.mutate({ url: 'https://example.com' })
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <Button onClick={handleAdd}>Add Website</Button>

      {websites?.map((website) => (
        <div key={website.id}>
          <h3>{website.domain}</h3>
          <span>{website.verified ? '✅' : '⚠️'}</span>
        </div>
      ))}
    </div>
  )
}
```

---

## 🚨 Error Handling

**Standard Error Response:**
```typescript
{
  "detail": string  // Error message
  "status_code": number
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (quota exceeded)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

**Error Handling Example:**
```typescript
try {
  const data = await api.post('/api/v1/websites', { url: 'invalid' })
} catch (error) {
  if (error.message.includes('401')) {
    // Redirect to login
  } else if (error.message.includes('429')) {
    // Show rate limit message
    toast.error('Rate limit exceeded. Please upgrade your plan.')
  } else {
    // General error
    toast.error(error.message)
  }
}
```

---

## 🔄 Polling for Scan Status

Scans run in the background. Poll for status updates:

```typescript
const { data: scan } = useQuery({
  queryKey: ['scan', scanId],
  queryFn: () => api.get(`/api/v1/crawls/${scanId}`),
  refetchInterval: (data) =>
    data?.status === 'running' ? 3000 : false,  // Poll every 3s while running
  enabled: !!scanId,
})
```

---

## 🌍 Environment Variables

Create `.env.local` in frontend:

```bash
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

---

## ✅ Testing Checklist

### Backend Running:
```bash
cd backend
python -m app.main
# Should see: "Application startup complete"
# Visit: http://localhost:8000/docs
```

### Test Authentication:
1. Get Clerk token in frontend
2. Send to backend in Authorization header
3. Backend validates with Clerk

### Test CORS:
1. Frontend on `http://localhost:5173`
2. Make API request from browser
3. Should NOT see CORS errors

### Test Endpoints:
- [ ] GET /health (no auth)
- [ ] GET /api/v1/websites (with auth)
- [ ] POST /api/v1/websites (with auth)
- [ ] POST /api/v1/crawls (with auth)
- [ ] POST /api/v1/content/optimize (with auth)

---

## 🎯 Quick Start

**1. Backend:**
```bash
cd backend
source venv/Scripts/activate  # Windows: venv\Scripts\activate
python -m app.main
```

**2. Frontend (Lovable):**
```bash
cd insight-navigator
npm install
npm run dev
```

**3. Test Connection:**
```javascript
// In browser console on frontend
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
// Should see: { status: "healthy" }
```

---

## 📞 Need Help?

**API Documentation:** http://localhost:8000/docs (Interactive)
**Backend Issues:** Check backend console for errors
**CORS Issues:** Check CORS_ORIGINS in backend/app/config.py
**Auth Issues:** Verify Clerk token is being sent correctly

---

**Last Updated:** February 11, 2026
**API Version:** 1.0.0
