"""
Email Service - Gestiona envío de emails transaccionales.

Tres modos (en orden de prioridad):
1. **Resend** - si ``RESEND_API_KEY`` está configurada (producción)
2. **SMTP** - si ``USE_SMTP_IN_DEV=true`` y ``SMTP_HOST`` apunta a algo
   alcanzable (MailHog local, Mailtrap, SES, etc.)
3. **Simulated** - log a consola con el payload completo (sin servicio externo)
"""
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any
import resend
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailError(Exception):
    """Custom email error"""
    pass


class EmailService:
    """Service for sending transactional emails via Resend / SMTP / log."""

    # Brand configuration - centralized
    BRAND = {
        "name": "Costa Rica Travel",
        "primary_color": "#1e7a67",
        "secondary_color": "#2a9d8f",
        "website_url": "https://costaricatravel.dev",
        "vendor_dashboard": "https://costaricatravel.dev/vendor/dashboard",
        "support_email": "info@costaricatravel.dev",
        "tagline": "Descubre Costa Rica: hoteles, tours y experiencias únicas",
        "signature": "The Costa Rica Travel Team",
    }

    def __init__(self):
        self.resend_configured = False
        self.smtp_configured = False
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME

        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY
            self.resend_configured = True
        elif getattr(settings, "USE_SMTP_IN_DEV", False) and getattr(settings, "SMTP_HOST", None):
            self.smtp_configured = True

    @property
    def configured(self) -> bool:
        """True if at least one transport is configured (Resend or SMTP)."""
        return self.resend_configured or self.smtp_configured

    def _build_email_template(self, title: str, content: str, show_signature: bool = True) -> str:
        """Build consistent email template with brand styling."""
        signature_html = f"""
                <p>Pura Vida!<br>{self.BRAND['signature']}</p>
        """ if show_signature else ""

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: {self.BRAND['primary_color']};">{title}</h1>

                {content}

                {signature_html}

                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """

    def _build_details_box(self, title: str, items: List[tuple]) -> str:
        """Build a consistent details box for emails."""
        items_html = "\n".join([
            f"<p><strong>{label}:</strong> {value}</p>" for label, value in items
        ])

        return f"""
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">{title}</h3>
                    {items_html}
                </div>
        """

    def _validate_email(self, email: str) -> bool:
        """Validate email format to prevent header injection."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and '\n' not in email and '\r' not in email

    def _sanitize_for_log(self, value: str) -> str:
        """Sanitize string for safe logging."""
        return value.replace('\n', ' ').replace('\r', ' ')[:100]

    async def _send_smtp(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send via SMTP (MailHog, Mailtrap, SES, etc.)."""
        smtp_host = settings.SMTP_HOST
        smtp_port = int(getattr(settings, "SMTP_PORT", 1025))
        use_tls = bool(getattr(settings, "SMTP_USE_TLS", False))
        smtp_user = getattr(settings, "SMTP_USER", None)
        smtp_password = getattr(settings, "SMTP_PASSWORD", None)

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to
        msg["Subject"] = subject
        if text:
            msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        def _do_send() -> str:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
                if use_tls:
                    smtp.starttls()
                if smtp_user and smtp_password:
                    smtp.login(smtp_user, smtp_password)
                smtp.sendmail(self.from_email, [to], msg.as_string())
                return msg.as_string().split("Date:")[-1][:50]  # pseudo-id

        try:
            await asyncio.to_thread(_do_send)
            logger.info(f"[EMAIL via SMTP] To: {to}, Subject: {self._sanitize_for_log(subject)}")
            return {"id": f"smtp-{int(asyncio.get_event_loop().time())}", "status": "sent"}
        except (OSError, smtplib.SMTPException) as e:
            logger.error(f"Failed SMTP send to {to}: {e}")
            raise EmailError(f"SMTP send failed: {e}") from e

    async def _send_resend(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Send via Resend API."""
        params = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": to,
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text
        if reply_to:
            params["reply_to"] = reply_to
        if attachments:
            params["attachments"] = attachments

        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"[EMAIL via Resend] To: {to}, ID: {email.get('id')}")
        return {"id": email.get("id"), "status": "sent"}

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email. Routing:
        - Resend if ``RESEND_API_KEY`` is set
        - SMTP if ``USE_SMTP_IN_DEV=true`` and ``SMTP_HOST`` is reachable
        - Otherwise log the payload and return ``status=simulated``
        """
        if not self._validate_email(to):
            raise EmailError(f"Invalid recipient email: {to}")
        if cc:
            for email in cc:
                if not self._validate_email(email):
                    raise EmailError(f"Invalid CC email: {email}")
        if bcc:
            for email in bcc:
                if not self._validate_email(email):
                    raise EmailError(f"Invalid BCC email: {email}")
        if reply_to and not self._validate_email(reply_to):
            raise EmailError(f"Invalid reply-to email: {reply_to}")

        if self.resend_configured:
            try:
                return await self._send_resend(to, subject, html, text, reply_to, attachments)
            except (RuntimeError, ValueError, ConnectionError) as e:
                logger.error(f"Resend send failed to {to}: {e}")
                raise EmailError(f"Email send failed: {e}") from e

        if self.smtp_configured:
            return await self._send_smtp(to, subject, html, text)

        safe_to = self._sanitize_for_log(to)
        safe_subject = self._sanitize_for_log(subject)
        logger.info(
            f"[EMAIL simulated] To: {safe_to}, Subject: {safe_subject} "
            f"(text len={len(text or '')}, html len={len(html or '')})"
        )
        return {"id": "simulated", "status": "simulated"}
    
    async def send_booking_confirmation(
        self,
        to: str,
        booking_code: str,
        property_name: str,
        check_in: str,
        check_out: str,
        total_amount: float,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Send booking confirmation email.
        """
        details = self._build_details_box("Booking Details", [
            ("Confirmation Code", booking_code),
            ("Property", property_name),
            ("Check-in", check_in),
            ("Check-out", check_out),
            ("Total", f"{currency} ${total_amount:.2f}"),
        ])
        
        content = f"""
                <p>Your booking has been confirmed!</p>
                {details}
                <p>Thank you for choosing {self.BRAND['name']}!</p>
        """
        
        html = self._build_email_template("Booking Confirmation", content)
        
        text = f"""Booking Confirmation

Your booking has been confirmed!

Booking Details:
- Confirmation Code: {booking_code}
- Property: {property_name}
- Check-in: {check_in}
- Check-out: {check_out}
- Total: {currency} ${total_amount:.2f}

Thank you for choosing {self.BRAND['name']}!"""
        
        return await self.send_email(
            to=to,
            subject=f"Booking Confirmed - {booking_code}",
            html=html,
            text=text
        )
    
    async def send_payment_receipt(
        self,
        to: str,
        booking_code: str,
        payment_amount: float,
        currency: str = "USD",
        payment_date: str = None
    ) -> Dict[str, Any]:
        """
        Send payment receipt email.
        """
        details = self._build_details_box("Payment Details", [
            ("Booking Code", booking_code),
            ("Amount Paid", f"{currency} ${payment_amount:.2f}"),
            ("Date", payment_date or "Today"),
        ])
        
        content = f"""
                <p>Thank you for your payment!</p>
                {details}
                <p>Your booking is now confirmed.</p>
        """
        
        html = self._build_email_template("Payment Receipt", content)
        
        return await self.send_email(
            to=to,
            subject=f"Payment Receipt - {booking_code}",
            html=html
        )
    
    async def send_welcome_email(
        self,
        to: str,
        full_name: str
    ) -> Dict[str, Any]:
        """
        Send welcome email to new users.
        """
        content = f"""
                <p>Hi {full_name},</p>
                
                <p>Thank you for joining {self.BRAND['name']}. We're excited to help you discover the beauty of Costa Rica.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">What's Next?</h3>
                    <ul>
                        <li>Explore our curated hotels and tours</li>
                        <li>Use our trip planner to create your perfect itinerary</li>
                        <li>Book with confidence - we verify all our vendors</li>
                    </ul>
                </div>
        """
        
        html = self._build_email_template(f"Welcome to {self.BRAND['name']}!", content)
        
        return await self.send_email(
            to=to,
            subject=f"Welcome to {self.BRAND['name']}!",
            html=html
        )
    
    async def send_vendor_welcome(
        self,
        to: str,
        business_name: str
    ) -> Dict[str, Any]:
        """
        Send welcome email to new vendors.
        """
        content = f"""
                <p>Hi {business_name},</p>
                
                <p>Thank you for registering as a vendor on {self.BRAND['name']}. We're excited to help you reach more travelers.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Next Steps</h3>
                    <ol>
                        <li>Complete your vendor profile</li>
                        <li>Add your properties or tours</li>
                        <li>Set up your Stripe Connect account for payments</li>
                        <li>Start receiving bookings!</li>
                    </ol>
                </div>
                
                <p>Questions? Reply to this email or contact our vendor support team at {self.BRAND['support_email']}.</p>
        """
        
        html = self._build_email_template(f"Welcome to {self.BRAND['name']} - Vendor Account", content)
        
        return await self.send_email(
            to=to,
            subject=f"Welcome to {self.BRAND['name']} - Vendor Account",
            html=html
        )
    
    async def send_booking_notification_to_vendor(
        self,
        to: str,
        business_name: str,
        booking_code: str,
        guest_name: str,
        check_in: str,
        check_out: str,
        total_amount: float
    ) -> Dict[str, Any]:
        """
        Notify vendor of new booking.
        """
        details = self._build_details_box("Booking Details", [
            ("Confirmation Code", booking_code),
            ("Guest", guest_name),
            ("Check-in", check_in),
            ("Check-out", check_out),
            ("Total Revenue", f"${total_amount:.2f}"),
        ])
        
        content = f"""
                <p>Hi {business_name},</p>
                
                <p>You have a new booking. Please review and confirm it in your vendor dashboard.</p>
                
                {details}
                
                <p><a href="{self.BRAND['vendor_dashboard']}" 
                      style="background: {self.BRAND['primary_color']}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                      View in Dashboard
                   </a>
                </p>
        """
        
        html = self._build_email_template("New Booking!", content, show_signature=False)
        
        return await self.send_email(
            to=to,
            subject=f"New Booking - {booking_code}",
            html=html
        )
    
    def is_configured(self) -> bool:
        """Check if email service is configured"""
        return self.configured


# Singleton instance
email_service = EmailService()
