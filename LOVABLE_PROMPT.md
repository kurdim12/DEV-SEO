# DevSEO Frontend - Lovable Build Prompt

## 🎯 Project Overview

Build a modern, professional SEO analytics dashboard for **DevSEO** - an AI-powered SEO analysis platform with unique Arabic language support.

**Target Users:**
- SEO professionals
- Digital marketing agencies
- Web developers
- Small business owners
- Arabic-speaking markets (MENA region)

**Key Differentiators:**
- First SEO tool with Arabic dialect detection
- Plain English explanations (not just technical jargon)
- Real-time content optimization
- Multi-language support (English/Arabic with RTL)

---

## 🏗️ Tech Stack Requirements

**Framework:** Next.js 14+ (App Router)
**Styling:** Tailwind CSS
**UI Components:** shadcn/ui (preferred) or Radix UI
**State Management:** React Query (TanStack Query) for API calls
**Authentication:** Clerk (already configured)
**Charts/Graphs:** Recharts or Chart.js
**Language:** TypeScript
**Internationalization:** next-intl

**Design System:**
- Modern, clean, professional
- Color scheme: Blues/Purples for primary, Red/Yellow/Green for scores
- Responsive (mobile, tablet, desktop)
- Dark mode support (optional but recommended)
- RTL layout support for Arabic

---

## 📡 Backend API Information

**Base URL (Development):** `http://localhost:8000`
**Base URL (Production):** Will be provided

**API Documentation:** Available at `http://localhost:8000/docs`

**Authentication:**
- Uses Clerk for user authentication
- Backend expects Clerk JWT token in Authorization header
- Format: `Authorization: Bearer <clerk_jwt_token>`

**Key API Endpoints:**

```typescript
// Websites
GET    /api/v1/websites          // List user's websites
POST   /api/v1/websites          // Add new website
GET    /api/v1/websites/{id}     // Get website details
PUT    /api/v1/websites/{id}     // Update website
DELETE /api/v1/websites/{id}     // Delete website
POST   /api/v1/websites/{id}/verify  // Verify domain ownership

// Scans/Crawls
GET    /api/v1/crawls             // List all scans
POST   /api/v1/crawls             // Start new scan
GET    /api/v1/crawls/{id}        // Get scan results
GET    /api/v1/crawls/{id}/pages  // Get scanned pages

// Content Optimizer (AI-powered)
POST   /api/v1/content/optimize   // Optimize content

// User Profile
GET    /api/v1/users/me           // Get current user
PUT    /api/v1/users/me           // Update user profile
```

**Response Format:**
All responses are JSON with consistent structure:
```json
{
  "id": "uuid",
  "data": {},
  "message": "Success",
  "timestamp": "2026-02-11T..."
}
```

---

## 📄 Pages to Build

### 1. Dashboard (`/dashboard`)

**Purpose:** Overview of user's SEO performance

**Components Needed:**
- Welcome header with user name
- Quick stats cards:
  - Total websites monitored
  - Total scans this month
  - Average SEO score
  - Critical issues count
- Recent scans table (last 10 scans)
  - Website name
  - Scan date
  - SEO score (colored badge)
  - Status (completed/running/failed)
  - Quick actions (view report, rescan)
- SEO score trend chart (line chart showing score over time)
- Quick actions:
  - "Add New Website" button (primary CTA)
  - "Run Scan" button

**Data Sources:**
- `GET /api/v1/websites` - Website list
- `GET /api/v1/crawls` - Recent scans
- Aggregate data client-side for stats

**Design Notes:**
- Use cards for stats with icons
- Color code SEO scores: 0-40 (red), 41-70 (yellow), 71-100 (green)
- Make it scannable - users should understand status at a glance

---

### 2. Websites Page (`/websites`)

**Purpose:** Manage all monitored websites

**Components Needed:**
- Page header with "Add Website" button
- Websites grid/list:
  - Website URL/domain
  - Verification status (verified badge)
  - Last scan date
  - Latest SEO score
  - Quick actions: Scan, Settings, Delete
