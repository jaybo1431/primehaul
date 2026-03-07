# PrimeHaul OS - Progress Log

**Last Updated:** 3 March 2026
**Repository:** github.com/jaybo1431/primehaul
**Branch:** main
**Slogan:** *An intelligent move.*

---

## Current Status: HARDENED & LAUNCH-READY

The platform is fully deployed at **primehaul.co.uk** — security-hardened, performance-optimized, and tested.

**Passwords:** Now loaded from environment variables (Railway). No more hardcoded defaults.

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

## Session Log: 3 March 2026

### Simplified Quote Flow — 10 Steps → 3

**Problem:** The post-approval customer journey was 10 web form steps: booking calendar → contact details → quote submission → quote preview → quote acceptance → T&Cs → move date → deposit → booking confirmed. Way too much friction.

**New Flow (3 steps):**
1. Boss approves quote → customer gets email showing **estimate range** (£X – £Y)
2. Customer clicks **"I'm Happy With This Quote"** → simple thank-you page
3. Boss gets **email + in-app notification** with customer contact info → continues via direct communication

**Changes:**

| File | What Changed |
|------|-------------|
| `app/notifications.py` | `send_quote_approved_email()` now takes `estimate_low`/`estimate_high` instead of `final_price`. Shows price range, CTA changed to "I'm Happy With This Quote". Added new `send_customer_accepted_notification()` that emails boss with customer contact details when they accept. |
| `app/main.py` | Both `/admin/job/{token}/approve` and `/quick-approve` routes now pass estimate range + accept-quote URL. New `GET /s/{slug}/{token}/accept-quote` route — idempotent, sets status to `customer_accepted`, sends boss notification, tracks activity + analytics. Old `/booking` URL 301-redirects to `/accept-quote`. |
| `app/templates/quote_accepted.html` | New clean thank-you page — green checkmark, estimate range card, 3-step "what happens next", company contact buttons. |
| `app/sms.py` | `notify_quote_approved()` updated — shows estimate range, CTA changed to "Happy with the price? Click to let us know:" |

**Old booking flow templates kept as dead code** (booking_calendar, quote_preview, etc.) — unreachable from new flow, can clean up later.

### Commits

```
6066625 Simplify quote flow: end at estimate, let boss handle booking
```

---

## Session Log: 24 February 2026 (Continued)

### Video Shortened Again — 59s → 30s, Full Polish

**Goal:** Cut video from 59s to ~30s for social media. Hook in first 2 seconds. Make it punchy.

**New Structure — 5 Scenes (was 7):**

| # | Scene | Duration | Voiceover |
|---|-------|----------|-----------|
| 1 | **Hook** | 3.0s | "PrimeHaul. Your AI surveyor." |
| 2 | **Problem → Flip** | 5.5s | "Customers ghost you. Site visits waste hours. There's a better way." |
| 3 | **The Magic** | 8.0s | "Your customer snaps photos. AI detects every item instantly." |
| 4 | **Boss Approve** | 6.0s | "You approve from your phone. Done in thirty seconds." |
| 5 | **Results + CTA** | 8.0s | "Ten times faster. Thirty percent more jobs. Try it free at primehaul.co.uk." |

**Total: 30.5 seconds (915 frames @ 30fps)**

**What Changed:**
- **Scene 1:** Logo slam with shockwave ring + impact flash. "Your AI Surveyor" subtitle. No slow fade.
- **Scene 2:** 3 pain cards appear near-simultaneously (3-frame stagger), red ambient glow, green wipe sweeps across, "There's a better way." lands.
- **Scene 3:** Merged old Scenes 3+4. Phone shows room-by-room photos with camera flash effects → crossfades to AI scan line sweeping down → items detected with volume labels. Side stats panel.
- **Scene 4:** Stripped-down dashboard. Notification banner with shake → price card → breathing approve button → green success flash → "QUOTE SENT". Cut inventory tags, Stripe deposit, price editing.
- **Scene 5:** Merged old Scenes 6+7. Fast stat counters (10x, 30%, 0) with impact shake → logo with spinning ring → "Try It Free" button with breathing glow → "Try it free at primehaul.co.uk" typewriter. Cut "Built by djam.ai".
- **Transitions:** 5 frames (~0.17s) — basically hard cuts between scenes.
- All voiceovers regenerated via ElevenLabs (George voice, turbo v2.5).

