"""
Marketplace Core Logic - "Uber for Removals"

This module handles:
- Job broadcasting to companies
- Bid management
- Commission calculation
- Geo-location matching
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    MarketplaceJob, Bid, JobBroadcast, Commission,
    Company, PricingConfig, MarketplaceRoom, MarketplaceItem
)


def calculate_distance_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    Returns distance in miles

    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates

    Returns:
        Distance in miles (float)
    """
    # Radius of Earth in miles
    R = 3959.0

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lng1_rad = math.radians(lng1)
    lng2_rad = math.radians(lng2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    distance = R * c
    return distance


def find_companies_in_radius(
    lat: float,
    lng: float,
    radius_miles: int,
    db: Session,
    exclude_company_ids: List[str] = None
) -> List[Company]:
    """
    Find all active companies within radius of a location

    Args:
        lat, lng: Center point coordinates
        radius_miles: Search radius
        db: Database session
        exclude_company_ids: Companies to exclude (optional)

    Returns:
        List of Company objects within radius
    """
    # Get all active companies (trial or active subscription)
    query = db.query(Company).filter(
        Company.subscription_status.in_(['trial', 'active', 'past_due']),
        Company.is_active == True
    )

    if exclude_company_ids:
        query = query.filter(~Company.id.in_(exclude_company_ids))

    all_companies = query.all()

    # Filter by distance (TODO: Add company.lat/lng to Company model in future)
    # For now, return all companies (assume all serve the area)
    # In production, add lat/lng to Company model and filter here

    nearby_companies = all_companies[:20]  # Limit to 20 companies for now

    return nearby_companies


def broadcast_job_to_companies(
    marketplace_job_id: str,
    db: Session,
    radius_miles: int = 50
) -> Dict:
    """
    Broadcast a marketplace job to all eligible companies

    Args:
        marketplace_job_id: Job UUID
        db: Database session
        radius_miles: How far to search for companies

    Returns:
        Dict with broadcast stats: {
            "companies_notified": 10,
            "emails_sent": 10,
            "broadcast_ids": [...]
        }
    """
    # Get the job
    job = db.query(MarketplaceJob).filter(
        MarketplaceJob.id == marketplace_job_id
    ).first()

    if not job:
        raise ValueError(f"Job {marketplace_job_id} not found")

    if job.status != 'in_progress':
        raise ValueError(f"Job must be in 'in_progress' status to broadcast. Current: {job.status}")

    # Extract location
    pickup = job.pickup or {}
    lat = pickup.get('lat')
    lng = pickup.get('lng')

    if not lat or not lng:
        raise ValueError("Job must have pickup location with lat/lng")

    # Find companies in radius
    companies = find_companies_in_radius(lat, lng, radius_miles, db)

    if not companies:
        # No companies found - update job status
        job.status = 'open_for_bids'
        job.broadcast_at = datetime.utcnow()
        db.commit()
        return {
            "companies_notified": 0,
            "emails_sent": 0,
            "broadcast_ids": [],
            "message": "No companies found in area"
        }

    # Create broadcast records and send notifications
    broadcast_ids = []
    emails_sent = 0

    for company in companies:
        # Check if already broadcasted to this company
        existing = db.query(JobBroadcast).filter(
            JobBroadcast.marketplace_job_id == marketplace_job_id,
            JobBroadcast.company_id == company.id
        ).first()

        if existing:
            continue  # Skip duplicates

        # Create broadcast record
        broadcast = JobBroadcast(
            marketplace_job_id=marketplace_job_id,
            company_id=company.id,
            notification_method='email'
        )
        db.add(broadcast)
        broadcast_ids.append(str(broadcast.id))

        # Send email notification (imported from notifications.py)
        try:
            from app.notifications import send_new_job_notification
            send_new_job_notification(company, job, db)
            emails_sent += 1
        except Exception as e:
            print(f"Failed to send email to {company.email}: {e}")

    # Update job status
    job.status = 'open_for_bids'
    job.broadcast_at = datetime.utcnow()
    job.bid_deadline = datetime.utcnow() + timedelta(hours=48)

    db.commit()

    return {
        "companies_notified": len(companies),
        "emails_sent": emails_sent,
        "broadcast_ids": broadcast_ids,
        "bid_deadline": job.bid_deadline
    }


def auto_generate_bid(
    marketplace_job_id: str,
    company_id: str,
    db: Session
) -> Optional[Bid]:
    """
    Auto-generate a bid based on company's pricing rules
    (Optional feature - companies can enable auto-bidding)

    Args:
        marketplace_job_id: Job UUID
        company_id: Company UUID
        db: Database session

    Returns:
        Bid object or None if failed
    """
    # Get job
    job = db.query(MarketplaceJob).filter(
        MarketplaceJob.id == marketplace_job_id
    ).first()

    if not job:
        return None

    # Get company pricing config
    pricing = db.query(PricingConfig).filter(
        PricingConfig.company_id == company_id
    ).first()

    if not pricing:
        return None

    # Calculate price using company's rules
    total_cbm = float(job.total_cbm or 0)

    base_price = float(pricing.callout_fee)
    cbm_price = total_cbm * float(pricing.price_per_cbm)

    # Count bulky/fragile items by weight threshold
    bulky_count = 0
    fragile_count = 0
    threshold = float(pricing.bulky_weight_threshold_kg or 50)

    rooms = db.query(MarketplaceRoom).filter(MarketplaceRoom.marketplace_job_id == job.id).all()
    for room in rooms:
        items = db.query(MarketplaceItem).filter(MarketplaceItem.marketplace_room_id == room.id).all()
        for item in items:
            qty = item.quantity or 1
            if item.weight_kg and float(item.weight_kg) > threshold:
                bulky_count += qty
            if item.fragile:
                fragile_count += qty

    bulky_surcharge = bulky_count * float(pricing.bulky_item_fee)
    fragile_surcharge = fragile_count * float(pricing.fragile_item_fee)

    total_price = base_price + cbm_price + bulky_surcharge + fragile_surcharge

    # Add 10% margin for auto-bids
    total_price = total_price * 1.10

    # Round to nearest £5
    total_price = round(total_price / 5) * 5

    # Create bid
    bid = Bid(
        marketplace_job_id=marketplace_job_id,
        company_id=company_id,
        price=total_price,
        message="Auto-generated quote based on our standard pricing",
        estimated_duration_hours=int(total_cbm * 0.5) + 4,  # Rough estimate
        crew_size=2 if total_cbm < 15 else 3,
        status='pending',
        expires_at=datetime.utcnow() + timedelta(hours=48),
        auto_generated=True
    )

    db.add(bid)
    db.commit()
    db.refresh(bid)

    # Update job status
    if job.status == 'open_for_bids':
        job.status = 'bids_received'
        db.commit()

    # Send notification to customer
    try:
        from app.notifications import send_new_bid_notification
        send_new_bid_notification(job, bid, db)
    except Exception as e:
        print(f"Failed to send bid notification: {e}")

    return bid


def accept_bid(
    marketplace_job_id: str,
    bid_id: str,
    db: Session
) -> Dict:
    """
    Customer accepts a winning bid

    Args:
        marketplace_job_id: Job UUID
        bid_id: Bid UUID
        db: Database session

    Returns:
        Dict with result: {
            "success": True,
            "winning_bid": Bid,
            "commission_amount": 127.50,
            "job_status": "awarded"
        }
    """
    # Get job
    job = db.query(MarketplaceJob).filter(
        MarketplaceJob.id == marketplace_job_id
    ).first()

    if not job:
        raise ValueError("Job not found")

    # Get bid
    bid = db.query(Bid).filter(
        Bid.id == bid_id,
        Bid.marketplace_job_id == marketplace_job_id
    ).first()

    if not bid:
        raise ValueError("Bid not found")

    # Validate bid is still valid
    if bid.status != 'pending':
        raise ValueError(f"Bid is not pending. Current status: {bid.status}")

    if bid.expires_at and datetime.utcnow() > bid.expires_at:
        raise ValueError("Bid has expired")

    # Accept this bid
    bid.status = 'accepted'
    bid.accepted_at = datetime.utcnow()

    # Reject all other bids for this job
    other_bids = db.query(Bid).filter(
        Bid.marketplace_job_id == marketplace_job_id,
        Bid.id != bid_id,
        Bid.status == 'pending'
    ).all()

    for other_bid in other_bids:
        other_bid.status = 'rejected'
        other_bid.rejected_at = datetime.utcnow()

    # Update job
    job.winning_company_id = bid.company_id
    job.winning_bid_id = bid.id
    job.final_price = bid.price
    job.status = 'awarded'
    job.awarded_at = datetime.utcnow()

    # Calculate commission
    commission_rate = float(job.commission_rate or 0.15)
    commission_amount = float(bid.price) * commission_rate

    job.commission_amount = commission_amount

    # Create commission record
    commission = Commission(
        marketplace_job_id=marketplace_job_id,
        company_id=bid.company_id,
        job_price=bid.price,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        status='pending'
    )
    db.add(commission)

    db.commit()

    # Send notifications
    try:
        from app.notifications import send_job_awarded_notification, send_job_not_awarded_notification

        # Notify winner
        winning_company = db.query(Company).filter(Company.id == bid.company_id).first()
        if winning_company:
            send_job_awarded_notification(winning_company, job, bid, db)

        # Notify losers
        for other_bid in other_bids:
            losing_company = db.query(Company).filter(Company.id == other_bid.company_id).first()
            if losing_company:
                send_job_not_awarded_notification(losing_company, job, db)

    except Exception as e:
        print(f"Failed to send award notifications: {e}")

    return {
        "success": True,
        "winning_bid": bid,
        "commission_amount": float(commission_amount),
        "job_status": "awarded",
        "losing_bids_count": len(other_bids)
    }


def charge_commission(
    commission_id: str,
    db: Session,
    stripe_api_key: str = None
) -> Dict:
    """
    Charge commission via Stripe
    (Uses Stripe Connect to charge company)

    Args:
        commission_id: Commission UUID
        db: Database session
        stripe_api_key: Stripe secret key

    Returns:
        Dict with result: {
            "success": True,
            "charge_id": "ch_...",
            "amount": 127.50
        }
    """
    import stripe
    import os

    # Get commission
    commission = db.query(Commission).filter(
        Commission.id == commission_id
    ).first()

    if not commission:
        raise ValueError("Commission not found")

    if commission.status != 'pending':
        raise ValueError(f"Commission must be pending. Current: {commission.status}")

    # Get company
    company = db.query(Company).filter(
        Company.id == commission.company_id
    ).first()

    if not company or not company.stripe_customer_id:
        raise ValueError("Company must have Stripe customer ID")

    # Set Stripe API key
    stripe.api_key = stripe_api_key or os.getenv("STRIPE_SECRET_KEY")

    # Amount in pence (Stripe uses smallest currency unit)
    amount_pence = int(float(commission.commission_amount) * 100)

    try:
        # Create charge
        charge = stripe.Charge.create(
            amount=amount_pence,
            currency='gbp',
            customer=company.stripe_customer_id,
            description=f"Commission for marketplace job {commission.marketplace_job_id}",
            metadata={
                "commission_id": str(commission.id),
                "job_id": str(commission.marketplace_job_id),
                "company_id": str(commission.company_id)
            }
        )

        # Update commission
        commission.status = 'paid'
        commission.stripe_charge_id = charge.id
        commission.paid_at = datetime.utcnow()

        # Update job
        job = db.query(MarketplaceJob).filter(
            MarketplaceJob.id == commission.marketplace_job_id
        ).first()
        if job:
            job.commission_paid = True
            job.commission_paid_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "charge_id": charge.id,
            "amount": float(commission.commission_amount),
            "status": "paid"
        }

    except stripe.error.CardError as e:
        # Card was declined
        commission.status = 'failed'
        commission.failed_at = datetime.utcnow()
        commission.failure_reason = str(e)
        db.commit()

        return {
            "success": False,
            "error": str(e),
            "status": "failed"
        }

    except Exception as e:
        # Other error
        commission.status = 'failed'
        commission.failed_at = datetime.utcnow()
        commission.failure_reason = str(e)
        db.commit()

        return {
            "success": False,
            "error": str(e),
            "status": "failed"
        }


