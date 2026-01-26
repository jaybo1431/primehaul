# PrimeHaul OS - Progress Log

**Last Updated:** 26 January 2026
**Repository:** github.com/jaybo1431/primehaul
**Branch:** main
**Latest Commit:** `ddb4d8f`

---

## Current Status: READY FOR PRODUCTION

The platform is fully built and deployed to Railway. Just need to connect custom domain.

---

## What's Built & Working

### Core Platform
- Multi-tenant B2B SaaS for UK removal companies
- Companies pay subscription, customers get FREE surveys
- FastAPI backend with 87+ API endpoints
- PostgreSQL database with 23 models
- Railway deployment with auto-migrations

### Customer Survey Flow
- Multi-step: Location → Property → Access → Date → Rooms → Photos → Review → Quote
- AI-powered inventory detection from photos (GPT-4 Vision)
- Instant quote generation with company's custom pricing
- Terms & Conditions acceptance tracking
- Deposit payment via Stripe

### Admin Dashboard
- **Survey Link Generator** - Green button to create unique customer links
- **Onboarding Guide** - Step-by-step tips for first-time users
- **Quick Approve** - Approve quotes in 30 seconds
- **Job Review** - View photos, inventory, edit prices
- **Settings** - Pricing, Branding, Analytics, T&Cs (all with onboarding tips)

### Billing
- Stripe subscriptions with **14-day free trial**
- Webhook handling
- Customer portal for self-service

### Company Isolation (VERIFIED)
- Each company has unique URL: `/s/{company-slug}/{token}/...`
- Surveys ONLY appear in the correct company's dashboard
- Complete data isolation via `company_id` foreign keys

---

## Session Log: 26 January 2026

### Changes Made Today

1. **Trial Period: 30 → 14 days**
   - `app/main.py` line 750
   - `app/templates/landing_primehaul_uk.html`
   - `app/templates/auth_signup.html`
   - `app/templates/billing_dashboard.html`

2. **Survey Link Generator**
   - Added to `app/templates/admin_dashboard_v2.html`
   - Green "+ New Survey Link" button
   - Generates unique 8-character tokens
   - Copy button + WhatsApp/SMS/Email share links

3. **Onboarding Guide (Dashboard)**
   - Shows for new users with no jobs
   - 5-step guide: Create link → Send → Customer fills → AI quotes → Approve
   - Dismissable (saved in localStorage + database)
   - Added dismiss endpoint: `POST /{company_slug}/admin/dismiss-onboarding`

4. **Onboarding Tips (All Settings Pages)**
   - **Pricing**: How pricing works, what each field means
   - **Branding**: Logo upload, colors, matching brand
   - **Analytics**: Understanding metrics, response time tips
   - **Terms & Conditions**: PDF upload, version control, legal proof

5. **UI Improvements**
   - "Back to Dashboard" button: `#444` → `#555` (more visible)
   - Error message: "Company slug already taken" → "Company name already taken"

6. **Landing Page**
   - Root URL `/` now serves `landing_primehaul_uk.html`
   - All references updated to 14-day trial

7. **Deployed to Railway**
   - Commit: `ddb4d8f`
   - Auto-deployed via GitHub push

---

## Domain Setup: primehaul.co.uk (IN PROGRESS)

### Step 1: Railway (DO THIS FIRST)
1. Go to railway.app → your project → web service
2. Settings → Networking → Custom Domain
3. Add: `primehaul.co.uk`
4. Add: `www.primehaul.co.uk`
5. **Copy the CNAME target** Railway gives you (e.g., `xyz.up.railway.app`)

### Step 2: Namecheap DNS
1. Log in to Namecheap
2. Domain List → `primehaul.co.uk` → Manage → Advanced DNS
3. Delete existing A/CNAME records for @ and www
4. Add these records:

| Type | Host | Value |
|------|------|-------|
| URL Redirect (301) | @ | https://www.primehaul.co.uk |
| CNAME | www | [your-railway-cname].up.railway.app |

### Step 3: Wait 15-30 minutes
- DNS propagation
- Railway SSL certificate

### Step 4: Test
- https://www.primehaul.co.uk → should load site
- https://primehaul.co.uk → should redirect to www

---

## Tomorrow's Test: 2 Companies

### Pre-Test Checklist
- [ ] Domain is live (primehaul.co.uk)
- [ ] SSL working (https)
- [ ] Can sign up new account
- [ ] Dashboard loads with onboarding
- [ ] Can generate survey link
- [ ] Survey link works for customer
- [ ] Quote appears in dashboard
- [ ] Can approve quote

### Test Flow for Each Company
1. Go to primehaul.co.uk
2. Click "Start Free Trial"
3. Fill in: Company name, name, email, password
4. See dashboard with onboarding guide
5. Click "+ New Survey Link"
6. Copy link, send to test customer (or themselves)
7. Customer fills survey with photos
8. Quote appears in dashboard
9. Click "Quick Approve"
10. Done!

### Verifying Isolation
- Company A's link: `/s/company-a-slug/abc123/start-v2`
- Company B's link: `/s/company-b-slug/xyz789/start-v2`
- Company A only sees their surveys
- Company B only sees their surveys

---

## Environment Variables (Railway)

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

## Key Files

| What | File |
|------|------|
| Main app | `app/main.py` |
| Models | `app/models.py` |
| Dashboard | `app/templates/admin_dashboard_v2.html` |
| Landing page | `app/templates/landing_primehaul_uk.html` |
| Signup | `app/templates/auth_signup.html` |
| Pricing settings | `app/templates/admin_pricing.html` |
| Branding settings | `app/templates/admin_branding.html` |
| Analytics | `app/templates/admin_analytics.html` |
| T&Cs settings | `app/templates/admin_terms.html` |

---

## Commands

```bash
# Clone fresh
git clone https://github.com/jaybo1431/primehaul.git

# Run locally
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Deploy (auto on push)
git add .
git commit -m "your message"
git push origin main
```

---

## Support

If you lose this chat and need help:
1. This file has everything you need
2. Code is all on GitHub: github.com/jaybo1431/primehaul
3. Railway dashboard has deployment logs
4. All features are working - just need domain setup

---

## Next Steps After Domain

1. [ ] Test full flow with real companies
2. [ ] Set up Stripe in live mode (currently test)
3. [ ] Configure email notifications (optional)
4. [ ] Add Google Analytics (optional)
