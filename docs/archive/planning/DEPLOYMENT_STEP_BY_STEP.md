# 🚀 PrimeHaul OS - Complete Deployment Guide

**Step-by-step instructions to get PrimeHaul OS from your computer to the internet**

This guide assumes you're starting from scratch. Follow every step carefully!

---

## 📋 What You'll Need

Before starting, make sure you have:
- [ ] Your computer (Mac/Windows/Linux - any works)
- [ ] primehaul.co.uk domain name (already registered)
- [ ] A credit/debit card for hosting costs (~£15-20/month)
- [ ] 2-3 hours of focused time

**Total Cost to Launch:**
- Hosting: £7-15/month (Railway or Render)
- Database: £7/month (Railway PostgreSQL)
- Stripe: Free (they take % of transactions)
- Email: Free initially (Gmail SMTP)
- **Total: ~£15-20/month**

---

## Phase 1: Local Setup & Testing (Do This First!)

### Step 1: Install Required Software

**macOS:**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install PostgreSQL (for local testing)
brew install postgresql@15
brew services start postgresql@15

# Verify installations
python3 --version  # Should show 3.11+
psql --version     # Should show PostgreSQL 15+
```

**Windows:**
1. Download Python 3.11+ from python.org
2. Download PostgreSQL from postgresql.org/download/windows
3. Install both (check "Add to PATH" during install)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql-15
sudo systemctl start postgresql
```

---

### Step 2: Set Up Your Local Database

**Create the database:**
```bash
# macOS/Linux:
createdb primehaul_local

# Windows (in PostgreSQL shell):
createdb primehaul_local
```

**Test database connection:**
```bash
psql primehaul_local
# You should see: primehaul_local=#
# Type \q to exit
```

---

### Step 3: Configure Environment Variables

**Create `.env` file in the project root:**
```bash
cd /Users/primehaul/PrimeHaul/primehaul-os
cp .env.example .env
nano .env  # Or open in any text editor
```

**Edit `.env` with your settings:**
```bash
# Database
DATABASE_URL=postgresql://localhost/primehaul_local

# Security (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_SECRET_KEY=<paste-your-generated-secret-here>

# OpenAI (you already have this)
OPENAI_API_KEY=sk-your-existing-key
OPENAI_VISION_MODEL=gpt-4o-mini

# Mapbox (you already have this)
MAPBOX_ACCESS_TOKEN=pk.eyJ1...your-existing-token

# Email (use Gmail for now - free!)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=<your-app-password>  # See Step 4
SMTP_FROM_EMAIL=noreply@primehaul.co.uk
SMTP_FROM_NAME=PrimeHaul

# Stripe (get from dashboard.stripe.com - use TEST keys for now!)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...  # We'll create this

# Dev Dashboard
DEV_DASHBOARD_PASSWORD=dev2025

# App
APP_ENV=development
APP_URL=http://localhost:8000
```

**Save and close the file**

---

### Step 4: Set Up Gmail SMTP (For Sending Emails)

**Why:** You need to send emails when jobs are broadcast, bids are submitted, etc.

1. **Go to your Google Account:** https://myaccount.google.com/
2. **Security → 2-Step Verification** - Turn this ON (required)
3. **Security → App Passwords** - Generate a new app password
   - Select "Mail" and "Other (Custom name)"
   - Name it "PrimeHaul OS"
   - Copy the 16-character password
4. **Paste this password into your `.env` file as `SMTP_PASSWORD`**

**Test email sending later after running the app!**

---

### Step 5: Set Up Stripe (For Payments)

