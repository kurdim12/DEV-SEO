"""
AI Recommendation model for storing Claude-generated SEO recommendations.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIRecommendation(Base):
    """
    Stores AI-generated SEO recommendations for crawl jobs and individual pages.

    Attributes:
        id: Unique identifier
        crawl_job_id: Foreign key to the crawl job this recommendation belongs to
        page_result_id: Optional foreign key to a specific page (null for overall recommendations)
        recommendation_type: Type of recommendation (content_quality, technical_seo, on_page, overall)
        title: Short title of the recommendation
        description: Detailed description with actionable steps
        priority: Priority level (high, medium, low)
        ai_generated_at: When the AI generated this recommendation
        implementation_status: Status (pending, implemented, dismissed)
        created_at: When the record was created
        updated_at: When the record was last updated
    """

    __tablename__ = "ai_recommendations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    crawl_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("crawl_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_result_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("page_results.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # high, medium, low
    ai_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    implementation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True, server_default="pending"
    )  # pending, implemented, dismissed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default="now()",
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default="now()",
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    crawl_job: Mapped["CrawlJob"] = relationship("CrawlJob", back_populates="ai_recommendations")
    page_result: Mapped[Optional["PageResult"]] = relationship("PageResult", back_populates="ai_recommendations")

    def __repr__(self) -> str:
        return f"<AIRecommendation {self.title} ({self.priority})>"
