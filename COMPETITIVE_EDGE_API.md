# 🚀 Competitive Edge API Documentation

**Date:** February 11, 2026
**Status:** Production Ready

These are the features that make DevSEO **UNIQUE** in the market.

---

## 🎯 What Makes Us Different

| Feature | DevSEO | ContentKing | Semrush | Screaming Frog |
|---------|--------|-------------|---------|----------------|
| **CWV Root Cause Analysis** | ✅ **YES** | ❌ No | ❌ No | ❌ No |
| **JS Rendering Diagnostics** | ✅ **YES** | ❌ No | Partial | Partial |
| **RTL/Arabic Validation** | ✅ **ONLY US** | ❌ No | ❌ No | ❌ No |
| **Real-time Webhooks** | ✅ **YES** | ✅ Yes | ❌ No | ❌ No |
| **Regression Diff** | ✅ **YES** | Partial | ❌ No | ❌ No |

---

## 📚 API Endpoints

Base URL: `https://api.devseo.com` (or `http://localhost:8000` for development)

All endpoints require authentication via Bearer token.

---

## 1. CWV Root Cause Analysis

**Nobody else does this. This is your #1 differentiator.**

### Endpoint
```http
POST /api/v1/analysis/cwv-root-cause
```

### When to Use
- After a deploy when performance degrades
- Monthly performance audits
- Before/after optimization comparison
- Proving SEO impact to stakeholders

### Request
```json
{
  "current_crawl_id": "uuid-of-current-scan",
  "previous_crawl_id": "uuid-of-baseline-scan" // optional
}
```

### Response
```json
{
  "has_baseline": true,
  "comparison": {
    "current_crawl_id": "...",
    "previous_crawl_id": "...",
    "time_difference_hours": 24.5
  },
  "changes": {
    "lcp": {
      "current": 2500,
      "previous": 2100,
      "change_ms": 400,
      "change_percent": 19.0,
      "is_regression": false,
      "threshold_ms": 500
    },
    "fid": {...},
    "cls": {...},
    "ttfb": {...}
  },
  "root_causes": [
    {
      "metric": "LCP",
      "severity": "critical",
      "category": "resource_optimization",
      "title": "LCP increased by 400ms",
      "description": "Largest Contentful Paint degraded from 2100ms to 2500ms...",
      "simple_explanation": "Your page loads slower now. Users see content 400ms later.",
      "likely_causes": [
        "Large unoptimized images added to hero/banner sections",
        "Web fonts blocking render (missing font-display: swap)",
        "Critical CSS not inlined or render-blocking stylesheets"
      ],
      "affected_pages": ["https://example.com/pricing", "https://example.com/features"],
      "affected_pages_count": 15,
      "how_to_fix": {
        "immediate": [
          "1. Identify LCP element: Run Lighthouse on affected pages",
          "2. If image: Optimize (WebP/AVIF), add width/height attributes",
          "3. Preload LCP resource: <link rel='preload' as='image' href='hero.jpg'>"
        ],
        "long_term": [
          "Set up image optimization pipeline (auto-convert to WebP)",
          "Implement CDN with image optimization (Cloudflare, Cloudinary)"
        ]
      },
      "business_impact": "For every 1 second delay, conversions drop 7-10%. Your 400ms regression could cost 3.2% in conversions.",
      "google_impact": "LCP > 2.5s moves pages from 'Good' to 'Needs Improvement'"
    }
  ],
  "severity": "warning",
  "summary": "Performance regression detected:\n• LCP worsened by 400ms...",
  "action_items": [
    {
      "priority": 1,
      "metric": "LCP",
      "title": "LCP increased by 400ms",
      "immediate_actions": ["1. Optimize hero image...", "2. Add preload hint..."],
      "estimated_time": "30-60 minutes",
      "impact": "High"
    }
  ]
}
```

### Example Use Cases

**1. Post-Deploy Check**
```bash
# Developer deploys at 3pm
# DevSEO auto-scans at 3:05pm
# Compare with pre-deploy baseline

curl -X POST https://api.devseo.com/api/v1/analysis/cwv-root-cause \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_crawl_id": "post-deploy-scan-id",
    "previous_crawl_id": "pre-deploy-scan-id"
  }'
```

**2. Monthly Report**
```python
import requests

# Compare this month vs last month
response = requests.post(
    "https://api.devseo.com/api/v1/analysis/cwv-root-cause",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "current_crawl_id": current_month_scan_id,
        "previous_crawl_id": last_month_scan_id
    }
)

root_causes = response.json()["root_causes"]
for cause in root_causes:
    if cause["severity"] == "critical":
        print(f"CRITICAL: {cause['title']}")
        print(f"Fix: {cause['how_to_fix']['immediate'][0]}")
```

---

