"""
Crawls router for managing website crawl jobs.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.dependencies import get_current_user_clerk
from app.models.user import User
from app.models.website import Website
from app.models.crawl_job import CrawlJob
from app.models.page_result import PageResult
from app.models.ai_recommendation import AIRecommendation
from app.schemas.crawl import CrawlJobResponse, PageResultResponse, CrawlReport
from app.schemas.recommendation import (
    AIRecommendationResponse,
    GenerateRecommendationsRequest,
    UpdateRecommendationRequest,
    RecommendationsSummary,
)
from app.services.crawler import WebCrawler
from app.services.seo_analyzer import SEOAnalyzer
from app.services.ai_service import AIService
from app.services.email_service import email_service
from app.config import settings
from app.tasks.crawl_tasks import process_crawl_job

router = APIRouter(prefix="/crawls", tags=["Crawls"])
limiter = Limiter(key_func=get_remote_address)


def _get_plan_limits(plan: str) -> dict:
    """Return (max_websites, max_scans_per_month, max_pages_per_scan) for a plan."""
    return {
        "free": {
            "websites": settings.FREE_MAX_WEBSITES,
            "scans": settings.FREE_MAX_SCANS_PER_MONTH,
            "pages": settings.FREE_MAX_PAGES_PER_SCAN,
        },
        "pro": {
            "websites": settings.PRO_MAX_WEBSITES,
            "scans": settings.PRO_MAX_SCANS_PER_MONTH,
            "pages": settings.PRO_MAX_PAGES_PER_SCAN,
        },
        "agency": {
            "websites": settings.AGENCY_MAX_WEBSITES,
            "scans": settings.AGENCY_MAX_SCANS_PER_MONTH,
            "pages": settings.AGENCY_MAX_PAGES_PER_SCAN,
        },
    }.get(plan, {"websites": 1, "scans": 1, "pages": 10})


async def run_crawl_job(
    crawl_job_id: UUID,
    website_domain: str,
    max_pages: int,
    db_url: str,
):
    """
    Background task to run a crawl job.

    Args:
        crawl_job_id: ID of the crawl job
        website_domain: Domain to crawl
        max_pages: Maximum pages to crawl
        db_url: Database URL
    """
    import logging
    import asyncio
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Starting crawl job {crawl_job_id} for {website_domain}")

    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession as AS

    # Create new engine and session for background task
    engine = create_async_engine(db_url)
    SessionLocal = async_sessionmaker(engine, class_=AS, expire_on_commit=False)

    async with SessionLocal() as db:
        try:
            # Update status to running
            result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
            crawl_job = result.scalar_one()
            crawl_job.status = "running"
            crawl_job.started_at = datetime.now(timezone.utc)
            await db.commit()

            # Progress tracking state
            last_update_count = 0

            # Define progress callback for live updates
            async def _update_progress(pages_crawled: int, pages_total: int):
                nonlocal last_update_count

                # Only write to DB every 3 pages to avoid spam
                if pages_crawled - last_update_count >= 3 or pages_crawled == pages_total:
                    # Refresh crawl job to check for cancellation
                    await db.refresh(crawl_job)

                    # Check if user requested cancellation
                    if crawl_job.cancellation_requested:
                        logger.info(f"🛑 Cancellation requested for crawl job {crawl_job_id}")
                        raise asyncio.CancelledError("Crawl cancelled by user")

                    # Update progress
                    crawl_job.pages_crawled = pages_crawled
                    crawl_job.pages_total = pages_total
                    await db.commit()
                    last_update_count = pages_crawled
                    logger.info(f"📊 Progress: {pages_crawled}/{pages_total} pages")

            # Run crawler with progress callback
            crawler = WebCrawler(website_domain, max_pages=max_pages)
            crawl_results = await crawler.crawl(progress_callback=_update_progress)

            # Analyze each page
            analyzer = SEOAnalyzer()
            page_results = []

            for crawl_result in crawl_results:
                if crawl_result.error:
                    continue

                # Analyze page
                analysis = analyzer.analyze(
                    crawl_result.html,
                    crawl_result.url,
                    crawl_result.status_code,
                )

                # Save page result
                page_result = PageResult(
                    crawl_job_id=crawl_job_id,
                    url=analysis.url,
                    status_code=crawl_result.status_code,
                    title=analysis.title,
                    meta_description=analysis.meta_description,
                    h1_tags=analysis.h1_tags,
                    word_count=analysis.word_count,
                    load_time_ms=crawl_result.load_time_ms,
                    mobile_friendly=analysis.mobile_friendly,
                    has_ssl=analysis.has_ssl,
                    canonical_url=analysis.canonical_url,
                    og_tags=analysis.og_tags,
                    schema_markup=analysis.schema_markup,
                    issues=[issue.to_dict() for issue in analysis.issues],
                    seo_score=analysis.seo_score,
                )
                db.add(page_result)
                page_results.append(page_result)

            # Commit pages first so we have IDs
            await db.commit()

            # Detect broken links
            # Build status map from crawl results
            status_map = {result.url: result.status_code for result in crawl_results}

            # Check each page for broken outgoing links
            for i, crawl_result in enumerate(crawl_results):
                if crawl_result.error or not crawl_result.outgoing_links:
                    continue

                page_result = page_results[i]
                broken_links = []

                for link in crawl_result.outgoing_links:
                    link_status = status_map.get(link)
                    # Check if link has 4xx or 5xx status
                    if link_status and (400 <= link_status < 600):
                        broken_links.append(link)

                # Add broken links issue if any found
                if broken_links:
                    issues = page_result.issues or []
                    issues.append({
                        "type": "broken_links",
                        "severity": "critical",
                        "message": f"Found {len(broken_links)} broken link(s) on this page",
                        "details": broken_links[:5],  # Limit to first 5 broken links
                    })
                    page_result.issues = issues
                    # Recalculate SEO score (deduct 5 points for broken links)
                    if page_result.seo_score:
                        page_result.seo_score = max(0, page_result.seo_score - 5)

            # Commit updated issues
            await db.commit()

            # Generate AI recommendations automatically (rule-based only, free!)
            ai_service = AIService()

            for page in page_results:
                page_data = {
                    "id": page.id,
                    "url": page.url,
                    "title": page.title,
                    "meta_description": page.meta_description,
                    "h1_tags": page.h1_tags,
                    "word_count": page.word_count,
                    "issues": page.issues,
                    "seo_score": page.seo_score,
                }

                # Generate rule-based recommendations (free, no AI cost)
                recommendations = await ai_service.generate_page_recommendations(
                    page_data,
                    use_ai_analysis=False,  # Don't use paid AI by default
                )

                # Save recommendations
                for rec_data in recommendations:
                    recommendation = AIRecommendation(
                        crawl_job_id=crawl_job_id,
                        page_result_id=rec_data.get("page_result_id"),
                        recommendation_type=rec_data["recommendation_type"],
                        title=rec_data["title"],
                        description=rec_data["description"],
                        priority=rec_data["priority"],
                        ai_generated_at=rec_data["ai_generated_at"],
                        implementation_status="pending",
                    )
                    db.add(recommendation)

            # Generate overall site-wide recommendations
            crawl_stats = {
                "avg_seo_score": sum(p.seo_score or 0 for p in page_results) / len(page_results) if page_results else 0,
                "total_issues": sum(len(p.issues) for p in page_results),
            }

            pages_data = [
                {
                    "id": p.id,
                    "url": p.url,
                    "title": p.title,
                    "meta_description": p.meta_description,
                    "h1_tags": p.h1_tags,
                    "word_count": p.word_count,
                    "issues": p.issues,
                    "seo_score": p.seo_score,
                }
                for p in page_results
            ]

            overall_recommendations = await ai_service.generate_overall_recommendations(
                pages_data,
                crawl_stats,
                use_ai_analysis=False,  # Don't use paid AI by default
            )

            for rec_data in overall_recommendations:
                recommendation = AIRecommendation(
                    crawl_job_id=crawl_job_id,
                    page_result_id=rec_data.get("page_result_id"),
                    recommendation_type=rec_data["recommendation_type"],
                    title=rec_data["title"],
                    description=rec_data["description"],
                    priority=rec_data["priority"],
                    ai_generated_at=rec_data["ai_generated_at"],
                    implementation_status="pending",
                )
                db.add(recommendation)

            # Update crawl job status
            crawl_job.status = "completed"
            crawl_job.completed_at = datetime.now(timezone.utc)
            crawl_job.pages_crawled = len(crawl_results)
            crawl_job.pages_total = len(crawl_results)

            await db.commit()

            # Send email notification
            try:
                await db.refresh(crawl_job, ["website"])
                await db.refresh(crawl_job.website, ["user"])

                if crawl_job.website.user.email:
                    # Calculate stats
                    avg_score = sum(p.seo_score for p in page_results if p.seo_score) / len(page_results) if page_results else 0
                    total_issues = sum(len(p.issues or []) for p in page_results)

                    report_url = f"{settings.FRONTEND_URL}/reports/{crawl_job_id}" if hasattr(settings, 'FRONTEND_URL') else f"https://app.devseo.io/reports/{crawl_job_id}"

                    await email_service.send_scan_complete(
                        to_email=crawl_job.website.user.email,
                        website_url=website_domain,
                        score=int(avg_score),
                        total_pages=len(page_results),
                        total_issues=total_issues,
                        report_url=report_url
                    )
                    logger.info(f"📧 Sent completion email to {crawl_job.website.user.email}")
            except Exception as email_error:
                logger.error(f"Failed to send completion email: {email_error}")

        except asyncio.CancelledError:
            logger.info(f"🛑 Crawl job {crawl_job_id} was cancelled")
            # Update status to cancelled
            await db.refresh(crawl_job)
            crawl_job.status = "cancelled"
            crawl_job.cancelled_at = datetime.now(timezone.utc)
            crawl_job.completed_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as e:
            logger.error(f"❌ Crawl job {crawl_job_id} failed: {e}", exc_info=True)
            # Update status to failed
            result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
            crawl_job = result.scalar_one()
            crawl_job.status = "failed"
            crawl_job.error_message = str(e)
            crawl_job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            # Send failure email notification
            try:
                await db.refresh(crawl_job, ["website"])
                await db.refresh(crawl_job.website, ["user"])

                if crawl_job.website.user.email:
                    await email_service.send_scan_failed(
                        to_email=crawl_job.website.user.email,
                        website_url=website_domain,
                        error_message=str(e)
                    )
                    logger.info(f"📧 Sent failure email to {crawl_job.website.user.email}")
            except Exception as email_error:
                logger.error(f"Failed to send failure email: {email_error}")

        finally:
            await engine.dispose()


@router.post(
    "/websites/{website_id}/crawl",
    response_model=CrawlJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a crawl job",
)
@limiter.limit("5/hour")  # 5 scans per hour per IP
async def start_crawl(
    request: Request,
    website_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> CrawlJob:
    """
    Start a new crawl job for a website.
    """
    # Get website
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

    # Check if there's already a running crawl
    result = await db.execute(
        select(CrawlJob).where(
            CrawlJob.website_id == website_id,
            CrawlJob.status.in_(["pending", "running"]),
        )
    )
    running_crawl = result.scalar_one_or_none()

    if running_crawl:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A crawl is already in progress for this website",
        )

    # Enforce plan limits
    limits = _get_plan_limits(current_user.plan)

    # Count scans this month
    now = datetime.now(timezone.utc)
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    scans_result = await db.execute(
        select(func.count(CrawlJob.id))
        .join(Website)
        .where(
            Website.user_id == current_user.id,
            CrawlJob.created_at >= first_of_month,
        )
    )
    scans_this_month = scans_result.scalar() or 0

    if scans_this_month >= limits["scans"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly scan limit reached ({limits['scans']} scans/month on {current_user.plan} plan). Upgrade to scan more.",
        )

    # Determine max pages based on plan
    max_pages = limits["pages"]

    # Create crawl job
    crawl_job = CrawlJob(
        website_id=website_id,
        status="pending",
    )
    db.add(crawl_job)
    await db.commit()
    await db.refresh(crawl_job)

    # Start crawl using Celery (async task processing)
    process_crawl_job.delay(
        str(crawl_job.id),
        website.domain,
        max_pages
    )

    return crawl_job


@router.get(
    "/{crawl_id}",
    response_model=CrawlJobResponse,
    summary="Get crawl job status",
)
async def get_crawl_job(
    crawl_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> CrawlJob:
    """Get the status of a crawl job."""
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    return crawl_job


@router.post(
    "/{crawl_id}/cancel",
    response_model=CrawlJobResponse,
    summary="Cancel a running crawl job",
)
async def cancel_crawl(
    crawl_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> CrawlJob:
    """Request cancellation of a running crawl job."""
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    # Can only cancel running or pending jobs
    if crawl_job.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a crawl with status: {crawl_job.status}",
        )

    # Mark for cancellation
    crawl_job.cancellation_requested = True
    await db.commit()
    await db.refresh(crawl_job)

    return crawl_job


@router.get(
    "/{crawl_id}/report",
    response_model=CrawlReport,
    summary="Get full crawl report",
)
async def get_crawl_report(
    crawl_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the complete crawl report with all page results."""
    # Get crawl job
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    # Get all page results
    result = await db.execute(
        select(PageResult)
        .where(PageResult.crawl_job_id == crawl_id)
        .order_by(PageResult.seo_score.desc())
    )
    pages = result.scalars().all()

    # Calculate summary statistics
    if pages:
        avg_score = sum(p.seo_score or 0 for p in pages) / len(pages)
        total_issues = sum(len(p.issues) for p in pages)
        critical_issues = sum(
            len([i for i in p.issues if i.get("severity") == "critical"]) for p in pages
        )
        warning_issues = sum(
            len([i for i in p.issues if i.get("severity") == "warning"]) for p in pages
        )
        info_issues = sum(
            len([i for i in p.issues if i.get("severity") == "info"]) for p in pages
        )
    else:
        avg_score = 0
        total_issues = 0
        critical_issues = 0
        warning_issues = 0
        info_issues = 0

    return {
        "crawl_job": crawl_job,
        "pages": pages,
        "summary": {
            "avg_score": round(avg_score, 1),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "info_issues": info_issues,
        },
    }