**Files Changed:**
- `video/generate-audio.js` — 5 new short scripts
- `video/public/s1-s5.mp3` — Regenerated audio
- `video/public/s6.mp3`, `video/public/s7.mp3` — Deleted
- `video/src/helpers/timing.ts` — 5 scenes, 915 frames, TRANS=5
- `video/src/scenes/Scene1Intro.tsx` — Rewritten (impact hook)
- `video/src/scenes/Scene2Problem.tsx` — Rewritten (fast cards + flip)
- `video/src/scenes/Scene3CustomerFlow.tsx` — Rewritten (merged with AI magic)
- `video/src/scenes/Scene4BossApprove.tsx` — New file (stripped dashboard)
- `video/src/scenes/Scene5ResultsCTA.tsx` — New file (merged results + CTA)
- `video/src/scenes/Scene4AImagic.tsx` — Deleted (merged into Scene3)
- `video/src/scenes/Scene5BossDashboard.tsx` — Deleted (replaced by Scene4BossApprove)
- `video/src/scenes/Scene6Results.tsx` — Deleted (merged into Scene5)
- `video/src/scenes/Scene7CTA.tsx` — Deleted (merged into Scene5)
- `video/src/PrimeHaulDemo.tsx` — Updated to 5 scenes

**Renders (all 3 formats on Desktop):**
- `primehaul-demo.mp4` — 1920x1080, 3.7 MB
- `primehaul-tiktok.mp4` — 1080x1920, 3.8 MB
- `primehaul-square.mp4` — 1080x1080, 3.5 MB

### Commits

```
c215eef Shorten video from 59s to 30s with polished 5-scene structure
```

---

## Session Log: 24 February 2026

### Full Security Audit & Sharpening — 4 Phases Implemented

**Phase 1: Security Hardening**
- Removed all hardcoded password defaults (`SUPERADMIN_PASSWORD`, `SALES_PASSWORD`) — app now crashes on startup if not set via env vars
- `DEV_DASHBOARD_PASSWORD` keeps default for local dev but logs a warning
- Created centralized `app/config.py` with `Settings` class — replaced 30+ scattered `os.getenv()` calls
- Session keys now randomized per deploy (`secrets.token_hex(32)`) — all sessions invalidated on restart
- All password comparisons now use `secrets.compare_digest()` (timing-attack safe)
- Blocked SVG uploads for logos (XSS vector) — now only allows PNG, JPG, WebP
- Fixed extension parsing to use `os.path.splitext()` with allowlist
- Fixed 4 bare `except:` clauses with specific exception types
- Added 3 security headers: `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy`
- Added rate limiting via `slowapi`: `/auth/login` (5/min), `/superadmin/login` (3/min), `/sales/login` (3/min)

**Phase 2: Performance**
- Wrapped email and SMS sending in `BackgroundTasks` on both approval endpoints — response returns instantly
- Wrapped AI vision calls in `asyncio.to_thread()` — frees event loop during 3-8s OpenAI calls
- Fixed N+1 queries in superadmin dashboard — batch-fetches companies instead of individual queries (3 lookups replaced ~55)
- Added database indexes: `idx_jobs_created_at`, `idx_jobs_status_submitted`, `idx_item_feedback_created`
- Added `Cache-Control: public, max-age=604800, immutable` for `/static/*` paths
- Added photo compression on upload: Pillow resizes to max 2048px, JPEG quality 80, auto-rotates from EXIF

