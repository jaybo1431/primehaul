# 🚀 PrimeHaul Marketplace - "Uber for Removals"

**Customer submits once. Companies bid. Customer picks winner. We take 15%.**

---

## 🎯 The Vision

### Old Model (B2B SaaS Only):
```
Customer → Company A's survey → Quote → Company A approves → Done
```
- Each company markets separately
- You sell 500 times to get 500 customers
- Revenue ceiling: £346k/year (3,500 companies × £99)

### New Model (Hybrid B2B + Marketplace):
```
Customer → Central PrimeHaul survey → Broadcast to ALL companies → Companies bid → Customer picks → 15% commission
```
- YOU market once to consumers
- Companies fight for jobs
- Revenue ceiling: £8-21M/year (marketplace transactions)

---

## 💰 Revenue Comparison

### B2B SaaS (Current):
```
100 companies × £99/month = £9,900/month
```

### Marketplace (New):
```
100 jobs/month × £700 avg × 15% = £10,500/month
1,000 jobs/month × £700 × 15% = £105,000/month 🚀
```

**The marketplace scales with JOB VOLUME, not company count.**

---

## 🔄 How It Works (Customer Flow)

### 1. **Customer Visits PrimeHaul.com**
- Landing page: "Get removal quotes in 5 minutes"
- NOT company-specific
- Central marketplace

### 2. **Customer Fills Out Survey**
- Same AI-powered flow (photos, map, property type)
- Takes 5 minutes
- AI analyzes everything

### 3. **Job Broadcasts to Companies**
- All companies within 50 miles get notified
- Email: "New removal job in London - 12.5 CBM - View & Bid"
- 48-hour bidding window

### 4. **Companies Submit Bids**
- Company sees full details (items, photos, locations)
- Submits price + optional message
- Example: "£850 - We can do this Thursday! 3-man crew."

### 5. **Customer Picks Winner**
- Sees all bids in dashboard
- Compares prices, reviews, crew size
- Accepts best bid with one click

### 6. **We Charge 15% Commission**
- Winner pays us 15% via Stripe
- Example: £850 job → £127.50 commission → £722.50 to company
- Automatic via Stripe Connect

---

## 🏗️ Database Structure (Already Built!)

### New Tables:

**`marketplace_jobs`** - Central job board
- Customer fills ONE survey
- Job has token like `m_abc123xyz`
- Status: in_progress → open_for_bids → awarded → completed

**`bids`** - Companies bidding
- Links company_id + marketplace_job_id
- Price, message, crew size, duration
- Expires after 48 hours

**`job_broadcasts`** - Notification tracking
- Which companies were notified
- When they viewed the job
- When they submitted bid

**`commissions`** - Our revenue
- Track 15% from each job
- Stripe payment status
- What we're owed vs paid

**`marketplace_rooms`/`items`/`photos`** - Inventory
- Same as company-specific jobs
- Separate tables for marketplace

---

## 💻 Code Architecture

### Main Files:

**`app/models.py`** ✅ DONE
- All marketplace database models
- 7 new tables + relationships

**`alembic/versions/002_add_marketplace.py`** ✅ DONE
- Database migration
- Run with: `alembic upgrade head`

**`app/marketplace.py`** ⏳ TODO (Next 30 min)
- Core marketplace logic
- broadcast_job_to_companies()
- auto_generate_bids()
- accept_bid()
- charge_commission()

**`app/templates/marketplace_*.html`** ⏳ TODO
- Customer landing page
- Customer survey flow (reuse existing)
- Customer bid selection
- Company bidding interface

**`app/notifications.py`** ⏳ TODO
- Email companies when new job
- Email customer when new bid
- Email when job awarded

---

## 🎨 User Interfaces Needed

### 1. Customer Landing Page
**URL:** `/marketplace` or just `/` (homepage)

**Design:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Get Removal Quotes in 5 Minutes

  AI analyzes your photos
  Companies compete for your job
  You pick the best price

  [Start Free Survey →]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. Customer Survey Flow
**URL:** `/marketplace/{token}/*`

**Reuse existing survey pages:**
- `/marketplace/{token}` - Start
- `/marketplace/{token}/move` - Pickup/dropoff map
- `/marketplace/{token}/property` - Property type
- `/marketplace/{token}/rooms` - Room picker
- `/marketplace/{token}/room/{room_id}` - Photo upload
- `/marketplace/{token}/contact` - Customer details
- `/marketplace/{token}/quotes` - **NEW** - View bids

### 3. Customer Quotes Dashboard
**URL:** `/marketplace/{token}/quotes`

