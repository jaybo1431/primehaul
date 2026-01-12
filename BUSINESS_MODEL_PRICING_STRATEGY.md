# 💰 PrimeHaul OS - Business Model & Pricing Strategy

## 🚨 THE PROBLEM WITH CURRENT MODEL

**Current Pricing:** £99/month flat fee, unlimited quotes

**The Issue:**
- Small company (10 quotes/month) = £99/month = **£9.90 per quote**
- Large company (200 quotes/month) = £99/month = **£0.50 per quote**
- **You're leaving 95% of revenue on the table with large customers!**

**Real-World Scenario:**
- **Small removal company:** 1-2 trucks, 10-20 quotes/month → £99 is fair
- **Medium company:** 5-10 trucks, 50-100 quotes/month → £99 is a steal (should be £300-500)
- **Large company:** 20+ trucks, 200+ quotes/month → £99 is ridiculous (should be £1,000+)

**Your Costs:**
- OpenAI API: ~£0.10-0.50 per photo analysis (depending on images)
- If large company does 200 quotes/month × 6 photos = 1,200 API calls = **£120-600/month in costs**
- You're losing money on large customers!

---

## 💡 SOLUTION: USAGE-BASED PRICING MODELS

Here are 3 proven pricing models that scale with value:

---

## MODEL 1: TIERED SUBSCRIPTION (RECOMMENDED) ⭐

**Best for:** Predictable revenue, easy to sell, scales with usage

### Pricing Tiers:

| Plan | Monthly Price | Included Quotes | Extra Quotes | Best For |
|------|--------------|-----------------|--------------|----------|
| **Starter** | £49/month | 10 quotes | £5/quote | Small (1-2 trucks) |
| **Professional** | £149/month | 50 quotes | £3/quote | Medium (5-10 trucks) |
| **Enterprise** | £399/month | 200 quotes | £2/quote | Large (20+ trucks) |
| **Unlimited** | £999/month | Unlimited | - | Very large (50+ trucks) |

### Revenue Projections:

**Scenario A: 500 Customers (Mixed)**
- 300 Starter @ £49 = £14,700
- 150 Professional @ £149 = £22,350
- 40 Enterprise @ £399 = £15,960
- 10 Unlimited @ £999 = £9,990
- **Total MRR: £63,000** (vs. £49,500 with flat £99)

**Scenario B: 500 Customers (All Small)**
- 500 Starter @ £49 = £24,500 MRR
- **Still profitable** (vs. £49,500 with flat £99)

**Scenario C: 500 Customers (All Large)**
- 500 Enterprise @ £399 = £199,500 MRR
- **4x more revenue!**

### Implementation:
```python
# In billing.py - add tier checking
def get_quote_limit(company: Company) -> int:
    tier_limits = {
        "starter": 10,
        "professional": 50,
        "enterprise": 200,
        "unlimited": float('inf')
    }
    return tier_limits.get(company.subscription_tier, 10)

def check_quote_limit(company: Company, db: Session) -> bool:
    current_month_quotes = db.query(Job).filter(
        Job.company_id == company.id,
        func.extract('month', Job.created_at) == datetime.now().month
    ).count()
    
    limit = get_quote_limit(company)
    return current_month_quotes < limit
```

### Pros:
✅ Predictable revenue  
✅ Easy to understand  
✅ Scales with company size  
✅ Encourages upgrades  
✅ Fair pricing for all

### Cons:
❌ Need to track usage  
❌ May lose some small customers (but gain more from large)

---

## MODEL 2: BASE + USAGE (HYBRID) 💰

**Best for:** Maximum revenue, aligns with your costs

### Pricing Structure:

**Base Fee:** £49/month (covers platform access)  
**Usage Fee:** £2.50 per quote (covers AI costs + margin)

### Example Costs:
- Small company: 10 quotes = £49 + (10 × £2.50) = **£74/month**
- Medium company: 50 quotes = £49 + (50 × £2.50) = **£174/month**
- Large company: 200 quotes = £49 + (200 × £2.50) = **£549/month**

### Revenue Projections:

**500 Customers (Mixed Usage):**
- Average 30 quotes/month per company
- Base: 500 × £49 = £24,500
- Usage: 500 × 30 × £2.50 = £37,500
- **Total MRR: £62,000**

**Your Costs:**
- OpenAI: 500 × 30 × 6 photos × £0.20 = £18,000/month
- **Gross Margin: £43,500 (70% margin)**

