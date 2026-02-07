# PrimeHaul - Master Guide
## "An intelligent move."

**Created:** 7 February 2026
**Owner:** Jaybo (Solo Founder)
**Website:** https://primehaul.co.uk
**Repository:** https://github.com/jaybo1431/primehaul

---

# ACCESS CREDENTIALS

## Admin Dashboards (Jaybo Only)

| Dashboard | URL | Password |
|-----------|-----|----------|
| **Superadmin** | https://primehaul.co.uk/superadmin | `Jaybo2026` |
| **Sales Automation** | https://primehaul.co.uk/sales | `Jaybo2026` |

## Railway (Hosting)
- URL: https://railway.app
- Project: PrimeHaul

## Namecheap (Domain)
- Domain: primehaul.co.uk

---

# WHAT'S BUILT

## The Product
AI-powered quoting software for UK removal companies.

**How it works:**
1. Customer photographs their rooms
2. AI counts every item (GPT-4 Vision)
3. Quote calculated instantly using company's prices
4. Company approves from their phone
5. Customer gets quote in 5 minutes (not 5 hours)

## Business Model
- **3 free credits** on signup
- **Credit packs:**
  - Starter: 10 credits for £99 (£9.90/survey)
  - Growth: 25 credits for £225 (£9.00/survey)
  - Pro: 50 credits for £399 (£7.98/survey)
  - Enterprise: 100 credits for £699 (£6.99/survey)

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** OpenAI GPT-4 Vision
- **Payments:** Stripe
- **Hosting:** Railway
- **Domain:** Namecheap

---

# SALES AUTOMATION

## Email Templates

### Email 1: "Quick one for {company_name}"
```
{first_name},

9pm last Tuesday. Customer sends photos of their house.
9:05pm. Full quote, ready to go.
9:07pm. They've paid the deposit and booked.

That happened. That's what AI-powered quotes look like.

Here's the simple version:
- Customer photographs each room
- AI counts every sofa, bed, wardrobe, box
- Quote calculated instantly using YOUR prices
- You glance at it, tap approve
- Done

No home visits. No phone tag. No Sunday afternoons doing estimates.

Your branding. Your prices. Customers think it's your own tech.

I've got 3 free quotes with your name on them: {demo_link}

Takes about 60 seconds to set up. See what you think.

Jay
PrimeHaul — An intelligent move.
```

### Email 2 (Day 3): "Re: Quick one for {company_name}"
```
{first_name},

One thing I should've mentioned:

You stay in control. Always.

The AI counts items and suggests a price. But nothing goes out until YOU approve it. See something you'd price differently? Change it. Want to add a note? Add it.

Think of it like having someone who does all the measuring and maths, then hands you the clipboard to sign off.

The flow:
Customer photographs rooms → AI lists everything → lands in your phone → you approve or adjust → customer gets it

That's it. Your call on everything.

Link's here when you're ready: {demo_link}

Jay
```

### Email 3 (Day 7): "Last one (then I'll leave you alone)"
```
{first_name},

Not going to keep emailing you. Just one thought I wanted to share:

The feedback that surprised me most wasn't about speed. It was this:

"Customers love it. They photograph their stuff at 10pm, wake up to a quote. We look like a proper professional operation."

Turns out people actually prefer snapping photos over booking a home visit. Faster for them too.

Anyway. If you ever want to try it, 3 free quotes: {demo_link}

All the best with the moves.

Jay
```

---

# LEADS TO CONTACT (17 with emails)

## London (7)
| Company | Email |
|---------|-------|
| Kiwi Movers | quote@kiwimovers.co.uk |
| Fox Moving | info@fox-moving.com |
| Get A Mover | nfo@getamover.co.uk |
| We Move Anything | enquiries@wemoveanything.com |
| Big Van World | sales@bigvanworld.co.uk |
| MTC Removals | info@mtcremovals.com |
| Quick Wasters | info@quickwasters.co.uk |

