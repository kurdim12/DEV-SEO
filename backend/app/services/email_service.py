"""
Email service for sending notifications using SendGrid.
"""
from typing import Optional, Dict, Any, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid."""

    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.from_email = Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME)
        else:
            self.client = None
            logger.warning("SendGrid API key not configured. Email notifications disabled.")

    def _is_enabled(self) -> bool:
        """Check if email service is properly configured."""
        return self.client is not None

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None
    ) -> bool:
        """
        Send an email via SendGrid.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_text: Plain text version (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self._is_enabled():
            logger.warning(f"Email service disabled. Would send to {to_email}: {subject}")
            return False

        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            if plain_text:
                message.plain_text_content = Content("text/plain", plain_text)

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

    async def send_scan_complete(
        self,
        to_email: str,
        website_url: str,
        score: int,
        total_pages: int,
        total_issues: int,
        report_url: str
    ) -> bool:
        """
        Send notification when a scan is complete.

        Args:
            to_email: User email
            website_url: Website that was scanned
            score: SEO score (0-100)
            total_pages: Number of pages scanned
            total_issues: Total issues found
            report_url: Link to view the full report

        Returns:
            bool: True if sent successfully
        """
        subject = f"✓ Scan Complete: {website_url} - Score {score}/100"

        # Determine score color
        if score >= 80:
            score_color = "#22c55e"  # green
            status = "Excellent"
        elif score >= 60:
            score_color = "#eab308"  # yellow
            status = "Good"
        elif score >= 40:
            score_color = "#f97316"  # orange
            status = "Needs Work"
        else:
            score_color = "#ef4444"  # red
            status = "Critical"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }}
        .score-badge {{
            background: {score_color};
            color: white;
            font-size: 48px;
            font-weight: bold;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        .score-label {{
            font-size: 14px;
            margin-top: 5px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .stat {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        .website-url {{
            color: #667eea;
            font-weight: 600;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Your SEO Scan is Complete!</h1>
    </div>

    <div class="content">
        <p>Great news! We've finished analyzing <span class="website-url">{website_url}</span></p>

        <div class="score-badge">
            {score}/100
            <div class="score-label">{status}</div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_pages}</div>
                <div class="stat-label">Pages Scanned</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_issues}</div>
                <div class="stat-label">Issues Found</div>
            </div>
            <div class="stat">
                <div class="stat-value">{score}</div>
                <div class="stat-label">SEO Score</div>
            </div>
        </div>

        <p>Your detailed SEO report is ready to view. Click the button below to see all the insights and recommendations:</p>

        <div style="text-align: center;">
            <a href="{report_url}" class="button">View Full Report →</a>
        </div>

        <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
            <strong>What's Next?</strong><br>
            Review the critical issues first, then work through the warnings. Each issue includes clear instructions on how to fix it.
        </p>
    </div>

    <div class="footer">
        <p>
            <strong>DevSEO</strong> - AI-Powered SEO Analysis<br>
            You're receiving this email because you requested a scan on DevSEO.<br>
            <a href="#" style="color: #667eea;">Manage Email Preferences</a>
        </p>
    </div>
</body>
</html>
        """

        plain_text = f"""
Scan Complete: {website_url}

Your SEO scan is complete!

Score: {score}/100 ({status})
Pages Scanned: {total_pages}
Issues Found: {total_issues}

View your full report: {report_url}

What's Next?
Review the critical issues first, then work through the warnings. Each issue includes clear instructions on how to fix it.

---
DevSEO - AI-Powered SEO Analysis
        """

        return await self.send_email(to_email, subject, html_content, plain_text)

    async def send_scan_failed(
        self,
        to_email: str,
        website_url: str,
        error_message: str
    ) -> bool:
        """
        Send notification when a scan fails.

        Args:
            to_email: User email
            website_url: Website that failed to scan
            error_message: Error description

        Returns:
            bool: True if sent successfully
        """
        subject = f"⚠️ Scan Failed: {website_url}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #ef4444;
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }}
        .error-box {{
            background: #fee;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ Scan Failed</h1>
    </div>

    <div class="content">
        <p>We encountered an issue while scanning <strong>{website_url}</strong></p>

        <div class="error-box">
            <strong>Error:</strong> {error_message}
        </div>

        <p><strong>Common Solutions:</strong></p>
        <ul>
            <li>Make sure your website is accessible and not blocking our crawler</li>
            <li>Check if your robots.txt allows crawling</li>
            <li>Verify the URL is correct and includes http:// or https://</li>
            <li>Try scanning again in a few minutes</li>
        </ul>

        <div style="text-align: center;">
            <a href="https://app.devseo.io/websites" class="button">Try Again</a>
        </div>
    </div>
</body>
</html>
        """

        plain_text = f"""
Scan Failed: {website_url}

We encountered an issue while scanning your website.

Error: {error_message}

Common Solutions:
- Make sure your website is accessible and not blocking our crawler
- Check if your robots.txt allows crawling
- Verify the URL is correct and includes http:// or https://
- Try scanning again in a few minutes

Try again: https://app.devseo.io/websites
        """

        return await self.send_email(to_email, subject, html_content, plain_text)

    async def send_issues_detected(
        self,
        to_email: str,
        website_url: str,
        new_issues: List[Dict[str, Any]],
        dashboard_url: str
    ) -> bool:
        """
        Send alert when new critical issues are detected.

        Args:
            to_email: User email
            website_url: Website with issues
            new_issues: List of new issues detected
            dashboard_url: Link to dashboard

        Returns:
            bool: True if sent successfully
        """
        subject = f"🔴 {len(new_issues)} New Issues Detected: {website_url}"

        issues_html = ""
        for issue in new_issues[:5]:  # Show max 5 issues
            issues_html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{issue.get('title', 'Unknown Issue')}</strong><br>
                <span style="color: #6b7280; font-size: 14px;">{issue.get('description', '')}</span>
            </li>
            """

        if len(new_issues) > 5:
            issues_html += f"<li><em>... and {len(new_issues) - 5} more issues</em></li>"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #ef4444;
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e5e7eb;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔴 New Issues Detected</h1>
    </div>
    <div class="content">
        <p>We found <strong>{len(new_issues)} new critical issues</strong> on <strong>{website_url}</strong></p>
        <ul>
            {issues_html}
        </ul>
        <div style="text-align: center;">
            <a href="{dashboard_url}" class="button">View All Issues</a>
        </div>
    </div>
</body>
</html>
        """

        return await self.send_email(to_email, subject, html_content)


# Global instance
email_service = EmailService()
