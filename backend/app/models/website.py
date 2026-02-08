"""Website model for managing user websites."""
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class Website(Base):
    """
    Website model representing user websites to be analyzed.

    Attributes:
        id: Unique website identifier (UUID)
        user_id: Foreign key to user who owns this website
        domain: Website domain (e.g., example.com)
        name: Display name for the website
        verified: Whether domain ownership is verified
        verification_method: Method used for verification (dns, meta_tag, file)
        verification_token: Token for domain verification
        settings: JSON settings (crawl depth, exclusions, etc.)
        created_at: Website creation timestamp
    """

    __tablename__ = "websites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_method: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # dns, meta_tag, file
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="websites")
    crawl_jobs: Mapped[list["CrawlJob"]] = relationship("CrawlJob", back_populates="website", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Website(id={self.id}, domain={self.domain}, verified={self.verified})>"
