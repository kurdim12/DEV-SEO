"""Website-related Pydantic schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
import re


class WebsiteCreate(BaseModel):
    """Schema for creating a new website."""

    domain: str = Field(..., description="Website domain (e.g., example.com)")
    name: Optional[str] = Field(None, description="Display name for the website")

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain."""
        # Remove protocol if present
        v = re.sub(r"^https?://", "", v)
        # Remove trailing slash
        v = v.rstrip("/")
        # Remove www. prefix
        v = re.sub(r"^www\.", "", v)
        # Basic domain validation
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-_.]+[a-zA-Z0-9]$", v):
            raise ValueError("Invalid domain format")
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "example": {
                "domain": "example.com",
                "name": "My Website",
            }
        }
    }


class WebsiteUpdate(BaseModel):
    """Schema for updating a website."""

    name: Optional[str] = Field(None, description="Display name for the website")
    settings: Optional[dict] = Field(None, description="Website settings")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Website Name",
                "settings": {"max_pages": 50, "exclude_paths": ["/admin"]},
            }
        }
    }


class WebsiteResponse(BaseModel):
    """Schema for website data in responses."""

    id: UUID
    user_id: UUID
    domain: str
    name: Optional[str] = None
    verified: bool
    verification_method: Optional[str] = None
    verification_token: Optional[str] = None
    settings: dict
    created_at: datetime
    last_scan_score: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "domain": "example.com",
                "name": "My Website",
                "verified": False,
                "verification_method": "dns",
                "verification_token": "devseo-verify-abc123",
                "settings": {},
                "created_at": "2026-02-06T12:00:00Z",
            }
        },
    }


class WebsiteVerifyRequest(BaseModel):
    """Schema for domain verification request."""

    method: str = Field(..., description="Verification method (dns, meta_tag, file)")

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate verification method."""
        allowed_methods = ["dns", "meta_tag", "file"]
        if v not in allowed_methods:
            raise ValueError(f"Method must be one of: {', '.join(allowed_methods)}")
        return v

    model_config = {
        "json_schema_extra": {"example": {"method": "dns"}}
    }


class WebsiteVerifyResponse(BaseModel):
    """Schema for domain verification response."""

    verified: bool
    message: str
    instructions: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "verified": False,
                "message": "Verification pending",
                "instructions": "Add the following TXT record to your DNS: devseo-verify-abc123",
            }
        }
    }
