#!/usr/bin/env python3
"""Add move_date column to jobs table"""

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Add move_date column
    db.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS move_date TIMESTAMP WITH TIME ZONE"))
    db.commit()
    print("✅ Added move_date column to jobs table")
except Exception as e:
    print(f"Note: {e}")
    print("(Column may already exist - this is fine)")
finally:
    db.close()
