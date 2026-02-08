"""
Robots.txt parser for respecting website crawling rules.
"""
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import httpx
from typing import Optional


class RobotsParser:
    """Parser for robots.txt files with caching."""

    def __init__(self, user_agent: str):
        """
        Initialize robots parser.

        Args:
            user_agent: User agent string to check permissions for
        """
        self.user_agent = user_agent
        self._parsers: dict[str, RobotFileParser] = {}

    async def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if URL can be fetched, False otherwise
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base_url, "/robots.txt")

        # Get or create parser for this domain
        if base_url not in self._parsers:
            parser = RobotFileParser()
            parser.set_url(robots_url)

            # Fetch robots.txt
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(robots_url, follow_redirects=True)
                    if response.status_code == 200:
                        parser.parse(response.text.splitlines())
                    else:
                        # If robots.txt not found, allow all
                        parser.parse([])
            except Exception:
                # If error fetching robots.txt, allow all (be permissive)
                parser.parse([])

            self._parsers[base_url] = parser

        # Check if URL can be fetched
        return self._parsers[base_url].can_fetch(self.user_agent, url)

    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay from robots.txt for a URL.

        Args:
            url: URL to check crawl delay for

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        if base_url in self._parsers:
            return self._parsers[base_url].crawl_delay(self.user_agent)
        return None
