# 🚀 PrimeHaul OS - AI-Powered Quote System for UK Removal Companies

**Transform your removal business with AI-powered instant quotes. Your customers fill out a 5-minute survey, AI analyzes photos, you approve from your phone. Win more jobs.**

---

## 🎯 What is PrimeHaul OS?

PrimeHaul OS is a **multi-tenant B2B SaaS platform** that helps UK removal companies:

1. **Generate instant, accurate quotes** using AI photo analysis
2. **Respond 10x faster** than competitors (approve from your phone in 30 seconds)
3. **Win 30% more jobs** through faster response times
4. **Eliminate wasted site visits** (customers self-survey with AI validation)

### Business Model

- **Customers** (people moving house) → Use surveys **FREE**
- **Removal companies** ("the boss") → Pay **£99/month** subscription

---

## ✨ Key Features

### For Removal Companies (Paid Subscribers)

- ✅ **AI Photo Analysis** - Customers take photos, AI identifies every item, calculates CBM
- ✅ **Mobile Boss Mode** - Approve quotes from your phone anywhere (job sites, in truck, at home)
- ✅ **Custom Branding** - Upload your logo, set your brand colors
- ✅ **Custom Pricing Rules** - Configure £/CBM rates, callout fees, surcharges
- ✅ **Multi-User Accounts** - Owner, Admin, Member roles
- ✅ **Analytics Dashboard** - Quote volume, conversion rates, AI costs, revenue trends
- ✅ **Unlimited Quotes** - No per-quote fees, unlimited usage
- ✅ **30-Day Free Trial** - No credit card required

### For Customers (Free)

- ✅ **5-Minute Survey** - Works on any phone or computer
- ✅ **Interactive Map** - Pick pickup/dropoff locations (Mapbox)
- ✅ **Photo Upload** - Take photos of each room
- ✅ **Instant Quote** - See price estimate immediately
- ✅ **Branded Experience** - See the removal company's branding, not ours

### Technical Features

- ✅ **Multi-Tenant Architecture** - Complete data isolation between companies
- ✅ **PostgreSQL Database** - Scalable, production-ready
- ✅ **Stripe Billing** - Subscription management, trial tracking, webhooks
- ✅ **JWT Authentication** - Secure, role-based access control
- ✅ **ML Data Collection** - Track 100% of user interactions for future AI improvements
- ✅ **Mobile-First Design** - Touch-optimized, works perfectly on phones
- ✅ **Real-Time Updates** - Auto-refresh dashboards

---

## 🚀 Quick Start (Testing Today)

### Option 1: Test Locally (5 minutes)

```bash
# 1. Clone and install
git clone <repo-url>
cd primehaul-os
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and MAPBOX_ACCESS_TOKEN

# 3. Start the server
./start_test.sh

# 4. Open on your phone (use the URL shown by the script)
```

### Option 2: Deploy to Production

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for complete deployment instructions.

---

## 📚 Documentation

### For Developers

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - How to deploy to production (Heroku, Railway, DigitalOcean)
- **[ML_DATA_STRATEGY.md](ML_DATA_STRATEGY.md)** - Machine learning roadmap and data collection strategy
- **[ML_QUICK_START.md](ML_QUICK_START.md)** - Get ML insights in 15 minutes with SQL queries
- **[MOBILE_BOSS_MODE.md](MOBILE_BOSS_MODE.md)** - Mobile-first features and optimization

### For Marketing & Sales

- **[UK_LEAD_GENERATION_STRATEGY.md](UK_LEAD_GENERATION_STRATEGY.md)** - 10-channel lead gen strategy for UK market
- **[LEAD_GEN_QUICK_START.md](LEAD_GEN_QUICK_START.md)** - Get your first 10 trials in 7 days
- **[EMAIL_TEMPLATES.md](EMAIL_TEMPLATES.md)** - Ready-to-use cold email sequences and automation
- **[LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)** - Complete checklist from setup to first customer

### For Testing

- **[TEST_TODAY.md](TEST_TODAY.md)** - Test the system on phone + PC right now

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database (via SQLAlchemy)
- **Alembic** - Database migrations
- **Stripe** - Subscription billing & webhooks
- **JWT** - Secure authentication

