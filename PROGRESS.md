# PrimeHaul OS - Progress Log

**Last Updated:** 7 February 2026
**Repository:** github.com/jaybo1431/primehaul
**Branch:** main
**Slogan:** *An intelligent move.*

---

## Current Status: READY TO SELL

The platform is fully deployed at **primehaul.co.uk** — now locked down and ready for customer acquisition.

**Passwords (Jaybo Only):**
- Superadmin: `/superadmin` → `Jaybo2026`
- Sales Dashboard: `/sales` → `Jaybo2026`

---

## What's Built & Working

### Core Platform
- Multi-tenant B2B SaaS for UK removal companies
- **Prepaid credits model**: 3 free credits, then buy packs (£6.99-£9.90/survey)
- FastAPI backend with 87+ API endpoints
- PostgreSQL database with 23 models
- Railway deployment with auto-migrations
- **Slogan:** "An intelligent move."

### Customer Survey Flow
- Multi-step: Location → Property → Access → Date → Rooms → Photos → Review → Quote
- AI-powered inventory detection from photos (GPT-4 Vision)
- **Multiple bedroom support**: Bed 1, Bed 2, Bed 3, Bed 4, Bed 5
- **+1 duplicate button**: Quickly add more of same item
- **Furniture variant toggle**: Customers can adjust sizes (e.g. 3-seater sofa → 2-seater)
- **Kitchen box estimation**: AI estimates boxes for cupboard contents
- **Wardrobe boxes**: Hanging clothes converted to wardrobe boxes
- **Packing service upsell**: Collapsible "Need help packing?" section
- Instant quote generation with company's custom pricing
- Terms & Conditions acceptance tracking
- Deposit payment via Stripe

### Admin Dashboard
- **Survey Link Generator** - Green button to create unique customer links
- **Email Invite** - Send survey links directly to customers via email
- **Onboarding Guide** - Step-by-step tips for first-time users
- **Quick Approve** - Approve quotes in 30 seconds
- **Job Review** - View photos, inventory, edit prices, correct AI detections
- **Recently Approved** - View approved quotes
- **Company Details** - Edit company name, email, phone number
- **Settings** - Pricing, Branding, Analytics, T&Cs (all with onboarding tips)

### Billing
- **Prepaid credits system**: Buy credit packs upfront
  - Starter: 10 credits for £99 (£9.90/survey)
  - Growth: 25 credits for £225 (£9.00/survey)
  - Pro: 50 credits for £399 (£7.98/survey)
  - Enterprise: 100 credits for £699 (£6.99/survey)
- **3 free credits** on signup
- **Partner accounts**: Unlimited free surveys for infrastructure partners
- Stripe Checkout integration
- Low credits warning banner when < 3 credits remaining

### Superadmin Dashboard (`/superadmin`)
- Password-protected control center for platform owner
- All companies, surveys, revenue at a glance
- ML training data stats (photos, items, corrections)
- **Recent ML Feedback** - View actual correction details (AI detected → corrected)
- **Self-Learning ML** - System learns from corrections and auto-applies patterns
- Database stats and recent activity feed
- Server status indicator
- Make any company a partner

### Company Isolation (VERIFIED)
- Each company has unique URL: `/s/{company-slug}/{token}/...`
- Surveys ONLY appear in the correct company's dashboard
- Complete data isolation via `company_id` foreign keys

---

## Session Log: 7 February 2026 (Evening)

### Solo Founder Mode Activated

**Decision:** This is Jaybo's project. No partners signed yet. Building for passive income.

### Security Lockdown

- Changed superadmin password to `Jaybo2026`
- Changed sales dashboard password to `Jaybo2026`
- Invalidated all existing sessions with new session key
- Locked CORS to primehaul.co.uk domains only
- Enabled TrustedHostMiddleware

### Brand Identity

**Slogan:** "An intelligent move."

Added to:
- Landing page header (next to logo)
- Landing page footer
- Meta title & description (SEO)
- Signup page
- Login page
- Cold email signature

### Cold Email Templates (Perfected)

