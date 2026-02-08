"""
SEO analyzer service for analyzing pages and generating SEO scores.
"""
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re


class SEOIssue:
    """Represents a single SEO issue."""

    def __init__(self, type: str, severity: str, message: str, suggestion: Optional[str] = None):
        self.type = type
        self.severity = severity  # critical, warning, info
        self.message = message
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class SEOAnalysisResult:
    """Result from analyzing a single page."""

    def __init__(self, url: str):
        self.url = url
        self.title: Optional[str] = None
        self.meta_description: Optional[str] = None
        self.h1_tags: List[str] = []
        self.h2_tags: List[str] = []
        self.h3_tags: List[str] = []
        self.word_count: int = 0
        self.mobile_friendly: bool = False
        self.has_ssl: bool = False
        self.canonical_url: Optional[str] = None
        self.og_tags: Dict[str, str] = {}
        self.twitter_tags: Dict[str, str] = {}
        self.schema_markup: Dict = {}
        self.structured_data_types: List[str] = []
        self.internal_links_count: int = 0
        self.external_links_count: int = 0
        self.images_count: int = 0
        self.images_without_alt: int = 0
        self.robots_meta: Optional[str] = None
        self.security_headers: Dict[str, bool] = {}
        self.issues: List[SEOIssue] = []
        self.seo_score: int = 0