### AI & ML
- **OpenAI GPT-4o-mini** - Vision API for item detection
- **Custom ML tracking** - Behavioral analytics for future models

### Frontend
- **Jinja2 Templates** - Server-side rendering
- **Vanilla JavaScript** - No framework bloat
- **Mobile-First CSS** - Touch-optimized, responsive
- **Mapbox GL JS** - Interactive maps

### Infrastructure
- **Heroku / Railway / Render** - Deployment platforms
- **GitHub Actions** - CI/CD (optional)
- **Google Analytics** - Marketing analytics

---

## 📁 Project Structure

```
primehaul-os/
├── app/
│   ├── main.py                 # Core FastAPI app (1,900+ lines)
│   ├── models.py               # Database models (10+ tables)
│   ├── database.py             # PostgreSQL connection
│   ├── auth.py                 # JWT & password hashing
│   ├── dependencies.py         # FastAPI dependencies
│   ├── billing.py              # Stripe integration
│   ├── ai_vision.py            # OpenAI Vision API
│   ├── static/
│   │   ├── app.css             # Main styles
│   │   ├── mobile-admin.css    # Mobile optimizations
│   │   ├── tracker.js          # ML behavioral tracking
│   │   └── uploads/            # Customer photos (company-isolated)
│   └── templates/
│       ├── landing_page.html   # Marketing homepage
│       ├── cbm_calculator.html # Free lead magnet tool
│       ├── auth_*.html         # Login/signup pages
│       ├── admin_*.html        # Admin dashboard & settings
│       ├── billing_*.html      # Stripe billing pages
│       └── *.html              # Customer survey pages
│
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── start_test.sh              # Quick start script
│
├── README.md                  # This file
├── DEPLOYMENT_GUIDE.md        # Production deployment
├── ML_DATA_STRATEGY.md        # ML roadmap
├── UK_LEAD_GENERATION_STRATEGY.md  # Marketing strategy
├── EMAIL_TEMPLATES.md         # Email sequences
├── LAUNCH_CHECKLIST.md        # Complete launch plan
└── TEST_TODAY.md             # Testing guide
```

---

## 🔐 Security Features

- ✅ **Multi-tenant isolation** - Each company's data is completely separate
- ✅ **Row-level security** - Every query filters by `company_id`
- ✅ **JWT authentication** - Secure, httpOnly cookies
- ✅ **Password hashing** - Bcrypt with salt
- ✅ **Role-based access** - Owner, Admin, Member permissions
- ✅ **SQL injection protection** - SQLAlchemy ORM
- ✅ **XSS protection** - Jinja2 auto-escaping
- ✅ **File upload validation** - Type, size, and content checks
- ✅ **Stripe webhook verification** - Signed requests only
- ✅ **Security headers** - X-Frame-Options, CSP, HSTS
- ✅ **GDPR compliant** - Data deletion on cancellation

---

## 🎬 How It Works (5 Minutes)

### For the Customer (FREE):

1. **Get survey link** from removal company (via email, text, or website)
2. **Enter pickup/dropoff** addresses on interactive map
3. **Select property type** (1-bed flat, 3-bed house, etc.)
4. **Take photos** of each room with their phone camera
5. **AI analyzes photos** and generates detailed inventory list
6. **See instant quote** with pricing breakdown
7. **Submit contact details** to book the job

### For the Removal Company (£99/month):

1. **Sign up** for 30-day free trial at `/auth/signup`
2. **Customize branding** (upload logo, set colors)
3. **Set pricing rules** (£/CBM, callout fees, surcharges)
4. **Share survey link** with customers
5. **Get notification** when quote submitted
6. **Review on phone** (anywhere: job site, truck, office)
7. **Approve in 30 seconds** with one tap
8. **Win the job!** 🎉

---

## 💰 Pricing & Business Model

### For Removal Companies:

**£99/month (unlimited)**
- Unlimited quotes
- Unlimited users
- AI photo analysis
- Custom branding
- Custom pricing
- Mobile dashboard
- Analytics
- 30-day free trial
- Cancel anytime

