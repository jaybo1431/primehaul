"""
PrimeHaul Sales Outreach Automation

Private dashboard for:
- Auto-scraping removal company leads
- Sending cold email sequences
- Reading and auto-replying to responses
- Tracking pipeline
"""

import os
import re
import json
import imaplib
import email
import smtplib
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.database import get_db
from app.models import Base
import logging

logger = logging.getLogger(__name__)


# ============================================
# DATABASE MODELS
# ============================================

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    REPLIED = "replied"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    SIGNED_UP = "signed_up"
    DEAD = "dead"


class Lead(Base):
    __tablename__ = "outreach_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    website = Column(String(255))
    location = Column(String(100))
    source = Column(String(50))  # Manual, Checkatrade, Yell, etc.

    status = Column(String(20), default="new")
    emails_sent = Column(Integer, default=0)
    last_contacted = Column(DateTime)
    last_reply = Column(DateTime)
    next_followup = Column(DateTime)

    notes = Column(Text)
    reply_summary = Column(Text)  # AI summary of their reply
    sentiment = Column(String(20))  # positive, negative, neutral, question

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutreachEmail(Base):
    __tablename__ = "outreach_emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), nullable=False)
    direction = Column(String(10))  # sent, received
    subject = Column(String(255))
    body = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    message_id = Column(String(255))  # For threading


# ============================================
# EMAIL TEMPLATES
# ============================================

EMAIL_TEMPLATES = {
    "initial": {
        "subject": "Your competitors are quoting in 5 mins now",
        "body": """Hey {first_name},

Be honest - how many quotes did you lose last month because you couldn't get back to them fast enough?

Every removal company I talk to says the same thing: "By the time I called them back, they'd already booked someone else."

Here's the fix:

Customer clicks your link → snaps photos of their rooms → AI counts EVERYTHING → instant quote.

5 minutes. Done. They book on the spot.

One company using this quoted 23 jobs last week. His words: "I used to spend my whole Sunday doing estimates. Now I approve them from the van between jobs."

I'll set you up with 3 free AI quotes - takes 60 seconds: {demo_link}

Your logo. Your pricing. Customers think it's your tech.

Jay

P.S. The busy season's coming. The companies using AI quotes are going to eat everyone else's lunch. Don't be lunch."""
    },

    "followup_1": {
        "subject": "Re: Your competitors are quoting in 5 mins now",
        "body": """{first_name},

Quick update - 3 more removal companies signed up yesterday.

Not trying to pressure you. Just saying - your competitors are going to start stealing your leads with instant quotes while you're still playing phone tag.

The maths is brutal:
- Old way: Customer enquires → you call back in 2 hours → they've already booked
- New way: Customer enquires → instant AI quote → they book YOU

Still got your 3 free quotes waiting: {demo_link}

60 seconds to set up. Seriously.

Jay"""
    },

    "followup_2": {
        "subject": "Closing your spot",
        "body": """Hey {first_name},

Last email, I promise.

I'm limiting free trials in each area so companies don't all get the same advantage. Makes sense - if everyone has AI quotes, no one has the edge.

Your 3 free quotes expire in 48 hours: {demo_link}

After that, you'd have to wait for the next opening.

No pressure. If you're happy with your current close rate, ignore this.

But if you're losing quotes to faster competitors... this is your fix.

Jay

P.S. One guy told me "I wish I'd done this 6 months ago." Don't be that guy in 6 months."""
    },

    "reply_interested": {
        "subject": "Re: {original_subject}",
        "body": """YES {first_name}! Let's get you set up.

Here's your link: {demo_link}

Literally takes 60 seconds:
1. Click the link, add your company name
2. Set your pricing (we've got smart defaults)
3. Send your first quote link to a customer

You could have your first AI quote out in the next 10 minutes.

Any issues, just reply here - I'll sort you out.

Jay

P.S. Pro tip: Send it to a real customer straight away. Nothing beats seeing their reaction when they get an instant quote instead of "we'll call you back"."""
    },

    "reply_question": {
        "subject": "Re: {original_subject}",
        "body": """{first_name},

Great question - here's the answer:

{answer}

Want me to jump on a quick 5-min call and walk you through it live? Sometimes easier than email.

Or just hit this link and see for yourself: {demo_link}

Jay"""
    },

    "reply_objection": {
        "subject": "Re: {original_subject}",
        "body": """{first_name},

Fair point. Let me address that:

{objection_response}

Look, I'm not here to twist your arm. You know your business.

But if speed-to-quote is costing you jobs, this solves it overnight: {demo_link}

Cheers,
Jay"""
    }
}

