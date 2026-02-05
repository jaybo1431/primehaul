import os
import uuid
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
import aiofiles

from app.ai_vision import extract_removal_inventory
from app.database import get_db, engine
from app.models import Base, Company, User, PricingConfig, Job, Room, Item, Photo, AdminNote, UsageAnalytics, UserInteraction, AIItemPrediction, MarketplaceJob, Bid, JobBroadcast, Commission, MarketplaceRoom, MarketplaceItem, MarketplacePhoto, ItemFeedback, FurnitureCatalog, TrainingDataset, LearnedCorrection
from app.auth import hash_password, verify_password, create_access_token, validate_password_strength
from app.dependencies import get_current_user, require_role, verify_company_access, get_optional_current_user
from app.sms import notify_quote_approved, notify_quote_submitted, notify_booking_confirmed
from app import billing
from app import marketplace
from app import notifications
from app.variants import get_variants_for_item, get_variant_map_for_js
from app import ml_learning

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Staging mode configuration
STAGING_MODE = os.getenv("STAGING_MODE", "false").lower() == "true"

if STAGING_MODE:
    from app.staging_auth import security, verify_staging_auth
    logger.info("🔒 STAGING MODE ENABLED - Site is password protected")
else:
    # Dummy dependencies for when staging mode is disabled
    security = None
    verify_staging_auth = None

app = FastAPI(title="PrimeHaul OS", version="1.0.0")

# Trust Railway's proxy headers (X-Forwarded-Proto, X-Forwarded-For)
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Security: Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security: Add trusted host middleware (configure for production)
# Uncomment and configure for production:
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def resolve_and_check_company(request: Request, call_next):
    """
    Middleware to resolve company from URL and check subscription status
    Applies to customer survey URLs: /s/{company_slug}/{token}
    """
    # Extract path segments
    path_parts = request.url.path.strip('/').split('/')

    # Check if this is a customer survey URL: /s/{company_slug}/{token}
    if len(path_parts) >= 3 and path_parts[0] == 's':
        company_slug = path_parts[1]

        # Get database session
        db = next(get_db())
        try:
            # Find company by slug
            company = db.query(Company).filter(Company.slug == company_slug).first()

            if not company:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Company '{company_slug}' not found"}
                )

            # Check subscription status
            now = datetime.utcnow()

            # Trial expired?
            if company.subscription_status == 'trial' and company.trial_ends_at:
                # Make comparison timezone-naive safe
                trial_end = company.trial_ends_at.replace(tzinfo=None) if company.trial_ends_at.tzinfo else company.trial_ends_at
                if now > trial_end:
                    return templates.TemplateResponse("trial_expired.html", {
                        "request": request,
                        "company": company,
                        "company_slug": company_slug
                    })

            # Subscription required?
            if company.subscription_status not in ['trial', 'active', 'past_due']:
                return templates.TemplateResponse("subscription_expired.html", {
                    "request": request,
                    "company": company,
                    "company_slug": company_slug,
                    "status": company.subscription_status
                })

            # Attach company to request state
            request.state.company = company

            # Attach branding for template injection
            request.state.branding = {
                "company_name": company.company_name,
                "logo_url": company.logo_url or "/static/placeholder-photo.jpg",
                "primary_color": company.primary_color,
                "secondary_color": company.secondary_color
            }
        finally:
            db.close()

    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_or_create_job(company_id: uuid.UUID, token: str, db: Session) -> Job:
    """
    Get existing job or create new one

    Args:
        company_id: Company UUID
        token: Job token
        db: Database session

    Returns:
        Job object
    """
    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company_id
    ).first()

    if not job:
        job = Job(
            company_id=company_id,
            token=token,
            status='in_progress'
        )
        db.add(job)
        db.commit()
        db.refresh(job)

    return job


def staging_auth_required(credentials: HTTPBasicCredentials = Depends(security) if STAGING_MODE else None):
    """
    Dependency for routes that should be password-protected in staging mode
    """
    if STAGING_MODE and credentials:
        verify_staging_auth(credentials)
    return True


