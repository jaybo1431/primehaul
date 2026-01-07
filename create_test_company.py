"""
Create a test company for testing the platform
"""

from app.database import get_db
from app.models import Company, PricingConfig, User
from app.auth import hash_password
import uuid

db = next(get_db())

# Create test company
company = Company(
    id=uuid.uuid4(),
    company_name='Test Removals',
    slug='test',
    email='test@primehaul.co.uk',
    subscription_status='active',
    is_active=True,
    primary_color='#2ee59d',
    secondary_color='#000000'
)
db.add(company)
db.commit()
db.refresh(company)

# Create pricing config
pricing = PricingConfig(
    id=uuid.uuid4(),
    company_id=company.id,
    price_per_cbm=35.00,
    callout_fee=250.00,
    bulky_item_fee=25.00,
    fragile_item_fee=15.00
)
db.add(pricing)

# Create admin user
user = User(
    id=uuid.uuid4(),
    company_id=company.id,
    email='admin@test.com',
    password_hash=hash_password('test123'),
    full_name='Test User',
    role='owner',
    is_active=True
)
db.add(user)
db.commit()

print('✅ Test company created!')
print('')
print('=' * 60)
print('CUSTOMER SURVEY (AI-Powered):')
print('  URL: http://localhost:8000/s/test/testjob123')
print('  Try this on your phone and desktop!')
print('')
print('ADMIN DASHBOARD:')
print('  URL: http://localhost:8000/test/admin/dashboard')
print('  Login: admin@test.com')
print('  Password: test123')
print('')
print('MARKETPLACE:')
print('  URL: http://localhost:8000/marketplace')
print('=' * 60)
print('')
print('🚀 Ready to test! Start the server with:')
print('   uvicorn app.main:app --reload')
