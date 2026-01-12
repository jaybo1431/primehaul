# 🧪 Complete Testing Guide for Sammie Demo

## 🎯 Pre-Demo Checklist

### Step 1: Fresh Database Reset (Railway Production)

**IMPORTANT:** Only do this if you want to completely reset Railway production data.

```bash
# Make sure you're using Railway database
export DATABASE_URL="<your-railway-postgres-url>"

# Run fresh start
python3 FRESH_START.py
```

When prompted, type `RESET` to confirm.

---

## 📱 Customer Flow Testing (Critical for Demo)

### Test URL for Sammie:
```
https://primehaul-production.up.railway.app/s/test-removals-ltd/sammie-demo/start-v2
```

### Complete Customer Journey Test:

#### ✅ Step 1: Start Page (Quote Entry)
- [ ] Page loads with monochrome design (white buttons, black background)
- [ ] Title says "Get an instant quote"
- [ ] Subtitle is professional (no emojis)
- [ ] Address autocomplete works (type "London")
- [ ] Voice button shows SVG microphone icon (not emoji)
- [ ] Property type selector shows clean cards
- [ ] Move date picker works (optional field)
- [ ] Click "Continue" button

**Expected:** Should redirect to access questions

---

#### ✅ Step 2: Access Questions
- [ ] Page loads with "Access details" title
- [ ] Pickup location shows with clean SVG icon (not emoji)
- [ ] Floor selector works (Ground, 1st, 2nd, 3rd, 4th+)
- [ ] If you select 4th+, custom input appears
- [ ] Lift yes/no shows checkmark and warning SVG icons
- [ ] Parking dropdown works
- [ ] Access restrictions checkboxes work
- [ ] Outdoor access dropdown works
- [ ] "Copy from pickup location" button has clean SVG icon
- [ ] Dropoff section mirrors pickup
- [ ] All icons are monochrome white (no green/red/blue)
- [ ] Click "Continue" button

**Expected:** Should redirect to rooms selection

---

#### ✅ Step 3: Rooms Selection
- [ ] Shows available rooms (Bedroom, Living Room, Kitchen, etc.)
- [ ] Can select multiple rooms
- [ ] Click "Continue" button

**Expected:** Should redirect to first room scan

---

#### ✅ Step 4: Room Photo Scanning
- [ ] Camera opens on mobile
- [ ] Can take photo of furniture
- [ ] Shows "Analyzing..." loading state
- [ ] AI detects items from photo
- [ ] Shows detected items with quantities
- [ ] Can add more photos
- [ ] Can proceed to next room or finish

**Expected:** AI should detect furniture items accurately

---

#### ✅ Step 5: Inventory Review
- [ ] Shows all detected items grouped by room
- [ ] Shows total CBM calculation
- [ ] Shows total items count
- [ ] Can edit quantities
- [ ] Click "Get My Quote" button

**Expected:** Should redirect to quote preview

---

#### ✅ Step 6: Quote Preview
- [ ] Shows price range (£X - £Y)
- [ ] Move summary section with clean SVG icons
- [ ] Route details with pickup/dropoff addresses
- [ ] All icons are monochrome (no colored icons)
- [ ] "Submit for review" or "Book your move" button (white with black text)
- [ ] Professional styling throughout

**Expected:** Quote calculated correctly based on items + distance + access

---

#### ✅ Step 7: Customer Contact (if auto-approved)
- [ ] Contact form loads
- [ ] Can enter name, email, phone
- [ ] Click "Confirm Booking" button

**Expected:** Should show confirmation page

---

## 🎨 Visual Design Checklist

