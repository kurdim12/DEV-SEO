"""Crawl job model for tracking website crawl operations."""
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class CrawlJob(Base):
    """
    Crawl job model for tracking website crawl operations.

    Attributes:
        id: Unique crawl job identifier (UUID)
        website_id: Foreign key to website being crawled
        status: Current status (pending, running, completed, failed, cancelled)
        pages_crawled: Number of pages successfully crawled
        pages_total: Total number of pages discovered
        started_at: When the crawl started
        completed_at: When the crawl finished
        error_message: Error details if crawl failed
        cancellation_requested: Whether user requested cancellation
        cancelled_at: When the crawl was cancelled
        created_at: Job creation timestamp
    """

    __tablename__ = "crawl_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )  # pending, running, completed, failed
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancellation_requested: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    website: Mapped["Website"] = relationship("Website", back_populates="crawl_jobs")
    page_results: Mapped[list["PageResult"]] = relationship(
        "PageResult", back_populates="crawl_job", cascade="all, delete-orphan"
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation", back_populates="crawl_job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CrawlJob(id={self.id}, status={self.status}, pages={self.pages_crawled}/{self.pages_total})>"