### Implementation:
```python
def calculate_monthly_bill(company: Company, db: Session) -> dict:
    base_fee = 49.00
    quotes_this_month = db.query(Job).filter(
        Job.company_id == company.id,
        func.extract('month', Job.created_at) == datetime.now().month
    ).count()
    
    usage_fee = quotes_this_month * 2.50
    total = base_fee + usage_fee
    
    return {
        "base_fee": base_fee,
        "quotes": quotes_this_month,
        "usage_fee": usage_fee,
        "total": total
    }
```

### Pros:
✅ Maximum revenue potential  
✅ Aligns with your costs  
✅ Fair for all company sizes  
✅ Transparent pricing

### Cons:
❌ More complex billing  
❌ Customers may be surprised by variable costs  
❌ Need usage tracking

---

## MODEL 3: PER-USER PRICING 👥

**Best for:** Companies with multiple surveyors/users

### Pricing Structure:

**£29/user/month** (minimum 2 users = £58/month)

### Example:
- Small: 2 users = £58/month
- Medium: 5 users = £145/month
- Large: 20 users = £580/month

### Revenue Projections:

**500 Companies (Mixed):**
- Average 4 users per company
- 500 × 4 × £29 = **£58,000 MRR**

### Pros:
✅ Scales with team size  
✅ Simple to understand  
✅ Encourages user adoption

### Cons:
❌ Doesn't align with actual usage (quotes)  
❌ May discourage adding users  
❌ Hard to track "active" vs "inactive" users

---

## 🎯 RECOMMENDED MODEL: TIERED SUBSCRIPTION (MODEL 1)

**Why?**
1. **Predictable revenue** - You know MRR upfront
2. **Easy to sell** - Simple tiers, no surprises
3. **Scales naturally** - Large companies pay more
4. **Industry standard** - Most SaaS companies use this
5. **Upgrade path** - Customers can grow into higher tiers

### Pricing Strategy:

**Starter Plan: £49/month (10 quotes)**
- Target: Small companies (1-2 trucks)
- Price point: Low barrier to entry
- Value: £4.90/quote (vs. £9.90 with old model)

**Professional Plan: £149/month (50 quotes)**
- Target: Medium companies (5-10 trucks)
- Price point: Sweet spot for most customers
- Value: £2.98/quote (vs. £1.98 with old model)

**Enterprise Plan: £399/month (200 quotes)**
- Target: Large companies (20+ trucks)
- Price point: Still cheaper than hiring surveyors
- Value: £2.00/quote (vs. £0.50 with old model)

**Unlimited Plan: £999/month**
- Target: Very large companies (50+ trucks)
- Price point: Enterprise pricing
- Value: Unlimited quotes

### Overage Pricing:
- **Starter:** £5/quote over limit
- **Professional:** £3/quote over limit
- **Enterprise:** £2/quote over limit

**Why overage?**
- Prevents customers from hitting limits unexpectedly
- Generates additional revenue
- Encourages upgrades

---

## 📊 REVENUE COMPARISON

### Current Model (£99 flat):
- 500 customers = **£49,500 MRR**
- Large companies subsidize small ones
- You lose money on high-usage customers

### Tiered Model (Recommended):
- 500 customers (mixed) = **£63,000 MRR** (+27%)
- 500 customers (all small) = **£24,500 MRR** (still profitable)
- 500 customers (all large) = **£199,500 MRR** (+303%)

### Hybrid Model (Base + Usage):
- 500 customers (avg 30 quotes) = **£62,000 MRR** (+25%)
- Scales perfectly with usage
- 70% gross margin

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Add Tier Tracking (Week 1)
```python
# Add to Company model:
subscription_tier = Column(String(50), default='starter')  # starter, professional, enterprise, unlimited
quotes_used_this_month = Column(Integer, default=0)
quotes_limit = Column(Integer, default=10)
```

### Phase 2: Update Billing (Week 1)
```python
# Update Stripe price IDs:
STRIPE_PRICE_STARTER = "price_xxx"  # £49/month
STRIPE_PRICE_PROFESSIONAL = "price_yyy"  # £149/month
STRIPE_PRICE_ENTERPRISE = "price_zzz"  # £399/month
STRIPE_PRICE_UNLIMITED = "price_aaa"  # £999/month
```

### Phase 3: Add Usage Tracking (Week 2)
```python
# Track quotes per month
def increment_quote_count(company: Company, db: Session):
    company.quotes_used_this_month += 1
    db.commit()
    
    # Check if over limit
    if company.quotes_used_this_month > company.quotes_limit:
        # Charge overage or block
        charge_overage(company, db)
```