- Empty state: "No websites yet. Add your first website to get started!"
- Add website modal/dialog:
  - URL input (validate URL format)
  - Optional: Website name
  - Submit button

**Data Sources:**
- `GET /api/v1/websites`
- `POST /api/v1/websites` (add new)
- `DELETE /api/v1/websites/{id}` (delete)

**Features:**
- Search/filter websites
- Sort by: name, last scan, score
- Bulk actions (optional)

---

### 3. Website Details (`/websites/[id]`)

**Purpose:** Deep dive into a specific website

**Components Needed:**
- Website header:
  - Domain name
  - Verification status
  - "Verify Domain" button (if not verified)
  - "Start Scan" button
  - Settings dropdown
- Tabs:
  - **Overview:** Latest scan summary
  - **Scan History:** All past scans
  - **Verification:** Domain ownership verification
  - **Settings:** Website configuration

**Tab 1: Overview**
- Latest SEO score (big, prominent)
- Key metrics cards:
  - Pages scanned
  - Issues found
  - Performance score
  - Readability score
- Recent issues list (top 5-10)
- "View Full Report" button

**Tab 2: Scan History**
- Table of all scans:
  - Date/time
  - SEO score
  - Pages scanned
  - Issues found
  - Actions (view report)
- Pagination

**Tab 3: Verification**
- Verification status badge
- Three verification methods (tabs/accordion):
  1. **DNS TXT Record**
     - Instructions
     - TXT record value to add
     - "Verify DNS" button
  2. **Meta Tag**
     - Instructions
     - Meta tag HTML to copy
     - "Verify Meta Tag" button
  3. **File Upload**
     - Instructions
     - File content to copy
     - File location (/.well-known/devseo-verify.txt)
     - "Verify File" button
- Show verification error if failed

**Tab 4: Settings**
- Website name (editable)
- Delete website (danger zone)

**Data Sources:**
- `GET /api/v1/websites/{id}`
- `GET /api/v1/crawls?website_id={id}`
- `POST /api/v1/websites/{id}/verify`

---

### 4. Scan Report (`/reports/[id]`)

**Purpose:** Detailed SEO analysis results

**Components Needed:**

**Header Section:**
- Website URL
- Scan date/time
- Overall SEO score (large, prominent, color-coded)
- "Plain English Mode" toggle switch (very important!)
- "Download PDF" button (placeholder for now)
- "Rescan" button

**Score Breakdown (Cards):**
- SEO Score (0-100)
- Performance Score (0-100)
- Readability Score (0-100) with grade level
- Pages Scanned count
- Issues Found count

**Plain English Toggle:**
When ON: Show `simple_message` from issues
When OFF: Show `message` (technical version)

Example:
- Technical: "Missing meta description tag in HTML head"
- Plain English: "Your page doesn't have a description. Add one to help Google understand what your page is about."

**Issues Section (Tabbed):**
- **All Issues** (default)
- **Critical** (red, must fix)
- **Warnings** (yellow, should fix)
- **Info** (blue, nice to fix)

Issues table/list:
- Severity icon/badge
- Message (plain English or technical based on toggle)
- Affected pages count
- Suggestion (how to fix)
- Expand/collapse for details

**Pages Analyzed Section:**
Table of all scanned pages:
- URL
- Status code (200, 404, 500, etc.)
- SEO score
- Readability score
- Response time
- Issues count
- "View Details" link

**Recommendations Section:**
- AI-generated recommendations
- Grouped by priority
- Actionable suggestions

**Data Sources:**
- `GET /api/v1/crawls/{id}` - Main scan data
- `GET /api/v1/crawls/{id}/pages` - Scanned pages

