#!/usr/bin/env python3
"""
IKEA Catalog Scraper - Build the AI training dataset
Scrapes furniture data from IKEA UK using their public API
"""
import requests
import json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import FurnitureCatalog
import uuid
import os
import re
from typing import List, Dict, Optional

# IKEA API endpoints
IKEA_SEARCH_API = "https://sik.search.blue.cdtapps.com/gb/en/search-result-page"
IKEA_PRODUCT_API = "https://api.ingka.ikea.com/salesitem/full/gb/en/"

# Categories to scrape with their query parameters
IKEA_CATEGORIES = {
    "sofas": "q=:relevance:category:fu002",
    "armchairs": "q=:relevance:category:fu003",
    "beds": "q=:relevance:category:bm003",
    "wardrobes": "q=:relevance:category:st002",
    "chests-of-drawers": "q=:relevance:category:st003",
    "sideboards": "q=:relevance:category:st004",
    "tv-media-furniture": "q=:relevance:category:st001",
    "bookcases": "q=:relevance:category:st005",
    "shelving-units": "q=:relevance:category:st006",
    "dining-tables": "q=:relevance:category:fu004",
    "desks": "q=:relevance:category:ws001",
    "chairs": "q=:relevance:category:fu004",
    "coffee-tables": "q=:relevance:category:fu005",
    "console-tables": "q=:relevance:category:fu006"
}


def get_database_url():
    """Get database URL from environment or use local"""
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("DATABASE_URL", "postgresql://primehaul@localhost/primehaul_local")


def extract_dimensions(product_data: Dict) -> Optional[Dict]:
    """Extract dimensions from IKEA product data"""
    try:
        # IKEA stores dimensions in different fields
        measurements = product_data.get('measurements', {})

        # Try to find width, depth, height
        width = None
        depth = None
        height = None

        # Parse measurement strings like "Width: 77 cm"
        for measure in measurements.get('assembledSize', []):
            label = measure.get('label', '').lower()
            value_str = measure.get('value', '')

            # Extract number from string like "77 cm"
            match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            if match:
                value = float(match.group(1))

                if 'width' in label:
                    width = value
                elif 'depth' in label or 'length' in label:
                    depth = value
                elif 'height' in label:
                    height = value

        if width and depth and height:
            return {
                'width': width,
                'depth': depth,
                'height': height
            }

        return None
    except Exception as e:
        return None


def scrape_ikea_product(product_id: str) -> Optional[Dict]:
    """Fetch detailed product information from IKEA API"""
    try:
        url = f"{IKEA_PRODUCT_API}{product_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ⚠️  Failed to fetch {product_id}: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"  ❌ Error fetching product {product_id}: {e}")
        return None


def scrape_ikea_category(category: str, query: str, session, max_products: int = 50):
    """Scrape products from an IKEA category using their search API"""
    print(f"\n📦 Scraping IKEA category: {category}")

    try:
        # Use simpler approach - scrape from web search results
        # IKEA's API requires complex authentication, so we'll use web scraping

        url = f"https://www.ikea.com/gb/en/cat/{category}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"  ❌ Failed to access category page: HTTP {response.status_code}")
            return 0

        # For now, use the manual dataset as a template
        # Real scraping would parse the HTML/JSON from the page
        print(f"  ℹ️  Category page accessed. Using manual dataset for now.")
        print(f"  ℹ️  Real API integration requires IKEA API keys (todo)")

        products_added = 0

        # Placeholder - in production this would parse actual IKEA data
        example_products = []

        for product in example_products:
            # Calculate CBM
            if product.get("dimensions"):
                dims = product["dimensions"]
                length_cm = dims.get("depth", 0) or dims.get("length", 0)
                width_cm = dims.get("width", 0)
                height_cm = dims.get("height", 0)

                if length_cm and width_cm and height_cm:
                    cbm = (length_cm * width_cm * height_cm) / 1_000_000
                else:
                    cbm = None

                # Determine if bulky (any dimension > 100cm or weight > 25kg)
                is_bulky = (
                    (length_cm and length_cm > 100) or
                    (width_cm and width_cm > 100) or
                    (height_cm and height_cm > 100) or
                    (product.get("weight", 0) > 25)
                )

                # Determine fragility based on type
                fragile_types = ["glass", "mirror", "ceramic", "lamp"]
                is_fragile = any(ft in product.get("type", "").lower() for ft in fragile_types)

                # Determine packing requirement
                if is_fragile:
                    packing_req = "small_box"
                elif cbm and cbm > 0.5:
                    packing_req = "none"  # Too big for boxes, moves as-is
                elif cbm and cbm > 0.1:
                    packing_req = "large_box"
                else:
                    packing_req = "medium_box"

                # Check if already exists
                existing = session.query(FurnitureCatalog).filter(
                    FurnitureCatalog.source == "ikea",
                    FurnitureCatalog.product_id == product["id"]
                ).first()

                if not existing:
                    catalog_item = FurnitureCatalog(
                        id=uuid.uuid4(),
                        source="ikea",
                        product_id=product["id"],
                        name=product["name"],
                        category=category,
                        length_cm=length_cm,
                        width_cm=width_cm,
                        height_cm=height_cm,
                        cbm=cbm,
                        weight_kg=product.get("weight"),
                        is_bulky=is_bulky,
                        is_fragile=is_fragile,
                        packing_requirement=packing_req,
                        image_urls=product.get("images", []),
                        description=f"{product['name']} - {product.get('size', '')}",
                        material=", ".join(product.get("materials", []))
                    )
                    session.add(catalog_item)
                    products_added += 1

        session.commit()
        print(f"✅ Added {products_added} products from {category}")
        return products_added

    except Exception as e:
        print(f"❌ Error scraping {category}: {e}")
        session.rollback()
        return 0


