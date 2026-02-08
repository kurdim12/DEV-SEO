"""Crawl-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CrawlJobCreate(BaseModel):
    """Schema for creating a new crawl job."""

    website_id: UUID = Field(..., description="Website ID to crawl")

    model_config = {
        "json_schema_extra": {
            "example": {
                "website_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    }


class CrawlJobResponse(BaseModel):
    """Schema for crawl job data in responses."""

    id: UUID
    website_id: UUID
    status: str
    pages_crawled: int
    pages_total: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "website_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "pages_crawled": 15,
                "pages_total": 50,
                "started_at": "2026-02-06T12:00:00Z",
                "completed_at": None,
                "error_message": None,
                "created_at": "2026-02-06T11:55:00Z",
            }
        },
    }


class SEOIssue(BaseModel):
    """Schema for an individual SEO issue."""

    type: str = Field(..., description="Issue type (e.g., 'missing_title')")
    severity: str = Field(..., description="Severity level (critical, warning, info)")
    message: str = Field(..., description="Human-readable issue description")
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing the issue")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "title_too_short",
                "severity": "warning",
                "message": "Page title is only 10 characters long",
                "suggestion": "Aim for 50-60 characters for optimal SEO",
            }
        }
    }


class PageResultResponse(BaseModel):
    """Schema for page result data in responses."""

    id: UUID
    crawl_job_id: UUID
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: Optional[List[str]] = None
    word_count: Optional[int] = None
    load_time_ms: Optional[int] = None
    mobile_friendly: Optional[bool] = None
    has_ssl: Optional[bool] = None
    canonical_url: Optional[str] = None
    og_tags: Optional[dict] = None
    schema_markup: Optional[dict] = None
    issues: List[SEOIssue] = []
    seo_score: Optional[int] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "crawl_job_id": "123e4567-e89b-12d3-a456-426614174002",
                "url": "https://example.com/",
                "status_code": 200,
                "title": "Example Domain",
                "meta_description": "Example domain for illustrative examples",
                "h1_tags": ["Example Domain"],
                "word_count": 150,
                "load_time_ms": 450,
                "mobile_friendly": True,
                "has_ssl": True,
                "canonical_url": "https://example.com/",
                "og_tags": {"og:title": "Example Domain"},
                "schema_markup": {},
                "issues": [
                    {
                        "type": "title_too_short",
                        "severity": "warning",
                        "message": "Page title is only 14 characters long",
                        "suggestion": "Aim for 50-60 characters for optimal SEO",
                    }
                ],
                "seo_score": 78,
                "created_at": "2026-02-06T12:05:00Z",
            }
        },
    }


class CrawlReport(BaseModel):
    """Schema for complete crawl report."""

    crawl_job: CrawlJobResponse
    pages: List[PageResultResponse]
    summary: dict = Field(
        ...,
        description="Summary statistics (avg_score, total_issues, etc.)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "crawl_job": {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "website_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "completed",
                    "pages_crawled": 50,
                    "pages_total": 50,
                    "started_at": "2026-02-06T12:00:00Z",
                    "completed_at": "2026-02-06T12:15:00Z",
                    "error_message": None,
                    "created_at": "2026-02-06T11:55:00Z",
                },
                "pages": [],
                "summary": {
                    "avg_score": 75,
                    "total_issues": 150,
                    "critical_issues": 5,
                    "warning_issues": 50,
                    "info_issues": 95,
                },
            }
        }
    }