**Trial-to-Paid Conversion Target:** 25-40%

### Revenue Projections (Year 1):

| Month | Trials | Paid | MRR | ARR |
|-------|--------|------|-----|-----|
| 1 | 20 | 5 | £495 | £5,940 |
| 3 | 60 | 15 | £1,485 | £17,820 |
| 6 | 120 | 30 | £2,970 | £35,640 |
| 12 | 250 | 60 | £5,940 | £71,280 |

**Target:** £594,000 ARR by end of Year 1 (500 paying customers)

---

## 📊 Key Metrics to Track

### Acquisition Metrics:
- **CAC (Customer Acquisition Cost):** Target: £50-£100
- **Trial Signups:** Target: 50/month by Month 3
- **Trial Activation Rate:** Target: 60% (send first survey)
- **Trial-to-Paid Conversion:** Target: 25-40%

### Engagement Metrics:
- **Quotes per Company:** Target: 10/month average
- **Response Time:** Target: <30 minutes (mobile approval)
- **Customer Survey Completion Rate:** Target: 70%

### Revenue Metrics:
- **MRR (Monthly Recurring Revenue)**
- **Churn Rate:** Target: <10%/month
- **LTV (Lifetime Value):** Target: £600+ (6+ months retention)
- **LTV:CAC Ratio:** Target: 3:1 or better

---

## 🚦 Getting Started

### 1. **For Testing (Today):**

Follow **[TEST_TODAY.md](TEST_TODAY.md)**

```bash
./start_test.sh
# Open survey on phone, test admin dashboard on PC
```

### 2. **For Deployment (This Week):**

Follow **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

- Set up PostgreSQL database
- Deploy to Heroku/Railway/Render
- Configure Stripe billing
- Launch!

### 3. **For Lead Generation (Week 2):**

Follow **[LEAD_GEN_QUICK_START.md](LEAD_GEN_QUICK_START.md)**

- Get first 500 UK removal company leads
- Set up cold email automation
- Launch Google Ads campaign
- Get first 10 trials in 7 days

### 4. **For Scaling (Month 2+):**

Follow **[LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)**

- Optimize conversion rates
- Scale best-performing channels
- Expand to new marketing channels
- Reach profitability

---

## 🛣️ Roadmap

### ✅ Phase 1: B2B SaaS Foundation (COMPLETE)
**Revenue Model:** £99/month per company
**Target:** 50 companies = £4,950 MRR

- [x] Multi-tenant B2B SaaS architecture
- [x] PostgreSQL database with migrations
- [x] JWT authentication & role-based access
- [x] Stripe subscription billing with 30-day trials
- [x] Custom branding (logo, colors)
- [x] Custom pricing rules (£/CBM, fees)
- [x] AI photo analysis (OpenAI Vision)
- [x] Mobile-responsive admin dashboard (Boss Mode)
- [x] ML data collection infrastructure
- [x] Analytics dashboard
- [x] Landing page & lead magnet (CBM calculator)
- [x] Email templates for lead generation
- [x] Dev dashboard (mission control)
- [x] Complete documentation (15+ guides)

**Status:** ✅ Production-ready. Launch Week 1.

---

### 🚀 Phase 2: MARKETPLACE - "Uber for Removals" (IN PROGRESS)
**Revenue Model:** 15% commission per job
**Target:** 100 jobs/month = £10,500 commission MRR

**Database & Models** (Week 1) ✅ DONE:
- [x] MarketplaceJob model (central job board)
- [x] Bid model (companies bidding)
- [x] JobBroadcast model (notification tracking)
- [x] Commission model (revenue tracking)
- [x] MarketplaceRoom/Item/Photo models
- [x] Database migration file created

**Core Marketplace Logic** (Week 1) ⏳ IN PROGRESS:
- [ ] Job broadcasting system
  - Find companies within radius
  - Send email notifications
  - Track who was notified
- [ ] Auto-bid generation (optional)
  - Companies enable auto-bid
  - Bids created from pricing rules