## 2. JavaScript Rendering Diagnostics

**70%+ of sites use React/Vue/Next.js. This tells them if JS breaks SEO.**

### Endpoint
```http
POST /api/v1/analysis/js-rendering
```

### When to Use
- Testing Next.js/React/Vue sites
- Diagnosing indexation issues
- Pre-launch SPA validation
- Post-deploy verification

### Request
```json
{
  "url": "https://example.com/page-to-test"
}
```

### Response
```json
{
  "url": "https://example.com",
  "analyzed_at": "2026-02-11T18:30:00Z",
  "pre_render": {
    "html_size_bytes": 1200,
    "has_content": false
  },
  "post_render": {
    "html_size_bytes": 45000,
    "render_time_ms": 2100,
    "resources_loaded": 47,
    "js_errors": ["TypeError: Cannot read property 'map' of undefined"]
  },
  "comparison": {
    "title": {
      "pre": null,
      "post": "Best SEO Tool for Arabic Sites",
      "changed": true
    },
    "meta_description": {
      "pre": null,
      "post": "DevSEO is the first real-time SEO monitoring platform...",
      "changed": true
    },
    "canonical": {
      "pre": null,
      "post": "https://example.com/",
      "changed": true
    },
    "h1": {
      "pre": [],
      "post": ["SEO Analysis Made Simple"],
      "changed": true
    },
    "links": {
      "pre_count": 0,
      "post_count": 47,
      "added": 47
    }
  },
  "performance_impact": {
    "dom_content_loaded_ms": 1800,
    "time_to_interactive_ms": 2100,
    "load_complete_ms": 3200,
    "assessment": "good",
    "impact_on_seo": "Excellent performance. Unlikely to hurt rankings."
  },
  "issues": [
    {
      "type": "title_js_dependent",
      "severity": "critical",
      "title": "Title Tag Only Appears After JavaScript",
      "description": "The <title> tag is empty before JavaScript runs...",
      "simple_explanation": "Your page title doesn't exist until JavaScript loads. Google might not wait long enough to see it.",
      "why_it_matters": "Title tag is the most important on-page SEO element...",
      "how_to_fix": [
        "1. Use server-side rendering (SSR) or static site generation (SSG)",
        "2. For Next.js: Use <Head> component or Metadata API",
        "3. Test fix: curl https://example.com | grep '<title>' should show title"
      ],
      "framework_specific_fixes": {
        "Next.js": "export const metadata = { title: 'Your Title' }",
        "React": "Use react-helmet-async with SSR",
        "Vue": "Use vue-meta or Nuxt.js"
      },
      "affected_elements": ["<title>"]
    },
    {
      "type": "empty_pre_render_content",
      "severity": "critical",
      "title": "Page Is Empty Before JavaScript Loads",
      "simple_explanation": "Your page is blank until JavaScript loads. Google may see nothing.",
      "business_impact": "Pages with no pre-rendered content often see 50-70% less organic traffic.",
      "google_guidance": "Google recommends 'dynamic rendering' is deprecated. Use SSR instead."
    }
  ],
  "severity": "critical",
  "recommendations": [
    {
      "priority": "critical",
      "title": "Implement Server-Side Rendering",
      "reason": "2 critical rendering issues detected",
      "action": "Move to SSR framework (Next.js, Nuxt, SvelteKit)",
      "estimated_effort": "1-2 weeks for migration",
      "impact": "High - will fix most rendering issues",
      "resources": [
        "Next.js SSR: https://nextjs.org/docs/basic-features/pages",
        "Google's SSR guide: https://developers.google.com/search/docs/advanced/javascript/javascript-seo-basics"
      ]
    }
  ]
}
```

### Example: CI/CD Integration

```yaml
# .github/workflows/seo-check.yml
name: SEO Pre-Render Check

on:
  pull_request:
    branches: [main]

jobs:
  seo-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check JS Rendering
        run: |
          RESPONSE=$(curl -X POST https://api.devseo.com/api/v1/analysis/js-rendering \
            -H "Authorization: Bearer ${{ secrets.DEVSEO_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"url": "${{ secrets.PREVIEW_URL }}"}')

          SEVERITY=$(echo $RESPONSE | jq -r '.severity')

          if [ "$SEVERITY" == "critical" ]; then
            echo "CRITICAL SEO ISSUES FOUND!"
            echo $RESPONSE | jq '.issues'
            exit 1
          fi
```

---

## 3. RTL/Arabic Technical Validation

**YOUR UNIQUE MOAT. Nobody else has this.**

### Endpoint
```http
POST /api/v1/analysis/rtl-validation
```

### When to Use
- Launching Arabic/RTL site
- Auditing multilingual sites
- Pre-deployment validation
- Competitive advantage for MENA market

