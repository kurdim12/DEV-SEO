"""
Enhanced RTL/Arabic Technical Validator
COMPETITIVE EDGE: NOBODY else validates Arabic/RTL technical correctness.

This is your UNIQUE MOAT - the one thing no competitor can easily copy.
"""
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import unicodedata
from app.services.arabic_analyzer import ArabicAnalyzer
import logging

logger = logging.getLogger(__name__)


class RTLValidatorEnhanced:
    """
    UNIQUE COMPETITIVE ADVANTAGE: The ONLY tool that validates Arabic/RTL technical SEO.

    What we check:
    1. Technical correctness (dir attribute, lang codes, bidi markup)
    2. Content quality (Arabic readability, mixed scripts, diacritics)
    3. Hreflang validation for Arabic locales
    4. Common RTL layout issues
    5. Font rendering optimization
    """

    def __init__(self):
        self.arabic_analyzer = ArabicAnalyzer()

    def validate_page(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Comprehensive RTL/Arabic validation.

        Returns issues, warnings, and optimization opportunities.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Detect if page is Arabic/RTL
        is_arabic = self._detect_arabic_content(html_content)
        has_arabic = self._has_arabic_text(html_content)

        if not has_arabic:
            return {
                "is_arabic_page": False,
                "message": "No Arabic content detected - RTL validation skipped",
            }

        issues = []

        # 1. Check dir attribute
        issues.extend(self._validate_dir_attribute(soup, is_arabic))

        # 2. Check lang attribute
        issues.extend(self._validate_lang_attribute(soup, is_arabic))

        # 3. Check bidirectional markup
        issues.extend(self._validate_bidi_markup(soup, html_content))

        # 4. Check hreflang for Arabic locales
        issues.extend(self._validate_hreflang_arabic(soup, url))

        # 5. Validate Arabic content quality
        issues.extend(self._validate_arabic_content_quality(html_content))

        # 6. Check for mixed directionality issues
        issues.extend(self._detect_mixed_directionality(html_content))

        # 7. Check font optimization
        issues.extend(self._check_arabic_font_optimization(soup))

        # 8. Validate RTL-specific meta tags
        issues.extend(self._validate_rtl_meta_tags(soup))

        # Calculate severity
        severity = self._calculate_severity(issues)

        return {
            "is_arabic_page": is_arabic,
            "has_arabic_content": has_arabic,
            "url": url,
            "issues": issues,
            "severity": severity,
            "summary": self._generate_summary(issues),
            "checklist": self._generate_checklist(issues),
        }

    def _detect_arabic_content(self, html_content: str) -> bool:
        """Detect if page is primarily Arabic."""
        # Remove HTML tags
        text = BeautifulSoup(html_content, 'html.parser').get_text()

        # Count Arabic characters
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F')
        total_chars = len(re.sub(r'\s', '', text))

        if total_chars == 0:
            return False

        arabic_ratio = arabic_chars / total_chars
        return arabic_ratio > 0.3  # More than 30% Arabic = Arabic page

    def _has_arabic_text(self, html_content: str) -> bool:
        """Check if page has ANY Arabic text."""
        return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F]', html_content))

    def _validate_dir_attribute(self, soup: BeautifulSoup, is_arabic: bool) -> List[Dict]:
        """
        CRITICAL: Validate dir attribute for RTL support.

        W3C requirement: dir attribute is ESSENTIAL for RTL scripts.
        """
        issues = []

        html_tag = soup.find('html')
        body_tag = soup.find('body')

        html_dir = html_tag.get('dir') if html_tag else None
        body_dir = body_tag.get('dir') if body_tag else None

        if is_arabic:
            # For Arabic pages, dir="rtl" is REQUIRED
            if not html_dir and not body_dir:
                issues.append({
                    "type": "missing_dir_attribute",
                    "severity": "critical",
                    "title": "Missing dir='rtl' Attribute",
                    "description": (
                        "The <html> or <body> tag must have dir='rtl' for Arabic content. "
                        "Without it, text displays left-to-right (wrong direction)."
                    ),
                    "simple_explanation": "Your Arabic text displays backwards because the page isn't marked as right-to-left.",
                    "w3c_reference": "https://www.w3.org/International/questions/qa-html-dir",
                    "visual_impact": "Text appears backwards, numbers misaligned, UI elements on wrong side",
                    "how_to_fix": [
                        "Add dir='rtl' to <html> tag: <html dir='rtl' lang='ar'>",
                        "Or add to <body> tag: <body dir='rtl'>",
                        "For multi-language sites: Use dir='auto' on containers",
                    ],
                    "code_example": '<html dir="rtl" lang="ar">',
                    "priority": 1,
                })

            elif html_dir != 'rtl' and body_dir != 'rtl':
                issues.append({
                    "type": "incorrect_dir_value",
                    "severity": "critical",
                    "title": f"Incorrect dir Value: '{html_dir or body_dir}'",
                    "description": f"The dir attribute is set to '{html_dir or body_dir}' but should be 'rtl' for Arabic content.",
                    "simple_explanation": "The text direction is set wrong. Arabic needs dir='rtl'.",
                    "how_to_fix": [f"Change dir='{html_dir or body_dir}' to dir='rtl'"],
                    "priority": 1,
                })

        return issues

    def _validate_lang_attribute(self, soup: BeautifulSoup, is_arabic: bool) -> List[Dict]:
        """
        Validate lang attribute for Arabic content.

        Note: Google uses language detection algorithms, NOT lang attribute.
        But lang is still best practice for accessibility.
        """
        issues = []

        html_tag = soup.find('html')
        lang = html_tag.get('lang') if html_tag else None

        if is_arabic:
            if not lang:
                issues.append({
                    "type": "missing_lang_attribute",
                    "severity": "warning",
                    "title": "Missing lang='ar' Attribute",
                    "description": (
                        "The <html> tag should have lang='ar' for Arabic content. "
                        "While Google doesn't rely on this for language detection, it helps screen readers."
                    ),
                    "simple_explanation": "Screen readers won't know the language is Arabic without lang='ar'.",
                    "accessibility_impact": "Screen readers may pronounce Arabic text with wrong accent",
                    "how_to_fix": ["Add lang='ar' to <html> tag: <html lang='ar' dir='rtl'>"],
                    "google_note": "Google uses algorithms for language detection, not lang attribute",
                    "priority": 2,
                })

            elif lang and not lang.startswith('ar'):
                issues.append({
                    "type": "incorrect_lang_code",
                    "severity": "warning",
                    "title": f"Lang Attribute Mismatch: '{lang}' for Arabic Content",
                    "description": f"Page has Arabic content but lang='{lang}'. Should be 'ar' or locale variant (ar-SA, ar-EG, etc).",
                    "simple_explanation": "Language code doesn't match the actual language used.",
                    "how_to_fix": [
                        "Change lang='{lang}' to lang='ar' for generic Arabic",
                        "Or use specific locale: ar-SA (Saudi), ar-EG (Egypt), ar-AE (UAE), etc",
                    ],
                    "priority": 2,
                })

        return issues

    def _validate_bidi_markup(self, soup: BeautifulSoup, html_content: str) -> List[Dict]:
        """
        Validate bidirectional text markup.

        When mixing LTR (English) and RTL (Arabic), special markup is needed.
        """
        issues = []

        # Check for mixed directionality without proper markup
        text_nodes = soup.find_all(text=True)

        for node in text_nodes:
            text = str(node).strip()
            if not text:
                continue

            has_rtl = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F]', text))
            has_ltr = bool(re.search(r'[a-zA-Z]', text))

            if has_rtl and has_ltr:
                # Mixed directionality - check if wrapped in proper markup
                parent = node.parent

                if parent and parent.name not in ['bdi', 'bdo']:
                    # Check if parent has dir attribute
                    if not parent.get('dir'):
                        issues.append({
                            "type": "mixed_direction_no_markup",
                            "severity": "warning",
                            "title": "Mixed Arabic/English Text Without Bidirectional Markup",
                            "description": (
                                "Text contains both Arabic and English without <bdi> or dir attribute. "
                                "This can cause display issues, especially with punctuation and numbers."
                            ),
                            "simple_explanation": "Mixed language text might display incorrectly. Numbers and punctuation can appear in wrong places.",
                            "example_text": text[:100] + "..." if len(text) > 100 else text,
                            "how_to_fix": [
                                "Wrap mixed-direction text in <bdi> tags: <bdi>Mixed text here</bdi>",
                                "Or add dir='auto' to parent: <p dir='auto'>...</p>",
                                "For isolated phrases: Use <bdo dir='rtl'> or <bdo dir='ltr'>",
                            ],
                            "w3c_reference": "https://www.w3.org/International/articles/inline-bidi-markup/",
                            "priority": 3,
                        })
                        break  # Only report once

        return issues

    def _validate_hreflang_arabic(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """
        Validate hreflang tags for Arabic locale variants.

        COMPETITIVE EDGE: We understand Arabic locale complexity.
        """
        issues = []

        hreflang_links = soup.find_all('link', rel='alternate', hreflang=True)

        if not hreflang_links:
            return []  # No hreflang = not a multilingual site

        arabic_hreflangs = [link for link in hreflang_links if link.get('hreflang', '').startswith('ar')]

        if arabic_hreflangs:
            # Validate locale codes
            valid_arabic_locales = [
                'ar', 'ar-SA', 'ar-EG', 'ar-AE', 'ar-MA', 'ar-DZ', 'ar-IQ', 'ar-KW',
                'ar-LY', 'ar-LB', 'ar-OM', 'ar-QA', 'ar-SD', 'ar-SY', 'ar-TN', 'ar-YE', 'ar-BH', 'ar-JO'
            ]

            for link in arabic_hreflangs:
                hreflang = link.get('hreflang')
                href = link.get('href')

                # Check if locale is valid
                if hreflang not in valid_arabic_locales:
                    issues.append({
                        "type": "invalid_arabic_locale",
                        "severity": "warning",
                        "title": f"Invalid Arabic Locale Code: '{hreflang}'",
                        "description": f"Hreflang uses '{hreflang}' which is not a standard Arabic locale.",
                        "simple_explanation": "The language/region code for Arabic isn't standard.",
                        "valid_locales": valid_arabic_locales,
                        "how_to_fix": [
                            f"Change '{hreflang}' to a valid Arabic locale from the list",
                            "Use 'ar' for generic Arabic, or ar-SA for Saudi Arabic, ar-EG for Egyptian, etc",
                        ],
                        "google_reference": "https://support.google.com/webmasters/answer/189077",
                        "priority": 3,
                    })

                # Check if URL is accessible
                # (Would do HTTP check here in production)

        return issues

    def _validate_arabic_content_quality(self, html_content: str) -> List[Dict]:
        """
        Validate Arabic content quality using Arabic analyzer.
        """
        issues = []

        # Extract main text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()

        # Use Arabic analyzer
        analysis = self.arabic_analyzer.analyze(text)

        # Check for quality issues
        if analysis.get('has_tashkeel', False):
            # Too many diacritics can hurt readability
            diacritic_ratio = analysis.get('diacritic_ratio', 0)
            if diacritic_ratio > 0.5:
                issues.append({
                    "type": "excessive_diacritics",
                    "severity": "info",
                    "title": "Excessive Arabic Diacritics (Tashkeel)",
                    "description": (
                        f"{diacritic_ratio * 100:.1f}% of Arabic text has diacritics. "
                        "While diacritics help pronunciation, too many can hurt readability in modern Arabic."
                    ),
                    "simple_explanation": "Your Arabic text has too many accent marks. Modern readers find this harder to read.",
                    "recommendation": "Use diacritics sparingly - only where needed to prevent ambiguity",
                    "priority": 4,
                })

        # Check for mixed numerals (Arabic-Indic vs Western)
        if self._has_mixed_numerals(text):
            issues.append({
                "type": "mixed_numeral_systems",
                "severity": "info",
                "title": "Inconsistent Numeral System (Western vs Arabic-Indic)",
                "description": "Page uses both Western numerals (1234) and Arabic-Indic numerals (١٢٣٤).",
                "simple_explanation": "Your numbers aren't consistent. Pick one style and stick with it.",
                "recommendation": "Choose one system: Western (1234) for international audience, Arabic-Indic (١٢٣٤) for local",
                "priority": 4,
            })

        return issues

    def _detect_mixed_directionality(self, html_content: str) -> List[Dict]:
        """Detect common mixed directionality issues."""
        issues = []

        # Check for URLs in Arabic text (URLs are always LTR)
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()

        # Pattern: Arabic text followed by URL without spacing/markup
        pattern = r'[\u0600-\u06FF]+\s*https?://[^\s]+'
        matches = re.findall(pattern, text)

        if matches:
            issues.append({
                "type": "url_in_rtl_text",
                "severity": "info",
                "title": "URLs Embedded in Arabic Text",
                "description": (
                    f"Found {len(matches)} URLs embedded in Arabic text. "
                    "URLs are always LTR and may display incorrectly in RTL context."
                ),
                "simple_explanation": "Links in Arabic text might look broken or backwards.",
                "how_to_fix": [
                    "Wrap URLs in <bdi> tags: <bdi>https://example.com</bdi>",
                    "Or use proper <a> tags with link text instead of showing URL",
                ],
                "priority": 4,
            })

        return issues

    def _check_arabic_font_optimization(self, soup: BeautifulSoup) -> List[Dict]:
        """Check for Arabic font optimization."""
        issues = []

        # Check if Arabic-optimized fonts are declared
        style_tags = soup.find_all('style')
        link_tags = soup.find_all('link', rel='stylesheet')

        has_arabic_font = False

        # Common Arabic fonts
        arabic_fonts = ['Noto Sans Arabic', 'Cairo', 'Almarai', 'Amiri', 'Tajawal', 'El Messiri']

        for style in style_tags:
            if style.string and any(font in style.string for font in arabic_fonts):
                has_arabic_font = True
                break

        if not has_arabic_font:
            issues.append({
                "type": "no_arabic_font_optimization",
                "severity": "info",
                "title": "No Arabic-Optimized Font Detected",
                "description": "Page doesn't explicitly use Arabic-optimized fonts. Default system fonts may not render Arabic beautifully.",
                "simple_explanation": "Your Arabic text uses default fonts. It could look much better.",
                "recommended_fonts": arabic_fonts,
                "how_to_fix": [
                    "Use Google Fonts Arabic fonts: Noto Sans Arabic, Cairo, Amiri",
                    "Add font-display: swap to prevent render blocking",
                    "Example: @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');",
                ],
                "priority": 5,
            })

        return issues

    def _validate_rtl_meta_tags(self, soup: BeautifulSoup) -> List[Dict]:
        """Validate RTL-specific meta tags."""
        issues = []

        # Check for viewport meta (affects RTL mobile rendering)
        viewport = soup.find('meta', attrs={'name': 'viewport'})

        if viewport:
            content = viewport.get('content', '')

            # Check if viewport locks orientation (bad for RTL)
            if 'user-scalable=no' in content:
                issues.append({
                    "type": "viewport_locked",
                    "severity": "info",
                    "title": "Viewport Locked - May Affect RTL Mobile Experience",
                    "description": "Viewport has user-scalable=no which can cause issues with RTL layouts on mobile.",
                    "simple_explanation": "Mobile users can't zoom. This can make Arabic text hard to read.",
                    "how_to_fix": ["Remove user-scalable=no from viewport meta tag"],
                    "priority": 5,
                })

        return issues

    def _has_mixed_numerals(self, text: str) -> bool:
        """Check if text mixes Western and Arabic-Indic numerals."""
        has_western = bool(re.search(r'[0-9]', text))
        has_arabic_indic = bool(re.search(r'[\u0660-\u0669]', text))
        return has_western and has_arabic_indic

    def _calculate_severity(self, issues: List[Dict]) -> str:
        """Calculate overall severity."""
        if not issues:
            return "excellent"

        critical_count = sum(1 for i in issues if i['severity'] == 'critical')
        warning_count = sum(1 for i in issues if i['severity'] == 'warning')

        if critical_count > 0:
            return "critical"
        elif warning_count > 0:
            return "warning"
        else:
            return "good"

    def _generate_summary(self, issues: List[Dict]) -> str:
        """Generate human-readable summary."""
        if not issues:
            return "✅ Excellent! Your Arabic/RTL implementation is technically correct."

        critical = [i for i in issues if i['severity'] == 'critical']
        warnings = [i for i in issues if i['severity'] == 'warning']
        info = [i for i in issues if i['severity'] == 'info']

        parts = []

        if critical:
            parts.append(f"🚨 {len(critical)} CRITICAL issues must be fixed immediately:")
            for issue in critical:
                parts.append(f"  • {issue['title']}")

        if warnings:
            parts.append(f"\n⚠️ {len(warnings)} warnings should be addressed:")
            for issue in warnings:
                parts.append(f"  • {issue['title']}")

        if info:
            parts.append(f"\nℹ️ {len(info)} optimization opportunities:")
            for issue in info:
                parts.append(f"  • {issue['title']}")

        return "\n".join(parts)

    def _generate_checklist(self, issues: List[Dict]) -> List[Dict]:
        """Generate prioritized checklist."""
        # Sort by priority
        sorted_issues = sorted(issues, key=lambda x: x.get('priority', 99))

        checklist = []
        for i, issue in enumerate(sorted_issues, 1):
            checklist.append({
                "order": i,
                "priority": issue.get('priority', 99),
                "title": issue['title'],
                "severity": issue['severity'],
                "quick_fix": issue['how_to_fix'][0] if issue.get('how_to_fix') else "See issue details",
                "estimated_time": self._estimate_fix_time(issue),
            })

        return checklist

    def _estimate_fix_time(self, issue: Dict) -> str:
        """Estimate time to fix."""
        severity = issue['severity']

        if severity == 'critical':
            return "5-15 minutes"
        elif severity == 'warning':
            return "15-30 minutes"
        else:
            return "30-60 minutes"
