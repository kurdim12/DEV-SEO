"""
Real-Time Webhook Alert System
COMPETITIVE EDGE: Alert teams the moment regressions are detected.

Market reality:
- ContentKing charges $139/mo for this
- Nobody else has real-time monitoring
- We do it better and cheaper
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import json
import logging
from enum import Enum
from app.models import Website, Crawl
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"  # Immediate action required
    WARNING = "warning"    # Should fix soon
    INFO = "info"          # Nice to know


class AlertChannel(str, Enum):
    """Supported alert channels."""
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    WEBHOOK = "webhook"  # Generic webhook
    EMAIL = "email"


class WebhookAlertService:
    """
    Send real-time alerts when regressions are detected.

    Competitive advantage:
    - Catch issues BEFORE Google re-crawls
    - Alert within minutes of deploy
    - Route to team's existing tools (Slack, Jira, etc)
    """

    def __init__(self, db: Session):
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def send_regression_alert(
        self,
        website_id: str,
        crawl_id: str,
        root_causes: List[Dict[str, Any]],
        severity: AlertSeverity,
        channels: Optional[List[AlertChannel]] = None
    ) -> Dict[str, Any]:
        """
        Send alert about detected regressions.

        Returns:
            Dict with send status for each channel
        """
        website = self.db.query(Website).filter(Website.id == website_id).first()
        crawl = self.db.query(Crawl).filter(Crawl.id == crawl_id).first()

        if not website or not crawl:
            raise ValueError("Website or crawl not found")

        # Default to all configured channels if not specified
        if not channels:
            channels = self._get_configured_channels(website_id)

        results = {}

        for channel in channels:
            try:
                if channel == AlertChannel.SLACK:
                    results['slack'] = await self._send_slack_alert(website, crawl, root_causes, severity)
                elif channel == AlertChannel.DISCORD:
                    results['discord'] = await self._send_discord_alert(website, crawl, root_causes, severity)
                elif channel == AlertChannel.TEAMS:
                    results['teams'] = await self._send_teams_alert(website, crawl, root_causes, severity)
                elif channel == AlertChannel.WEBHOOK:
                    results['webhook'] = await self._send_generic_webhook(website, crawl, root_causes, severity)
                elif channel == AlertChannel.EMAIL:
                    results['email'] = await self._send_email_alert(website, crawl, root_causes, severity)

            except Exception as e:
                logger.error(f"Failed to send {channel} alert: {str(e)}")
                results[channel.value] = {"success": False, "error": str(e)}

        return results

    async def _send_slack_alert(
        self,
        website: Website,
        crawl: Crawl,
        root_causes: List[Dict],
        severity: AlertSeverity
    ) -> Dict:
        """
        Send formatted Slack message.

        Slack webhook format: https://api.slack.com/messaging/webhooks
        """
        # Get Slack webhook URL from website settings (would be stored in DB)
        webhook_url = self._get_webhook_url(website.id, AlertChannel.SLACK)
        if not webhook_url:
            return {"success": False, "error": "No Slack webhook configured"}

        # Emoji based on severity
        emoji_map = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.INFO: "ℹ️",
        }
        emoji = emoji_map.get(severity, "📊")

        # Color coding
        color_map = {
            AlertSeverity.CRITICAL: "#FF0000",
            AlertSeverity.WARNING: "#FFA500",
            AlertSeverity.INFO: "#0000FF",
        }
        color = color_map.get(severity, "#808080")

        # Build Slack blocks (richer formatting)
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} SEO Regression Detected: {website.domain}",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.value.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Detected:*\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Scan ID:*\n`{crawl.id[:8]}...`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Issues Found:*\n{len(root_causes)} problems"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        # Add top 3 root causes
        for i, rc in enumerate(root_causes[:3], 1):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{i}. {rc['title']}*\n"
                        f"_{rc['simple_explanation']}_\n"
                        f"• Metric: {rc['metric']}\n"
                        f"• Impact: {rc.get('business_impact', 'Performance degraded')}"
                    )
                }
            })

        # Add action button
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Report"
                    },
                    "url": f"https://app.devseo.com/reports/{crawl.id}",
                    "style": "primary" if severity == AlertSeverity.CRITICAL else "default"
                }
            ]
        })

        payload = {
            "text": f"{emoji} SEO Regression on {website.domain}",  # Fallback text
            "blocks": blocks,
            "attachments": [{
                "color": color,
                "footer": "DevSEO Real-Time Monitoring",
                "footer_icon": "https://app.devseo.com/icon.png",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }

        try:
            response = await self.http_client.post(webhook_url, json=payload)
            response.raise_for_status()
            return {"success": True, "channel": "slack"}
        except httpx.HTTPError as e:
            logger.error(f"Slack webhook failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _send_discord_alert(
        self,
        website: Website,
        crawl: Crawl,
        root_causes: List[Dict],
        severity: AlertSeverity
    ) -> Dict:
        """
        Send formatted Discord message.

        Discord webhook format: https://discord.com/developers/docs/resources/webhook
        """
        webhook_url = self._get_webhook_url(website.id, AlertChannel.DISCORD)
        if not webhook_url:
            return {"success": False, "error": "No Discord webhook configured"}

        # Color coding for embed
        color_map = {
            AlertSeverity.CRITICAL: 0xFF0000,  # Red
            AlertSeverity.WARNING: 0xFFA500,   # Orange
            AlertSeverity.INFO: 0x0000FF,      # Blue
        }
        color = color_map.get(severity, 0x808080)

        # Build embed fields
        fields = []
        for i, rc in enumerate(root_causes[:3], 1):
            fields.append({
                "name": f"{i}. {rc['title']}",
                "value": (
                    f"**Impact:** {rc.get('business_impact', 'Performance degraded')}\n"
                    f"**Fix:** {rc['how_to_fix']['immediate'][0][:100]}..."
                ),
                "inline": False
            })

        payload = {
            "content": f"🚨 SEO Regression Alert",
            "embeds": [{
                "title": f"Regression Detected: {website.domain}",
                "description": f"**{len(root_causes)} issues** detected in latest scan",
                "color": color,
                "fields": fields,
                "footer": {
                    "text": "DevSEO Real-Time Monitoring"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "url": f"https://app.devseo.com/reports/{crawl.id}"
            }]
        }

        try:
            response = await self.http_client.post(webhook_url, json=payload)
            response.raise_for_status()
            return {"success": True, "channel": "discord"}
        except httpx.HTTPError as e:
            logger.error(f"Discord webhook failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _send_teams_alert(
        self,
        website: Website,
        crawl: Crawl,
        root_causes: List[Dict],
        severity: AlertSeverity
    ) -> Dict:
        """
        Send Microsoft Teams adaptive card.

        Teams webhook format: https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors
        """
        webhook_url = self._get_webhook_url(website.id, AlertChannel.TEAMS)
        if not webhook_url:
            return {"success": False, "error": "No Teams webhook configured"}

        # Theme color
        theme_color_map = {
            AlertSeverity.CRITICAL: "FF0000",
            AlertSeverity.WARNING: "FFA500",
            AlertSeverity.INFO: "0000FF",
        }
        theme_color = theme_color_map.get(severity, "808080")

        # Build facts
        facts = [
            {"name": "Severity", "value": severity.value.upper()},
            {"name": "Website", "value": website.domain},
            {"name": "Issues Found", "value": str(len(root_causes))},
            {"name": "Scan Time", "value": crawl.started_at.strftime('%Y-%m-%d %H:%M UTC')},
        ]

        # Build sections for root causes
        sections = []
        for i, rc in enumerate(root_causes[:3], 1):
            sections.append({
                "activityTitle": f"{i}. {rc['title']}",
                "activitySubtitle": rc['simple_explanation'],
                "facts": [
                    {"name": "Metric", "value": rc['metric']},
                    {"name": "Severity", "value": rc['severity']},
                ]
            })

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"SEO Regression: {website.domain}",
            "themeColor": theme_color,
            "title": f"🚨 SEO Regression Detected",
            "sections": [{
                "activityTitle": f"Regression on {website.domain}",
                "facts": facts
            }] + sections,
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "View Full Report",
                "targets": [{
                    "os": "default",
                    "uri": f"https://app.devseo.com/reports/{crawl.id}"
                }]
            }]
        }

        try:
            response = await self.http_client.post(webhook_url, json=payload)
            response.raise_for_status()
            return {"success": True, "channel": "teams"}
        except httpx.HTTPError as e:
            logger.error(f"Teams webhook failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _send_generic_webhook(
        self,
        website: Website,
        crawl: Crawl,
        root_causes: List[Dict],
        severity: AlertSeverity
    ) -> Dict:
        """
        Send generic JSON webhook (for custom integrations, Zapier, etc).
        """
        webhook_url = self._get_webhook_url(website.id, AlertChannel.WEBHOOK)
        if not webhook_url:
            return {"success": False, "error": "No webhook configured"}

        payload = {
            "event": "seo_regression_detected",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity.value,
            "website": {
                "id": website.id,
                "domain": website.domain,
                "url": website.url,
            },
            "crawl": {
                "id": crawl.id,
                "started_at": crawl.started_at.isoformat(),
                "status": crawl.status,
                "seo_score": crawl.seo_score,
                "performance_score": crawl.performance_score,
            },
            "root_causes": root_causes,
            "report_url": f"https://app.devseo.com/reports/{crawl.id}",
        }

        try:
            response = await self.http_client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return {"success": True, "channel": "webhook"}
        except httpx.HTTPError as e:
            logger.error(f"Generic webhook failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _send_email_alert(
        self,
        website: Website,
        crawl: Crawl,
        root_causes: List[Dict],
        severity: AlertSeverity
    ) -> Dict:
        """
        Send email alert via SendGrid/email service.
        """
        # Would integrate with email_service.py
        # For now, returning placeholder
        return {"success": False, "error": "Email alerts not yet configured"}

    def _get_webhook_url(self, website_id: str, channel: AlertChannel) -> Optional[str]:
        """
        Get webhook URL for a specific channel from website settings.

        In production, these would be stored in a website_webhooks table.
        For now, returning None (would need to add to database schema).
        """
        # Placeholder - would query database:
        # webhook = db.query(WebsiteWebhook).filter(
        #     WebsiteWebhook.website_id == website_id,
        #     WebsiteWebhook.channel == channel,
        #     WebsiteWebhook.enabled == True
        # ).first()
        # return webhook.url if webhook else None
        return None

    def _get_configured_channels(self, website_id: str) -> List[AlertChannel]:
        """Get all configured alert channels for a website."""
        # Placeholder - would query database
        return []

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Celery task for sending alerts asynchronously
async def send_alert_async(
    db: Session,
    website_id: str,
    crawl_id: str,
    root_causes: List[Dict],
    severity: str,
    channels: Optional[List[str]] = None
):
    """
    Celery task wrapper for sending alerts.

    Usage in worker:
        from app.tasks import send_alert_task
        send_alert_task.delay(website_id, crawl_id, root_causes, "critical")
    """
    service = WebhookAlertService(db)

    try:
        # Convert string severity to enum
        severity_enum = AlertSeverity(severity)

        # Convert string channels to enums
        channel_enums = None
        if channels:
            channel_enums = [AlertChannel(ch) for ch in channels]

        results = await service.send_regression_alert(
            website_id=website_id,
            crawl_id=crawl_id,
            root_causes=root_causes,
            severity=severity_enum,
            channels=channel_enums
        )

        return results
    finally:
        await service.close()