@router.get(
    "/{crawl_id}/export/csv",
    summary="Export crawl report as CSV",
)
async def export_crawl_csv(
    crawl_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export all page results from a crawl as CSV."""
    # Get crawl job and verify ownership
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    # Get all page results
    result = await db.execute(
        select(PageResult)
        .where(PageResult.crawl_job_id == crawl_id)
        .order_by(PageResult.seo_score.desc())
    )
    pages = result.scalars().all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "URL",
        "Status Code",
        "SEO Score",
        "Title",
        "Meta Description",
        "H1 Tags",
        "Word Count",
        "Load Time (ms)",
        "Mobile Friendly",
        "Has SSL",
        "Total Issues",
        "Critical Issues",
        "Warning Issues",
    ])

    # Write data rows
    for page in pages:
        issues = page.issues or []
        critical_count = len([i for i in issues if i.get("severity") == "critical"])
        warning_count = len([i for i in issues if i.get("severity") == "warning"])

        writer.writerow([
            page.url,
            page.status_code,
            page.seo_score or 0,
            page.title or "",
            page.meta_description or "",
            "; ".join(page.h1_tags or []),
            page.word_count or 0,
            page.load_time_ms,
            "Yes" if page.mobile_friendly else "No",
            "Yes" if page.has_ssl else "No",
            len(issues),
            critical_count,
            warning_count,
        ])

    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=seo-report-{crawl_id}.csv"
        },
    )


@router.get(
    "/websites/{website_id}/score-history",
    summary="Get score history for a website",
)
async def get_score_history(
    website_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get score history for a website showing avg score over time."""
    # Verify website ownership
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

    # Get completed crawls with their average scores
    result = await db.execute(
        select(
            CrawlJob.id,
            CrawlJob.completed_at,
            func.avg(PageResult.seo_score).label("avg_score"),
            func.count(PageResult.id).label("pages_count"),
        )
        .join(PageResult, PageResult.crawl_job_id == CrawlJob.id)
        .where(
            CrawlJob.website_id == website_id,
            CrawlJob.status == "completed",
        )
        .group_by(CrawlJob.id, CrawlJob.completed_at)
        .order_by(CrawlJob.completed_at.asc())
    )

    history = []
    for row in result:
        history.append({
            "crawl_id": str(row.id),
            "date": row.completed_at.isoformat() if row.completed_at else None,
            "avg_score": round(float(row.avg_score or 0), 1),
            "pages_count": row.pages_count,
        })

    return history


@router.get(
    "/websites/{website_id}/history",
    response_model=List[CrawlJobResponse],
    summary="Get crawl history",
)
async def get_crawl_history(
    website_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> List[CrawlJob]:
    """Get all crawl jobs for a website."""
    # Verify website ownership
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

    # Get crawl history
    result = await db.execute(
        select(CrawlJob)
        .where(CrawlJob.website_id == website_id)
        .order_by(CrawlJob.created_at.desc())
    )
    crawls = result.scalars().all()

    return list(crawls)


@router.post(
    "/{crawl_id}/recommendations",
    response_model=List[AIRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI recommendations for a crawl",
)
async def generate_recommendations(
    crawl_id: UUID,
    request: GenerateRecommendationsRequest,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> List[AIRecommendation]:
    """
    Generate AI-powered SEO recommendations for a completed crawl.

    This uses a hybrid 3-tier approach:
    1. Rule-based engine (FREE, fast, covers 95% of issues)
    2. GPT-4o-mini (CHEAP ~$0.0005/page, optional for content analysis)
    3. Ollama (FREE, optional for privacy)
    """
    # Get crawl job
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    if crawl_job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crawl must be completed before generating recommendations",
        )

    # Check if recommendations already exist
    result = await db.execute(
        select(AIRecommendation).where(AIRecommendation.crawl_job_id == crawl_id)
    )
    existing_recommendations = result.scalars().all()

    if existing_recommendations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendations already generated for this crawl. Use GET to retrieve them.",
        )

    # Get all page results
    result = await db.execute(
        select(PageResult).where(PageResult.crawl_job_id == crawl_id)
    )
    pages = result.scalars().all()

    if not pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pages found for this crawl",
        )

    # Initialize AI service
    ai_service = AIService()

    # Generate recommendations for each page
    all_recommendations = []
    for page in pages:
        page_data = {
            "id": page.id,
            "url": page.url,
            "title": page.title,
            "meta_description": page.meta_description,
            "h1_tags": page.h1_tags,
            "word_count": page.word_count,
            "issues": page.issues,
            "seo_score": page.seo_score,
        }

        recommendations = await ai_service.generate_page_recommendations(
            page_data,
            use_ai_analysis=request.use_ai_analysis,
        )

        all_recommendations.extend(recommendations)

    # Generate overall site-wide recommendations
    crawl_stats = {
        "avg_seo_score": sum(p.seo_score or 0 for p in pages) / len(pages),
        "total_issues": sum(len(p.issues) for p in pages),
    }

    pages_data = [
        {
            "id": p.id,
            "url": p.url,
            "title": p.title,
            "meta_description": p.meta_description,
            "h1_tags": p.h1_tags,
            "word_count": p.word_count,
            "issues": p.issues,
            "seo_score": p.seo_score,
        }
        for p in pages
    ]

    overall_recommendations = await ai_service.generate_overall_recommendations(
        pages_data,
        crawl_stats,
        use_ai_analysis=request.use_ai_analysis,
    )

    all_recommendations.extend(overall_recommendations)

    # Save recommendations to database
    db_recommendations = []
    for rec_data in all_recommendations:
        recommendation = AIRecommendation(
            crawl_job_id=crawl_id,
            page_result_id=rec_data.get("page_result_id"),
            recommendation_type=rec_data["recommendation_type"],
            title=rec_data["title"],
            description=rec_data["description"],
            priority=rec_data["priority"],
            ai_generated_at=rec_data["ai_generated_at"],
            implementation_status="pending",
        )
        db.add(recommendation)
        db_recommendations.append(recommendation)

    await db.commit()

    # Refresh to get IDs
    for rec in db_recommendations:
        await db.refresh(rec)

    return db_recommendations


@router.get(
    "/{crawl_id}/recommendations",
    response_model=List[AIRecommendationResponse],
    summary="Get recommendations for a crawl",
)
async def get_recommendations(
    crawl_id: UUID,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> List[AIRecommendation]:
    """
    Get all AI recommendations for a crawl job.

    Optional filters:
    - priority: Filter by priority (high, medium, low)
    - status: Filter by implementation status (pending, in_progress, completed, dismissed)
    """
    # Verify crawl job ownership
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    # Build query
    query = select(AIRecommendation).where(AIRecommendation.crawl_job_id == crawl_id)

    if priority:
        query = query.where(AIRecommendation.priority == priority)

    if status_filter:
        query = query.where(AIRecommendation.implementation_status == status_filter)

    query = query.order_by(
        # Order by priority (high -> medium -> low)
        AIRecommendation.priority.desc(),
        AIRecommendation.created_at.desc(),
    )

    result = await db.execute(query)
    recommendations = result.scalars().all()

    return list(recommendations)


@router.get(
    "/{crawl_id}/recommendations/summary",
    response_model=RecommendationsSummary,
    summary="Get recommendations summary",
)
async def get_recommendations_summary(
    crawl_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get summary statistics for recommendations."""
    # Verify crawl job ownership
    result = await db.execute(
        select(CrawlJob)
        .join(Website)
        .where(
            CrawlJob.id == crawl_id,
            Website.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()

    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )

    # Get all recommendations
    result = await db.execute(
        select(AIRecommendation).where(AIRecommendation.crawl_job_id == crawl_id)
    )
    recommendations = result.scalars().all()

    # Calculate summary
    by_priority = {"high": 0, "medium": 0, "low": 0}
    by_status = {"pending": 0, "in_progress": 0, "completed": 0, "dismissed": 0}
    by_type = {}

    for rec in recommendations:
        # Count by priority
        if rec.priority in by_priority:
            by_priority[rec.priority] += 1

        # Count by status
        if rec.implementation_status in by_status:
            by_status[rec.implementation_status] += 1

        # Count by type
        if rec.recommendation_type not in by_type:
            by_type[rec.recommendation_type] = 0
        by_type[rec.recommendation_type] += 1

    return {
        "total": len(recommendations),
        "by_priority": by_priority,
        "by_status": by_status,
        "by_type": by_type,
    }


@router.patch(
    "/recommendations/{recommendation_id}",
    response_model=AIRecommendationResponse,
    summary="Update recommendation status",
)
async def update_recommendation(
    recommendation_id: UUID,
    request: UpdateRecommendationRequest,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
) -> AIRecommendation:
    """Update the implementation status of a recommendation."""
    # Get recommendation and verify ownership
    result = await db.execute(
        select(AIRecommendation)
        .join(CrawlJob)
        .join(Website)
        .where(
            AIRecommendation.id == recommendation_id,
            Website.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "dismissed"]
    if request.implementation_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    # Update status
    recommendation.implementation_status = request.implementation_status
    recommendation.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(recommendation)

    return recommendation

