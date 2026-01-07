# 🧹 Stack Cleanup Audit

## Current Status
**Total markdown files**: 20
**Total templates**: 39
**Utility scripts**: 6

---

## 📋 Recommended Actions

### ✅ KEEP (Essential - Production)

#### Documentation
- [x] `README.md` - Main project documentation
- [x] `QUICK_START_STAGING.md` - Essential deployment guide (NEW)
- [x] `STAGING_DEPLOYMENT_GUIDE.md` - Detailed staging setup (NEW)
- [x] `PRIMEHAUL_UK_DEPLOYMENT.md` - Production deployment
- [x] `WEBSITE_READY.md` - Website overview (NEW)
- [x] `UX_IMPROVEMENTS_SUMMARY.md` - UX changes documentation

#### Templates (Core Customer Flow)
- [x] `base.html` - Base template
- [x] `landing_primehaul_uk.html` - **PRIMARY** landing page
- [x] `start_v2.html` - **PRIMARY** streamlined start flow
- [x] `photos_bulk.html` - Bulk photo upload
- [x] `booking_calendar.html` - Calendar booking
- [x] `access_questions.html` - Access parameters
- [x] `property_type.html` - Property selection
- [x] `rooms_pick.html` - Room selection
- [x] `room_scan.html` - Room photo capture
- [x] `review_inventory.html` - Inventory review
- [x] `quote_preview.html` - Quote display
- [x] `customer_contact.html` - Contact form
- [x] `move_map.html` - Map display
- [x] `move_date.html` - Date selection
- [x] `booking_confirmed.html` - Booking confirmation
- [x] `inventory.html` - Inventory display

#### Templates (Admin)
- [x] `admin_login.html` - Admin login
- [x] `admin_dashboard_v2.html` - **PRIMARY** admin dashboard
- [x] `admin_job_review_v2.html` - **PRIMARY** job review
- [x] `admin_analytics.html` - Analytics
- [x] `admin_pricing.html` - Pricing config
- [x] `admin_branding.html` - Branding config

#### Templates (Auth & Billing)
- [x] `auth_login.html` - User login
- [x] `auth_signup.html` - User signup
- [x] `billing_dashboard.html` - Billing
- [x] `subscription_expired.html` - Subscription alerts
- [x] `trial_expired.html` - Trial expiry
- [x] `deposit_payment.html` - Payment page

#### Templates (Legal)
- [x] `terms.html` - Terms of Service (NEW)
- [x] `privacy.html` - Privacy Policy (NEW)
- [x] `contact.html` - Contact page (NEW)

#### Templates (Tools)
- [x] `cbm_calculator.html` - Free CBM tool
- [x] `dev_dashboard.html` - Developer dashboard

#### Utility Scripts (Keep)
- [x] `create_test_company.py` - Useful for testing
- [x] `reset_test_data.py` - Useful for testing
- [x] `check_user.py` - Useful for admin tasks
- [x] `create_pricing_config.py` - Useful for setup

---

### 📦 ARCHIVE (Move to /docs/archive)

These are old planning/strategy docs - useful for reference but not needed for daily operations:

#### Strategy & Planning Docs
- [ ] `INVESTOR_PITCH.md` - Investor materials
- [ ] `LAUNCH_TODAY.md` - Old launch planning
- [ ] `REALISTIC_LAUNCH_STRATEGY.md` - Launch strategy notes
- [ ] `PRE_LAUNCH_AUDIT.md` - Old audit
- [ ] `TEST_TODAY_QUICK.md` - Test notes
- [ ] `SIMULATION_RESULTS.md` - Simulation results

#### Partner/Marketplace (Not using yet)
- [ ] `MARKETPLACE_GUIDE.md`
- [ ] `PARTNER_LAUNCH_PLAN.md`
- [ ] `PARTNER_PARTNERSHIP_PROPOSAL.md`
- [ ] `PARTNER_ROLE_FINAL.md`
- [ ] `PARTNER_START_HERE.md`
- [ ] `PARTNER_TEMPLATES.md`

#### Redundant Deployment Docs
- [ ] `DEPLOYMENT_STEP_BY_STEP.md` - Superseded by STAGING_DEPLOYMENT_GUIDE
- [ ] `QUICK_FIX_MARKETPLACE.md` - One-time fix notes

---

### 🗑️ DELETE (Redundant/Obsolete)

#### Obsolete Templates
- [ ] `landing_page.html` - **REPLACED** by `landing_primehaul_uk.html`
- [ ] `start.html` - **REPLACED** by `start_v2.html` (old multi-page flow)
- [ ] `test_map.html` - Test file only, can remove in production

#### Already Deleted (Git shows)
- [x] `EXTREME_FEATURES.md` - Deleted ✅
- [x] `HOW_TO_SAVE_EVERYTHING.md` - Deleted ✅
- [x] `app/templates/admin_dashboard.html` - Deleted ✅
- [x] `app/templates/admin_job_review.html` - Deleted ✅