**Response Structure:**
```typescript
interface ScanReport {
  id: string
  website_id: string
  status: 'completed' | 'running' | 'failed'
  seo_score: number
  performance_score: number
  pages_scanned: number
  started_at: string
  completed_at: string

  issues: Issue[]
  pages: PageResult[]
  recommendations: Recommendation[]
}

interface Issue {
  type: string
  severity: 'critical' | 'warning' | 'info'
  message: string          // Technical message
  simple_message: string   // Plain English (if available)
  suggestion: string
  affected_pages: number
  page_urls: string[]
}

interface PageResult {
  url: string
  status_code: number
  seo_score: number
  readability_score: number
  readability_grade: string
  response_time_ms: number
  issues_count: number
  title: string
  meta_description: string
  word_count: number
  created_at: string
}
```

**Design Notes:**
- Make issues easy to scan
- Color code severity consistently
- Plain English toggle should be prominent
- Show progress if scan is still running
- Empty states for no issues (celebrate!)

---

### 5. Content Optimizer (`/content-optimizer`)

**Purpose:** AI-powered content optimization tool

**Components Needed:**

**Input Section:**
Two input modes (radio buttons or tabs):
1. **Text Input Mode:**
   - Large textarea for content
   - Character/word counter
   - "Optimize Content" button

2. **URL Input Mode:**
   - URL input field
   - "Fetch & Optimize" button

**Target Keyword (Optional):**
- Text input for target keyword
- Helper text: "e.g., 'best coffee shops in Dubai'"

**Results Section (appears after optimization):**

**Title Suggestions:**
- 3 optimized title options
- Character count for each
- Reasoning/explanation
- Copy button for each

**Meta Description:**
- Generated meta description
- Character count (145-155 ideal)
- Copy button

**Readability Analysis:**
- Flesch Reading Ease score (0-100)
- Grade level (e.g., "8th-9th grade")
- Interpretation (e.g., "Easy to read")
- Sentence length analysis

**Keyword Density:**
- Top 10 keywords with percentages
- Target keyword density (if provided)
- Recommendations for keyword usage

**Content Quality Checklist:**
- Word count (with benchmark: 300/600/1000+)
- Heading structure suggestions
- Internal linking recommendations
- Missing keyword variations

**API Endpoint:**
```typescript
POST /api/v1/content/optimize
Body: {
  text?: string           // Either text or url (not both)
  url?: string
  target_keyword?: string // Optional
}

Response: {
  title_suggestions: {
    title: string
    character_count: number
    reasoning: string
  }[]
  meta_description: {
    text: string
    character_count: number
  }
  readability: {
    score: number          // 0-100
    grade_level: string    // e.g., "8th-9th grade"
    interpretation: string // e.g., "Easy to read"
  }
  keyword_density: {
    keyword: string
    count: number
    density: number        // percentage
  }[]
  content_quality: {
    word_count: number
    suggestions: string[]
  }
}
```

**Design Notes:**
- Clear separation between input and results
- Make results easy to copy (copy buttons everywhere)
- Show loading state while analyzing
- Celebrate good scores

---

### 6. Billing/Subscription (`/billing`)

**Purpose:** Manage subscription and usage

**Components Needed:**

**Current Plan Section:**
- Plan name (Free/Starter/Pro/Agency)
- Plan price
- Billing period (monthly/annual)
- "Upgrade Plan" or "Change Plan" button
- "Cancel Subscription" link (if subscribed)

**Usage This Month:**
Progress bars showing:
- Websites: X / Y used
- Scans: X / Y used
- Content optimizations: X / Y used

**Pricing Plans (if not subscribed or upgrading):**
3-4 plan cards:

**Free/Trial Plan:**
- $0/month
- 1 website
- 5 scans/month
- 10 optimizations/month
- Email support

**Starter Plan - $19/month:**
- 5 websites
- 50 scans/month
- 100 optimizations/month
- Email support
- Plain English mode
- Domain verification

**Pro Plan - $49/month (Most Popular):**
- 25 websites
- 500 scans/month
- Unlimited optimizations
- Priority support
- White-label PDFs
- API access
- Scheduled scans

**Agency Plan - $149/month:**
- Unlimited websites
- Unlimited scans
- Unlimited optimizations
- Dedicated support
- Client management
- White-label everything
- Custom branding