**Design:**
```
Your Removal Job - 12.5 CBM
London → Manchester (210 miles)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quotes Received (3)

┌─────────────────────────────┐
│ ABC Removals ⭐⭐⭐⭐⭐ (4.8)  │
│ £850                         │
│ "We can do Thursday!"        │
│ 3-man crew • 8 hours         │
│ [Accept Quote →]             │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Fast Movers ⭐⭐⭐⭐ (4.2)     │
│ £920                         │
│ "Available this week"        │
│ 2-man crew • 10 hours        │
│ [Accept Quote →]             │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Budget Removals ⭐⭐⭐ (3.9)  │
│ £750                         │
│ "Cheapest price!"            │
│ 2-man crew • 12 hours        │
│ [Accept Quote →]             │
└─────────────────────────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Company Marketplace Dashboard
**URL:** `/{company_slug}/admin/marketplace`

**Design:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Available Jobs in Your Area

┌─────────────────────────────┐
│ 🆕 London → Manchester      │
│ 12.5 CBM • 3-bed house      │
│ 210 miles • Thursday move   │
│ Est: £850-950               │
│ [View Details & Bid →]      │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Birmingham → Bristol         │
│ 8.2 CBM • 2-bed flat        │
│ 90 miles • Flexible         │
│ Est: £550-650               │
│ [View Details & Bid →]      │
└─────────────────────────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Active Bids (2)
[Show bids you've submitted]

Your Won Jobs (5)
[Jobs you won in last 30 days]
```

### 5. Bid Submission Form
**URL:** `/{company_slug}/admin/marketplace/job/{job_id}/bid`

**Design:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Submit Your Bid

Job Details:
- 12.5 CBM
- 3-bed house
- Living Room, 2 Bedrooms, Kitchen
- 157 items detected by AI

Your Pricing (Auto-calculated):
Base: £250
Volume: £437.50 (12.5 × £35)
Bulky surcharge: £75
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Suggested Price: £762.50

Your Bid:
Price: £[___850___]
Message: "We can do this Thursday!"
Crew Size: [_3_] movers
Duration: [_8_] hours

[Submit Bid →]

After you win:
Job price: £850
Commission (15%): -£127.50
You receive: £722.50
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📧 Email Notifications

### Email 1: Job Posted (To Companies)
```
Subject: 🆕 New removal job in London - £850-950

Hi ABC Removals,

A new removal job just posted in your area:

📍 London → Manchester (210 miles)
🏠 3-bed house (12.5 CBM)
📅 Preferred date: Thursday
💰 Estimated price: £850-950

[View Job & Submit Bid →]

You have 48 hours to submit a bid.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PrimeHaul Marketplace
```

### Email 2: New Bid (To Customer)
```
Subject: You have a new quote for your removal

Hi Sarah,

ABC Removals just submitted a quote for your move:

💰 Price: £850
👥 3-man crew
⏱️ Estimated 8 hours
📝 "We can do this Thursday!"

[View All Quotes →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PrimeHaul
```

### Email 3: Job Awarded (To Winner)
```
Subject: 🎉 You won the job! £850 - London removal

Congratulations!

Sarah picked your bid for the removal job.

Job Details:
- Price: £850
- Commission: -£127.50 (15%)
- You receive: £722.50

Customer Contact:
Sarah Johnson
07123 456789
sarah@email.com

[View Full Job Details →]

Next steps:
1. Contact customer to confirm date
2. Complete the move
3. Get paid automatically

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PrimeHaul Marketplace
```

### Email 4: Job Awarded (To Losers)
```
Subject: Job filled - Keep bidding!

Hi,

The removal job from London → Manchester has been awarded to another company.

Don't worry - more jobs are posted daily!

[View Available Jobs →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PrimeHaul Marketplace
```

---

## 🔧 Implementation Steps (Next 2 Weeks)

### Week 1: Core Marketplace

**Day 1-2: Database & Models** ✅ DONE
- [x] Create marketplace models
- [x] Create migration file
- [ ] Run migration: `alembic upgrade head`

**Day 3-4: Job Broadcasting**
- [ ] Create `app/marketplace.py`
- [ ] Function: `broadcast_job_to_companies(job_id, radius_miles)`
- [ ] Function: `find_companies_in_radius(lat, lng, radius)`
- [ ] Function: `send_job_notification_email(company, job)`

**Day 5-7: Bidding System**
- [ ] Company marketplace dashboard template
- [ ] Bid submission form
- [ ] POST endpoint: submit_bid()
- [ ] Email notification when bid submitted

### Week 2: Customer Experience

**Day 8-9: Customer Survey Flow**
- [ ] Marketplace landing page
- [ ] Reuse existing survey templates (with marketplace URLs)
- [ ] Customer contact form (with email opt-in)

**Day 10-12: Bid Selection**
- [ ] Customer quotes dashboard
- [ ] Accept bid endpoint
- [ ] Email notifications (winner + losers)
- [ ] Commission calculation + tracking

**Day 13-14: Testing & Polish**
- [ ] End-to-end test: Customer → Bids → Accept → Commission
- [ ] Fix bugs
- [ ] Add analytics tracking
- [ ] Update dev dashboard with marketplace metrics

---

## 💡 Smart Features

