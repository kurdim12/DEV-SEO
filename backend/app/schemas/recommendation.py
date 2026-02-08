"""AI Recommendation-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class AIRecommendationResponse(BaseModel):
    """Schema for AI recommendation data in responses."""

    id: UUID
    crawl_job_id: UUID
    page_result_id: Optional[UUID] = None
    recommendation_type: str
    title: str
    description: str
    priority: str  # high, medium, low
    ai_generated_at: datetime
    implementation_status: str  # pending, in_progress, completed, dismissed
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174004",
                "crawl_job_id": "123e4567-e89b-12d3-a456-426614174002",
                "page_result_id": "123e4567-e89b-12d3-a456-426614174003",
                "recommendation_type": "content_quality",
                "title": "Expand Content Depth",
                "description": "The page has only 150 words. Consider expanding to at least 300 words to provide more value and improve SEO rankings.",
                "priority": "medium",
                "ai_generated_at": "2026-02-06T12:20:00Z",
                "implementation_status": "pending",
                "created_at": "2026-02-06T12:20:00Z",
                "updated_at": "2026-02-06T12:20:00Z",
            }
        },
    }


class GenerateRecommendationsRequest(BaseModel):
    """Schema for requesting AI recommendation generation."""

    use_ai_analysis: bool = Field(
        False,
        description="Whether to use AI for content analysis (costs money with OpenAI, free with Ollama)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "use_ai_analysis": False,
            }
        }
    }


class UpdateRecommendationRequest(BaseModel):
    """Schema for updating a recommendation's status."""

    implementation_status: str = Field(
        ...,
        description="New implementation status (pending, in_progress, completed, dismissed)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "implementation_status": "completed",
            }
        }
    }


class RecommendationsSummary(BaseModel):
    """Schema for recommendations summary."""

    total: int
    by_priority: dict = Field(
        ...,
        description="Count by priority level (high, medium, low)",
    )
    by_status: dict = Field(
        ...,
        description="Count by implementation status",
    )
    by_type: dict = Field(
        ...,
        description="Count by recommendation type",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 25,
                "by_priority": {
                    "high": 5,
                    "medium": 12,
                    "low": 8,
                },
                "by_status": {
                    "pending": 20,
                    "in_progress": 3,
                    "completed": 2,
                    "dismissed": 0,
                },
                "by_type": {
                    "title": 5,
                    "meta_description": 8,
                    "content_quality": 7,
                    "overall": 5,
                },
            }
        }
    }