**Billing History:**
- Table of past invoices
- Download PDF button for each

**Payment Method:**
- Card details (masked)
- "Update Payment Method" button

**API Integration (Placeholder for now):**
```typescript
// These will be implemented by backend later
GET  /api/v1/billing/subscription
POST /api/v1/billing/checkout        // Create Stripe checkout
POST /api/v1/billing/portal          // Stripe customer portal
GET  /api/v1/billing/usage
GET  /api/v1/billing/invoices
```

**Design Notes:**
- Make "Pro" plan stand out (recommended badge)
- Show value proposition clearly
- Progress bars for usage limits
- Clear upgrade path

---

### 7. Settings (`/settings`)

**Purpose:** User preferences and account settings

**Components Needed:**

**Tabs/Sections:**

**1. Profile:**
- Display name
- Email (from Clerk, read-only)
- Avatar upload
- Save button

**2. Preferences:**
- **Language:** English / العربية (Arabic) dropdown
  - Changes UI language
  - Saves to user profile
  - Triggers RTL layout for Arabic

- **Default Report Mode:**
  - Radio buttons: Plain English / Technical
  - Saves preference for report viewing

- **Email Notifications:**
  - Toggle: Scan complete emails
  - Toggle: Scan failed emails
  - Toggle: Weekly summary
  - Toggle: Marketing emails

**3. API Keys** (if Pro/Agency plan):
- Generate API key button
- List of active API keys:
  - Key name
  - Key (masked, show/copy)
  - Created date
  - Last used
  - Delete button

**4. Danger Zone:**
- Export data button
- Delete account button (confirmation modal)

**API Endpoints:**
```typescript
GET  /api/v1/users/me
PUT  /api/v1/users/me
POST /api/v1/users/me/api-keys
GET  /api/v1/users/me/api-keys
DELETE /api/v1/users/me/api-keys/{id}
```

---

## 🌍 Internationalization (i18n)

**Languages:** English (default), Arabic

**Implementation:**
Use `next-intl` library

**Setup:**
```
messages/
  en.json    // English translations
  ar.json    // Arabic translations
```

**Key Translation Areas:**
- Navigation menu
- Button labels
- Form labels
- Error messages
- Success messages
- Dashboard stats labels
- Settings page

**RTL Support for Arabic:**
- Add `dir="rtl"` to `<html>` when Arabic selected
- Mirror layout (sidebar on right, etc.)
- Use `text-align: start` instead of `left`
- Test all components in RTL mode

**Example Translations:**

**en.json:**
```json
{
  "nav": {
    "dashboard": "Dashboard",
    "websites": "Websites",
    "reports": "Reports",
    "content": "Content Optimizer",
    "billing": "Billing",
    "settings": "Settings"
  },
  "dashboard": {
    "welcome": "Welcome back",
    "totalWebsites": "Total Websites",
    "avgScore": "Average SEO Score",
    "criticalIssues": "Critical Issues",
    "recentScans": "Recent Scans"
  },
  "buttons": {
    "addWebsite": "Add Website",
    "startScan": "Start Scan",
    "viewReport": "View Report",
    "save": "Save",
    "cancel": "Cancel"
  }
}
```

**ar.json:**
```json
{
  "nav": {
    "dashboard": "لوحة التحكم",
    "websites": "المواقع",
    "reports": "التقارير",
    "content": "محسن المحتوى",
    "billing": "الفواتير",
    "settings": "الإعدادات"
  },
  "dashboard": {
    "welcome": "مرحباً بعودتك",
    "totalWebsites": "إجمالي المواقع",
    "avgScore": "متوسط نقاط SEO",
    "criticalIssues": "مشاكل حرجة",
    "recentScans": "الفحوصات الأخيرة"
  },
  "buttons": {
    "addWebsite": "إضافة موقع",
    "startScan": "بدء الفحص",
    "viewReport": "عرض التقرير",
    "save": "حفظ",
    "cancel": "إلغاء"
  }
}
```

---

## 🎨 Design System

**Colors:**