**Phase 3: UX Polish**
- Created custom 404 and 500 error pages matching PrimeHaul dark theme
- 500 handler has plain HTML fallback if template rendering fails
- Added canonical URL, Twitter Card tags, og:image to landing page
- Added JSON-LD `SoftwareApplication` structured data for Google rich results

**Phase 4: Test Infrastructure**
- Added `pytest`, `httpx`, `pytest-asyncio` to requirements
- Created `tests/conftest.py` with SQLite in-memory database, UUID/JSONB type adapters
- Created 19 tests across 3 files: `test_auth.py`, `test_survey_flow.py`, `test_quote_approval.py`
- All 19 tests passing

**Files Changed:**
- `app/config.py` — New centralized settings
- `app/main.py` — Security fixes, performance optimizations, error handlers
- `requirements.txt` — Added `slowapi`, `pytest`, `httpx`, `pytest-asyncio`
- `alembic/versions/fix015_performance_indexes.py` — New performance indexes
- `app/templates/error_404.html` — New custom 404 page
- `app/templates/error_500.html` — New custom 500 page
- `app/templates/landing_primehaul_uk.html` — SEO meta tags, OG tags, JSON-LD
- `tests/` — New test infrastructure and test files
- `pytest.ini` — Test configuration

**Action Required:**
- Set strong `SUPERADMIN_PASSWORD` and `SALES_PASSWORD` in Railway env vars (app will crash without them)
- Run `alembic upgrade head` to apply performance indexes
- Create `app/static/og-image.png` (1200x630px) for social sharing previews

---

## Session Log: 23 February 2026 (Continued)

### Video Ads Shortened — 100s → 59s

**Problem:** Feedback that the promo videos were too long at ~100 seconds.

**Solution:** Rewrote all 7 voiceover scripts to be more concise, regenerated audio via ElevenLabs, and compressed animation timing across all scenes.

**Script Changes:**
- S2 (Problem): Cut to two sharp sentences about wasted site visits and losing customers
- S3 (Customer Flow): Tightened to "send a link, drop a pin, snap photos, done"
- S4 (AI Magic): Focused on scan → identify → calculate, no filler
- S5 (Boss Dashboard): Streamlined to set price → approve → deposit paid
- S6 (Results): Kept punchy stats — 10x faster, 30% more jobs, zero site visits
- S7 (CTA): Unchanged — already tight

**Animation Timing Compressed:**
- Scene 2: Pain point delays (30,180,320) → (20,100,175)
- Scene 3: Screen transitions (120,280,440) → (70,160,250)
- Scene 4: Scan/accuracy/totals/quote delays all compressed ~60%
- Scene 5: Notification/card/price/approve/deposit delays all compressed ~60%

**New Durations:**
| Scene | Old | New |
|-------|-----|-----|
| S1 Intro | 4.7s | 4.7s |
| S2 Problem | 12.3s | 8.3s |
| S3 Customer Flow | 18.3s | 9.8s |
| S4 AI Magic | 23.7s | 11.7s |
| S5 Boss Dashboard | 25.3s | 12.7s |
| S6 Results | 8.7s | 6.9s |
| S7 CTA | 6.3s | 4.5s |
| **Total** | **~100s** | **~59s** |

**Renders (all 3 formats):**
- `video/out/primehaul-demo.mp4` — 1920x1080, 6.1 MB
- `video/out/primehaul-tiktok.mp4` — 1080x1920, 6.2 MB
- `video/out/primehaul-square.mp4` — 1080x1080, 5.9 MB

**Files Modified:**
- `video/generate-audio.js` — Shorter scripts for all 7 scenes
- `video/public/s1-s7.mp3` — Regenerated audio files
- `video/src/helpers/timing.ts` — Updated durations (1760 frames ≈ 58.7s)
- `video/src/scenes/Scene2Problem.tsx` — Compressed pain point delays
- `video/src/scenes/Scene3CustomerFlow.tsx` — Compressed screen transitions
- `video/src/scenes/Scene4AImagic.tsx` — Compressed all animation delays
- `video/src/scenes/Scene5BossDashboard.tsx` — Compressed all animation delays

