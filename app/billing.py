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

from app.models import Company, Job, StripeEvent

load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")  # Legacy subscription price
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_SURVEY_PRICE_PENCE = 999  # £9.99 per survey

logger = logging.getLogger(__name__)


# ============================================================================
# STRIPE CONNECT - For removal companies to receive deposits directly
# ============================================================================

def create_connect_account(company: Company, db: Session) -> dict:
    """
    Create a Stripe Connect Express account for a removal company.
    This allows them to receive deposit payments directly.
    """
    try:
        account = stripe.Account.create(
            type="express",
            country="GB",
            email=company.email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="company",
            metadata={
                "company_id": str(company.id),
                "slug": company.slug
            }
        )

        company.stripe_connect_account_id = account.id
        db.commit()

        logger.info(f"Created Stripe Connect account for {company.slug}: {account.id}")
        return {"account_id": account.id}

    except stripe.error.StripeError as e:
        logger.error(f"Error creating Connect account: {str(e)}")
        raise Exception(f"Failed to create payment account: {str(e)}")


def create_connect_onboarding_link(company: Company, return_url: str, refresh_url: str) -> dict:
    """
    Create an onboarding link for the company to complete Stripe Connect setup.
    """
    if not company.stripe_connect_account_id:
        raise Exception("No Stripe Connect account found")

    try:
        link = stripe.AccountLink.create(
            account=company.stripe_connect_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        logger.info(f"Created Connect onboarding link for {company.slug}")
        return {"url": link.url}

    except stripe.error.StripeError as e:
        logger.error(f"Error creating onboarding link: {str(e)}")
        raise Exception(f"Failed to create onboarding link: {str(e)}")


def check_connect_account_status(company: Company, db: Session) -> dict:
    """
    Check if a company's Stripe Connect account is fully set up.
    """
    if not company.stripe_connect_account_id:
        return {"connected": False, "status": "not_started"}

    try:
        account = stripe.Account.retrieve(company.stripe_connect_account_id)

        # Check if onboarding is complete
        charges_enabled = account.charges_enabled
        payouts_enabled = account.payouts_enabled

        if charges_enabled and payouts_enabled:
            if not company.stripe_connect_onboarding_complete:
                company.stripe_connect_onboarding_complete = True
                db.commit()
            return {
                "connected": True,
                "status": "active",
                "charges_enabled": True,
                "payouts_enabled": True
            }
        else:
            return {
                "connected": True,
                "status": "pending",
                "charges_enabled": charges_enabled,
                "payouts_enabled": payouts_enabled,
                "requirements": account.requirements.currently_due if account.requirements else []
            }

    except stripe.error.StripeError as e:
        logger.error(f"Error checking Connect account: {str(e)}")
        return {"connected": False, "status": "error", "error": str(e)}


def create_deposit_payment_intent(
    company: Company,
    amount_pence: int,
    job_token: str,
    customer_email: str,
    customer_name: str
) -> dict:
    """
    Create a payment intent for a deposit that goes directly to the removal company.
    Uses Stripe Connect to send funds directly to their account.
    """
    if not company.stripe_connect_account_id:
        raise Exception("Company has not connected their Stripe account")

    if not company.stripe_connect_onboarding_complete:
        raise Exception("Company has not completed Stripe setup")

    try:
        # Create payment intent with direct transfer to company
        intent = stripe.PaymentIntent.create(
            amount=amount_pence,
            currency="gbp",
            transfer_data={
                "destination": company.stripe_connect_account_id,
            },
            metadata={
                "job_token": job_token,
                "company_id": str(company.id),
                "type": "deposit"
            },
            receipt_email=customer_email,
            description=f"Moving deposit - {company.company_name}",
        )

        logger.info(f"Created deposit payment intent for job {job_token}: {intent.id}")
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Error creating deposit payment: {str(e)}")
        raise Exception(f"Failed to create payment: {str(e)}")


# ============================================================================
# PREPAID CREDITS SYSTEM - Companies buy credits upfront
# ============================================================================

# Credit pack pricing (in pence)
CREDIT_PACKS = {
    "starter": {"credits": 10, "price_pence": 9900, "price_display": "£99", "per_survey": "£9.90"},
    "growth": {"credits": 25, "price_pence": 22500, "price_display": "£225", "per_survey": "£9.00"},
    "pro": {"credits": 50, "price_pence": 39900, "price_display": "£399", "per_survey": "£7.98"},
    "enterprise": {"credits": 100, "price_pence": 69900, "price_display": "£699", "per_survey": "£6.99"},
}


def use_survey_credit(company: Company, job_token: str, db: Session) -> dict:
    """
    Use one credit for a survey submission.
    Partners have unlimited credits.
    Returns success if credit used, or error if no credits.
    """
    # Partners have unlimited credits
    if getattr(company, 'is_partner', False):
        company.surveys_used = (company.surveys_used or 0) + 1
        db.commit()
        partner_name = getattr(company, 'partner_name', None)
        logger.info(f"Partner survey (unlimited) by {company.slug} ({partner_name})")
        return {
            "success": True,
            "reason": "partner_account",
            "partner_name": partner_name,
            "credits_remaining": "unlimited"
        }

    # Check if company has credits
    credits = getattr(company, 'credits', 0) or 0

    if credits <= 0:
        logger.warning(f"No credits for {company.slug} - survey blocked")
        return {
            "success": False,
            "reason": "no_credits",
            "error": "You've run out of survey credits. Please purchase more to continue."
        }

    # Use one credit
    company.credits = credits - 1
    company.surveys_used = (company.surveys_used or 0) + 1
    db.commit()

    logger.info(f"Credit used by {company.slug}. {company.credits} remaining.")
    return {
        "success": True,
        "reason": "credit_used",
        "credits_remaining": company.credits
    }


def get_company_credits(company: Company) -> dict:
    """
    Get credit balance for a company.
    """
    is_partner = getattr(company, 'is_partner', False)
    credits = getattr(company, 'credits', 0) or 0

    return {
        "credits": credits if not is_partner else "unlimited",
        "is_partner": is_partner,
        "surveys_used": company.surveys_used or 0,
        "low_credits": credits <= 2 and not is_partner,
        "packs": CREDIT_PACKS
    }


def create_credit_purchase_session(
    company: Company,
    pack_id: str,
    success_url: str,
    cancel_url: str,
    db: Session
) -> dict:
    """
    Create a Stripe Checkout session to purchase credits.
    """
    if pack_id not in CREDIT_PACKS:
        raise Exception(f"Invalid pack: {pack_id}")

    pack = CREDIT_PACKS[pack_id]

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

        # Create checkout session for credit purchase
        session = stripe.checkout.Session.create(
            customer=company.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": pack["price_pence"],
                    "product_data": {
                        "name": f"PrimeHaul Survey Credits ({pack['credits']} pack)",
                        "description": f"{pack['credits']} survey credits at {pack['per_survey']} each",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "company_id": str(company.id),
                "slug": company.slug,
                "pack_id": pack_id,
                "credits": pack["credits"],
                "type": "credit_purchase"
            }
        )

        logger.info(f"Created credit purchase session for {company.slug}: {pack_id} ({pack['credits']} credits)")

        return {
            "url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating credit purchase session: {str(e)}")
        raise Exception(f"Failed to create checkout: {str(e)}")


def add_credits_to_company(company: Company, credits: int, db: Session) -> dict:
    """
    Add credits to a company's balance (called after successful payment).
    """
    old_balance = getattr(company, 'credits', 0) or 0
    company.credits = old_balance + credits
    db.commit()

    logger.info(f"Added {credits} credits to {company.slug}. New balance: {company.credits}")

    return {
        "added": credits,
        "old_balance": old_balance,
        "new_balance": company.credits
    }


# Legacy function for backwards compatibility
def charge_survey_fee(company: Company, job_token: str, db: Session) -> dict:
    """Legacy wrapper - now uses credit system"""
    result = use_survey_credit(company, job_token, db)
    # Convert to old format for backwards compatibility
    return {
        "charged": False,  # Credits are prepaid, not charged per survey
        "reason": result.get("reason"),
        "credits_remaining": result.get("credits_remaining"),
        "success": result.get("success", False),
        "error": result.get("error")
    }


def get_company_usage(company: Company) -> dict:
    """
    Get usage statistics for a company's billing dashboard.
    """
    credits_info = get_company_credits(company)
    return {
        "credits": credits_info["credits"],
        "surveys_used": credits_info["surveys_used"],
        "is_partner": credits_info["is_partner"],
        "low_credits": credits_info["low_credits"],
        "packs": CREDIT_PACKS
    }


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


def handle_checkout_completed(event_data: dict, db: Session):
    """
    Handle checkout.session.completed event - for credit purchases and deposit payments
    """
    session = event_data["object"]
    metadata = session.get("metadata", {})
    checkout_type = metadata.get("type")

    if checkout_type == "deposit":
        _handle_deposit_checkout(session, metadata, db)
    elif checkout_type == "credit_purchase":
        _handle_credit_purchase_checkout(metadata, db)


def _handle_deposit_checkout(session: dict, metadata: dict, db: Session):
    """Mark job as deposit_paid when Stripe checkout completes"""
    job_token = metadata.get("job_token")
    if not job_token:
        logger.error(f"Deposit checkout missing job_token: {metadata}")
        return

    job = db.query(Job).filter(Job.token == job_token).first()
    if not job:
        logger.error(f"Job not found for deposit checkout: {job_token}")
        return

    if job.status == "deposit_paid":
        logger.info(f"Job {job_token} already marked deposit_paid, skipping")
        return

    job.status = "deposit_paid"
    job.deposit_paid_at = datetime.utcnow()
    db.commit()

    amount = session.get("amount_total", 0) / 100
    logger.info(f"Deposit paid for job {job_token}: £{amount:.2f}")


def _handle_credit_purchase_checkout(metadata: dict, db: Session):
    """Process credit purchase from checkout"""
    company_id = metadata.get("company_id")
    credits_to_add = int(metadata.get("credits", 0))
    pack_id = metadata.get("pack_id")

    if not company_id or not credits_to_add:
        logger.error(f"Missing data in credit purchase: {metadata}")
        return

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        logger.error(f"Company not found for credit purchase: {company_id}")
        return

    # Add credits
    result = add_credits_to_company(company, credits_to_add, db)
    logger.info(f"Credit purchase complete for {company.slug}: +{credits_to_add} credits ({pack_id}). Balance: {result['new_balance']}")


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
            "checkout.session.completed": handle_checkout_completed,
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