# ============================================================================
# MARKETING & LANDING PAGE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Main marketing landing page for primehaul.co.uk
    """
    return templates.TemplateResponse("landing_primehaul_uk.html", {"request": request})


@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms of Service page"""
    return templates.TemplateResponse("legal_terms.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy Policy page"""
    return templates.TemplateResponse("legal_privacy.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request, _auth: bool = Depends(staging_auth_required)):
    """
    Contact page
    Protected by password in staging mode
    """
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/trial", response_class=HTMLResponse)
async def trial_redirect(request: Request):
    """
    /trial URL redirects to signup (for marketing campaigns)
    """
    return RedirectResponse(url="/auth/signup", status_code=302)


@app.get("/tools/cbm-calculator", response_class=HTMLResponse)
async def cbm_calculator(request: Request):
    """
    Free CBM calculator tool (lead magnet)
    Drives organic traffic and generates leads
    """
    return templates.TemplateResponse("cbm_calculator.html", {"request": request})


@app.get("/dev/dashboard", response_class=HTMLResponse)
async def dev_dashboard(
    request: Request,
    password: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Developer mission control dashboard
    Password protected: Set DEV_DASHBOARD_PASSWORD in .env
    """
    # Simple password protection
    DEV_PASSWORD = os.getenv("DEV_DASHBOARD_PASSWORD", "dev2025")

    # Check password (via query param for simplicity)
    if password != DEV_PASSWORD:
        return HTMLResponse(content="""
            <html>
            <head>
                <style>
                    body {
                        background: #000;
                        color: #fff;
                        font-family: monospace;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .login-box {
                        background: #1a1a1a;
                        padding: 40px;
                        border-radius: 12px;
                        border: 1px solid #2ee59d;
                        text-align: center;
                    }
                    input {
                        background: #0a0a0a;
                        border: 1px solid #333;
                        color: #fff;
                        padding: 12px;
                        border-radius: 6px;
                        width: 250px;
                        margin: 20px 0;
                        font-size: 16px;
                    }
                    button {
                        background: #2ee59d;
                        color: #000;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        font-weight: 700;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <h1 style="color: #2ee59d; margin-bottom: 10px;">🔒 Dev Dashboard</h1>
                    <p style="color: #888; margin-bottom: 20px;">Enter password to access</p>
                    <form method="get">
                        <input type="password" name="password" placeholder="Password" autofocus required />
                        <br>
                        <button type="submit">Unlock Dashboard</button>
                    </form>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        Set DEV_DASHBOARD_PASSWORD in .env
                    </p>
                </div>
            </body>
            </html>
        """, status_code=401)

    # Calculate metrics
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Revenue metrics
    paying_customers = db.query(Company).filter(
        Company.subscription_status == 'active'
    ).count()

    active_trials = db.query(Company).filter(
        Company.subscription_status == 'trial',
        Company.trial_ends_at > now
    ).count()

    churned_customers = db.query(Company).filter(
        Company.subscription_status == 'canceled',
        Company.subscription_canceled_at >= month_ago
    ).count()

    total_companies = db.query(Company).count()

    # Calculate MRR (£99 per paying customer)
    mrr = paying_customers * 99
    arr = mrr * 12
    arpu = 99  # Fixed pricing

    # Trial conversion rate
    total_trials = db.query(Company).filter(
        Company.subscription_status.in_(['active', 'canceled']),
        Company.created_at >= month_ago - timedelta(days=30)  # Last 60 days for fair sample
    ).count()
    trial_conversion = round((paying_customers / max(total_trials, 1)) * 100, 1) if total_trials > 0 else 0

    # Churn rate
    churn_rate = round((churned_customers / max(paying_customers + churned_customers, 1)) * 100, 1)

    # System health
    db_status = True  # If we got here, DB is working
    stripe_webhook_status = True  # TODO: Check last webhook timestamp

    # Activity metrics
    total_jobs = db.query(Job).count()

    signups_today = db.query(Company).filter(
        Company.created_at >= today_start
    ).count()

    quotes_today = db.query(Job).filter(
        Job.created_at >= today_start
    ).count()

    submitted_today = db.query(Job).filter(
        Job.submitted_at >= today_start
    ).count()

    approved_today = db.query(Job).filter(
        Job.approved_at >= today_start
    ).count()

    photos_today = db.query(Photo).filter(
        Photo.created_at >= today_start
    ).count()

    # Marketing metrics (7 days)
    trial_signups_7d = db.query(Company).filter(
        Company.created_at >= week_ago
    ).count()

    landing_visits = 0  # TODO: Integrate Google Analytics
    signup_conversion = 0  # TODO: Calculate from analytics
    cac = 50  # Estimated

    # Launch checklist
    launch_checklist = [
        {
            "title": "Deploy to production",
            "action": "Heroku/Railway/Render setup",
            "done": os.getenv("APP_ENV") == "production",
            "priority": "high"
        },
        {
            "title": "Configure Stripe billing",
            "action": "Create product, set up webhooks",
            "done": bool(os.getenv("STRIPE_PRICE_ID")),
            "priority": "high"
        },
        {
            "title": "Set up PostgreSQL database",
            "action": "Run alembic upgrade head",
            "done": db_status,
            "priority": "high"
        },
        {
            "title": "Get first test trial",
            "action": "Create a test company signup",
            "done": total_companies > 0,
            "priority": "high"
        },
        {
            "title": "Build lead list (500 companies)",
            "action": "See LEAD_GEN_QUICK_START.md",
            "done": False,  # Manual check
            "priority": "high"
        },
        {
            "title": "Set up cold email (Lemlist)",
            "action": "Create account, import templates",
            "done": False,  # Manual check
            "priority": "high"
        },
        {
            "title": "Launch Google Ads (£300 budget)",
            "action": "Create campaign, see LEAD_GEN_QUICK_START.md",
            "done": False,  # Manual check
            "priority": "medium"
        },
        {
            "title": "Get 5 real trials",
            "action": "Cold email + LinkedIn + ads",
            "done": total_companies >= 5,
            "priority": "high"
        },
        {
            "title": "Get first paying customer",
            "action": "Follow up with trials",
            "done": paying_customers > 0,
            "priority": "high"
        },
        {
            "title": "Set up Google Analytics",
            "action": "Track landing page visits, signups",
            "done": False,  # Manual check
            "priority": "medium"
        },
    ]

    launch_progress_count = sum(1 for task in launch_checklist if task["done"])
    launch_total = len(launch_checklist)
    launch_progress_percent = round((launch_progress_count / launch_total) * 100)

    # Dynamic "What to do next" based on current state
    next_actions = []

    if total_companies == 0:
        next_actions.append({
            "text": "Create your first test company at /auth/signup",
            "priority": "high"
        })

    if paying_customers == 0:
        next_actions.append({
            "text": "Get your first paying customer! Follow LAUNCH_CHECKLIST.md",
            "priority": "high"
        })

    if total_companies < 5:
        next_actions.append({
            "text": "Launch lead generation: Send 100 cold emails",
            "priority": "high"
        })

    if trial_signups_7d == 0:
        next_actions.append({
            "text": "No signups this week - check your marketing campaigns",
            "priority": "high"
        })

    if active_trials > 0 and paying_customers == 0:
        next_actions.append({
            "text": f"You have {active_trials} active trials - follow up with them!",
            "priority": "high"
        })

    # Default actions if nothing urgent
    if not next_actions:
        next_actions = [
            {"text": "Review today's quotes and respond to customers", "priority": "medium"},
            {"text": "Check Stripe dashboard for payment issues", "priority": "medium"},
            {"text": "Write a blog post for SEO (see UK_LEAD_GENERATION_STRATEGY.md)", "priority": "low"},
            {"text": "Send LinkedIn connection requests (30/day)", "priority": "medium"},
        ]

    # Recent activity feed
    recent_activity = []

    # Get recent companies
    recent_companies = db.query(Company).order_by(Company.created_at.desc()).limit(5).all()
    for company in recent_companies:
        time_ago = _time_ago(company.created_at, now)
        recent_activity.append({
            "icon": "🎉",
            "text": f"New signup: {company.company_name}",
            "time": time_ago
        })

    # Get recent jobs
    recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
    for job in recent_jobs:
        time_ago = _time_ago(job.created_at, now)
        company = db.query(Company).filter(Company.id == job.company_id).first()
        if company:
            if job.approved_at:
                recent_activity.append({
                    "icon": "✅",
                    "text": f"{company.company_name}: Quote approved (£{job.custom_price_low or 0})",
                    "time": time_ago
                })
            elif job.submitted_at:
                recent_activity.append({
                    "icon": "📋",
                    "text": f"{company.company_name}: New quote submitted",
                    "time": time_ago
                })
            else:
                recent_activity.append({
                    "icon": "📝",
                    "text": f"{company.company_name}: Quote in progress",
                    "time": time_ago
                })

    # Sort by most recent
    recent_activity.sort(key=lambda x: x["time"])

    # Alerts
    alerts = []

    if paying_customers == 0 and total_companies > 5:
        alerts.append({
            "title": "Low Conversion Rate",
            "message": f"You have {total_companies} signups but 0 paying customers. Check your trial onboarding!"
        })

    if churn_rate > 15:
        alerts.append({
            "title": "High Churn Rate",
            "message": f"Churn rate is {churn_rate}% (target: <10%). Interview churned customers to understand why."
        })

    if not os.getenv("STRIPE_WEBHOOK_SECRET"):
        alerts.append({
            "title": "Stripe Webhooks Not Configured",
            "message": "Set STRIPE_WEBHOOK_SECRET in .env to handle subscription events."
        })

    # Marketplace metrics
    marketplace_stats = marketplace.get_marketplace_stats(db)

    return templates.TemplateResponse("dev_dashboard.html", {
        "request": request,
        "now": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "mrr": mrr,
        "arr": arr,
        "arpu": arpu,
        "paying_customers": paying_customers,
        "active_trials": active_trials,
        "churned_customers": churned_customers,
        "trial_conversion": trial_conversion,
        "churn_rate": churn_rate,
        "db_status": db_status,
        "stripe_webhook_status": stripe_webhook_status,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "signups_today": signups_today,
        "quotes_today": quotes_today,
        "submitted_today": submitted_today,
        "approved_today": approved_today,
        "photos_today": photos_today,
        "landing_visits": landing_visits,
        "trial_signups_7d": trial_signups_7d,
        "signup_conversion": signup_conversion,
        "cac": cac,
        "launch_checklist": launch_checklist,
        "launch_progress_count": launch_progress_count,
        "launch_total": launch_total,
        "launch_progress_percent": launch_progress_percent,
        "next_actions": next_actions,
        "recent_activity": recent_activity,
        "alerts": alerts,
        # Marketplace stats
        "marketplace_open_jobs": marketplace_stats.get("open_jobs", 0),
        "marketplace_total_bids": marketplace_stats.get("total_bids", 0),
        "marketplace_avg_bids": marketplace_stats.get("avg_bids_per_job", 0),
        "marketplace_jobs_awarded": marketplace_stats.get("jobs_awarded", 0),
        "marketplace_commission_pending": marketplace_stats.get("commission_pending", 0),
        "marketplace_commission_collected": marketplace_stats.get("commission_collected", 0),
    })


def _time_ago(dt, now):
    """Helper to format time ago"""
    if not dt:
        return "unknown"
    delta = now - dt
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return "just now"


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    return templates.TemplateResponse("auth_login.html", {
        "request": request
    })


@app.post("/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login and create JWT token"""
    # Find user by email
    user = db.query(User).filter(User.email == email, User.is_active == True).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("auth_login.html", {
            "request": request,
            "error": "Invalid email or password"
        })

    # Check company subscription status
    company = user.company
    if company.subscription_status not in ['trial', 'active']:
        return templates.TemplateResponse("auth_login.html", {
            "request": request,
            "error": "Your subscription has expired. Please contact support."
        })

    # Create JWT token
    token = create_access_token(str(user.id), str(user.company_id))

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Redirect to company dashboard
    response = RedirectResponse(url=f"/{company.slug}/admin/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400  # 24 hours
    )

    return response


@app.get("/auth/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Show signup page"""
    return templates.TemplateResponse("auth_signup.html", {
        "request": request
    })


@app.post("/auth/signup")
async def signup(
    request: Request,
    company_name: str = Form(...),
    slug: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    phone: Optional[str] = Form(None),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process signup and create company + owner account"""

    # Validate password confirmation
    if password != password_confirm:
        return templates.TemplateResponse("auth_signup.html", {
            "request": request,
            "error": "Passwords do not match",
            "company_name": company_name,
            "slug": slug,
            "email": email,
            "full_name": full_name,
            "phone": phone
        })

    # Validate password strength
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        return templates.TemplateResponse("auth_signup.html", {
            "request": request,
            "error": error_msg,
            "company_name": company_name,
            "slug": slug,
            "email": email,
            "full_name": full_name,
            "phone": phone
        })

    # Check if slug is already taken
    existing_company = db.query(Company).filter(Company.slug == slug).first()
    if existing_company:
        return templates.TemplateResponse("auth_signup.html", {
            "request": request,
            "error": "Company name already taken. Please try a different name.",
            "company_name": company_name,
            "email": email,
            "full_name": full_name,
            "phone": phone
        })

    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("auth_signup.html", {
            "request": request,
            "error": "This email is already registered. Please login instead.",
            "company_name": company_name,
            "slug": slug,
            "full_name": full_name,
            "phone": phone
        })

    # Create company with 14-day trial
    trial_ends_at = datetime.utcnow() + timedelta(days=14)
    company = Company(
        company_name=company_name,
        slug=slug,
        email=email,
        phone=phone,
        subscription_status='trial',
        trial_ends_at=trial_ends_at,
        is_active=True,
        onboarding_completed=False
    )
    db.add(company)
    db.flush()  # Get company.id

    # Create owner user
    password_hash = hash_password(password)
    owner = User(
        company_id=company.id,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role='owner',
        is_active=True,
        email_verified=False
    )
    db.add(owner)

    # Create default pricing config
    default_pricing = PricingConfig(
        company_id=company.id,
        price_per_cbm=35.00,
        callout_fee=250.00,
        bulky_item_fee=25.00,
        fragile_item_fee=15.00,
        weight_threshold_kg=1000,
        price_per_kg_over_threshold=0.50,
        estimate_low_multiplier=0.90,
        estimate_high_multiplier=1.20
    )
    db.add(default_pricing)

    db.commit()

    logger.info(f"New company registered: {company_name} (slug: {slug})")

    # Create JWT token and login
    token = create_access_token(str(owner.id), str(company.id))

    # Redirect to dashboard with welcome message
    response = RedirectResponse(url=f"/{company.slug}/admin/dashboard?welcome=true", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400  # 24 hours
    )

    return response


@app.post("/auth/logout")
async def logout():
    """Logout and clear authentication cookie"""
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


# ============================================================================
# SUPERADMIN DASHBOARD - Platform owner control center
# ============================================================================

SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "primehaul2026")


def verify_superadmin(request: Request) -> bool:
    """Check if user has superadmin access"""
    token = request.cookies.get("superadmin_token")
    return token == "superadmin_authenticated"


@app.get("/superadmin", response_class=HTMLResponse)
@app.get("/superadmin/", response_class=HTMLResponse)
def superadmin_redirect():
    """Redirect to login"""
    return RedirectResponse(url="/superadmin/login", status_code=303)


@app.get("/superadmin/login", response_class=HTMLResponse)
def superadmin_login_page(request: Request, error: str = None):
    """Superadmin login page"""
    if verify_superadmin(request):
        return RedirectResponse(url="/superadmin/dashboard", status_code=303)
    return templates.TemplateResponse("superadmin_login.html", {"request": request, "error": error})


@app.post("/superadmin/login")
def superadmin_login(request: Request, password: str = Form(...)):
    """Validate superadmin password"""
    if password == SUPERADMIN_PASSWORD:
        response = RedirectResponse(url="/superadmin/dashboard", status_code=303)
        response.set_cookie("superadmin_token", "superadmin_authenticated", httponly=True, secure=True, max_age=86400)
        return response
    return RedirectResponse(url="/superadmin/login?error=Invalid+password", status_code=303)


@app.get("/superadmin/logout")
def superadmin_logout():
    """Logout superadmin"""
    response = RedirectResponse(url="/superadmin/login", status_code=303)
    response.delete_cookie("superadmin_token")
    return response


@app.get("/superadmin/dashboard", response_class=HTMLResponse)
def superadmin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Superadmin dashboard with all platform data"""
    if not verify_superadmin(request):
        return RedirectResponse(url="/superadmin/login", status_code=303)

    from datetime import datetime, timedelta

    try:
        # Get all companies
        companies = db.query(Company).order_by(Company.created_at.desc()).all()

        # Calculate stats
        total_surveys = db.query(func.sum(Company.surveys_used)).scalar() or 0
        total_items = db.query(Item).count()
        total_photos = db.query(Photo).count()
        ml_corrections = db.query(ItemFeedback).count()
        surveys_today = db.query(Job).filter(
            Job.submitted_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()

        # Revenue estimate (surveys beyond free tier * £9.99)
        revenue_total = 0
        for c in companies:
            is_partner = getattr(c, 'is_partner', False) or False
            if not is_partner:
                paid_surveys = max(0, (c.surveys_used or 0) - 3)
                revenue_total += paid_surveys * 9.99

        stats = {
            "total_companies": len(companies),
            "total_surveys": total_surveys,
            "total_items": total_items,
            "ml_corrections": ml_corrections,
            "surveys_today": surveys_today,
            "revenue_total": revenue_total
        }

        # ML training data stats
        ml_stats = {
            "total_photos": total_photos,
            "total_items": total_items,
            "corrections": db.query(ItemFeedback).filter(ItemFeedback.feedback_type == 'correction').count(),
            "variant_changes": db.query(ItemFeedback).filter(ItemFeedback.feedback_type == 'variant_change').count()
        }

        # Database stats
        db_stats = {
            "jobs": db.query(Job).count(),
            "rooms": db.query(Room).count(),
            "photos": total_photos,
            "items": total_items,
            "feedback": ml_corrections,
            "analytics": db.query(UsageAnalytics).count()
        }

        # Recent activity (last 20 analytics events)
        recent_events = db.query(UsageAnalytics).order_by(UsageAnalytics.recorded_at.desc()).limit(20).all()
        recent_activity = []
        for event in recent_events:
            company = db.query(Company).filter(Company.id == event.company_id).first()
            time_diff = datetime.utcnow() - event.recorded_at.replace(tzinfo=None)
            if time_diff.days > 0:
                time_ago = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                time_ago = f"{time_diff.seconds // 3600}h ago"
            else:
                time_ago = f"{time_diff.seconds // 60}m ago"

            recent_activity.append({
                "event_type": event.event_type,
                "company_name": company.company_name if company else "Unknown",
                "time_ago": time_ago,
                "metadata": str(event.metadata)[:100] if event.metadata else None
            })

        # Recent ML feedback (last 30 corrections/changes)
        recent_feedback_records = db.query(ItemFeedback).order_by(ItemFeedback.created_at.desc()).limit(30).all()
        recent_feedback = []
        for fb in recent_feedback_records:
            company = db.query(Company).filter(Company.id == fb.company_id).first()
            time_diff = datetime.utcnow() - fb.created_at.replace(tzinfo=None)
            if time_diff.days > 0:
                time_ago = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                time_ago = f"{time_diff.seconds // 3600}h ago"
            else:
                time_ago = f"{time_diff.seconds // 60}m ago"

            recent_feedback.append({
                "feedback_type": fb.feedback_type or "unknown",
                "ai_detected": fb.ai_detected_name or "—",
                "corrected_to": fb.corrected_name or "—",
                "company_name": company.company_name if company else "Unknown",
                "time_ago": time_ago,
                "notes": fb.notes[:80] if fb.notes else None
            })

        return templates.TemplateResponse("superadmin_dashboard.html", {
            "request": request,
            "companies": companies,
            "stats": stats,
            "ml_stats": ml_stats,
            "db_stats": db_stats,
            "recent_activity": recent_activity,
            "recent_feedback": recent_feedback
        })

    except Exception as e:
        logger.error(f"Superadmin dashboard error: {str(e)}")
        return HTMLResponse(f"<h1>Dashboard Error</h1><pre>{str(e)}</pre><p><a href='/superadmin/logout'>Logout</a></p>", status_code=500)


@app.post("/superadmin/make-partner/{company_slug}")
def make_partner(request: Request, company_slug: str, partner_name: str = Form(...), db: Session = Depends(get_db)):
    """Make a company a partner (unlimited free surveys)"""
    if not verify_superadmin(request):
        return RedirectResponse(url="/superadmin/login", status_code=303)

    company = db.query(Company).filter(Company.slug == company_slug).first()
    if company:
        company.is_partner = True
        company.partner_name = partner_name
        db.commit()
        logger.info(f"Made {company_slug} a partner: {partner_name}")

    return RedirectResponse(url="/superadmin/dashboard", status_code=303)


@app.get("/superadmin/learning")
def superadmin_learning(request: Request, db: Session = Depends(get_db)):
    """View ML learning stats and learned patterns"""
    if not verify_superadmin(request):
        return RedirectResponse(url="/superadmin/login", status_code=303)

    try:
        learning_stats = ml_learning.get_learning_stats(db)
        return templates.TemplateResponse("superadmin_learning.html", {
            "request": request,
            "stats": learning_stats
        })
    except Exception as e:
        logger.error(f"Superadmin learning error: {str(e)}")
        return HTMLResponse(f"<h1>Learning Error</h1><pre>{str(e)}</pre><p><a href='/superadmin/dashboard'>Back</a></p>", status_code=500)


@app.post("/superadmin/run-learning")
def superadmin_run_learning(request: Request, db: Session = Depends(get_db)):
    """Manually trigger a learning cycle"""
    if not verify_superadmin(request):
        return RedirectResponse(url="/superadmin/login", status_code=303)

    try:
        result = ml_learning.run_learning_cycle(db)
        logger.info(f"Manual learning cycle completed: {result}")
        return RedirectResponse(url="/superadmin/learning?success=true", status_code=303)
    except Exception as e:
        logger.error(f"Manual learning cycle error: {str(e)}")
        return RedirectResponse(url=f"/superadmin/learning?error={str(e)}", status_code=303)


@app.post("/superadmin/fix-survey-counts")
def superadmin_fix_survey_counts(request: Request, db: Session = Depends(get_db)):
    """
    One-time fix: Count submitted jobs and update surveys_used for each company.
    This fixes historical data from before the counter was implemented.
    """
    if not verify_superadmin(request):
        return RedirectResponse(url="/superadmin/login", status_code=303)

    try:
        companies = db.query(Company).all()
        fixed = 0

        for company in companies:
            # Count jobs that have been submitted (not in_progress)
            submitted_count = db.query(Job).filter(
                Job.company_id == company.id,
                Job.status.in_(['awaiting_approval', 'approved', 'rejected', 'completed', 'accepted'])
            ).count()

            if submitted_count > 0:
                old_count = company.surveys_used or 0
                company.surveys_used = submitted_count

                # Also fix free_surveys_remaining
                used_free = min(submitted_count, 3)
                company.free_surveys_remaining = max(0, 3 - used_free)

                if old_count != submitted_count:
                    fixed += 1
                    logger.info(f"Fixed {company.slug}: {old_count} → {submitted_count} surveys")

        db.commit()
        logger.info(f"Survey count fix complete: {fixed} companies updated")
        return RedirectResponse(url=f"/superadmin/dashboard?fixed={fixed}", status_code=303)

    except Exception as e:
        logger.error(f"Survey count fix error: {str(e)}")
        return RedirectResponse(url=f"/superadmin/dashboard?error={str(e)}", status_code=303)


# ============================================================================
# CUSTOMER SURVEY ENDPOINTS
# ============================================================================


@app.get("/s/{company_slug}/{token}", response_class=HTMLResponse)
def survey_start(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Start customer survey"""
    from datetime import date
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("start_v2.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Get Quote - {company.company_name}",
        "nav_title": "Get Quote",
        "back_url": None,
        "progress": 10,
        "mapbox_token": os.getenv("MAPBOX_ACCESS_TOKEN", ""),
        "job": job,
        "today": date.today().isoformat()
    })


@app.post("/s/{company_slug}/{token}/start")
def survey_start_post(company_slug: str, token: str):
    """Proceed to location selection"""
    return RedirectResponse(url=f"/s/{company_slug}/{token}/move", status_code=303)


# ----------------------------
# STREAMLINED V2 FLOW (Combined Address + Property)
# ----------------------------

@app.get("/s/{company_slug}/{token}/start-v2", response_class=HTMLResponse)
def start_v2_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """New streamlined start page - combines addresses + property type"""
    from datetime import date
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("start_v2.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Get Quote - {company.company_name}",
        "nav_title": "Get Quote",
        "back_url": None,
        "progress": 10,
        "mapbox_token": os.getenv("MAPBOX_ACCESS_TOKEN", ""),
        "job": job,
        "today": date.today().isoformat()
    })


@app.post("/s/{company_slug}/{token}/start-v2")
def start_v2_post(
    request: Request,
    company_slug: str,
    token: str,
    pickup_label: str = Form(...),
    pickup_lat: str = Form(...),
    pickup_lng: str = Form(...),
    dropoff_label: str = Form(...),
    dropoff_lat: str = Form(...),
    dropoff_lng: str = Form(...),
    property_type: str = Form(...),
    move_date: str = Form(""),
    db: Session = Depends(get_db)
):
    """Save all data from streamlined start page"""
    from datetime import datetime

    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Save addresses (with fallback for empty coordinates)
    try:
        pickup_lat_val = float(pickup_lat) if pickup_lat else 0.0
        pickup_lng_val = float(pickup_lng) if pickup_lng else 0.0
        dropoff_lat_val = float(dropoff_lat) if dropoff_lat else 0.0
        dropoff_lng_val = float(dropoff_lng) if dropoff_lng else 0.0
    except (ValueError, TypeError):
        pickup_lat_val = pickup_lng_val = dropoff_lat_val = dropoff_lng_val = 0.0

    job.pickup = {"label": pickup_label, "lat": pickup_lat_val, "lng": pickup_lng_val}
    job.dropoff = {"label": dropoff_label, "lat": dropoff_lat_val, "lng": dropoff_lng_val}

    # Save property type
    job.property_type = property_type

    # Save move date if provided
    if move_date:
        try:
            job.move_date = datetime.strptime(move_date, "%Y-%m-%d")
        except:
            pass  # Skip if invalid date

    db.commit()

    # Always go to access questions - even studios/1-beds can have difficult access
    return RedirectResponse(url=f"/s/{company_slug}/{token}/access", status_code=303)


@app.get("/s/{company_slug}/{token}/move", response_class=HTMLResponse)
def move_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Location selection page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("move_map.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Set your move - {company.company_name}",
        "nav_title": "Set your move",
        "back_url": f"/s/{company_slug}/{token}",
        "progress": 25,
        "mapbox_token": os.getenv("MAPBOX_ACCESS_TOKEN", ""),
        "pickup": job.pickup,
        "dropoff": job.dropoff,
    })


@app.post("/s/{company_slug}/{token}/move")
def move_post(
    request: Request,
    company_slug: str,
    token: str,
    pickup_label: str = Form(""),
    pickup_lat: str = Form(""),
    pickup_lng: str = Form(""),
    dropoff_label: str = Form(""),
    dropoff_lat: str = Form(""),
    dropoff_lng: str = Form(""),
    db: Session = Depends(get_db)
):
    """Save location data"""
    if not (pickup_label and pickup_lat and pickup_lng and dropoff_label and dropoff_lat and dropoff_lng):
        return RedirectResponse(url=f"/s/{company_slug}/{token}/move?err=missing", status_code=303)

    try:
        p_lat = float(pickup_lat); p_lng = float(pickup_lng)
        d_lat = float(dropoff_lat); d_lng = float(dropoff_lng)
    except ValueError:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/move?err=coords", status_code=303)

    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    job.pickup = {"label": pickup_label, "lat": p_lat, "lng": p_lng}
    job.dropoff = {"label": dropoff_label, "lat": d_lat, "lng": d_lng}
    db.commit()

    return RedirectResponse(url=f"/s/{company_slug}/{token}/property", status_code=303)


@app.get("/s/{company_slug}/{token}/property", response_class=HTMLResponse)
def property_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Property type selection page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("property_type.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Property - {company.company_name}",
        "nav_title": "Property",
        "back_url": f"/s/{company_slug}/{token}/move",
        "progress": 50,
        "property_type": job.property_type,
    })


@app.post("/s/{company_slug}/{token}/property")
def property_post(
    request: Request,
    company_slug: str,
    token: str,
    property_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save property type"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    job.property_type = property_type
    db.commit()
    return RedirectResponse(url=f"/s/{company_slug}/{token}/access", status_code=303)


# ----------------------------
# ACCESS QUESTIONS
# ----------------------------

@app.get("/s/{company_slug}/{token}/access", response_class=HTMLResponse)
def access_questions_get(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Display access difficulty questions for pickup and dropoff"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("access_questions.html", {
        "request": request,
        "company_slug": company_slug,
        "token": token,
        "branding": request.state.branding,
        "title": f"Access Details - {company.company_name}",
        "nav_title": "Access Details",
        "back_url": f"/s/{company_slug}/{token}/property",
        "progress": 30,
        "job": job,
        "pickup_access": job.pickup_access or {},
        "dropoff_access": job.dropoff_access or {}
    })


@app.post("/s/{company_slug}/{token}/access")
def access_questions_post(
    request: Request,
    company_slug: str,
    token: str,
    # Pickup fields
    pickup_floors: int = Form(...),
    pickup_has_lift: str = Form(...),
    pickup_parking_type: str = Form(...),
    pickup_parking_distance: int = Form(0),
    pickup_restrictions: list = Form([]),
    pickup_outdoor_access: str = Form("direct"),
    pickup_outdoor_steps: int = Form(0),
    pickup_notes: str = Form(""),
    # Dropoff fields
    dropoff_floors: int = Form(...),
    dropoff_has_lift: str = Form(...),
    dropoff_parking_type: str = Form(...),
    dropoff_parking_distance: int = Form(0),
    dropoff_restrictions: list = Form([]),
    dropoff_outdoor_access: str = Form("direct"),
    dropoff_outdoor_steps: int = Form(0),
    dropoff_notes: str = Form(""),
    db: Session = Depends(get_db)
):
    """Save access difficulty parameters"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Construct pickup access JSON
    job.pickup_access = {
        "floors": pickup_floors,
        "has_lift": pickup_has_lift == "yes",
        "parking_type": pickup_parking_type,
        "parking_distance_meters": pickup_parking_distance,
        "building_restrictions": pickup_restrictions if isinstance(pickup_restrictions, list) else [pickup_restrictions] if pickup_restrictions else [],
        "outdoor_access": pickup_outdoor_access,
        "outdoor_steps": pickup_outdoor_steps,
        "notes": pickup_notes.strip()
    }

    # Construct dropoff access JSON
    job.dropoff_access = {
        "floors": dropoff_floors,
        "has_lift": dropoff_has_lift == "yes",
        "parking_type": dropoff_parking_type,
        "parking_distance_meters": dropoff_parking_distance,
        "building_restrictions": dropoff_restrictions if isinstance(dropoff_restrictions, list) else [dropoff_restrictions] if dropoff_restrictions else [],
        "outdoor_access": dropoff_outdoor_access,
        "outdoor_steps": dropoff_outdoor_steps,
        "notes": dropoff_notes.strip()
    }

    db.commit()

    return RedirectResponse(url=f"/s/{company_slug}/{token}/move-date", status_code=303)


# ----------------------------
# MOVE DATE
# ----------------------------

@app.get("/s/{company_slug}/{token}/move-date", response_class=HTMLResponse)
def move_date_get(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Show move date selection"""
    from datetime import date
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("move_date.html", {
        "request": request,
        "company_slug": company_slug,
        "token": token,
        "job": job,
        "today": date.today().isoformat()
    })


@app.post("/s/{company_slug}/{token}/move-date")
def move_date_post(
    request: Request,
    company_slug: str,
    token: str,
    move_date: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save move date"""
    from datetime import datetime
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Parse the date string (YYYY-MM-DD) to datetime
    job.move_date = datetime.strptime(move_date, '%Y-%m-%d')
    db.commit()

    # If job is approved (post-quote flow), go to deposit/booking
    # Otherwise go to rooms (initial survey flow)
    if job.status == 'approved':
        return RedirectResponse(url=f"/s/{company_slug}/{token}/deposit", status_code=303)
    else:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/rooms", status_code=303)


# ----------------------------
# ROOMS (tap to add)
# ----------------------------

@app.get("/s/{company_slug}/{token}/rooms", response_class=HTMLResponse)
def rooms_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Rooms selection page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get all rooms for this job
    rooms = db.query(Room).filter(Room.job_id == job.id).all()

    return templates.TemplateResponse("rooms_pick.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Rooms - {company.company_name}",
        "nav_title": "Rooms",
        "back_url": f"/s/{company_slug}/{token}/property",
        "progress": 65,
        "rooms": rooms,
    })


@app.post("/s/{company_slug}/{token}/rooms/add")
def rooms_add(
    request: Request,
    company_slug: str,
    token: str,
    room_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Add a new room"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Create new room
    room = Room(
        job_id=job.id,
        name=room_name
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # Immediately go to scan items for this room
    return RedirectResponse(url=f"/s/{company_slug}/{token}/room/{room.id}", status_code=303)


# ----------------------------
# SCAN ITEMS (photos per room)
# ----------------------------

@app.get("/s/{company_slug}/{token}/room/{room_id}", response_class=HTMLResponse)
def room_scan_get(request: Request, company_slug: str, token: str, room_id: str, db: Session = Depends(get_db)):
    """Room photo scanning page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get room
    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/rooms", status_code=303)

    # Get items and photos for this room
    items = db.query(Item).filter(Item.room_id == room.id).all()
    photos = db.query(Photo).filter(Photo.room_id == room.id).all()

    # Build items_json for template (include variant options per item)
    items_json = {
        "items": [{
            "name": item.name,
            "qty": item.qty,
            "notes": item.notes or "",
            "bulky": item.bulky,
            "fragile": item.fragile,
            "length_cm": float(item.length_cm) if item.length_cm else None,
            "width_cm": float(item.width_cm) if item.width_cm else None,
            "height_cm": float(item.height_cm) if item.height_cm else None,
            "weight_kg": float(item.weight_kg) if item.weight_kg else None,
            "cbm": float(item.cbm) if item.cbm else None,
            "variants": [v["name"] for v in (get_variants_for_item(item.name) or [])],
        } for item in items],
        "summary": room.summary or ""
    }

    # Build photos list for template
    photos_list = [{"filename": p.filename, "url": f"/static/{p.storage_path}"} for p in photos]

    # Variant map for client-side matching after AJAX photo uploads
    variant_map_js = get_variant_map_for_js()

    return templates.TemplateResponse("room_scan.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"{room.name} - {company.company_name}",
        "nav_title": room.name,
        "back_url": f"/s/{company_slug}/{token}/rooms",
        "progress": 75,
        "room_id": str(room.id),
        "room_name": room.name,
        "photos": photos_list,
        "items_json": items_json,
        "variant_map_js": variant_map_js,
    })


@app.post("/s/{company_slug}/{token}/room/{room_id}/upload")
async def room_scan_upload(
    request: Request,
    company_slug: str,
    token: str,
    room_id: str,
    photos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    """Upload and analyze photos for a room"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get room
    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/rooms", status_code=303)

    if not photos:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/room/{room_id}?err=no_photos", status_code=303)

    # Create company-specific upload directory
    company_upload_dir = UPLOAD_DIR / str(company.id) / token
    company_upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded photos and track paths for AI analysis
    saved_paths = []
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic", "image/heif"}

    for f in photos:
        # Validate file type
        if f.content_type not in ALLOWED_TYPES:
            logger.warning(f"Rejected file with invalid type: {f.content_type}")
            continue

        # Generate unique filename
        ext = os.path.splitext(f.filename or "photo.jpg")[1] or ".jpg"
        fname = f"{uuid.uuid4().hex[:12]}{ext}"
        file_path = company_upload_dir / fname

        # Save file with size validation
        try:
            content = await f.read()
            if len(content) > MAX_FILE_SIZE:
                logger.warning(f"File {f.filename} exceeds size limit")
                continue

            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(content)

            saved_paths.append(str(file_path))

            # Save photo record to database
            storage_path = f"uploads/{company.id}/{token}/{fname}"
            photo = Photo(
                room_id=room.id,
                filename=fname,
                original_filename=f.filename,
                file_size_bytes=len(content),
                mime_type=f.content_type,
                storage_path=storage_path
            )
            db.add(photo)
            logger.info(f"Saved photo: {fname}")
        except Exception as e:
            logger.error(f"Error saving photo {f.filename}: {e}")
            continue

    db.commit()

    # Use AI to analyze photos and extract inventory
    if saved_paths:
        try:
            # 🧠 SELF-LEARNING: Get learned patterns to enhance AI prompt
            learned_guidance = None
            try:
                learned_guidance = ml_learning.get_learned_patterns_for_prompt(db)
                if learned_guidance:
                    logger.info("Injecting learned patterns into AI prompt")
            except Exception as e:
                logger.warning(f"Could not get learned patterns: {e}")

            logger.info(f"Analyzing {len(saved_paths)} photos with AI vision...")
            inventory = extract_removal_inventory(saved_paths, learned_guidance=learned_guidance)

            # 🧠 SELF-LEARNING: Apply learned corrections to AI detections (backup)
            if inventory.get("items"):
                try:
                    inventory["items"], corrections = ml_learning.apply_learned_corrections(inventory["items"], db)
                    if corrections:
                        logger.info(f"Auto-applied {len(corrections)} learned corrections")
                except Exception as e:
                    logger.warning(f"Could not apply learned corrections: {e}")

            # Store structured items
            if inventory.get("items"):
                created_items = []
                for item_data in inventory["items"]:
                    weight_kg = item_data.get("weight_kg")
                    item = Item(
                        room_id=room.id,
                        name=item_data.get("name", "Unknown item"),
                        qty=item_data.get("qty", 1),
                        notes=item_data.get("notes", ""),
                        length_cm=item_data.get("length_cm"),
                        width_cm=item_data.get("width_cm"),
                        height_cm=item_data.get("height_cm"),
                        weight_kg=weight_kg,
                        cbm=item_data.get("cbm"),
                        bulky=(float(weight_kg) > 50) if weight_kg else False,
                        fragile=item_data.get("fragile", False),
                        item_category=item_data.get("item_category", "furniture"),
                        packing_requirement=item_data.get("packing_requirement", "none")
                    )
                    db.add(item)
                    created_items.append((item, item_data))

                # Update room summary
                if inventory.get("summary"):
                    room.summary = inventory.get("summary", "")

                db.commit()
                logger.info(f"AI detected {len(inventory['items'])} items")

                # 🎓 AUTO-LEARN: Save OpenAI detections as training data
                for item, item_data in created_items:
                    try:
                        # Only save if we have dimensions (good training data)
                        if item.length_cm and item.width_cm and item.height_cm:
                            training_entry = TrainingDataset(
                                id=uuid.uuid4(),
                                image_url=saved_paths[0] if saved_paths else None,
                                image_hash=None,
                                item_name=item.name,
                                item_category=item.item_category or "furniture",
                                length_cm=item.length_cm,
                                width_cm=item.width_cm,
                                height_cm=item.height_cm,
                                cbm=item.cbm,
                                weight_kg=item.weight_kg,
                                is_bulky=item.bulky,
                                is_fragile=item.fragile,
                                packing_requirement=item.packing_requirement,
                                source_type='openai_live',  # Live detection
                                source_id=item.id,
                                confidence_score=0.85,  # OpenAI is reliable
                                verified=False,  # Not yet verified by admin
                                used_in_training=False
                            )
                            db.add(training_entry)
                    except Exception as e:
                        logger.warning(f"Could not save training data for item: {e}")

                db.commit()
                logger.info(f"💡 Saved {len(created_items)} OpenAI detections to training dataset")

                # Track analytics event
                photo_count = len(photos)
                ai_cost = photo_count * 0.003  # Approximate $0.003 per image
                track_event(
                    company_id=company.id,
                    event_type='photo_analyzed',
                    metadata={
                        'job_token': token,
                        'room_id': str(room_id),
                        'photo_count': photo_count,
                        'items_detected': len(inventory['items'])
                    },
                    ai_cost_usd=ai_cost,
                    db=db
                )
            else:
                logger.warning("AI returned no items")

        except Exception as e:
            logger.error(f"AI vision error: {e}")

    return RedirectResponse(url=f"/s/{company_slug}/{token}/room/{room_id}?saved=1", status_code=303)


@app.post("/s/{company_slug}/{token}/room/{room_id}/upload-json")
async def room_scan_upload_json(
    request: Request,
    company_slug: str,
    token: str,
    room_id: str,
    photos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    """JSON version of upload endpoint for AJAX calls"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get room
    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return JSONResponse({"ok": False, "error": "Room not found"}, status_code=404)

    if not photos:
        return JSONResponse({"ok": False, "error": "No photos provided"}, status_code=400)

    # Create company-specific upload directory
    company_upload_dir = UPLOAD_DIR / str(company.id) / token
    company_upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded photos and track paths for AI analysis
    saved_paths = []
    photo_records = []
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/webp", "image/heic", "image/heif"}

    for f in photos:
        # Validate file type
        if f.content_type not in ALLOWED_TYPES:
            logger.warning(f"Rejected file with invalid type: {f.content_type}")
            continue

        # Generate unique filename
        ext = os.path.splitext(f.filename or "photo.jpg")[1] or ".jpg"
        fname = f"{uuid.uuid4().hex[:12]}{ext}"
        file_path = company_upload_dir / fname

        # Save file with size validation
        try:
            content = await f.read()
            if len(content) > MAX_FILE_SIZE:
                logger.warning(f"File {f.filename} exceeds size limit")
                continue

            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(content)

            saved_paths.append(str(file_path))

            # Save photo record to database
            storage_path = f"uploads/{company.id}/{token}/{fname}"
            photo = Photo(
                room_id=room.id,
                filename=fname,
                original_filename=f.filename,
                file_size_bytes=len(content),
                mime_type=f.content_type,
                storage_path=storage_path
            )
            db.add(photo)
            photo_records.append({"filename": fname, "url": f"/static/{storage_path}"})
            logger.info(f"Saved photo: {fname}")
        except Exception as e:
            logger.error(f"Error saving photo {f.filename}: {e}")
            continue

    db.commit()

    # Use AI to analyze photos and extract inventory
    items_list = []
    if saved_paths:
        try:
            # 🧠 SELF-LEARNING: Get learned patterns to enhance AI prompt
            learned_guidance = None
            try:
                learned_guidance = ml_learning.get_learned_patterns_for_prompt(db)
                if learned_guidance:
                    logger.info("Injecting learned patterns into AI prompt")
            except Exception as e:
                logger.warning(f"Could not get learned patterns: {e}")

            logger.info(f"Analyzing {len(saved_paths)} photos with AI vision...")
            inventory = extract_removal_inventory(saved_paths, learned_guidance=learned_guidance)

            # 🧠 SELF-LEARNING: Apply learned corrections to AI detections (backup)
            if inventory.get("items"):
                try:
                    inventory["items"], corrections = ml_learning.apply_learned_corrections(inventory["items"], db)
                    if corrections:
                        logger.info(f"Auto-applied {len(corrections)} learned corrections")
                except Exception as e:
                    logger.warning(f"Could not apply learned corrections: {e}")

            # Store structured items
            if inventory.get("items"):
                created_items = []
                for item_data in inventory["items"]:
                    weight_kg = item_data.get("weight_kg")
                    item = Item(
                        room_id=room.id,
                        name=item_data.get("name", "Unknown item"),
                        qty=item_data.get("qty", 1),
                        notes=item_data.get("notes", ""),
                        length_cm=item_data.get("length_cm"),
                        width_cm=item_data.get("width_cm"),
                        height_cm=item_data.get("height_cm"),
                        weight_kg=weight_kg,
                        cbm=item_data.get("cbm"),
                        bulky=(float(weight_kg) > 50) if weight_kg else False,
                        fragile=item_data.get("fragile", False),
                        item_category=item_data.get("item_category", "furniture"),
                        packing_requirement=item_data.get("packing_requirement", "none")
                    )
                    db.add(item)
                    items_list.append(item_data)
                    created_items.append((item, item_data))

                # Update room summary
                if inventory.get("summary"):
                    room.summary = inventory.get("summary", "")

                db.commit()
                logger.info(f"AI detected {len(inventory['items'])} items")

                # 🎓 AUTO-LEARN: Save OpenAI detections as training data
                for item, item_data in created_items:
                    try:
                        if item.length_cm and item.width_cm and item.height_cm:
                            training_entry = TrainingDataset(
                                id=uuid.uuid4(),
                                image_url=saved_paths[0] if saved_paths else None,
                                item_name=item.name,
                                item_category=item.item_category or "furniture",
                                length_cm=item.length_cm,
                                width_cm=item.width_cm,
                                height_cm=item.height_cm,
                                cbm=item.cbm,
                                weight_kg=item.weight_kg,
                                is_bulky=item.bulky,
                                is_fragile=item.fragile,
                                packing_requirement=item.packing_requirement,
                                source_type='openai_live',
                                source_id=item.id,
                                confidence_score=0.85,
                                verified=False,
                                used_in_training=False
                            )
                            db.add(training_entry)
                    except Exception as e:
                        logger.warning(f"Could not save training data: {e}")
                db.commit()

        except Exception as e:
            logger.error(f"AI vision error: {e}")

    # Return JSON response
    return JSONResponse({
        "ok": True,
        "photos": photo_records,
        "items_json": {
            "items": items_list,
            "summary": room.summary or ""
        }
    })


@app.delete("/s/{company_slug}/{token}/room/{room_id}/delete-item/{item_index}")
def delete_room_item(
    request: Request,
    company_slug: str,
    token: str,
    room_id: str,
    item_index: int,
    db: Session = Depends(get_db)
):
    """Delete a specific item from a room by index"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get room
    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return JSONResponse({"error": "Room not found"}, status_code=404)

    # Get all items for this room
    items = db.query(Item).filter(Item.room_id == room.id).order_by(Item.id).all()

    # Validate index
    if item_index < 0 or item_index >= len(items):
        return JSONResponse({"error": "Invalid item index"}, status_code=400)

    # Delete the item at this index
    item_to_delete = items[item_index]
    db.delete(item_to_delete)
    db.commit()

    logger.info(f"Deleted item '{item_to_delete.name}' from room {room.name} (job {token})")

    return JSONResponse({"success": True, "message": "Item deleted"})


@app.post("/s/{company_slug}/{token}/room/{room_id}/increment-item/{item_index}")
def increment_room_item(
    request: Request,
    company_slug: str,
    token: str,
    room_id: str,
    item_index: int,
    db: Session = Depends(get_db)
):
    """Increment quantity of a specific item by 1"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Get room
    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return JSONResponse({"error": "Room not found"}, status_code=404)

    # Get all items for this room
    items = db.query(Item).filter(Item.room_id == room.id).order_by(Item.id).all()

    # Validate index
    if item_index < 0 or item_index >= len(items):
        return JSONResponse({"error": "Invalid item index"}, status_code=400)

    # Increment the item quantity
    item = items[item_index]
    item.qty = (item.qty or 1) + 1
    db.commit()

    logger.info(f"Incremented item '{item.name}' to qty {item.qty} in room {room.name} (job {token})")

    return JSONResponse({"success": True, "new_qty": item.qty})


@app.post("/s/{company_slug}/{token}/room/{room_id}/update-variant/{item_index}")
def update_item_variant(
    request: Request,
    company_slug: str,
    token: str,
    room_id: str,
    item_index: int,
    variant_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update an item's variant (size/type) with pre-set dimensions from variant map"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    room = db.query(Room).filter(Room.id == room_id, Room.job_id == job.id).first()
    if not room:
        return JSONResponse({"error": "Room not found"}, status_code=404)

    items = db.query(Item).filter(Item.room_id == room.id).order_by(Item.id).all()
    if item_index < 0 or item_index >= len(items):
        return JSONResponse({"error": "Invalid item index"}, status_code=400)

    item = items[item_index]
    original_name = item.name

    # Find the matching variant data
    from app.variants import VARIANT_MAP, get_variant_category
    category = get_variant_category(original_name) or get_variant_category(variant_name)
    if not category:
        return JSONResponse({"error": "No variants available"}, status_code=400)

    variant_data = None
    for v in VARIANT_MAP[category]["variants"]:
        if v["name"] == variant_name:
            variant_data = v
            break

    if not variant_data:
        return JSONResponse({"error": "Invalid variant"}, status_code=400)

    # Store original AI detection in notes for ML training
    if "Original AI detection:" not in (item.notes or ""):
        original_note = f"Original AI detection: {original_name}"
        item.notes = f"{original_note}. {item.notes}" if item.notes else original_note

    # Update item with variant dimensions
    item.name = variant_data["name"]
    item.length_cm = variant_data["length_cm"]
    item.width_cm = variant_data["width_cm"]
    item.height_cm = variant_data["height_cm"]
    item.weight_kg = variant_data["weight_kg"]
    item.cbm = variant_data["cbm"]
    item.bulky = variant_data["weight_kg"] > 50
    db.commit()

    # Save correction as ItemFeedback for ML training
    try:
        feedback = ItemFeedback(
            item_id=item.id,
            company_id=company.id,
            ai_detected_name=original_name,
            corrected_name=variant_data["name"],
            corrected_dimensions={
                "length_cm": variant_data["length_cm"],
                "width_cm": variant_data["width_cm"],
                "height_cm": variant_data["height_cm"]
            },
            corrected_cbm=variant_data["cbm"],
            corrected_weight=variant_data["weight_kg"],
            feedback_type="correction",
            notes="Customer variant selection"
        )
        db.add(feedback)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not save variant feedback: {e}")

    logger.info(f"Variant changed: '{original_name}' -> '{variant_data['name']}' in room {room.name} (job {token})")

    return JSONResponse({
        "success": True,
        "new_name": variant_data["name"],
        "length_cm": variant_data["length_cm"],
        "width_cm": variant_data["width_cm"],
        "height_cm": variant_data["height_cm"],
        "weight_kg": variant_data["weight_kg"],
        "cbm": variant_data["cbm"],
        "bulky": variant_data["weight_kg"] > 50,
        "variants": [v["name"] for v in VARIANT_MAP[category]["variants"]],
    })


@app.post("/s/{company_slug}/{token}/room/{room_id}/confirm_items")
def room_confirm_items(company_slug: str, token: str, room_id: str):
    """Process confirmed items - redirect to rooms list"""
    return RedirectResponse(url=f"/s/{company_slug}/{token}/rooms", status_code=303)


# ----------------------------
# BULK PHOTO UPLOAD (all rooms at once)
# ----------------------------

@app.get("/s/{company_slug}/{token}/photos/bulk", response_class=HTMLResponse)
def photos_bulk_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Bulk photo upload page - upload all photos at once, AI detects rooms"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("photos_bulk.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Upload Photos - {company.company_name}",
        "nav_title": "Upload Photos",
        "back_url": f"/s/{company_slug}/{token}/rooms",
        "progress": 70,
    })


@app.post("/s/{company_slug}/{token}/photos/bulk-upload")
async def photos_bulk_upload(
    request: Request,
    company_slug: str,
    token: str,
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Handle bulk photo upload with AI room detection"""
    import asyncio

    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    if not photos or len(photos) == 0:
        return JSONResponse({"ok": False, "error": "No photos uploaded"}, status_code=400)

    if len(photos) > 30:
        return JSONResponse({"ok": False, "error": "Maximum 30 photos allowed"}, status_code=400)

    if len(photos) < 3:
        return JSONResponse({"ok": False, "error": "Please upload at least 3 photos"}, status_code=400)

    # Create uploads directory
    upload_dir = os.path.join("uploads", str(company.id), token)
    os.makedirs(upload_dir, exist_ok=True)

    try:
        # Save all photos first
        saved_paths = []
        photo_records = []

        for photo_file in photos:
            # Generate unique filename
            ext = os.path.splitext(photo_file.filename)[1] or ".jpg"
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await photo_file.read()
                await f.write(content)

            saved_paths.append(file_path)

        # 🧠 SELF-LEARNING: Get learned patterns to enhance AI prompt
        learned_guidance = None
        try:
            learned_guidance = ml_learning.get_learned_patterns_for_prompt(db)
            if learned_guidance:
                logger.info("Injecting learned patterns into AI prompt")
        except Exception as e:
            logger.warning(f"Could not get learned patterns: {e}")

        # Use AI to analyze all photos together
        logger.info(f"Analyzing {len(saved_paths)} photos with AI for bulk upload...")
        inventory = extract_removal_inventory(saved_paths, learned_guidance=learned_guidance)

        # 🧠 SELF-LEARNING: Apply learned corrections to AI detections (backup)
        if inventory.get("items"):
            try:
                inventory["items"], corrections = ml_learning.apply_learned_corrections(inventory["items"], db)
                if corrections:
                    logger.info(f"Auto-applied {len(corrections)} learned corrections")
            except Exception as e:
                logger.warning(f"Could not apply learned corrections: {e}")

        # Get room suggestion from AI (we'll use the summary to guess the room type)
        # For bulk upload, create ONE room called "Whole Property" and put everything in it
        room = Room(
            job_id=job.id,
            name="Whole Property",
            summary=inventory.get("summary", "AI-detected items from all photos")
        )
        db.add(room)
        db.flush()  # Get room ID

        # Save photos to database
        for i, file_path in enumerate(saved_paths):
            photo = Photo(
                room_id=room.id,
                filename=os.path.basename(file_path),
                original_filename=photos[i].filename,
                file_size_bytes=len(content),  # Approximate
                mime_type=photos[i].content_type,
                storage_path=file_path
            )
            db.add(photo)
            photo_records.append({
                "url": f"/uploads/{company.id}/{token}/{photo.filename}",
                "filename": photo.filename
            })

        # Store detected items
        if inventory.get("items"):
            for item_data in inventory["items"]:
                weight_kg = item_data.get("weight_kg")
                item = Item(
                    room_id=room.id,
                    name=item_data.get("name", "Unknown item"),
                    qty=item_data.get("qty", 1),
                    notes=item_data.get("notes", ""),
                    length_cm=item_data.get("length_cm"),
                    width_cm=item_data.get("width_cm"),
                    height_cm=item_data.get("height_cm"),
                    weight_kg=weight_kg,
                    cbm=item_data.get("cbm"),
                    bulky=(float(weight_kg) > 50) if weight_kg else False,
                    fragile=item_data.get("fragile", False),
                    item_category=item_data.get("item_category", "furniture"),
                    packing_requirement=item_data.get("packing_requirement", "none")
                )
                db.add(item)

        db.commit()

        logger.info(f"Bulk upload: Created 1 room with {len(inventory.get('items', []))} items")

        return JSONResponse({
            "ok": True,
            "photos": photo_records,
            "rooms": [{
                "name": room.name,
                "summary": room.summary,
                "item_count": len(inventory.get("items", []))
            }],
            "total_items": len(inventory.get("items", []))
        })

    except Exception as e:
        logger.error(f"Bulk upload error: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ----------------------------
# REVIEW + QUOTE
# ----------------------------

@app.get("/s/{company_slug}/{token}/review", response_class=HTMLResponse)
def review_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Review inventory page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    rooms = db.query(Room).filter(Room.job_id == job.id).all()

    return templates.TemplateResponse("review_inventory.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Review - {company.company_name}",
        "nav_title": "Review",
        "back_url": f"/s/{company_slug}/{token}/rooms",
        "progress": 90,
        "rooms": rooms,
    })


@app.post("/s/{company_slug}/{token}/review/finish")
def review_finish(company_slug: str, token: str):
    """Proceed to quote"""
    return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)


def calculate_packing_materials(job: Job, pricing: PricingConfig, db: Session) -> dict:
    """Calculate packing materials needed based on items"""
    import re

    # Get all items for this job
    rooms = db.query(Room).filter(Room.job_id == job.id).all()

    # Count packing requirements
    small_boxes = 0      # Pack 1
    medium_boxes = 0     # Pack 2
    large_boxes = 0      # Pack 3
    extra_small = 0      # Pack 6
    robe_cartons = 0     # Wardrobe boxes
    mattress_covers = 0  # Mattress covers

    for room in rooms:
        items = db.query(Item).filter(Item.room_id == room.id).all()
        for item in items:
            qty = item.qty or 1
            packing_req = item.packing_requirement or "none"

            if packing_req == 'small_box':
                # Books, heavy items: ~20 books per box
                small_boxes += max(1, qty // 20)
            elif packing_req == 'medium_box':
                # Kitchen items, clothes: ~15 items per box
                medium_boxes += max(1, qty // 15)
            elif packing_req == 'large_box':
                # Linens, bedding: ~10 items per box
                large_boxes += max(1, qty // 10)
            elif packing_req in ('robe_carton', 'wardrobe_box'):
                # Wardrobe boxes for hanging clothes
                # qty represents number of wardrobe boxes needed
                robe_cartons += qty
            elif packing_req == 'mattress_cover':
                mattress_covers += qty

    total_boxes = small_boxes + medium_boxes + large_boxes + extra_small + robe_cartons

    # Calculate costs
    pack1_cost = small_boxes * float(pricing.pack1_price)
    pack2_cost = medium_boxes * float(pricing.pack2_price)
    pack3_cost = large_boxes * float(pricing.pack3_price)
    pack6_cost = extra_small * float(pricing.pack6_price)
    robe_cost = robe_cartons * float(pricing.robe_carton_price)
    mattress_cost = mattress_covers * float(pricing.mattress_cover_price)

    # Tape: 1 roll per 10 boxes
    tape_rolls = max(1, (total_boxes // 10) + (1 if total_boxes % 10 > 0 else 0)) if total_boxes > 0 else 0
    tape_cost = tape_rolls * float(pricing.tape_price)

    # Paper: 1.5 packs per 10 CBM
    total_cbm = float(job.total_cbm or 0)
    paper_packs = (total_cbm / 10) * 1.5 if total_cbm > 0 else 0
    paper_cost = paper_packs * float(pricing.paper_price)

    # If customer is providing their own packing, cost is £0 but still show quantities
    if job.customer_provides_packing:
        total_packing_cost = 0
        pack1_cost = pack2_cost = pack3_cost = pack6_cost = 0
        robe_cost = mattress_cost = tape_cost = paper_cost = 0
    else:
        total_packing_cost = (pack1_cost + pack2_cost + pack3_cost + pack6_cost +
                              robe_cost + mattress_cost + tape_cost + paper_cost)

    return {
        "total_cost": round(total_packing_cost, 2),
        "breakdown": {
            "small_boxes": {"qty": small_boxes, "cost": round(pack1_cost, 2)},
            "medium_boxes": {"qty": medium_boxes, "cost": round(pack2_cost, 2)},
            "large_boxes": {"qty": large_boxes, "cost": round(pack3_cost, 2)},
            "extra_small_boxes": {"qty": extra_small, "cost": round(pack6_cost, 2)},
            "robe_cartons": {"qty": robe_cartons, "cost": round(robe_cost, 2)},
            "mattress_covers": {"qty": mattress_covers, "cost": round(mattress_cost, 2)},
            "tape_rolls": {"qty": tape_rolls, "cost": round(tape_cost, 2)},
            "paper_packs": {"qty": round(paper_packs, 1), "cost": round(paper_cost, 2)}
        },
        "total_boxes": total_boxes
    }


def calculate_packing_service(job: Job, pricing: PricingConfig, db: Session) -> dict:
    """
    Calculate packing service estimates per room
    Returns: {
        "rooms": [{"room_id": "...", "room_name": "Kitchen", "hours": 2.5, "cost": 100.00, "items_count": 45}],
        "total_hours": 5.0,
        "total_cost": 200.00
    }
    """
    rooms = db.query(Room).filter(Room.job_id == job.id).all()
    room_estimates = []
    total_hours = 0

    for room in rooms:
        items = db.query(Item).filter(Item.room_id == room.id).all()

        # Count items that need packing (loose items)
        items_needing_packing = 0
        for item in items:
            packing_req = item.packing_requirement or "none"
            if packing_req in ['small_box', 'medium_box', 'large_box']:
                items_needing_packing += (item.qty or 1)

        # Skip rooms with no loose items
        if items_needing_packing == 0:
            continue

        # Estimate packing time based on item count and room type
        # Base: 5 items per 15 minutes = 20 items/hour
        # Kitchens are slower (fragile, wrapping): 15 items/hour
        # Bedrooms/living rooms: 20 items/hour

        if 'kitchen' in room.name.lower():
            packing_rate = 15  # items per hour
        else:
            packing_rate = 20  # items per hour

        estimated_hours = max(0.5, items_needing_packing / packing_rate)  # Minimum 30min per room
        estimated_cost = estimated_hours * float(pricing.packing_labor_per_hour)

        # Check if customer wants this room packed
        is_selected = False
        if job.packing_service_rooms:
            is_selected = str(room.id) in job.packing_service_rooms

        room_estimates.append({
            "room_id": str(room.id),
            "room_name": room.name,
            "hours": round(estimated_hours, 1),
            "cost": round(estimated_cost, 2),
            "items_count": items_needing_packing,
            "is_selected": is_selected
        })

        if is_selected:
            total_hours += estimated_hours

    total_cost = total_hours * float(pricing.packing_labor_per_hour)

    return {
        "rooms": room_estimates,
        "total_hours": round(total_hours, 1),
        "total_cost": round(total_cost, 2)
    }


def calculate_quote(job: Job, db: Session) -> dict:
    """Calculate professional quote using company's custom pricing"""
    # Get company pricing config
    pricing = db.query(PricingConfig).filter(PricingConfig.company_id == job.company_id).first()
    if not pricing:
        raise ValueError(f"No pricing config for company {job.company_id}")

    # Get all items across all rooms for this job
    total_items = 0
    bulky_items = 0
    fragile_items = 0
    total_cbm = 0
    total_weight_kg = 0

    rooms = db.query(Room).filter(Room.job_id == job.id).all()
    for room in rooms:
        items = db.query(Item).filter(Item.room_id == room.id).all()
        for item in items:
            qty = item.qty
            total_items += qty

            # CBM calculations
            if item.cbm:
                total_cbm += float(item.cbm) * qty

            # Weight calculations
            if item.weight_kg:
                total_weight_kg += float(item.weight_kg) * qty

            if item.weight_kg and float(item.weight_kg) > float(pricing.bulky_weight_threshold_kg or 50):
                bulky_items += qty
            if item.fragile:
                fragile_items += qty

    # Professional pricing using company's custom rates
    base_price = float(pricing.callout_fee)
    cbm_price = total_cbm * float(pricing.price_per_cbm)
    bulky_surcharge = bulky_items * float(pricing.bulky_item_fee)
    fragile_surcharge = fragile_items * float(pricing.fragile_item_fee)

    # Weight-based pricing
    weight_price = 0
    if total_weight_kg > pricing.weight_threshold_kg:
        weight_price = (total_weight_kg - pricing.weight_threshold_kg) * float(pricing.price_per_kg_over_threshold)

    # Distance pricing - calculated from pickup/dropoff coordinates
    distance_price = 0
    distance_miles = 0
    if job.pickup and job.dropoff:
        pickup_lat = job.pickup.get('lat')
        pickup_lng = job.pickup.get('lng')
        dropoff_lat = job.dropoff.get('lat')
        dropoff_lng = job.dropoff.get('lng')

        if all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
            # Haversine formula for distance in miles
            import math
            R = 3959.0  # Earth's radius in miles
            lat1_rad = math.radians(float(pickup_lat))
            lat2_rad = math.radians(float(dropoff_lat))
            dlat = math.radians(float(dropoff_lat) - float(pickup_lat))
            dlng = math.radians(float(dropoff_lng) - float(pickup_lng))
            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance_miles = R * c

            # Calculate price: miles over base distance × price per mile
            base_distance = float(pricing.base_distance_km or 0) * 0.621371  # Convert km to miles
            price_per_mile = float(pricing.price_per_km or 2.00) * 1.60934  # Convert per-km to per-mile
            if distance_miles > base_distance:
                distance_price = (distance_miles - base_distance) * price_per_mile
            else:
                distance_price = 0

    # === ACCESS DIFFICULTY PRICING ===
    access_price = 0
    access_breakdown = {"pickup": {}, "dropoff": {}}

    # Helper function to calculate access fees for one location
    def calculate_location_access(access_data):
        if not access_data:
            return 0, {}

        location_fees = {}
        location_total = 0

        # Floors pricing
        floors = access_data.get('floors', 0)
        if floors > 0:
            floor_fee = floors * float(pricing.price_per_floor)
            location_fees['floors'] = floor_fee
            location_total += floor_fee

        # No lift surcharge (only if floors > 0 AND no lift)
        if floors > 0 and not access_data.get('has_lift', False):
            no_lift_fee = float(pricing.no_lift_surcharge)
            location_fees['no_lift'] = no_lift_fee
            location_total += no_lift_fee

        # Parking difficulty
        parking_type = access_data.get('parking_type', 'driveway')
        if parking_type == 'street':
            parking_fee = float(pricing.parking_street_fee)
            location_fees['parking'] = parking_fee
            location_total += parking_fee
        elif parking_type == 'permit_zone':
            parking_fee = float(pricing.parking_permit_fee)
            location_fees['parking'] = parking_fee
            location_total += parking_fee
        elif parking_type == 'limited':
            parking_fee = float(pricing.parking_limited_fee)
            location_fees['parking'] = parking_fee
            location_total += parking_fee

        # Parking distance (if not driveway)
        if parking_type != 'driveway':
            distance_meters = access_data.get('parking_distance_meters', 0)
            if distance_meters > 0:
                distance_increments = (distance_meters // 50) + (1 if distance_meters % 50 > 0 else 0)
                distance_fee = distance_increments * float(pricing.parking_distance_per_50m)
                location_fees['parking_distance'] = distance_fee
                location_total += distance_fee

        # Building restrictions
        restrictions = access_data.get('building_restrictions', [])
        if 'narrow_stairs' in restrictions or 'narrow_doorways' in restrictions or 'narrow_hallway' in restrictions:
            narrow_fee = float(pricing.narrow_access_fee)
            location_fees['narrow_access'] = narrow_fee
            location_total += narrow_fee

        if 'time_restrictions' in restrictions:
            time_fee = float(pricing.time_restriction_fee)
            location_fees['time_restrictions'] = time_fee
            location_total += time_fee

        if 'booking_required' in restrictions:
            booking_fee = float(pricing.booking_required_fee)
            location_fees['booking_required'] = booking_fee
            location_total += booking_fee

        # Outdoor access
        outdoor_access = access_data.get('outdoor_access', 'direct')
        if outdoor_access == 'path':
            path_fee = float(pricing.outdoor_path_fee)
            location_fees['outdoor_path'] = path_fee
            location_total += path_fee
        elif outdoor_access == 'steps':
            path_fee = float(pricing.outdoor_path_fee)
            location_fees['outdoor_path'] = path_fee
            location_total += path_fee

            # Outdoor steps pricing (per 5 steps)
            outdoor_steps = access_data.get('outdoor_steps', 0)
            if outdoor_steps > 0:
                step_increments = (outdoor_steps // 5) + (1 if outdoor_steps % 5 > 0 else 0)
                steps_fee = step_increments * float(pricing.outdoor_steps_per_5)
                location_fees['outdoor_steps'] = steps_fee
                location_total += steps_fee

        return location_total, location_fees

    # Calculate pickup access fees
    pickup_access_total, pickup_access_fees = calculate_location_access(job.pickup_access)
    access_breakdown['pickup'] = pickup_access_fees
    access_price += pickup_access_total

    # Calculate dropoff access fees
    dropoff_access_total, dropoff_access_fees = calculate_location_access(job.dropoff_access)
    access_breakdown['dropoff'] = dropoff_access_fees
    access_price += dropoff_access_total

    # === PACKING MATERIALS PRICING ===
    packing_data = calculate_packing_materials(job, pricing, db)
    packing_price = packing_data['total_cost']
    packing_breakdown = packing_data['breakdown']

    # === PACKING SERVICE LABOR PRICING ===
    packing_service_data = calculate_packing_service(job, pricing, db)
    packing_service_price = packing_service_data['total_cost']
    packing_service_breakdown = packing_service_data

    total = base_price + cbm_price + bulky_surcharge + fragile_surcharge + weight_price + distance_price + access_price + packing_price + packing_service_price

    # Apply company's estimate multipliers
    estimate_low = int(total * float(pricing.estimate_low_multiplier))
    estimate_high = int(total * float(pricing.estimate_high_multiplier))

    # Determine confidence based on completeness
    if total_items < 5 or total_cbm < 1:
        confidence = "Low - Need more photos"
    elif total_items < 20 or total_cbm < 5:
        confidence = "Medium"
    else:
        confidence = "High"

    # Update job with totals
    job.total_cbm = round(total_cbm, 2)
    job.total_weight_kg = round(total_weight_kg, 0)
    db.commit()

    # Use custom prices if admin set them
    final_low = job.custom_price_low or estimate_low
    final_high = job.custom_price_high or estimate_high

    # NOTE: Auto-approval removed - all quotes require manual admin approval
    # This ensures the admin always reviews before the customer can accept

    return {
        "estimate_low": final_low,
        "estimate_high": final_high,
        "ai_estimate_low": estimate_low,
        "ai_estimate_high": estimate_high,
        "has_custom_price": bool(job.custom_price_low),
        "total_items": total_items,
        "bulky_items": bulky_items,
        "fragile_items": fragile_items,
        "total_cbm": round(total_cbm, 2),
        "total_weight_kg": round(total_weight_kg, 0),
        "confidence": confidence,
        "distance_miles": round(distance_miles, 1),
        "breakdown": {
            "base": base_price,
            "volume": round(cbm_price, 2),
            "bulky": bulky_surcharge,
            "fragile": fragile_surcharge,
            "weight": round(weight_price, 2),
            "distance": distance_price,
            "access": round(access_price, 2),
            "packing": round(packing_price, 2),
            "packing_service": round(packing_service_price, 2)
        },
        "access_breakdown": access_breakdown,
        "packing_breakdown": packing_breakdown,
        "packing_service_breakdown": packing_service_breakdown
    }


@app.get("/s/{company_slug}/{token}/quote-preview", response_class=HTMLResponse)
def quote_preview(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Show quote preview to customer"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    quote = calculate_quote(job, db)

    return templates.TemplateResponse("quote_preview.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "company": company,
        "branding": request.state.branding,
        "title": f"Your Quote - {company.company_name}",
        "nav_title": "Your Quote",
        "back_url": f"/s/{company_slug}/{token}/rooms",
        "progress": 100,
        "job": job,
        "estimate_low": quote["estimate_low"],
        "estimate_high": quote["estimate_high"],
        "total_items": quote["total_items"],
        "bulky_items": quote["bulky_items"],
        "fragile_items": quote["fragile_items"],
        "total_cbm": quote["total_cbm"],
        "total_weight_kg": quote["total_weight_kg"],
        "confidence": quote["confidence"],
        "distance_miles": quote.get("distance_miles", 0),
        "breakdown": quote["breakdown"],
        "packing_breakdown": quote.get("packing_breakdown"),
        "access_breakdown": quote.get("access_breakdown"),
        "packing_service_breakdown": quote.get("packing_service_breakdown"),
    })


@app.post("/s/{company_slug}/{token}/packing-preference")
def update_packing_preference(
    request: Request,
    company_slug: str,
    token: str,
    use_company_packing: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update customer's packing materials preference"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Update preference
    job.customer_provides_packing = (use_company_packing == "no")
    db.commit()

    # Redirect back to quote preview to show updated pricing
    return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)


@app.post("/s/{company_slug}/{token}/packing-service")
def update_packing_service(
    request: Request,
    company_slug: str,
    token: str,
    room_ids: list[str] = Form([]),
    db: Session = Depends(get_db)
):
    """Update which rooms customer wants packing service for"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Update selected rooms
    job.packing_service_rooms = room_ids if room_ids else []
    db.commit()

    # Redirect back to quote preview to show updated pricing
    return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)


@app.post("/s/{company_slug}/{token}/submit-quote")
def submit_quote_for_approval(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Redirect to contact form to collect customer details before submission"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # If customer already has contact details, skip to actual submission
    if job.customer_name and job.customer_phone and job.customer_email:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/do-submit", status_code=303)

    # Otherwise, collect contact details first
    return RedirectResponse(url=f"/s/{company_slug}/{token}/contact", status_code=303)


@app.api_route("/s/{company_slug}/{token}/do-submit", methods=["GET", "POST"])
def do_submit_quote(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Actually submit the quote for approval (after contact details collected)"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Only submit if still in progress
    if job.status == "in_progress":
        job.status = "awaiting_approval"
        job.submitted_at = datetime.utcnow()
        db.commit()
        logger.info(f"Quote {token} submitted for approval by {job.customer_name}. CBM: {job.total_cbm}, Weight: {job.total_weight_kg}kg")

        # Charge survey fee (or use free survey)
        try:
            charge_result = billing.charge_survey_fee(company, token, db)
            if charge_result.get("charged"):
                logger.info(f"Charged £9.99 survey fee for {company.slug}")
            elif charge_result.get("reason") == "free_survey":
                logger.info(f"Used free survey for {company.slug}. {charge_result.get('free_remaining')} remaining.")
            elif charge_result.get("reason") == "no_payment_method":
                logger.warning(f"No payment method for {company.slug} - survey submitted but not charged")
        except Exception as e:
            logger.error(f"Error charging survey fee: {str(e)}")
            # Don't block the submission - just log the error

        # Track analytics event
        track_event(
            company_id=company.id,
            event_type='job_submitted',
            metadata={
                'job_token': token,
                'customer_name': job.customer_name,
                'description': f"Quote submitted for approval by {job.customer_name}"
            },
            db=db
        )

        # 🧠 SELF-LEARNING: Run learning cycle to process any feedback
        try:
            learning_result = ml_learning.run_learning_cycle(db)
            if learning_result.get("new_patterns_learned") or learning_result.get("patterns_promoted_to_auto"):
                logger.info(f"ML Learning: {learning_result.get('new_patterns_learned', 0)} new patterns, {learning_result.get('patterns_promoted_to_auto', 0)} promoted to auto-apply")
        except Exception as e:
            logger.warning(f"Learning cycle error (non-blocking): {e}")

    # Redirect back to quote preview with submission confirmation
    return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)


# ----------------------------
# CALENDAR BOOKING
# ----------------------------

@app.get("/s/{company_slug}/{token}/booking", response_class=HTMLResponse)
def booking_calendar_get(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Calendar booking page with time slots"""
    from datetime import date, timedelta

    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    quote = calculate_quote(job, db)

    # Set date range (today to 180 days out for flexibility)
    min_date = date.today().isoformat()
    max_date = (date.today() + timedelta(days=180)).isoformat()

    return templates.TemplateResponse("booking_calendar.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Book Move - {company.company_name}",
        "nav_title": "Book Your Move",
        "back_url": f"/s/{company_slug}/{token}/quote-preview",
        "progress": 95,
        "job": job,
        "estimate_low": quote["estimate_low"],
        "estimate_high": quote["estimate_high"],
        "min_date": min_date,
        "max_date": max_date,
    })


@app.post("/s/{company_slug}/{token}/booking/confirm")
def booking_confirm(
    request: Request,
    company_slug: str,
    token: str,
    move_date: str = Form(...),
    time_slot: str = Form(...),
    special_requirements: str = Form(""),
    db: Session = Depends(get_db)
):
    """Save booking details and redirect to contact form"""
    from datetime import datetime

    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Save booking details
    job.move_date = datetime.strptime(move_date, "%Y-%m-%d")

    # Store time slot and special requirements in job notes or new fields
    # For now, we'll use a simple approach
    booking_details = {
        "time_slot": time_slot,
        "special_requirements": special_requirements
    }

    # You could add these fields to the Job model, or store in JSONB
    # For simplicity, let's add to pickup JSONB (or create a new field)
    if not hasattr(job, 'booking_details'):
        # Store in a note for now (you can add a proper field later)
        pass

    db.commit()

    # Send booking confirmation SMS if customer details available
    if job.customer_phone and job.customer_name:
        try:
            # Format time slot for display
            time_slot_display = {
                "morning": "8:00 AM - 12:00 PM",
                "afternoon": "12:00 PM - 4:00 PM",
                "flexible": "Flexible (Any time)"
            }.get(time_slot, time_slot)

            notify_booking_confirmed(
                customer_name=job.customer_name,
                customer_phone=job.customer_phone,
                company_name=company.company_name,
                move_date=job.move_date.strftime("%A, %B %d, %Y"),
                time_slot=time_slot_display
            )
            logger.info(f"Booking confirmation SMS sent for job {token}")
        except Exception as e:
            logger.error(f"Failed to send booking confirmation SMS for job {token}: {e}")

    # Redirect to contact form
    return RedirectResponse(url=f"/s/{company_slug}/{token}/contact", status_code=303)


@app.get("/s/{company_slug}/{token}/contact", response_class=HTMLResponse)
def customer_contact_form(request: Request, company_slug: str, token: str, db: Session = Depends(get_db)):
    """Customer contact details form"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)
    quote = calculate_quote(job, db)

    return templates.TemplateResponse("customer_contact.html", {
        "request": request,
        "token": token,
        "company_slug": company_slug,
        "branding": request.state.branding,
        "title": f"Contact Details - {company.company_name}",
        "nav_title": "Contact Details",
        "back_url": f"/s/{company_slug}/{token}/quote-preview",
        "progress": 100,
        "job": job,
        "estimate_low": quote["estimate_low"],
        "estimate_high": quote["estimate_high"],
        "total_items": quote["total_items"],
        "total_cbm": quote["total_cbm"],
    })


@app.post("/s/{company_slug}/{token}/submit-contact")
def submit_contact_and_quote(
    request: Request,
    company_slug: str,
    token: str,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save contact details and submit quote for approval"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    if not customer_name or not customer_phone or not customer_email:
        return RedirectResponse(url=f"/s/{company_slug}/{token}/contact?err=required", status_code=303)

    # Save customer details
    job.customer_name = customer_name.strip()
    job.customer_phone = customer_phone.strip()
    job.customer_email = customer_email.strip()
    db.commit()

    logger.info(f"Contact details saved for {token}: {customer_name} ({customer_email}, {customer_phone})")

    # Now do the actual submission (status change, survey fee, etc.)
    return RedirectResponse(url=f"/s/{company_slug}/{token}/do-submit", status_code=307)  # 307 preserves POST


# ----------------------------
# QUOTE ACCEPTANCE
# ----------------------------

@app.get("/s/{company_slug}/{token}/quote/accept", response_class=HTMLResponse)
def quote_acceptance_page(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Quote acceptance page - customer explicitly accepts the quote"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Only show if quote is approved
    if job.status != 'approved':
        return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)

    # Calculate quote for display
    quote = calculate_quote(job, db)

    # Get error from query params
    error = request.query_params.get('error')

    return templates.TemplateResponse("quote_acceptance.html", {
        "request": request,
        "company": company,
        "company_slug": company_slug,
        "token": token,
        "job": job,
        "quote": quote,
        "branding": request.state.branding,
        "title": f"Accept Quote - {company.company_name}",
        "nav_title": "Accept Quote",
        "back_url": f"/s/{company_slug}/{token}/quote-preview",
        "progress": 85,
        "error": error
    })


@app.post("/s/{company_slug}/{token}/quote/accept")
def accept_quote(
    request: Request,
    company_slug: str,
    token: str,
    accept_quote: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Process quote acceptance"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Validate acceptance
    if accept_quote != "on":
        return RedirectResponse(
            url=f"/s/{company_slug}/{token}/quote/accept?error=You must accept the quote to continue.",
            status_code=303
        )

    # Quote is already approved, just redirect to T&Cs (if enabled) or move date
    if company.tcs_enabled and company.tcs_document_url:
        # Redirect to T&Cs acceptance
        return RedirectResponse(url=f"/s/{company_slug}/{token}/tcs", status_code=303)
    else:
        # No T&Cs required, redirect to move date selection
        return RedirectResponse(url=f"/s/{company_slug}/{token}/move-date", status_code=303)


# ----------------------------
# TERMS & CONDITIONS - CUSTOMER
# ----------------------------

@app.get("/s/{company_slug}/{token}/tcs/view")
def view_terms_document(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """View T&Cs PDF document (direct download/view)"""
    company = request.state.company

    if not company.tcs_document_url:
        raise HTTPException(status_code=404, detail="Terms & Conditions not available")

    # Redirect to PDF document
    return RedirectResponse(url=company.tcs_document_url, status_code=302)


@app.get("/s/{company_slug}/{token}/tcs", response_class=HTMLResponse)
def customer_tcs_acceptance_page(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Customer T&Cs acceptance page"""
    from app.models import TermsAcceptance

    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Check if T&Cs exist and are enabled
    if not company.tcs_document_url or not company.tcs_enabled:
        # Skip T&Cs if not configured
        return RedirectResponse(url=f"/s/{company_slug}/{token}/deposit", status_code=303)

    # Check if already accepted
    existing_acceptance = db.query(TermsAcceptance).filter(
        TermsAcceptance.job_id == job.id
    ).first()

    if existing_acceptance and existing_acceptance.accepted:
        # Already accepted, redirect to next step
        return RedirectResponse(url=f"/s/{company_slug}/{token}/deposit", status_code=303)

    # Get error from query params
    error = request.query_params.get('error')

    return templates.TemplateResponse("customer_tcs_accept.html", {
        "request": request,
        "company": company,
        "company_slug": company_slug,
        "token": token,
        "job": job,
        "branding": request.state.branding,
        "title": f"Terms & Conditions - {company.company_name}",
        "nav_title": "Terms & Conditions",
        "back_url": f"/s/{company_slug}/{token}/quote-preview",
        "progress": 90,
        "error": error
    })


@app.post("/s/{company_slug}/{token}/tcs/accept")
def accept_terms_and_conditions(
    request: Request,
    company_slug: str,
    token: str,
    accept_tcs: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Process T&Cs acceptance"""
    from app.models import TermsAcceptance

    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Validate acceptance
    if accept_tcs != "on":
        return RedirectResponse(
            url=f"/s/{company_slug}/{token}/tcs?error=You must accept the Terms & Conditions to continue.",
            status_code=303
        )

    # Check if already accepted
    existing_acceptance = db.query(TermsAcceptance).filter(
        TermsAcceptance.job_id == job.id
    ).first()

    if existing_acceptance and existing_acceptance.accepted:
        # Already accepted, just redirect
        return RedirectResponse(url=f"/s/{company_slug}/{token}/deposit", status_code=303)

    # Get customer metadata for legal compliance
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Create acceptance record
    acceptance = TermsAcceptance(
        job_id=job.id,
        company_id=company.id,
        tcs_version=company.tcs_version,
        tcs_document_url=company.tcs_document_url,
        tcs_document_hash=company.tcs_document_hash,
        customer_name=job.customer_name or "Unknown",
        customer_email=job.customer_email or "unknown@example.com",
        customer_phone=job.customer_phone,
        ip_address=client_ip,
        user_agent=user_agent,
        acceptance_method="web_form",
        accepted=True
    )

    db.add(acceptance)
    db.commit()

    logger.info(f"T&Cs v{company.tcs_version} accepted by {job.customer_name} for job {token}. IP: {client_ip}")

    # Redirect to move date selection page
    return RedirectResponse(url=f"/s/{company_slug}/{token}/move-date", status_code=303)


# ----------------------------
# DEPOSIT PAYMENT
# ----------------------------

@app.get("/s/{company_slug}/{token}/deposit", response_class=HTMLResponse)
def deposit_payment_page(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Show deposit payment page for approved quotes"""
    import os
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Only show deposit page if quote is approved
    if job.status != 'approved':
        return RedirectResponse(url=f"/s/{company_slug}/{token}/quote-preview", status_code=303)

    # Check if T&Cs acceptance is required but missing
    if company.tcs_enabled and company.tcs_document_url:
        from app.models import TermsAcceptance

        existing_acceptance = db.query(TermsAcceptance).filter(
            TermsAcceptance.job_id == job.id,
            TermsAcceptance.accepted == True
        ).first()

        if not existing_acceptance:
            # Redirect to T&Cs acceptance page
            return RedirectResponse(url=f"/s/{company_slug}/{token}/tcs", status_code=303)

    quote = calculate_quote(job, db)

    # Calculate deposit (20% of low estimate)
    deposit_amount = int(quote["estimate_low"] * 0.20)
    balance_due = quote["estimate_low"] - deposit_amount

    # Check if Stripe is configured
    stripe_configured = bool(os.getenv("STRIPE_SECRET_KEY"))

    # Check if company has Stripe Connect set up for receiving deposits
    connect_ready = company.stripe_connect_onboarding_complete

    return templates.TemplateResponse("deposit_payment.html", {
        "request": request,
        "company": company,
        "company_slug": company_slug,
        "token": token,
        "job": job,
        "quote_low": quote["estimate_low"],
        "quote_high": quote["estimate_high"],
        "total_items": quote["total_items"],
        "total_cbm": quote["total_cbm"],
        "deposit_amount": deposit_amount,
        "balance_due": balance_due,
        "stripe_configured": stripe_configured,
        "connect_ready": connect_ready
    })


@app.post("/s/{company_slug}/{token}/confirm-booking-manual")
def confirm_booking_manual(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Manual booking confirmation (when Stripe not configured)"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    # Update job status to booked
    job.status = "booked_pending_payment"
    db.commit()

    logger.info(f"Job {token} manually confirmed by customer. Payment pending.")

    return RedirectResponse(url=f"/s/{company_slug}/{token}/booking-confirmed", status_code=303)


@app.get("/s/{company_slug}/{token}/booking-confirmed", response_class=HTMLResponse)
def booking_confirmed_page(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Booking confirmation page"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    return templates.TemplateResponse("booking_confirmed.html", {
        "request": request,
        "company_slug": company_slug,
        "token": token,
        "job": job,
        "company": company
    })


@app.get("/test-map", response_class=HTMLResponse)
def test_map(request: Request):
    token = os.getenv("MAPBOX_ACCESS_TOKEN", "")
    return templates.TemplateResponse("test_map.html", {
        "request": request,
        "title": "Test Map — PrimeHaul OS",
        "nav_title": "Test Map",
        "back_url": "/",
        "progress": None,
        "mapbox_token": token,
    })


# ============================================
# ADMIN ROUTES - Company Admin Dashboard
# ============================================

@app.get("/admin", response_class=HTMLResponse)
def admin_redirect():
    """Redirect old admin URL to new auth login"""
    return RedirectResponse(url="/auth/login", status_code=301)


@app.get("/{company_slug}/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin dashboard showing all jobs for this company"""
    company = verify_company_access(company_slug, current_user)

    # Get jobs by status
    awaiting_jobs = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status == 'awaiting_approval'
    ).order_by(Job.submitted_at.desc()).all()

    approved_jobs = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status == 'approved'
    ).order_by(Job.approved_at.desc()).limit(10).all()

    rejected_jobs = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status == 'rejected'
    ).order_by(Job.rejected_at.desc()).limit(10).all()

    # Welcome message for new signups
    welcome = request.query_params.get("welcome") == "true"

    # Show onboarding for new users who haven't dismissed it and have no completed jobs
    total_jobs = db.query(Job).filter(Job.company_id == company.id).count()
    show_onboarding = welcome or (total_jobs == 0 and not company.onboarding_completed)

    return templates.TemplateResponse("admin_dashboard_v2.html", {
        "request": request,
        "company": company,
        "current_user": current_user,
        "title": f"Dashboard - {company.company_name}",
        "company_slug": company_slug,
        "awaiting_jobs": awaiting_jobs,
        "approved_jobs": approved_jobs,
        "rejected_jobs": rejected_jobs,
        "welcome": welcome,
        "show_onboarding": show_onboarding
    })


@app.post("/{company_slug}/admin/dismiss-onboarding")
def dismiss_onboarding(
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss the onboarding banner"""
    company = verify_company_access(company_slug, current_user)
    company.onboarding_completed = True
    db.commit()
    return {"status": "ok"}


@app.get("/{company_slug}/admin/job/{token}", response_class=HTMLResponse)
def admin_job_review(
    request: Request,
    company_slug: str,
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detailed job review for admin"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if not job:
        return RedirectResponse(url=f"/{company_slug}/admin/dashboard", status_code=303)

    # 🔒 PAYWALL: Don't show detailed data until customer submits (and we count the survey)
    if job.status == "in_progress":
        return templates.TemplateResponse("admin_job_pending.html", {
            "request": request,
            "title": "Survey In Progress — PrimeHaul OS",
            "token": token,
            "job": job,
            "company": company,
            "company_slug": company_slug
        })

    quote = calculate_quote(job, db)

    return templates.TemplateResponse("admin_job_review_v2.html", {
        "request": request,
        "title": f"Review Job {token[:8]} — PrimeHaul OS",
        "token": token,
        "job": job,
        "company": company,
        "quote": quote,
        "breakdown": quote.get("breakdown"),
        "packing_breakdown": quote.get("packing_breakdown"),
        "packing_service_breakdown": quote.get("packing_service_breakdown"),
        "access_breakdown": quote.get("access_breakdown"),
        "company_slug": company_slug
    })


@app.post("/{company_slug}/admin/job/{token}/approve")
def admin_approve_job(
    company_slug: str,
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a job"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if job:
        job.status = "approved"
        job.approved_at = datetime.utcnow()
        db.commit()
        logger.info(f"Job {token} approved by admin {current_user.email}")

        # Track analytics event
        track_event(
            company_id=company.id,
            event_type='job_approved',
            metadata={
                'job_token': token,
                'customer_name': job.customer_name,
                'description': f"Quote approved for {job.customer_name}"
            },
            db=db
        )

        # Send SMS notification to customer
        if job.customer_phone:
            try:
                notify_quote_approved(
                    phone=job.customer_phone,
                    company_name=company.company_name,
                    booking_url=f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN', 'localhost:8000')}/s/{company_slug}/{token}/booking"
                )
            except Exception as e:
                logger.error(f"Failed to send approval SMS: {e}")

    return RedirectResponse(url=f"/{company_slug}/admin/dashboard", status_code=303)


@app.post("/{company_slug}/admin/job/{token}/reject")
def admin_reject_job(
    company_slug: str,
    token: str,
    reason: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a job"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if job:
        job.status = "rejected"
        job.rejected_at = datetime.utcnow()
        job.rejection_reason = reason
        db.commit()
        logger.info(f"Job {token} rejected by admin {current_user.email}. Reason: {reason}")

        # Track analytics event
        track_event(
            company_id=company.id,
            event_type='job_rejected',
            metadata={
                'job_token': token,
                'customer_name': job.customer_name,
                'description': f"Quote rejected for {job.customer_name}",
                'reason': reason
            },
            db=db
        )

        # TODO: Send SMS/email to customer with rejection reason

    return RedirectResponse(url=f"/{company_slug}/admin/dashboard", status_code=303)


@app.post("/{company_slug}/admin/job/{token}/update-price")
def admin_update_price(
    company_slug: str,
    token: str,
    custom_price_low: int = Form(...),
    custom_price_high: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update custom pricing for a job"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if job:
        job.custom_price_low = custom_price_low
        job.custom_price_high = custom_price_high
        db.commit()
        logger.info(f"Job {token} price updated to £{custom_price_low}-{custom_price_high} by {current_user.email}")

    return RedirectResponse(url=f"/{company_slug}/admin/job/{token}", status_code=303)


@app.post("/{company_slug}/admin/job/{token}/add-note")
def admin_add_note(
    company_slug: str,
    token: str,
    note: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an admin note to a job"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if job and note.strip():
        admin_note = AdminNote(
            job_id=job.id,
            user_id=current_user.id,
            note=note.strip(),
            created_at=datetime.utcnow()
        )
        db.add(admin_note)
        db.commit()
        logger.info(f"Note added to job {token} by {current_user.email}")

    return RedirectResponse(url=f"/{company_slug}/admin/job/{token}", status_code=303)


@app.post("/{company_slug}/admin/job/{token}/quick-approve")
def admin_quick_approve(
    company_slug: str,
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick approve from dashboard without opening details"""
    company = verify_company_access(company_slug, current_user)

    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == company.id
    ).first()

    if job:
        job.status = "approved"
        job.approved_at = datetime.utcnow()
        db.commit()
        logger.info(f"Job {token} quick-approved by {current_user.email}")

        # Send SMS notification to customer
        if job.customer_phone and job.customer_name:
            try:
                # Calculate quote for price range
                quote = calculate_quote(job, db)
                booking_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN', 'localhost:8000')}/s/{company_slug}/{token}/booking"

                notify_quote_approved(
                    customer_name=job.customer_name,
                    customer_phone=job.customer_phone,
                    company_name=company.company_name,
                    price_low=quote["estimate_low"],
                    price_high=quote["estimate_high"],
                    booking_url=booking_url
                )
                logger.info(f"SMS sent to customer for quick-approved job {token}")
            except Exception as e:
                logger.error(f"Failed to send quick-approve SMS for job {token}: {e}")

        return JSONResponse({"success": True})

    return JSONResponse({"error": "Job not found"}, status_code=404)


@app.post("/admin/item-feedback")
async def submit_item_feedback(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit AI training feedback for an item"""
    try:
        data = await request.json()

        # Get the item
        item = db.query(Item).filter(Item.id == data.get('item_id')).first()
        if not item:
            return JSONResponse({"error": "Item not found"}, status_code=404)

        # Get the item's job to find the company
        room = db.query(Room).filter(Room.id == item.room_id).first()
        if not room:
            return JSONResponse({"error": "Room not found"}, status_code=404)

        job = db.query(Job).filter(Job.id == room.job_id).first()
        if not job:
            return JSONResponse({"error": "Job not found"}, status_code=404)

        # Create feedback record
        feedback = ItemFeedback(
            id=uuid.uuid4(),
            item_id=item.id,
            company_id=job.company_id,
            user_id=current_user.id,
            ai_detected_name=item.name,
            ai_detected_category=item.category,
            ai_confidence=item.confidence,
            corrected_name=data.get('corrected_name'),
            corrected_category=data.get('corrected_category'),
            corrected_dimensions=data.get('corrected_dimensions'),
            corrected_cbm=None,
            corrected_weight=data.get('corrected_weight'),
            feedback_type=data.get('feedback_type', 'correction'),
            notes=data.get('notes')
        )

        # Calculate corrected CBM if dimensions provided
        if data.get('corrected_dimensions'):
            dims = data['corrected_dimensions']
            length = dims.get('length', 0)
            width = dims.get('width', 0)
            height = dims.get('height', 0)
            if length and width and height:
                feedback.corrected_cbm = (length * width * height) / 1_000_000

        db.add(feedback)
        db.commit()

        logger.info(f"AI feedback submitted for item {item.id} by {current_user.email}: {data.get('feedback_type')}")

        return JSONResponse({"success": True, "message": "Feedback submitted successfully"})

    except Exception as e:
        logger.error(f"Error submitting item feedback: {e}")
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/admin/export-training-data")
def export_training_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all training data (catalog + feedback) for ML model training"""
    try:
        training_data = []

        # 1. Export IKEA catalog data
        catalog_items = db.query(FurnitureCatalog).all()
        for item in catalog_items:
            training_data.append({
                "source": "catalog",
                "source_type": item.source,
                "product_id": item.product_id,
                "item_name": item.name,
                "item_category": item.category,
                "length_cm": float(item.length_cm) if item.length_cm else None,
                "width_cm": float(item.width_cm) if item.width_cm else None,
                "height_cm": float(item.height_cm) if item.height_cm else None,
                "cbm": float(item.cbm) if item.cbm else None,
                "weight_kg": float(item.weight_kg) if item.weight_kg else None,
                "is_bulky": item.is_bulky,
                "is_fragile": item.is_fragile,
                "packing_requirement": item.packing_requirement,
                "image_urls": item.image_urls,
                "verified": True,  # Catalog data is verified
                "confidence_score": 1.0
            })

        # 2. Export admin feedback corrections
        feedbacks = db.query(ItemFeedback).filter(
            ItemFeedback.feedback_type.in_(['correction', 'confirmation'])
        ).all()

        for feedback in feedbacks:
            # Get original item for image URLs
            item = db.query(Item).filter(Item.id == feedback.item_id).first()
            if not item:
                continue

            room = db.query(Room).filter(Room.id == item.room_id).first()
            if not room:
                continue

            # Get photo URLs
            photos = db.query(Photo).filter(Photo.room_id == room.id).all()
            image_urls = [photo.url for photo in photos]

            if feedback.feedback_type == 'correction':
                # Use corrected data
                training_data.append({
                    "source": "feedback_correction",
                    "source_type": "admin_corrected",
                    "item_name": feedback.corrected_name or feedback.ai_detected_name,
                    "item_category": feedback.corrected_category or feedback.ai_detected_category,
                    "length_cm": feedback.corrected_dimensions.get('length') if feedback.corrected_dimensions else float(item.length_cm),
                    "width_cm": feedback.corrected_dimensions.get('width') if feedback.corrected_dimensions else float(item.width_cm),
                    "height_cm": feedback.corrected_dimensions.get('height') if feedback.corrected_dimensions else float(item.height_cm),
                    "cbm": float(feedback.corrected_cbm) if feedback.corrected_cbm else float(item.cbm),
                    "weight_kg": float(feedback.corrected_weight) if feedback.corrected_weight else float(item.weight_kg),
                    "is_bulky": item.bulky,
                    "is_fragile": item.fragile,
                    "packing_requirement": item.packing_requirement,
                    "image_urls": image_urls,
                    "verified": True,
                    "confidence_score": 1.0,
                    "original_ai_detection": {
                        "name": feedback.ai_detected_name,
                        "category": feedback.ai_detected_category,
                        "confidence": float(feedback.ai_confidence) if feedback.ai_confidence else None
                    }
                })
            elif feedback.feedback_type == 'confirmation':
                # AI was correct, use original detection as verified
                training_data.append({
                    "source": "feedback_confirmation",
                    "source_type": "admin_confirmed",
                    "item_name": feedback.ai_detected_name,
                    "item_category": feedback.ai_detected_category,
                    "length_cm": float(item.length_cm),
                    "width_cm": float(item.width_cm),
                    "height_cm": float(item.height_cm),
                    "cbm": float(item.cbm),
                    "weight_kg": float(item.weight_kg),
                    "is_bulky": item.bulky,
                    "is_fragile": item.fragile,
                    "packing_requirement": item.packing_requirement,
                    "image_urls": image_urls,
                    "verified": True,
                    "confidence_score": 1.0
                })

        logger.info(f"Training data exported: {len(training_data)} items ({current_user.email})")

        return JSONResponse({
            "success": True,
            "total_items": len(training_data),
            "breakdown": {
                "catalog_items": len(catalog_items),
                "feedback_items": len(feedbacks)
            },
            "data": training_data
        })

    except Exception as e:
        logger.error(f"Error exporting training data: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# ============================================================================
# BILLING & SUBSCRIPTION ENDPOINTS
# ============================================================================

@app.get("/{company_slug}/billing", response_class=HTMLResponse)
def billing_dashboard(
    request: Request,
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Billing dashboard for subscription management"""
    company = verify_company_access(company_slug, current_user)

    # Check subscription status
    subscription_info = billing.check_subscription_status(company)

    return templates.TemplateResponse("billing_dashboard.html", {
        "request": request,
        "title": "Billing & Subscription — PrimeHaul OS",
        "company": company,
        "company_slug": company_slug,
        "subscription_info": subscription_info
    })


@app.post("/{company_slug}/billing/create-checkout")
def create_checkout(
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session"""
    company = verify_company_access(company_slug, current_user)

    # Build success and cancel URLs
    app_url = os.getenv("APP_URL", "https://primehaul.co.uk")
    success_url = f"{app_url}/{company_slug}/billing?billing_success=true"
    cancel_url = f"{app_url}/{company_slug}/billing?billing_canceled=true"

    try:
        checkout_session = billing.create_checkout_session(
            company=company,
            success_url=success_url,
            cancel_url=cancel_url,
            db=db
        )

        # Redirect to Stripe checkout
        return RedirectResponse(url=checkout_session["url"], status_code=303)

    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return RedirectResponse(
            url=f"/{company_slug}/billing?error=checkout_failed",
            status_code=303
        )


@app.post("/{company_slug}/billing/manage")
def manage_subscription(
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe customer portal session"""
    company = verify_company_access(company_slug, current_user)

    # Build return URL
    app_url = os.getenv("APP_URL", "https://primehaul.co.uk")
    return_url = f"{app_url}/{company_slug}/billing"

    try:
        portal_session = billing.create_customer_portal_session(
            company=company,
            return_url=return_url
        )

        # Redirect to Stripe customer portal
        return RedirectResponse(url=portal_session["url"], status_code=303)

    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}")
        return RedirectResponse(
            url=f"/{company_slug}/billing?error=portal_failed",
            status_code=303
        )


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        logger.error("Missing Stripe signature")
        return JSONResponse({"error": "Missing signature"}, status_code=400)

    try:
        # Verify webhook signature
        event = billing.verify_webhook_signature(payload, signature)

        # Process the event
        success = billing.process_webhook_event(event, db)

        if success:
            return JSONResponse({"status": "success"})
        else:
            return JSONResponse({"status": "ignored"})

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=400)


# ============================================================================
# STRIPE CONNECT - For removal companies to receive deposits directly
# ============================================================================

@app.get("/{company_slug}/admin/payments", response_class=HTMLResponse)
def payments_settings(
    request: Request,
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Payment settings page - Stripe Connect onboarding"""
    company = verify_company_access(company_slug, current_user)

    # Check Connect account status
    connect_status = billing.check_connect_account_status(company, db)

    # Get usage stats
    usage = billing.get_company_usage(company)

    return templates.TemplateResponse("admin_payments.html", {
        "request": request,
        "company": company,
        "company_slug": company_slug,
        "title": "Payment Settings",
        "connect_status": connect_status,
        "usage": usage
    })


@app.post("/{company_slug}/admin/payments/connect")
def start_stripe_connect(
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start Stripe Connect onboarding for receiving deposits"""
    company = verify_company_access(company_slug, current_user)

    app_url = os.getenv("APP_URL", "https://primehaul.co.uk")

    try:
        # Create Connect account if needed
        if not company.stripe_connect_account_id:
            billing.create_connect_account(company, db)

        # Create onboarding link
        link = billing.create_connect_onboarding_link(
            company=company,
            return_url=f"{app_url}/{company_slug}/admin/payments?connected=true",
            refresh_url=f"{app_url}/{company_slug}/admin/payments?refresh=true"
        )

        return RedirectResponse(url=link["url"], status_code=303)

    except Exception as e:
        logger.error(f"Error starting Connect onboarding: {str(e)}")
        return RedirectResponse(
            url=f"/{company_slug}/admin/payments?error=connect_failed",
            status_code=303
        )


@app.post("/s/{company_slug}/{token}/create-deposit-payment")
def create_deposit_payment(
    request: Request,
    company_slug: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Create a deposit payment intent (Stripe Connect - direct to company)"""
    company = request.state.company
    job = get_or_create_job(company.id, token, db)

    if job.status != 'approved':
        return JSONResponse({"error": "Quote not approved"}, status_code=400)

    if not company.stripe_connect_onboarding_complete:
        return JSONResponse({"error": "Company has not set up payments"}, status_code=400)

    # Calculate deposit
    quote = calculate_quote(job, db)
    deposit_amount_pence = int(quote["estimate_low"] * 0.20 * 100)

    try:
        payment = billing.create_deposit_payment_intent(
            company=company,
            amount_pence=deposit_amount_pence,
            job_token=token,
            customer_email=job.customer_email or "",
            customer_name=job.customer_name or ""
        )

        return JSONResponse({
            "client_secret": payment["client_secret"],
            "amount": deposit_amount_pence / 100
        })

    except Exception as e:
        logger.error(f"Error creating deposit payment: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


# ============================================================================
# BRANDING & CUSTOMIZATION ENDPOINTS
# ============================================================================

@app.get("/{company_slug}/admin/branding", response_class=HTMLResponse)
def branding_settings(
    request: Request,
    company_slug: str,
    success: Optional[str] = None,
    error: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Branding settings page"""
    company = verify_company_access(company_slug, current_user)

    return templates.TemplateResponse("admin_branding.html", {
        "request": request,
        "title": "Branding Settings — PrimeHaul OS",
        "company": company,
        "company_slug": company_slug,
        "success": success,
        "error": error
    })


@app.post("/{company_slug}/admin/branding/upload-logo")
async def upload_logo(
    company_slug: str,
    logo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload company logo"""
    company = verify_company_access(company_slug, current_user)

    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/svg+xml"]
    if logo.content_type not in allowed_types:
        return RedirectResponse(
            url=f"/{company_slug}/admin/branding?error=Invalid file type. Please upload PNG, JPG, or SVG.",
            status_code=303
        )

    # Validate file size (max 2MB)
    contents = await logo.read()
    if len(contents) > 2 * 1024 * 1024:  # 2MB
        return RedirectResponse(
            url=f"/{company_slug}/admin/branding?error=File too large. Maximum size is 2MB.",
            status_code=303
        )

    # Create logos directory if it doesn't exist
    logos_dir = Path("app/static/logos")
    logos_dir.mkdir(parents=True, exist_ok=True)

    # Determine file extension
    extension = logo.filename.split('.')[-1] if '.' in logo.filename else 'png'
    filename = f"{company.id}.{extension}"
    file_path = logos_dir / filename

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    # Update company logo URL
    company.logo_url = f"/static/logos/{filename}"
    db.commit()

    logger.info(f"Logo uploaded for company {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/branding?success=true",
        status_code=303
    )


@app.post("/{company_slug}/admin/branding/update-colors")
def update_brand_colors(
    company_slug: str,
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update brand colors"""
    company = verify_company_access(company_slug, current_user)

    # Validate hex color format
    import re
    hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

    if not hex_pattern.match(primary_color):
        return RedirectResponse(
            url=f"/{company_slug}/admin/branding?error=Invalid primary color format. Use hex format like #2ee59d",
            status_code=303
        )

    if not hex_pattern.match(secondary_color):
        return RedirectResponse(
            url=f"/{company_slug}/admin/branding?error=Invalid secondary color format. Use hex format like #1a1a1a",
            status_code=303
        )

    # Update colors
    company.primary_color = primary_color
    company.secondary_color = secondary_color
    db.commit()

    logger.info(f"Brand colors updated for company {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/branding?success=true",
        status_code=303
    )


# ============================================================================
# COMPANY DETAILS ENDPOINTS - ADMIN
# ============================================================================

@app.get("/{company_slug}/admin/company-details", response_class=HTMLResponse)
def company_details_settings(
    request: Request,
    company_slug: str,
    success: Optional[str] = None,
    error: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Company details settings page"""
    company = verify_company_access(company_slug, current_user)

    return templates.TemplateResponse("admin_company_details.html", {
        "request": request,
        "title": "Company Details — PrimeHaul OS",
        "company": company,
        "company_slug": company_slug,
        "success": success,
        "error": error
    })


@app.post("/{company_slug}/admin/company-details/update")
def update_company_details(
    company_slug: str,
    company_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update company details"""
    company = verify_company_access(company_slug, current_user)

    # Validate company name
    if not company_name or len(company_name.strip()) < 2:
        return RedirectResponse(
            url=f"/{company_slug}/admin/company-details?error=Company name must be at least 2 characters.",
            status_code=303
        )

    # Validate email format
    import re
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email.strip()):
        return RedirectResponse(
            url=f"/{company_slug}/admin/company-details?error=Please enter a valid email address.",
            status_code=303
        )

    # Check email uniqueness (if changed)
    if email.strip() != company.email:
        existing = db.query(Company).filter(Company.email == email.strip(), Company.id != company.id).first()
        if existing:
            return RedirectResponse(
                url=f"/{company_slug}/admin/company-details?error=This email is already in use by another company.",
                status_code=303
            )

    # Validate phone (optional, basic format)
    if phone and phone.strip():
        phone_clean = phone.strip()
        phone_pattern = re.compile(r'^[\+]?[\d\s\-\(\)]{7,20}$')
        if not phone_pattern.match(phone_clean):
            return RedirectResponse(
                url=f"/{company_slug}/admin/company-details?error=Please enter a valid phone number.",
                status_code=303
            )

    # Update company
    company.company_name = company_name.strip()
    company.email = email.strip()
    company.phone = phone.strip() if phone and phone.strip() else None
    db.commit()

    logger.info(f"Company details updated for {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/company-details?success=true",
        status_code=303
    )


# ============================================================================
# TERMS & CONDITIONS ENDPOINTS - ADMIN
# ============================================================================

@app.get("/{company_slug}/admin/terms", response_class=HTMLResponse)
def admin_terms_page(
    company_slug: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin page to manage Terms & Conditions"""
    from app.models import TermsAcceptance

    company = verify_company_access(company_slug, current_user)

    # Get acceptance count
    acceptance_count = db.query(func.count(TermsAcceptance.id)).filter(
        TermsAcceptance.company_id == company.id
    ).scalar() or 0

    # Get recent acceptances (last 10)
    recent_acceptances = db.query(TermsAcceptance).filter(
        TermsAcceptance.company_id == company.id
    ).order_by(TermsAcceptance.created_at.desc()).limit(10).all()

    # Calculate next version
    current_version = company.tcs_version or "1.0"
    try:
        major, minor = map(int, current_version.split('.'))
        next_version = f"{major}.{minor + 1}"
    except:
        next_version = "1.1"

    # Get success/error from query params
    success = request.query_params.get('success') == 'true'
    error = request.query_params.get('error')

    return templates.TemplateResponse("admin_terms.html", {
        "request": request,
        "company": company,
        "company_slug": company_slug,
        "acceptance_count": acceptance_count,
        "recent_acceptances": recent_acceptances,
        "next_version": next_version,
        "success": success,
        "error": error
    })


@app.post("/{company_slug}/admin/terms/upload")
async def upload_terms_document(
    company_slug: str,
    tcs_document: UploadFile = File(...),
    enable_immediately: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload new T&Cs PDF document"""
    import hashlib

    company = verify_company_access(company_slug, current_user)

    # Validate file type
    if tcs_document.content_type != "application/pdf":
        return RedirectResponse(
            url=f"/{company_slug}/admin/terms?error=Invalid file type. Please upload a PDF document.",
            status_code=303
        )

    # Validate file size (max 10MB)
    contents = await tcs_document.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB
        return RedirectResponse(
            url=f"/{company_slug}/admin/terms?error=File too large. Maximum size is 10MB.",
            status_code=303
        )

    # Calculate document hash (SHA-256) for legal proof
    document_hash = hashlib.sha256(contents).hexdigest()

    # Create documents directory structure
    documents_dir = Path("app/static/documents") / str(company.id)
    documents_dir.mkdir(parents=True, exist_ok=True)

    # Calculate new version
    if company.tcs_version:
        try:
            major, minor = map(int, company.tcs_version.split('.'))
            new_version = f"{major}.{minor + 1}"
        except:
            new_version = "1.1"
    else:
        new_version = "1.0"

    # Filename format: tcs-v{version}-{hash[:8]}.pdf
    filename = f"tcs-v{new_version}-{document_hash[:8]}.pdf"
    file_path = documents_dir / filename

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    # Update company record
    company.tcs_document_url = f"/static/documents/{company.id}/{filename}"
    company.tcs_version = new_version
    company.tcs_updated_at = datetime.utcnow()
    company.tcs_document_hash = document_hash

    # Enable if checkbox was checked
    if enable_immediately == "on":
        company.tcs_enabled = True

    db.commit()

    logger.info(f"T&Cs v{new_version} uploaded for company {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/terms?success=true",
        status_code=303
    )


@app.post("/{company_slug}/admin/terms/toggle")
def toggle_terms_requirement(
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable or disable T&Cs requirement"""
    company = verify_company_access(company_slug, current_user)

    # Check if T&Cs document exists
    if not company.tcs_document_url:
        return RedirectResponse(
            url=f"/{company_slug}/admin/terms?error=Please upload a T&Cs document first.",
            status_code=303
        )

    # Toggle enabled status
    company.tcs_enabled = not company.tcs_enabled
    db.commit()

    status_text = "enabled" if company.tcs_enabled else "disabled"
    logger.info(f"T&Cs {status_text} for company {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/terms?success=true",
        status_code=303
    )


# ============================================================================
# PRICING CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/{company_slug}/admin/pricing", response_class=HTMLResponse)
def pricing_settings(
    request: Request,
    company_slug: str,
    success: Optional[str] = None,
    error: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pricing configuration page"""
    company = verify_company_access(company_slug, current_user)

    # Get or create pricing config
    pricing = db.query(PricingConfig).filter(
        PricingConfig.company_id == company.id
    ).first()

    if not pricing:
        # Create default pricing config
        pricing = PricingConfig(
            company_id=company.id,
            price_per_cbm=35.00,
            callout_fee=250.00,
            bulky_item_fee=25.00,
            fragile_item_fee=15.00,
            weight_threshold_kg=1000,
            price_per_kg_over_threshold=0.50,
            estimate_low_multiplier=0.85,
            estimate_high_multiplier=1.15
        )
        db.add(pricing)
        db.commit()

    return templates.TemplateResponse("admin_pricing.html", {
        "request": request,
        "title": "Pricing Configuration — PrimeHaul OS",
        "company": company,
        "company_slug": company_slug,
        "pricing": pricing,
        "success": success,
        "error": error
    })


@app.post("/{company_slug}/admin/pricing")
def update_pricing(
    company_slug: str,
    price_per_cbm: float = Form(...),
    callout_fee: float = Form(...),
    bulky_item_fee: float = Form(...),
    bulky_weight_threshold_kg: int = Form(50),
    fragile_item_fee: float = Form(...),
    weight_threshold_kg: int = Form(...),
    price_per_kg_over_threshold: float = Form(...),
    base_distance_km: int = Form(0),
    price_per_km: float = Form(2.00),
    pack1_price: float = Form(...),
    pack2_price: float = Form(...),
    pack3_price: float = Form(...),
    pack6_price: float = Form(...),
    robe_carton_price: float = Form(...),
    tape_price: float = Form(...),
    paper_price: float = Form(...),
    mattress_cover_price: float = Form(...),
    packing_labor_per_hour: float = Form(...),
    estimate_low_multiplier: float = Form(...),
    estimate_high_multiplier: float = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update pricing configuration"""
    company = verify_company_access(company_slug, current_user)

    # Validate inputs
    all_prices = [
        price_per_cbm, callout_fee, bulky_item_fee, fragile_item_fee, price_per_kg_over_threshold,
        price_per_km, pack1_price, pack2_price, pack3_price, pack6_price, robe_carton_price,
        tape_price, paper_price, mattress_cover_price, packing_labor_per_hour
    ]

    if any(v < 0 for v in all_prices):
        return RedirectResponse(
            url=f"/{company_slug}/admin/pricing?error=All prices must be positive numbers",
            status_code=303
        )

    if weight_threshold_kg < 0:
        return RedirectResponse(
            url=f"/{company_slug}/admin/pricing?error=Weight threshold must be a positive number",
            status_code=303
        )

    if estimate_low_multiplier >= estimate_high_multiplier:
        return RedirectResponse(
            url=f"/{company_slug}/admin/pricing?error=Low estimate multiplier must be less than high estimate multiplier",
            status_code=303
        )

    # Get or create pricing config
    pricing = db.query(PricingConfig).filter(
        PricingConfig.company_id == company.id
    ).first()

    if not pricing:
        pricing = PricingConfig(company_id=company.id)
        db.add(pricing)

    # Update all fields
    pricing.price_per_cbm = price_per_cbm
    pricing.callout_fee = callout_fee
    pricing.bulky_item_fee = bulky_item_fee
    pricing.bulky_weight_threshold_kg = bulky_weight_threshold_kg
    pricing.fragile_item_fee = fragile_item_fee
    pricing.weight_threshold_kg = weight_threshold_kg
    pricing.price_per_kg_over_threshold = price_per_kg_over_threshold
    pricing.base_distance_km = base_distance_km
    pricing.price_per_km = price_per_km
    pricing.pack1_price = pack1_price
    pricing.pack2_price = pack2_price
    pricing.pack3_price = pack3_price
    pricing.pack6_price = pack6_price
    pricing.robe_carton_price = robe_carton_price
    pricing.tape_price = tape_price
    pricing.paper_price = paper_price
    pricing.mattress_cover_price = mattress_cover_price
    pricing.packing_labor_per_hour = packing_labor_per_hour
    pricing.estimate_low_multiplier = estimate_low_multiplier
    pricing.estimate_high_multiplier = estimate_high_multiplier

    db.commit()

    logger.info(f"Pricing config updated for company {company.slug} by {current_user.email}")

    return RedirectResponse(
        url=f"/{company_slug}/admin/pricing?success=true",
        status_code=303
    )


# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@app.get("/{company_slug}/admin/analytics", response_class=HTMLResponse)
def analytics_dashboard(
    request: Request,
    company_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analytics dashboard with key metrics"""
    company = verify_company_access(company_slug, current_user)

    # Calculate date range (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Total quotes (all jobs created in last 30 days)
    total_quotes = db.query(Job).filter(
        Job.company_id == company.id,
        Job.created_at >= thirty_days_ago
    ).count()

    # Submitted quotes (with contact info)
    submitted_quotes = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status.in_(['awaiting_approval', 'approved', 'rejected']),
        Job.submitted_at >= thirty_days_ago
    ).count()

    # Approved quotes
    approved_quotes = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status == 'approved',
        Job.approved_at >= thirty_days_ago
    ).count()

    # Photos analyzed
    photos_analyzed = db.query(UsageAnalytics).filter(
        UsageAnalytics.company_id == company.id,
        UsageAnalytics.event_type == 'photo_analyzed',
        UsageAnalytics.recorded_at >= thirty_days_ago
    ).count()

    # AI costs
    ai_costs = db.query(func.sum(UsageAnalytics.ai_cost_usd)).filter(
        UsageAnalytics.company_id == company.id,
        UsageAnalytics.recorded_at >= thirty_days_ago
    ).scalar() or 0.0

    # Calculate metrics
    submission_rate = round((submitted_quotes / total_quotes * 100) if total_quotes > 0 else 0, 1)
    approval_rate = round((approved_quotes / submitted_quotes * 100) if submitted_quotes > 0 else 0, 1)
    approval_rate_overall = round((approved_quotes / total_quotes * 100) if total_quotes > 0 else 0, 1)
    avg_cost_per_photo = (ai_costs / photos_analyzed) if photos_analyzed > 0 else 0
    ai_cost_gbp = ai_costs * 0.82  # Approximate USD to GBP conversion

    # Average response time (hours from submission to approval)
    approved_jobs = db.query(Job).filter(
        Job.company_id == company.id,
        Job.status == 'approved',
        Job.approved_at >= thirty_days_ago,
        Job.submitted_at.isnot(None)
    ).all()

    avg_response_hours = 0
    if approved_jobs:
        total_hours = sum([
            (job.approved_at - job.submitted_at).total_seconds() / 3600
            for job in approved_jobs
        ])
        avg_response_hours = round(total_hours / len(approved_jobs), 1)

    # Average quote value
    avg_quote_value = 0
    approved_with_price = db.query(func.avg((Job.custom_price_low + Job.custom_price_high) / 2)).filter(
        Job.company_id == company.id,
        Job.status == 'approved',
        Job.custom_price_low.isnot(None),
        Job.custom_price_high.isnot(None)
    ).scalar()
    if approved_with_price:
        avg_quote_value = round(approved_with_price, 0)

    # Recent events
    recent_events = db.query(UsageAnalytics).filter(
        UsageAnalytics.company_id == company.id
    ).order_by(UsageAnalytics.recorded_at.desc()).limit(20).all()

    metrics = {
        'total_quotes': total_quotes,
        'submitted_quotes': submitted_quotes,
        'approved_quotes': approved_quotes,
        'photos_analyzed': photos_analyzed,
        'submission_rate': submission_rate,
        'approval_rate': approval_rate,
        'approval_rate_overall': approval_rate_overall,
        'total_ai_cost_usd': ai_costs,
        'total_ai_cost_gbp': ai_cost_gbp,
        'avg_cost_per_photo': avg_cost_per_photo,
        'avg_response_hours': avg_response_hours,
        'avg_quote_value': avg_quote_value
    }

    return templates.TemplateResponse("admin_analytics.html", {
        "request": request,
        "title": "Analytics — PrimeHaul OS",
        "company": company,
        "company_slug": company_slug,
        "metrics": metrics,
        "recent_events": recent_events
    })


def track_event(
    company_id: uuid.UUID,
    event_type: str,
    metadata: dict = None,
    ai_cost_usd: float = 0,
    db: Session = None
):
    """
    Track analytics event

    Args:
        company_id: Company UUID
        event_type: Event type (quote_generated, photo_analyzed, job_submitted, job_approved, job_rejected)
        metadata: Additional event data
        ai_cost_usd: AI API cost in USD
        db: Database session
    """
    if not db:
        return

    event = UsageAnalytics(
        company_id=company_id,
        event_type=event_type,
        metadata=metadata or {},
        ai_cost_usd=ai_cost_usd,
        recorded_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()


# ============================================================================
# ML DATA COLLECTION ENDPOINTS
# ============================================================================

@app.post("/api/track")
async def track_user_interaction(
    request: Request,
    event_type: str = Form(...),
    page_url: str = Form(...),
    session_id: Optional[str] = Form(None),
    job_token: Optional[str] = Form(None),
    element_id: Optional[str] = Form(None),
    element_text: Optional[str] = Form(None),
    time_spent_seconds: Optional[float] = Form(None),
    scroll_depth_percent: Optional[int] = Form(None),
    screen_width: Optional[int] = Form(None),
    screen_height: Optional[int] = Form(None),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Track user interaction for ML training and UX optimization

    This endpoint is called by frontend JavaScript to capture all user behavior.
    Every click, scroll, page view, and interaction is stored for analysis.

    Use Cases:
    - Identify drop-off points in customer journey
    - Optimize UI based on real user behavior
    - Train ML models for lead scoring
    - A/B test effectiveness measurement
    """
    try:
        # Get or create session ID
        if not session_id:
            session_id = str(uuid.uuid4())

        # Get company from request state if available
        company_id = None
        if hasattr(request.state, 'company'):
            company_id = request.state.company.id

        # Parse device type from user agent
        user_agent = request.headers.get('user-agent', '')
        device_type = 'desktop'
        if 'mobile' in user_agent.lower():
            device_type = 'mobile'
        elif 'tablet' in user_agent.lower():
            device_type = 'tablet'

        # Extract browser
        browser = user_agent.split()[0] if user_agent else 'unknown'

        # Parse metadata JSON if provided
        meta_dict = {}
        if metadata:
            try:
                meta_dict = json.loads(metadata)
            except:
                pass

        # Create interaction record
        interaction = UserInteraction(
            session_id=session_id,
            job_token=job_token,
            company_id=company_id,
            event_type=event_type,
            page_url=page_url,
            element_id=element_id,
            element_text=element_text[:200] if element_text else None,
            time_spent_seconds=time_spent_seconds,
            scroll_depth_percent=scroll_depth_percent,
            device_type=device_type,
            browser=browser[:100],
            screen_width=screen_width,
            screen_height=screen_height,
            ip_address=request.client.host,
            user_agent=user_agent[:500],
            metadata=meta_dict,
            recorded_at=datetime.utcnow()
        )

        db.add(interaction)
        db.commit()

        return JSONResponse({
            "ok": True,
            "session_id": session_id  # Return to client for continuity
        })

    except Exception as e:
        logger.error(f"Error tracking interaction: {str(e)}")
        # Don't fail - tracking shouldn't break user experience
        return JSONResponse({"ok": False}, status_code=200)


# ============================================================================
# MARKETPLACE ENDPOINTS - "Uber for Removals"
# ============================================================================
# Customer submits once, companies bid, customer picks winner, we take 15%
# Revenue model: 15% commission on marketplace jobs
# ============================================================================

# ----------------------------
# CUSTOMER-FACING: Landing & Job Submission
# ----------------------------

@app.get("/marketplace", response_class=HTMLResponse)
async def marketplace_landing(request: Request):
    """
    Marketplace landing page - Public facing
    Customer starts their removal quote journey here
    """
    return templates.TemplateResponse("marketplace_landing.html", {
        "request": request
    })


@app.post("/marketplace/start")
async def marketplace_start(request: Request, db: Session = Depends(get_db)):
    """
    Create a new marketplace job (NOT company-specific)
    Returns redirect to marketplace survey flow
    """
    # Generate unique token for this marketplace job
    token = f"m_{uuid.uuid4().hex[:12]}"  # m_ prefix for marketplace
    
    # Create marketplace job record
    job = MarketplaceJob(
        token=token,
        status='in_progress',
        broadcast_radius_miles=50,  # Default 50-mile radius
        commission_rate=0.15  # 15% commission
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Created marketplace job: {job.id} with token: {token}")
    
    # Redirect to marketplace survey flow (reuse existing survey pages but marketplace URLs)
    return RedirectResponse(url=f"/marketplace/{token}/move", status_code=303)


@app.get("/marketplace/{token}/move", response_class=HTMLResponse)
def marketplace_move_get(request: Request, token: str, db: Session = Depends(get_db)):
    """Marketplace job - pickup/dropoff selection"""
    job = db.query(MarketplaceJob).filter(MarketplaceJob.token == token).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generic branding (not company-specific)
    branding = {
        "company_name": "PrimeHaul",
        "logo_url": "/static/logo.png",
        "primary_color": "#2ee59d",
        "secondary_color": "#1a1a1a"
    }
    
    return templates.TemplateResponse("move_map.html", {
        "request": request,
        "token": token,
        "company_slug": "marketplace",  # Use "marketplace" as slug for URLs
        "branding": branding,
        "title": "Set your move - PrimeHaul",
        "nav_title": "Set your move",
        "back_url": f"/marketplace",
        "progress": 25,
        "mapbox_token": os.getenv("MAPBOX_ACCESS_TOKEN", ""),
        "pickup": job.pickup,
        "dropoff": job.dropoff,
    })


@app.post("/marketplace/{token}/move")
def marketplace_move_post(
    request: Request,
    token: str,
    pickup_label: str = Form(""),
    pickup_lat: str = Form(""),
    pickup_lng: str = Form(""),
    dropoff_label: str = Form(""),
    dropoff_lat: str = Form(""),
    dropoff_lng: str = Form(""),
    db: Session = Depends(get_db)
):
    """Save marketplace job location"""
    job = db.query(MarketplaceJob).filter(MarketplaceJob.token == token).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        p_lat = float(pickup_lat); p_lng = float(pickup_lng)
        d_lat = float(dropoff_lat); d_lng = float(dropoff_lng)
    except ValueError:
        return RedirectResponse(url=f"/marketplace/{token}/move?err=coords", status_code=303)
    
    # Extract city names from labels
    pickup_city = pickup_label.split(',')[0] if ',' in pickup_label else pickup_label
    dropoff_city = dropoff_label.split(',')[0] if ',' in dropoff_label else dropoff_label
    
    job.pickup = {"label": pickup_label, "lat": p_lat, "lng": p_lng}
    job.dropoff = {"label": dropoff_label, "lat": d_lat, "lng": d_lng}
    job.pickup_city = pickup_city[:100]
    job.dropoff_city = dropoff_city[:100]
    db.commit()
    
    return RedirectResponse(url=f"/marketplace/{token}/property", status_code=303)


# TODO: Add remaining marketplace customer flow endpoints:
# - /marketplace/{token}/property (GET/POST)
# - /marketplace/{token}/rooms (GET/POST)
# - /marketplace/{token}/room/{room_id} (GET/POST with photo upload)
# - /marketplace/{token}/contact (GET/POST - final submission + broadcast trigger)
# These will reuse existing templates but with marketplace branding


@app.get("/marketplace/{token}/quotes", response_class=HTMLResponse)
def marketplace_quotes_get(request: Request, token: str, db: Session = Depends(get_db)):
    """
    Customer views all bids for their marketplace job
    Compare prices, crew sizes, company ratings
    """
    job = db.query(MarketplaceJob).filter(MarketplaceJob.token == token).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all bids for this job (pending or accepted)
    bids = db.query(Bid).filter(
        Bid.marketplace_job_id == job.id,
        Bid.status.in_(['pending', 'accepted', 'rejected'])
    ).order_by(Bid.price.asc()).all()  # Sort by price (lowest first)
    
    # Eager load company info for each bid
    for bid in bids:
        bid.company = db.query(Company).filter(Company.id == bid.company_id).first()
    
    # Get winning company if job is awarded
    winning_company = None
    if job.winning_company_id:
        winning_company = db.query(Company).filter(Company.id == job.winning_company_id).first()
    
    # Calculate hours until bid deadline
    hours_until_deadline = 48
    if job.bid_deadline:
        time_diff = job.bid_deadline - datetime.utcnow()
        hours_until_deadline = max(0, int(time_diff.total_seconds() / 3600))
    
    return templates.TemplateResponse("marketplace_quotes.html", {
        "request": request,
        "job": job,
        "bids": bids,
        "winning_company": winning_company,
        "hours_until_deadline": hours_until_deadline,
        "now": datetime.utcnow(),
        "timedelta": timedelta
    })


@app.post("/marketplace/{token}/quotes/{bid_id}/accept")
def marketplace_accept_bid(
    request: Request,
    token: str,
    bid_id: str,
    db: Session = Depends(get_db)
):
    """
    Customer accepts a bid - creates winner, rejects others, charges commission
    """
    job = db.query(MarketplaceJob).filter(MarketplaceJob.token == token).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Use marketplace.accept_bid() function
    try:
        result = marketplace.accept_bid(str(job.id), bid_id, db)
        logger.info(f"Bid accepted: Job {job.id}, Bid {bid_id}, Commission: {result['commission_amount']}")
        
        # Redirect back to quotes page to show success
        return RedirectResponse(url=f"/marketplace/{token}/quotes?success=true", status_code=303)
        
    except Exception as e:
        logger.error(f"Error accepting bid: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------
# COMPANY-FACING: Marketplace Dashboard & Bidding
# ----------------------------

@app.get("/{company_slug}/admin/marketplace", response_class=HTMLResponse)
def company_marketplace_dashboard(
    request: Request,
    company_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Company marketplace dashboard
    Shows: available jobs, active bids, won jobs
    """
    company = db.query(Company).filter(Company.slug == company_slug).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Verify user belongs to this company
    if current_user.company_id != company.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get available jobs (open for bids, not yet bid on by this company)
    existing_bid_job_ids = db.query(Bid.marketplace_job_id).filter(
        Bid.company_id == company.id
    ).subquery()
    
    available_jobs = db.query(MarketplaceJob).filter(
        MarketplaceJob.status.in_(['open_for_bids', 'bids_received']),
        ~MarketplaceJob.id.in_(existing_bid_job_ids)
    ).order_by(MarketplaceJob.created_at.desc()).limit(20).all()
    
    # Add estimated price ranges to jobs
    for job in available_jobs:
        # Simple estimate: £30-40/CBM + £200-300 callout
        cbm = float(job.total_cbm or 0)
        job.estimate_low = (cbm * 30) + 200
        job.estimate_high = (cbm * 40) + 300
    
    # Get company's active bids
    my_bids = db.query(Bid).filter(
        Bid.company_id == company.id,
        Bid.status == 'pending'
    ).order_by(Bid.created_at.desc()).all()
    
    # Eager load jobs for bids
    for bid in my_bids:
        bid.job = db.query(MarketplaceJob).filter(MarketplaceJob.id == bid.marketplace_job_id).first()
        # Count total bids for this job
        bid.job.bid_count = db.query(func.count(Bid.id)).filter(
            Bid.marketplace_job_id == bid.marketplace_job_id
        ).scalar()
    
    # Get won jobs (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    won_jobs = db.query(Bid).filter(
        Bid.company_id == company.id,
        Bid.status == 'accepted',
        Bid.accepted_at >= thirty_days_ago
    ).order_by(Bid.accepted_at.desc()).all()
    
    for bid in won_jobs:
        bid.job = db.query(MarketplaceJob).filter(MarketplaceJob.id == bid.marketplace_job_id).first()
    
    # Calculate stats
    stats = {
        "available_jobs": len(available_jobs),
        "active_bids": len(my_bids),
        "jobs_won": len(won_jobs),
        "win_rate": 0
    }
    
    # Calculate win rate (last 30 days)
    total_bids_30d = db.query(func.count(Bid.id)).filter(
        Bid.company_id == company.id,
        Bid.created_at >= thirty_days_ago
    ).scalar() or 0
    
    if total_bids_30d > 0:
        stats["win_rate"] = int((len(won_jobs) / total_bids_30d) * 100)
    
    return templates.TemplateResponse("marketplace_dashboard.html", {
        "request": request,
        "company": company,
        "available_jobs": available_jobs,
        "my_bids": my_bids,
        "won_jobs": won_jobs,
        "stats": stats,
        "now": datetime.utcnow(),
        "timedelta": timedelta
    })


@app.get("/{company_slug}/admin/marketplace/job/{job_id}", response_class=HTMLResponse)
def company_marketplace_job_detail(
    request: Request,
    company_slug: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Company views full marketplace job details + submits bid
    Shows: inventory, photos, pricing calculator, bid form
    """
    company = db.query(Company).filter(Company.slug == company_slug).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    job = db.query(MarketplaceJob).filter(MarketplaceJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get rooms and items
    rooms = db.query(MarketplaceRoom).filter(MarketplaceRoom.marketplace_job_id == job.id).all()
    for room in rooms:
        room.items = db.query(MarketplaceItem).filter(MarketplaceItem.marketplace_room_id == room.id).all()
        room.photos = db.query(MarketplacePhoto).filter(MarketplacePhoto.marketplace_room_id == room.id).all()
    
    # Get company pricing config
    pricing = db.query(PricingConfig).filter(PricingConfig.company_id == company.id).first()
    if not pricing:
        # Create default pricing if not exists
        pricing = PricingConfig(
            company_id=company.id,
            price_per_cbm=35.00,
            callout_fee=250.00,
            bulky_item_fee=25.00,
            fragile_item_fee=15.00
        )
        db.add(pricing)
        db.commit()
    
    # Calculate suggested price
    total_cbm = float(job.total_cbm or 0)
    base_price = float(pricing.callout_fee)
    cbm_price = total_cbm * float(pricing.price_per_cbm)
    
    # Count bulky/fragile items by weight threshold
    bulky_count = 0
    fragile_count = 0
    threshold = float(pricing.bulky_weight_threshold_kg or 50)
    for room in rooms:
        for item in room.items:
            qty = item.quantity or 1
            if item.weight_kg and float(item.weight_kg) > threshold:
                bulky_count += qty
            if item.fragile:
                fragile_count += qty

    bulky_surcharge = bulky_count * float(pricing.bulky_item_fee)
    fragile_surcharge = fragile_count * float(pricing.fragile_item_fee)
    
    suggested_price = base_price + cbm_price + bulky_surcharge + fragile_surcharge
    suggested_price = round(suggested_price / 5) * 5  # Round to nearest £5
    
    # Check if company already bid on this job
    existing_bid = db.query(Bid).filter(
        Bid.marketplace_job_id == job.id,
        Bid.company_id == company.id
    ).first()
    
    # Count total bids
    bid_count = db.query(func.count(Bid.id)).filter(Bid.marketplace_job_id == job.id).scalar() or 0
    
    # Calculate hours until deadline
    hours_until_deadline = 48
    if job.bid_deadline:
        time_diff = job.bid_deadline - datetime.utcnow()
        hours_until_deadline = max(0, int(time_diff.total_seconds() / 3600))
    
    return templates.TemplateResponse("marketplace_job_detail.html", {
        "request": request,
        "company": company,
        "job": job,
        "rooms": rooms,
        "pricing": pricing,
        "suggested_price": suggested_price,
        "existing_bid": existing_bid,
        "bid_count": bid_count,
        "hours_until_deadline": hours_until_deadline
    })


@app.post("/{company_slug}/admin/marketplace/job/{job_id}/bid")
def company_submit_bid(
    request: Request,
    company_slug: str,
    job_id: str,
    price: float = Form(...),
    crew_size: Optional[int] = Form(None),
    estimated_duration_hours: Optional[int] = Form(None),
    message: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Company submits a bid on marketplace job
    """
    company = db.query(Company).filter(Company.slug == company_slug).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    job = db.query(MarketplaceJob).filter(MarketplaceJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate bid is still possible
    if job.status not in ['open_for_bids', 'bids_received']:
        raise HTTPException(status_code=400, detail="Job is no longer accepting bids")
    
    # Check if already bid
    existing_bid = db.query(Bid).filter(
        Bid.marketplace_job_id == job.id,
        Bid.company_id == company.id
    ).first()
    
    if existing_bid:
        raise HTTPException(status_code=400, detail="You have already submitted a bid for this job")
    
    # Create bid
    bid = Bid(
        marketplace_job_id=job.id,
        company_id=company.id,
        price=price,
        message=message[:500] if message else None,
        estimated_duration_hours=estimated_duration_hours,
        crew_size=crew_size,
        status='pending',
        expires_at=job.bid_deadline,
        auto_generated=False
    )
    db.add(bid)
    
    # Update job status
    if job.status == 'open_for_bids':
        job.status = 'bids_received'
    
    # Update broadcast record
    broadcast = db.query(JobBroadcast).filter(
        JobBroadcast.marketplace_job_id == job.id,
        JobBroadcast.company_id == company.id
    ).first()
    if broadcast:
        broadcast.bid_submitted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(bid)
    
    # Send notification to customer
    try:
        notifications.send_new_bid_notification(job, bid, db)
    except Exception as e:
        logger.error(f"Failed to send bid notification: {e}")
    
    logger.info(f"Bid submitted: Company {company.id} → Job {job.id}, Price £{price}")
    
    # Redirect back to marketplace dashboard with success message
    return RedirectResponse(
        url=f"/{company_slug}/admin/marketplace?bid_success=true",
        status_code=303
    )


# ----------------------------
# ADMIN: Manual Job Broadcasting (Dev Tools)
# ----------------------------

@app.post("/admin/marketplace/job/{job_id}/broadcast")
def admin_broadcast_job(
    job_id: str,
    radius_miles: int = Form(50),
    db: Session = Depends(get_db)
):
    """
    Manually trigger job broadcast to companies
    (This would normally happen automatically when customer submits job)
    """
    try:
        result = marketplace.broadcast_job_to_companies(job_id, db, radius_miles)
        return JSONResponse({
            "success": True,
            "result": result
        })
    except Exception as e:
        logger.error(f"Error broadcasting job: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------
# MARKETPLACE METRICS (for dev dashboard)
# ----------------------------

@app.get("/admin/marketplace/stats")
def get_marketplace_stats_endpoint(db: Session = Depends(get_db)):
    """Get marketplace statistics for dev dashboard"""
    stats = marketplace.get_marketplace_stats(db)
    return JSONResponse(stats)

