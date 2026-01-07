#!/usr/bin/env python3
"""Check if test user exists"""

from app.database import SessionLocal
from app.models import User, Company

db = SessionLocal()

# Find test company
company = db.query(Company).filter(Company.slug == "test").first()

if not company:
    print("❌ Test company not found")
    db.close()
    exit(1)

print(f"✅ Found company: {company.company_name}")
print(f"   Company ID: {company.id}")
print(f"   Slug: {company.slug}")
print(f"   Email: {company.email}")
print(f"   Status: {company.subscription_status}")
print()

# Find users for this company
users = db.query(User).filter(User.company_id == company.id).all()

if not users:
    print("❌ No users found for this company!")
    print("   Creating admin user now...")

    from app.auth import hash_password
    import uuid

    user = User(
        id=uuid.uuid4(),
        company_id=company.id,
        email='admin@test.com',
        password_hash=hash_password('test123'),
        full_name='Test Admin',
        role='owner',
        is_active=True
    )
    db.add(user)
    db.commit()

    print(f"✅ Created user: admin@test.com")
    print(f"   Password: test123")
else:
    print(f"✅ Found {len(users)} user(s):")
    for user in users:
        print(f"   - Email: {user.email}")
        print(f"     Name: {user.full_name}")
        print(f"     Role: {user.role}")
        print(f"     Active: {user.is_active}")
        print()

db.close()
