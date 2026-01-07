#!/usr/bin/env python3
"""Reset test data - clears all jobs while keeping company and user"""

from app.database import SessionLocal
from app.models import Job, Room, Item, Photo, AdminNote, UsageAnalytics
from sqlalchemy import text

db = SessionLocal()

try:
    # Get count before deletion
    job_count = db.query(Job).count()
    room_count = db.query(Room).count()
    item_count = db.query(Item).count()
    photo_count = db.query(Photo).count()

    print("🗑️  Clearing test data...")
    print(f"   - Jobs: {job_count}")
    print(f"   - Rooms: {room_count}")
    print(f"   - Items: {item_count}")
    print(f"   - Photos: {photo_count}")
    print()

    # Delete all jobs (cascades to rooms, items, photos, notes)
    db.query(Job).delete()

    # Delete usage analytics
    db.query(UsageAnalytics).delete()

    # Commit changes
    db.commit()

    print("✅ Database reset complete!")
    print()
    print("═══════════════════════════════════════════════════════")
    print("READY TO TEST!")
    print("═══════════════════════════════════════════════════════")
    print()
    print("Customer Survey:")
    print("  http://localhost:8000/s/test/testjob123")
    print()
    print("Admin Dashboard:")
    print("  http://localhost:8000/test/admin/dashboard")
    print()
    print("═══════════════════════════════════════════════════════")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
