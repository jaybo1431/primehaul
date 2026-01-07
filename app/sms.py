"""
SMS notification service using Twilio
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio number
TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"

# Initialize Twilio client (lazy loading)
_twilio_client = None


def get_twilio_client():
    """Get or create Twilio client"""
    global _twilio_client

    if not TWILIO_ENABLED:
        logger.info("Twilio SMS disabled (TWILIO_ENABLED=false)")
        return None

    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        return None

    if _twilio_client is None:
        try:
            from twilio.rest import Client
            _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            logger.info("Twilio client initialized successfully")
        except ImportError:
            logger.error("Twilio package not installed. Run: pip install twilio")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            return None

    return _twilio_client


def send_sms(to_phone: str, message: str) -> bool:
    """
    Send an SMS message via Twilio

    Args:
        to_phone: Recipient phone number (E.164 format, e.g., +447700900123)
        message: Message text (max 160 chars recommended)

    Returns:
        True if sent successfully, False otherwise
    """
    client = get_twilio_client()

    if client is None:
        logger.info(f"SMS NOT SENT (Twilio disabled): {to_phone[:6]}*** - {message[:50]}...")
        return False

    try:
        # Format phone number (ensure it has country code)
        if not to_phone.startswith('+'):
            # Assume UK number if no country code
            to_phone = '+44' + to_phone.lstrip('0')

        # Send SMS
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        logger.info(f"SMS sent successfully to {to_phone[:6]}***: SID {sms.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone}: {e}")
        return False


# ----------------------------
# Predefined notification templates
# ----------------------------

def notify_quote_approved(customer_name: str, customer_phone: str, company_name: str, price_low: int, price_high: int, booking_url: str) -> bool:
    """Send notification when quote is approved"""
    message = f"""Hi {customer_name}! ✅

Your {company_name} quote is APPROVED!

💰 Price: £{price_low:,}-£{price_high:,}

Book your move now:
{booking_url}

Reply STOP to opt out"""

    return send_sms(customer_phone, message)


def notify_quote_submitted(customer_name: str, customer_phone: str, company_name: str) -> bool:
    """Send notification when quote is submitted for review"""
    message = f"""Hi {customer_name}! 📋

Your {company_name} quote has been submitted!

Our team is reviewing it now. You'll receive a text within 2 hours with your final price.

Thanks!

Reply STOP to opt out"""

    return send_sms(customer_phone, message)


def notify_booking_confirmed(customer_name: str, customer_phone: str, company_name: str, move_date: str, time_slot: str) -> bool:
    """Send notification when booking is confirmed"""
    message = f"""Hi {customer_name}! 🎉

Your move is CONFIRMED with {company_name}!

📅 Date: {move_date}
⏰ Time: {time_slot}

We'll send a reminder 2 days before.

Reply STOP to opt out"""

    return send_sms(customer_phone, message)


def notify_quote_ready(customer_name: str, customer_phone: str, company_name: str, quote_url: str) -> bool:
    """Send notification when quote is ready to view"""
    message = f"""Hi {customer_name}! 💰

Your {company_name} quote is ready!

View your quote here:
{quote_url}

Reply STOP to opt out"""

    return send_sms(customer_phone, message)


# Test function
def test_sms(test_phone: str = None) -> bool:
    """
    Test SMS functionality

    Args:
        test_phone: Phone number to test (defaults to env var TEST_PHONE)

    Returns:
        True if test SMS sent successfully
    """
    test_phone = test_phone or os.getenv("TEST_PHONE")

    if not test_phone:
        logger.error("No test phone number provided. Set TEST_PHONE env var or pass as argument")
        return False

    message = "🧪 Test SMS from primehaul! If you received this, SMS notifications are working! Reply STOP to opt out"
    return send_sms(test_phone, message)