**Email 1 - "Quick one for {company_name}"**
- Opens with timestamp story: "9pm... 9:05pm... 9:07pm booked"
- Shows outcome before explanation
- Confident close: "See what you think"

**Email 2 - "Re: Quick one..."**
- Addresses control objection: "You stay in control. Always."
- Clipboard metaphor for approval flow

**Email 3 - "Last one (then I'll leave you alone)"**
- Honest subject line
- Customer experience testimonial
- Warm exit: "All the best with the moves"

### Lead Scraper Built

**File:** `scripts/scrape_leads.py`

Scrapes from:
- Checkatrade
- Yell
- Thomson Local
- Curated manual list

**17 leads with emails ready:**
- 7 in London
- 4 in Manchester
- 1 in Birmingham, Nottingham, Leeds, Edinburgh, Southampton, Brighton, Cambridge

### To-Do Before Sending

1. [ ] Set up Google Workspace for `jay@primehaul.co.uk`
2. [ ] Add MX, SPF, DKIM, DMARC records in Namecheap
3. [ ] Create App Password
4. [ ] Configure SMTP in Railway
5. [ ] Send first batch of emails
6. [ ] Register with ICO (£40)

### Commits This Session

```
584d132 Add slogan "An intelligent move." everywhere
e160eed Lock down all admin access - Jaybo only
043fdcc Security: Lock down CORS and enable trusted hosts
3f903c4 Perfect the cold email sequence - story-driven, confident
1045249 Polish email templates - confident, not desperate
d36a6b8 Rewrite cold email templates to hit harder
4e1970b Ignore scraped leads folder
dddccfd Add private sales automation dashboard with auto email sequences
e8c4e7e Add email survey invite feature for boss dashboard
```

---

## Session Log: 6 February 2026

### Prepaid Credits System

**Problem:** Pay-per-survey billing (£9.99 charged after each survey) created friction and unpredictable costs for removal companies.

**Solution:** Replaced with prepaid credit packs that companies buy upfront:

| Pack | Credits | Price | Per Survey |
|------|---------|-------|------------|
| Starter | 10 | £99 | £9.90 |
| Growth | 25 | £225 | £9.00 |
| Pro | 50 | £399 | £7.98 |
| Enterprise | 100 | £699 | £6.99 |

- 3 free credits on signup (replaces 14-day trial)
- Credits deducted when survey is submitted
- Low credits warning banner when < 3 remaining
- Buy credits page with Stripe Checkout integration

### Final Quote Price

**Problem:** Boss could only approve a price range (£500-£650), but customers expected a single fixed quote.

**Solution:** When boss clicks "Approve", a modal appears asking for the final fixed price. AI suggests the midpoint as default. The final price replaces the estimate range on the customer's quote.

- New `final_quote_price` column on Job model
- Modal with AI-suggested default
- Quote preview shows single price when approved

### Activity Tracking System

**Purpose:** Monitor boss behavior during beta testing to collect product insights and lay foundation for self-evolving AI system.

**What's Tracked:**
- Page views with time spent
- Button clicks and interactions (link generated, copied, shared)
- Feature usage patterns
- Friction points (rage clicks, long pauses, errors)
- Session flows (user journeys)

**New Module:** `app/activity_tracker.py`
- `track_activity()` — Core tracking function
- `track_boss_action()` — Boss-specific events
- `track_customer_action()` — Customer survey events
- `track_friction()` — UX friction points
- `get_live_boss_activity()` — Real-time feed for superadmin
- `get_funnel_analytics()` — Survey drop-off rates
- `get_friction_hotspots()` — Pages with most friction
- `analyze_patterns_and_suggest()` — AI-powered UX suggestions

**New Superadmin Activity Dashboard:** `/superadmin/activity`
- **Live Feed** tab — Real-time boss activity (auto-refreshes every 30s)
- **AI Insights** tab — Detected issues with severity levels
- **Funnel** tab — Survey conversion rates with drop-off visualization
- **Engagement** tab — Company engagement rankings