- [ ] Bid management
  - Companies view available jobs
  - Submit manual bids
  - Edit/withdraw bids

**Customer Flow** (Week 1-2) ⏳ NEXT:
- [ ] Marketplace landing page (`/marketplace`)
- [ ] Customer survey (reuse existing flow)
- [ ] Customer quotes dashboard
  - View all bids
  - Compare prices
  - Accept winner
- [ ] Email notifications
  - New job notification (to companies)
  - New bid notification (to customer)
  - Job awarded (to winner + losers)

**Company Dashboard** (Week 2) ⏳ NEXT:
- [ ] Marketplace jobs feed
- [ ] Bid submission form
- [ ] Active bids tracking
- [ ] Won jobs tracking
- [ ] Commission calculator

**Payment & Commission** (Week 2) ⏳ NEXT:
- [ ] Stripe Connect integration
- [ ] Automatic 15% commission charge
- [ ] Commission tracking dashboard
- [ ] Payout to companies

**Testing & Launch** (Week 2):
- [ ] End-to-end test (customer → bid → accept → commission)
- [ ] Beta launch (10 real customers via £500 Google Ads)
- [ ] Iterate based on feedback
- [ ] Scale to 100 jobs/month

**Success Metrics:**
- 80% of jobs receive bids
- 3-5 bids per job (average)
- 60%+ acceptance rate
- <5% disputes/cancellations

---

### 🎯 Phase 3: Hybrid Optimization (Month 2-3)
**Combined Revenue:** B2B (£4,950) + Marketplace (£10,500) = **£15,450 MRR**

**Optimize Conversion:**
- [ ] A/B test landing pages
- [ ] Improve bidding UX
- [ ] Add review system (5-star ratings)
- [ ] Add instant accept (if 1 bid after 24h)
- [ ] Add urgency indicators ("2 companies viewing now")

**Quality Control:**
- [ ] Company verification (insurance, license)
- [ ] Automatic quality scores
- [ ] Ban low-rated companies
- [ ] Dispute resolution system
- [ ] Escrow payments (hold for 7 days)

**Marketing Scale:**
- [ ] Increase Google Ads to £2,000/month
- [ ] Launch Facebook/Instagram ads
- [ ] SEO content (10 blog posts)
- [ ] Referral program (customer + company)
- [ ] Partnership with estate agents

**Analytics & ML:**
- [ ] Bid prediction model (suggest optimal bid price)
- [ ] Lead quality scoring
- [ ] Churn prediction
- [ ] Dynamic pricing recommendations

---

### 📈 Phase 4: Scale & Dominate (Month 4-12)
**Target:** £100,000+ MRR

**Geographic Expansion:**
- [ ] Launch in top 20 UK cities
- [ ] City-specific landing pages
- [ ] Local SEO optimization
- [ ] Regional pricing variations

**Premium Features:**
- [ ] Priority bidding (pay extra to be shown first)
- [ ] Guaranteed jobs (companies pre-pay for X jobs/month)
- [ ] Premium listings (featured company badge)
- [ ] Dedicated account manager (enterprise companies)

**Customer Experience:**
- [ ] Mobile app (React Native)
- [ ] Real-time bidding (WebSockets)
- [ ] Live chat with companies
- [ ] Video quotes (companies record video intro)
- [ ] In-app payment (pay deposit upfront)

**Company Tools:**
- [ ] Route optimization (plan multi-job days)
- [ ] Crew scheduling
- [ ] Invoice generation
- [ ] Customer CRM
- [ ] Analytics dashboard (win rate, revenue trends)

**Automation:**
- [ ] Email/SMS notifications (SendGrid, Twilio)
- [ ] Push notifications (browser + mobile)
- [ ] WhatsApp integration
- [ ] Calendar sync (Google Calendar, Outlook)
- [ ] Zapier integration

---

### 🚀 Phase 5: Platform Expansion (Year 2+)
**Target:** £500,000+ MRR | £6M+ ARR

**New Verticals:**
- [ ] Commercial removals (offices, warehouses)
- [ ] International moves
- [ ] Storage marketplace
- [ ] Packing services marketplace
- [ ] Cleaning services marketplace

