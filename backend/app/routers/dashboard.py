"""
Dashboard router for getting user statistics and overview data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_clerk
from app.models.user import User
from app.models.website import Website
from app.models.crawl_job import CrawlJob
from app.models.page_result import PageResult

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get dashboard statistics for the current user.

    Returns:
        Dictionary with website count, scan count, and average SEO score
    """
    # Get website count
    result = await db.execute(
        select(func.count(Website.id)).where(Website.user_id == current_user.id)
    )
    website_count = result.scalar() or 0

    # Get scan count (completed scans this month)
    from datetime import datetime, timezone

    first_day_of_month = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    result = await db.execute(
        select(func.count(CrawlJob.id))
        .join(Website)
        .where(
            Website.user_id == current_user.id,
            CrawlJob.status == "completed",
            CrawlJob.created_at >= first_day_of_month,
        )
    )
    scans_this_month = result.scalar() or 0

    # Get average SEO score from all completed scans
    result = await db.execute(
        select(func.avg(PageResult.seo_score))
        .join(CrawlJob)
        .join(Website)
        .where(
            Website.user_id == current_user.id,
            CrawlJob.status == "completed",
            PageResult.seo_score.isnot(None),
        )
    )
    avg_score = result.scalar()
    avg_score = round(avg_score, 1) if avg_score else None

    # Get total pages scanned
    result = await db.execute(
        select(func.count(PageResult.id))
        .join(CrawlJob)
        .join(Website)
        .where(
            Website.user_id == current_user.id,
            CrawlJob.status == "completed",
        )
    )
    total_pages_scanned = result.scalar() or 0

    # Get recent activity (last 5 completed scans)
    result = await db.execute(
        select(CrawlJob, Website)
        .join(Website)
        .where(
            Website.user_id == current_user.id,
            CrawlJob.status == "completed",
        )
        .order_by(CrawlJob.completed_at.desc())
        .limit(5)
    )
    recent_scans = []
    for crawl_job, website in result.all():
        recent_scans.append({
            "id": str(crawl_job.id),
            "website_id": str(website.id),
            "website_name": website.name,
            "website_domain": website.domain,
            "pages_crawled": crawl_job.pages_crawled,
            "completed_at": crawl_job.completed_at.isoformat() if crawl_job.completed_at else None,
        })

    return {
        "website_count": website_count,
        "scans_this_month": scans_this_month,
        "avg_seo_score": avg_score,
        "total_pages_scanned": total_pages_scanned,
        "recent_scans": recent_scans,
    }