### Glowing Packing CTA (Improved)

**Change:** The packing service upsell was in a collapsed `<details>` dropdown. Now it's an always-visible card with:
- Breathing green glow animation (`glowPulse`)
- Prominent header with 📦 icon
- "From +£X" pricing
- Larger checkboxes (20x20px) for easier mobile tapping
- "Professional packing service — all materials included" footer

### Variant Toggle — Ordering Fix

**Bug:** Item indices mismatched between room scan view and update-variant endpoint because they used different ordering.

**Fix:** Both now use `order_by(Item.id)` for consistent indexing.

### Private Sales Automation Dashboard

**Feature:** Fully automated lead outreach system at `/sales` (password protected).

**What It Does:**
1. **Auto-scrape leads** — Import from CSV or use built-in scraper
2. **Send cold emails** — 3-email sequence (initial + 2 follow-ups)
3. **Read replies** — Checks inbox via IMAP
4. **Analyze sentiment** — Detects positive/negative/question
5. **Auto-reply** — Sends appropriate response based on sentiment
6. **Track pipeline** — New → Contacted → Replied → Interested → Signed Up

**Email Sequence:**
- Day 0: Initial email ("Quick question about your quoting process")
- Day 3: Follow-up 1 ("Just bumping this...")
- Day 7: Follow-up 2 ("Last one from me")

**Files:**
- `app/outreach.py` — Core automation logic, email templates, IMAP/SMTP
- `app/templates/sales_dashboard.html` — Private dashboard UI
- `app/main.py` — Routes at `/sales/*`
- `scripts/run_sales_automation.py` — Cron job script
- `scripts/scrape_leads.py` — Lead scraper for Checkatrade/Yell

**Environment Variables:**
- `SALES_PASSWORD` — Dashboard password (default: primesales2026)
- `SALES_AUTOMATION` — Set to "true" to enable auto-sending
- `SMTP_USER` / `SMTP_PASSWORD` — For sending emails
- `IMAP_HOST` / `IMAP_PORT` — For reading replies (default: Gmail)

**Access:** `https://app.primehaul.co.uk/sales`

### Email Survey Invitations

**Feature:** Bosses can now send survey links directly to customers via email from the dashboard.

**How It Works:**
1. Boss generates a survey link on the dashboard
2. Enters customer name (optional) and email
3. Clicks "Send Invite"
4. Customer receives a beautifully formatted HTML email with:
   - "Get Your Free Removal Quote" header
   - Big green CTA button to start survey
   - "How It Works" 3-step guide
   - "Why Choose Us?" benefits section
   - Company branding

**Files:**
- `app/notifications.py` — Added `send_survey_invitation()` function
- `app/main.py` — Added `/admin/send-survey-invite` POST endpoint
- `app/templates/admin_dashboard_v2.html` — Added email input UI + `sendEmailInvite()` JS

**Analytics:** Invite sends tracked as `survey_invite_sent` events for analytics.

### Files Created

- `app/activity_tracker.py` — Comprehensive activity tracking module
- `app/templates/superadmin_activity.html` — Live activity dashboard
- `app/templates/admin_buy_credits.html` — Credit purchase page
- `alembic/versions/fix008_credits_system.py` — Credits column migration
- `alembic/versions/fix009_final_quote_price.py` — Final quote price migration

### Files Modified

- `app/main.py` — Credits endpoints, final quote approval, activity tracking
- `app/billing.py` — Credit pack definitions, Stripe Checkout integration
- `app/models.py` — Added `credits` and `final_quote_price` columns
- `app/templates/admin_dashboard_v2.html` — Credits display, tracking JS
- `app/templates/admin_job_review_v2.html` — Final price modal
- `app/templates/quote_preview.html` — Glowing packing CTA
- `app/templates/superadmin_dashboard.html` — Activity link

### Commits

```
8b7815b Fix: Consistent item ordering in room scan for variant toggle
bdec679 UI: Replace hidden packing dropdown with glowing CTA card
5aad0c8 Add activity tracking system for real-time boss behavior monitoring
0c69784 Add final quote price - boss sets fixed price when approving
0c92655 Implement prepaid credits system replacing pay-per-survey billing
```