### ICO Registration & Contact Emails

- Updated `legal_privacy.html` — ICO registration from `[To be registered]` to `00013181949`
- Updated `landing_primehaul_uk.html` — ICO in FAQ, contact emails in footer (info@, sales@, support@), ICO in footer
- Updated `app/notifications.py` — Added ICO and info@ to all email footers

### Google Workspace Email Migration

Migrated MX records from Namecheap Private Email to Google Workspace:
- Added 5 Google MX records in Namecheap DNS
- Verified propagation via Google DNS
- Still pending: App Password generation from hello@primehaul.co.uk + Railway SMTP env vars

### Commits

```
10d01f7 Add ICO registration number and contact emails to footer and legal pages
86c4eb1 Update PROGRESS.md with 23 Feb session — email notifications and SMTP settings
1a7912d Shorten video ads from 100s to 59s with tighter scripts and animations
```

---

## Session Log: 23 February 2026

### Quote Approval Email Notification

**Feature:** When the boss approves a quote (standard or quick-approve), the customer now receives a professional HTML email with their approved price and a link to book.

**Email Contents:**
- "Your Quote is Ready" header with company branding
- Prominent approved price in green (£X,XXX.XX)
- Move summary (collection → delivery addresses)
- "View Quote & Book" CTA button
- Company name and phone in footer
- Plain text fallback included

**Integration Points:**
- Standard approval endpoint (`/{slug}/admin/job/{token}/approve`)
- Quick approval endpoint (`/{slug}/admin/job/{token}/quick-approve`)
- Only sends if customer has an email address
- Wrapped in try/except — email failure never blocks approval

### Per-Company Email Sending (Two-Tier System)

**Problem:** All emails were sent from PrimeHaul's SMTP account. Bosses wanted emails to come from their own company email address.

**Solution — Two tiers:**

**Tier 1 (Default, no setup):** Emails sent as *"Smith Removals via PrimeHaul"* from `noreply@primehaul.co.uk` with Reply-To set to the company's email. Customer replies go directly to the company.

**Tier 2 (Company SMTP):** Boss configures their own SMTP credentials in Company Details settings. Emails then send directly from their own email address (e.g. `info@smithremovals.co.uk`).

