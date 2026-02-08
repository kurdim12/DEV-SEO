"""Page result model for storing SEO analysis results."""
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class PageResult(Base):
    """
    Page result model storing SEO analysis results for individual pages.

    Attributes:
        id: Unique page result identifier (UUID)
        crawl_job_id: Foreign key to crawl job
        url: Full URL of the analyzed page
        status_code: HTTP status code
        title: Page title
        meta_description: Meta description content
        h1_tags: Array of H1 headings
        word_count: Total word count on page
        load_time_ms: Page load time in milliseconds
        mobile_friendly: Whether page is mobile-friendly
        has_ssl: Whether page uses HTTPS
        canonical_url: Canonical URL if specified
        og_tags: Open Graph tags (JSON)
        schema_markup: Structured data (JSON)
        issues: Array of SEO issues found (JSON)
        seo_score: Overall SEO score (0-100)
        created_at: Result creation timestamp
    """

    __tablename__ = "page_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    crawl_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h1_tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    load_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mobile_friendly: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_ssl: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    canonical_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    schema_markup: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    issues: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    seo_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    crawl_job: Mapped["CrawlJob"] = relationship("CrawlJob", back_populates="page_results")
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation", back_populates="page_result", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PageResult(id={self.id}, url={self.url}, score={self.seo_score})>"