---

## Session Log: 5 February 2026

### Self-Learning ML System

**Purpose:** The system now learns from user corrections and automatically improves future AI detections. The more it's used, the smarter it gets.

**How It Works:**
1. Users correct AI detections (e.g., "Large Couch" → "3-seater sofa")
2. Corrections stored in `ItemFeedback` table
3. System analyzes patterns — when 70%+ of corrections match, pattern is learned
4. **AI Prompt Evolution** — Learned patterns injected into GPT-4 prompt, improving base detections
5. **Post-Processing** — Results double-checked against learned patterns
6. **Dimension Learning** — System averages corrected dimensions and applies them
7. Learning cycle runs after each survey submission + can be triggered manually

**Two-Layer Intelligence:**
- Layer 1: AI prompt enhanced with learned naming conventions and dimensions
- Layer 2: Output corrections applied based on confidence thresholds

**New Database Table:**
- `learned_corrections` — stores learned patterns with confidence scores

**New Module:**
- `app/ml_learning.py` — pattern detection, confidence calculation, auto-apply logic

**Integration Points:**
- Photo upload (3 locations) — applies learned corrections to AI results
- Survey submission — triggers learning cycle
- Superadmin dashboard — shows feedback details and link to learning page

**Superadmin Learning Page (`/superadmin/learning`):**
- View all learned patterns with confidence bars
- See which patterns are auto-applied vs still learning
- Manual "Run Learning Cycle" button
- Explanation of how the system learns

**Files Created:**
- `app/ml_learning.py` — Self-learning module
- `app/templates/superadmin_learning.html` — Learning dashboard
- `alembic/versions/fix007_learned_corrections.py` — Migration

**Files Modified:**
- `app/models.py` — Added `LearnedCorrection` model
- `app/main.py` — Integrated learning into AI detection + survey submission
- `app/templates/superadmin_dashboard.html` — Added feedback display + learning link

---

### Distance Pricing — Now Calculated from Coordinates

**Problem:** Distance was hardcoded to £120 regardless of actual distance. The `base_distance_km` and `price_per_km` fields existed in the database but were never used.

**Solution:**
- Distance now calculated using Haversine formula from pickup/dropoff lat/lng coordinates
- Admin pricing page has new "Distance Pricing" section with configurable base distance (km) and price per km
- Quote breakdown shows actual miles calculated
- Job review shows distance in the route section

### Approval Flow Fixed

**Problem:** Auto-approval triggered during quote preview (when customer was still browsing), causing jobs to show as "Approved" in the dashboard before the customer even submitted. No manual approval step.

**Solution:**
- Removed auto-approval logic from `calculate_quote()` — all quotes now require manual admin approval
- Fixed `submit-quote` endpoint to properly set status to `awaiting_approval` and track `submitted_at`
- Updated `quote_preview.html` to show correct states:
  - `in_progress` → "Submit for review" button
  - `awaiting_approval` → "Awaiting approval" message with orange styling
  - `approved` → "Accept This Quote" button with green styling

### Property Type Auto-Submit

**Problem:** After selecting property type (House, Flat, etc.), customer had to tap a separate "Continue to Rooms" button — unnecessary friction.

**Solution:** Property type tiles now auto-submit on tap. Select House → immediately goes to rooms selection. Cleaner, faster flow.

### Files Modified

- `app/main.py` — Distance calculation, removed auto-approval, fixed submit-quote endpoint, added distance pricing to admin
- `app/templates/admin_pricing.html` — Added Distance Pricing section
- `app/templates/admin_job_review_v2.html` — Shows distance in miles
- `app/templates/quote_preview.html` — Updated status display logic
- `app/templates/property_type.html` — Auto-submit on tile tap

### Quote Price Styling

Made the quote price bigger and clearer on the customer quote preview page — solid white text at 40px with subtle green glow instead of faded gradient.

