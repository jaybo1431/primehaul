"""
Furniture variant mappings for customer size corrections.
Maps item categories to available size variants with pre-set dimensions.
Used in room_scan to let customers toggle between sizes (e.g. 3-seater → 2-seater).
Customer corrections are saved as ItemFeedback for ML training.
"""

VARIANT_MAP = {
    "sofa": {
        "match_keywords": ["sofa", "couch", "settee"],
        "variants": [
            {"name": "2-seater sofa", "length_cm": 150, "width_cm": 85, "height_cm": 85, "weight_kg": 25, "cbm": 1.08},
            {"name": "3-seater sofa", "length_cm": 200, "width_cm": 85, "height_cm": 85, "weight_kg": 35, "cbm": 1.45},
            {"name": "4-seater sofa", "length_cm": 250, "width_cm": 90, "height_cm": 85, "weight_kg": 45, "cbm": 1.91},
            {"name": "corner sofa", "length_cm": 250, "width_cm": 200, "height_cm": 85, "weight_kg": 55, "cbm": 4.25},
            {"name": "sofa bed", "length_cm": 200, "width_cm": 90, "height_cm": 85, "weight_kg": 50, "cbm": 1.53},
            {"name": "2-seater leather sofa", "length_cm": 150, "width_cm": 85, "height_cm": 85, "weight_kg": 35, "cbm": 1.08},
            {"name": "3-seater leather sofa", "length_cm": 200, "width_cm": 85, "height_cm": 85, "weight_kg": 45, "cbm": 1.45},
        ]
    },
    "armchair": {
        "match_keywords": ["armchair", "recliner", "accent chair"],
        "variants": [
            {"name": "armchair", "length_cm": 85, "width_cm": 80, "height_cm": 90, "weight_kg": 20, "cbm": 0.61},
            {"name": "recliner chair", "length_cm": 90, "width_cm": 85, "height_cm": 100, "weight_kg": 35, "cbm": 0.77},
        ]
    },
    "wardrobe": {
        "match_keywords": ["wardrobe"],
        "variants": [
            {"name": "single wardrobe", "length_cm": 60, "width_cm": 55, "height_cm": 190, "weight_kg": 45, "cbm": 0.63},
            {"name": "double wardrobe", "length_cm": 120, "width_cm": 60, "height_cm": 190, "weight_kg": 80, "cbm": 1.37},
            {"name": "triple wardrobe", "length_cm": 180, "width_cm": 60, "height_cm": 190, "weight_kg": 110, "cbm": 2.05},
        ]
    },
    "bed": {
        "match_keywords": ["bed frame", "bed", "divan"],
        "variants": [
            {"name": "single bed frame", "length_cm": 200, "width_cm": 90, "height_cm": 50, "weight_kg": 25, "cbm": 0.90},
            {"name": "double bed frame", "length_cm": 200, "width_cm": 140, "height_cm": 50, "weight_kg": 35, "cbm": 1.40},
            {"name": "king size bed frame", "length_cm": 200, "width_cm": 150, "height_cm": 50, "weight_kg": 40, "cbm": 1.50},
            {"name": "super king bed frame", "length_cm": 200, "width_cm": 180, "height_cm": 50, "weight_kg": 50, "cbm": 1.80},
        ]
    },
    "mattress": {
        "match_keywords": ["mattress"],
        "variants": [
            {"name": "single mattress", "length_cm": 190, "width_cm": 90, "height_cm": 20, "weight_kg": 15, "cbm": 0.34},
            {"name": "double mattress", "length_cm": 190, "width_cm": 135, "height_cm": 25, "weight_kg": 25, "cbm": 0.64},
            {"name": "king size mattress", "length_cm": 200, "width_cm": 150, "height_cm": 25, "weight_kg": 30, "cbm": 0.75},
            {"name": "super king mattress", "length_cm": 200, "width_cm": 180, "height_cm": 25, "weight_kg": 35, "cbm": 0.90},
        ]
    },
    "dining_table": {
        "match_keywords": ["dining table", "kitchen table"],
        "variants": [
            {"name": "2-seater dining table", "length_cm": 80, "width_cm": 80, "height_cm": 75, "weight_kg": 15, "cbm": 0.48},
            {"name": "4-seater dining table", "length_cm": 120, "width_cm": 80, "height_cm": 75, "weight_kg": 25, "cbm": 0.72},
            {"name": "6-seater dining table", "length_cm": 160, "width_cm": 90, "height_cm": 75, "weight_kg": 35, "cbm": 1.08},
            {"name": "8-seater dining table", "length_cm": 200, "width_cm": 100, "height_cm": 75, "weight_kg": 45, "cbm": 1.50},
        ]
    },
    "desk": {
        "match_keywords": ["desk", "writing desk", "office desk", "computer desk"],
        "variants": [
            {"name": "small desk", "length_cm": 100, "width_cm": 50, "height_cm": 75, "weight_kg": 15, "cbm": 0.38},
            {"name": "large desk", "length_cm": 150, "width_cm": 70, "height_cm": 75, "weight_kg": 30, "cbm": 0.79},
            {"name": "L-shaped desk", "length_cm": 160, "width_cm": 120, "height_cm": 75, "weight_kg": 40, "cbm": 1.44},
        ]
    },
    "chest_of_drawers": {
        "match_keywords": ["chest of drawers", "drawers", "dresser"],
        "variants": [
            {"name": "3-drawer chest", "length_cm": 80, "width_cm": 45, "height_cm": 70, "weight_kg": 25, "cbm": 0.25},
            {"name": "5-drawer chest", "length_cm": 80, "width_cm": 45, "height_cm": 110, "weight_kg": 35, "cbm": 0.40},
            {"name": "wide 6-drawer chest", "length_cm": 120, "width_cm": 45, "height_cm": 80, "weight_kg": 40, "cbm": 0.43},
        ]
    },
    "bookcase": {
        "match_keywords": ["bookcase", "bookshelf", "shelving unit", "shelf unit"],
        "variants": [
            {"name": "small bookcase", "length_cm": 80, "width_cm": 30, "height_cm": 100, "weight_kg": 15, "cbm": 0.24},
            {"name": "tall bookcase", "length_cm": 80, "width_cm": 30, "height_cm": 180, "weight_kg": 30, "cbm": 0.43},
            {"name": "wide bookcase", "length_cm": 120, "width_cm": 35, "height_cm": 180, "weight_kg": 40, "cbm": 0.76},
        ]
    },
    "tv": {
        "match_keywords": ["tv", "television", "flat screen"],
        "variants": [
            {"name": "32-inch TV", "length_cm": 73, "width_cm": 43, "height_cm": 8, "weight_kg": 5, "cbm": 0.03},
            {"name": "50-inch TV", "length_cm": 115, "width_cm": 70, "height_cm": 10, "weight_kg": 15, "cbm": 0.08},
            {"name": "65-inch TV", "length_cm": 146, "width_cm": 85, "height_cm": 10, "weight_kg": 25, "cbm": 0.12},
        ]
    },
    "fridge": {
        "match_keywords": ["fridge", "refrigerator", "fridge freezer"],
        "variants": [
            {"name": "under-counter fridge", "length_cm": 55, "width_cm": 55, "height_cm": 85, "weight_kg": 30, "cbm": 0.26},
            {"name": "tall fridge freezer", "length_cm": 60, "width_cm": 65, "height_cm": 180, "weight_kg": 65, "cbm": 0.70},
            {"name": "American fridge freezer", "length_cm": 90, "width_cm": 70, "height_cm": 180, "weight_kg": 110, "cbm": 1.13},
        ]
    },
    "washing_machine": {
        "match_keywords": ["washing machine", "washer dryer"],
        "variants": [
            {"name": "washing machine", "length_cm": 60, "width_cm": 60, "height_cm": 85, "weight_kg": 70, "cbm": 0.31},
            {"name": "washer dryer", "length_cm": 60, "width_cm": 60, "height_cm": 85, "weight_kg": 80, "cbm": 0.31},
        ]
    },
    "dining_chair": {
        "match_keywords": ["dining chair"],
        "variants": [
            {"name": "dining chair", "length_cm": 45, "width_cm": 45, "height_cm": 90, "weight_kg": 5, "cbm": 0.18},
            {"name": "upholstered dining chair", "length_cm": 50, "width_cm": 50, "height_cm": 95, "weight_kg": 8, "cbm": 0.24},
        ]
    },
    "sideboard": {
        "match_keywords": ["sideboard", "buffet", "credenza"],
        "variants": [
            {"name": "small sideboard", "length_cm": 100, "width_cm": 40, "height_cm": 80, "weight_kg": 25, "cbm": 0.32},
            {"name": "large sideboard", "length_cm": 160, "width_cm": 45, "height_cm": 85, "weight_kg": 40, "cbm": 0.61},
        ]
    },
    "tv_stand": {
        "match_keywords": ["tv stand", "tv unit", "media unit", "tv cabinet"],
        "variants": [
            {"name": "small TV stand", "length_cm": 100, "width_cm": 40, "height_cm": 50, "weight_kg": 15, "cbm": 0.20},
            {"name": "large TV stand", "length_cm": 160, "width_cm": 45, "height_cm": 55, "weight_kg": 25, "cbm": 0.40},
        ]
    },
}


