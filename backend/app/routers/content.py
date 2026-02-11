"""
Content optimization router for AI-powered content analysis and suggestions.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from bs4 import BeautifulSoup
import textstat
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.dependencies import get_current_user_clerk
from app.models.user import User
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["Content Optimization"])
limiter = Limiter(key_func=get_remote_address)


class ContentOptimizeRequest(BaseModel):
    """Request for content optimization."""
    text: Optional[str] = Field(None, description="Raw text content to optimize")
    url: Optional[HttpUrl] = Field(None, description="URL to fetch and optimize content from")
    target_keyword: Optional[str] = Field(None, description="Target SEO keyword")


class TitleSuggestion(BaseModel):
    """Title suggestion with SEO score."""
    title: str
    character_count: int
    reason: str


class ContentOptimizationResponse(BaseModel):
    """Response with content optimization suggestions."""
    title_suggestions: list[TitleSuggestion]
    meta_description: str
    meta_description_length: int
    keyword_density: dict[str, float]
    readability_score: float
    readability_grade: str
    readability_assessment: str
    word_count: int
    missing_keywords: list[str]
    content_improvements: list[str]
    internal_linking_suggestions: list[str]


async def fetch_content_from_url(url: str) -> tuple[str, str]:
    """
    Fetch content from URL and extract title and body text.

    Returns:
        tuple: (title, body_text)
    """
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(str(url), headers={
            "User-Agent": "DevSEO-Content-Bot/1.0"
        })

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch URL (status: {response.status_code})"
            )

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return title_text, text


def calculate_keyword_density(text: str, top_n: int = 10) -> dict[str, float]:
    """Calculate keyword density for top words."""
    # Remove special characters and convert to lowercase
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Common stop words to ignore
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'now', 'see', 'use', 'way', 'who', 'will', 'with', 'this', 'that', 'from', 'have', 'had', 'what', 'when', 'your', 'more', 'than', 'been', 'were', 'said', 'each', 'which', 'their', 'there', 'would', 'about', 'into', 'could', 'other', 'these', 'first', 'after', 'also', 'well', 'only', 'very', 'much', 'even', 'most', 'such', 'because', 'should', 'before'}

    words = [w for w in words if w not in stop_words]
    total_words = len(words)

    if total_words == 0:
        return {}

    # Count occurrences
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    # Calculate density
    density = {word: (count / total_words) * 100
               for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:top_n]}

    return density


def generate_title_suggestions(current_title: str, target_keyword: Optional[str], content: str) -> list[TitleSuggestion]:
    """Generate SEO-optimized title suggestions."""
    suggestions = []

    # Suggestion 1: Keyword-first format (if keyword provided)
    if target_keyword:
        title1 = f"{target_keyword.title()}: Complete Guide for 2025"
        suggestions.append(TitleSuggestion(
            title=title1,
            character_count=len(title1),
            reason="Keyword-first format with year for freshness"
        ))

        title2 = f"How to {target_keyword.title()} - Expert Tips & Strategies"
        suggestions.append(TitleSuggestion(
            title=title2,
            character_count=len(title2),
            reason="How-to format with keyword, appeals to searchers"
        ))

        title3 = f"{target_keyword.title()} | Professional Guide"
        suggestions.append(TitleSuggestion(
            title=title3,
            character_count=len(title3),
            reason="Concise, professional format with keyword"
        ))
    else:
        # Generic improvements to current title
        clean_title = current_title[:60] if len(current_title) > 60 else current_title

        suggestions.append(TitleSuggestion(
            title=f"{clean_title} - Complete Guide 2025",
            character_count=len(f"{clean_title} - Complete Guide 2025"),
            reason="Added completeness indicator and year"
        ))

        suggestions.append(TitleSuggestion(
            title=f"{clean_title} | Expert Insights",
            character_count=len(f"{clean_title} | Expert Insights"),
            reason="Added authority signal"
        ))

    return suggestions[:3]


def generate_meta_description(content: str, target_keyword: Optional[str]) -> str:
    """Generate SEO-optimized meta description."""
    # Get first 2-3 sentences
    sentences = content.split('.')[:3]
    base_description = '. '.join(sentences).strip()

    # Truncate to ideal length (145-155 characters)
    if len(base_description) > 155:
        base_description = base_description[:152] + "..."

    # Add keyword if provided and not already present
    if target_keyword and target_keyword.lower() not in base_description.lower():
        if len(base_description) + len(target_keyword) + 10 < 155:
            base_description = f"{target_keyword.title()}: {base_description}"
        else:
            # Replace first few words with keyword
            words = base_description.split()
            base_description = f"{target_keyword.title()} {' '.join(words[2:])}".strip()

    # Ensure it ends properly
    if not base_description.endswith(('.', '!', '?', '...')):
        base_description = base_description.rsplit(' ', 1)[0] + "..."

    return base_description[:155]


@router.post(
    "/optimize",
    response_model=ContentOptimizationResponse,
    summary="Optimize content for SEO",
    description="Analyze and optimize content with AI-powered suggestions for titles, meta descriptions, keywords, and readability"
)
@limiter.limit("20/hour")  # 20 content optimizations per hour
async def optimize_content(
    http_request: Request,
    request: ContentOptimizeRequest,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> ContentOptimizationResponse:
    """
    Optimize content for SEO with AI-powered suggestions.
    """
    # Get content (either from text or URL)
    if request.url:
        current_title, content = await fetch_content_from_url(str(request.url))
    elif request.text:
        current_title = ""
        content = request.text
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'text' or 'url' must be provided"
        )

    # Calculate readability
    readability_score = textstat.flesch_reading_ease(content)
    readability_grade = textstat.text_standard(content, float_output=False)

    # Assess readability
    if readability_score >= 80:
        assessment = "Very Easy - Easily understood by 11-year-olds"
    elif readability_score >= 60:
        assessment = "Easy - Easily understood by 13-15 year-olds"
    elif readability_score >= 50:
        assessment = "Fairly Difficult - High school level"
    elif readability_score >= 30:
        assessment = "Difficult - College level"
    else:
        assessment = "Very Difficult - College graduate level"

    # Calculate keyword density
    keyword_density = calculate_keyword_density(content)

    # Generate title suggestions
    title_suggestions = generate_title_suggestions(current_title, request.target_keyword, content)

    # Generate meta description
    meta_description = generate_meta_description(content, request.target_keyword)

    # Analyze for missing keywords (if target keyword provided)
    missing_keywords = []
    if request.target_keyword:
        keyword_lower = request.target_keyword.lower()
        content_lower = content.lower()

        # Check variations
        variations = [
            keyword_lower,
            keyword_lower + "s",  # plural
            keyword_lower + "ing",  # gerund
            "best " + keyword_lower,
            keyword_lower + " tips",
            keyword_lower + " guide",
        ]

        for variation in variations:
            if variation not in content_lower:
                missing_keywords.append(variation)

    # Content improvements
    word_count = len(content.split())
    improvements = []

    if word_count < 300:
        improvements.append("📝 Content is too short. Aim for at least 300 words for better SEO. Current: " + str(word_count))
    elif word_count < 600:
        improvements.append("📝 Consider expanding content to 600-1000 words for better ranking potential")

    if readability_score < 50:
        improvements.append("📖 Content is too complex. Simplify language for better readability")

    avg_sentence_length = textstat.avg_sentence_length(content)
    if avg_sentence_length > 25:
        improvements.append(f"✂️ Sentences are too long (avg: {avg_sentence_length:.1f} words). Break them into shorter sentences")

    if request.target_keyword:
        keyword_count = content.lower().count(request.target_keyword.lower())
        target_density = (keyword_count / word_count) * 100 if word_count > 0 else 0

        if target_density < 0.5:
            improvements.append(f"🎯 Target keyword '{request.target_keyword}' appears only {keyword_count} times ({target_density:.1f}%). Aim for 1-2% density")
        elif target_density > 3:
            improvements.append(f"⚠️ Target keyword '{request.target_keyword}' appears too often ({target_density:.1f}%). Reduce to avoid keyword stuffing")

    # Check for headers (basic heuristic)
    has_headers = bool(re.search(r'\n[A-Z][^\n]{10,50}\n', content))
    if not has_headers:
        improvements.append("📑 Add headings (H2, H3) to structure your content better")

    # Internal linking suggestions
    internal_linking = []
    if request.target_keyword:
        internal_linking.append(f"Link to related pages about '{request.target_keyword}'")
        internal_linking.append(f"Add links to your homepage or main category page")
        internal_linking.append(f"Link to supporting content that explains '{request.target_keyword}' in depth")

    return ContentOptimizationResponse(
        title_suggestions=title_suggestions,
        meta_description=meta_description,
        meta_description_length=len(meta_description),
        keyword_density=keyword_density,
        readability_score=round(readability_score, 1),
        readability_grade=readability_grade,
        readability_assessment=assessment,
        word_count=word_count,
        missing_keywords=missing_keywords[:5],
        content_improvements=improvements,
        internal_linking_suggestions=internal_linking
    )
