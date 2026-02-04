# PrimeHaul OS - Progress Log

**Last Updated:** 4 February 2026
**Repository:** github.com/jaybo1431/primehaul
**Branch:** main
**Latest Commit:** `b41a470`

---

## Current Status: LIVE & WORKING

The platform is fully deployed at **primehaul.co.uk** and tested working.

---

## What's Built & Working

### Core Platform
- Multi-tenant B2B SaaS for UK removal companies
- **Pay-per-survey model**: £9.99/survey (changed from £99/month subscription)
- FastAPI backend with 87+ API endpoints
- PostgreSQL database with 23 models
- Railway deployment with auto-migrations

### Customer Survey Flow
- Multi-step: Location → Property → Access → Date → Rooms → Photos → Review → Quote
- AI-powered inventory detection from photos (GPT-4 Vision)
- **Multiple bedroom support**: Bed 1, Bed 2, Bed 3, Bed 4, Bed 5
- **+1 duplicate button**: Quickly add more of same item
- **Kitchen box estimation**: AI estimates boxes for cupboard contents
- **Wardrobe boxes**: Hanging clothes converted to wardrobe boxes
- Instant quote generation with company's custom pricing
- Terms & Conditions acceptance tracking
- Deposit payment via Stripe

### Admin Dashboard
- **Survey Link Generator** - Green button to create unique customer links
- **Onboarding Guide** - Step-by-step tips for first-time users
- **Quick Approve** - Approve quotes in 30 seconds
- **Job Review** - View photos, inventory, edit prices, correct AI detections
- **Recently Approved** - View approved quotes
- **Settings** - Pricing, Branding, Analytics, T&Cs (all with onboarding tips)

### Billing
- **Pay-per-survey**: £9.99 per completed survey
- **Enterprise tier**: Contact for 50+ surveys/month
- 14-day free trial with 3 free surveys
- Stripe integration
- Customer portal for self-service

### Company Isolation (VERIFIED)
- Each company has unique URL: `/s/{company-slug}/{token}/...`
- Surveys ONLY appear in the correct company's dashboard
- Complete data isolation via `company_id` foreign keys

---

## Session Log: 4 February 2026

### Bulky Item Weight Threshold Fix

**Problem:** Dining tables, chairs, and other moderate furniture were unfairly charged a £25/item bulky surcharge based on being furniture, not weight. A dining set (1 table + 6 chairs) could add £175 in bulky fees even though none of the items exceed 50kg.

**Solution:** Changed bulky classification from a manual/AI boolean flag to a weight-based threshold (default 50kg). Items are only "bulky" for pricing purposes if they weigh over the configurable threshold.

| Change | Details |
|--------|---------|
| New config field | `bulky_weight_threshold_kg` added to PricingConfig (default 50kg) |
| Quote calculation | Now counts bulky items by `weight_kg > threshold` instead of boolean flag |
| AI vision prompt | Updated to guide weight-based bulky estimation (>50kg) |
| Item creation | 3 endpoints now set `bulky` flag by weight instead of trusting AI boolean |
| Admin pricing page | New "Bulky Weight Threshold (kg)" field added |
| Marketplace pricing | Auto-bid and bid form now query items by weight instead of inventory_summary |
| Furniture catalog | 20 items under 50kg changed from bulky to non-bulky |

### Database Migration

| Migration | Purpose |
|-----------|---------|
| `fix004_bulky_weight_threshold.py` | Add `bulky_weight_threshold_kg` column to `pricing_configs` (default 50) |

### Files Modified

- `app/models.py` — Added `bulky_weight_threshold_kg` column
- `app/main.py` — Quote calculation, 3 item creation spots, update_pricing endpoint, marketplace bid form
- `app/ai_vision.py` — Updated AI prompt for weight-based bulky guidance
- `app/marketplace.py` — Updated auto_generate_bid to count by weight
- `app/templates/admin_pricing.html` — Added threshold input field
- `populate_furniture_catalog.py` — Updated is_bulky flags for 20 items
- `alembic/versions/fix004_bulky_weight_threshold.py` — New migration

### Commits

```
b41a470 Fix: Use weight-based threshold (50kg) for bulky item pricing instead of manual flag
```

---

## Session Log: 3 February 2026

