# 🚀 LAUNCH TODAY - Step-by-Step Guide
**Goal:** Get PrimeHaul OS live and accepting real customers in 6 hours
**Date:** December 30, 2025

---

## ⏰ TIME BUDGET (6 hours total)

- **Hour 1:** Environment setup (database, API keys)
- **Hour 2:** Email configuration + testing
- **Hour 3-4:** Fix marketplace flow
- **Hour 5:** Test everything
- **Hour 6:** Deploy to production OR soft launch locally

---

## 📋 STEP-BY-STEP CHECKLIST

### HOUR 1: Environment Setup (60 minutes)

#### ✅ Task 1.1: Install PostgreSQL (15 min)

```bash
# Mac users:
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb primehaul_local

# Test connection
psql primehaul_local
# Type \q to exit

# Windows/Linux users:
# Download from: https://www.postgresql.org/download/
# Or use Railway: https://railway.app (easier!)
```

**Checkpoint:** `psql primehaul_local` connects without error ✅

---

#### ✅ Task 1.2: Update .env File (15 min)

```bash
# Navigate to project
cd /Users/primehaul/PrimeHaul/primehaul-os

# Open .env file
code .env  # or nano .env

# Update these lines:
DATABASE_URL=postgresql://primehaul:password@localhost/primehaul_local
```

**Checkpoint:** .env has real database URL ✅

---

#### ✅ Task 1.3: Get OpenAI API Key (15 min)

1. Go to: https://platform.openai.com/api-keys
2. Sign up / log in
3. Click "Create new secret key"
4. Name it "PrimeHaul OS"
5. Copy the key (starts with `sk-proj-...`)
6. Add billing method (required for API to work)
7. Set spending limit to £20/month (safety)

```bash
# Add to .env:
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

**Cost check:** £0.003 per photo × 15 photos/job × 100 jobs = £4.50/month

**Checkpoint:** OpenAI key in .env ✅

---

#### ✅ Task 1.4: Run Database Migrations (15 min)

```bash
# Install dependencies (if not done yet)
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Should see:
# INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_add_marketplace
```

**Troubleshooting:**
```bash
# If alembic command not found:
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
pip install alembic

# If database connection error:
# Check DATABASE_URL in .env matches your PostgreSQL setup
```

**Checkpoint:** No migration errors, database has tables ✅

---

### HOUR 2: Email Configuration (60 minutes)

#### ✅ Task 2.1: Set Up Gmail App Password (20 min)

**Important:** You NEED 2-factor authentication enabled on your Google account!

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already)
3. Go to: https://myaccount.google.com/apppasswords
4. Select app: "Mail"
5. Select device: "Other" → enter "PrimeHaul OS"
6. Click "Generate"
7. Copy the 16-character password (format: `abcd efgh ijkl mnop`)

```bash
# Add to .env:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop  # Remove spaces!
SMTP_FROM_EMAIL=noreply@primehaul.co.uk
SMTP_FROM_NAME=PrimeHaul
```

**Checkpoint:** Gmail app password added to .env ✅

---

#### ✅ Task 2.2: Test Email Sending (15 min)

```python
# Create test file: test_email.py
from dotenv import load_dotenv
load_dotenv()

from app.notifications import send_email

# Send test email to yourself
result = send_email(
    to_email="YOUR-EMAIL@gmail.com",  # Use your real email!
    subject="🎉 PrimeHaul OS Email Test",
    html_body="""
    <h1>Email System Working!</h1>
    <p>If you're reading this, SMTP is configured correctly.</p>
    <p>You're ready to launch! 🚀</p>
    """
)

print(f"Email sent: {result}")
```

```bash
# Run test
python test_email.py

# Should see:
# [EMAIL SENT] To: your-email@gmail.com, Subject: 🎉 PrimeHaul OS Email Test
# Email sent: True
```

**Check your inbox** - email should arrive in 1-2 minutes.

**Checkpoint:** Test email received ✅

---

#### ✅ Task 2.3: Fix Common Gmail Issues (25 min buffer)

**Issue 1: "Username and Password not accepted"**
```
Solution:
- Make sure you're using App Password, NOT your regular Gmail password
- Remove spaces from app password: abcd-efgh-ijkl-mnop
- Check 2FA is enabled on Google account
```

**Issue 2: "SMTP AUTH extension not supported"**
```
Solution:
- Change port from 465 to 587
- Make sure SMTP_PORT=587 in .env
```

**Issue 3: "Less secure app access"**
```
Solution:
- Google removed this feature in May 2022
- You MUST use App Passwords now (not regular password)
- Enable 2FA first, then generate app password
```

**Alternative if Gmail doesn't work:**
Use SendGrid (5000 free emails/month):
1. Sign up: https://sendgrid.com/pricing/
2. Get API key
3. Update .env:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=YOUR-SENDGRID-API-KEY
```