### Phase 4: Add Upgrade Flow (Week 2)
```python
# Add upgrade endpoint
@app.post("/billing/upgrade")
async def upgrade_plan(
    new_tier: str,
    current_user: User = Depends(get_current_user)
):
    # Create new Stripe subscription
    # Update company tier
    # Prorate billing
```

### Phase 5: Migration Strategy (Week 3)
- **Existing customers:** Grandfather at current tier (Starter = £49)
- **New customers:** New pricing immediately
- **Upsell existing:** Email campaign to upgrade

---

## 💡 ADDITIONAL REVENUE OPPORTUNITIES

### 1. **Overage Charges**
- Charge per quote over limit
- Generates 10-20% additional revenue
- Encourages upgrades

### 2. **Add-Ons**
- **Priority Support:** +£29/month
- **Custom Branding:** +£49/month (already included in higher tiers)
- **API Access:** +£99/month
- **White-Label:** +£199/month

### 3. **Annual Plans (Discount)**
- Offer 2 months free for annual payment
- Improves cash flow
- Reduces churn

### 4. **Setup Fees**
- One-time £99 setup fee (waived for annual)
- Covers onboarding costs
- Improves unit economics

---

## 📈 REVENUE PROJECTIONS (TIERED MODEL)

### Year 1 (500 Customers):
**Conservative (All Small):**
- 500 × £49 = **£24,500 MRR** = **£294K ARR**

**Realistic (Mixed):**
- 300 Starter @ £49 = £14,700
- 150 Professional @ £149 = £22,350
- 40 Enterprise @ £399 = £15,960
- 10 Unlimited @ £999 = £9,990
- **Total: £63,000 MRR = £756K ARR**

**Optimistic (More Large):**
- 200 Starter @ £49 = £9,800
- 150 Professional @ £149 = £22,350
- 100 Enterprise @ £399 = £39,900
- 50 Unlimited @ £999 = £49,950
- **Total: £122,000 MRR = £1.46M ARR**

### Year 2 (1,000 Customers):
**Realistic:**
- **£126,000 MRR = £1.51M ARR**
- Plus marketplace commission: +£10,500/month
- **Total: £136,500 MRR = £1.64M ARR**

---

## 🎯 ACTION ITEMS

### Immediate (This Week):
1. ✅ **Decide on pricing model** (recommend Tiered)
2. ✅ **Update Stripe products** (create 4 price tiers)
3. ✅ **Add tier field to Company model**
4. ✅ **Add usage tracking** (quotes per month)

### Short-Term (This Month):
5. ✅ **Build upgrade flow** (let customers change tiers)
6. ✅ **Add usage dashboard** (show quotes used/remaining)
7. ✅ **Update marketing materials** (new pricing)
8. ✅ **Email existing customers** (grandfather + upsell)

### Long-Term (This Quarter):
9. ✅ **Add overage billing** (charge for extra quotes)
10. ✅ **Add annual plans** (2 months free)
11. ✅ **Add-ons marketplace** (priority support, etc.)
12. ✅ **Usage analytics** (help customers optimize)

---

## 💰 FINAL RECOMMENDATION

**Switch to Tiered Subscription Model:**

1. **Starter:** £49/month (10 quotes) - For small companies
2. **Professional:** £149/month (50 quotes) - For medium companies  
3. **Enterprise:** £399/month (200 quotes) - For large companies
4. **Unlimited:** £999/month - For very large companies

**Why This Works:**
- ✅ **27-303% revenue increase** depending on customer mix
- ✅ **Fair pricing** for all company sizes
- ✅ **Predictable revenue** (you know MRR)
- ✅ **Easy to sell** (simple tiers)
- ✅ **Scales with value** (large companies pay more)
- ✅ **Industry standard** (proven model)

**Migration:**
- Grandfather existing customers at Starter tier (£49)
- New customers get new pricing
- Upsell existing customers to higher tiers

**Expected Impact:**
- Current: £49,500 MRR (500 customers @ £99)
- New: £63,000-199,500 MRR (depending on mix)
- **Revenue increase: 27-303%**

---

## 📞 NEXT STEPS

1. **Review this plan** - Does tiered model make sense?
2. **Update Stripe** - Create 4 new price tiers
3. **Update code** - Add tier tracking and limits
4. **Update marketing** - New pricing page
5. **Email customers** - Announce new pricing (grandfather existing)

**Ready to implement? Let me know and I'll help you code the tiered pricing system!** 🚀