**Create Stripe Account:**
1. Go to https://dashboard.stripe.com/register
2. Sign up (free)
3. Skip onboarding (you're in TEST mode)

**Get your TEST API keys:**
1. Dashboard → Developers → API Keys
2. Copy "Publishable key" (starts with pk_test_...)
3. Copy "Secret key" (starts with sk_test_...)
4. Paste both into your `.env` file

**Create a Subscription Product:**
1. Dashboard → Products → Add Product
   - Name: "PrimeHaul OS Professional"
   - Description: "Unlimited AI-powered removal quotes"
   - Price: £99.00 GBP / month
   - Billing period: Monthly
   - Click "Save"
2. Copy the Price ID (starts with price_...)
3. Paste into `.env` as `STRIPE_PRICE_ID`

**Create Webhook (for subscription events):**
1. Dashboard → Developers → Webhooks → Add Endpoint
2. Endpoint URL: `http://localhost:8000/webhooks/stripe` (for local testing)
3. Events to listen to:
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
4. Copy the "Signing secret" (starts with whsec_...)
5. Paste into `.env` as `STRIPE_WEBHOOK_SECRET`

---

### Step 6: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi  # Should show fastapi
pip list | grep sqlalchemy  # Should show sqlalchemy
```

---

### Step 7: Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic upgrade head

# This creates all tables:
# - companies, users, pricing_configs, jobs, rooms, items, photos
# - marketplace_jobs, bids, job_broadcasts, commissions
# - admin_notes, usage_analytics, etc.

# Verify tables were created
psql primehaul_local -c "\dt"
# You should see ~20 tables listed
```

**If you see errors:** Check your `DATABASE_URL` in `.env` is correct

---

### Step 8: Create Your First Test Company

**Run Python to create a test company:**
```bash
python3
```

```python
from app.database import get_db, engine
from app.models import Company, User, PricingConfig
from app.auth import hash_password
import uuid

db = next(get_db())

# Create test company
company = Company(
    slug="test-removals",
    company_name="Test Removals Ltd",
    email="test@primehaul.co.uk",
    subscription_status="trial",
    is_active=True,
    primary_color="#2ee59d",
    secondary_color="#1a1a1a"
)
db.add(company)
db.commit()
db.refresh(company)

# Create owner user
user = User(
    company_id=company.id,
    email="test@primehaul.co.uk",
    password_hash=hash_password("test123"),
    full_name="Test User",
    role="owner",
    is_active=True
)
db.add(user)

# Create default pricing
pricing = PricingConfig(
    company_id=company.id,
    price_per_cbm=35.00,
    callout_fee=250.00,
    bulky_item_fee=25.00,
    fragile_item_fee=15.00
)
db.add(pricing)

db.commit()
print(f"✅ Created company: {company.slug}")
print(f"✅ Created user: {user.email} (password: test123)")
exit()
```

---

### Step 9: Run the App Locally

```bash
# Make sure you're in the project directory
cd /Users/primehaul/PrimeHaul/primehaul-os

# Make sure virtual environment is activated
source venv/bin/activate

# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 10: Test Locally (IMPORTANT!)

**Open your browser and test these URLs:**

1. **Marketplace Landing Page:**
   - http://localhost:8000/marketplace
   - Should show beautiful landing page
   - Click "Start Free Survey"

2. **Dev Dashboard:**
   - http://localhost:8000/dev-dashboard
   - Password: `dev2025`
   - Should show all metrics

3. **Company Admin Login:**
   - http://localhost:8000/test-removals/admin
   - Email: test@primehaul.co.uk
   - Password: test123
   - Should show dashboard

4. **Company Marketplace Dashboard:**
   - http://localhost:8000/test-removals/admin/marketplace
   - Should show "Available Jobs" (empty for now)

**If all 4 work → You're ready for production! 🎉**

---

## Phase 2: Deploy to Production

### Step 11: Choose a Hosting Provider

**Recommended: Railway (Easiest)**
- Pros: Super easy, auto-deploys from Git, includes database
- Cons: £15-20/month
- Best for: Getting live FAST

**Alternative: Render (Cheaper)**
- Pros: Free tier available, easy setup
- Cons: Free tier sleeps after inactivity
- Best for: Testing before paying

**Let's use Railway:**

---

### Step 12: Deploy to Railway

1. **Create Railway Account:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Free trial includes $5 credit

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select primehaul-os repository

3. **Add PostgreSQL Database:**
   - In your project, click "+ New"
   - Select "Database"
   - Choose "PostgreSQL"
   - Wait for it to provision (~2 min)

4. **Configure Environment Variables:**
   - Click on your app service
   - Go to "Variables" tab
   - Click "Raw Editor"
   - Paste ALL variables from your `.env` file
   - **IMPORTANT CHANGES:**
     - `DATABASE_URL` → Use Railway's database URL (click "Connect" on PostgreSQL service, copy "Connection URL")
     - `APP_ENV=production`
     - `APP_URL=https://your-app.railway.app` (you'll get this URL after deploy)
   - Click "Update Variables"

5. **Deploy:**
   - Railway automatically deploys on git push
   - Wait 2-5 minutes for first deploy
   - Check "Deployments" tab for status

6. **Run Migrations:**
   - Once deployed, click "Deployments"
   - Click the three dots → "View Logs"
   - You need to run migrations manually:
   - Go to "Settings" → "Generate Domain"
   - Copy the domain (e.g., primehaul-os-production.up.railway.app)
   - SSH into Railway (they'll show you how in dashboard)
   - Run: `alembic upgrade head`

7. **Test Your Live App:**
   - Visit https://your-app.railway.app/marketplace
   - Should work exactly like local!

---

### Step 13: Connect Your Domain (primehaul.co.uk)

**In Railway:**
1. Go to your app service
2. Settings → Domains
3. Click "Custom Domain"
4. Enter: `app.primehaul.co.uk`
5. Railway will give you a CNAME record

**In your Domain Registrar (where you bought primehaul.co.uk):**
1. Go to DNS settings
2. Add CNAME record:
   - Name: `app`
   - Value: `your-app.railway.app` (from Railway)
   - TTL: 3600
3. Save

**Wait 10-60 minutes for DNS to propagate**

**Test:** https://app.primehaul.co.uk/marketplace

---

### Step 14: Update Stripe Webhook for Production

**Now that you have a live URL:**

1. Go to Stripe Dashboard → Webhooks
2. Edit your webhook
3. Change URL to: `https://app.primehaul.co.uk/webhooks/stripe`
4. Save

**OR create a new webhook for production:**
1. Add Endpoint → `https://app.primehaul.co.uk/webhooks/stripe`
2. Select same events as before
3. Copy new webhook secret
4. Update `STRIPE_WEBHOOK_SECRET` in Railway environment variables

---

### Step 15: Switch to Stripe LIVE Mode

**Once you're ready to accept real payments:**

1. Stripe Dashboard → top-left toggle → Switch to "Live mode"
2. Go to API Keys → Reveal live keys
3. Copy live keys (pk_live_... and sk_live_...)
4. Update Railway environment variables:
   - `STRIPE_SECRET_KEY=sk_live_...`
   - `STRIPE_PUBLISHABLE_KEY=pk_live_...`
5. Create LIVE price for £99/month (same as test mode)
6. Update `STRIPE_PRICE_ID` in Railway

---

## Phase 3: Launch Checklist

### Step 16: Pre-Launch Testing

**Test EVERYTHING on production before launching:**

- [ ] Marketplace landing page loads
- [ ] Customer can start survey
- [ ] Customer can upload photos
- [ ] AI analyzes photos correctly
- [ ] Customer can submit job
- [ ] Job broadcasts to companies (check email)
- [ ] Company receives email notification
- [ ] Company can view job details
- [ ] Company can submit bid
- [ ] Customer receives bid notification email
- [ ] Customer can view all bids
- [ ] Customer can accept a bid
- [ ] Winner receives notification
- [ ] Losers receive notification
- [ ] Commission is calculated correctly
- [ ] Company signup works
- [ ] Company can login
- [ ] Company dashboard loads
- [ ] Subscription checkout works
- [ ] Stripe webhook processes events
- [ ] Dev dashboard shows correct metrics

---

### Step 17: Create Your First REAL Company

**Instead of "test-removals", create your first real customer:**

1. Go to https://app.primehaul.co.uk/auth/signup
2. Fill out signup form:
   - Company name: "ABC Removals"
   - Your email
   - Strong password
3. They get 30-day free trial automatically
4. Email them: "Your PrimeHaul OS account is ready!"

---

### Step 18: Marketing Setup (Get First Customers)

**Week 1: Manual outreach (FREE)**

**Find 10 removal companies:**
```
1. Google "removal companies London" (or your area)
2. Find companies with websites (not just aggregators)
3. Get their contact email (usually on Contact page)
4. Email them this template:
```

**Email Template:**
```
Subject: Free 30-day trial - AI-powered removal quotes

Hi [Company Name],

I built a tool that generates removal quotes in 5 minutes using AI.

Instead of typing everything manually, your customers just:
1. Take photos with their phone
2. AI analyzes everything
3. You get a detailed quote instantly

Try it free for 30 days: https://app.primehaul.co.uk/auth/signup

Your custom URL: app.primehaul.co.uk/s/[company-slug]
Price after trial: £99/month (unlimited quotes)

Want a demo? Reply to this email.

Best,
[Your Name]
PrimeHaul OS
```

**Goal: Get 5 companies signed up in Week 1**

---

### Step 19: Launch Marketplace

**Once you have 5+ B2B customers signed up:**

1. **Test marketplace with real job:**
   - Go to https://app.primehaul.co.uk/marketplace
   - Submit a test job (your own house move)
   - Verify 5 companies receive email
   - Ask them to submit test bids
   - Accept one bid
   - Verify commission is charged

2. **Launch Google Ads (£500 budget):**
   - Campaign: "Removal quotes UK"
   - Keywords: "removal quote", "moving quote", "removal cost calculator"
   - Ad copy: "Get removal quotes in 5 min - AI-powered"
   - Landing page: https://app.primehaul.co.uk/marketplace
   - Goal: 10 real customer submissions in Week 1

3. **Monitor metrics:**
   - Dev dashboard: https://app.primehaul.co.uk/dev-dashboard
   - Track: jobs submitted, bids received, acceptance rate
   - Target: 50%+ jobs get bids, 30%+ acceptance rate

---

### Step 20: Scale (Month 2-3)

**If marketplace is working (bids coming in, customers accepting):**

1. **Increase Google Ads to £2,000/month**
   - Target: 50 marketplace jobs/month
   - Revenue: 50 × £700 × 15% = £5,250/month commission

2. **Keep selling B2B:**
   - Target: 50 companies × £99 = £4,950/month MRR
   - Total: £10,200/month combined revenue

3. **Add features:**
   - Company reviews/ratings
   - SMS notifications (Twilio)
   - Auto-bidding for companies
   - Advanced analytics

---

## Common Issues & Solutions

### "Database connection failed"
**Fix:** Check `DATABASE_URL` in environment variables. Should be `postgresql://...`

### "Stripe webhook failing"
**Fix:**
1. Check webhook URL is correct (https://app.primehaul.co.uk/webhooks/stripe)
2. Check `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard
3. View webhook logs in Stripe dashboard

### "Emails not sending"
**Fix:**
1. Check Gmail app password is correct
2. Check 2FA is enabled on Google account
3. View logs: Railway dashboard → View Logs
4. Look for SMTP errors

### "Migration failed: relation already exists"
**Fix:**
```bash
# Drop all tables and re-run migrations
psql $DATABASE_URL
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
alembic upgrade head
```

### "Company can't login"
**Fix:** Check password was hashed correctly:
```python
from app.auth import hash_password, verify_password
verify_password("test123", user.password_hash)  # Should return True
```

---

## Monitoring & Maintenance

### Daily Checks (5 minutes)
1. **Dev dashboard:** https://app.primehaul.co.uk/dev-dashboard
   - Any errors?
   - Any new signups?
   - Any marketplace jobs?

2. **Railway dashboard:**
   - Check logs for errors
   - Check database usage (should be < 1GB for now)
   - Check monthly bill (should be ~£15-20)

### Weekly Checks (15 minutes)
1. **Stripe dashboard:**
   - How many subscriptions active?
   - Any failed payments?
   - Total revenue?

2. **Google Ads (if running):**
   - How many clicks?
   - Cost per job submission?
   - Conversion rate?

3. **Database backup:**
   - Railway auto-backs up, but good to verify
   - Settings → Backups → View latest

---

## Next Steps After Launch

### Month 1: Get to 10 customers
- [ ] 5 B2B companies (£495 MRR)
- [ ] 5 marketplace jobs (£350-500 commission)
- [ ] Total: £850-1,000 revenue

### Month 2-3: Scale to £10k MRR
- [ ] 50 B2B companies (£4,950 MRR)
- [ ] 50 marketplace jobs (£5,250 commission)
- [ ] Total: £10,200/month

### Month 4-12: Hit £100k ARR
- [ ] 200 B2B companies (£19,800 MRR)
- [ ] 200 marketplace jobs (£21,000 commission)
- [ ] Total: £40,800/month = £489,600/year

---

## Emergency Contacts

**If something breaks:**
1. Check Railway logs first
2. Check Stripe dashboard for payment issues
3. Check database is running (Railway → PostgreSQL → Status)
4. Email support@railway.app (fast response)

**Your Stack:**
- **Code:** GitHub (backed up automatically)
- **Hosting:** Railway
- **Database:** Railway PostgreSQL (auto-backed up daily)
- **Email:** Gmail SMTP (upgrade to SendGrid at 1000+ users)
- **Payments:** Stripe
- **Domain:** Wherever you registered primehaul.co.uk

---

## You're Ready to Launch! 🚀

**Recap what you've built:**
- ✅ AI-powered removal quote system
- ✅ Multi-tenant B2B SaaS (£99/month per company)
- ✅ Marketplace bidding platform (15% commission)
- ✅ Custom branding for each company
- ✅ Stripe billing + subscriptions
- ✅ Email notifications
- ✅ Analytics dashboard
- ✅ Mobile-first design

**Revenue potential:**
- Month 1: £1,000
- Month 3: £10,000
- Month 12: £40,000
- Year 2: £100,000+

**Time to market: 2-3 hours** (if you follow this guide)

**NOW GO LAUNCH IT! 💪**

---

Need help? Email me or check:
- Railway docs: https://docs.railway.app
- Stripe docs: https://stripe.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- Alembic docs: https://alembic.sqlalchemy.org

**Good luck! You've got this! 🎉**