**Checkpoint:** Email system 100% working ✅

---

### HOUR 3-4: Fix Marketplace Flow (120 minutes)

#### ✅ Task 3.1: Create Marketplace System Company (20 min)

Create file: `create_marketplace_company.py`

```python
from dotenv import load_dotenv
load_dotenv()

from app.database import get_db
from app.models import Company, PricingConfig, User
from app.auth import hash_password
import uuid

db = next(get_db())

# Check if already exists
existing = db.query(Company).filter(Company.slug == "marketplace").first()
if existing:
    print(f"✅ Marketplace company already exists: {existing.id}")
else:
    # Create marketplace system company
    marketplace_company = Company(
        company_name="PrimeHaul Marketplace",
        slug="marketplace",
        email="marketplace@primehaul.co.uk",
        subscription_status="active",
        trial_ends_at=None,
        is_active=True,
        onboarding_completed=True,
        primary_color="#2ee59d",
        secondary_color="#000000"
    )
    db.add(marketplace_company)
    db.commit()
    db.refresh(marketplace_company)

    # Create pricing config
    pricing = PricingConfig(
        company_id=marketplace_company.id,
        price_per_cbm=35.00,
        callout_fee=250.00,
        bulky_item_fee=25.00,
        fragile_item_fee=15.00
    )
    db.add(pricing)

    # Create system user (for admin access)
    system_user = User(
        company_id=marketplace_company.id,
        email="admin@primehaul.co.uk",
        password_hash=hash_password("primehaul2025"),
        full_name="System Admin",
        role="owner",
        is_active=True
    )
    db.add(system_user)

    db.commit()

    print(f"✅ Created marketplace company: {marketplace_company.id}")
    print(f"✅ Created pricing config")
    print(f"✅ Created admin user: admin@primehaul.co.uk / primehaul2025")

db.close()
```

```bash
# Run it:
python create_marketplace_company.py
```

**Checkpoint:** Marketplace company created ✅

---

#### ✅ Task 3.2: Update Landing Page Button (5 min)

**File:** `app/templates/marketplace_landing.html`

Find line ~100 (the "Start Free Survey" button):

```html
<!-- FIND THIS: -->
<a href="/marketplace/start" class="cta-button">

<!-- CHANGE TO: -->
<a href="/s/marketplace/start" class="cta-button">
```

Save file.

**Checkpoint:** Landing page button updated ✅

---

#### ✅ Task 3.3: Update /marketplace/start Endpoint (10 min)

**File:** `app/main.py`

Find line ~2341, replace the entire endpoint:

```python
# OLD VERSION (delete this):
@app.post("/marketplace/start")
async def marketplace_start(db: Session = Depends(get_db)):
    token = str(uuid.uuid4())[:8]
    marketplace_job = MarketplaceJob(token=token, status='in_progress')
    db.add(marketplace_job)
    db.commit()
    return RedirectResponse(url=f"/marketplace/{token}/move", status_code=302)

# NEW VERSION (paste this):
@app.post("/marketplace/start")
async def marketplace_start():
    """Redirect to marketplace company survey (reuses B2B flow)"""
    token = str(uuid.uuid4())[:8]
    return RedirectResponse(url=f"/s/marketplace/{token}/move", status_code=302)
```

Save file.

**Checkpoint:** Start endpoint updated ✅

---

#### ✅ Task 3.4: Add Submit to Marketplace Endpoint (45 min)

**File:** `app/main.py`

Add this NEW endpoint after the existing B2B submit endpoints (around line 2300):

**SEE QUICK_FIX_MARKETPLACE.md for full code** - it's too long to paste here.

Key points:
- Copy job data from Job → MarketplaceJob
- Copy rooms, items, photos to marketplace tables
- Broadcast to companies
- Send confirmation email to customer

**Checkpoint:** New endpoint added ✅

---

#### ✅ Task 3.5: Update Quote Preview Template (15 min)

**File:** `app/templates/quote_preview.html`

Find the submit form (around line 180):

```html
<!-- FIND THE SUBMIT FORM -->
<form method="post" action="/s/{{ company.slug }}/{{ token }}/submit">

<!-- REPLACE WITH CONDITIONAL: -->
{% if company.slug == 'marketplace' %}
    <form method="post" action="/s/marketplace/{{ token }}/submit-to-marketplace">
{% else %}
    <form method="post" action="/s/{{ company.slug }}/{{ token }}/submit">
{% endif %}

<!-- Form fields stay the same -->

<!-- Update button text: -->
{% if company.slug == 'marketplace' %}
    <button type="submit" class="submit-btn">Submit to Get Quotes →</button>
{% else %}
    <button type="submit" class="submit-btn">Request Quote</button>
{% endif %}

</form>
```

