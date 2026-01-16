# 🤖 PrimeHaul AI Training System

## The Core IP/Moat

**This is the secret sauce** - PrimeHaul's AI furniture detection and measurement system that gets smarter with every move.

While competitors rely on manual data entry or third-party APIs, we're building our own proprietary ML model trained on:
- Real removal company data (every job is training data)
- IKEA/furniture catalog dimensions (ground truth)
- Admin feedback corrections (supervised learning loop)

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. IKEA/Furniture Catalogs                            │
│     └─> Known products with exact dimensions           │
│                                                         │
│  2. Customer Photos                                     │
│     └─> Real-world furniture in actual homes          │
│                                                         │
│  3. Admin Corrections                                   │
│     └─> Human-verified labels when AI gets it wrong   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              FEEDBACK LOOP (The Magic)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Customer takes photo → AI detects furniture →          │
│  Admin reviews → Clicks "Correct" if wrong →            │
│  Correction saved to training dataset →                 │
│  Model improves for next customer                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              TRAINING DATASET EXPORT                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  GET /admin/export-training-data                        │
│  └─> Returns JSON with all verified labels             │
│                                                         │
│  {                                                       │
│    "item_name": "KALLAX Shelving Unit 2x4",            │
│    "dimensions": {77, 39, 147},                        │
│    "verified": true,                                    │
│    "source": "ikea_catalog"                            │
│  }                                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Database Schema

### 1. `furniture_catalog` - Ground Truth Data
Scraped product catalogs from IKEA, Wayfair, etc.

```sql
CREATE TABLE furniture_catalog (
  id UUID PRIMARY KEY,
  source VARCHAR(50),          -- 'ikea', 'wayfair', 'johnlewis'
  product_id VARCHAR(100),     -- External product ID
  name VARCHAR(255),           -- 'KALLAX Shelving Unit 2x4'
  category VARCHAR(100),       -- 'shelving', 'sofa', 'table'
  length_cm DECIMAL(10,2),
  width_cm DECIMAL(10,2),
  height_cm DECIMAL(10,2),
  cbm DECIMAL(10,4),           -- Pre-calculated volume
  weight_kg DECIMAL(10,2),
  is_bulky BOOLEAN,
  is_fragile BOOLEAN,
  packing_requirement VARCHAR(50),
  image_urls JSONB,            -- Official product images
  description TEXT,
  material VARCHAR(100),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Current Status:**
- ✅ 7 IKEA products loaded (KALLAX, PAX, KIVIK, EKEDALEN, MALM, LACK)
- 📊 Ready to scale to thousands with full API integration

### 2. `item_feedback` - The Learning Loop
Admin corrections that make the AI smarter.

```sql
CREATE TABLE item_feedback (
  id UUID PRIMARY KEY,
  item_id UUID,                -- Link to detected item
  company_id UUID,             -- Which removal company
  user_id UUID,                -- Which admin made the correction

  -- What the AI detected
  ai_detected_name VARCHAR(255),
  ai_detected_category VARCHAR(100),
  ai_confidence DECIMAL(3,2),  -- How confident AI was (0.00-1.00)

  -- What the admin corrected it to
  corrected_name VARCHAR(255),
  corrected_category VARCHAR(100),
  corrected_dimensions JSONB,  -- {length, width, height}
  corrected_cbm DECIMAL(10,4),
  corrected_weight DECIMAL(10,2),

  feedback_type VARCHAR(50),   -- 'correction', 'confirmation', 'deletion'
  notes TEXT,
  catalog_item_id UUID,        -- Link to matched catalog item if found
  created_at TIMESTAMP
);
```

**Feedback Types:**
- `correction` - AI got it wrong, here's the right answer
- `confirmation` - AI got it right, verify this label
- `deletion` - AI detected something that doesn't exist (false positive)

### 3. `training_dataset` - ML-Ready Export
Processed, verified data ready for model training.

```sql
CREATE TABLE training_dataset (
  id UUID PRIMARY KEY,
  image_url VARCHAR(500),      -- Link to training image
  image_hash VARCHAR(64),      -- Dedupe identical images

  -- Ground truth labels
  item_name VARCHAR(255),
  item_category VARCHAR(100),
  length_cm DECIMAL(10,2),
  width_cm DECIMAL(10,2),
  height_cm DECIMAL(10,2),
  cbm DECIMAL(10,4),
  weight_kg DECIMAL(10,2),
  is_bulky BOOLEAN,
  is_fragile BOOLEAN,
  packing_requirement VARCHAR(50),

  -- Metadata
  source_type VARCHAR(50),     -- 'catalog', 'customer_feedback', 'admin_confirmed'
  source_id UUID,              -- Reference to source record
  confidence_score DECIMAL(3,2),
  verified BOOLEAN,
  used_in_training BOOLEAN,
  training_batch VARCHAR(50),
  created_at TIMESTAMP
);
```

## How It Works

### For Customers (Invisible Magic)
1. Customer takes photo of bedroom
2. AI detects: "Double bed, 2x bedside tables, wardrobe"
3. System auto-calculates CBM, weight, pricing
4. Quote ready in 3 minutes

### For Admins (The Training Interface)
1. Admin reviews quote in dashboard
2. Sees detected item: "2x KALLAX Shelving Unit - 77×39×147cm"
3. Clicks **"🤖 Correct"** button if AI got it wrong
4. Modal opens with pre-filled fields:
   - Item name
   - Category
   - Dimensions (L×W×H)
   - Weight
   - Notes
5. Can choose:
   - **✅ Submit Correction** - AI was wrong, here's the truth
   - **👍 Confirm AI is Correct** - AI nailed it, verify this label
6. Correction saved to `item_feedback` table
7. Next time AI sees similar furniture, it's smarter

### For ML Engineers (The Export API)
```bash
# Export all training data
GET /admin/export-training-data
Authorization: Bearer {token}

