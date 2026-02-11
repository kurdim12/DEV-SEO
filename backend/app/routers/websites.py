"""
Websites router for CRUD operations on user websites.
"""
from typing import List
from uuid import UUID
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_clerk
from app.models.user import User
from app.models.website import Website
from app.models.crawl_job import CrawlJob
from app.models.page_result import PageResult
from app.schemas.website import (
    WebsiteCreate,
    WebsiteUpdate,
    WebsiteResponse,
    WebsiteVerifyRequest,
    WebsiteVerifyResponse,
)
from app.services.verification_service import verification_service

router = APIRouter(prefix="/websites", tags=["Websites"])


@router.post(
    "",
    response_model=WebsiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new website",
)
async def create_website(
    website_data: WebsiteCreate,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> Website:
    """
    Add a new website to monitor.

    - **domain**: Website domain (e.g., example.com)
    - **name**: Optional display name
    """
    # Check if website already exists for this user
    result = await db.execute(
        select(Website).where(
            Website.user_id == current_user.id,
            Website.domain == website_data.domain,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website already exists",
        )

    # Enforce website limit for plan
    from app.routers.crawls import _get_plan_limits  # avoid circular import at top
    limits = _get_plan_limits(current_user.plan)
    count_result = await db.execute(
        select(func.count(Website.id)).where(Website.user_id == current_user.id)
    )
    current_count = count_result.scalar() or 0
    if current_count >= limits["websites"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Website limit reached ({limits['websites']} websites on {current_user.plan} plan). Upgrade to add more.",
        )

    # Create website
    website = Website(
        user_id=current_user.id,
        domain=website_data.domain,
        name=website_data.name or website_data.domain,
        verification_token=f"devseo-verify-{secrets.token_urlsafe(16)}",
    )

    db.add(website)
    await db.commit()
    await db.refresh(website)

    return website


@router.get(
    "",
    response_model=List[WebsiteResponse],
    summary="List user websites",
)
async def list_websites(
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get all websites for the authenticated user with last scan scores."""
    result = await db.execute(
        select(Website)
        .where(Website.user_id == current_user.id)
        .order_by(Website.created_at.desc())
    )
    websites = result.scalars().all()

    # Calculate last_scan_score for each website
    websites_with_scores = []
    for website in websites:
        # Get the latest completed crawl
        crawl_result = await db.execute(
            select(CrawlJob)
            .where(
                CrawlJob.website_id == website.id,
                CrawlJob.status == "completed",
            )
            .order_by(CrawlJob.completed_at.desc())
            .limit(1)
        )
        latest_crawl = crawl_result.scalar_one_or_none()

        last_scan_score = None
        if latest_crawl:
            # Calculate average score from pages
            pages_result = await db.execute(
                select(func.avg(PageResult.seo_score))
                .where(PageResult.crawl_job_id == latest_crawl.id)
            )
            avg_score = pages_result.scalar()
            if avg_score is not None:
                last_scan_score = round(float(avg_score))

        # Convert to dict and add last_scan_score
        website_dict = {
            "id": website.id,
            "user_id": website.user_id,
            "domain": website.domain,
            "name": website.name,
            "verified": website.verified,
            "verification_method": website.verification_method,
            "verification_token": website.verification_token,
            "settings": website.settings,
            "created_at": website.created_at,
            "last_scan_score": last_scan_score,
        }
        websites_with_scores.append(website_dict)

    return websites_with_scores


@router.get(
    "/{website_id}",
    response_model=WebsiteResponse,
    summary="Get website details",
)
async def get_website(
    website_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> Website:
    """Get details of a specific website."""
    result = await db.execute(
        select(Website).where(
            Website.id == website_id,
            Website.user_id == current_user.id,
        )
    )
    website = result.scalar_one_or_none()

    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found",
        )

    return website


@router.patch(
    "/{website_id}",
    response_model=WebsiteResponse,
    summary="Update website",
)
async def update_website(
    website_id: UUID,
    website_data: WebsiteUpdate,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> Website:
    """Update website details."""
    result = await db.execute(
        select(Website).where(
            Website.id == website_id,
            Website.user_id == current_user.id,
        )
    )
    website = result.scalar_one_or_none()

    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found",
        )

    # Update fields
    if website_data.name is not None:
        website.name = website_data.name
    if website_data.settings is not None:
        website.settings = website_data.settings

    await db.commit()
    await db.refresh(website)

    return website


@router.delete(
    "/{website_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete website",
)
async def delete_website(
    website_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
):
    """Delete a website and all its associated data."""
    result = await db.execute(
        select(Website).where(
            Website.id == website_id,
            Website.user_id == current_user.id,
        )
    )
    website = result.scalar_one_or_none()

    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found",
        )

    await db.delete(website)
    await db.commit()


@router.post(
    "/{website_id}/verify",
    response_model=WebsiteVerifyResponse,
    summary="Verify domain ownership",
)
async def verify_website(
    website_id: UUID,
    verify_request: WebsiteVerifyRequest,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> WebsiteVerifyResponse:
    """
    Verify domain ownership using DNS TXT record, meta tag, or file method.
    """
    result = await db.execute(
        select(Website).where(
            Website.id == website_id,
            Website.user_id == current_user.id,
        )
    )
    website = result.scalar_one_or_none()

    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found",
        )

    if website.verified:
        return WebsiteVerifyResponse(
            verified=True,
            message="Domain already verified",
        )

    # Set verification method
    website.verification_method = verify_request.method

    # Attempt actual verification
    verified, message = await verification_service.verify_domain(
        url=website.url,
        token=website.verification_token,
        method=verify_request.method
    )

    if verified:
        website.verified = True
        website.verified_at = func.now()
        await db.commit()

        return WebsiteVerifyResponse(
            verified=True,
            message=message,
        )
    else:
        # Return instructions if verification failed
        instructions = {
            "dns": f"Add the following TXT record to your DNS:\n\nName: _devseo-verify.{website.domain} or root domain\nValue: {website.verification_token}",
            "meta_tag": f'Add this meta tag to your homepage <head>:\n\n<meta name="devseo-verification" content="{website.verification_token}">',
            "file": f"Create a file at https://{website.domain}/.well-known/devseo-verify.txt with content:\n\n{website.verification_token}",
        }

        await db.commit()

        return WebsiteVerifyResponse(
            verified=False,
            message=message,
            instructions=instructions.get(verify_request.method),
        )
