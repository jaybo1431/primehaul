"""
Email Notification System - Marketplace & B2B

This module handles all email notifications:
- Marketplace: Job broadcasts, bid notifications, award notifications
- B2B: Welcome emails, trial reminders, subscription updates

Uses Python's smtplib for now (upgrade to SendGrid/Mailgun in production)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models import (
    Company, MarketplaceJob, Bid, User
)


def get_smtp_config():
    """Get SMTP configuration from environment variables"""
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@primehaul.co.uk"),
        "from_name": os.getenv("SMTP_FROM_NAME", "PrimeHaul")
    }


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML version of email
        text_body: Plain text version (optional)

    Returns:
        True if sent successfully, False otherwise
    """
    config = get_smtp_config()

    # Skip if SMTP not configured (development mode)
    if not config["username"] or not config["password"]:
        print(f"[EMAIL SKIPPED - SMTP not configured] To: {to_email}, Subject: {subject}")
        return True

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{config['from_name']} <{config['from_email']}>"
        msg['To'] = to_email

        # Add plain text version
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)

        # Add HTML version
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        # Send via SMTP
        with smtplib.SMTP(config['host'], config['port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)

        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True

    except Exception as e:
        print(f"[EMAIL FAILED] To: {to_email}, Error: {e}")
        return False


def format_currency(amount: float) -> str:
    """Format number as GBP currency"""
    return f"£{amount:,.2f}"


def format_cbm(cbm: float) -> str:
    """Format CBM with 1 decimal place"""
    return f"{cbm:.1f} CBM"


# ==========================================
# MARKETPLACE NOTIFICATIONS
# ==========================================

def send_new_job_notification(company: Company, job: MarketplaceJob, db: Session) -> bool:
    """
    Email company about new marketplace job available for bidding

    Args:
        company: Company to notify
        job: Marketplace job
        db: Database session

    Returns:
        True if sent successfully
    """
    # Get job details
    pickup_city = job.pickup_city or "Unknown"
    dropoff_city = job.dropoff_city or "Unknown"
    total_cbm = float(job.total_cbm or 0)
    property_type = job.property_type or "Property"

    # Calculate estimated price range (rough estimate)
    # Use average UK pricing: £35/CBM + £250 callout
    est_low = (total_cbm * 30) + 200
    est_high = (total_cbm * 40) + 300

    # Calculate distance (if available)
    distance_text = ""
    if job.pickup and job.dropoff:
        try:
            from app.marketplace import calculate_distance_miles
            pickup_lat = job.pickup.get('lat')
            pickup_lng = job.pickup.get('lng')
            dropoff_lat = job.dropoff.get('lat')
            dropoff_lng = job.dropoff.get('lng')

            if all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
                distance = calculate_distance_miles(
                    pickup_lat, pickup_lng, dropoff_lat, dropoff_lng
                )
                distance_text = f"{int(distance)} miles"
        except:
            pass

    # Bid deadline
    deadline = job.bid_deadline or (datetime.utcnow() + timedelta(hours=48))
    hours_left = int((deadline - datetime.utcnow()).total_seconds() / 3600)

    subject = f"🆕 New removal job in {pickup_city} - {format_currency(est_low)}-{format_currency(est_high)}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2ee59d; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .job-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .detail-label {{ font-weight: 600; color: #666; }}
            .detail-value {{ color: #333; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .cta-button:hover {{ background: #26c785; }}
            .urgency {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">New Removal Job Available</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">A customer is waiting for your quote</p>
            </div>

            <div class="content">
                <p>Hi {company.company_name},</p>

                <p>A new removal job just posted in your area. This customer is ready to book!</p>

                <div class="job-details">
                    <h3 style="margin-top: 0; color: #2ee59d;">Job Details</h3>

                    <div class="detail-row">
                        <span class="detail-label">📍 Route</span>
                        <span class="detail-value">{pickup_city} → {dropoff_city}</span>
                    </div>

                    {f'<div class="detail-row"><span class="detail-label">🚗 Distance</span><span class="detail-value">{distance_text}</span></div>' if distance_text else ''}

                    <div class="detail-row">
                        <span class="detail-label">🏠 Property</span>
                        <span class="detail-value">{property_type}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">📦 Volume</span>
                        <span class="detail-value">{format_cbm(total_cbm)}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">💰 Estimated Value</span>
                        <span class="detail-value">{format_currency(est_low)} - {format_currency(est_high)}</span>
                    </div>
                </div>

                <div class="urgency">
                    <strong>⏰ Bid Deadline:</strong> You have {hours_left} hours to submit your quote
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/{company.slug}/admin/marketplace/job/{job.id}" class="cta-button">
                        View Full Details & Submit Bid →
                    </a>
                </center>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>Why bid on marketplace jobs?</strong><br>
                    • No marketing costs - we find the customers<br>
                    • AI-analyzed inventory - accurate quotes<br>
                    • Customers are ready to book NOW<br>
                    • Win rate: Companies typically win 1 in 3-4 bids
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul Marketplace • Connecting customers with the best removal companies</p>
                <p><a href="https://app.primehaul.co.uk/{company.slug}/admin/settings" style="color: #999;">Notification Settings</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(company.email, subject, html_body)


def send_new_bid_notification(job: MarketplaceJob, bid: Bid, db: Session) -> bool:
    """
    Email customer when they receive a new bid

    Args:
        job: Marketplace job
        bid: Bid that was just submitted
        db: Database session

    Returns:
        True if sent successfully
    """
    # Get company info
    company = db.query(Company).filter(Company.id == bid.company_id).first()
    if not company:
        return False

    # Get bid count
    from sqlalchemy import func
    total_bids = db.query(func.count(Bid.id)).filter(
        Bid.marketplace_job_id == job.id,
        Bid.status == 'pending'
    ).scalar() or 0

    subject = f"New quote received: {format_currency(float(bid.price))} from {company.company_name}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2ee59d; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .bid-card {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2ee59d; }}
            .price {{ font-size: 32px; font-weight: bold; color: #2ee59d; margin: 10px 0; }}
            .company-name {{ font-size: 20px; font-weight: 600; color: #333; margin-bottom: 10px; }}
            .bid-details {{ color: #666; margin: 15px 0; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .badge {{ display: inline-block; background: #fff3cd; color: #856404; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">🎉 You have a new quote!</h2>
            </div>

            <div class="content">
                <p>Hi {job.customer_name or 'there'},</p>

                <p>Great news! A removal company just submitted a quote for your move from {job.pickup_city} to {job.dropoff_city}.</p>

                <div class="bid-card">
                    <div class="company-name">{company.company_name}</div>
                    <div class="price">{format_currency(float(bid.price))}</div>

                    <div class="bid-details">
                        {f'<p><strong>Crew:</strong> {bid.crew_size} movers</p>' if bid.crew_size else ''}
                        {f'<p><strong>Estimated time:</strong> {bid.estimated_duration_hours} hours</p>' if bid.estimated_duration_hours else ''}
                        {f'<p style="margin-top: 15px; font-style: italic;">"{bid.message}"</p>' if bid.message else ''}
                    </div>

                    <span class="badge">Quote {total_bids} of {total_bids}</span>
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/marketplace/{job.token}/quotes" class="cta-button">
                        View All Quotes & Book →
                    </a>
                </center>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>💡 Tip:</strong> Wait for a few more quotes to compare prices. Most jobs receive 3-5 quotes within 24 hours.
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul • Making moving easier</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(job.customer_email, subject, html_body)


def send_job_awarded_notification(company: Company, job: MarketplaceJob, bid: Bid, db: Session) -> bool:
    """
    Email winning company when customer accepts their bid

    Args:
        company: Winning company
        job: Marketplace job
        bid: Accepted bid
        db: Database session

    Returns:
        True if sent successfully
    """
    commission_amount = float(job.commission_amount or 0)
    bid_price = float(bid.price)
    company_receives = bid_price - commission_amount

    subject = f"🎉 Congratulations! You won the job - {format_currency(bid_price)}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2ee59d 0%, #26c785 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
            .trophy {{ font-size: 48px; margin-bottom: 10px; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .success-card {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; border: 2px solid #2ee59d; }}
            .price-breakdown {{ background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .row {{ display: flex; justify-content: space-between; padding: 8px 0; }}
            .total {{ border-top: 2px solid #2ee59d; margin-top: 10px; padding-top: 10px; font-weight: bold; font-size: 18px; }}
            .customer-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }}
            .next-steps {{ background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="trophy">🏆</div>
                <h2 style="margin: 0;">Congratulations!</h2>
                <p style="margin: 10px 0 0 0; font-size: 18px;">The customer chose your quote</p>
            </div>

            <div class="content">
                <p>Hi {company.company_name},</p>

                <p><strong>Great news!</strong> {job.customer_name or 'The customer'} accepted your quote for the removal job from {job.pickup_city} to {job.dropoff_city}.</p>

                <div class="success-card">
                    <h3 style="margin-top: 0; color: #2ee59d;">Job Details</h3>
                    <p><strong>Route:</strong> {job.pickup_city} → {job.dropoff_city}</p>
                    <p><strong>Volume:</strong> {format_cbm(float(job.total_cbm or 0))}</p>
                    <p><strong>Property:</strong> {job.property_type or 'N/A'}</p>
                </div>

                <div class="price-breakdown">
                    <h3 style="margin-top: 0;">💰 Payment Breakdown</h3>
                    <div class="row">
                        <span>Job price:</span>
                        <span>{format_currency(bid_price)}</span>
                    </div>
                    <div class="row">
                        <span>PrimeHaul commission (15%):</span>
                        <span>-{format_currency(commission_amount)}</span>
                    </div>
                    <div class="row total">
                        <span>You receive:</span>
                        <span style="color: #2ee59d;">{format_currency(company_receives)}</span>
                    </div>
                </div>

                <div class="customer-info">
                    <h3 style="margin-top: 0;">📞 Customer Contact Information</h3>
                    <p><strong>Name:</strong> {job.customer_name or 'N/A'}</p>
                    <p><strong>Email:</strong> {job.customer_email or 'N/A'}</p>
                    <p><strong>Phone:</strong> {job.customer_phone or 'N/A'}</p>
                </div>

                <div class="next-steps">
                    <h3 style="margin-top: 0;">✅ Next Steps</h3>
                    <ol style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Contact the customer</strong> within 24 hours to confirm the move date and details</li>
                        <li><strong>Complete the move</strong> to the customer's satisfaction</li>
                        <li><strong>Payment will be processed</strong> automatically - commission charged to your account</li>
                    </ol>
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/{company.slug}/admin/marketplace/job/{job.id}" class="cta-button">
                        View Full Job Details →
                    </a>
                </center>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>Need help?</strong> Contact PrimeHaul support at support@primehaul.co.uk
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul Marketplace • Connecting you with customers</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(company.email, subject, html_body)


def send_job_not_awarded_notification(company: Company, job: MarketplaceJob, db: Session) -> bool:
    """
    Email losing companies when another company wins the job

    Args:
        company: Company that didn't win
        job: Marketplace job
        db: Database session

    Returns:
        True if sent successfully
    """
    subject = "Job filled - More opportunities available"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #6c757d; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .info-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }}
            .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
            .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #2ee59d; }}
            .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">Job Update</h2>
            </div>

            <div class="content">
                <p>Hi {company.company_name},</p>

                <p>The removal job from <strong>{job.pickup_city} → {job.dropoff_city}</strong> has been awarded to another company.</p>

                <div class="info-box">
                    <h3 style="margin-top: 0;">💡 Don't worry - this is normal!</h3>
                    <p>On average, companies win <strong>1 in every 3-4 bids</strong> on the PrimeHaul marketplace. The key to success is bidding on multiple jobs.</p>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">10+</div>
                        <div class="stat-label">New jobs posted daily</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">30%</div>
                        <div class="stat-label">Average win rate</div>
                    </div>
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/{company.slug}/admin/marketplace" class="cta-button">
                        View Available Jobs →
                    </a>
                </center>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>💡 Tips to win more jobs:</strong><br>
                    • Respond quickly (first bids win 40% more often)<br>
                    • Price competitively but fairly<br>
                    • Add a personal message to stand out<br>
                    • Build your reviews (coming soon)
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul Marketplace • Keep bidding, keep winning</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(company.email, subject, html_body)


# ==========================================
# B2B SAAS NOTIFICATIONS
# ==========================================

def send_welcome_email(company: Company, user: User, temporary_password: str) -> bool:
    """
    Welcome email when company signs up

    Args:
        company: New company
        user: Owner user account
        temporary_password: Temporary password for first login

    Returns:
        True if sent successfully
    """
    subject = f"Welcome to PrimeHaul OS - Your 30-day trial has started"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2ee59d 0%, #26c785 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .credentials {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; font-family: monospace; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }}
            .checklist {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">🎉 Welcome to PrimeHaul OS!</h2>
                <p style="margin: 10px 0 0 0;">Your 30-day free trial has started</p>
            </div>

            <div class="content">
                <p>Hi {user.full_name or 'there'},</p>

                <p>Welcome to <strong>PrimeHaul OS</strong> - the AI-powered removal quote system that will transform how you quote jobs.</p>

                <div class="credentials">
                    <strong>⚠️ Your Login Credentials:</strong><br><br>
                    <strong>URL:</strong> https://app.primehaul.co.uk/{company.slug}/admin<br>
                    <strong>Email:</strong> {user.email}<br>
                    <strong>Temporary Password:</strong> {temporary_password}<br><br>
                    <em>Please change your password after first login!</em>
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/{company.slug}/admin" class="cta-button">
                        Login to Your Dashboard →
                    </a>
                </center>

                <div class="checklist">
                    <h3 style="margin-top: 0;">✅ Getting Started Checklist</h3>
                    <ol style="padding-left: 20px;">
                        <li><strong>Login</strong> and change your password</li>
                        <li><strong>Customize your branding</strong> (logo, colors)</li>
                        <li><strong>Set your pricing rules</strong> (£/CBM, surcharges)</li>
                        <li><strong>Send your first survey</strong> to a customer</li>
                        <li><strong>Watch the AI</strong> analyze photos and calculate quotes</li>
                    </ol>
                </div>

                <p><strong>What's included in your trial:</strong></p>
                <ul>
                    <li>✅ Unlimited AI-powered quotes</li>
                    <li>✅ Custom branding (your logo, colors)</li>
                    <li>✅ Custom pricing rules</li>
                    <li>✅ Multi-user accounts</li>
                    <li>✅ Analytics dashboard</li>
                    <li>✅ Email support</li>
                </ul>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>Need help?</strong> Reply to this email or contact us at support@primehaul.co.uk
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul OS • AI-powered removal quotes</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_body)


def send_trial_ending_reminder(company: Company, days_left: int) -> bool:
    """
    Remind company their trial is ending soon

    Args:
        company: Company on trial
        days_left: Days remaining in trial

    Returns:
        True if sent successfully
    """
    subject = f"⏰ Your PrimeHaul trial ends in {days_left} days"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #ffc107; color: #333; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .cta-button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }}
            .pricing {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .price {{ font-size: 48px; font-weight: bold; color: #2ee59d; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">⏰ Your trial is ending soon</h2>
            </div>

            <div class="content">
                <p>Hi {company.company_name},</p>

                <p>Your 30-day free trial of PrimeHaul OS ends in <strong>{days_left} days</strong>.</p>

                <div class="pricing">
                    <p style="margin: 0; color: #666;">Continue with PrimeHaul OS for</p>
                    <div class="price">£99<span style="font-size: 24px;">/month</span></div>
                    <p style="color: #666; margin: 10px 0 0 0;">Unlimited AI-powered quotes</p>
                </div>

                <center>
                    <a href="https://app.primehaul.co.uk/{company.slug}/billing/subscribe" class="cta-button">
                        Subscribe Now →
                    </a>
                </center>

                <p style="margin-top: 30px;"><strong>What you'll keep:</strong></p>
                <ul>
                    <li>✅ Unlimited quotes (no per-quote fees)</li>
                    <li>✅ AI photo analysis</li>
                    <li>✅ Custom branding</li>
                    <li>✅ Custom pricing rules</li>
                    <li>✅ Multi-user accounts</li>
                    <li>✅ Priority support</li>
                </ul>

                <p style="color: #666; font-size: 14px;">
                    Cancel anytime. No long-term contracts.
                </p>
            </div>

            <div class="footer">
                <p>PrimeHaul OS</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(company.email, subject, html_body)