**Settings UI (Company Details page):**
- SMTP Server + Port fields (grid layout)
- Email/Username field
- Password field (with Gmail App Password link)
- Optional From Email override
- "Send Test Email" button (sends to company's contact email)
- Status badges: green check when configured, yellow warning when not
- Collapsible "Common email provider settings" cheat sheet (Gmail, Outlook, Yahoo, Zoho)

**Technical Changes:**
- `send_email()` accepts optional `smtp_config` dict — uses company SMTP when provided, falls back to PrimeHaul default
- `send_quote_approved_email()` routes through company SMTP or falls back to "via PrimeHaul" branding
- Both approval endpoints build SMTP config from company model fields

### Database Migration

| Migration | Purpose |
|-----------|---------|
| `fix014_company_smtp_settings.py` | Add `smtp_host`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_from_email` to companies |

### Files Created

- `alembic/versions/fix014_company_smtp_settings.py` — SMTP columns migration

### Files Modified

- `app/models.py` — 5 new SMTP columns on Company model
- `app/notifications.py` — New `send_quote_approved_email()` function, `send_email()` updated with `from_name`, `reply_to`, `smtp_config` params
- `app/main.py` — Email send in both approval endpoints, 2 new SMTP endpoints (save + test), updated company details GET with SMTP query params
- `app/templates/admin_company_details.html` — New "Email Settings" section with full SMTP config UI

### Commits

```
d4f2fb0 Add quote approval email and per-company SMTP settings
```

---

## Session Log: 22 February 2026

### PrimeHaul Promotional Video Ad

Built a full animated video ad using **Remotion** (React-based video framework) with AI voiceover via **ElevenLabs**.

**Video Structure — 7 Scenes (~100 seconds):**
1. **Intro** — Logo + "Stop Quoting Blind. Start Quoting Smart."
2. **The Problem** — Wasted site visits, slow quotes, lost jobs
3. **Customer Flow** — Phone mockup: link → pin drop → photos → done
4. **AI Magic** — AI scanning photos, detecting items with CBM/weight
5. **Boss Dashboard** — Survey notification, job card, price setting, deposit
6. **Results** — Animated stats (10x faster, 30% more jobs, 0 site visits)
7. **CTA** — Free trial, primehaul.co.uk, "Built by djam.ai"

**Voice:** George (British male) on ElevenLabs Turbo v2.5 model — energetic, natural UK accent with low stability/high style for expressiveness.

**Three Formats Rendered:**
- `video/out/primehaul-demo.mp4` — 1920x1080 (YouTube/website) — 8.8 MB
- `video/out/primehaul-tiktok.mp4` — 1080x1920 (TikTok/Reels) — 8.8 MB
- `video/out/primehaul-square.mp4` — 1080x1080 (Instagram/Facebook) — 8.5 MB

**Tech Stack:**
- Remotion 4.0.242 for animation/rendering
- ElevenLabs API for TTS voiceover (George voice, turbo_v2_5 model)
- 7 React scene components with spring animations, typewriter effects, phone mockups
- `generate-audio.js` script for bulk audio generation

**Key Files:**
| What | File |
|------|------|
| Main composition | `video/src/PrimeHaulDemo.tsx` |
| Scene components | `video/src/scenes/Scene1-7*.tsx` |
| Timing config | `video/src/helpers/timing.ts` |
| Audio generator | `video/generate-audio.js` |
| Color palette | `video/src/helpers/colors.ts` |
| Animations | `video/src/helpers/animations.ts` |

---

## Session Log: 13 February 2026

### Go-Live Preparation with Rick

Working with business partner Rick to prepare for public launch. Major UX polish, accessibility features, and infrastructure setup.

### Delivery Property Type Added

**Problem:** Survey only asked about collection property type, not delivery location.

**Solution:**
- Added `dropoff_property_type` column to jobs table
- New `/dropoff-property` step in survey flow after pickup property type
- Options: House, Bungalow, Flat, Office, Storage
- Added "Bungalow" option to collection property types too
- Quote preview and admin job review now show both property types

### Photo Display Bug Fixed

**Problem:** Room scan photos stuck on "Analysing" and showed blank boxes instead of actual photos.

**Root Cause:** Photo URLs pointed to `/static/uploads/...` but files were stored in `uploads/` and served via `/photo/...` endpoint.

**Solution:**
- Fixed photo URLs to use correct `/photo/{company_id}/{token}/{filename}` endpoint
- Added instant photo preview using FileReader API (shows photo immediately while AI processes)
- Added processing overlay with spinner on photos during AI analysis
- Two-phase progress: "Uploading" → "AI Analyzing"
- Better success messages showing item count

### Access Details Validation UX

**Problem:** Customers couldn't proceed from parking/details page but didn't know what was missing.

**Solution:**
- Added clear validation error banner listing exactly which fields are missing
- Red highlighting on incomplete fields (lift radio buttons, parking dropdown)
- Auto-scroll to first error
- Real-time error clearing when user fills in field
- Shake animation on error banner to draw attention

### Quote Acceptance Price Fix

**Problem:** Quote acceptance page showed estimate range (£350-£450) instead of final price after admin approved.

**Solution:** Now shows single final price (£400) with "Final price confirmed" label when `job.final_quote_price` is set.

### Mobile Header Overflow Fixed

**Problem:** On mobile, "An intelligent move." tagline pushed "Get 3 Free Credits" button off screen.

**Solution:** Hide tagline on mobile (<768px), reduce header padding/font sizes.

### Landing Page Copy Updates

Updated to reflect credit-based pricing model:
- "What if I don't like it?" FAQ → explains credits model, no subscription
- "14-Day Trial" → "Get 3 Free Credits"
- "Cancel anytime" → "No subscription • Credits never expire"
- Added ICO registration to data security FAQ

### Light/Dark Mode Toggle

**Feature:** Full theme switching for both customer survey and admin dashboard.

**Implementation:**
- CSS custom properties for both themes (dark default, light mode via `.light-mode` class)
- 🌙/☀️ toggle button in nav header
- Defaults to system preference (`prefers-color-scheme`)
- Persists to localStorage (separate keys for survey vs admin)
- Smooth color transitions
- Updates mobile browser chrome color

**Light Mode Colors:**
- Background: #f5f5f7 (clean light gray)
- Cards: #ffffff (white)
- Text: #1d1d1f (dark gray)
- Green accent adjusted for contrast

### Voice Guidance (Accessibility)

**Feature:** Optional voice guide that reads instructions aloud on each survey page - "granny proof" for less tech-savvy users.

**Implementation:**
- Friendly opt-in card on first visit: "Need a helping hand?"
- "Voice ON" green pill toggle in header (easy to spot and control)
- Uses **OpenAI TTS** with "nova" voice (natural, human-like)
- Server-side caching (`tts_cache/`) for fast repeat plays
- Remembers preference in localStorage
- Every survey page has custom voice prompt

**ALL Survey Pages with Voice Guidance:**
| Page | Message Summary |
|------|-----------------|
| Start | "Welcome! Enter your addresses and choose property types..." |
| Property Type | "What type of property are we collecting from?..." |
| Dropoff Property | "What type of property are we delivering to?..." |
| Access Details | "Tell us about floors, lifts, and parking..." |
| Move Date | "When would you like to move?..." |
| Move Map | "Let's set your moving locations..." |
| Room Selection | "Tap on each room that has items..." |
| Room Scan | "Tap Take Photos and point your camera..." |
| Photos Bulk | "Time to photograph your home..." |
| Review Inventory | "Quick check before your quote..." |
| Quote Preview | Different messages for pending/awaiting/approved status |
| Quote Acceptance | "Tick the checkbox and tap Accept Quote..." |

### Email Setup Guide

Created comprehensive email templates and outreach documentation for Rick:
- 4-email sequence with timing (Day 1 → Day 3 → Day 8 → Day 15)
- Initial contact + 3 follow-up templates
- Reply templates for common responses
- Subject line A/B testing ideas
- Where to find leads (Checkatrade, Yell, LinkedIn, etc.)
- Tracking spreadsheet structure
- GDPR compliance notes

### Infrastructure

- Google Workspace domain verified
- Email aliases configured (sales@, privacy@ → Rick, support@, hello@ → Jaybo)
- ICO registration complete

### Alembic Migration Chain Fixed

**Problem:** Deployment failed due to conflicting migration revisions.

**Fix:**
- Renamed `fix010_dropoff_property_type.py` to `fix011_dropoff_property_type.py`
- Updated `down_revision` from `fix009` to `fix010_outreach`
- Fixed `fix010_outreach` to reference `fix009` (not `fix009_final_quote_price`)

### Files Created

- `app/templates/dropoff_property_type.html` — Delivery property type selection
- `/Users/primehaul/Desktop/PRIMEHAUL_EMAIL_TEMPLATES.md` — Outreach templates for Rick
- `/Users/primehaul/Desktop/RICK_GO_LIVE_TASKS.md` — Rick's go-live checklist
- `GO_LIVE_CHECKLIST.md` — Comprehensive launch checklist

### Files Modified

- `app/main.py` — Photo URL fixes, dropoff property endpoints, validation
- `app/models.py` — Added `dropoff_property_type` column
- `app/static/app.css` — Light mode theme, theme toggle button styles
- `app/templates/base.html` — Theme toggle, voice guide toggle, JS for both
- `app/templates/admin_dashboard_v2.html` — Theme toggle for admin
- `app/templates/start_v2.html` — Dropoff property type section, voice guidance
- `app/templates/property_type.html` — Added Bungalow option, voice guidance
- `app/templates/dropoff_property_type.html` — New template with voice guidance
- `app/templates/access_questions.html` — Validation UX, voice guidance
- `app/templates/rooms_pick.html` — Voice guidance
- `app/templates/room_scan.html` — Photo preview, processing overlay, voice guidance
- `app/templates/quote_preview.html` — Voice guidance (status-aware)
- `app/templates/quote_acceptance.html` — Final price display, voice guidance
- `app/templates/landing_primehaul_uk.html` — Mobile header fix, copy updates, ICO

### Voice Guide Overhaul

**Problem:** Voice guidance existed but wasn't being triggered, and the small speaker icon in the header was too subtle for users to notice. Users wanted something "super intuitive" for less tech-savvy customers.

**Solution:**

1. **Friendly Opt-In Card at Start**
   - New pulsing green card appears on first visit: "Need a helping hand?"
   - Two clear buttons: "Yes, guide me" / "No thanks"
   - Only shows once (remembered via localStorage)
   - When enabled, speaks a welcoming intro and starts guiding

2. **Improved Header Toggle**
   - Redesigned from small icon to visible pill button
   - Shows "Voice" when off, "ON" (green) when active
   - Green border/background when voice is enabled
   - Tapping immediately speaks current page guidance

3. **All Survey Pages Now Have Guidance**
   - Added voice to 4 missing templates:
     - `move_date.html`: "When would you like to move?..."
     - `move_map.html`: "Let's set your moving locations..."
     - `photos_bulk.html`: "Time to photograph your home..."
     - `review_inventory.html`: "Quick check before your quote..."

4. **Voice Quality Upgrade (OpenAI TTS)**
   - Changed from robotic browser TTS to OpenAI's "nova" voice
   - Natural, friendly, human-like speech
   - Server-side caching (`tts_cache/`) for performance
   - Works via `/api/speak` POST endpoint

**Files Modified:**
- `app/templates/start_v2.html` — Voice opt-in card + CSS
- `app/templates/base.html` — New voice toggle UI + JS
- `app/static/app.css` — Voice toggle pill styles
- `app/templates/move_date.html` — Added voice guidance
- `app/templates/move_map.html` — Added voice guidance
- `app/templates/photos_bulk.html` — Added voice guidance
- `app/templates/review_inventory.html` — Added voice guidance

### Commits

```
6a76171 Improve voice guide: add friendly opt-in card and complete all survey pages
d71019a Upgrade voice guide to OpenAI TTS for natural human-like voice
3e651e0 Update PROGRESS.md with 13 Feb session - go-live prep with Rick
235d6a4 Fix: Correct fix010_outreach down_revision
0fa717e Fix: Alembic migration chain - rename fix010 to fix011
12424d2 Fix: Photo display bug and enhance room scan UX
09be84f UX: Add clear validation feedback on access details page
7b3ab62 Fix: Show final quote price on acceptance page
e3d44b3 Fix: Mobile header overflow - hide tagline on small screens
22e6e3d Fix: Update landing page copy to reflect credit-based pricing
55d4fa2 Update FAQ: Add ICO registration to data security answer
a6e8e9f Feature: Add light/dark mode toggle to survey app and admin dashboard
e39f077 Feature: Add voice guidance for survey app (accessibility)
```

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
9. [x] Email notifications (quote approval + per-company SMTP)
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