### Stripe Connect + Pay-Per-Survey Billing

**Problem:** Needed a way for:
1. Customer deposits to go directly to removal companies (not through PrimeHaul)
2. PrimeHaul to charge £9.99 per completed survey after 3 free trial surveys

**Solution — Stripe Connect for Deposits:**
- Removal companies connect their Stripe account via Dashboard → Payments
- Customer deposits transfer directly to company's bank account
- PrimeHaul never handles deposit money — clean and compliant
- New admin page at `/{slug}/admin/payments` for Connect onboarding

**Solution — Pay-Per-Survey Billing:**
- Every company gets 3 free surveys during trial
- When customer clicks "Submit for review", survey is counted
- After 3 free surveys, £9.99 charged to company's payment method
- Usage tracking displayed in Payments settings page

### Database Migration

| Migration | Purpose |
|-----------|---------|
| `fix005_stripe_connect_and_usage.py` | Add `stripe_connect_account_id`, `surveys_used`, `free_surveys_remaining` to companies |

### Files Created/Modified

- `app/templates/admin_payments.html` — **New**: Payment settings with Connect onboarding + usage stats
- `app/billing.py` — Added Stripe Connect functions + survey charging logic
- `app/main.py` — New endpoints for Connect onboarding, deposit payments, survey charging
- `app/models.py` — Added Connect + usage tracking fields to Company model
- `app/templates/admin_dashboard_v2.html` — Added Payments nav link
- `app/static/app.css` — Quote price styling fix

### Customer Contact Flow Restored

**Problem:** The customer contact details page (name, email, phone) was missing from the survey flow. The `/submit-quote` endpoint was changing status directly without collecting contact info first.

**Solution:**
- Split submission into two steps: contact collection → actual submission
- `/submit-quote` now redirects to `/contact` if customer details are missing
- New `/do-submit` endpoint handles the actual submission (status change, survey fee, analytics)
- `/submit-contact` saves details then redirects to `/do-submit`
- Better customer name tracking in logs and analytics events

### UX Cleanup — Strip Bloat from Survey and Dashboard

**Goal:** Make the app super easy for both customers and removal company admins. Remove verbose text, redundant UI, and distracting elements while keeping all the power under the hood.

**Customer Survey Changes:**
| Before | After |
|--------|-------|
| Long subtitles with explanations | Short, action-focused text |
| Dead voice input code (40+ lines) | Removed |
| Packing service always visible with glow animation | Collapsed `<details>` section |
| Verbose T&Cs section | Compact single-line link |
| Hints and pro tips on every page | Removed — UI is self-explanatory |

**Admin Dashboard Changes:**
| Before | After |
|--------|-------|
| 5-step onboarding banner (55 lines) | 3-line compact welcome |
| "Today's Summary" stats section | Removed (redundant) |
| Keyboard shortcuts hint | Removed |
| Full pricing breakdown in job review | Collapsible `<details>` section |
| T&Cs with IP, version, timestamp | Compact badge: "✓ T&Cs accepted" |

**Files Modified:**
- `start_v2.html` — Simplified text, removed dead voice code
- `room_scan.html` — Cleaner instructions
- `rooms_pick.html` — Removed duplicate code, shorter text
- `quote_preview.html` — Collapsed packing service
- `customer_contact.html` — Removed redundant hints
- `admin_dashboard_v2.html` — Major declutter (-300 lines)
- `admin_job_review_v2.html` — Collapsible breakdown, compact badges

**Result:** 326 lines of template bloat removed. Cleaner, faster UX.

### Color Scheme Update

**Problem:** Orange colors for "pending" and "awaiting approval" states looked too aggressive and pushy.

**Solution:** Replaced all orange (`#ffa500`) with soft blue (`#60a5fa`) across 11 templates and CSS. Calmer, more professional look.

### Partner Accounts

**Purpose:** Ricky (business partner with real-world infrastructure - trucks, manpower) needs unlimited free surveys for his own removal business.

