#!/usr/bin/env python3
"""Create default pricing config for test company"""

from app.database import SessionLocal
from app.models import Company, PricingConfig

db = SessionLocal()

# Find test company
company = db.query(Company).filter(Company.slug == "test").first()

if not company:
    print("❌ Test company not found")
    db.close()
    exit(1)

# Check if pricing config already exists
existing = db.query(PricingConfig).filter(PricingConfig.company_id == company.id).first()

if existing:
    print(f"✅ Pricing config already exists for company '{company.company_name}'")
    print(f"   - Price per CBM: £{existing.price_per_cbm}")
    print(f"   - Callout fee: £{existing.callout_fee}")
    db.close()
    exit(0)

# Create default pricing config
pricing = PricingConfig(
    company_id=company.id,
    price_per_cbm=35.00,  # £35 per cubic meter
    callout_fee=250.00,   # £250 base callout fee
    bulky_item_fee=25.00, # £25 per bulky item
    fragile_item_fee=15.00, # £15 per fragile item
    weight_threshold_kg=1000,  # 1000kg threshold
    price_per_kg_over_threshold=0.50  # £0.50 per kg over threshold
)

db.add(pricing)
db.commit()

print(f"✅ Created default pricing config for company '{company.company_name}'")
print(f"   - Price per CBM: £{pricing.price_per_cbm}")
print(f"   - Callout fee: £{pricing.callout_fee}")
print(f"   - Bulky item fee: £{pricing.bulky_item_fee}")
print(f"   - Fragile item fee: £{pricing.fragile_item_fee}")

db.close()