# Common objection responses - punchy and real
OBJECTION_RESPONSES = {
    "too busy": "That's literally why you need this. You're too busy to spend 2 hours quoting. This does it in 5 minutes. One guy told me he used to quote on Sundays - now he's actually watching his kid's football games.",
    "already have software": "Nice! Quick question though - can your customers photograph their rooms and get an instant quote without calling you? That's the game-changer. The companies winning right now are the ones who quote BEFORE the customer has time to call anyone else.",
    "too expensive": "Here's the maths: It's £6.99 per quote at bulk rates. The average removal job is what, £600-800? You need to win ONE extra job per year to be massively in profit. Most companies are winning 3-4 extra jobs per MONTH because they're first to quote.",
    "not interested": "Respect. I'll leave you be. One thing though - bookmark this link: {demo_link}. When you lose a job to someone who quoted faster, you'll know where to find me. No hard feelings either way.",
    "how does it work": "Dead simple: Customer clicks your link → takes 5 photos of their rooms → AI instantly counts every sofa, bed, wardrobe, box → calculates the quote using YOUR prices → you approve it with one tap from your phone. Total time: 5 minutes. No home visit. No phone tag. No spreadsheets.",
    "is it accurate": "Trained on thousands of UK removals. Typically within 5% of what you'd quote manually. But here's the thing - YOU approve every quote before it goes out. If the AI says £650 and you think it's £700, you change it. You're always in control.",
    "maybe later": "Totally get it. Just know that I'm limiting free trials by area - don't want every company in your postcode having the same advantage. When you're ready, hit me up and I'll see if there's still a spot.",
    "send more info": "Even better - just try it. Here's 3 free quotes, no card needed: {demo_link}. Takes 60 seconds to set up. You'll learn more in 5 minutes of using it than any PDF I could send.",
}


# ============================================
# EMAIL FUNCTIONS
# ============================================

def get_smtp_config():
    """Get SMTP configuration from environment"""
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "from_email": os.environ.get("OUTREACH_EMAIL", os.environ.get("SMTP_USER", "")),
        "from_name": os.environ.get("OUTREACH_NAME", "Jay from PrimeHaul"),
    }


def get_imap_config():
    """Get IMAP configuration for reading replies"""
    return {
        "host": os.environ.get("IMAP_HOST", "imap.gmail.com"),
        "port": int(os.environ.get("IMAP_PORT", 993)),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
    }


def send_outreach_email(
    to_email: str,
    subject: str,
    body: str,
    reply_to_message_id: str = None
) -> tuple[bool, str]:
    """
    Send an outreach email

    Returns:
        (success, message_id or error)
    """
    config = get_smtp_config()

    if not config["user"] or not config["password"]:
        return False, "SMTP not configured"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{config['from_name']} <{config['from_email']}>"
        msg['To'] = to_email

        # Generate message ID for threading
        message_id = f"<{uuid.uuid4()}@primehaul.co.uk>"
        msg['Message-ID'] = message_id

        if reply_to_message_id:
            msg['In-Reply-To'] = reply_to_message_id
            msg['References'] = reply_to_message_id

        # Plain text version
        msg.attach(MIMEText(body, 'plain'))

        # HTML version (simple formatting)
        html_body = body.replace('\n', '<br>')
        html = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
        {html_body}
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))

        # Send
        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls()
            server.login(config["user"], config["password"])
            server.send_message(msg)

        return True, message_id

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False, str(e)