### Request
```json
{
  "url": "https://example.com/ar",
  "html_content": "<html>...</html>" // optional, if not provided will fetch
}
```

### Response
```json
{
  "is_arabic_page": true,
  "has_arabic_content": true,
  "url": "https://example.com/ar",
  "issues": [
    {
      "type": "missing_dir_attribute",
      "severity": "critical",
      "title": "Missing dir='rtl' Attribute",
      "description": "The <html> or <body> tag must have dir='rtl' for Arabic content...",
      "simple_explanation": "Your Arabic text displays backwards because the page isn't marked as right-to-left.",
      "w3c_reference": "https://www.w3.org/International/questions/qa-html-dir",
      "visual_impact": "Text appears backwards, numbers misaligned, UI elements on wrong side",
      "how_to_fix": [
        "Add dir='rtl' to <html> tag: <html dir='rtl' lang='ar'>",
        "Or add to <body> tag: <body dir='rtl'>"
      ],
      "code_example": "<html dir=\"rtl\" lang=\"ar\">",
      "priority": 1
    },
    {
      "type": "incorrect_lang_code",
      "severity": "warning",
      "title": "Lang Attribute Mismatch: 'en' for Arabic Content",
      "simple_explanation": "Language code doesn't match the actual language used.",
      "how_to_fix": [
        "Change lang='en' to lang='ar' for generic Arabic",
        "Or use specific locale: ar-SA (Saudi), ar-EG (Egypt), ar-AE (UAE)"
      ],
      "priority": 2
    },
    {
      "type": "mixed_direction_no_markup",
      "severity": "warning",
      "title": "Mixed Arabic/English Text Without Bidirectional Markup",
      "simple_explanation": "Mixed language text might display incorrectly. Numbers and punctuation can appear in wrong places.",
      "how_to_fix": [
        "Wrap mixed-direction text in <bdi> tags: <bdi>Mixed text here</bdi>",
        "Or add dir='auto' to parent: <p dir='auto'>...</p>"
      ],
      "w3c_reference": "https://www.w3.org/International/articles/inline-bidi-markup/",
      "priority": 3
    }
  ],
  "severity": "critical",
  "summary": "🚨 2 CRITICAL issues must be fixed immediately:\n  • Missing dir='rtl' Attribute\n  • ...",
  "checklist": [
    {
      "order": 1,
      "priority": 1,
      "title": "Missing dir='rtl' Attribute",
      "severity": "critical",
      "quick_fix": "Add dir='rtl' to <html> tag",
      "estimated_time": "5-15 minutes"
    }
  ]
}
```

### Value Proposition

**Market Reality:**
- MENA digital advertising market: $3.5B+ (2024)
- Arabic is #4 most used language on internet
- **NO OTHER TOOL** validates RTL technical correctness

**What We Check:**
1. ✅ `dir` attribute correctness (critical for display)
2. ✅ `lang` codes (ar, ar-SA, ar-EG, etc)
3. ✅ Bidirectional text markup (<bdi>, <bdo>)
4. ✅ Hreflang validation for Arabic locales
5. ✅ Mixed LTR/RTL content issues
6. ✅ Arabic font optimization
7. ✅ Diacritic usage (readability)
8. ✅ Numeral system consistency

---

## 4. Webhook Alerts

**Real-time alerts when regressions are detected. ContentKing charges $139/mo for this.**

### Endpoint
```http
POST /api/v1/analysis/webhooks/configure
```

### Request
```json
{
  "website_id": "uuid-here",
  "channel": "slack", // slack, discord, teams, webhook, email
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "enabled": true
}
```

### Supported Channels

#### Slack
```json
{
  "channel": "slack",
  "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
}
```

**What You Get:**
- Rich formatted messages with color coding
- Severity emoji (🚨 critical, ⚠️ warning)
- Direct links to full reports
- Action buttons

#### Discord
```json
{
  "channel": "discord",
  "webhook_url": "https://discord.com/api/webhooks/123456789/XXXXXXXXXXXXXXXXXXXX"
}
```

**What You Get:**
- Embedded messages with color
- Issue summaries
- Quick fix suggestions

#### Microsoft Teams
```json
{
  "channel": "teams",
  "webhook_url": "https://outlook.office.com/webhook/..."
}
```

**What You Get:**
- Adaptive cards
- Actionable buttons
- Facts table with metrics

#### Generic Webhook
```json
{
  "channel": "webhook",
  "webhook_url": "https://your-api.com/seo-alerts"
}
```

**Payload:**
```json
{
  "event": "seo_regression_detected",
  "timestamp": "2026-02-11T18:30:00Z",
  "severity": "critical",
  "website": {
    "id": "uuid",
    "domain": "example.com",
    "url": "https://example.com"
  },
  "crawl": {
    "id": "uuid",
    "started_at": "2026-02-11T18:00:00Z",
    "seo_score": 78
  },
  "root_causes": [...],
  "report_url": "https://app.devseo.com/reports/uuid"
}
```

