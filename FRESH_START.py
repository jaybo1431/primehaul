#!/usr/bin/env python3
"""
🎯 FRESH START - Complete Database Reset & Test Data Setup
Run this to get a clean slate ready for demos and testing.
"""
import os
import sys
from sqlalchemy import create_engine
from app.models import Base, Company, PricingConfig, User
from app.auth import hash_password
import uuid
from datetime import datetime, timedelta, timezone

def fresh_start():
    """Complete reset and setup with test data"""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("💡 TIP: Load your .env file or set DATABASE_URL")
        sys.exit(1)

    print("=" * 70)
    print("🎯 FRESH START - Complete Database Reset")
    print("=" * 70)
    print("")
    print("⚠️  WARNING: This will DELETE ALL DATA and create fresh test data!")
    print(f"📍 Database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    print("")

    # Safety check
    if "railway" in database_url or "production" in database_url:
        print("🛑 PRODUCTION DATABASE DETECTED!")
        print("This script is for LOCAL TESTING ONLY.")
        confirm = input("Type 'DELETE PRODUCTION DATA' if you really want to continue: ")
        if confirm != "DELETE PRODUCTION DATA":
            print("❌ Cancelled - Smart choice!")
            sys.exit(0)
    else:
        confirm = input("Type 'RESET' to continue: ")
        if confirm != "RESET":
            print("❌ Cancelled")
            sys.exit(0)

    print("")
    print("🔗 Connecting to database...")
    engine = create_engine(database_url)

    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("📦 Creating fresh tables...")
    Base.metadata.create_all(bind=engine)

    print("")
    print("=" * 70)
    print("✅ Database Reset Complete!")
    print("=" * 70)
    print("")
    print("🎨 Creating test company and demo data...")
    print("")

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Create primary test company
        company = Company(
            id=uuid.uuid4(),
            company_name='PrimeHaul Removals',
            slug='test-removals-ltd',
            email='hello@primehaul.co.uk',
            phone='+44 20 1234 5678',
            subscription_status='active',
            is_active=True,
            primary_color='#ffffff',
            secondary_color='#000000',
            created_at=datetime.now(timezone.utc),
            trial_ends_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db.add(company)
        db.flush()

        # Create comprehensive pricing config
        pricing = PricingConfig(
            id=uuid.uuid4(),
            company_id=company.id,
            # Base pricing
            price_per_cbm=35.00,
            callout_fee=150.00,

            # Item surcharges
            bulky_item_fee=25.00,
            fragile_item_fee=15.00,

            # Distance pricing
            price_per_mile=2.50,
            free_miles=10,

            # Access difficulty multipliers
            per_floor_cost=15.00,
            no_lift_multiplier=1.25,
            narrow_access_fee=30.00,
            parking_distance_per_10m=5.00,

            # Weight limits
            weight_limit_kg=1000.0,
            price_per_extra_kg=0.50,

            # Packing materials
            pack1_price=1.05,
            pack2_price=1.55,
            pack3_price=2.00,
            pack6_price=1.05,
            robe_carton_price=10.00,
            tape_price=1.14,
            paper_price=7.50,
            mattress_cover_price=1.74
        )
        db.add(pricing)

        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            company_id=company.id,
            email='admin@test.com',
            password_hash=hash_password('test123'),
            full_name='Test Admin',
            role='owner',
            is_active=True
        )
        db.add(admin)

        # Create a regular staff user
        staff = User(
            id=uuid.uuid4(),
            company_id=company.id,
            email='staff@test.com',
            password_hash=hash_password('test123'),
            full_name='Test Staff',
            role='staff',
            is_active=True
        )
        db.add(staff)

        db.commit()

        print("✅ Test company created: PrimeHaul Removals")
        print("✅ Pricing config created with comprehensive rates")
        print("✅ Admin user created")
        print("✅ Staff user created")
        print("")
        print("=" * 70)
        print("🎉 FRESH START COMPLETE!")
        print("=" * 70)
        print("")
        print("📋 ADMIN DASHBOARD:")
        print(f"   URL: http://localhost:8000/test-removals-ltd/admin/dashboard")
        print(f"   OR:  https://primehaul-production.up.railway.app/test-removals-ltd/admin/dashboard")
        print("")
        print("🔑 LOGIN CREDENTIALS:")
        print("   Admin Email:    admin@test.com")
        print("   Staff Email:    staff@test.com")
        print("   Password:       test123")
        print("")
        print("📱 CUSTOMER QUOTE URLs (use any token):")
        print("   http://localhost:8000/s/test-removals-ltd/sammie-demo/start-v2")
        print("   http://localhost:8000/s/test-removals-ltd/client-1/start-v2")
        print("   http://localhost:8000/s/test-removals-ltd/test-123/start-v2")
        print("")
        print("   OR on Railway:")
        print("   https://primehaul-production.up.railway.app/s/test-removals-ltd/sammie-demo/start-v2")
        print("")
        print("💡 TIP: Each unique token creates a new quote/job automatically")
        print("")
        print("=" * 70)
        print("")

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fresh_start()