def check_for_replies(db: Session, since_hours: int = 24) -> List[Dict]:
    """
    Check inbox for replies to outreach emails

    Returns list of new replies with parsed info
    """
    config = get_imap_config()

    if not config["user"] or not config["password"]:
        return []

    replies = []

    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(config["host"], config["port"])
        mail.login(config["user"], config["password"])
        mail.select('INBOX')

        # Search for recent emails
        since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%d-%b-%Y")
        _, message_nums = mail.search(None, f'(SINCE {since_date})')

        for num in message_nums[0].split():
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)

            from_email = email.utils.parseaddr(msg['From'])[1]
            subject = msg['Subject'] or ""
            message_id = msg['Message-ID']
            in_reply_to = msg.get('In-Reply-To', '')

            # Check if this is a reply to one of our emails
            lead = db.query(Lead).filter(Lead.email == from_email).first()
            if not lead:
                continue

            # Check if we already processed this
            existing = db.query(OutreachEmail).filter(
                OutreachEmail.message_id == message_id
            ).first()
            if existing:
                continue

            # Extract body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

            # Analyze sentiment
            sentiment = analyze_reply_sentiment(body_text)

            replies.append({
                "lead_id": str(lead.id),
                "lead_name": lead.company_name,
                "from_email": from_email,
                "subject": subject,
                "body": body_text,
                "message_id": message_id,
                "sentiment": sentiment,
            })

            # Save the reply
            outreach_email = OutreachEmail(
                lead_id=lead.id,
                direction="received",
                subject=subject,
                body=body_text,
                message_id=message_id,
            )
            db.add(outreach_email)

            # Update lead
            lead.last_reply = datetime.utcnow()
            lead.status = "replied"
            lead.sentiment = sentiment

            db.commit()

        mail.close()
        mail.logout()

    except Exception as e:
        logger.error(f"Error checking replies: {e}")

    return replies


def analyze_reply_sentiment(body: str) -> str:
    """
    Simple sentiment analysis on reply

    Returns: positive, negative, neutral, question
    """
    body_lower = body.lower()

    # Positive signals
    positive_words = ['interested', 'sounds good', 'tell me more', 'yes', 'great', 'love', 'perfect', 'demo', 'try', 'sign up', 'how do i', 'send me']
    if any(word in body_lower for word in positive_words):
        return "positive"

    # Negative signals
    negative_words = ['not interested', 'no thanks', 'unsubscribe', 'stop', 'remove', 'don\'t contact', 'already have', 'not for us', 'too busy']
    if any(word in body_lower for word in negative_words):
        return "negative"

    # Question signals
    question_words = ['how', 'what', 'why', 'when', 'who', 'does it', 'can it', 'is it', '?']
    if any(word in body_lower for word in question_words):
        return "question"

    return "neutral"


def generate_auto_reply(lead: Lead, their_reply: str, sentiment: str) -> tuple[str, str]:
    """
    Generate an appropriate auto-reply based on sentiment

    Returns: (subject, body)
    """
    first_name = lead.company_name.split()[0] if lead.company_name else "there"
    demo_link = f"https://app.primehaul.co.uk/signup?ref={lead.email.split('@')[0]}"

    if sentiment == "positive":
        template = EMAIL_TEMPLATES["reply_interested"]
        subject = template["subject"].replace("{original_subject}", "Quick question about your quoting process")
        body = template["body"].format(
            first_name=first_name,
            demo_link=demo_link
        )

    elif sentiment == "negative":
        # Check for specific objection
        their_reply_lower = their_reply.lower()
        objection_response = OBJECTION_RESPONSES.get("not interested")

        for key, response in OBJECTION_RESPONSES.items():
            if key in their_reply_lower:
                objection_response = response
                break

        template = EMAIL_TEMPLATES["reply_objection"]
        subject = template["subject"].replace("{original_subject}", "Quick question about your quoting process")
        body = template["body"].format(
            first_name=first_name,
            objection_response=objection_response,
            demo_link=demo_link
        )

    elif sentiment == "question":
        # Try to match their question to an answer
        their_reply_lower = their_reply.lower()
        answer = "Happy to explain more - what specifically would you like to know?"

        if "how does it work" in their_reply_lower or "how it works" in their_reply_lower:
            answer = OBJECTION_RESPONSES["how does it work"]
        elif "accurate" in their_reply_lower or "reliable" in their_reply_lower:
            answer = OBJECTION_RESPONSES["is it accurate"]
        elif "cost" in their_reply_lower or "price" in their_reply_lower or "expensive" in their_reply_lower:
            answer = OBJECTION_RESPONSES["too expensive"]

        template = EMAIL_TEMPLATES["reply_question"]
        subject = template["subject"].replace("{original_subject}", "Quick question about your quoting process")
        body = template["body"].format(
            first_name=first_name,
            answer=answer
        )

    else:  # neutral
        template = EMAIL_TEMPLATES["reply_interested"]
        subject = template["subject"].replace("{original_subject}", "Quick question about your quoting process")
        body = template["body"].format(
            first_name=first_name,
            demo_link=demo_link
        )

    return subject, body