def get_variant_category(item_name: str):
    """
    Match an AI-detected item name to a variant category.
    Returns the category key (e.g. 'sofa', 'bed') or None if no match.
    Uses longest-keyword-first matching to avoid 'bed' matching 'sofa bed'.
    """
    name_lower = item_name.lower()

    # Build a flat list of (keyword, category) sorted by keyword length descending
    # so "sofa bed" matches before "bed" or "sofa"
    matches = []
    for category, data in VARIANT_MAP.items():
        for keyword in data["match_keywords"]:
            if keyword in name_lower:
                matches.append((len(keyword), category))

    if matches:
        # Return the category with the longest keyword match
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1]
    return None


def get_variants_for_item(item_name: str):
    """
    Get available variants for an item based on its name.
    Returns list of variant dicts or None if no variants available.
    """
    category = get_variant_category(item_name)
    if category:
        return VARIANT_MAP[category]["variants"]
    return None


def get_variant_map_for_js():
    """
    Return a simplified variant map for client-side JavaScript.
    Format: { "sofa": { "keywords": [...], "variants": [...] }, ... }
    """
    js_map = {}
    for category, data in VARIANT_MAP.items():
        js_map[category] = {
            "keywords": data["match_keywords"],
            "variants": [v["name"] for v in data["variants"]]
        }
    return js_map