**Primary (Blue):**
- 50: #eff6ff
- 500: #3b82f6 (main brand color)
- 700: #1d4ed8

**Success (Green):**
- SEO score 71-100: #10b981

**Warning (Yellow/Orange):**
- SEO score 41-70: #f59e0b

**Danger (Red):**
- SEO score 0-40: #ef4444

**Neutral (Gray):**
- Background: #f9fafb
- Text: #111827
- Borders: #e5e7eb

**Typography:**
- Font: Inter or System UI
- Headings: Bold, larger sizes
- Body: Regular, 16px base

**Components:**
Use shadcn/ui for:
- Buttons
- Cards
- Dialogs/Modals
- Form inputs
- Dropdowns
- Tables
- Badges
- Tabs
- Progress bars
- Charts (Recharts)

**Spacing:**
- Use Tailwind spacing scale (4px increments)
- Consistent padding/margins

---

## 📱 Responsive Design

**Breakpoints:**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

**Mobile Considerations:**
- Collapsible sidebar navigation
- Stack cards vertically
- Simplify tables (show fewer columns)
- Touch-friendly buttons (min 44px)
- Bottom navigation bar (optional)

---

## 🔐 Authentication Flow

**Using Clerk:**

**Protected Routes:**
All routes except landing page should require authentication.

**Setup:**
```tsx
import { ClerkProvider, SignIn, SignUp, UserButton } from '@clerk/nextjs'

// Wrap app with ClerkProvider
// Use UserButton component in navbar
// Protect routes with middleware
```

**User Data:**
Clerk provides:
- User ID (sync with backend)
- Email
- Name
- Avatar

**Backend Integration:**
- Get Clerk JWT token: `await getToken()`
- Send in API requests: `Authorization: Bearer {token}`

---

## 🚀 State Management

**Use React Query (TanStack Query):**

**Benefits:**
- Automatic caching
- Loading/error states
- Refetching on focus
- Optimistic updates

**Example:**
```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Fetch websites
const { data: websites, isLoading } = useQuery({
  queryKey: ['websites'],
  queryFn: async () => {
    const res = await fetch('/api/v1/websites', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    return res.json()
  }
})

// Create website
const createWebsite = useMutation({
  mutationFn: (data) => fetch('/api/v1/websites', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: { 'Authorization': `Bearer ${token}` }
  }),
  onSuccess: () => {
    queryClient.invalidateQueries(['websites'])
  }
})
```

---

## 🧪 Key Features to Implement

### 1. Plain English Mode Toggle
**Critical Feature!**

**Location:** Scan report page
**Implementation:**
- Toggle switch in header
- Save preference to localStorage
- Show `issue.simple_message` when ON
- Show `issue.message` when OFF

**Example:**
```tsx
const [plainEnglish, setPlainEnglish] = useState(
  localStorage.getItem('plainEnglish') === 'true'
)

const togglePlainEnglish = () => {
  const newValue = !plainEnglish
  setPlainEnglish(newValue)
  localStorage.setItem('plainEnglish', String(newValue))
}

// In issue display
{plainEnglish ? issue.simple_message : issue.message}
```

### 2. Real-time Scan Progress
**Location:** Dashboard, Website details

**Implementation:**
- Poll `/api/v1/crawls/{id}` every 3-5 seconds while status is 'running'
- Show progress bar or spinner
- Update UI when completed
- Show notification on completion

### 3. Copy to Clipboard
**Location:** Content optimizer, Domain verification

**Implementation:**
```tsx
const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
  toast.success('Copied to clipboard!')
}
```

### 4. Empty States
**Critical for UX!**

Show friendly empty states for:
- No websites yet → "Add your first website to get started"
- No scans yet → "Run your first scan to see results"
- No issues found → "🎉 Perfect! No issues found"

### 5. Loading States
**Show loading for:**
- Initial page load
- API requests
- Scan in progress

Use skeletons, spinners, or progress bars

### 6. Error Handling
**Handle gracefully:**
- API errors (show toast notification)
- Network errors (retry button)
- Validation errors (inline form errors)
- 404 pages
- 500 errors