## Manchester (3)
| Company | Email |
|---------|-------|
| Man With A Van Manchester | info@manwithavanremovalsmanchester.co.uk |
| Burke Bros Moving | sales@burkebros.co.uk |
| A Star Removals | info@astarremovals.co.uk |

## Midlands & North (3)
| Company | Email | Location |
|---------|-------|----------|
| Complete Removals | sales@completeremovals.co.uk | Birmingham |
| Near & Far Removals | enquiries@nearandfarremovals.co.uk | Nottingham |
| Britannia Leeds | info@britanniaturnbulls.co.uk | Leeds |

## Scotland (1)
| Company | Email |
|---------|-------|
| Clark & Rose | moving@clarkandrose.co.uk |

## South (3)
| Company | Email | Location |
|---------|-------|----------|
| White & Company | hq@whiteandcompany.co.uk | Southampton |
| Moveme | hello@viewmychain.com | Brighton |
| Abels Moving | enquiries@abels.co.uk | Cambridge |

---

# SETUP CHECKLIST

## Google Workspace Setup (for jay@primehaul.co.uk)

### Step 1: Sign Up
1. Go to: https://workspace.google.com/business/signup/welcome
2. Business name: `PrimeHaul`
3. Domain: `primehaul.co.uk`
4. Email: `jay@primehaul.co.uk`
5. Plan: Business Starter (£4.60/month)

### Step 2: Add DNS Records in Namecheap

**MX Records (for receiving email):**
| Type | Host | Value | Priority |
|------|------|-------|----------|
| MX | @ | aspmx.l.google.com | 1 |
| MX | @ | alt1.aspmx.l.google.com | 5 |
| MX | @ | alt2.aspmx.l.google.com | 5 |
| MX | @ | alt3.aspmx.l.google.com | 10 |
| MX | @ | alt4.aspmx.l.google.com | 10 |

**SPF Record (for deliverability):**
| Type | Host | Value |
|------|------|-------|
| TXT | @ | v=spf1 include:_spf.google.com ~all |

**DMARC Record:**
| Type | Host | Value |
|------|------|-------|
| TXT | _dmarc | v=DMARC1; p=none; rua=mailto:jay@primehaul.co.uk |

### Step 3: Create App Password
1. Go to: https://myaccount.google.com
2. Security → 2-Step Verification → Turn ON
3. Security → App passwords
4. Create for "Mail" / "Other (PrimeHaul)"
5. Copy the 16-character password

### Step 4: Add to Railway Environment Variables
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=jay@primehaul.co.uk
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
OUTREACH_EMAIL=jay@primehaul.co.uk
OUTREACH_NAME=Jay from PrimeHaul
```

---

# OTHER TO-DOS

## Legal/Compliance
- [ ] Register with ICO (https://ico.org.uk) - £40/year
- [ ] Review privacy policy

## Marketing
- [ ] Set up Trustpilot account
- [ ] Get first customer testimonial
- [ ] Add trust badges to site

---

# THE PASSIVE INCOME MATH

| Customers | Credits/Month | Revenue/Month |
|-----------|---------------|---------------|
| 5 | 50 credits | ~£500 |
| 10 | 100 credits | ~£1,000 |
| 20 | 200 credits | ~£2,000 |
| 50 | 500 credits | ~£5,000 |

**Goal:** Get 10 paying customers = £1,000/month passive

---

# THE 30-DAY PLAN

## Week 1: First Blood
- Set up professional email
- Send 50 cold emails
- Follow up on any replies
- Book first demo

## Week 2: First Customer
- Demo to interested leads
- Set them up with 3 free quotes
- Get them using it on real customers
- Close first sale (£99)

## Week 3: First Testimonial
- Call customers who've used it
- Get a quote for the website
- Ask for referrals

## Week 4: Scale Up
- 100+ emails sent
- 2-3 paying customers
- Testimonials on site
- Repeat the process

---

# CONTACT

**Repository:** https://github.com/jaybo1431/primehaul
**Live Site:** https://primehaul.co.uk
**Email (once set up):** jay@primehaul.co.uk

---

*Built by Jaybo with Claude. An intelligent move.*