Save file.

**Checkpoint:** Template updated ✅

---

#### ✅ Task 3.6: Update Mapbox Token (10 min)

Your `.env` already has a Mapbox token, but verify it works:

```bash
# Check .env has:
MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoiZGptZWRzIiwiYSI6ImNtam5iNm55eTAwZXozZHF4MHFiYWtvc3MifQ.gg9r7PJHAMUQ_skmsYOAkQ
```

If you need a new one:
1. Go to: https://account.mapbox.com/access-tokens/
2. Create token (free tier: 50,000 loads/month)
3. Replace in .env

**Checkpoint:** Mapbox token verified ✅

---

### HOUR 5: Test Everything (60 minutes)

#### ✅ Task 5.1: Start Server (5 min)

```bash
cd /Users/primehaul/PrimeHaul/primehaul-os
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

**Checkpoint:** Server running without errors ✅

---

#### ✅ Task 5.2: Test Marketplace Flow (30 min)

**Complete customer journey:**

1. **Landing page:**
   - Go to: http://localhost:8000/marketplace
   - Should see hero section, features, CTA ✅

2. **Start survey:**
   - Click "Start Free Survey"
   - Should redirect to map selection ✅

3. **Pick locations:**
   - Enter pickup address (e.g., "London, UK")
   - Enter dropoff address (e.g., "Manchester, UK")
   - Click "Continue" ✅

4. **Property type:**
   - Select "2-Bedroom Flat"
   - Click "Continue" ✅

5. **Room selection:**
   - Select: Living Room, Kitchen, Bedroom 1, Bedroom 2
   - Click "Start Scanning" ✅

6. **Upload photos:**
   - For each room, upload 2-3 photos
   - Watch AI analyze (should work now with real OpenAI key) ✅
   - Click "Next Room" after each ✅

7. **Quote preview:**
   - Should see AI-generated inventory ✅
   - Should show estimated price range ✅
   - Click "Submit to Get Quotes" ✅

8. **Enter contact:**
   - Name, email, phone
   - Click "Submit" ✅

9. **Redirect to quotes page:**
   - Should redirect to `/marketplace/{token}/quotes` ✅
   - Should show "Waiting for quotes..." ✅

10. **Check emails:**
    - Customer should receive confirmation email ✅
    - Companies should receive "New job" email ✅

**If ANY step fails, debug before continuing!**

**Checkpoint:** Full customer flow works end-to-end ✅

---

#### ✅ Task 5.3: Test Company Bid Submission (15 min)

1. **Create test company:**
   ```bash
   # Go to: http://localhost:8000/auth/signup
   # Or create via Python:
   python -c "
   from app.database import get_db
   from app.models import Company, PricingConfig, User
   from app.auth import hash_password

   db = next(get_db())
   company = Company(
       company_name='Test Removals Ltd',
       slug='test-removals',
       email='test@test.com',
       subscription_status='active',
       is_active=True,
       primary_color='#2ee59d'
   )
   db.add(company)
   db.commit()

   pricing = PricingConfig(company_id=company.id)
   db.add(pricing)

   user = User(
       company_id=company.id,
       email='test@test.com',
       password_hash=hash_password('test123'),
       full_name='Test User',
       role='owner'
   )
   db.add(user)
   db.commit()
   print('✅ Test company created: test@test.com / test123')
   "
   ```

2. **Login as company:**
   - Go to: http://localhost:8000/test-removals/admin/login
   - Email: test@test.com
   - Password: test123

3. **View marketplace job:**
   - Go to: http://localhost:8000/test-removals/admin/marketplace
   - Should see the job you just created ✅
   - Click "View Details"

4. **Submit bid:**
   - Price: £850
   - Message: "We can do this next Thursday!"
   - Crew size: 2
   - Duration: 6 hours
   - Click "Submit Bid" ✅

5. **Check customer email:**
   - Should receive "New quote from Test Removals Ltd" ✅

**Checkpoint:** Bidding works ✅

---

#### ✅ Task 5.4: Test Bid Acceptance (10 min)

1. **As customer, go to quotes page:**
   - http://localhost:8000/marketplace/{token}/quotes
   - Should see bid from Test Removals Ltd ✅

2. **Accept bid:**
   - Click "Accept Quote" button ✅

3. **Check emails:**
   - Test Removals should get "Congratulations!" email ✅
   - Other companies (if any) should get "Job filled" email ✅

4. **Check database:**
   ```bash
   psql primehaul_local

   # Check commission created:
   SELECT id, job_price, commission_amount, status FROM commissions;

   # Should see:
   # £850 job, £127.50 commission, status = pending
   ```

**Checkpoint:** Full marketplace flow working ✅

---

### HOUR 6: Launch Decision (60 minutes)

You have 3 options:

#### Option A: Soft Launch (Local Testing)
**Time:** 10 minutes

1. Share local URL with friends/family: http://localhost:8000/marketplace
2. Get 3-5 test submissions
3. Fix any issues found
4. Deploy to production next week

**Best for:** Making sure everything works before real launch

---

#### Option B: Deploy to Railway (Production)
**Time:** 45 minutes

```bash
# 1. Create Railway account
# Go to: https://railway.app
# Sign up with GitHub