---

## 📊 Charts & Visualizations

**Use Recharts library**

**Charts Needed:**

1. **SEO Score Trend (Line Chart):**
   - X-axis: Date
   - Y-axis: SEO score (0-100)
   - Show last 30 days
   - Location: Dashboard

2. **Score Breakdown (Doughnut/Pie):**
   - SEO score
   - Performance score
   - Readability score
   - Location: Report page

3. **Issues by Severity (Bar Chart):**
   - Critical, Warning, Info counts
   - Color coded
   - Location: Dashboard

4. **Usage Chart (Progress Bars):**
   - Websites used vs limit
   - Scans used vs limit
   - Location: Billing page

---

## 🎯 User Flows to Optimize

### 1. First-Time User Flow
1. Sign up with Clerk
2. See welcome modal/tour
3. Click "Add Website"
4. Enter URL, click Add
5. Click "Start Scan"
6. Wait (show progress)
7. View report
8. Celebrate! 🎉

### 2. Returning User Flow
1. Login
2. See dashboard with latest data
3. Quick action: Rescan or view report

### 3. Content Optimization Flow
1. Go to Content Optimizer
2. Paste content or URL
3. Enter target keyword (optional)
4. Click Optimize
5. See results
6. Copy suggestions
7. Apply to website

---

## 🔔 Notifications & Feedback

**Use Toast Notifications:**

**Success:**
- "Website added successfully!"
- "Scan started!"
- "Copied to clipboard"
- "Settings saved"

**Error:**
- "Failed to start scan. Please try again."
- "Invalid URL format"
- "Rate limit exceeded"

**Info:**
- "Scan in progress... This may take a few minutes"
- "Verification sent. Check your DNS records."

**Implementation:**
Use `sonner` or `react-hot-toast`

---

## 🚨 Edge Cases to Handle

1. **Long URLs:** Truncate with ellipsis, show full on hover
2. **No data:** Show empty states with CTAs
3. **Scan failures:** Show error message with retry option
4. **Slow API:** Show loading states, timeout after 30s
5. **Invalid input:** Client-side validation before API call
6. **Concurrent scans:** Disable "Start Scan" if already running
7. **Expired sessions:** Redirect to login
8. **Rate limits:** Show upgrade prompt
9. **Large datasets:** Implement pagination
10. **Mobile layout:** Test all features on mobile

---

## 🎨 UI/UX Best Practices

1. **Consistency:** Use design system consistently
2. **Feedback:** Always show loading/success/error states
3. **Accessibility:**
   - Proper contrast ratios
   - Keyboard navigation
   - ARIA labels
   - Alt text for images
4. **Performance:**
   - Lazy load images
   - Code splitting
   - Optimize bundle size
5. **Progressive Enhancement:**
   - Work without JS where possible
   - Graceful degradation
6. **Mobile-first:** Design for mobile, enhance for desktop

---

## 📦 Folder Structure

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/
│   │   └── sign-up/
│   ├── (dashboard)/
│   │   ├── layout.tsx        // Dashboard layout with sidebar
│   │   ├── page.tsx           // Dashboard home
│   │   ├── websites/
│   │   │   ├── page.tsx       // Websites list
│   │   │   └── [id]/
│   │   │       └── page.tsx   // Website details
│   │   ├── reports/
│   │   │   └── [id]/
│   │   │       └── page.tsx   // Scan report
│   │   ├── content-optimizer/
│   │   │   └── page.tsx       // Content optimizer
│   │   ├── billing/
│   │   │   └── page.tsx       // Billing & subscription
│   │   └── settings/
│   │       └── page.tsx       // User settings
│   ├── layout.tsx             // Root layout
│   └── page.tsx               // Landing page (public)
├── components/
│   ├── ui/                    // shadcn components
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── StatsCard.tsx
│   ├── websites/
│   │   ├── WebsiteCard.tsx
│   │   ├── AddWebsiteDialog.tsx
│   │   └── VerificationWizard.tsx
│   ├── reports/
│   │   ├── ScoreCard.tsx
│   │   ├── IssuesList.tsx
│   │   ├── PlainEnglishToggle.tsx
│   │   └── PagesTable.tsx
│   ├── content/
│   │   ├── ContentInput.tsx
│   │   ├── TitleSuggestions.tsx
│   │   └── ReadabilityScore.tsx
│   └── billing/
│       └── PricingCard.tsx
├── lib/
│   ├── api.ts                 // API client
│   ├── utils.ts               // Utility functions
│   └── types.ts               // TypeScript types
├── hooks/
│   ├── useWebsites.ts         // React Query hooks
│   ├── useScans.ts
│   └── useContentOptimizer.ts
├── messages/
│   ├── en.json                // English translations
│   └── ar.json                // Arabic translations
└── public/
    └── images/