class SEOAnalyzer:
    """
    Analyzes HTML content and generates SEO scores and recommendations.
    """

    def analyze(
        self,
        html: str,
        url: str,
        status_code: int,
        headers: Optional[Dict[str, str]] = None,
    ) -> SEOAnalysisResult:
        """
        Analyze HTML content and generate SEO report.

        Args:
            html: HTML content to analyze
            url: Page URL
            status_code: HTTP status code
            headers: HTTP response headers for security analysis

        Returns:
            SEOAnalysisResult object
        """
        result = SEOAnalysisResult(url)
        response_headers = headers or {}

        # Check SSL
        result.has_ssl = url.startswith("https://")
        if not result.has_ssl:
            result.issues.append(
                SEOIssue(
                    "no_ssl",
                    "critical",
                    "Page does not use HTTPS",
                    "Enable HTTPS/SSL for better security and SEO",
                )
            )

        # Parse HTML
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            result.issues.append(
                SEOIssue("parse_error", "critical", f"Failed to parse HTML: {str(e)}")
            )
            return result

        # Analyze title
        self._analyze_title(soup, result)

        # Analyze meta description
        self._analyze_meta_description(soup, result)

        # Analyze headings (H1, H2, H3)
        self._analyze_headings(soup, result)

        # Analyze content
        self._analyze_content(soup, result)

        # Analyze mobile-friendliness
        self._analyze_mobile(soup, result)

        # Analyze images
        self._analyze_images(soup, result)

        # Analyze canonical
        self._analyze_canonical(soup, result, url)

        # Analyze Open Graph tags
        self._analyze_og_tags(soup, result)

        # Analyze Twitter Card tags
        self._analyze_twitter_tags(soup, result)

        # Analyze structured data (JSON-LD, Microdata)
        self._analyze_structured_data(soup, result)

        # Analyze robots meta tag
        self._analyze_robots_meta(soup, result)

        # Analyze internal/external links
        self._analyze_links(soup, result, url)

        # Analyze security headers from HTTP response
        self._analyze_security_headers(response_headers, result)

        # Analyze favicon
        self._analyze_favicon(soup, result)

        # Calculate SEO score
        result.seo_score = self._calculate_score(result)

        return result

    def _analyze_title(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze page title."""
        title_tag = soup.find("title")

        if not title_tag or not title_tag.string:
            result.issues.append(
                SEOIssue(
                    "missing_title",
                    "critical",
                    "Page is missing a title tag",
                    "Add a descriptive title tag between 50-60 characters",
                )
            )
            return

        title = title_tag.string.strip()
        result.title = title

        if len(title) < 30:
            result.issues.append(
                SEOIssue(
                    "title_too_short",
                    "warning",
                    f"Page title is only {len(title)} characters long",
                    "Aim for 50-60 characters for optimal SEO",
                )
            )
        elif len(title) > 60:
            result.issues.append(
                SEOIssue(
                    "title_too_long",
                    "warning",
                    f"Page title is {len(title)} characters long (may be truncated)",
                    "Keep title under 60 characters to avoid truncation in search results",
                )
            )

    def _analyze_meta_description(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze meta description."""
        meta_desc = soup.find("meta", attrs={"name": "description"})

        if not meta_desc or not meta_desc.get("content"):
            result.issues.append(
                SEOIssue(
                    "missing_meta_description",
                    "warning",
                    "Page is missing a meta description",
                    "Add a meta description between 150-160 characters",
                )
            )
            return

        description = meta_desc["content"].strip()
        result.meta_description = description

        if len(description) < 70:
            result.issues.append(
                SEOIssue(
                    "meta_description_too_short",
                    "info",
                    f"Meta description is only {len(description)} characters long",
                    "Aim for 150-160 characters for optimal display in search results",
                )
            )
        elif len(description) > 160:
            result.issues.append(
                SEOIssue(
                    "meta_description_too_long",
                    "info",
                    f"Meta description is {len(description)} characters long",
                    "Keep meta description under 160 characters",
                )
            )

    def _analyze_headings(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze heading structure (H1, H2, H3)."""
        # H1 tags
        h1_tags = soup.find_all("h1")
        result.h1_tags = [h.get_text().strip() for h in h1_tags if h.get_text().strip()]

        if not result.h1_tags:
            result.issues.append(
                SEOIssue(
                    "missing_h1",
                    "critical",
                    "Page is missing an H1 heading",
                    "Add a single H1 heading that describes the page content",
                )
            )
        elif len(result.h1_tags) > 1:
            result.issues.append(
                SEOIssue(
                    "multiple_h1",
                    "warning",
                    f"Page has {len(result.h1_tags)} H1 headings",
                    "Use only one H1 heading per page for better SEO",
                )
            )

        # H2 and H3 tags
        h2_tags = soup.find_all("h2")
        result.h2_tags = [h.get_text().strip() for h in h2_tags if h.get_text().strip()]

        h3_tags = soup.find_all("h3")
        result.h3_tags = [h.get_text().strip() for h in h3_tags if h.get_text().strip()]

        # Check heading hierarchy - warn if H3 exists but no H2
        if result.h3_tags and not result.h2_tags:
            result.issues.append(
                SEOIssue(
                    "heading_hierarchy",
                    "info",
                    "Page uses H3 headings but has no H2 headings",
                    "Use proper heading hierarchy (H1 > H2 > H3) for better structure",
                )
            )

    def _analyze_content(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze page content."""
        # Remove script and style elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        text = soup.get_text()
        words = re.findall(r'\w+', text)
        result.word_count = len(words)

        if result.word_count < 300:
            result.issues.append(
                SEOIssue(
                    "thin_content",
                    "warning",
                    f"Page has only {result.word_count} words",
                    "Add more quality content (aim for at least 300 words)",
                )
            )

    def _analyze_mobile(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze mobile-friendliness."""
        viewport_meta = soup.find("meta", attrs={"name": "viewport"})
        result.mobile_friendly = bool(viewport_meta)

        if not result.mobile_friendly:
            result.issues.append(
                SEOIssue(
                    "no_viewport_meta",
                    "critical",
                    "Page is missing viewport meta tag for mobile devices",
                    'Add <meta name="viewport" content="width=device-width, initial-scale=1">',
                )
            )

    def _analyze_images(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze images for alt text and optimization."""
        images = soup.find_all("img")
        result.images_count = len(images)
        images_without_alt = [img for img in images if not img.get("alt")]
        result.images_without_alt = len(images_without_alt)

        if images_without_alt:
            result.issues.append(
                SEOIssue(
                    "missing_alt_text",
                    "warning",
                    f"{len(images_without_alt)} image(s) missing alt text",
                    "Add descriptive alt text to all images for accessibility and SEO",
                )
            )

    def _analyze_canonical(self, soup: BeautifulSoup, result: SEOAnalysisResult, url: str):
        """Analyze canonical URL."""
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical and canonical.get("href"):
            result.canonical_url = canonical["href"]
        else:
            result.issues.append(
                SEOIssue(
                    "missing_canonical",
                    "info",
                    "Page is missing a canonical tag",
                    "Add a canonical tag to prevent duplicate content issues",
                )
            )

    def _analyze_og_tags(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze Open Graph tags."""
        og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
        for tag in og_tags:
            property_name = tag.get("property")
            content = tag.get("content")
            if property_name and content:
                result.og_tags[property_name] = content

        # Check for essential OG tags
        essential_og = ["og:title", "og:description", "og:image"]
        missing_og = [tag for tag in essential_og if tag not in result.og_tags]
        if missing_og:
            result.issues.append(
                SEOIssue(
                    "missing_og_tags",
                    "info",
                    f"Missing Open Graph tags: {', '.join(missing_og)}",
                    "Add OG tags to improve social media sharing appearance",
                )
            )

    def _analyze_twitter_tags(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze Twitter Card meta tags."""
        twitter_tags = soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")})
        for tag in twitter_tags:
            name = tag.get("name")
            content = tag.get("content")
            if name and content:
                result.twitter_tags[name] = content

    def _analyze_structured_data(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Detect JSON-LD and Microdata structured data."""
        types_found: List[str] = []

        # JSON-LD
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        schema_type = data.get("@type", "")
                        if schema_type:
                            types_found.append(str(schema_type))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                schema_type = item.get("@type", "")
                                if schema_type:
                                    types_found.append(str(schema_type))
            except (json.JSONDecodeError, Exception):
                pass

        # Microdata (itemtype attribute)
        microdata = soup.find_all(attrs={"itemtype": True})
        for elem in microdata:
            itemtype = elem.get("itemtype", "")
            if "schema.org/" in itemtype:
                schema_type = itemtype.split("schema.org/")[-1]
                if schema_type and schema_type not in types_found:
                    types_found.append(schema_type)

        result.structured_data_types = types_found
        if types_found:
            result.schema_markup = {"types": types_found}

        if not types_found:
            result.issues.append(
                SEOIssue(
                    "no_structured_data",
                    "info",
                    "No structured data (JSON-LD/Microdata) found",
                    "Add schema.org markup to help search engines understand your content",
                )
            )

    def _analyze_robots_meta(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Analyze robots meta tag for noindex/nofollow directives."""
        robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.IGNORECASE)})
        if robots_meta and robots_meta.get("content"):
            content = robots_meta["content"].lower()
            result.robots_meta = content

            if "noindex" in content:
                result.issues.append(
                    SEOIssue(
                        "robots_noindex",
                        "critical",
                        "Page has robots meta tag set to noindex",
                        "Remove noindex directive if you want this page to appear in search results",
                    )
                )

    def _analyze_links(self, soup: BeautifulSoup, result: SEOAnalysisResult, url: str):
        """Count internal and external links."""
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            internal = 0
            external = 0

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()
                if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                if href.startswith("/") or href.startswith("./") or href.startswith("../"):
                    internal += 1
                else:
                    try:
                        link_domain = urlparse(href).netloc.lower()
                        if link_domain.startswith("www."):
                            link_domain = link_domain[4:]
                        if link_domain == domain or not link_domain:
                            internal += 1
                        else:
                            external += 1
                    except Exception:
                        internal += 1

            result.internal_links_count = internal
            result.external_links_count = external

            if internal < 2:
                result.issues.append(
                    SEOIssue(
                        "low_internal_links",
                        "info",
                        f"Page has only {internal} internal link(s)",
                        "Add more internal links to improve site navigation and distribute link equity",
                    )
                )
        except Exception:
            pass

    def _analyze_security_headers(self, headers: Dict[str, str], result: SEOAnalysisResult):
        """Check important security headers."""
        headers_lower = {k.lower(): v for k, v in headers.items()}

        security_checks = {
            "x-frame-options": "x-frame-options" in headers_lower,
            "x-content-type-options": "x-content-type-options" in headers_lower,
            "strict-transport-security": "strict-transport-security" in headers_lower,
            "content-security-policy": "content-security-policy" in headers_lower,
        }
        result.security_headers = security_checks

        missing = [h for h, present in security_checks.items() if not present]
        if missing and result.has_ssl:
            result.issues.append(
                SEOIssue(
                    "missing_security_headers",
                    "info",
                    f"Missing security headers: {', '.join(missing)}",
                    "Add security headers to improve trust signals and site security",
                )
            )

    def _analyze_favicon(self, soup: BeautifulSoup, result: SEOAnalysisResult):
        """Check for favicon."""
        favicon = soup.find("link", rel=lambda r: r and "icon" in r)
        if not favicon:
            # Also check for shortcut icon
            favicon = soup.find("link", attrs={"rel": "shortcut icon"})

        if not favicon:
            result.issues.append(
                SEOIssue(
                    "missing_favicon",
                    "info",
                    "No favicon found",
                    "Add a favicon to improve brand recognition in browser tabs",
                )
            )

    def _calculate_score(self, result: SEOAnalysisResult) -> int:
        """
        Calculate overall SEO score (0-100).

        Args:
            result: SEOAnalysisResult object

        Returns:
            Score from 0-100
        """
        score = 100

        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == "critical":
                score -= 15
            elif issue.severity == "warning":
                score -= 8
            elif issue.severity == "info":
                score -= 2

        # Bonuses for good practices
        if result.title and 50 <= len(result.title) <= 60:
            score += 3

        if result.meta_description and 120 <= len(result.meta_description) <= 160:
            score += 3

        if result.word_count >= 500:
            score += 3

        if result.h2_tags:
            score += 2

        if result.structured_data_types:
            score += 3

        if result.og_tags.get("og:title") and result.og_tags.get("og:description"):
            score += 2

        if result.canonical_url:
            score += 2

        # Ensure score is in valid range
        return max(0, min(100, score))