# 2. Install Railway CLI
npm install -g @railway/cli
# Or: curl -fsSL https://railway.app/install.sh | sh

# 3. Login
railway login

# 4. Initialize project
railway init
# Select: Empty Project

# 5. Add PostgreSQL
railway add
# Select: PostgreSQL

# 6. Deploy app
railway up

# 7. Add environment variables
railway variables set OPENAI_API_KEY=sk-proj-...
railway variables set SMTP_USERNAME=your-email@gmail.com
railway variables set SMTP_PASSWORD=your-app-password
# ... (all variables from .env)

# 8. Get domain
railway domain
# Generates: https://your-app-name.up.railway.app

# 9. Connect custom domain (optional)
# Go to Railway dashboard → Settings → Domains
# Add: app.primehaul.co.uk
# Update DNS: CNAME → railway domain
```

**Checkpoint:** Live on Railway ✅

---

#### Option C: Deploy to Heroku
**Time:** 45 minutes

```bash
# 1. Install Heroku CLI
brew tap heroku/brew && brew install heroku
# Or: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create primehaul-os

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 5. Set environment variables
heroku config:set OPENAI_API_KEY=sk-proj-...
heroku config:set SMTP_USERNAME=your-email@gmail.com
# ... (all variables)

# 6. Deploy
git push heroku main

# 7. Run migrations
heroku run alembic upgrade head

# 8. Open app
heroku open
```

**Checkpoint:** Live on Heroku ✅

---

## ✅ FINAL LAUNCH CHECKLIST

Before announcing to the world:

- [ ] Database configured and migrated
- [ ] OpenAI API key working (test with photo upload)
- [ ] Email system working (test with real email)
- [ ] Marketplace company created
- [ ] Full customer flow tested (end-to-end)
- [ ] Bid submission tested
- [ ] Bid acceptance tested
- [ ] Confirmation emails arriving
- [ ] Company notification emails arriving
- [ ] Winner/loser emails working
- [ ] Commission records created
- [ ] No errors in server logs
- [ ] Mobile responsiveness tested (use iPhone/Android)
- [ ] Payment ready (Stripe configured) - OPTIONAL for MVP
- [ ] Domain connected (primehaul.co.uk) - OPTIONAL for MVP

---

## 🎉 YOU'RE LIVE!

**Congratulations!** You now have a working marketplace platform.

### Next Steps (After Launch):

**Week 1:**
1. Get 5 real marketplace job submissions
2. Monitor emails are working
3. Fix any bugs that appear
4. Respond to customer questions

**Week 2:**
1. Add first 3 B2B companies
2. Implement power-ups from PRE_LAUNCH_AUDIT.md
3. Set up Google Analytics
4. Start Google Ads campaign (£300 budget)

**Month 1:**
1. Reach £1,000 revenue (B2B + marketplace)
2. Get first paying B2B customer
3. Collect first commission
4. Iterate based on feedback

---

## 🆘 TROUBLESHOOTING

**Server won't start:**
```bash
# Check for syntax errors:
python -m py_compile app/main.py

# Check port isn't in use:
lsof -i :8000
kill -9 <PID>
```

**Photos won't upload:**
```bash
# Check uploads directory exists:
ls -la app/static/uploads/

# Check permissions:
chmod -R 755 app/static/uploads/
```

**AI analysis fails:**
```bash
# Test OpenAI key:
python -c "
import openai
openai.api_key = 'sk-proj-YOUR-KEY'
print('Testing OpenAI...')
response = openai.models.list()
print('✅ OpenAI key works!')
"
```

**Emails not sending:**
```bash
# Run test_email.py again
python test_email.py

# Check Gmail security:
# https://myaccount.google.com/security

# Try SendGrid instead (easier):
# https://sendgrid.com/pricing/
```

---

## 📞 STUCK?

If you get stuck, check these files:
1. `PRE_LAUNCH_AUDIT.md` - Detailed issue analysis
2. `QUICK_FIX_MARKETPLACE.md` - Marketplace flow fix
3. `DEPLOYMENT_STEP_BY_STEP.md` - Full deployment guide

**YOU'VE GOT THIS! 🚀**

Your platform is 6 hours away from being live. Just follow this checklist step-by-step, test thoroughly, and launch!

**LET'S GO! 💪**