def get_marketplace_stats(db: Session) -> Dict:
    """
    Get marketplace statistics for dev dashboard

    Returns:
        Dict with stats: {
            "total_jobs": 150,
            "open_jobs": 5,
            "total_bids": 450,
            "avg_bids_per_job": 3.0,
            "commission_pending": 1250.00,
            "commission_collected": 8750.00
        }
    """
    # Total jobs
    total_jobs = db.query(MarketplaceJob).count()

    # Open jobs (waiting for bids)
    open_jobs = db.query(MarketplaceJob).filter(
        MarketplaceJob.status.in_(['open_for_bids', 'bids_received'])
    ).count()

    # Total bids
    total_bids = db.query(Bid).count()

    # Avg bids per job
    avg_bids = total_bids / max(total_jobs, 1)

    # Commission pending
    from sqlalchemy import func
    commission_pending = db.query(
        func.sum(Commission.commission_amount)
    ).filter(
        Commission.status == 'pending'
    ).scalar() or 0

    # Commission collected
    commission_collected = db.query(
        func.sum(Commission.commission_amount)
    ).filter(
        Commission.status == 'paid'
    ).scalar() or 0

    # Jobs awarded (completed bidding)
    jobs_awarded = db.query(MarketplaceJob).filter(
        MarketplaceJob.status == 'awarded'
    ).count()

    # Acceptance rate
    acceptance_rate = (jobs_awarded / max(total_jobs, 1)) * 100 if total_jobs > 0 else 0

    return {
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "jobs_awarded": jobs_awarded,
        "total_bids": total_bids,
        "avg_bids_per_job": round(avg_bids, 1),
        "acceptance_rate": round(acceptance_rate, 1),
        "commission_pending": float(commission_pending),
        "commission_collected": float(commission_collected),
        "commission_total": float(commission_pending) + float(commission_collected)
    }