**Implementation:**
- Added `is_partner` and `partner_name` fields to Company model
- Partners skip all billing — unlimited surveys forever
- Can mark any company as partner via superadmin dashboard

### Superadmin Dashboard

**URL:** `/superadmin` (password protected via `SUPERADMIN_PASSWORD` env var)

**Features:**
- All companies with status, surveys used, partner badges
- Key metrics: companies, surveys, items detected, ML corrections, revenue
- ML training data stats (photos, items, corrections, variant changes)
- Database stats (jobs, rooms, photos, items, feedback, analytics)
- Recent activity feed with timestamps
- Server status indicator
- Make any company a partner

**Files Created:**
- `app/templates/superadmin_dashboard.html`
- `app/templates/superadmin_login.html`
- `alembic/versions/fix006_partner_accounts.py`

### Legal Pages — Terms of Service & Privacy Policy

**Purpose:** Platform needs proper legal documentation for UK GDPR compliance and user accountability.

**Created:**
- `app/templates/legal_terms.html` — Terms of Service covering:
  - Service description, account registration, billing model
  - Pay-per-survey (£9.99) and partner accounts explained
  - Acceptable use, customer data responsibilities
  - AI-generated quote disclaimers
  - Intellectual property, limitation of liability
  - Termination terms, governing law (England and Wales)

- `app/templates/legal_privacy.html` — Privacy Policy covering:
  - Data collected from companies and customers (as data processor)
  - Third parties: Stripe, OpenAI, Mapbox, Railway
  - Data retention periods
  - UK GDPR rights (access, rectification, erasure, portability)
  - Security measures, cookies, international transfers
  - Contact: privacy@primehaul.co.uk

**Signup Flow:**
- Added T&Cs acceptance checkbox to `auth_signup.html`
- Users must agree to Terms of Service and Privacy Policy before creating account
- Links open in new tab for easy review
- JavaScript validation ensures checkbox is ticked

**Routes:**
- `/terms` — Serves Terms of Service page
- `/privacy` — Serves Privacy Policy page

### Files Created/Modified

- `app/templates/legal_terms.html` — **New**: Terms of Service
- `app/templates/legal_privacy.html` — **New**: Privacy Policy
- `app/templates/auth_signup.html` — Added T&Cs checkbox with validation
- `app/main.py` — Updated /terms and /privacy routes

### Commits

```
f9d80aa Feature: Partner accounts + Superadmin dashboard
57f03fc Style: Replace orange with soft blue for pending states
613296f UX cleanup: Strip bloat from survey and dashboard
79b42b2 Fix: Restore customer contact details step in survey flow
771f43f Feature: Stripe Connect for deposits + pay-per-survey billing
4d1e8eb Style: Make quote price bigger and clearer
88df266 Fix: Distance pricing, approval flow, and property type UX
```

---

## Session Log: 4 February 2026 (Evening)

### Glowing Packing Service CTA

**Problem:** The "Need help packing?" upsell was hidden in a collapsed `<details>` dropdown — customers almost certainly never saw it.

**Solution:** Replaced with an always-visible card with a green glowing pulse animation (`@keyframes glowPulse`). Room checkboxes have green accents when selected. Clear "This is optional" note at the bottom.

### Admin Company Details Settings

**Problem:** Company name, email, and phone were set at signup and could never be changed.

**Solution:** New admin settings page at `/{slug}/admin/company-details` with:
- Editable company name, email, phone fields
- Email format validation and uniqueness check
- Phone format validation
- Slug shown as read-only (used in customer URLs)
- Navigation link added to admin dashboard

### Furniture Size/Variant Toggle

**Problem:** AI detects "3-seater sofa" but the customer has a 2-seater. They could only delete or +1, never correct the size. Lost ML training signal.

**Solution:** Compact dropdown appears below furniture items in room scan, covering 15 categories:
- Sofas (2/3/4-seater, corner, sofa bed, leather)
- Wardrobes (single/double/triple)
- Beds (single/double/king/super king)
- Dining tables (2/4/6/8-seater)
- Mattresses, desks, chests of drawers, bookcases, TVs, fridges, washing machines, armchairs, dining chairs, sideboards, TV stands