#### One-Time Migration Scripts
- [ ] `add_move_date_column.py` - One-time migration (alembic handles this now)
- [ ] `create_tables.py` - Replaced by alembic migrations

#### Marketplace Templates (Not using yet, can remove)
- [ ] `marketplace_dashboard.html` - Not in use
- [ ] `marketplace_job_detail.html` - Not in use
- [ ] `marketplace_landing.html` - Not in use
- [ ] `marketplace_quotes.html` - Not in use

---

## 📊 Space Savings

**Markdown files**: 20 → 6 (keep) = **14 files to archive**
**Templates**: 39 → 33 (keep) = **6 files to remove**
**Utility scripts**: 6 → 4 (keep) = **2 files to remove**

**Total cleanup**: 22 files to archive/remove

---

## 🎯 Cleanup Plan

### Step 1: Create Archive Folder
```bash
mkdir -p docs/archive/planning
mkdir -p docs/archive/marketplace
mkdir -p docs/archive/old-migrations
```

### Step 2: Archive Planning Docs
```bash
mv INVESTOR_PITCH.md docs/archive/planning/
mv LAUNCH_TODAY.md docs/archive/planning/
mv REALISTIC_LAUNCH_STRATEGY.md docs/archive/planning/
mv PRE_LAUNCH_AUDIT.md docs/archive/planning/
mv TEST_TODAY_QUICK.md docs/archive/planning/
mv SIMULATION_RESULTS.md docs/archive/planning/
mv DEPLOYMENT_STEP_BY_STEP.md docs/archive/planning/
mv QUICK_FIX_MARKETPLACE.md docs/archive/planning/
```

### Step 3: Archive Marketplace Docs
```bash
mv MARKETPLACE_GUIDE.md docs/archive/marketplace/
mv PARTNER_*.md docs/archive/marketplace/
```

### Step 4: Remove Obsolete Templates
```bash
rm app/templates/landing_page.html
rm app/templates/start.html
rm app/templates/test_map.html
rm app/templates/marketplace_*.html
```

### Step 5: Archive Old Scripts
```bash
mv add_move_date_column.py docs/archive/old-migrations/
mv create_tables.py docs/archive/old-migrations/
```

### Step 6: Update References in Code
```bash
# Remove route for old start.html in main.py
# Remove route for test_map.html in main.py
```

---

## ✅ After Cleanup

### Root Directory (Clean!)
```
/primehaul-os
├── README.md                           # Main docs
├── QUICK_START_STAGING.md             # Quick deployment
├── STAGING_DEPLOYMENT_GUIDE.md        # Detailed staging
├── PRIMEHAUL_UK_DEPLOYMENT.md         # Production deployment
├── WEBSITE_READY.md                   # Website overview
├── UX_IMPROVEMENTS_SUMMARY.md         # UX documentation
├── .env.example                        # Config template
├── requirements.txt                    # Dependencies
├── alembic.ini                         # DB migrations
├── create_test_company.py             # Test utility
├── reset_test_data.py                 # Test utility
├── check_user.py                      # Admin utility
├── create_pricing_config.py           # Setup utility
├── app/                                # Application code
├── alembic/                            # Migrations
└── docs/                               # Documentation
    └── archive/                        # Archived materials
        ├── planning/                   # Old planning docs
        ├── marketplace/                # Marketplace docs (future)
        └── old-migrations/             # Old migration scripts
```

---

## 🎨 Benefits

### Clarity
✅ Clear what's essential vs. reference
✅ Easy for new developers to understand
✅ Focus on production code

### Performance
✅ Faster deployments (fewer files)
✅ Cleaner Git history
✅ Smaller repository size

### Maintenance
✅ Less confusion about which files are current
✅ Easier to find documentation
✅ Better organized

---

## ⚠️ Important Notes

### Don't Delete Yet If:
- You haven't backed up the project
- You're in the middle of a feature
- You're not sure what a file does

### Safe to Delete:
- Old planning docs (archived)
- Superseded templates (old versions)
- One-time migration scripts (alembic handles migrations)

---

## 🚀 Recommended Action

**Do this cleanup AFTER:**
1. ✅ Current backup is created
2. ✅ You've tested staging deployment
3. ✅ Everything works on staging

**Then:**
1. Create archive folders
2. Move files (don't delete yet)
3. Test everything still works
4. If all good after 1 week, can delete archives

---

## 📝 Summary

**Current State**: 65+ files (bloated)
**After Cleanup**: ~40 essential files (streamlined)
**Archived**: ~22 files (safe to remove later)

**Result**: Clean, professional, production-ready codebase! 🎉

---

**Status**: Ready to execute
**Risk**: Low (archiving, not deleting)
**Time**: 10 minutes
**Impact**: Much cleaner codebase
