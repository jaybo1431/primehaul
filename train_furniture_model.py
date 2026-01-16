#!/usr/bin/env python3
"""
PrimeHaul Custom Furniture Detection Model Training Pipeline

This script trains a custom ML model on our proprietary dataset:
- IKEA/furniture catalog data (ground truth)
- Admin feedback corrections (supervised learning)
- Customer photos with verified labels

The goal: Beat OpenAI at furniture detection using our own data.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from dotenv import load_dotenv

# ML imports
try:
    import torch
    import torch.nn as nn
    from transformers import AutoImageProcessor, AutoModelForImageClassification, TrainingArguments, Trainer
    from datasets import Dataset, Image
    from PIL import Image as PILImage
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not installed. Run: pip install torch transformers datasets pillow")
    ML_AVAILABLE = False


load_dotenv()

# Configuration
API_BASE_URL = os.getenv("APP_URL", "http://localhost:8000")
AUTH_TOKEN = None  # Will be set via login
MODEL_OUTPUT_DIR = "./models/furniture-detector-v1"
DATA_CACHE_DIR = "./training_data_cache"


class FurnitureModelTrainer:
    """Train custom furniture detection model"""

    def __init__(self):
        self.training_data = []
        self.model = None
        self.processor = None

    def login(self, email: str, password: str) -> bool:
        """Authenticate to get access token"""
        global AUTH_TOKEN

        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                data={"username": email, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                AUTH_TOKEN = data.get("access_token")
                print(f"✅ Logged in as {email}")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def fetch_training_data_from_db(self) -> Dict:
        """Fetch ALL training dataset from database - maximize data!"""
        print("\n📊 Fetching training data from ALL sources...")

        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from app.models import FurnitureCatalog, ItemFeedback, Item, Room, TrainingDataset
            from dotenv import load_dotenv

            load_dotenv()

            database_url = os.getenv("DATABASE_URL", "postgresql://primehaul@localhost/primehaul_local")
            engine = create_engine(database_url)
            Session = sessionmaker(bind=engine)
            session = Session()

            training_data = []
            sources_count = {}

            # 1. Export catalog data (verified furniture specs)
            catalog_items = session.query(FurnitureCatalog).all()
            for item in catalog_items:
                training_data.append({
                    "source": "catalog",
                    "source_type": item.source,
                    "product_id": item.product_id,
                    "item_name": item.name,
                    "item_category": item.category,
                    "length_cm": float(item.length_cm) if item.length_cm else None,
                    "width_cm": float(item.width_cm) if item.width_cm else None,
                    "height_cm": float(item.height_cm) if item.height_cm else None,
                    "cbm": float(item.cbm) if item.cbm else None,
                    "weight_kg": float(item.weight_kg) if item.weight_kg else None,
                    "is_bulky": item.is_bulky,
                    "is_fragile": item.is_fragile,
                    "packing_requirement": item.packing_requirement,
                    "image_urls": item.image_urls or [],
                    "verified": True,
                    "confidence_score": 1.0
                })
            sources_count['catalog'] = len(catalog_items)

            # 2. Export from training_dataset table (OpenAI extractions + synthetic)
            training_dataset_items = session.query(TrainingDataset).all()
            for item in training_dataset_items:
                if item.item_category:  # Only if we have a category
                    training_data.append({
                        "source": item.source_type or "training_dataset",
                        "item_name": item.item_name,
                        "item_category": item.item_category,
                        "length_cm": float(item.length_cm) if item.length_cm else None,
                        "width_cm": float(item.width_cm) if item.width_cm else None,
                        "height_cm": float(item.height_cm) if item.height_cm else None,
                        "cbm": float(item.cbm) if item.cbm else None,
                        "weight_kg": float(item.weight_kg) if item.weight_kg else None,
                        "is_bulky": item.is_bulky,
                        "is_fragile": item.is_fragile,
                        "verified": item.verified,
                        "confidence_score": float(item.confidence_score) if item.confidence_score else 0.8
                    })

                    source_key = item.source_type or "training_dataset"
                    sources_count[source_key] = sources_count.get(source_key, 0) + 1

            # 3. Export admin feedback (highest quality!)
            feedbacks = session.query(ItemFeedback).filter(
                ItemFeedback.feedback_type.in_(['correction', 'confirmation'])
            ).all()

            for feedback in feedbacks:
                item = session.query(Item).filter(Item.id == feedback.item_id).first()
                if not item:
                    continue

                if feedback.feedback_type == 'correction':
                    training_data.append({
                        "source": "admin_correction",
                        "item_name": feedback.corrected_name or feedback.ai_detected_name,
                        "item_category": feedback.corrected_category or feedback.ai_detected_category,
                        "length_cm": feedback.corrected_dimensions.get('length') if feedback.corrected_dimensions else float(item.length_cm),
                        "width_cm": feedback.corrected_dimensions.get('width') if feedback.corrected_dimensions else float(item.width_cm),
                        "height_cm": feedback.corrected_dimensions.get('height') if feedback.corrected_dimensions else float(item.height_cm),
                        "cbm": float(feedback.corrected_cbm) if feedback.corrected_cbm else float(item.cbm),
                        "weight_kg": float(feedback.corrected_weight) if feedback.corrected_weight else float(item.weight_kg),
                        "verified": True,
                        "confidence_score": 1.0  # Admin corrections are gold!
                    })
                elif feedback.feedback_type == 'confirmation':
                    training_data.append({
                        "source": "admin_confirmation",
                        "item_name": feedback.ai_detected_name,
                        "item_category": feedback.ai_detected_category,
                        "verified": True,
                        "confidence_score": 1.0
                    })

            sources_count['admin_feedback'] = len(feedbacks)

            session.close()

            data = {
                "total_items": len(training_data),
                "breakdown": sources_count,
                "data": training_data
            }

            print(f"✅ Fetched {data['total_items']} training samples from multiple sources:")
            for source, count in sorted(sources_count.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {source:25s} → {count:4d} items")

            self.training_data = training_data

            # Cache to disk
            cache_file = Path(DATA_CACHE_DIR) / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cache_file.parent.mkdir(exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Cached to {cache_file}")

            return data

        except Exception as e:
            print(f"❌ Error fetching training data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def prepare_dataset(self):
        """Convert training data to ML-ready format"""
        print("\n🔧 Preparing dataset...")

        # Build category index
        categories = list(set([item['item_category'] for item in self.training_data if item.get('item_category')]))
        categories.sort()
        category_to_id = {cat: idx for idx, cat in enumerate(categories)}

        print(f"   Found {len(categories)} categories: {', '.join(categories[:5])}...")

        # Convert to dataset format
        dataset_items = []

        for item in self.training_data:
            if not item.get('item_category'):
                continue

            dataset_items.append({
                'category': item['item_category'],
                'category_id': category_to_id[item['item_category']],
                'name': item['item_name'],
                'dimensions': {
                    'length': item.get('length_cm', 0),
                    'width': item.get('width_cm', 0),
                    'height': item.get('height_cm', 0)
                },
                'cbm': item.get('cbm', 0),
                'weight_kg': item.get('weight_kg', 0),
                'is_bulky': item.get('is_bulky', False),
                'is_fragile': item.get('is_fragile', False),
                'verified': item.get('verified', False)
            })

        print(f"✅ Prepared {len(dataset_items)} training examples")

        return dataset_items, categories, category_to_id

    def train_simple_classifier(self):
        """Train a simple furniture category classifier (rule-based baseline)"""
        print("\n🤖 Training furniture category classifier...")
        print("   Using rule-based approach (no deep learning required)")

        dataset_items, categories, category_to_id = self.prepare_dataset()

        # For now, we'll train a simple rule-based classifier on dimensions
        # In production, this would use images + transformers

        print("\n📊 Training Statistics:")
        print(f"   Total samples: {len(dataset_items)}")
        print(f"   Categories: {len(categories)}")
        print(f"   Verified samples: {sum(1 for item in dataset_items if item['verified'])}")

        # Build dimension-based rules
        category_stats = {}
        for item in dataset_items:
            cat = item['category']
            if cat not in category_stats:
                category_stats[cat] = {
                    'cbm_samples': [],
                    'weight_samples': [],
                    'count': 0
                }

            category_stats[cat]['cbm_samples'].append(item['cbm'])
            category_stats[cat]['weight_samples'].append(item['weight_kg'])
            category_stats[cat]['count'] += 1

        # Calculate averages for each category
        category_profiles = {}
        for cat, stats in category_stats.items():
            category_profiles[cat] = {
                'avg_cbm': np.mean(stats['cbm_samples']) if stats['cbm_samples'] else 0,
                'avg_weight': np.mean(stats['weight_samples']) if stats['weight_samples'] else 0,
                'count': stats['count']
            }

        print("\n📈 Category Profiles:")
        for cat, profile in sorted(category_profiles.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"   {cat:20s} → {profile['count']:3d} samples | Avg CBM: {profile['avg_cbm']:.2f} | Avg Weight: {profile['avg_weight']:.1f}kg")

        # Save model
        model_data = {
            'categories': categories,
            'category_to_id': category_to_id,
            'category_profiles': category_profiles,
            'total_samples': len(dataset_items),
            'trained_at': datetime.now().isoformat(),
            'version': '1.0-baseline'
        }

        output_path = Path(MODEL_OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)

        model_file = output_path / 'furniture_model_v1.json'
        with open(model_file, 'w') as f:
            json.dump(model_data, f, indent=2)

        print(f"\n✅ Model saved to {model_file}")
        print(f"   Version: {model_data['version']}")
        print(f"   Categories: {len(categories)}")

        return model_data

    def predict(self, item_name: str, dimensions: Dict) -> Dict:
        """Predict furniture category based on name and dimensions"""
        # Load model
        model_file = Path(MODEL_OUTPUT_DIR) / 'furniture_model_v1.json'

        if not model_file.exists():
            return {"error": "Model not trained yet. Run train() first."}

        with open(model_file) as f:
            model = json.load(f)

        # Calculate CBM
        length = dimensions.get('length', 0)
        width = dimensions.get('width', 0)
        height = dimensions.get('height', 0)
        cbm = (length * width * height) / 1_000_000 if all([length, width, height]) else 0

        # Find closest category by CBM
        best_category = None
        min_diff = float('inf')

        for cat, profile in model['category_profiles'].items():
            diff = abs(profile['avg_cbm'] - cbm)
            if diff < min_diff:
                min_diff = diff
                best_category = cat

        confidence = max(0.5, 1.0 - (min_diff / cbm)) if cbm > 0 else 0.5

        return {
            'predicted_category': best_category,
            'confidence': confidence,
            'cbm': cbm,
            'model_version': model['version']
        }


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("🤖 PRIMEHAUL CUSTOM FURNITURE DETECTION MODEL")
    print("=" * 70)

    trainer = FurnitureModelTrainer()

    # Fetch training data directly from database (no API needed)
    data = trainer.fetch_training_data_from_db()

    if not data or data['total_items'] == 0:
        print("❌ No training data available. Add catalog items and feedback first.")
        print("Run: python3 populate_furniture_catalog.py")
        return

    # Train model
    model = trainer.train_simple_classifier()

    # Test prediction
    if model:
        print("\n" + "=" * 70)
        print("🧪 TESTING MODEL")
        print("=" * 70)

        test_item = {
            'name': 'KALLAX Shelving Unit',
            'dimensions': {'length': 77, 'width': 39, 'height': 147}
        }

        prediction = trainer.predict(test_item['name'], test_item['dimensions'])

        if 'error' in prediction:
            print(f"\n❌ Prediction error: {prediction['error']}")
        else:
            print(f"\nTest Item: {test_item['name']}")
            print(f"Dimensions: {test_item['dimensions']}")
            print(f"Predicted Category: {prediction['predicted_category']}")
            print(f"Confidence: {prediction['confidence']:.2%}")

    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\nModel saved to: {MODEL_OUTPUT_DIR}")
    print(f"Total training samples: {data['total_items']}")
    print("\nNext steps:")
    print("1. Collect more feedback to improve accuracy")
    print("2. Add image recognition (requires customer photos)")
    print("3. A/B test against OpenAI API")


if __name__ == "__main__":
    main()