**White-Label:**
- [ ] Sell platform to large removal companies
- [ ] Custom domain support
- [ ] Full branding control
- [ ] API access
- [ ] Dedicated infrastructure

**Advanced ML:**
- [ ] Demand forecasting
- [ ] Dynamic pricing engine
- [ ] Customer lifetime value prediction
- [ ] Fraud detection
- [ ] Photo quality auto-enhancement

**Technology:**
- [ ] Subdomain support (`{company}.primehaul.com`)
- [ ] Custom domain support
- [ ] Voice commands ("Hey Siri, bid £850")
- [ ] Apple Watch app
- [ ] AI chatbot for customer support
- [ ] Blockchain for transparent pricing (maybe)

---

## 📊 Revenue Milestones

| Milestone | B2B SaaS | Marketplace | Total MRR | Timeline |
|-----------|----------|-------------|-----------|----------|
| Launch | £495 (5 companies) | £0 | **£495** | Month 1 |
| Beta | £2,970 (30 companies) | £3,150 (30 jobs) | **£6,120** | Month 2 |
| Scale | £4,950 (50 companies) | £10,500 (100 jobs) | **£15,450** | Month 3 |
| Growth | £9,900 (100 companies) | £31,500 (300 jobs) | **£41,400** | Month 6 |
| Dominate | £19,800 (200 companies) | £105,000 (1,000 jobs) | **£124,800** | Month 12 |

**Year 1 ARR Target:** £1.5M (realistic with execution)
**Year 2 ARR Target:** £6M (if marketplace scales)

---

## 🎯 Current Focus (Next 14 Days)

**Week 1: Build Marketplace Core**
- [x] Database models ✅
- [x] Migration file ✅
- [ ] Job broadcasting logic
- [ ] Company bidding interface
- [ ] Email notifications

**Week 2: Customer Experience + Testing**
- [ ] Marketplace landing page
- [ ] Customer bid selection UI
- [ ] End-to-end test
- [ ] Launch £500 Google Ads beta
- [ ] Get 10 real marketplace jobs

**Goal:** Prove marketplace works with real customers by Day 14.

---

**See [MARKETPLACE_GUIDE.md](MARKETPLACE_GUIDE.md) for complete implementation details.**

---

## 🤝 Contributing

This is a proprietary commercial project. For issues, questions, or feature requests:

1. Open a GitHub issue
2. Email: hello@primehaul-os.com

---

## 📝 License

Proprietary. All rights reserved.

---

## 🎉 Success Stories (Coming Soon)

### Target Case Study:

**ABC Removals (London)**
- Before PrimeHaul OS:
  - 40 quote requests/month
  - 20 jobs won (50% conversion)
  - £12,000/month revenue
  - 15 hours/week on site visits

- After PrimeHaul OS (3 months):
  - 40 quote requests/month (same)
  - 26 jobs won (65% conversion!) 🚀
  - £15,600/month revenue (+£3,600!)
  - 5 hours/week on site visits (-10 hours saved!)
  - ROI: 36x (£99 cost → £3,600 extra revenue)

---

## 🏆 Competitive Advantages

### vs Traditional Quoting:
- **10x faster response time** (30 seconds vs 4 hours)
- **No site visits needed** (AI analyzes photos remotely)
- **Mobile-first** (boss approves from anywhere)
- **Accurate pricing** (AI calculates CBM precisely)

### vs Competitors (other removal software):
- **AI-powered** (most competitors are manual entry)
- **Mobile-optimized** (most are desktop-only)
- **Simple pricing** (£99/month unlimited, not per-quote fees)
- **Customer does the work** (self-survey, not office admin)

---

## 📞 Support

- **Documentation:** See `/docs` folder
- **Email:** hello@primehaul-os.com
- **Issues:** GitHub Issues
- **Live chat:** Coming soon

---

**Built with ❤️ for UK removal companies who want to win more jobs and waste less time.**

**Ready to launch? Follow [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) and get your first customer in 30 days! 🚀**
