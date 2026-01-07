"""
Stripe billing integration for PrimeHaul OS
Handles subscription management, checkout sessions, and webhook events
"""

import os
import logging
from datetime import datetime
from typing import Optional
import stripe
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models import Company, StripeEvent

load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")  # £99/month price ID
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

logger = logging.getLogger(__name__)


def create_checkout_session(
    company: Company,
    success_url: str,
    cancel_url: str,
    db: Session
) -> dict:
    """
    Create a Stripe Checkout session for subscription

    Args:
        company: Company object
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if checkout is cancelled
        db: Database session

    Returns:
        Dict with checkout session details (url, session_id)
    """
    try:
        # Create or retrieve Stripe customer
        if not company.stripe_customer_id:
            customer = stripe.Customer.create(
                email=company.email,
                name=company.company_name,
                metadata={
                    "company_id": str(company.id),
                    "slug": company.slug
                }
            )
            company.stripe_customer_id = customer.id
            db.commit()
        else:
            customer_id = company.stripe_customer_id

        # Create checkout session with 30-day trial
        session = stripe.checkout.Session.create(
            customer=company.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": STRIPE_PRICE_ID,
                "quantity": 1,
            }],
            mode="subscription",
            subscription_data={
                "trial_period_days": 30,
                "metadata": {
                    "company_id": str(company.id),
                    "slug": company.slug
                }
            },
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "company_id": str(company.id),
                "slug": company.slug
            }
        )

        logger.info(f"Created checkout session for company {company.slug}: {session.id}")

        return {
            "url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        raise Exception(f"Failed to create checkout session: {str(e)}")


def create_customer_portal_session(
    company: Company,
    return_url: str
) -> dict:
    """
    Create a Stripe Customer Portal session for managing subscription

    Args:
        company: Company object
        return_url: URL to return to after portal session

    Returns:
        Dict with portal session URL
    """
    try:
        if not company.stripe_customer_id:
            raise Exception("No Stripe customer ID found")

        session = stripe.billing_portal.Session.create(
            customer=company.stripe_customer_id,
            return_url=return_url,
        )

        logger.info(f"Created portal session for company {company.slug}")

        return {
            "url": session.url
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal session: {str(e)}")
        raise Exception(f"Failed to create portal session: {str(e)}")


def verify_webhook_signature(payload: bytes, signature: str) -> dict:
    """
    Verify Stripe webhook signature and return event

    Args:
        payload: Raw request body
        signature: Stripe signature header

    Returns:
        Stripe event object

    Raises:
        stripe.error.SignatureVerificationError: If signature is invalid
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        raise


def handle_subscription_created(event_data: dict, db: Session):
    """
    Handle customer.subscription.created event

    Args:
        event_data: Stripe event data
        db: Database session
    """
    subscription = event_data["object"]
    company_id = subscription["metadata"].get("company_id")

    if not company_id:
        logger.error("No company_id in subscription metadata")
        return

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        logger.error(f"Company not found: {company_id}")
        return

    company.subscription_status = "active"
    company.stripe_subscription_id = subscription["id"]
    company.trial_ends_at = None  # Clear trial date
    db.commit()

    logger.info(f"Subscription created for company {company.slug}: {subscription['id']}")


def handle_subscription_updated(event_data: dict, db: Session):
    """
    Handle customer.subscription.updated event

    Args:
        event_data: Stripe event data
        db: Database session
    """
    subscription = event_data["object"]
    subscription_id = subscription["id"]

    company = db.query(Company).filter(
        Company.stripe_subscription_id == subscription_id
    ).first()

    if not company:
        logger.error(f"Company not found for subscription: {subscription_id}")
        return

    # Update status based on subscription status
    stripe_status = subscription["status"]

    status_mapping = {
        "active": "active",
        "trialing": "trial",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "past_due"
    }

    company.subscription_status = status_mapping.get(stripe_status, "inactive")
    db.commit()

    logger.info(f"Subscription updated for company {company.slug}: {stripe_status}")


def handle_subscription_deleted(event_data: dict, db: Session):
    """
    Handle customer.subscription.deleted event

    Args:
        event_data: Stripe event data
        db: Database session
    """
    subscription = event_data["object"]
    subscription_id = subscription["id"]

    company = db.query(Company).filter(
        Company.stripe_subscription_id == subscription_id
    ).first()

    if not company:
        logger.error(f"Company not found for subscription: {subscription_id}")
        return

    company.subscription_status = "canceled"
    company.subscription_canceled_at = datetime.utcnow()
    db.commit()

    logger.info(f"Subscription canceled for company {company.slug}")


def handle_invoice_paid(event_data: dict, db: Session):
    """
    Handle invoice.paid event

    Args:
        event_data: Stripe event data
        db: Database session
    """
    invoice = event_data["object"]
    customer_id = invoice["customer"]

    company = db.query(Company).filter(
        Company.stripe_customer_id == customer_id
    ).first()

    if not company:
        logger.error(f"Company not found for customer: {customer_id}")
        return

    # Ensure subscription is active
    if company.subscription_status in ["past_due", "unpaid"]:
        company.subscription_status = "active"
        db.commit()

    logger.info(f"Invoice paid for company {company.slug}: {invoice['id']}")


def handle_invoice_payment_failed(event_data: dict, db: Session):
    """
    Handle invoice.payment_failed event

    Args:
        event_data: Stripe event data
        db: Database session
    """
    invoice = event_data["object"]
    customer_id = invoice["customer"]

    company = db.query(Company).filter(
        Company.stripe_customer_id == customer_id
    ).first()

    if not company:
        logger.error(f"Company not found for customer: {customer_id}")
        return

    company.subscription_status = "past_due"
    db.commit()

    logger.warning(f"Payment failed for company {company.slug}: {invoice['id']}")
    # TODO: Send email notification about payment failure


def process_webhook_event(event: dict, db: Session) -> bool:
    """
    Process Stripe webhook event

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        True if processed successfully
    """
    event_type = event["type"]
    event_data = event["data"]

    # Log event to database
    stripe_event = StripeEvent(
        stripe_event_id=event["id"],
        event_type=event_type,
        payload=event,
        processed=False
    )
    db.add(stripe_event)
    db.commit()

    try:
        # Handle different event types
        handlers = {
            "customer.subscription.created": handle_subscription_created,
            "customer.subscription.updated": handle_subscription_updated,
            "customer.subscription.deleted": handle_subscription_deleted,
            "invoice.paid": handle_invoice_paid,
            "invoice.payment_failed": handle_invoice_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event_data, db)
            stripe_event.processed = True
            db.commit()
            logger.info(f"Processed webhook event: {event_type}")
            return True
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
            return False

    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {str(e)}")
        return False


def check_subscription_status(company: Company) -> dict:
    """
    Check current subscription status

    Args:
        company: Company object

    Returns:
        Dict with status information
    """
    now = datetime.utcnow()

    # Check trial status
    if company.subscription_status == "trial":
        if company.trial_ends_at and now > company.trial_ends_at:
            return {
                "is_active": False,
                "status": "trial_expired",
                "message": "Your 30-day trial has expired. Subscribe to continue."
            }
        return {
            "is_active": True,
            "status": "trial",
            "days_remaining": (company.trial_ends_at - now).days if company.trial_ends_at else 0
        }

    # Check active subscription
    if company.subscription_status == "active":
        return {
            "is_active": True,
            "status": "active",
            "message": "Subscription is active"
        }

    # Check past due
    if company.subscription_status == "past_due":
        return {
            "is_active": True,  # Grace period - allow access
            "status": "past_due",
            "message": "Payment failed. Please update your payment method."
        }

    # Canceled or inactive
    return {
        "is_active": False,
        "status": company.subscription_status,
        "message": "Subscription required to access PrimeHaul OS"
    }
