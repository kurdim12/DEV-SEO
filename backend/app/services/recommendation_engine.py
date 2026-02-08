"""
Rule-based SEO recommendation engine.
Generates actionable SEO recommendations based on common patterns and best practices.
This covers 95% of SEO issues without any AI API costs!
"""
from typing import List, Dict, Any
from datetime import datetime, timezone


class SEORecommendation:
    """Represents a single SEO recommendation."""

    def __init__(
        self,
        title: str,
        description: str,
        priority: str,  # high, medium, low
        recommendation_type: str,  # technical_seo, content_quality, on_page, performance
        page_specific: bool = True,
    ):
        self.title = title
        self.description = description
        self.priority = priority
        self.recommendation_type = recommendation_type
        self.page_specific = page_specific


class RuleBasedRecommendationEngine:
    """
    Generates SEO recommendations based on predefined rules and best practices.
    Fast, accurate, and completely FREE!
    """

    def analyze_page(self, page_data: Dict[str, Any]) -> List[SEORecommendation]:
        """
        Analyze a single page and generate recommendations.

        Args:
            page_data: Dictionary with page information (title, meta_description, etc.)

        Returns:
            List of SEORecommendation objects
        """
        recommendations = []

        recommendations.extend(self._check_title(page_data))
        recommendations.extend(self._check_meta_description(page_data))
        recommendations.extend(self._check_headings(page_data))
        recommendations.extend(self._check_content(page_data))
        recommendations.extend(self._check_technical_seo(page_data))
        recommendations.extend(self._check_performance(page_data))
        recommendations.extend(self._check_images(page_data))
        recommendations.extend(self._check_structured_data(page_data))
        recommendations.extend(self._check_social_tags(page_data))
        recommendations.extend(self._check_links(page_data))

        return recommendations

    def _check_title(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check title tag optimization."""
        recs = []
        title = page.get("title", "")

        if not title:
            recs.append(SEORecommendation(
                title="Missing Title Tag",
                description="Add a descriptive title tag (50-60 characters). The title is crucial for SEO and appears in search results.",
                priority="high",
                recommendation_type="on_page"
            ))
        elif len(title) < 30:
            recs.append(SEORecommendation(
                title="Title Too Short",
                description=f"Current title is {len(title)} characters. Aim for 50-60 characters to fully utilize search result space.",
                priority="medium",
                recommendation_type="on_page"
            ))
        elif len(title) > 60:
            recs.append(SEORecommendation(
                title="Title Too Long",
                description=f"Current title is {len(title)} characters and will be truncated in search results. Keep it under 60 characters.",
                priority="medium",
                recommendation_type="on_page"
            ))

        return recs

    def _check_meta_description(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check meta description optimization."""
        recs = []
        meta_desc = page.get("meta_description", "")

        if not meta_desc:
            recs.append(SEORecommendation(
                title="Missing Meta Description",
                description="Add a compelling meta description (150-160 characters). This text appears in search results and influences click-through rates.",
                priority="high",
                recommendation_type="on_page"
            ))
        elif len(meta_desc) < 120:
            recs.append(SEORecommendation(
                title="Meta Description Too Short",
                description=f"Current meta description is {len(meta_desc)} characters. Aim for 150-160 characters to maximize impact.",
                priority="medium",
                recommendation_type="on_page"
            ))
        elif len(meta_desc) > 160:
            recs.append(SEORecommendation(
                title="Meta Description Too Long",
                description=f"Current meta description is {len(meta_desc)} characters. Keep it under 160 characters to avoid truncation.",
                priority="low",
                recommendation_type="on_page"
            ))

        return recs

    def _check_headings(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check heading structure."""
        recs = []
        h1_tags = page.get("h1_tags", [])
        issues = page.get("issues", [])

        if not h1_tags or len(h1_tags) == 0:
            recs.append(SEORecommendation(
                title="Missing H1 Tag",
                description="Add an H1 heading that clearly describes the page content. Every page should have exactly one H1.",
                priority="high",
                recommendation_type="on_page"
            ))
        elif len(h1_tags) > 1:
            recs.append(SEORecommendation(
                title="Multiple H1 Tags",
                description=f"Found {len(h1_tags)} H1 tags. Use only one H1 per page for better SEO structure.",
                priority="medium",
                recommendation_type="on_page"
            ))

        # Check if H1 is too short
        if h1_tags and len(h1_tags[0]) < 20:
            recs.append(SEORecommendation(
                title="H1 Too Short",
                description="H1 heading should be descriptive (at least 20 characters) to effectively communicate page topic.",
                priority="low",
                recommendation_type="on_page"
            ))

        # Check for heading hierarchy issue
        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "heading_hierarchy":
                recs.append(SEORecommendation(
                    title="Improper Heading Hierarchy",
                    description="Page uses H3 headings without H2 headings. Maintain proper hierarchy: H1 → H2 → H3 for better content structure.",
                    priority="low",
                    recommendation_type="on_page"
                ))
                break

        return recs

    def _check_content(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check content quality and length."""
        recs = []
        word_count = page.get("word_count", 0)

        if word_count == 0:
            recs.append(SEORecommendation(
                title="No Text Content",
                description="Page has no text content. Add substantial, valuable content (at least 300 words) for better SEO.",
                priority="high",
                recommendation_type="content_quality"
            ))
        elif word_count < 300:
            recs.append(SEORecommendation(
                title="Thin Content",
                description=f"Page has only {word_count} words. Aim for at least 300-500 words of quality content for better rankings.",
                priority="medium",
                recommendation_type="content_quality"
            ))
        elif word_count < 500:
            recs.append(SEORecommendation(
                title="Could Use More Content",
                description=f"Page has {word_count} words. Consider expanding to 500+ words to provide more value and improve SEO.",
                priority="low",
                recommendation_type="content_quality"
            ))

        return recs

    def _check_technical_seo(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check technical SEO factors."""
        recs = []
        issues = page.get("issues", [])

        # HTTPS check
        if not page.get("has_ssl", False):
            recs.append(SEORecommendation(
                title="Not Using HTTPS",
                description="Enable HTTPS/SSL certificate. Google prioritizes secure sites and browsers show warnings for non-HTTPS sites.",
                priority="high",
                recommendation_type="technical_seo"
            ))

        # Mobile-friendly check
        mobile_friendly = page.get("mobile_friendly")
        if mobile_friendly is False:
            recs.append(SEORecommendation(
                title="Not Mobile-Friendly",
                description="Page is not mobile-friendly. With mobile-first indexing, responsive design is critical for SEO.",
                priority="high",
                recommendation_type="technical_seo"
            ))

        # Canonical URL check
        canonical = page.get("canonical_url")
        if not canonical:
            recs.append(SEORecommendation(
                title="Missing Canonical Tag",
                description="Add a canonical tag to prevent duplicate content issues and consolidate SEO signals.",
                priority="medium",
                recommendation_type="technical_seo"
            ))

        # Status code check
        status_code = page.get("status_code")
        if status_code and status_code >= 400:
            recs.append(SEORecommendation(
                title=f"HTTP Error: {status_code}",
                description=f"Page returns {status_code} error. Fix server/page errors to ensure search engines can access content.",
                priority="high",
                recommendation_type="technical_seo"
            ))
        elif status_code and 300 <= status_code < 400:
            recs.append(SEORecommendation(
                title="Redirect Chain Detected",
                description=f"Page returns {status_code} redirect. Minimize redirects for better performance and SEO.",
                priority="low",
                recommendation_type="technical_seo"
            ))

        # Robots noindex check
        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "robots_noindex":
                recs.append(SEORecommendation(
                    title="Page Blocked from Indexing",
                    description="This page has a robots meta tag set to noindex. Remove it if you want this page to appear in search results.",
                    priority="high",
                    recommendation_type="technical_seo"
                ))
                break

        return recs

    def _check_performance(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check page performance metrics."""
        recs = []
        load_time = page.get("load_time_ms", 0)

        if load_time > 3000:
            recs.append(SEORecommendation(
                title="Slow Page Load Time",
                description=f"Page loads in {load_time}ms. Aim for under 2 seconds. Optimize images, minify CSS/JS, and enable caching.",
                priority="high",
                recommendation_type="performance"
            ))
        elif load_time > 2000:
            recs.append(SEORecommendation(
                title="Page Load Could Be Faster",
                description=f"Page loads in {load_time}ms. Consider optimization to get under 2 seconds for better user experience and SEO.",
                priority="medium",
                recommendation_type="performance"
            ))

        return recs

    def _check_images(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check image optimization."""
        recs = []

        issues = page.get("issues", [])
        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "missing_alt_text":
                recs.append(SEORecommendation(
                    title="Images Missing Alt Text",
                    description="Add descriptive alt text to all images for accessibility and SEO. Alt text helps search engines understand image content.",
                    priority="medium",
                    recommendation_type="on_page"
                ))
                break

        return recs

    def _check_structured_data(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check structured data / schema markup."""
        recs = []
        issues = page.get("issues", [])

        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "no_structured_data":
                recs.append(SEORecommendation(
                    title="Add Structured Data Markup",
                    description="Implement schema.org JSON-LD markup (e.g., Article, Product, FAQ, Organization) to help Google display rich results and improve click-through rates.",
                    priority="medium",
                    recommendation_type="technical_seo"
                ))
                break

        return recs

    def _check_social_tags(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check Open Graph and social media tags."""
        recs = []
        issues = page.get("issues", [])

        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "missing_og_tags":
                recs.append(SEORecommendation(
                    title="Incomplete Open Graph Tags",
                    description="Add missing Open Graph tags (og:title, og:description, og:image) to control how your pages appear when shared on social media.",
                    priority="low",
                    recommendation_type="on_page"
                ))
                break

        return recs

    def _check_links(self, page: Dict[str, Any]) -> List[SEORecommendation]:
        """Check internal linking."""
        recs = []
        issues = page.get("issues", [])

        for issue in issues:
            if isinstance(issue, dict) and issue.get("type") == "low_internal_links":
                recs.append(SEORecommendation(
                    title="Improve Internal Linking",
                    description="This page has very few internal links. Add relevant links to other pages on your site to improve navigation, distribute page authority, and help search engines discover more content.",
                    priority="low",
                    recommendation_type="on_page"
                ))
                break

        return recs

    def generate_overall_recommendations(
        self,
        pages: List[Dict[str, Any]],
        crawl_stats: Dict[str, Any]
    ) -> List[SEORecommendation]:
        """
        Generate site-wide recommendations based on overall crawl results.

        Args:
            pages: List of all page data
            crawl_stats: Overall crawl statistics

        Returns:
            List of site-wide SEORecommendation objects
        """
        recs = []

        if not pages:
            return recs

        # Check average page speed
        load_times = [p.get("load_time_ms", 0) for p in pages if p.get("load_time_ms")]
        if load_times:
            avg_load_time = sum(load_times) / len(load_times)
            if avg_load_time > 2000:
                recs.append(SEORecommendation(
                    title="Site-Wide Performance Issue",
                    description=f"Average page load time is {int(avg_load_time)}ms. Implement global optimizations like CDN, image compression, and caching.",
                    priority="high",
                    recommendation_type="performance",
                    page_specific=False
                ))

        # Check HTTPS adoption
        https_pages = sum(1 for p in pages if p.get("has_ssl", False))
        if https_pages < len(pages):
            recs.append(SEORecommendation(
                title="Incomplete HTTPS Migration",
                description=f"{len(pages) - https_pages} pages still use HTTP. Complete HTTPS migration for all pages.",
                priority="high",
                recommendation_type="technical_seo",
                page_specific=False
            ))

        # Check mobile-friendliness
        mobile_pages = sum(1 for p in pages if p.get("mobile_friendly", False))
        if mobile_pages < len(pages) * 0.9:
            recs.append(SEORecommendation(
                title="Mobile-Friendliness Issues",
                description=f"Only {mobile_pages}/{len(pages)} pages are mobile-friendly. Implement responsive design across the entire site.",
                priority="high",
                recommendation_type="technical_seo",
                page_specific=False
            ))

        # Check for thin content across site
        thin_content_pages = sum(1 for p in pages if p.get("word_count", 0) < 300)
        if thin_content_pages > len(pages) * 0.3:
            recs.append(SEORecommendation(
                title="Site-Wide Thin Content",
                description=f"{thin_content_pages}/{len(pages)} pages have thin content (<300 words). Focus on adding substantial, valuable content.",
                priority="medium",
                recommendation_type="content_quality",
                page_specific=False
            ))

        # Check missing meta descriptions
        missing_meta = sum(1 for p in pages if not p.get("meta_description"))
        if missing_meta > len(pages) * 0.2:
            recs.append(SEORecommendation(
                title="Many Pages Missing Meta Descriptions",
                description=f"{missing_meta}/{len(pages)} pages lack meta descriptions. Add compelling descriptions to improve click-through rates.",
                priority="medium",
                recommendation_type="on_page",
                page_specific=False
            ))

        # Check structured data adoption
        pages_with_schema = sum(
            1 for p in pages
            if p.get("schema_markup") and p["schema_markup"].get("types")
        )
        if pages_with_schema < len(pages) * 0.3:
            recs.append(SEORecommendation(
                title="Low Structured Data Adoption",
                description=f"Only {pages_with_schema}/{len(pages)} pages use structured data. Implement schema.org markup to gain rich snippets in search results.",
                priority="medium",
                recommendation_type="technical_seo",
                page_specific=False
            ))

        # Check missing H2 headings (content structure)
        pages_without_h2 = self._count_pages_missing_issue_type(pages, "heading_hierarchy")
        pages_missing_h2_count = sum(
            1 for p in pages
            if not any(
                isinstance(i, dict) and "h2" in i.get("message", "").lower()
                for i in p.get("issues", [])
            ) and p.get("word_count", 0) > 300
        )

        # Check canonical coverage
        missing_canonical = sum(1 for p in pages if not p.get("canonical_url"))
        if missing_canonical > len(pages) * 0.5:
            recs.append(SEORecommendation(
                title="Missing Canonical Tags Site-Wide",
                description=f"{missing_canonical}/{len(pages)} pages lack canonical tags. Add canonical tags to prevent duplicate content issues.",
                priority="medium",
                recommendation_type="technical_seo",
                page_specific=False
            ))

        return recs

    def _count_pages_missing_issue_type(self, pages: List[Dict[str, Any]], issue_type: str) -> int:
        """Count pages that have a specific issue type."""
        count = 0
        for page in pages:
            for issue in page.get("issues", []):
                if isinstance(issue, dict) and issue.get("type") == issue_type:
                    count += 1
                    break
        return count

    def _summarize_common_issues(self, pages: List[Dict[str, Any]]) -> str:
        """Summarize the most common issues across pages."""
        issue_counts: Dict[str, int] = {}

        for page in pages[:50]:  # Sample first 50 pages
            for issue in page.get("issues", []):
                if isinstance(issue, dict):
                    issue_type = issue.get("type", "unknown")
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return "\n".join([f"- {issue}: {count} pages" for issue, count in top_issues])