### Auto-Generated Bids (Optional)
Companies can enable "auto-bid":
```
If job < 50 miles from my location:
  Auto-bid at: My pricing rules + 10% margin
  Max jobs/week: 5
```

**Benefit:** Companies never miss a job opportunity.

### Instant Accept (Optional)
If only 1 bid after 24 hours:
```
Show customer: "Accept now and secure your date!"
```

**Benefit:** Faster conversion, less waiting.

### Review System (Future)
After job completion:
```
Customer rates company: 1-5 stars + review
Shows on future bids: "⭐⭐⭐⭐⭐ (4.8) - 23 reviews"
```

**Benefit:** Quality control, trust building.

---

## 📊 Metrics to Track (Dev Dashboard)

Add to dev dashboard:

**Marketplace Metrics:**
- Total marketplace jobs (all time)
- Jobs today (open for bids)
- Total bids received
- Avg bids per job (target: 3-5)
- Acceptance rate (jobs with winner / total jobs)
- Avg bid response time
- Commission owed (pending)
- Commission collected (paid)

**Marketplace Revenue:**
- Commission MRR (monthly)
- Avg commission per job
- Total marketplace revenue (all time)

**Company Performance:**
- Top bidders (most bids submitted)
- Top winners (most jobs won)
- Win rate by company

---

## 🚨 Edge Cases to Handle

### 1. **No Bids After 48 Hours**
```
Email customer: "No quotes yet. Try extending your deadline or adjusting your requirements."
Suggest: Contact companies directly
```

### 2. **Customer Accepts Then Cancels**
```
Charge cancellation fee (10% of bid price)
Compensate company for time
Refund customer minus fee
```

### 3. **Company Doesn't Show Up**
```
Ban company from marketplace
Refund customer
Find replacement company
```

### 4. **Dispute After Job**
```
Escrow payment for 7 days
Allow dispute filing
Mediate or refund
```

### 5. **Company Overbids (Way Too High)**
```
Show warning: "This bid is 50% higher than similar jobs"
Suggest price range
```

---

## 🎯 Launch Strategy (First 30 Days)

### Week 1: Soft Launch (Internal Testing)
- Get 3 of your existing B2B customers to join marketplace
- Post 5 test jobs yourself
- Test bidding → acceptance → commission
- Fix bugs

### Week 2: Beta Launch (10 Real Customers)
- Run £500 Google Ads campaign
- Target: "removal quotes London"
- Get 10 real customer submissions
- Manually broadcast to companies
- Track conversion rate

### Week 3: Scale Marketing
- If Week 2 works (>50% of jobs get bids):
  - Increase Google Ads to £2,000/month
  - Launch Facebook ads
  - SEO content (blog posts)
- Target: 50 jobs/month

### Week 4: Optimize & Iterate
- Analyze data: Which companies win most? Why?
- Customer feedback: Why did you pick that bid?
- Company feedback: How can we get you more jobs?
- Improve UX based on feedback

**Goal:** 100 marketplace jobs/month by Month 2
- 100 jobs × £700 avg × 15% = £10,500 commission/month
- Plus £5,000 B2B SaaS = **£15,500 total MRR**

---

## 🏆 Success Criteria

**Marketplace is working when:**
- ✅ 80% of jobs receive at least 1 bid
- ✅ Avg 3-5 bids per job
- ✅ 60%+ of jobs get accepted (customer picks winner)
- ✅ <5% disputes/cancellations
- ✅ Companies keep coming back (win rate 20-30%)

**Revenue is working when:**
- ✅ Marketplace revenue > B2B revenue
- ✅ CAC < £50 per job
- ✅ Commission collection rate > 95%

---

## 🔥 Why This Will Win

**vs AnyVan/Shiply:**
1. ✅ **AI-powered** (they're manual entry - slow & tedious)
2. ✅ **5-minute survey** (theirs take 30+ minutes)
3. ✅ **Mobile-first** (theirs are clunky desktop)
4. ✅ **Instant AI quotes** (theirs wait for companies to manually calculate)

**Competitive Advantage:**
```
AnyVan: Customer types everything → Wait days → Get quotes
PrimeHaul: Customer takes photos → AI does it → Instant quotes → Companies bid

Result: 10x faster, 10x better UX
```

---

## 🚀 Next Steps (Right Now!)

1. **Run the migration:**
```bash
alembic upgrade head
```

2. **Build marketplace.py:**
```bash
# See implementation in app/marketplace.py
# Coming in next 30 minutes!
```

3. **Create templates:**
```bash
# See app/templates/marketplace_*.html
# Customer flow + company bidding UI
```

4. **Test end-to-end:**
```bash
# Submit marketplace job
# Broadcast to companies
# Companies bid
# Customer accepts
# Commission charged
```

5. **Launch beta:**
```bash
# Run £500 Google Ads test
# Get 10 real customers
# Validate demand
# SCALE!
```

---

**LET'S BUILD THE UBER OF REMOVALS! 🚀**