```

---

## 🔗 API Client Setup

**Create reusable API client:**

```typescript
// lib/api.ts
import { useAuth } from '@clerk/nextjs'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
      throw new Error(`API Error: ${response.statusText}`)
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

---

## 🎯 Priority Order

**Phase 1 (Critical - Week 1):**
1. Dashboard page
2. Websites list/add/delete
3. Website details with verification
4. Scan report page with Plain English toggle
5. Content optimizer page

**Phase 2 (Important - Week 2):**
6. Billing/subscription page (UI only, backend later)
7. Settings page
8. Arabic language support + RTL
9. Mobile responsive design
10. Error handling & loading states

**Phase 3 (Polish - Week 3):**
11. Charts and visualizations
12. Empty states
13. Onboarding flow
14. Animations and transitions
15. Performance optimization

---

## ✅ Definition of Done

A page is complete when:
- [ ] Responsive (mobile, tablet, desktop)
- [ ] Works in both English and Arabic (RTL)
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Empty states designed
- [ ] Accessible (keyboard nav, ARIA labels)
- [ ] API integration working
- [ ] TypeScript types defined
- [ ] No console errors
- [ ] Matches design system

---

## 🐛 Known Backend Limitations

1. **Payment system not ready yet:** Build UI, backend will integrate Stripe later
2. **Some API endpoints may be placeholders:** Build UI assuming they'll work
3. **Real-time updates:** Use polling for now (WebSockets later)
4. **PDF generation:** Button can be placeholder for now

---

## 🔑 Environment Variables Needed

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# For production (later):
NEXT_PUBLIC_API_URL=https://api.devseo.io
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
```

---

## 📞 Questions to Ask if Unclear

1. **Color scheme:** Any specific brand colors?
2. **Logo:** Do you have a logo file?
3. **Font:** Any preference beyond Inter/System UI?
4. **Charts:** Which metrics to show on dashboard?
5. **Mobile:** Bottom nav bar or hamburger menu?
6. **Dark mode:** Priority or can be added later?

---

## 🎉 Success Metrics

The frontend is successful if:
- Users can add websites easily
- Scan reports are clear and actionable
- Plain English mode makes issues understandable
- Content optimizer provides value
- UI feels fast and responsive
- Arabic users have first-class experience
- Mobile users can access all features

---

## 📚 Reference Links

**Backend API Docs:** http://localhost:8000/docs
**Design Inspiration:**
- Ahrefs (SEO tool)
- Screaming Frog (crawler)
- Vercel Dashboard (modern UI)
- Linear (clean design)

**Component Libraries:**
- shadcn/ui: https://ui.shadcn.com
- Recharts: https://recharts.org
- next-intl: https://next-intl-docs.vercel.app

---

## 🚀 Let's Build!

This is an exciting project with real competitive advantages (Arabic support, Plain English mode). Focus on making the UI clean, fast, and user-friendly. The backend is solid - your job is to make it shine through beautiful, intuitive interfaces.

**Remember:** SEO professionals look at data all day. Make your dashboard the one they *want* to use because it's clear, fast, and gives them insights they can act on immediately.

Good luck! 🎨✨