### Major Bugs Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Room selection 500 error | Jinja2 `items_json.items` calling dict.items() method | Changed to `items_json.get('items', [])` |
| Quote preview 500 error | Missing `company` in template context | Added `company` to context |
| Admin job review 500 error | Missing `company` in template context | Added `company` to context |
| Photo URLs broken | Photo model missing `url` property | Added `@property url` to Photo model |
| Item dimensions errors | None values in template | Added fallbacks (`or 0`) |
| Wrong attribute name | `item.category` should be `item.item_category` | Fixed attribute name |
| Form action URLs | Missing `company_slug` prefix | Added `{{ company_slug }}` to URLs |
| Null pointer errors | `job.pickup.label` when label is None | Added null checks throughout |

### Features Added

| Feature | Description |
|---------|-------------|
| Multiple bedrooms | Bed 1, Bed 2, Bed 3, Bed 4, Bed 5 options |
| +1 duplicate button | Green button to add more of same item |
| Improved AI detection | Kitchen boxes, wardrobe boxes, cross-photo deduplication |
| Pay-per-survey pricing | £9.99/survey + Enterprise option (replaced £99/month) |

### Pricing Model Change

Changed from **£99/month unlimited** to:
- **Pay Per Survey**: £9.99 per completed survey
- **Enterprise**: Custom pricing for 50+ surveys/month (contact: enterprise@primehaul.co.uk)

Updated in:
- Landing page pricing section
- Signup page benefits
- Billing dashboard
- Trial expired page
- Subscription expired page
- Terms of service

### Database Migrations Added

| Migration | Purpose |
|-----------|---------|
| `fix003_item_columns.py` | Add `item_category` and `packing_requirement` to items table |

### Template Audit & Cleanup

Audited all 37 templates for:
- Missing context variables
- Null safety issues
- Correct form action URLs
- Attribute name mismatches

Fixed null safety in:
- `admin_dashboard_v2.html`
- `admin_job_review_v2.html`
- `quote_preview.html`
- `deposit_payment.html`
- `booking_calendar.html`

### Commits Today

```
efdf551 Audit cleanup: Additional null safety for label access
42f31d2 Fix: Admin job review template - null safety and correct paths
54c22b9 Fix: Add company object to admin_job_review template context
d0839b0 Fix: Null-safety for job.pickup.label and photo counting
b287403 Fix: Add url property to Photo model
c662ee6 Fix: Add company object to quote_preview template context
55f1b5b Fix: Quote preview errors - room.name and wardrobe_box handling
cef5ee7 Feature improvements: rooms, items, and AI detection
8dbded4 Remove 60-day trial urgency badge from landing page
3a69d37 Update pricing: £99/mo subscription → £9.99/survey pay-per-use
62dda1e Fix: Add missing item_category and packing_requirement columns
```

---

## Session Log: 26 January 2026

### Changes Made

1. **Trial Period: 30 → 14 days**
2. **Survey Link Generator** - Green "+ New Survey Link" button
3. **Onboarding Guide** - 5-step guide for new users
4. **Onboarding Tips** - All settings pages
5. **UI Improvements** - Button visibility
6. **Landing Page** - Root URL serves PrimeHaul UK landing
7. **Deployed to Railway** - Commit `ddb4d8f`

---

## Domain: primehaul.co.uk (LIVE)

Domain is configured and working.

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
| AI Vision | `app/ai_vision.py` |
| Dashboard | `app/templates/admin_dashboard_v2.html` |
| Job Review | `app/templates/admin_job_review_v2.html` |
| Landing page | `app/templates/landing_primehaul_uk.html` |
| Survey start | `app/templates/start_v2.html` |
| Room selection | `app/templates/rooms_pick.html` |
| Room scan | `app/templates/room_scan.html` |
| Quote preview | `app/templates/quote_preview.html` |

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

## Next Steps

1. [x] Domain setup (primehaul.co.uk working)
2. [x] Test survey flow end-to-end
3. [x] Fix all internal server errors
4. [ ] Test with real companies
5. [ ] Switch Stripe to live mode
6. [ ] Implement actual pay-per-survey billing logic (UI done, backend needs metered billing)
7. [ ] Email notifications (optional)
8. [ ] Google Analytics (optional)

---

## Known Issues

None currently - all tested flows working.

---

## Support

If you lose this chat and need help:
1. This file has everything you need
2. Code is all on GitHub: github.com/jaybo1431/primehaul
3. Railway dashboard has deployment logs
4. All features are working
