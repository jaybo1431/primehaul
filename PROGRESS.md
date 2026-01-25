# PrimeHaul OS - Progress & Production Checklist

**Last Updated:** 25 January 2026
**Repository:** github.com/jaybo1431/primehaul
**Branch:** main (synced)

---

## What We've Built

### Core Platform (Complete)
- **Multi-tenant B2B SaaS** - Removal companies pay £49-£999/month, customers get FREE surveys
- **FastAPI Backend** - 87 API endpoints, 4,400+ lines in main.py
- **PostgreSQL Database** - 23 models, 8 migrations completed
- **Railway Deployment** - Auto-migrations on startup

### Customer Survey Flow (Complete)
- Multi-step survey: Location -> Property -> Access -> Date -> Rooms -> Photos -> Review -> Quote
- AI-powered inventory detection from photos (GPT-4 Vision)
- Instant quote generation with detailed pricing
- Terms & Conditions acceptance tracking
- Deposit payment via Stripe

### Admin Dashboard (Complete)
- **NEW: Survey Link Generator** - Generate unique links to send to customers
- **NEW: Onboarding Guide** - Step-by-step hints for first-time users
- Job queue with pending quotes
- 30-second quick approval button
- Price override capability
- Custom pricing config (15+ parameters)
- Custom branding (logo, colors)
- Multi-user accounts with roles (owner/admin/member)
- Analytics dashboard

### Billing (Complete)
- Stripe subscriptions with **14-day free trial** (updated from 30 days)
- Webhook handling for all events
- Customer portal for self-service

### AI & ML Infrastructure (Complete)
- OpenAI GPT-4o-mini integration for photo analysis
- 100% behavioral tracking for ML improvement
- Admin feedback loop for corrections
- Training data pipeline

### Company Isolation (Verified)
- Each company has unique URL: `/s/{company-slug}/{token}/...`
- Surveys only appear in the correct company's dashboard
- Complete data isolation via `company_id` foreign keys

---

## How It Works (For Bosses)

### Quick Start Guide
1. **Sign up** at primehaul.co.uk (14-day free trial, no card needed)
2. **Login** to your dashboard
3. **Click "+ New Survey Link"** to generate a unique customer link
4. **Send link** to customer (WhatsApp, text, email)
5. **Customer fills out survey** (3 minutes, photos of each room)
6. **AI generates quote** instantly using YOUR pricing
7. **You approve** with one tap from the dashboard
8. **Customer gets quote** and can book!

### Dashboard Features
- **Survey Link Generator**: Green button at top, generates shareable links
- **Quick Approve**: Approve quotes in 30 seconds
- **View Details**: Review photos, inventory, edit prices
- **Settings**: Pricing, Branding, Terms & Conditions

---

## Deploying to primehaul.co.uk

### Step 1: Push Changes to GitHub
```bash
git add .
git commit -m "Production ready: 14-day trial, survey link generator, onboarding"
git push origin main
```

### Step 2: Railway Custom Domain Setup
1. Go to [Railway Dashboard](https://railway.app)
2. Open your project
3. Click on your service
4. Go to **Settings** > **Networking** > **Custom Domain**
5. Add: `primehaul.co.uk`
6. Railway will give you a CNAME target (e.g., `xyz.up.railway.app`)

### Step 3: DNS Configuration (at your domain registrar)
Add these DNS records:

| Type | Name | Value |
|------|------|-------|
| CNAME | @ | `your-railway-url.up.railway.app` |
| CNAME | www | `your-railway-url.up.railway.app` |

*Note: Some registrars need an A record for root domain. Use Railway's IP if needed.*

### Step 4: Wait for SSL
Railway automatically provisions SSL (HTTPS). Takes 5-15 minutes.

### Step 5: Test
- Visit https://primehaul.co.uk - should show landing page
- Try signup flow
- Test survey link generation

---

## Tomorrow's Test with 2 Companies

### Pre-Test Checklist
- [ ] Railway deployment is live
- [ ] primehaul.co.uk is pointing to Railway
- [ ] SSL certificate is active (HTTPS working)
- [ ] Stripe is in test mode (or live if ready)
- [ ] OpenAI API key has credits
- [ ] Mapbox token is valid

### What Each Company Does
1. **Go to** primehaul.co.uk
2. **Click "Start Free Trial"**
3. **Fill in**: Company name, their name, email, password
4. **Get redirected** to their dashboard
5. **See onboarding guide** explaining the 5 steps
6. **Click "+ New Survey Link"**
7. **Copy the link** and send to a test customer (themselves or real customer)
8. **Customer fills survey** (photos, addresses, etc)
9. **Company sees quote** appear in dashboard
10. **Quick approve** the quote

### Verifying Isolation
- Company A's surveys ONLY appear in Company A's dashboard
- Company B's surveys ONLY appear in Company B's dashboard
- URL structure ensures this: `/s/company-a-slug/...` vs `/s/company-b-slug/...`

---

## Environment Variables Required

```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=64-character-secret
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
OPENAI_API_KEY=sk-...
MAPBOX_ACCESS_TOKEN=pk.eyJ...
```

---

## Session Notes

### 25 Jan 2026 - Production Prep
**Changes Made:**
- Changed trial period from 30 days to **14 days**
- Added **Survey Link Generator** to dashboard (green button)
- Added **Onboarding Guide** for first-time users (dismissable)
- Added **dismiss-onboarding** endpoint
- Verified **company isolation** is working correctly
- Updated landing page trial references

**Files Changed:**
- `app/main.py` - trial period, onboarding logic, dismiss endpoint
- `app/templates/admin_dashboard_v2.html` - survey link generator, onboarding banner
- `app/templates/landing_primehaul_uk.html` - 14-day trial
- `app/templates/auth_signup.html` - 14-day trial

**Ready for tomorrow's test!**

---

## Commands Cheatsheet

```bash
# Clone fresh
git clone https://github.com/jaybo1431/primehaul.git

# Run locally
uvicorn app.main:app --reload

# Reset database (dev only)
python QUICK_RESET.py

# Run migrations
alembic upgrade head

# Deploy (Railway auto-deploys on push)
git push origin main
```

---

## Key Files Reference

| Purpose | File |
|---------|------|
| Main app | `app/main.py` |
| Database models | `app/models.py` |
| AI vision | `app/ai_vision.py` |
| Stripe billing | `app/billing.py` |
| Dashboard template | `app/templates/admin_dashboard_v2.html` |
| Landing page | `app/templates/landing_primehaul_uk.html` |
| Signup page | `app/templates/auth_signup.html` |
| Deploy config | `railway.json` |