### Monochrome Branding:
- [ ] All buttons are WHITE background with BLACK text
- [ ] Shadows are subtle white glows (not blue/colored)
- [ ] Icons are clean monochrome SVG (no emojis)
- [ ] No green/blue/red colored elements (except subtle green for "approved" badge)
- [ ] Dark backgrounds (#0b0b0c, #141416)
- [ ] Text is white or muted white
- [ ] Borders are subtle white lines

### Professional Copy:
- [ ] No exclamation marks
- [ ] No emoji in text (✨, 💰, 🚀, etc.)
- [ ] Clean, action-oriented language
- [ ] "Get an instant quote" not "Get Your Quote!"
- [ ] "Continue" not "Continue →"

---

## 🔧 Admin Dashboard Testing

### Login:
```
URL: https://primehaul-production.up.railway.app/test-removals-ltd/admin/dashboard
Email: admin@test.com
Password: test123
```

### Admin Checklist:
- [ ] Dashboard shows all submitted quotes
- [ ] Can click into quote details
- [ ] Shows customer info, items, access details
- [ ] Shows quote breakdown with pricing
- [ ] Can approve/reject quotes
- [ ] Can add admin notes
- [ ] Keyboard shortcuts work (J/K to navigate)

---

## 🚨 Common Issues & Fixes

### Issue: "Not authenticated" error
**Fix:** Make sure `STAGING_MODE=false` in Railway environment variables

### Issue: Address autocomplete not working
**Fix:** Check that `MAPBOX_ACCESS_TOKEN` is set in Railway

### Issue: Photos not uploading
**Fix:** Check Railway logs for errors, ensure uploads directory exists

### Issue: Quote shows £0
**Fix:** Check that pricing config exists in database (run FRESH_START.py)

---

## 📊 Success Criteria for Sammie Demo

### Must Work Perfectly:
1. ✅ Customer can get quote in under 3 minutes
2. ✅ AI accurately detects furniture from photos
3. ✅ Quote calculation is accurate and realistic
4. ✅ Design is sleek, professional, monochrome
5. ✅ Mobile experience is smooth (test on phone!)
6. ✅ Admin can review and approve quotes quickly

### Nice to Have:
- Custom domain (staging.primehaul.co.uk) - optional
- Multiple test quotes to show variety
- Real-looking test data

---

## 🎬 Demo Script for Sammie

**1. Show Customer Flow (3 min)**
- Open customer URL on your phone
- Fill in addresses (use real London addresses)
- Select property type (2-bed flat)
- Complete access questions (show how detailed it is)
- Take photos of furniture (or use test photos)
- Get instant quote

**2. Show Admin Dashboard (2 min)**
- Log into admin dashboard
- Show quote that was just submitted
- Show detailed breakdown (items, access, pricing)
- Approve the quote
- Show how customer gets notified

**3. Highlight Key Features (1 min)**
- "AI-powered from photos - no manual entry"
- "Accurate quotes with access difficulty factored in"
- "Professional monochrome design"
- "Works perfectly on mobile"
- "2-hour quote approval SLA"

---

## 🔄 Quick Reset for Multiple Demos

If you want to reset between demos:

```bash
# Reset database and create fresh test data
python3 FRESH_START.py

# Or just use new tokens for each demo:
# /s/test-removals-ltd/sammie-demo-1/start-v2
# /s/test-removals-ltd/sammie-demo-2/start-v2
# /s/test-removals-ltd/client-test/start-v2
```

Each unique token creates a fresh quote automatically!

---

## ✅ Final Pre-Demo Checklist

**1 Day Before:**
- [ ] Run FRESH_START.py on Railway database
- [ ] Test complete customer flow on your phone
- [ ] Test admin dashboard on laptop
- [ ] Prepare 2-3 demo URLs with different tokens
- [ ] Take test photos of furniture (or find good stock photos)

**1 Hour Before:**
- [ ] Check Railway deployment is healthy
- [ ] Test one quick quote end-to-end
- [ ] Have admin dashboard open in one tab
- [ ] Have customer URL ready on phone

**During Demo:**
- [ ] Start with customer flow on phone (Sammie can see it's mobile-first)
- [ ] Show admin dashboard on laptop (show the business side)
- [ ] Keep it simple - show the core value
- [ ] Be ready to answer: "How is this different from competitors?"

---

Good luck! 🚀
