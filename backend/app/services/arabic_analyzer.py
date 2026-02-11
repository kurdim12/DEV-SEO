"""
Arabic language analysis service for SEO.
Includes dialect detection, RTL validation, and Arabic-specific SEO checks.
"""
from typing import Dict, List, Optional, Tuple
from pyarabic import araby
import re
import logging

logger = logging.getLogger(__name__)


class ArabicAnalyzer:
    """Analyzer for Arabic language content and RTL layout issues."""

    # Dialect markers (common words/phrases unique to each dialect)
    GULF_MARKERS = [
        'شلون', 'ويش', 'يمكن', 'زين', 'عاد', 'خلاص', 'ياهل', 'حق', 'مال', 'شنو',
        'هالوقت', 'الحين', 'باجر', 'كذا', 'مدري'
    ]

    LEVANTINE_MARKERS = [
        'شو', 'كيف', 'هيك', 'منيح', 'مش', 'بدي', 'صحيح', 'هلأ', 'ليش', 'شوي',
        'كتير', 'مبارح', 'بكرا', 'هلق', 'يلا'
    ]

    EGYPTIAN_MARKERS = [
        'ازاي', 'ايه', 'كده', 'تمام', 'مش', 'عايز', 'علشان', 'دلوقتي', 'امبارح',
        'بكره', 'ليه', 'ازيك', 'يعني', 'خالص', 'قوي'
    ]

    MAGHREBI_MARKERS = [
        'واش', 'كيفاش', 'بزاف', 'مزيان', 'دابا', 'غدا', 'البارح', 'علاش', 'هاكا',
        'بصح', 'نتا', 'نتي'
    ]

    # Common transliteration patterns (Arabizi/Franco-Arab)
    ARABIZI_PATTERNS = [
        (r'\b\d+[a-z]+\d*\b', 'Numbers mixed with letters'),
        (r'\b(2|3|5|6|7|8|9)[a-z]+\b', 'Arabic sounds as numbers'),
        (r'\b(salam|sabah|masa|shukran|afwan|inshallah)\b', 'Arabic words in Latin script')
    ]

    def __init__(self):
        """Initialize the Arabic analyzer."""
        self.stop_words = araby.STOPWORDS if hasattr(araby, 'STOPWORDS') else set()

    def detect_arabic_content(self, text: str) -> Tuple[bool, float]:
        """
        Detect if text contains Arabic content.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (has_arabic: bool, arabic_percentage: float)
        """
        if not text:
            return False, 0.0

        arabic_chars = sum(1 for char in text if araby.is_arabicrange(char))
        total_chars = len([c for c in text if c.strip()])

        if total_chars == 0:
            return False, 0.0

        percentage = (arabic_chars / total_chars) * 100
        has_arabic = percentage > 10  # Consider Arabic if >10% Arabic characters

        return has_arabic, percentage

    def detect_dialect(self, text: str) -> Dict[str, any]:
        """
        Detect Arabic dialect used in text.

        Args:
            text: Arabic text to analyze

        Returns:
            Dict with detected dialect, confidence, and markers found
        """
        # Normalize and clean text
        text_normalized = araby.strip_tashkeel(text).lower()

        # Count markers for each dialect
        scores = {
            'gulf': sum(1 for marker in self.GULF_MARKERS if marker in text_normalized),
            'levantine': sum(1 for marker in self.LEVANTINE_MARKERS if marker in text_normalized),
            'egyptian': sum(1 for marker in self.EGYPTIAN_MARKERS if marker in text_normalized),
            'maghrebi': sum(1 for marker in self.MAGHREBI_MARKERS if marker in text_normalized),
        }

        total_markers = sum(scores.values())

        if total_markers == 0:
            return {
                'dialect': 'modern_standard_arabic',
                'confidence': 0.5,
                'markers_found': 0,
                'is_mixed': False,
                'message': 'No dialect markers found - likely Modern Standard Arabic (MSA)'
            }

        # Get dominant dialect
        dominant_dialect = max(scores, key=scores.get)
        dominant_score = scores[dominant_dialect]
        confidence = dominant_score / total_markers if total_markers > 0 else 0

        # Check if mixed
        dialects_present = sum(1 for score in scores.values() if score > 0)
        is_mixed = dialects_present > 1

        return {
            'dialect': dominant_dialect,
            'confidence': round(confidence, 2),
            'markers_found': dominant_score,
            'total_markers': total_markers,
            'is_mixed': is_mixed,
            'dialect_breakdown': {k: v for k, v in scores.items() if v > 0},
            'message': f"{'Mixed dialects detected' if is_mixed else 'Single dialect'} - dominant: {dominant_dialect.replace('_', ' ').title()}"
        }

    def detect_arabizi(self, text: str) -> Dict[str, any]:
        """
        Detect Arabizi (Franco-Arab) usage in text.

        Args:
            text: Text to check

        Returns:
            Dict with Arabizi detection results
        """
        text_lower = text.lower()
        arabizi_matches = []

        for pattern, description in self.ARABIZI_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                arabizi_matches.append({
                    'pattern': description,
                    'examples': matches[:5]  # Limit to 5 examples
                })

        has_arabizi = len(arabizi_matches) > 0

        return {
            'has_arabizi': has_arabizi,
            'matches': arabizi_matches,
            'message': 'Arabizi/Franco-Arab detected - consider using Arabic script for better SEO' if has_arabizi else 'No Arabizi detected'
        }

    def check_rtl_html(self, html: str, url: str) -> List[Dict[str, str]]:
        """
        Check HTML for RTL (Right-to-Left) layout issues.

        Args:
            html: HTML content to check
            url: Page URL

        Returns:
            List of RTL-related issues
        """
        issues = []
        html_lower = html.lower()

        # Check 1: Missing dir="rtl" on <html> tag
        if 'dir="rtl"' not in html_lower and 'dir=rtl' not in html_lower:
            has_arabic, percentage = self.detect_arabic_content(html)
            if has_arabic and percentage > 50:
                issues.append({
                    'type': 'missing_rtl_attribute',
                    'severity': 'critical',
                    'message': f'Page contains {percentage:.1f}% Arabic content but missing dir="rtl" on <html> tag',
                    'fix': 'Add dir="rtl" lang="ar" to your <html> tag'
                })

        # Check 2: CSS direction property
        has_css_direction_ltr = bool(re.search(r'direction\s*:\s*ltr', html_lower))
        if has_css_direction_ltr:
            has_arabic, percentage = self.detect_arabic_content(html)
            if has_arabic and percentage > 30:
                issues.append({
                    'type': 'css_direction_conflict',
                    'severity': 'warning',
                    'message': 'CSS sets direction:ltr but page has significant Arabic content',
                    'fix': 'Change CSS direction to rtl or remove the property to inherit from <html dir="rtl">'
                })

        # Check 3: Lang attribute
        if 'lang="ar"' not in html_lower:
            has_arabic, percentage = self.detect_arabic_content(html)
            if has_arabic and percentage > 50:
                issues.append({
                    'type': 'missing_lang_attribute',
                    'severity': 'warning',
                    'message': 'Missing lang="ar" attribute on <html> tag',
                    'fix': 'Add lang="ar" to your <html> tag for better accessibility'
                })

        # Check 4: Text alignment in CSS
        has_text_align_left = bool(re.search(r'text-align\s*:\s*left', html_lower))
        if has_text_align_left:
            has_arabic, percentage = self.detect_arabic_content(html)
            if has_arabic and percentage > 30:
                issues.append({
                    'type': 'text_alignment_issue',
                    'severity': 'info',
                    'message': 'Found text-align:left in CSS - consider using text-align:right or text-align:start for Arabic',
                    'fix': 'Use text-align:start for automatic RTL support'
                })

        # Check 5: Input fields without dir attribute
        input_count = html_lower.count('<input')
        input_with_dir = html_lower.count('<input') if 'dir=' in html_lower else 0

        if input_count > 0 and input_with_dir == 0:
            has_arabic, percentage = self.detect_arabic_content(html)
            if has_arabic:
                issues.append({
                    'type': 'input_rtl_missing',
                    'severity': 'info',
                    'message': f'Found {input_count} input fields without dir attribute',
                    'fix': 'Add dir="auto" to input fields for automatic RTL detection'
                })

        return issues

    def analyze_arabic_keywords(self, text: str, top_n: int = 10) -> Dict[str, any]:
        """
        Extract and analyze Arabic keywords from text.

        Args:
            text: Arabic text
            top_n: Number of top keywords to return

        Returns:
            Dict with keyword analysis
        """
        # Remove tashkeel (diacritics)
        text_clean = araby.strip_tashkeel(text)

        # Tokenize
        words = araby.tokenize(text_clean)

        # Filter out short words and numbers
        words = [w for w in words if len(w) >= 3 and araby.is_arabicrange(w[0])]

        # Count occurrences
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        # Sort by frequency
        top_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:top_n]

        return {
            'top_keywords': [{'keyword': k, 'count': v} for k, v in top_keywords],
            'total_words': len(words),
            'unique_words': len(word_count),
            'vocabulary_richness': len(word_count) / len(words) if words else 0
        }

    def generate_seo_suggestions(self, text: str, html: str, url: str) -> Dict[str, any]:
        """
        Generate comprehensive Arabic SEO suggestions.

        Args:
            text: Page text content
            html: Full HTML
            url: Page URL

        Returns:
            Dict with all Arabic-specific SEO suggestions
        """
        has_arabic, arabic_percentage = self.detect_arabic_content(text)

        if not has_arabic:
            return {
                'has_arabic': False,
                'message': 'No Arabic content detected'
            }

        dialect_info = self.detect_dialect(text)
        arabizi_info = self.detect_arabizi(text)
        rtl_issues = self.check_rtl_html(html, url)
        keyword_analysis = self.analyze_arabic_keywords(text)

        suggestions = []

        # Dialect suggestions
        if dialect_info['is_mixed']:
            suggestions.append({
                'type': 'dialect_consistency',
                'priority': 'medium',
                'message': f"Mixed Arabic dialects detected. For better user experience, stick to one dialect or use Modern Standard Arabic (MSA).",
                'details': dialect_info['dialect_breakdown']
            })

        # Arabizi warning
        if arabizi_info['has_arabizi']:
            suggestions.append({
                'type': 'arabizi_usage',
                'priority': 'high',
                'message': 'Arabizi (Franco-Arab) detected. Search engines prefer proper Arabic script.',
                'details': arabizi_info['matches']
            })

        # RTL issues
        for issue in rtl_issues:
            suggestions.append({
                'type': issue['type'],
                'priority': issue['severity'],
                'message': issue['message'],
                'fix': issue['fix']
            })

        # Keyword density check
        if keyword_analysis['vocabulary_richness'] < 0.3:
            suggestions.append({
                'type': 'keyword_variety',
                'priority': 'medium',
                'message': f"Low vocabulary richness ({keyword_analysis['vocabulary_richness']:.2%}). Add more varied Arabic keywords.",
            })

        return {
            'has_arabic': True,
            'arabic_percentage': round(arabic_percentage, 1),
            'dialect_analysis': dialect_info,
            'arabizi_analysis': arabizi_info,
            'rtl_issues': rtl_issues,
            'keyword_analysis': keyword_analysis,
            'suggestions': suggestions,
            'summary': f"Detected {dialect_info['dialect'].replace('_', ' ').title()} with {len(rtl_issues)} RTL issues and {len(suggestions)} total suggestions"
        }


# Global instance
arabic_analyzer = ArabicAnalyzer()