# ============================================
# AUTOMATION FUNCTIONS
# ============================================

def get_leads_to_contact(db: Session, limit: int = 10) -> List[Lead]:
    """Get leads that need to be contacted"""
    # New leads that haven't been contacted
    new_leads = db.query(Lead).filter(
        Lead.status == "new",
        Lead.email.isnot(None),
        Lead.email != ""
    ).limit(limit).all()

    return new_leads


def get_leads_for_followup(db: Session, limit: int = 10) -> List[Lead]:
    """Get leads that need a follow-up"""
    now = datetime.utcnow()

    # Leads contacted but no reply, and enough time has passed
    followup_leads = db.query(Lead).filter(
        Lead.status == "contacted",
        Lead.emails_sent < 3,  # Max 3 emails
        Lead.next_followup <= now
    ).limit(limit).all()

    return followup_leads


def send_initial_email(lead: Lead, db: Session) -> bool:
    """Send initial cold email to a lead"""
    template = EMAIL_TEMPLATES["initial"]

    first_name = lead.company_name.split()[0] if lead.company_name else "there"
    demo_link = f"https://app.primehaul.co.uk/signup?ref={lead.email.split('@')[0]}"

    subject = template["subject"]
    body = template["body"].format(
        first_name=first_name,
        company_name=lead.company_name,
        demo_link=demo_link
    )

    success, message_id = send_outreach_email(lead.email, subject, body)

    if success:
        # Save sent email
        outreach_email = OutreachEmail(
            lead_id=lead.id,
            direction="sent",
            subject=subject,
            body=body,
            message_id=message_id,
        )
        db.add(outreach_email)

        # Update lead
        lead.status = "contacted"
        lead.emails_sent = 1
        lead.last_contacted = datetime.utcnow()
        lead.next_followup = datetime.utcnow() + timedelta(days=3)

        db.commit()
        return True

    return False


def send_followup_email(lead: Lead, db: Session) -> bool:
    """Send follow-up email based on how many we've sent"""
    emails_sent = lead.emails_sent or 0

    if emails_sent >= 3:
        lead.status = "dead"
        db.commit()
        return False

    template_key = f"followup_{emails_sent}"
    if template_key not in EMAIL_TEMPLATES:
        template_key = "followup_2"  # Use final template

    template = EMAIL_TEMPLATES[template_key]

    first_name = lead.company_name.split()[0] if lead.company_name else "there"
    demo_link = f"https://app.primehaul.co.uk/signup?ref={lead.email.split('@')[0]}"

    subject = template["subject"]
    body = template["body"].format(
        first_name=first_name,
        demo_link=demo_link
    )

    success, message_id = send_outreach_email(lead.email, subject, body)

    if success:
        outreach_email = OutreachEmail(
            lead_id=lead.id,
            direction="sent",
            subject=subject,
            body=body,
            message_id=message_id,
        )
        db.add(outreach_email)

        lead.emails_sent = emails_sent + 1
        lead.last_contacted = datetime.utcnow()

        # Set next followup
        if lead.emails_sent >= 3:
            lead.status = "dead"
            lead.next_followup = None
        else:
            lead.next_followup = datetime.utcnow() + timedelta(days=4)

        db.commit()
        return True

    return False