Each variant has pre-set dimensions (length, width, height, weight, CBM). Corrections saved as `ItemFeedback` records for ML training. Original AI detection preserved in item notes.

### Bug Fix: Room Scan JS Scoping

**Problem:** `showToast`, `renderItems`, `escapeHtml` were defined inside an IIFE but called from `incrementItem`/`deleteItem` outside it — the +1 and delete buttons were silently broken.

**Fix:** Moved shared functions to top-level script scope. Added `renderItems(currentItems)` call on page load so server-rendered items get interactive buttons.

### Files Modified

- `app/variants.py` — **New**: 15 furniture categories with variant dimensions
- `app/templates/admin_company_details.html` — **New**: Company details settings page
- `app/main.py` — 3 new endpoints (company details GET/POST, variant update POST), modified room_scan_get
- `app/templates/quote_preview.html` — Replaced hidden packing dropdown with glowing CTA card
- `app/static/app.css` — Added `glowPulse` keyframe animation
- `app/templates/room_scan.html` — Variant dropdown, JS scope fix, client-side variant lookup
- `app/templates/admin_dashboard_v2.html` — Added "Company Details" nav link

### HTTPS Security Fix

**Problem:** Multiple hardcoded `http://192.168.0.139:8000` URLs in SMS booking links sent to customers. Auth cookies set to `secure=False`. Stripe redirect URLs defaulted to `http://localhost`. No proxy header trust for Railway's SSL termination.

**Fixes:**

| Fix | Details |
|-----|---------|
| Booking SMS links | Replaced 2x hardcoded local IP with `RAILWAY_PUBLIC_DOMAIN` env var |
| Stripe redirects | Changed `APP_URL` default from `http://localhost` to `https://primehaul.co.uk` |
| Auth cookies | `secure=False` → `secure=True` (2 spots: login + signup) |
| Proxy headers | Added `ProxyHeadersMiddleware` to trust Railway's `X-Forwarded-Proto` |

**Note:** Ensure `RAILWAY_PUBLIC_DOMAIN` is set to `primehaul.co.uk` in Railway env vars.

### Landing Page — Cost Comparison Section

Added a "Do The Maths" section between the stats and pricing sections on the landing page. Side-by-side red vs green cards showing:
- **Without primehaul**: 3 site visits × £75 = £225 to win one job
- **With primehaul**: £9.99 per survey, AI instant quote, approve in 30 secs

Bold headline: **"That's a 95% cost reduction on quoting"**. Responsive — stacks on mobile.

### Commits

```
09ad402 Add cost comparison section to landing page — 95% quoting cost reduction
e089b02 Fix: HTTPS security — remove hardcoded local IPs, secure cookies, trust proxy headers
8102e2e Feature: Glowing packing CTA, company details settings, furniture variant toggle
1b4e8cf Update progress log with Feb 3-4 session notes
1b1d345 Remove voice input buttons from survey start page
```

---

## Session Log: 4 February 2026 (Morning)

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
| Furniture Variants | `app/variants.py` |
| Dashboard | `app/templates/admin_dashboard_v2.html` |
| Job Review | `app/templates/admin_job_review_v2.html` |
| Company Details | `app/templates/admin_company_details.html` |
| Landing page | `app/templates/landing_primehaul_uk.html` |
| Survey start | `app/templates/start_v2.html` |
| Room selection | `app/templates/rooms_pick.html` |
| Room scan | `app/templates/room_scan.html` |
| Quote preview | `app/templates/quote_preview.html` |
| Terms of Service | `app/templates/legal_terms.html` |
| Privacy Policy | `app/templates/legal_privacy.html` |

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
4. [x] Prepaid credits billing system (replaces pay-per-survey)
5. [x] Final quote price feature
6. [x] Activity tracking for product insights
7. [ ] Test with real companies
8. [ ] Switch Stripe to live mode
9. [ ] Email notifications (optional)
10. [ ] Google Analytics (optional)

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
