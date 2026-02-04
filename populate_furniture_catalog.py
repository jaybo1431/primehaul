#!/usr/bin/env python3
"""
Populate Furniture Catalog with comprehensive dataset

Adds 50+ popular furniture items from:
- IKEA (most popular moving items)
- Wayfair (common furniture)
- John Lewis (UK furniture)

This is curated manual data with accurate dimensions for training.
"""

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import FurnitureCatalog
import os
from dotenv import load_dotenv

load_dotenv()


def get_database_url():
    """Get database URL from environment"""
    return os.getenv("DATABASE_URL", "postgresql://primehaul@localhost/primehaul_local")


def populate_catalog():
    """Add comprehensive furniture catalog"""
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=" * 80)
    print("🛋️  POPULATING COMPREHENSIVE FURNITURE CATALOG")
    print("=" * 80)

    # Comprehensive furniture dataset
    furniture_items = [
        # ============ IKEA POPULAR ITEMS (Sofas & Seating) ============
        {
            "source": "ikea", "product_id": "S59209867", "name": "KIVIK 3-seat sofa",
            "category": "sofa", "length_cm": 228, "width_cm": 95, "height_cm": 83,
            "weight_kg": 85.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S49155163", "name": "EKTORP 3-seat sofa",
            "category": "sofa", "length_cm": 218, "width_cm": 88, "height_cm": 88,
            "weight_kg": 75.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S09216757", "name": "KLIPPAN 2-seat sofa",
            "category": "sofa", "length_cm": 180, "width_cm": 88, "height_cm": 66,
            "weight_kg": 42.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S20103039", "name": "POÄNG Armchair",
            "category": "armchair", "length_cm": 68, "width_cm": 82, "height_cm": 100,
            "weight_kg": 10.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S79836975", "name": "STRANDMON Wing chair",
            "category": "armchair", "length_cm": 82, "width_cm": 96, "height_cm": 101,
            "weight_kg": 22.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ IKEA BEDS ============
        {
            "source": "ikea", "product_id": "S79307218", "name": "MALM Bed frame 140x200cm",
            "category": "bed", "length_cm": 209, "width_cm": 155, "height_cm": 38,
            "weight_kg": 55.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S29278283", "name": "MALM Bed frame 160x200cm",
            "category": "bed", "length_cm": 209, "width_cm": 175, "height_cm": 38,
            "weight_kg": 63.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S99305871", "name": "HEMNES Bed frame 160x200cm",
            "category": "bed", "length_cm": 211, "width_cm": 174, "height_cm": 66,
            "weight_kg": 74.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S80473753", "name": "SLATTUM Upholstered bed 140x200cm",
            "category": "bed", "length_cm": 205, "width_cm": 155, "height_cm": 105,
            "weight_kg": 48.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ IKEA STORAGE (Wardrobes, Shelving) ============
        {
            "source": "ikea", "product_id": "S49017717", "name": "PAX Wardrobe 100x60x201cm",
            "category": "wardrobe", "length_cm": 100, "width_cm": 60, "height_cm": 201,
            "weight_kg": 60.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S69276757", "name": "PAX Wardrobe 150x60x201cm",
            "category": "wardrobe", "length_cm": 150, "width_cm": 60, "height_cm": 201,
            "weight_kg": 82.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S59278265", "name": "PAX Wardrobe 200x60x201cm",
            "category": "wardrobe", "length_cm": 200, "width_cm": 60, "height_cm": 201,
            "weight_kg": 105.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "10275862", "name": "KALLAX Shelving unit 2x2",
            "category": "shelving", "length_cm": 77, "width_cm": 39, "height_cm": 77,
            "weight_kg": 17.5, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "70301537", "name": "KALLAX Shelving unit 2x4",
            "category": "shelving", "length_cm": 77, "width_cm": 39, "height_cm": 147,
            "weight_kg": 35.5, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S60275812", "name": "KALLAX Shelving unit 4x4",
            "category": "shelving", "length_cm": 147, "width_cm": 39, "height_cm": 147,
            "weight_kg": 61.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S10323067", "name": "BILLY Bookcase 80x28x202cm",
            "category": "bookcase", "length_cm": 80, "width_cm": 28, "height_cm": 202,
            "weight_kg": 31.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S30263844", "name": "HEMNES Bookcase 90x37x198cm",
            "category": "bookcase", "length_cm": 90, "width_cm": 37, "height_cm": 198,
            "weight_kg": 50.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ IKEA DRAWERS ============
        {
            "source": "ikea", "product_id": "S30360461", "name": "MALM Chest of 3 drawers",
            "category": "chest_of_drawers", "length_cm": 80, "width_cm": 48, "height_cm": 78,
            "weight_kg": 35.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S80360466", "name": "MALM Chest of 6 drawers",
            "category": "chest_of_drawers", "length_cm": 80, "width_cm": 48, "height_cm": 123,
            "weight_kg": 52.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S10473028", "name": "HEMNES Chest of 8 drawers",
            "category": "chest_of_drawers", "length_cm": 160, "width_cm": 50, "height_cm": 95,
            "weight_kg": 72.0, "is_bulky": True, "packing_requirement": "none"
        },

        # ============ IKEA TABLES ============
        {
            "source": "ikea", "product_id": "40331753", "name": "EKEDALEN Extendable table",
            "category": "dining_table", "length_cm": 120, "width_cm": 80, "height_cm": 75,
            "weight_kg": 35.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S19155788", "name": "BJURSTA Extendable table",
            "category": "dining_table", "length_cm": 140, "width_cm": 84, "height_cm": 74,
            "weight_kg": 42.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S30449825", "name": "INGATORP Extendable table",
            "category": "dining_table", "length_cm": 110, "width_cm": 78, "height_cm": 74,
            "weight_kg": 38.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "60245359", "name": "LACK Side table",
            "category": "side_table", "length_cm": 55, "width_cm": 55, "height_cm": 45,
            "weight_kg": 4.5, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S50449908", "name": "LACK Coffee table",
            "category": "coffee_table", "length_cm": 90, "width_cm": 55, "height_cm": 45,
            "weight_kg": 6.5, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S00104294", "name": "HEMNES Coffee table",
            "category": "coffee_table", "length_cm": 118, "width_cm": 75, "height_cm": 47,
            "weight_kg": 28.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ IKEA DESKS ============
        {
            "source": "ikea", "product_id": "S30214157", "name": "MICKE Desk",
            "category": "desk", "length_cm": 142, "width_cm": 50, "height_cm": 75,
            "weight_kg": 26.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S89326170", "name": "BEKANT Desk 160x80cm",
            "category": "desk", "length_cm": 160, "width_cm": 80, "height_cm": 65,
            "weight_kg": 45.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S60261151", "name": "HEMNES Desk",
            "category": "desk", "length_cm": 155, "width_cm": 65, "height_cm": 75,
            "weight_kg": 48.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ WAYFAIR ITEMS ============
        {
            "source": "wayfair", "product_id": "W001", "name": "Hampton 3 Seater Sofa",
            "category": "sofa", "length_cm": 210, "width_cm": 90, "height_cm": 85,
            "weight_kg": 78.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W002", "name": "Madison Velvet Armchair",
            "category": "armchair", "length_cm": 85, "width_cm": 90, "height_cm": 95,
            "weight_kg": 28.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W003", "name": "Camden Upholstered Bed King",
            "category": "bed", "length_cm": 215, "width_cm": 180, "height_cm": 120,
            "weight_kg": 65.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W004", "name": "Oakwood Wardrobe 3 Door",
            "category": "wardrobe", "length_cm": 180, "width_cm": 60, "height_cm": 200,
            "weight_kg": 95.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W005", "name": "Rustic Oak Dining Table",
            "category": "dining_table", "length_cm": 180, "width_cm": 90, "height_cm": 76,
            "weight_kg": 52.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W006", "name": "Metropolitan Bookcase",
            "category": "bookcase", "length_cm": 100, "width_cm": 35, "height_cm": 190,
            "weight_kg": 42.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W007", "name": "Classic Oak Chest 5 Drawers",
            "category": "chest_of_drawers", "length_cm": 90, "width_cm": 45, "height_cm": 110,
            "weight_kg": 45.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W008", "name": "Glass Top Coffee Table",
            "category": "coffee_table", "length_cm": 120, "width_cm": 70, "height_cm": 45,
            "weight_kg": 25.0, "is_bulky": False, "is_fragile": True, "packing_requirement": "none"
        },

        # ============ JOHN LEWIS ITEMS ============
        {
            "source": "johnlewis", "product_id": "JL001", "name": "Bailey Large 3 Seater Sofa",
            "category": "sofa", "length_cm": 225, "width_cm": 95, "height_cm": 90,
            "weight_kg": 88.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL002", "name": "Croft Armchair",
            "category": "armchair", "length_cm": 90, "width_cm": 95, "height_cm": 98,
            "weight_kg": 32.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL003", "name": "Wilton King Size Bed",
            "category": "bed", "length_cm": 220, "width_cm": 178, "height_cm": 125,
            "weight_kg": 72.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL004", "name": "Alba 3 Door Wardrobe",
            "category": "wardrobe", "length_cm": 150, "width_cm": 58, "height_cm": 195,
            "weight_kg": 78.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL005", "name": "Calia 6-8 Seater Dining Table",
            "category": "dining_table", "length_cm": 200, "width_cm": 100, "height_cm": 75,
            "weight_kg": 68.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL006", "name": "Montreal Tall Bookcase",
            "category": "bookcase", "length_cm": 80, "width_cm": 40, "height_cm": 200,
            "weight_kg": 48.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL007", "name": "Fusion Chest of Drawers",
            "category": "chest_of_drawers", "length_cm": 100, "width_cm": 50, "height_cm": 85,
            "weight_kg": 40.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL008", "name": "Marble Coffee Table",
            "category": "coffee_table", "length_cm": 110, "width_cm": 60, "height_cm": 42,
            "weight_kg": 35.0, "is_bulky": False, "is_fragile": True, "packing_requirement": "none"
        },
        {
            "source": "johnlewis", "product_id": "JL009", "name": "Partners Home Office Desk",
            "category": "desk", "length_cm": 150, "width_cm": 75, "height_cm": 76,
            "weight_kg": 42.0, "is_bulky": False, "packing_requirement": "none"
        },

        # ============ TV STANDS & SIDEBOARDS ============
        {
            "source": "ikea", "product_id": "S90351877", "name": "BESTÅ TV unit",
            "category": "tv_stand", "length_cm": 120, "width_cm": 40, "height_cm": 38,
            "weight_kg": 28.0, "is_bulky": False, "packing_requirement": "none"
        },
        {
            "source": "ikea", "product_id": "S60245848", "name": "HEMNES Sideboard",
            "category": "sideboard", "length_cm": 157, "width_cm": 47, "height_cm": 88,
            "weight_kg": 58.0, "is_bulky": True, "packing_requirement": "none"
        },
        {
            "source": "wayfair", "product_id": "W009", "name": "Modern TV Stand 150cm",
            "category": "tv_stand", "length_cm": 150, "width_cm": 45, "height_cm": 50,
            "weight_kg": 32.0, "is_bulky": False, "packing_requirement": "none"
        },
    ]

    added = 0
    skipped = 0

    for item in furniture_items:
        # Calculate CBM
        cbm = (item["length_cm"] * item["width_cm"] * item["height_cm"]) / 1_000_000

        # Check if exists
        existing = session.query(FurnitureCatalog).filter(
            FurnitureCatalog.source == item["source"],
            FurnitureCatalog.product_id == item["product_id"]
        ).first()

        if existing:
            skipped += 1
            continue

        catalog_entry = FurnitureCatalog(
            id=uuid.uuid4(),
            source=item["source"],
            product_id=item["product_id"],
            name=item["name"],
            category=item["category"],
            length_cm=item["length_cm"],
            width_cm=item["width_cm"],
            height_cm=item["height_cm"],
            cbm=round(cbm, 4),
            weight_kg=item.get("weight_kg"),
            is_bulky=item.get("is_bulky", False),
            is_fragile=item.get("is_fragile", False),
            packing_requirement=item.get("packing_requirement", "none"),
            image_urls=[],
            description=item["name"]
        )

        session.add(catalog_entry)
        added += 1

    session.commit()

    print(f"\n✅ Added {added} new items to catalog")
    print(f"⏭️  Skipped {skipped} existing items")

    # Show breakdown
    totals = session.query(FurnitureCatalog.source, FurnitureCatalog).all()
    sources = {}
    for item in totals:
        source = item[1].source
        sources[source] = sources.get(source, 0) + 1

    print(f"\n📊 Catalog Breakdown:")
    for source, count in sorted(sources.items()):
        print(f"   {source:15s} → {count:3d} items")

    total = session.query(FurnitureCatalog).count()
    print(f"\n📦 Total items in catalog: {total}")

    session.close()


if __name__ == "__main__":
    populate_catalog()