def run_automation_cycle(db: Session) -> Dict:
    """
    Run one cycle of the automation:
    1. Check for replies
    2. Send auto-replies where appropriate
    3. Send initial emails to new leads
    4. Send follow-ups where due

    Returns stats
    """
    stats = {
        "replies_found": 0,
        "auto_replies_sent": 0,
        "initial_emails_sent": 0,
        "followups_sent": 0,
        "errors": []
    }

    # 1. Check for replies
    try:
        replies = check_for_replies(db, since_hours=24)
        stats["replies_found"] = len(replies)

        # 2. Send auto-replies (only for positive/question, not negative)
        for reply in replies:
            lead = db.query(Lead).filter(Lead.id == reply["lead_id"]).first()
            if not lead:
                continue

            if reply["sentiment"] in ["positive", "question", "neutral"]:
                subject, body = generate_auto_reply(lead, reply["body"], reply["sentiment"])
                success, _ = send_outreach_email(lead.email, subject, body)
                if success:
                    stats["auto_replies_sent"] += 1

                    # Update lead status
                    if reply["sentiment"] == "positive":
                        lead.status = "interested"
                    db.commit()

    except Exception as e:
        stats["errors"].append(f"Reply check error: {e}")

    # 3. Send initial emails (max 5 per cycle to avoid spam)
    try:
        new_leads = get_leads_to_contact(db, limit=5)
        for lead in new_leads:
            if send_initial_email(lead, db):
                stats["initial_emails_sent"] += 1
    except Exception as e:
        stats["errors"].append(f"Initial email error: {e}")

    # 4. Send follow-ups (max 5 per cycle)
    try:
        followup_leads = get_leads_for_followup(db, limit=5)
        for lead in followup_leads:
            if send_followup_email(lead, db):
                stats["followups_sent"] += 1
    except Exception as e:
        stats["errors"].append(f"Followup error: {e}")

    return stats


# ============================================
# DASHBOARD STATS
# ============================================

def get_pipeline_stats(db: Session) -> Dict:
    """Get stats for the dashboard"""
    from sqlalchemy import func

    total = db.query(func.count(Lead.id)).scalar() or 0
    new = db.query(func.count(Lead.id)).filter(Lead.status == "new").scalar() or 0
    contacted = db.query(func.count(Lead.id)).filter(Lead.status == "contacted").scalar() or 0
    replied = db.query(func.count(Lead.id)).filter(Lead.status == "replied").scalar() or 0
    interested = db.query(func.count(Lead.id)).filter(Lead.status == "interested").scalar() or 0
    signed_up = db.query(func.count(Lead.id)).filter(Lead.status == "signed_up").scalar() or 0
    dead = db.query(func.count(Lead.id)).filter(Lead.status == "dead").scalar() or 0

    return {
        "total": total,
        "new": new,
        "contacted": contacted,
        "replied": replied,
        "interested": interested,
        "signed_up": signed_up,
        "dead": dead,
        "response_rate": round((replied + interested) / max(contacted, 1) * 100, 1),
        "conversion_rate": round(signed_up / max(total, 1) * 100, 1),
    }


def get_recent_activity(db: Session, limit: int = 20) -> List[Dict]:
    """Get recent email activity"""
    emails = db.query(OutreachEmail).order_by(
        OutreachEmail.sent_at.desc()
    ).limit(limit).all()

    activity = []
    for e in emails:
        lead = db.query(Lead).filter(Lead.id == e.lead_id).first()
        activity.append({
            "id": str(e.id),
            "lead_name": lead.company_name if lead else "Unknown",
            "lead_email": lead.email if lead else "",
            "direction": e.direction,
            "subject": e.subject,
            "body_preview": (e.body or "")[:100] + "..." if e.body and len(e.body) > 100 else e.body,
            "sent_at": e.sent_at.isoformat() if e.sent_at else None,
        })

    return activity


def import_leads_from_csv(csv_content: str, db: Session) -> Dict:
    """Import leads from CSV content"""
    import csv
    from io import StringIO

    reader = csv.DictReader(StringIO(csv_content))

    imported = 0
    skipped = 0
    errors = []

    for row in reader:
        email = row.get('email', '').strip()
        if not email or '@' not in email:
            skipped += 1
            continue

        # Check if already exists
        existing = db.query(Lead).filter(Lead.email == email).first()
        if existing:
            skipped += 1
            continue

        try:
            lead = Lead(
                company_name=row.get('name', row.get('company_name', '')).strip(),
                email=email,
                phone=row.get('phone', '').strip(),
                website=row.get('website', '').strip(),
                location=row.get('location', '').strip(),
                source=row.get('source', 'CSV Import').strip(),
                status="new",
            )
            db.add(lead)
            imported += 1
        except Exception as e:
            errors.append(str(e))

    db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
    }