def scrape_manual_ikea_data(session):
    """
    Add manual IKEA products with known dimensions
    This is starter data until we build the full scraper
    """
    print("\n📚 Adding manual IKEA starter dataset...")

    starter_products = [
        # KALLAX Series (very popular shelving)
        {
            "product_id": "10275862",
            "name": "KALLAX Shelving unit 2x2",
            "category": "shelving",
            "length_cm": 77, "width_cm": 39, "height_cm": 77,
            "weight_kg": 17.5, "is_bulky": False, "is_fragile": False,
            "packing_requirement": "none"
        },
        {
            "product_id": "70301537",
            "name": "KALLAX Shelving unit 2x4",
            "category": "shelving",
            "length_cm": 77, "width_cm": 39, "height_cm": 147,
            "weight_kg": 35.5, "is_bulky": True, "is_fragile": False,
            "packing_requirement": "none"
        },

        # PAX Wardrobes
        {
            "product_id": "S49017717",
            "name": "PAX Wardrobe 100x60x201 cm",
            "category": "wardrobe",
            "length_cm": 100, "width_cm": 60, "height_cm": 201,
            "weight_kg": 60.0, "is_bulky": True, "is_fragile": False,
            "packing_requirement": "none"
        },

        # KIVIK Sofas
        {
            "product_id": "S59209867",
            "name": "KIVIK 3-seat sofa",
            "category": "sofa",
            "length_cm": 228, "width_cm": 95, "height_cm": 83,
            "weight_kg": 85.0, "is_bulky": True, "is_fragile": False,
            "packing_requirement": "none"
        },

        # Dining Tables
        {
            "product_id": "40331753",
            "name": "EKEDALEN Extendable table",
            "category": "table",
            "length_cm": 120, "width_cm": 80, "height_cm": 75,
            "weight_kg": 35.0, "is_bulky": True, "is_fragile": False,
            "packing_requirement": "none"
        },

        # Beds
        {
            "product_id": "S79307218",
            "name": "MALM Bed frame 140x200 cm",
            "category": "bed",
            "length_cm": 209, "width_cm": 155, "height_cm": 38,
            "weight_kg": 55.0, "is_bulky": True, "is_fragile": False,
            "packing_requirement": "none"
        },

        # Small items
        {
            "product_id": "60245359",
            "name": "LACK Side table",
            "category": "table",
            "length_cm": 55, "width_cm": 55, "height_cm": 45,
            "weight_kg": 4.5, "is_bulky": False, "is_fragile": False,
            "packing_requirement": "none"
        }
    ]

    added = 0
    for product in starter_products:
        # Calculate CBM
        cbm = (product["length_cm"] * product["width_cm"] * product["height_cm"]) / 1_000_000

        # Check if exists
        existing = session.query(FurnitureCatalog).filter(
            FurnitureCatalog.source == "ikea",
            FurnitureCatalog.product_id == product["product_id"]
        ).first()

        if not existing:
            catalog_item = FurnitureCatalog(
                id=uuid.uuid4(),
                source="ikea",
                product_id=product["product_id"],
                name=product["name"],
                category=product["category"],
                length_cm=product["length_cm"],
                width_cm=product["width_cm"],
                height_cm=product["height_cm"],
                cbm=round(cbm, 4),
                weight_kg=product["weight_kg"],
                is_bulky=product["is_bulky"],
                is_fragile=product["is_fragile"],
                packing_requirement=product["packing_requirement"],
                image_urls=[],
                description=product["name"]
            )
            session.add(catalog_item)
            added += 1

    session.commit()
    print(f"✅ Added {added} starter IKEA products")
    return added


def main():
    """Main scraper function"""
    print("=" * 70)
    print("🛋️  IKEA CATALOG SCRAPER - Building AI Training Dataset")
    print("=" * 70)

    # Connect to database
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Start with manual data
        total_added = scrape_manual_ikea_data(session)

        # TODO: Implement full API scraping
        # for category in IKEA_CATEGORIES:
        #     added = scrape_ikea_category(category, session)
        #     total_added += added
        #     time.sleep(1)  # Be nice to their servers

        print("\n" + "=" * 70)
        print(f"✅ SCRAPING COMPLETE!")
        print(f"📊 Total products added: {total_added}")
        print("=" * 70)

        # Show stats
        total_count = session.query(FurnitureCatalog).filter(
            FurnitureCatalog.source == "ikea"
        ).count()
        print(f"📦 Total IKEA products in catalog: {total_count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
