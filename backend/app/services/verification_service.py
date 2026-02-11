"""
Domain verification service for validating website ownership.
"""
import dns.resolver
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for verifying domain ownership via DNS, meta tag, or file upload."""

    def __init__(self):
        self.timeout = 10.0

    async def verify_dns(self, domain: str, token: str) -> Tuple[bool, str]:
        """
        Verify domain ownership via DNS TXT record.

        Args:
            domain: The domain to verify (e.g., "example.com")
            token: The verification token to look for

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Remove protocol if present
            domain = domain.replace("http://", "").replace("https://", "")
            domain = domain.split("/")[0]  # Remove path if present

            # Try both with and without _devseo-verify prefix
            records_to_check = [
                f"_devseo-verify.{domain}",
                domain
            ]

            for record in records_to_check:
                try:
                    answers = dns.resolver.resolve(record, 'TXT')
                    for rdata in answers:
                        txt_value = str(rdata).strip('"')
                        if token in txt_value or txt_value == token:
                            logger.info(f"✅ DNS verification successful for {domain}")
                            return True, f"DNS TXT record verified successfully on {record}"
                except dns.resolver.NXDOMAIN:
                    continue
                except dns.resolver.NoAnswer:
                    continue

            return False, f"DNS TXT record not found. Add a TXT record at _devseo-verify.{domain} or at root domain with value: {token}"

        except Exception as e:
            logger.error(f"DNS verification error for {domain}: {e}")
            return False, f"DNS verification failed: {str(e)}"

    async def verify_meta_tag(self, url: str, token: str) -> Tuple[bool, str]:
        """
        Verify domain ownership via meta tag in homepage HTML.

        Args:
            url: The website URL (e.g., "https://example.com")
            token: The verification token to look for

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            # Fetch homepage
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "DevSEO-Verification-Bot/1.0"
                })

                if response.status_code != 200:
                    return False, f"Failed to fetch homepage (status code: {response.status_code})"

                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for meta tag with name="devseo-verification"
                meta_tag = soup.find('meta', attrs={'name': 'devseo-verification'})

                if meta_tag and meta_tag.get('content'):
                    if token in meta_tag.get('content') or meta_tag.get('content') == token:
                        logger.info(f"✅ Meta tag verification successful for {url}")
                        return True, "Meta tag verified successfully"

                return False, f"Meta tag not found. Add this to your homepage <head>: <meta name=\"devseo-verification\" content=\"{token}\">"

        except httpx.TimeoutException:
            return False, "Timeout while fetching homepage. Please try again."
        except Exception as e:
            logger.error(f"Meta tag verification error for {url}: {e}")
            return False, f"Meta tag verification failed: {str(e)}"

    async def verify_file(self, url: str, token: str) -> Tuple[bool, str]:
        """
        Verify domain ownership via verification file.

        Args:
            url: The website URL (e.g., "https://example.com")
            token: The verification token to look for

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            # Parse base URL
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            # Try both .well-known and root directory
            file_urls = [
                f"{base_url}/.well-known/devseo-verify.txt",
                f"{base_url}/devseo-verify.txt"
            ]

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                for file_url in file_urls:
                    try:
                        response = await client.get(file_url, headers={
                            "User-Agent": "DevSEO-Verification-Bot/1.0"
                        })

                        if response.status_code == 200:
                            content = response.text.strip()
                            if token in content or content == token:
                                logger.info(f"✅ File verification successful for {url}")
                                return True, f"Verification file found and verified at {file_url}"

                    except httpx.HTTPStatusError:
                        continue

            return False, f"Verification file not found. Upload a file at {base_url}/.well-known/devseo-verify.txt containing: {token}"

        except httpx.TimeoutException:
            return False, "Timeout while fetching verification file. Please try again."
        except Exception as e:
            logger.error(f"File verification error for {url}: {e}")
            return False, f"File verification failed: {str(e)}"

    async def verify_domain(
        self,
        url: str,
        token: str,
        method: str = "dns"
    ) -> Tuple[bool, str]:
        """
        Verify domain ownership using specified method.

        Args:
            url: The website URL
            token: The verification token
            method: Verification method ("dns", "meta", or "file")

        Returns:
            Tuple of (success: bool, message: str)
        """
        if method == "dns":
            # Extract domain from URL
            domain = url.replace("http://", "").replace("https://", "").split("/")[0]
            return await self.verify_dns(domain, token)
        elif method == "meta":
            return await self.verify_meta_tag(url, token)
        elif method == "file":
            return await self.verify_file(url, token)
        else:
            return False, f"Invalid verification method: {method}. Use 'dns', 'meta', or 'file'."


# Global instance
verification_service = VerificationService()
