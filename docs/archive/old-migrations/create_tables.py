"""
Quick script to create all database tables
This is simpler than fixing the alembic migration table order
"""

from app.database import engine
from app.models import Base

# Create all tables
print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")