**Use Cases:**
- Zapier integration (create Jira ticket)
- Custom alerting pipeline
- PagerDuty integration
- Datadog/monitoring integration

---

## 5. Regression Diff

**Compare two scans and see exactly what changed.**

### Endpoint
```http
POST /api/v1/analysis/regression-diff
```

### Request
```json
{
  "current_crawl_id": "after-deploy-uuid",
  "previous_crawl_id": "before-deploy-uuid"
}
```

### Response
```json
{
  "current_crawl_id": "...",
  "previous_crawl_id": "...",
  "time_between_scans_hours": 2.5,
  "changes": {
    "seo_score": {
      "before": 85,
      "after": 78,
      "change": -7,
      "change_percent": -8.2
    },
    "performance_score": {
      "before": 90,
      "after": 85,
      "change": -5
    },
    "pages_scanned": {
      "before": 150,
      "after": 150,
      "change": 0
    }
  },
  "is_regression": true,
  "severity": "critical",
  "impact_assessment": "REGRESSION: SEO score changed -7 points (-8.2%)",
  "recommended_actions": [
    "Run CWV root cause analysis to identify specific issues",
    "Check JS rendering diagnostics if score dropped significantly",
    "Review recent deploys or content changes"
  ]
}
```

---

## 🎯 Complete Workflow Example

**Scenario:** Agency managing 20 client websites

```python
import requests

API_BASE = "https://api.devseo.com"
TOKEN = "your-api-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Configure webhooks for all clients
for client in clients:
    requests.post(
        f"{API_BASE}/api/v1/analysis/webhooks/configure",
        headers=headers,
        json={
            "website_id": client["website_id"],
            "channel": "slack",
            "webhook_url": client["slack_webhook"],
            "enabled": True
        }
    )

# 2. After each deploy, compare with baseline
def post_deploy_check(website_id, current_scan_id):
    # Get baseline scan
    baseline = get_last_known_good_scan(website_id)

    # Run regression diff
    diff = requests.post(
        f"{API_BASE}/api/v1/analysis/regression-diff",
        headers=headers,
        json={
            "current_crawl_id": current_scan_id,
            "previous_crawl_id": baseline["id"]
        }
    ).json()

    if diff["is_regression"]:
        # Get detailed root cause
        root_cause = requests.post(
            f"{API_BASE}/api/v1/analysis/cwv-root-cause",
            headers=headers,
            json={
                "current_crawl_id": current_scan_id,
                "previous_crawl_id": baseline["id"]
            }
        ).json()

        # Alert sent automatically via webhook
        # Also create Jira ticket
        create_jira_ticket(
            title=f"SEO Regression: {website_domain}",
            description=root_cause["summary"],
            priority="Critical" if root_cause["severity"] == "critical" else "High"
        )

# 3. Monthly Arabic site audit
def monthly_arabic_audit(websites):
    for site in websites:
        if site["language"] == "ar":
            validation = requests.post(
                f"{API_BASE}/api/v1/analysis/rtl-validation",
                headers=headers,
                json={"url": site["url"]}
            ).json()

            # Generate report
            critical_issues = [i for i in validation["issues"] if i["severity"] == "critical"]
            if critical_issues:
                send_client_report(site["client_email"], validation)
```

---

## 💰 Pricing Impact

**What these features justify:**

- **CWV Root Cause:** Saves 2-4 hours of manual debugging = $200-400 value per analysis
- **JS Rendering:** Catches SEO-breaking bugs before production = Prevents 50-70% traffic loss
- **RTL Validation:** Enables MENA market entry = $3.5B market opportunity
- **Real-time Alerts:** Catches issues in minutes vs days = Prevents ranking drops
- **Regression Diff:** Proves SEO ROI to stakeholders = Justifies continued investment

**Our pricing:** $99/month (Pro tier)
**Value delivered:** $500-1,000+/month
**ROI:** 5-10x

---

## 📊 API Rate Limits

- Free tier: 10 analyses/day
- Starter ($29/mo): 100 analyses/day
- Pro ($99/mo): Unlimited analyses
- Agency ($299/mo): Unlimited + priority queue

---

## 🚀 Get Started

1. Sign up at https://app.devseo.com
2. Get API token from dashboard
3. Run your first analysis
4. Set up webhooks for real-time alerts
5. Integrate into CI/CD

**Questions?** support@devseo.com

---

**Created:** February 11, 2026
**Last Updated:** February 11, 2026
**Status:** Production Ready

🎉 **These features make you UNIQUE. Ship them and win.**
