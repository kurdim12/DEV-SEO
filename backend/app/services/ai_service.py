"""
Hybrid AI Service for SEO recommendations.
Uses a 3-tier approach:
1. Rule-based engine (FREE, fast, covers 95% of issues)
2. GPT-4o-mini (CHEAP, for content analysis)
3. Ollama (FREE, optional for privacy)
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from app.services.recommendation_engine import RuleBasedRecommendationEngine, SEORecommendation
from app.config import settings


class AIService:
    """
    Hybrid AI service that combines rule-based recommendations with optional AI analysis.
    """

    def __init__(self):
        self.rule_engine = RuleBasedRecommendationEngine()
        self.use_ai = settings.OPENAI_API_KEY is not None
        self.use_ollama = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

    async def generate_page_recommendations(
        self,
        page_data: Dict[str, Any],
        use_ai_analysis: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a single page.

        Args:
            page_data: Page crawl data
            use_ai_analysis: Whether to use AI for content analysis (costs money)

        Returns:
            List of recommendation dictionaries
        """
        # Tier 1: Always run rule-based analysis (FREE!)
        rule_recs = self.rule_engine.analyze_page(page_data)

        recommendations = [self._recommendation_to_dict(rec, page_data.get("id")) for rec in rule_recs]

        # Tier 2: Optionally add AI content analysis
        if use_ai_analysis and self.use_ai:
            ai_recs = await self._generate_ai_content_recommendations(page_data)
            recommendations.extend(ai_recs)
        elif use_ai_analysis and self.use_ollama:
            ai_recs = await self._generate_ollama_recommendations(page_data)
            recommendations.extend(ai_recs)

        return recommendations

    async def generate_overall_recommendations(
        self,
        pages: List[Dict[str, Any]],
        crawl_stats: Dict[str, Any],
        use_ai_analysis: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate site-wide recommendations.

        Args:
            pages: All crawled pages
            crawl_stats: Overall crawl statistics
            use_ai_analysis: Whether to use AI for strategic analysis

        Returns:
            List of recommendation dictionaries
        """
        # Tier 1: Rule-based overall analysis
        rule_recs = self.rule_engine.generate_overall_recommendations(pages, crawl_stats)

        recommendations = [self._recommendation_to_dict(rec, None) for rec in rule_recs]

        # Tier 2: Optionally add AI strategic recommendations
        if use_ai_analysis and self.use_ai:
            ai_recs = await self._generate_ai_strategic_recommendations(pages, crawl_stats)
            recommendations.extend(ai_recs)

        return recommendations

    async def _generate_ai_content_recommendations(
        self,
        page_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use GPT-4o-mini to analyze content quality and suggest improvements.
        Very cheap: ~$0.0005 per page
        """
        try:
            import openai

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = self._build_content_analysis_prompt(page_data)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert SEO content strategist. Analyze the content and provide 2-3 actionable recommendations in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.7
            )

            result = json.loads(response.choices[0].message.content)

            recommendations = []
            for rec in result.get("recommendations", []):
                recommendations.append({
                    "page_result_id": page_data.get("id"),
                    "recommendation_type": "content_quality",
                    "title": rec.get("title", "AI Content Suggestion"),
                    "description": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "ai_generated_at": datetime.now(timezone.utc),
                })

            return recommendations

        except Exception as e:
            print(f"AI content analysis failed: {e}")
            return []

    async def _generate_ai_strategic_recommendations(
        self,
        pages: List[Dict[str, Any]],
        crawl_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use GPT-4o-mini to generate strategic SEO recommendations.
        """
        try:
            import openai

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = self._build_strategic_analysis_prompt(pages, crawl_stats)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert SEO strategist. Analyze the website and provide 3-5 high-level strategic recommendations in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.7
            )

            result = json.loads(response.choices[0].message.content)

            recommendations = []
            for rec in result.get("recommendations", []):
                recommendations.append({
                    "page_result_id": None,  # Site-wide recommendation
                    "recommendation_type": "overall",
                    "title": rec.get("title", "Strategic Recommendation"),
                    "description": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "ai_generated_at": datetime.now(timezone.utc),
                })

            return recommendations

        except Exception as e:
            print(f"AI strategic analysis failed: {e}")
            return []

    async def _generate_ollama_recommendations(
        self,
        page_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use Ollama (local LLaMA) for content recommendations.
        100% FREE and private!
        """
        try:
            import httpx

            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

            prompt = self._build_content_analysis_prompt(page_data)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "llama3.1",
                        "prompt": f"As an SEO expert, analyze this page and provide 2-3 actionable recommendations:\n\n{prompt}\n\nRespond in JSON format with 'recommendations' array.",
                        "stream": False,
                        "format": "json"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    recommendations_data = json.loads(result.get("response", "{}"))

                    recommendations = []
                    for rec in recommendations_data.get("recommendations", []):
                        recommendations.append({
                            "page_result_id": page_data.get("id"),
                            "recommendation_type": "content_quality",
                            "title": rec.get("title", "Local AI Suggestion"),
                            "description": rec.get("description", ""),
                            "priority": rec.get("priority", "medium"),
                            "ai_generated_at": datetime.now(timezone.utc),
                        })

                    return recommendations

        except Exception as e:
            print(f"Ollama analysis failed: {e}")
            return []

        return []

    def _build_content_analysis_prompt(self, page_data: Dict[str, Any]) -> str:
        """Build prompt for content analysis."""
        return f"""Analyze this webpage content:

URL: {page_data.get('url', 'N/A')}
Title: {page_data.get('title', 'N/A')}
Meta Description: {page_data.get('meta_description', 'N/A')}
Word Count: {page_data.get('word_count', 0)}
H1 Tags: {', '.join(page_data.get('h1_tags', []))}

Provide 2-3 specific, actionable content improvement recommendations focusing on:
1. Content quality and depth
2. User intent match
3. Content structure and readability

Format as JSON:
{{
  "recommendations": [
    {{
      "title": "Brief title",
      "description": "Specific actionable advice",
      "priority": "high|medium|low"
    }}
  ]
}}"""

    def _build_strategic_analysis_prompt(
        self,
        pages: List[Dict[str, Any]],
        crawl_stats: Dict[str, Any]
    ) -> str:
        """Build prompt for strategic analysis."""
        avg_score = crawl_stats.get("avg_seo_score", 0)
        total_pages = len(pages)

        return f"""Analyze this website's overall SEO strategy:

Total Pages: {total_pages}
Average SEO Score: {avg_score}/100
Total Issues: {crawl_stats.get('total_issues', 0)}

Common Issues:
{self._summarize_common_issues(pages)}

Provide 3-5 high-level strategic recommendations to improve overall SEO.
Focus on quick wins and high-impact changes.

Format as JSON:
{{
  "recommendations": [
    {{
      "title": "Brief strategic recommendation",
      "description": "Detailed explanation and implementation steps",
      "priority": "high|medium|low"
    }}
  ]
}}"""

    def _summarize_common_issues(self, pages: List[Dict[str, Any]]) -> str:
        """Summarize the most common issues across pages."""
        issue_counts: Dict[str, int] = {}

        for page in pages[:50]:  # Sample first 50 pages
            for issue in page.get("issues", []):
                if isinstance(issue, dict):
                    issue_type = issue.get("type", "unknown")
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Get top 5 issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return "\n".join([f"- {issue}: {count} pages" for issue, count in top_issues])

    def _recommendation_to_dict(
        self,
        rec: SEORecommendation,
        page_id: Optional[str]
    ) -> Dict[str, Any]:
        """Convert SEORecommendation to dictionary format."""
        return {
            "page_result_id": page_id if rec.page_specific else None,
            "recommendation_type": rec.recommendation_type,
            "title": rec.title,
            "description": rec.description,
            "priority": rec.priority,
            "ai_generated_at": datetime.now(timezone.utc),
        }