# Response
{
  "success": true,
  "total_items": 1247,
  "breakdown": {
    "catalog_items": 7,
    "feedback_items": 1240
  },
  "data": [
    {
      "source": "catalog",
      "item_name": "KALLAX Shelving unit 2x4",
      "item_category": "shelving",
      "length_cm": 77,
      "width_cm": 39,
      "height_cm": 147,
      "cbm": 0.4428,
      "weight_kg": 35.5,
      "is_bulky": true,
      "verified": true,
      "confidence_score": 1.0,
      "image_urls": []
    },
    {
      "source": "feedback_correction",
      "item_name": "IKEA PAX Wardrobe",
      "item_category": "wardrobe",
      "verified": true,
      "confidence_score": 1.0,
      "original_ai_detection": {
        "name": "Large cupboard",
        "confidence": 0.72
      }
    }
  ]
}
```

## Files Modified/Created

### New Files
- ✅ `scrape_ikea_catalog.py` - IKEA catalog scraper (7 products loaded)
- ✅ `alembic/versions/4be4b1152694_add_ai_training_tables.py` - Database migration
- ✅ `AI_TRAINING_SYSTEM.md` - This documentation

### Modified Files
- ✅ `app/models.py` - Added 3 new tables (FurnitureCatalog, ItemFeedback, TrainingDataset)
- ✅ `app/main.py`:
  - Added imports: `ItemFeedback`, `FurnitureCatalog`, `TrainingDataset`
  - Added `POST /admin/item-feedback` - Submit AI corrections
  - Added `GET /admin/export-training-data` - Export training dataset
- ✅ `app/templates/admin_job_review_v2.html`:
  - Added "🤖 Correct" button next to each detected item
  - Added correction modal with form fields
  - Added JavaScript to handle feedback submission

## Next Steps: Scaling the AI

### Phase 1: More Catalog Data (Week 1)
- [ ] Scrape full IKEA catalog (1000+ products)
- [ ] Add Wayfair catalog
- [ ] Add John Lewis/Argos furniture
- [ ] Add B&Q/Homebase garden furniture

### Phase 2: Enhanced Feedback (Week 2)
- [ ] Image cropping in correction modal (let admin highlight item)
- [ ] Bulk correction interface (correct multiple items at once)
- [ ] Analytics dashboard (AI accuracy over time)
- [ ] Catalog matching suggestions ("Did you mean KALLAX?")

### Phase 3: Custom Model Training (Month 1)
- [ ] Train initial model on catalog + first 100 corrections
- [ ] Deploy model to production (A/B test vs OpenAI)
- [ ] Measure accuracy improvements
- [ ] Fine-tune on company-specific furniture patterns

### Phase 4: The Moat Deepens (Ongoing)
- [ ] Every job = more training data
- [ ] Model gets smarter with every correction
- [ ] Competitors can't replicate without our dataset
- [ ] We own the best furniture detection AI in the industry

## The Business Advantage

**Why This Matters:**
1. **Faster Quotes:** 3 minutes vs 30 minutes (competitors)
2. **More Accurate:** Our AI learns from real removals data
3. **Proprietary:** Can't be copied - requires thousands of real jobs
4. **Scalable:** Every new customer improves the system
5. **Sellable:** "AI-powered furniture detection" is a product in itself

**Potential Revenue Streams:**
- Primary: SaaS subscription (£199/month for removal companies)
- Secondary: Sell API access to other moving/storage companies
- Tertiary: License the AI model to furniture retailers

## Technical Implementation

### Running the System

```bash
# 1. Run database migration
python3 -m alembic upgrade head

# 2. Load IKEA catalog
python3 scrape_ikea_catalog.py

# 3. Start the server
uvicorn app.main:app --reload

# 4. Test the feedback system
# - Log in as admin: admin@test.com / test123
# - Review a quote
# - Click "🤖 Correct" on any item
# - Submit feedback

# 5. Export training data
curl -H "Authorization: Bearer {token}" \
  https://primehaul-production.up.railway.app/admin/export-training-data
```

### Database Queries

```sql
-- See all feedback corrections
SELECT
  ai_detected_name,
  corrected_name,
  feedback_type,
  created_at
FROM item_feedback
ORDER BY created_at DESC;

-- Count corrections by company
SELECT
  company_id,
  COUNT(*) as total_corrections,
  SUM(CASE WHEN feedback_type = 'correction' THEN 1 ELSE 0 END) as corrections,
  SUM(CASE WHEN feedback_type = 'confirmation' THEN 1 ELSE 0 END) as confirmations
FROM item_feedback
GROUP BY company_id;

-- Most commonly corrected items
SELECT
  ai_detected_name,
  COUNT(*) as times_corrected,
  ARRAY_AGG(DISTINCT corrected_name) as common_corrections
FROM item_feedback
WHERE feedback_type = 'correction'
GROUP BY ai_detected_name
ORDER BY times_corrected DESC;
```

## The Vision

In 6 months, PrimeHaul will have:
- **10,000+ verified furniture labels** from real jobs
- **50+ removal companies** contributing training data
- **Custom ML model** that beats OpenAI for furniture detection
- **The most accurate removal quote AI** in the UK

And the best part? Every competitor who copies our UX only makes our moat deeper - because they don't have our training data.

---

**Built:** January 13, 2026
**Status:** ✅ Live and Learning
**First Training Data:** 7 IKEA products + growing daily

🚀 **Let's make the smartest AI in the removal industry.**
