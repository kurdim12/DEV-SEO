"""
Web crawler service for crawling websites and extracting content.
"""
import asyncio
import xml.etree.ElementTree as ET
import ipaddress
import socket
from typing import Set, List, Dict, Optional, Callable, Awaitable
from urllib.parse import urlparse
import time

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.utils.robots_parser import RobotsParser
from app.utils.url_helpers import (
    normalize_url,
    ensure_absolute_url,
    should_crawl_url,
    get_base_url,
)

# SSRF protection: blocked IP address ranges
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),          # Private
    ipaddress.ip_network("172.16.0.0/12"),       # Private
    ipaddress.ip_network("192.168.0.0/16"),      # Private
    ipaddress.ip_network("127.0.0.0/8"),         # Loopback
    ipaddress.ip_network("169.254.0.0/16"),      # Link-local
    ipaddress.ip_network("::1/128"),             # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),            # IPv6 private
]


def _is_safe_url(url: str) -> bool:
    """
    Reject URLs resolving to private/loopback/link-local addresses (SSRF protection).
    Returns True if safe, False if should be blocked.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return False

    # Block raw IPs that are private
    try:
        addr = ipaddress.ip_address(hostname)
        return not any(addr in net for net in BLOCKED_NETWORKS)
    except ValueError:
        pass  # It's a hostname, not a raw IP

    # Resolve hostname and check all resolved IPs
    try:
        resolved = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in resolved:
            addr = ipaddress.ip_address(sockaddr[0])
            if any(addr in net for net in BLOCKED_NETWORKS):
                return False
    except socket.gaierror:
        return False  # Can't resolve = block

    return True


class CrawlerResult:
    """Result from crawling a single page."""

    def __init__(
        self,
        url: str,
        status_code: int,
        html: str,
        load_time_ms: int,
        headers: Optional[Dict[str, str]] = None,
        redirect_chain: Optional[List[str]] = None,
        error: Optional[str] = None,
        outgoing_links: Optional[List[str]] = None,
    ):
        self.url = url
        self.status_code = status_code
        self.html = html
        self.load_time_ms = load_time_ms
        self.headers = headers or {}
        self.redirect_chain = redirect_chain or []
        self.error = error
        self.outgoing_links = outgoing_links or []


class WebCrawler:
    """
    Web crawler that respects robots.txt and rate limits.
    Supports sitemap discovery, redirect tracking, and content-type filtering.
    """

    def __init__(self, domain: str, max_pages: int = 50):
        """
        Initialize crawler.

        Args:
            domain: Domain to crawl (e.g., example.com)
            max_pages: Maximum number of pages to crawl
        """
        self.domain = domain
        self.max_pages = max_pages
        self.start_url = f"https://{domain}"

        # SSRF protection: validate domain doesn't resolve to private IPs
        if not _is_safe_url(self.start_url):
            raise ValueError(f"Domain {domain!r} resolves to a private/internal address")

        self.robots_parser = RobotsParser(settings.CRAWLER_USER_AGENT)
        self.visited_urls: Set[str] = set()
        self.to_crawl: List[str] = []
        self.results: List[CrawlerResult] = []

        # Rate limiting
        self.last_request_time = 0.0
        self.min_delay = 1.0 / settings.CRAWLER_MAX_REQUESTS_PER_SECOND
        self._effective_delay: Optional[float] = None

    async def crawl(
        self, progress_callback: Optional[Callable[[int, int], Awaitable[None]]] = None
    ) -> List[CrawlerResult]:
        """
        Start crawling the website.

        Args:
            progress_callback: Optional async callback(pages_crawled, pages_total)
                called after each page is crawled

        Returns:
            List of CrawlerResult objects
        """
        async with httpx.AsyncClient(
            timeout=settings.CRAWLER_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": settings.CRAWLER_USER_AGENT},
        ) as client:
            # Discover URLs from sitemap first
            sitemap_urls = await self._fetch_sitemap_urls(client)

            # Build seed list: homepage + sitemap URLs
            seed_urls = [self.start_url] + sitemap_urls
            for url in seed_urls:
                normalized = normalize_url(url)
                if normalized not in self.to_crawl:
                    self.to_crawl.append(normalized)

            # Check robots.txt for crawl-delay (must be fetched first via can_fetch)
            await self.robots_parser.can_fetch(self.start_url)
            crawl_delay = self.robots_parser.get_crawl_delay(self.start_url)
            if crawl_delay:
                self._effective_delay = max(float(crawl_delay), self.min_delay)

            while self.to_crawl and len(self.visited_urls) < self.max_pages:
                url = self.to_crawl.pop(0)

                # Skip if already visited
                if url in self.visited_urls:
                    continue

                # Check robots.txt
                if not await self.robots_parser.can_fetch(url):
                    continue

                # Rate limiting
                await self._apply_rate_limit()

                # Crawl page
                result = await self._crawl_page(client, url)
                self.visited_urls.add(url)
                self.results.append(result)

                # Call progress callback if provided
                if progress_callback:
                    pages_crawled = len(self.visited_urls)
                    pages_total = min(
                        len(self.visited_urls) + len(self.to_crawl), self.max_pages
                    )
                    await progress_callback(pages_crawled, pages_total)

                # Extract links if successful HTML page
                if result.status_code == 200 and not result.error and result.html:
                    links = self._extract_links(result.html, url)
                    for link in links:
                        if link not in self.visited_urls and link not in self.to_crawl:
                            self.to_crawl.append(link)

        return self.results

    async def _fetch_sitemap_urls(self, client: httpx.AsyncClient) -> List[str]:
        """Discover and parse sitemap.xml to get URLs for crawling."""
        urls: List[str] = []
        sitemap_locations = [
            f"{self.start_url}/sitemap.xml",
            f"{self.start_url}/sitemap_index.xml",
        ]

        # Check robots.txt for Sitemap directive
        try:
            response = await client.get(f"{self.start_url}/robots.txt")
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        if sitemap_url not in sitemap_locations:
                            sitemap_locations.insert(0, sitemap_url)
        except Exception:
            pass

        for sitemap_url in sitemap_locations[:3]:
            try:
                response = await client.get(sitemap_url)
                if response.status_code == 200:
                    parsed_urls = self._parse_sitemap(response.text)
                    urls.extend(parsed_urls)
                    if urls:
                        break
            except Exception:
                continue

        # Filter to same domain and limit count
        filtered = [u for u in urls if should_crawl_url(u, self.domain)]
        return filtered[: self.max_pages * 2]

    def _parse_sitemap(self, xml_content: str) -> List[str]:
        """Parse sitemap XML and extract URLs."""
        urls: List[str] = []
        try:
            root = ET.fromstring(xml_content)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Regular sitemap URLs
            for url_elem in root.findall(".//sm:url/sm:loc", ns):
                if url_elem.text:
                    urls.append(url_elem.text.strip())

            # If no URLs found, try without namespace
            if not urls:
                for loc in root.iter("loc"):
                    if loc.text:
                        urls.append(loc.text.strip())
        except Exception:
            pass
        return urls

    async def _crawl_page(self, client: httpx.AsyncClient, url: str) -> CrawlerResult:
        """
        Crawl a single page.

        Args:
            client: HTTP client
            url: URL to crawl

        Returns:
            CrawlerResult object
        """
        start_time = time.time()

        try:
            response = await client.get(url)
            load_time_ms = int((time.time() - start_time) * 1000)

            # Track redirect chain
            redirect_chain = [str(r.url) for r in response.history]

            # Check content type - only process HTML pages
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and response.status_code == 200:
                return CrawlerResult(
                    url=str(response.url),
                    status_code=response.status_code,
                    html="",
                    load_time_ms=load_time_ms,
                    headers=dict(response.headers),
                    redirect_chain=redirect_chain,
                    outgoing_links=[],
                )

            # Extract outgoing links for broken link detection
            outgoing_links = self._extract_links(response.text, str(response.url))

            return CrawlerResult(
                url=str(response.url),
                status_code=response.status_code,
                html=response.text,
                load_time_ms=load_time_ms,
                headers=dict(response.headers),
                redirect_chain=redirect_chain,
                outgoing_links=outgoing_links,
            )
        except Exception as e:
            load_time_ms = int((time.time() - start_time) * 1000)
            return CrawlerResult(
                url=url,
                status_code=0,
                html="",
                load_time_ms=load_time_ms,
                error=str(e),
            )

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = []

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()
                # Skip fragments, javascript, mailto, tel
                if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue

                absolute_url = ensure_absolute_url(href, base_url)
                normalized_url = normalize_url(absolute_url)

                if should_crawl_url(normalized_url, self.domain):
                    links.append(normalized_url)

            return links
        except Exception:
            return []

    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        delay = self._effective_delay or self.min_delay
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)

        self.last_request_time = time.time()

    def get_progress(self) -> Dict[str, int]:
        """
        Get current crawl progress.

        Returns:
            Dictionary with pages_crawled and pages_total
        """
        return {
            "pages_crawled": len(self.visited_urls),
            "pages_total": min(len(self.visited_urls) + len(self.to_crawl), self.max_pages),
        }
