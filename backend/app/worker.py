"""
Background worker for processing crawl jobs.

This worker polls the database for pending crawl jobs and processes them.
Run this script separately from the main FastAPI application:
    python -m app.worker
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.models.crawl_job import CrawlJob
from app.models.website import Website
from app.models.page_result import PageResult
from app.services.crawler import WebCrawler
from app.services.seo_analyzer import SEOAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrawlWorker:
    """Background worker that processes crawl jobs."""

    def __init__(self):
        """Initialize the worker."""
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.SessionLocal = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.running = True

    async def process_crawl_job(self, crawl_job_id: str, website_domain: str, max_pages: int):
        """
        Process a single crawl job.

        Args:
            crawl_job_id: ID of the crawl job
            website_domain: Domain to crawl
            max_pages: Maximum pages to crawl
        """
        async with self.SessionLocal() as db:
            try:
                logger.info(f"Starting crawl job {crawl_job_id} for {website_domain}")

                # Update status to running
                result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
                crawl_job = result.scalar_one()
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
                        issues=[issue.to_dict() for issue in analysis.issues],
                        seo_score=analysis.seo_score,
                    )
                    db.add(page_result)
                    pages_analyzed += 1

                    # Commit every 5 pages to show progress
                    if pages_analyzed % 5 == 0:
                        crawl_job.pages_crawled = pages_analyzed
                        await db.commit()
                        logger.info(f"Analyzed {pages_analyzed} pages so far")

                # Update crawl job status
                result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
                crawl_job = result.scalar_one()
                crawl_job.status = "completed"
                crawl_job.completed_at = datetime.now(timezone.utc)
                crawl_job.pages_crawled = len(crawl_results)
                crawl_job.pages_total = len(crawl_results)

                await db.commit()
                logger.info(f"Completed crawl job {crawl_job_id}: {pages_analyzed} pages analyzed")

            except Exception as e:
                logger.error(f"Error processing crawl job {crawl_job_id}: {str(e)}", exc_info=True)
                # Update status to failed
                try:
                    result = await db.execute(select(CrawlJob).where(CrawlJob.id == crawl_job_id))
                    crawl_job = result.scalar_one()
                    crawl_job.status = "failed"
                    crawl_job.error_message = str(e)
                    crawl_job.completed_at = datetime.now(timezone.utc)
                    await db.commit()
                except Exception as commit_error:
                    logger.error(f"Failed to update job status: {commit_error}")

    async def check_for_pending_jobs(self):
        """Check database for pending crawl jobs and process them."""
        async with self.SessionLocal() as db:
            try:
                # Find pending jobs
                result = await db.execute(
                    select(CrawlJob, Website)
                    .join(Website)
                    .where(CrawlJob.status == "pending")
                    .limit(5)  # Process up to 5 jobs at a time
                )
                jobs = result.all()

                for crawl_job, website in jobs:
                    # Determine max pages based on plan
                    max_pages = settings.FREE_MAX_PAGES_PER_SCAN

                    # Process job in background
                    asyncio.create_task(
                        self.process_crawl_job(
                            str(crawl_job.id),
                            website.domain,
                            max_pages
                        )
                    )

            except Exception as e:
                logger.error(f"Error checking for pending jobs: {str(e)}", exc_info=True)

    async def run(self):
        """Run the worker continuously."""
        logger.info("Starting crawl worker...")
        logger.info(f"Checking for jobs every {settings.WORKER_POLL_INTERVAL_SECONDS} seconds")

        while self.running:
            try:
                await self.check_for_pending_jobs()
                await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}", exc_info=True)
                await asyncio.sleep(5)  # Wait a bit before retrying

        # Cleanup
        await self.engine.dispose()
        logger.info("Worker shut down complete")


async def main():
    """Main entry point for the worker."""
    worker = CrawlWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
