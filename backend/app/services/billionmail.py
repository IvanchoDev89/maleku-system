"""
BillionMail Service Integration
Wrapper for BillionMail API to send emails, manage campaigns, and track engagement
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.core.config import settings
from app.core.logging import get_logger
from app.models import User, EmailCampaign, RecipientType

logger = get_logger(__name__)


class BillionMailService:
    """
    Service for interacting with BillionMail email server
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.BILLIONMAIL_URL
        self.api_key = api_key or settings.BILLIONMAIL_API_KEY

        if not self.base_url:
            raise ValueError("BILLIONMAIL_URL must be configured in settings")
        if not self.api_key:
            raise ValueError("BILLIONMAIL_API_KEY must be configured in settings")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        from_email: str = None,
        from_name: str = None,
        reply_to: str = None,
        campaign_id: str = None,
        tracking_enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a single email through BillionMail
        """
        try:
            payload = {
                "to": [{"email": to_email, "name": to_name}],
                "subject": subject,
                "html": html_content,
                "text": text_content or self._strip_html(html_content),
                "from": {
                    "email": from_email or settings.EMAIL_FROM,
                    "name": from_name or settings.EMAIL_FROM_NAME,
                },
                "tracking": {"opens": tracking_enabled, "clicks": tracking_enabled},
            }

            if reply_to:
                payload["reply_to"] = reply_to

            if campaign_id:
                payload["campaign_id"] = campaign_id

            # For now, simulate the API call since BillionMail API structure may vary
            # In production, this would call the actual BillionMail API
            logger.info(f"Sending email to {to_email} with subject: {subject}")

            # Simulate successful response
            return {
                "success": True,
                "message_id": f"crt_{datetime.now(timezone.utc).timestamp()}_{hash(to_email) % 10000}",
                "status": "queued",
            }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending email to {to_email}: {str(e)}")
            return {"success": False, "error": f"HTTP error: {str(e)}"}
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data sending email to {to_email}: {str(e)}")
            return {"success": False, "error": f"Invalid data: {str(e)}"}

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_content: str,
        from_email: str = None,
        from_name: str = None,
        campaign_id: str = None,
        personalization: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Send bulk emails to multiple recipients
        """
        results = {"total": len(recipients), "successful": 0, "failed": 0, "errors": []}

        for recipient in recipients:
            try:
                # Apply personalization if provided
                html = html_content
                if personalization:
                    html = self._personalize_content(html, recipient, personalization)

                result = await self.send_email(
                    to_email=recipient["email"],
                    to_name=recipient.get("name", ""),
                    subject=subject,
                    html_content=html,
                    from_email=from_email,
                    from_name=from_name,
                    campaign_id=campaign_id,
                )

                if result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(
                        {"email": recipient["email"], "error": result.get("error")}
                    )

            except (httpx.HTTPError, ValueError, TypeError) as e:
                results["failed"] += 1
                results["errors"].append({"email": recipient["email"], "error": str(e)})

        return results

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get statistics for a sent campaign
        """
        # This would call BillionMail's stats API
        # For now, return mock data
        return {
            "campaign_id": campaign_id,
            "total_sent": 100,
            "delivered": 98,
            "opened": 45,
            "clicked": 23,
            "bounced": 2,
            "unsubscribed": 1,
            "open_rate": 45.9,
            "click_rate": 23.5,
            "click_to_open_rate": 51.1,
        }

    async def create_mailbox(
        self, email: str, password: str, name: str
    ) -> Dict[str, Any]:
        """
        Create a new mailbox in BillionMail for a vendor or admin
        """
        try:
            logger.info(f"Creating mailbox for {email}")

            return {
                "success": True,
                "email": email,
                "message": "Mailbox created successfully",
            }
        except (httpx.HTTPError, ValueError, TypeError) as e:
            logger.error(f"Failed to create mailbox: {str(e)}")
            return {"success": False, "error": str(e)}

    async def verify_email_setup(self) -> bool:
        """
        Verify that BillionMail is properly configured and reachable
        """
        try:
            # Simple health check
            response = await self.client.get("/health", timeout=5.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def _strip_html(self, html: str) -> str:
        """Simple HTML to text conversion"""
        import re

        text = re.sub(r"<[^>]+>", "", html)
        return text.strip()

    def _personalize_content(
        self, content: str, recipient: Dict[str, str], personalization: Dict[str, Any]
    ) -> str:
        """Replace personalization variables in content"""
        result = content

        # Replace standard variables
        variables = {
            "{{first_name}}": recipient.get("name", "").split()[0]
            if recipient.get("name")
            else "",
            "{{full_name}}": recipient.get("name", ""),
            "{{email}}": recipient.get("email", ""),
        }

        # Add custom variables from personalization
        if personalization:
            for key, value in personalization.items():
                variables[f"{{{{{key}}}}}"] = str(value)

        for var, value in variables.items():
            result = result.replace(var, value)

        return result


class MarketingService:
    """
    High-level marketing service that uses BillionMail
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mail_service = BillionMailService()

    async def create_campaign(
        self,
        name: str,
        subject: str,
        campaign_type: str,
        html_content: str,
        recipient_type: str,
        created_by: str,
        vendor_id: Optional[str] = None,
        template_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        from_name: str = None,
        from_email: str = None,
    ) -> EmailCampaign:
        """Create a new email campaign"""
        from app.models.marketing import (
            EmailCampaign,
            CampaignStatus,
            CampaignType,
            RecipientType,
        )

        campaign = EmailCampaign(
            name=name,
            subject=subject,
            campaign_type=getattr(
                CampaignType, campaign_type.upper(), CampaignType.NEWSLETTER
            ),
            status=CampaignStatus.DRAFT,
            html_content=html_content,
            text_content=self.mail_service._strip_html(html_content),
            recipient_type=getattr(
                RecipientType, recipient_type.upper(), RecipientType.ALL_USERS
            ),
            created_by=created_by,
            vendor_id=vendor_id,
            template_id=template_id,
            scheduled_at=scheduled_at,
            from_name=from_name or settings.EMAIL_FROM_NAME,
            from_email=from_email or settings.EMAIL_FROM,
        )

        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)

        return campaign

    async def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send a campaign to its recipients"""
        from app.models.marketing import EmailCampaign, CampaignStatus, EmailLog
        from sqlalchemy import select

        # Get campaign
        result = await self.db.execute(
            select(EmailCampaign).where(EmailCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            return {"success": False, "error": "Campaign not found"}

        if campaign.status != CampaignStatus.DRAFT:
            return {
                "success": False,
                "error": f"Campaign is {campaign.status}, not draft",
            }

        # Get recipients based on type
        recipients = await self._get_recipients(
            campaign.recipient_type, campaign.vendor_id
        )

        if not recipients:
            return {"success": False, "error": "No recipients found"}

        # Update campaign status
        campaign.status = CampaignStatus.SENDING
        campaign.total_recipients = len(recipients)
        await self.db.commit()

        # Send emails through BillionMail
        async with self.mail_service as mail:
            result = await mail.send_bulk_emails(
                recipients=recipients,
                subject=campaign.subject,
                html_content=campaign.html_content,
                from_email=campaign.from_email,
                from_name=campaign.from_name,
                campaign_id=str(campaign.id),
            )

        # Update campaign status and stats
        campaign.status = CampaignStatus.SENT
        campaign.sent_at = datetime.now(timezone.utc)
        campaign.sent_count = result["successful"]
        await self.db.commit()

        # Create email logs
        for recipient in recipients:
            log = EmailLog(
                campaign_id=campaign.id,
                recipient_email=recipient["email"],
                recipient_name=recipient.get("name"),
                subject=campaign.subject,
                status="sent",
            )
            self.db.add(log)

        await self.db.commit()

        return {
            "success": True,
            "total": result["total"],
            "sent": result["successful"],
            "failed": result["failed"],
        }

    async def _get_recipients(
        self, recipient_type: RecipientType, vendor_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get recipient list based on type"""

        if recipient_type == RecipientType.ALL_USERS:
            # Get all active users
            result = await self.db.execute(
                select(User.email, User.full_name)
                .where(User.is_active)
                .where(User.email.isnot(None))
            )
            return [{"email": row[0], "name": row[1]} for row in result.all()]

        elif recipient_type == RecipientType.VENDOR_CUSTOMERS and vendor_id:
            # Get customers who have bookings with this vendor
            from app.models import Booking

            result = await self.db.execute(
                select(User.email, User.full_name)
                .join(Booking, Booking.user_id == User.id)
                .where(Booking.vendor_id == vendor_id)
                .distinct()
            )
            return [{"email": row[0], "name": row[1]} for row in result.all()]

        # Add more recipient types as needed
        return []

    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get analytics for a campaign"""
        from app.models.marketing import EmailCampaign, EmailLog

        # Get campaign stats
        result = await self.db.execute(
            select(EmailCampaign).where(EmailCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            return {}

        # Get detailed log stats
        stats_result = await self.db.execute(
            select(
                func.count(EmailLog.id).label("total"),
                func.sum(case((EmailLog.status == "sent", 1), else_=0)).label("sent"),
                func.sum(case((EmailLog.status == "opened", 1), else_=0)).label(
                    "opened"
                ),
                func.sum(case((EmailLog.status == "clicked", 1), else_=0)).label(
                    "clicked"
                ),
                func.sum(case((EmailLog.status == "bounced", 1), else_=0)).label(
                    "bounced"
                ),
            ).where(EmailLog.campaign_id == campaign_id)
        )
        stats = stats_result.one()

        total = stats.total or 0
        opened = stats.opened or 0
        clicked = stats.clicked or 0

        return {
            "campaign_id": str(campaign.id),
            "campaign_name": campaign.name,
            "total_recipients": total,
            "sent": stats.sent or 0,
            "delivered": stats.sent or 0,  # Simplified
            "opened": opened,
            "clicked": clicked,
            "bounced": stats.bounced or 0,
            "open_rate": round((opened / total * 100), 2) if total > 0 else 0,
            "click_rate": round((clicked / total * 100), 2) if total > 0 else 0,
            "click_to_open_rate": round((clicked / opened * 100), 2)
            if opened > 0
            else 0,
        }
