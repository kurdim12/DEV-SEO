"""
Celery tasks for email sending and notifications.
"""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.celery_app import celery_app
from app.config import settings
from app.models.user import User
from app.models.crawl_job import CrawlJob
from app.services.email_service import EmailService

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
    name="app.tasks.email_tasks.send_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
)
def send_email(self, to_email: str, subject: str, html_content: str):
    """
    Send an email using SendGrid.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content

    Returns:
        dict: Status of email sending
    """
    try:
        logger.info(f"Sending email to {to_email}: {subject}")

        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid API key not configured, skipping email send")
            return {"status": "skipped", "reason": "sendgrid_not_configured"}

        email_service = EmailService()
        result = run_async(
            email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )
        )

        logger.info(f"Email sent successfully to {to_email}")
        return {"status": "sent", "to": to_email, "subject": subject}

    except Exception as exc:
        logger.error(f"Error sending email to {to_email}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.email_tasks.send_crawl_complete_notification")
def send_crawl_complete_notification(crawl_job_id: str, user_email: str):
    """
    Send notification email when a crawl job completes.

    Args:
        crawl_job_id: UUID of the completed crawl job
        user_email: User's email address

    Returns:
        dict: Status of notification
    """
    try:
        logger.info(f"Sending crawl completion notification for job {crawl_job_id}")
        result = run_async(_send_crawl_complete_notification_async(crawl_job_id, user_email))
        return result
    except Exception as exc:
        logger.error(f"Error sending crawl notification: {exc}", exc_info=True)
        raise


async def _send_crawl_complete_notification_async(crawl_job_id: str, user_email: str):
    """Async implementation of crawl completion notification."""
    async with SessionLocal() as db:
        # Get crawl job details
        result = await db.execute(
            select(CrawlJob).where(CrawlJob.id == crawl_job_id)
        )
        crawl_job = result.scalar_one_or_none()

        if not crawl_job:
            raise ValueError(f"Crawl job {crawl_job_id} not found")

        # Generate email content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Your SEO Crawl is Complete!</h2>

                <p>Hi there,</p>

                <p>Great news! Your website crawl has finished processing.</p>

                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Crawl Summary</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>Pages Analyzed:</strong> {crawl_job.pages_crawled}</li>
                        <li><strong>Status:</strong> {crawl_job.status.title()}</li>
                        <li><strong>Started:</strong> {crawl_job.started_at.strftime('%Y-%m-%d %H:%M UTC') if crawl_job.started_at else 'N/A'}</li>
                        <li><strong>Completed:</strong> {crawl_job.completed_at.strftime('%Y-%m-%d %H:%M UTC') if crawl_job.completed_at else 'N/A'}</li>
                    </ul>
                </div>

                <p>You can now review your SEO analysis and get actionable recommendations to improve your website's search engine ranking.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://devseo.io/dashboard"
                       style="background-color: #4CAF50; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Results
                    </a>
                </div>

                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Need help? Reply to this email or visit our <a href="https://devseo.io/support">support center</a>.
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="color: #999; font-size: 12px; text-align: center;">
                    DevSEO - AI-Powered SEO Analysis Platform<br>
                    <a href="https://devseo.io" style="color: #999;">devseo.io</a>
                </p>
            </div>
        </body>
        </html>
        """

        # Send email
        email_service = EmailService()
        await email_service.send_email(
            to_email=user_email,
            subject=f"Your SEO Crawl is Complete - {crawl_job.pages_crawled} Pages Analyzed",
            html_content=html_content
        )

        return {
            "status": "sent",
            "crawl_job_id": crawl_job_id,
            "user_email": user_email,
            "pages_crawled": crawl_job.pages_crawled
        }


@celery_app.task(name="app.tasks.email_tasks.send_daily_digest")
def send_daily_digest():
    """
    Send daily digest emails to active users.
    Scheduled to run once per day via Celery Beat.

    Returns:
        dict: Summary of emails sent
    """
    try:
        logger.info("Starting daily digest email send")
        result = run_async(_send_daily_digest_async())
        logger.info(f"Daily digest complete: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error sending daily digest: {exc}", exc_info=True)
        raise


async def _send_daily_digest_async():
    """Async implementation of daily digest."""
    async with SessionLocal() as db:
        # Get users who had crawls in the last 24 hours
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        stmt = select(User).join(User.websites).join(CrawlJob).where(
            CrawlJob.completed_at >= yesterday,
            CrawlJob.status == "completed"
        ).distinct()

        result = await db.execute(stmt)
        users = result.scalars().all()

        emails_sent = 0
        for user in users:
            try:
                # Get user's recent crawls
                crawls_stmt = select(CrawlJob).join(Website).where(
                    Website.user_id == user.id,
                    CrawlJob.completed_at >= yesterday,
                    CrawlJob.status == "completed"
                ).order_by(CrawlJob.completed_at.desc())

                crawls_result = await db.execute(crawls_stmt)
                recent_crawls = crawls_result.scalars().all()

                # Generate digest email
                html_content = _generate_digest_email(user, recent_crawls)

                # Send email (using Celery task)
                send_email.delay(
                    to_email=user.email,
                    subject="Your Daily SEO Digest",
                    html_content=html_content
                )

                emails_sent += 1

            except Exception as e:
                logger.error(f"Error sending digest to {user.email}: {e}", exc_info=True)
                continue

        return {
            "status": "completed",
            "emails_sent": emails_sent,
            "users_processed": len(users)
        }


def _generate_digest_email(user, recent_crawls):
    """Generate HTML content for daily digest email."""
    crawls_html = ""
    for crawl in recent_crawls[:5]:  # Max 5 crawls
        crawls_html += f"""
        <div style="background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50;">
            <h4 style="margin: 0 0 10px 0;">Crawl Completed</h4>
            <p style="margin: 5px 0;"><strong>Pages:</strong> {crawl.pages_crawled}</p>
            <p style="margin: 5px 0;"><strong>Completed:</strong> {crawl.completed_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
        </div>
        """

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">Your Daily SEO Digest</h2>

            <p>Hi {user.name or 'there'},</p>

            <p>Here's a summary of your SEO activity in the last 24 hours:</p>

            <h3>Recent Crawls ({len(recent_crawls)})</h3>
            {crawls_html}

            <div style="text-align: center; margin: 30px 0;">
                <a href="https://devseo.io/dashboard"
                   style="background-color: #4CAF50; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    View Dashboard
                </a>
            </div>

            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                To unsubscribe from daily digests, visit your
                <a href="https://devseo.io/settings/notifications">notification settings</a>.
            </p>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

            <p style="color: #999; font-size: 12px; text-align: center;">
                DevSEO - AI-Powered SEO Analysis Platform<br>
                <a href="https://devseo.io" style="color: #999;">devseo.io</a>
            </p>
        </div>
    </body>
    </html>
    """
