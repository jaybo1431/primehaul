#!/usr/bin/env python3
"""
DANGER: This script DELETES ALL DATA and recreates empty tables
Only use for testing/development!
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.models import Base

def reset_database():
    """Drop all tables and recreate them (DELETES ALL DATA!)"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"📍 Database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    print("")

    confirm = input("Type 'DELETE ALL DATA' to confirm: ")
    if confirm != "DELETE ALL DATA":
        print("❌ Cancelled")
        sys.exit(0)

    print("")
    print("🔗 Connecting to database...")
    engine = create_engine(database_url)

    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("📦 Creating fresh tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Database reset successfully!")
    print("🎉 All tables are now empty and ready for fresh data!")

if __name__ == "__main__":
    reset_database()
