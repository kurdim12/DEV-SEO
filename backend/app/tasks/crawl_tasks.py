"""
Celery tasks for website crawling and SEO analysis.
"""
import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.celery_app import celery_app
from app.config import settings
from app.models.crawl_job import CrawlJob
from app.models.page_result import PageResult
from app.services.crawler import WebCrawler
from app.services.seo_analyzer import SEOAnalyzer

logger = logging.getLogger(__name__)

# Create async engine for tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def run_async(coro):
    """Helper to run async functions in sync Celery tasks."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(
    name="app.tasks.crawl_tasks.process_crawl_job",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def process_crawl_job(self, crawl_job_id: str, website_domain: str, max_pages: int = 50):
    """
    Process a crawl job: crawl website and analyze SEO for each page.

    Args:
        crawl_job_id: UUID of the crawl job
        website_domain: Domain to crawl
        max_pages: Maximum number of pages to crawl

    Returns:
        dict: Summary of crawl results
    """
    try:
        logger.info(f"Starting crawl job {crawl_job_id} for {website_domain}")
        result = run_async(_process_crawl_job_async(crawl_job_id, website_domain, max_pages))
        logger.info(f"Completed crawl job {crawl_job_id}: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error processing crawl job {crawl_job_id}: {exc}", exc_info=True)
        # Retry the task
        raise self.retry(exc=exc)


async def _process_crawl_job_async(crawl_job_id: str, website_domain: str, max_pages: int):
    """Async implementation of crawl job processing."""
    async with SessionLocal() as db:
        try:
            # Get crawl job
            result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
            crawl_job = result.scalar_one_or_none()

            if not crawl_job:
                raise ValueError(f"Crawl job {crawl_job_id} not found")

            # Check if cancellation was requested
            if crawl_job.cancellation_requested:
                crawl_job.status = "cancelled"
                crawl_job.cancelled_at = datetime.now(timezone.utc)
                await db.commit()
                return {"status": "cancelled", "pages_crawled": 0}

            # Update status to running
            crawl_job.status = "running"
            crawl_job.started_at = datetime.now(timezone.utc)
            await db.commit()

            # Run crawler
            logger.info(f"Crawling {website_domain} (max {max_pages} pages)")
            crawler = WebCrawler(website_domain, max_pages=max_pages)
            crawl_results = await crawler.crawl()
            logger.info(f"Crawled {len(crawl_results)} pages")

            # Analyze each page
            analyzer = SEOAnalyzer()
            pages_analyzed = 0

            for crawl_result in crawl_results:
                # Check for cancellation between pages
                await db.refresh(crawl_job)
                if crawl_job.cancellation_requested:
                    crawl_job.status = "cancelled"
                    crawl_job.cancelled_at = datetime.now(timezone.utc)
                    await db.commit()
                    return {
                        "status": "cancelled",
                        "pages_crawled": pages_analyzed,
                        "total_pages": len(crawl_results)
                    }

                if crawl_result.error:
                    logger.warning(f"Error crawling {crawl_result.url}: {crawl_result.error}")
                    continue

                # Analyze page
                analysis = analyzer.analyze(
                    crawl_result.html,
                    crawl_result.url,
                    crawl_result.status_code,
                    headers=crawl_result.headers,
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
                    readability_score=analysis.readability_score,
                    readability_grade=analysis.readability_grade,
                    issues=[issue.to_dict() for issue in analysis.issues],
                    seo_score=analysis.seo_score,
                )
                db.add(page_result)
                pages_analyzed += 1

                # Update progress
                crawl_job.pages_crawled = pages_analyzed
                crawl_job.pages_total = len(crawl_results)

                # Commit every 10 pages to show progress
                if pages_analyzed % 10 == 0:
                    await db.commit()
                    logger.info(f"Progress: {pages_analyzed}/{len(crawl_results)} pages analyzed")

            # Final update
            crawl_job.status = "completed"
            crawl_job.completed_at = datetime.now(timezone.utc)
            crawl_job.pages_total = len(crawl_results)
            await db.commit()

            return {
                "status": "completed",
                "pages_crawled": pages_analyzed,
                "total_pages": len(crawl_results),
                "duration_seconds": (
                    crawl_job.completed_at - crawl_job.started_at
                ).total_seconds() if crawl_job.started_at else None
            }

        except Exception as e:
            logger.error(f"Error in crawl job {crawl_job_id}: {e}", exc_info=True)

            # Update job status to failed
            if crawl_job:
                crawl_job.status = "failed"
                crawl_job.error_message = str(e)
                crawl_job.completed_at = datetime.now(timezone.utc)
                await db.commit()

            raise


@celery_app.task(name="app.tasks.crawl_tasks.cleanup_old_results")
def cleanup_old_results():
    """
    Periodic task to clean up old crawl results.
    Removes page results older than 90 days.
    """
    try:
        logger.info("Starting cleanup of old results")
        result = run_async(_cleanup_old_results_async())
        logger.info(f"Cleanup completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error during cleanup: {exc}", exc_info=True)
        raise


async def _cleanup_old_results_async():
    """Async implementation of cleanup."""
    async with SessionLocal() as db:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

        # Delete old page results
        stmt = delete(PageResult).where(PageResult.created_at < cutoff_date)
        result = await db.execute(stmt)
        deleted_count = result.rowcount

        # Delete old completed/failed crawl jobs
        stmt = delete(CrawlJob).where(
            CrawlJob.completed_at < cutoff_date,
            CrawlJob.status.in_(["completed", "failed", "cancelled"])
        )
        result = await db.execute(stmt)
        deleted_jobs = result.rowcount

        await db.commit()

        return {
            "deleted_page_results": deleted_count,
            "deleted_crawl_jobs": deleted_jobs,
            "cutoff_date": cutoff_date.isoformat()
        }


@celery_app.task(name="app.tasks.crawl_tasks.cancel_crawl_job")
def cancel_crawl_job(crawl_job_id: str):
    """
    Mark a crawl job for cancellation.

    The actual cancellation happens in the running task when it checks
    the cancellation_requested flag.

    Args:
        crawl_job_id: UUID of the crawl job to cancel

    Returns:
        dict: Status of cancellation request
    """
    try:
        logger.info(f"Cancelling crawl job {crawl_job_id}")
        result = run_async(_cancel_crawl_job_async(crawl_job_id))
        return result
    except Exception as exc:
        logger.error(f"Error cancelling crawl job {crawl_job_id}: {exc}", exc_info=True)
        raise


async def _cancel_crawl_job_async(crawl_job_id: str):
    """Async implementation of crawl job cancellation."""
    async with SessionLocal() as db:
        result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
        crawl_job = result.scalar_one_or_none()

        if not crawl_job:
            raise ValueError(f"Crawl job {crawl_job_id} not found")

        if crawl_job.status in ["completed", "failed", "cancelled"]:
            return {"status": "already_finished", "current_status": crawl_job.status}

        crawl_job.cancellation_requested = True
        await db.commit()

        return {"status": "cancellation_requested", "crawl_job_id": crawl_job_id}
