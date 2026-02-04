"""
SQLAlchemy database models for PrimeHaul OS
Multi-tenant B2B SaaS platform for moving quote management
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, DECIMAL, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Company(Base):
    """
    Companies table - Each moving company using the platform
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Basic Info
    company_name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)  # e.g., 'acme-removals'
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))

    # Subscription
    subscription_status = Column(String(50), nullable=False, default='trial', index=True)  # trial, active, past_due, canceled
    stripe_customer_id = Column(String(255), unique=True, index=True)
    stripe_subscription_id = Column(String(255))
    trial_ends_at = Column(DateTime(timezone=True))
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_canceled_at = Column(DateTime(timezone=True))

    # Branding
    logo_url = Column(Text)
    primary_color = Column(String(7), default='#2ee59d')  # Hex color
    secondary_color = Column(String(7), default='#000000')

    # Terms & Conditions
    tcs_document_url = Column(Text)  # Path to current T&Cs PDF
    tcs_version = Column(String(20), default='1.0')  # Current version number
    tcs_updated_at = Column(DateTime(timezone=True))  # When last updated
    tcs_document_hash = Column(String(64))  # SHA-256 hash of current document
    tcs_enabled = Column(Boolean, default=False)  # Whether T&Cs required for this company

    # Status
    is_active = Column(Boolean, default=True)
    onboarding_completed = Column(Boolean, default=False)

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    pricing_config = relationship("PricingConfig", back_populates="company", uselist=False, cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    usage_analytics = relationship("UsageAnalytics", back_populates="company", cascade="all, delete-orphan")
    stripe_events = relationship("StripeEvent", back_populates="company", cascade="all, delete-orphan")


class User(Base):
    """
    Users table - Admin users per company
    """
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_company_email', 'company_id', 'email', unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Identity
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Role
    role = Column(String(50), nullable=False, default='member')  # owner, admin, member

    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    company = relationship("Company", back_populates="users")
    admin_notes = relationship("AdminNote", back_populates="user", cascade="all, delete-orphan")


class PricingConfig(Base):
    """
    Pricing configurations table - Per-company pricing rules
    """
    __tablename__ = "pricing_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Volume Pricing
    price_per_cbm = Column(DECIMAL(10, 2), nullable=False, default=35.00)  # £35/CBM

    # Base Fees
    callout_fee = Column(DECIMAL(10, 2), nullable=False, default=250.00)

    # Item Surcharges
    bulky_item_fee = Column(DECIMAL(10, 2), nullable=False, default=25.00)
    bulky_weight_threshold_kg = Column(Integer, default=50)  # Items over this weight are "bulky"
    fragile_item_fee = Column(DECIMAL(10, 2), nullable=False, default=15.00)

    # Weight Pricing (over threshold)
    weight_threshold_kg = Column(Integer, default=1000)  # 1 tonne
    price_per_kg_over_threshold = Column(DECIMAL(10, 2), default=0.50)

    # Distance Pricing (future)
    base_distance_km = Column(Integer, default=0)
    price_per_km = Column(DECIMAL(10, 2), default=2.00)

    # Estimate Range Multipliers
    estimate_low_multiplier = Column(DECIMAL(3, 2), default=0.90)  # -10%
    estimate_high_multiplier = Column(DECIMAL(3, 2), default=1.20)  # +20%

    # Access Difficulty Pricing
    # Floors & Lift
    price_per_floor = Column(DECIMAL(10, 2), nullable=False, default=15.00)  # £15 per floor
    no_lift_surcharge = Column(DECIMAL(10, 2), nullable=False, default=50.00)  # £50 if stairs + no lift

    # Parking
    parking_street_fee = Column(DECIMAL(10, 2), nullable=False, default=25.00)  # Street parking
    parking_permit_fee = Column(DECIMAL(10, 2), nullable=False, default=40.00)  # Permit zone
    parking_limited_fee = Column(DECIMAL(10, 2), nullable=False, default=60.00)  # Very limited/difficult
    parking_distance_per_50m = Column(DECIMAL(10, 2), nullable=False, default=10.00)  # £10 per 50m carry

    # Building Restrictions
    narrow_access_fee = Column(DECIMAL(10, 2), nullable=False, default=35.00)  # Narrow stairs/doors
    time_restriction_fee = Column(DECIMAL(10, 2), nullable=False, default=25.00)  # Specific time windows
    booking_required_fee = Column(DECIMAL(10, 2), nullable=False, default=20.00)  # Need building approval

    # Outdoor Access
    outdoor_steps_per_5 = Column(DECIMAL(10, 2), nullable=False, default=15.00)  # £15 per 5 outdoor steps
    outdoor_path_fee = Column(DECIMAL(10, 2), nullable=False, default=20.00)  # Garden/path access

    # Packing Materials Pricing
    pack1_price = Column(DECIMAL(10, 2), nullable=False, default=1.05)  # 18×18×10" small box
    pack2_price = Column(DECIMAL(10, 2), nullable=False, default=1.55)  # 18×18×20" medium box
    pack3_price = Column(DECIMAL(10, 2), nullable=False, default=2.00)  # 18×18×30" large box
    pack6_price = Column(DECIMAL(10, 2), nullable=False, default=1.05)  # 18×13×13" extra small
    robe_carton_price = Column(DECIMAL(10, 2), nullable=False, default=10.00)  # Wardrobe box
    tape_price = Column(DECIMAL(10, 2), nullable=False, default=1.14)  # £1.14 per 10 boxes
    paper_price = Column(DECIMAL(10, 2), nullable=False, default=7.50)  # £7.50 per 1.5 packs per 10 CBM
    mattress_cover_price = Column(DECIMAL(10, 2), nullable=False, default=1.74)  # King size mattress cover

    # Packing Service Labor Pricing
    packing_labor_per_hour = Column(DECIMAL(10, 2), nullable=False, default=40.00)  # £40/hour for packing service

    # Relationships
    company = relationship("Company", back_populates="pricing_config")


class FurnitureCatalog(Base):
    """
    Furniture catalog from IKEA, Wayfair, etc. for AI training
    """
    __tablename__ = "furniture_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)  # 'ikea', 'wayfair', 'johnlewis'
    product_id = Column(String(100))  # External product ID
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # 'sofa', 'table', 'wardrobe', etc.

    # Dimensions
    length_cm = Column(DECIMAL(10, 2))
    width_cm = Column(DECIMAL(10, 2))
    height_cm = Column(DECIMAL(10, 2))
    cbm = Column(DECIMAL(10, 4))
    weight_kg = Column(DECIMAL(10, 2))

    # Classification
    is_bulky = Column(Boolean, default=False)
    is_fragile = Column(Boolean, default=False)
    packing_requirement = Column(String(50))  # 'none', 'small_box', 'large_box', etc.

    # Images
    image_urls = Column(JSONB)  # List of image URLs

    # Metadata
    description = Column(Text)
    material = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ItemFeedback(Base):
    """
    Admin corrections for AI training - the feedback loop
    """
    __tablename__ = "item_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))

    # Original AI detection
    ai_detected_name = Column(String(255))
    ai_detected_category = Column(String(100))
    ai_confidence = Column(DECIMAL(3, 2))  # 0.00 to 1.00

    # Admin correction
    corrected_name = Column(String(255))
    corrected_category = Column(String(100))
    corrected_dimensions = Column(JSONB)  # {length, width, height}
    corrected_cbm = Column(DECIMAL(10, 4))
    corrected_weight = Column(DECIMAL(10, 2))

    # Feedback type
    feedback_type = Column(String(50))  # 'correction', 'confirmation', 'deletion', 'false_positive'
    notes = Column(Text)

    # Link to catalog if matched
    catalog_item_id = Column(UUID(as_uuid=True), ForeignKey('furniture_catalog.id', ondelete='SET NULL'))

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    item = relationship("Item")
    company = relationship("Company")
    user = relationship("User")
    catalog_item = relationship("FurnitureCatalog")


class TrainingDataset(Base):
    """
    Processed training data ready for ML model
    """
    __tablename__ = "training_dataset"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Image data
    image_url = Column(String(500))
    image_hash = Column(String(64))  # For deduplication

    # Ground truth labels
    item_name = Column(String(255), nullable=False)
    item_category = Column(String(100), nullable=False)
    length_cm = Column(DECIMAL(10, 2))
    width_cm = Column(DECIMAL(10, 2))
    height_cm = Column(DECIMAL(10, 2))
    cbm = Column(DECIMAL(10, 4))
    weight_kg = Column(DECIMAL(10, 2))
    is_bulky = Column(Boolean)
    is_fragile = Column(Boolean)
    packing_requirement = Column(String(50))

    # Source
    source_type = Column(String(50))  # 'catalog', 'customer_feedback', 'admin_confirmed'
    source_id = Column(UUID(as_uuid=True))  # Reference to catalog or feedback record

    # Quality
    confidence_score = Column(DECIMAL(3, 2))  # How confident we are in this label
    verified = Column(Boolean, default=False)

    # ML metadata
    used_in_training = Column(Boolean, default=False)
    training_batch = Column(String(50))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Job(Base):
    """
    Jobs table - Customer removal quotes
    """
    __tablename__ = "jobs"
    __table_args__ = (
        Index('idx_jobs_company_status', 'company_id', 'status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(50), nullable=False, unique=True, index=True)  # Customer-facing survey token
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Location Data (JSONB for flexibility)
    pickup = Column(JSONB)  # {"label": "...", "lat": ..., "lng": ...}
    dropoff = Column(JSONB)

    # Property Info
    property_type = Column(String(100))
    move_date = Column(DateTime(timezone=True))  # Preferred move date

    # Access Parameters (JSONB for flexibility)
    pickup_access = Column(JSONB)  # Pickup location access difficulty
    dropoff_access = Column(JSONB)  # Dropoff location access difficulty

    # Customer Contact
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))

    # Packing Preferences
    customer_provides_packing = Column(Boolean, default=False)  # True if customer brings own materials
    packing_service_rooms = Column(JSONB)  # List of room IDs customer wants packed: ["room-id-1", "room-id-2"]

    # Status & Timestamps
    status = Column(String(50), nullable=False, default='in_progress', index=True)  # in_progress, awaiting_approval, approved, rejected
    submitted_at = Column(DateTime(timezone=True), index=True)
    approved_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)

    # Calculations
    total_cbm = Column(DECIMAL(10, 2), default=0)
    total_weight_kg = Column(DECIMAL(10, 2), default=0)

    # Custom Pricing (overrides)
    custom_price_low = Column(Integer)
    custom_price_high = Column(Integer)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    rooms = relationship("Room", back_populates="job", cascade="all, delete-orphan")
    admin_notes = relationship("AdminNote", back_populates="job", cascade="all, delete-orphan")
    terms_acceptance = relationship("TermsAcceptance", back_populates="job", uselist=False, cascade="all, delete-orphan")


class Room(Base):
    """
    Rooms table - Rooms within a job
    """
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Room Info
    name = Column(String(100), nullable=False)
    summary = Column(Text)

    # Relationships
    job = relationship("Job", back_populates="rooms")
    items = relationship("Item", back_populates="room", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="room", cascade="all, delete-orphan")


class Item(Base):
    """
    Items table - Inventory items within a room
    """
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Item Details
    name = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    notes = Column(Text)

    # Physical Properties
    length_cm = Column(DECIMAL(10, 2))
    width_cm = Column(DECIMAL(10, 2))
    height_cm = Column(DECIMAL(10, 2))
    weight_kg = Column(DECIMAL(10, 2))
    cbm = Column(DECIMAL(10, 4))

    # Attributes
    bulky = Column(Boolean, default=False)
    fragile = Column(Boolean, default=False)

    # Packing classification
    item_category = Column(String(50))  # furniture, loose_items, wardrobe, mattress, already_boxed
    packing_requirement = Column(String(50))  # none, small_box, medium_box, large_box, robe_carton, mattress_cover

    # Relationships
    room = relationship("Room", back_populates="items")


class Photo(Base):
    """
    Photos table - Customer-uploaded photos
    """
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # File Info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))

    # Storage (company-specific paths)
    storage_path = Column(Text, nullable=False)  # e.g., "uploads/{company_id}/{job_token}/{filename}"

    # Relationships
    room = relationship("Room", back_populates="photos")

    @property
    def url(self):
        """Return the URL to access this photo"""
        return f"/static/{self.storage_path}"


class AdminNote(Base):
    """
    Admin notes table - Internal notes on jobs
    """
    __tablename__ = "admin_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Note Content
    note = Column(Text, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="admin_notes")
    user = relationship("User", back_populates="admin_notes")


class UsageAnalytics(Base):
    """
    Usage analytics table - Track events for analytics dashboard
    """
    __tablename__ = "usage_analytics"
    __table_args__ = (
        Index('idx_analytics_company_date', 'company_id', 'recorded_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Event Type
    event_type = Column(String(100), nullable=False, index=True)  # quote_generated, photo_analyzed, job_submitted, job_approved

    # Event metadata (flexible JSONB) - renamed from 'metadata' to avoid SQLAlchemy reserved name
    event_metadata = Column(JSONB)  # {job_id, photos_count, ai_cost_usd, etc.}

    # AI Costs (track per event)
    ai_cost_usd = Column(DECIMAL(10, 4), default=0)

    # Relationships
    company = relationship("Company", back_populates="usage_analytics")


class StripeEvent(Base):
    """
    Stripe events table - Log all webhook events for audit trail
    """
    __tablename__ = "stripe_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='SET NULL'), index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Stripe Event
    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # customer.subscription.created, invoice.paid, etc.
    payload = Column(JSONB, nullable=False)  # Full webhook payload

    # Processing Status
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    # Relationships
    company = relationship("Company", back_populates="stripe_events")


class UserInteraction(Base):
    """
    Track ALL user interactions for ML training and UX optimization
    Captures behavioral data: clicks, scrolls, page views, form inputs, etc.

    ML Use Cases:
    - Predict customer drop-off points
    - Optimize UI/UX based on behavioral patterns
    - Lead scoring (time on site, engagement level)
    - A/B testing effectiveness
    """
    __tablename__ = "user_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(String(100), nullable=False, index=True)  # Track full customer journey
    job_token = Column(String(50), index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # page_view, click, scroll, input, upload, error
    page_url = Column(String(500), nullable=False)
    element_id = Column(String(200))  # What element was interacted with
    element_text = Column(String(200))  # Button text, link text, etc.

    # Timing metrics (critical for ML)
    time_spent_seconds = Column(Float)
    scroll_depth_percent = Column(Integer)  # How far they scrolled (0-100)

    # Device & browser info (for segmentation)
    device_type = Column(String(20))  # mobile, tablet, desktop
    browser = Column(String(100))
    screen_width = Column(Integer)
    screen_height = Column(Integer)

    # Geographic data (for regional patterns)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))

    # Flexible metadata storage - renamed from 'metadata' to avoid SQLAlchemy reserved name
    interaction_metadata = Column(JSONB)  # Extra data specific to event type

    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Relationships
    company = relationship("Company")


class AIItemPrediction(Base):
    """
    Store individual AI predictions for ML training and improvement
    Tracks confidence scores, manual corrections, and model performance

    ML Use Cases:
    - Retrain models with corrected data
    - Track model accuracy over time
    - A/B test different AI models
    - Identify items AI struggles with
    """
    __tablename__ = "ai_item_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id"), nullable=False, index=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False, index=True)

    # AI prediction
    item_name = Column(String(200), nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0
    bounding_box = Column(JSONB)  # {x, y, width, height} as percentages

    # Dimensions predicted by AI
    predicted_length_cm = Column(Float)
    predicted_width_cm = Column(Float)
    predicted_height_cm = Column(Float)
    predicted_weight_kg = Column(Float)
    predicted_cbm = Column(Float)

    # Classification flags
    predicted_bulky = Column(Boolean, default=False)
    predicted_fragile = Column(Boolean, default=False)

    # Correction tracking (CRITICAL for ML retraining)
    was_accepted = Column(Boolean, default=True, index=True)
    was_manually_corrected = Column(Boolean, default=False, index=True)
    corrected_to_item_name = Column(String(200))
    corrected_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    correction_timestamp = Column(DateTime(timezone=True))

    # Model metadata (for version tracking)
    ai_model_version = Column(String(50))  # e.g., "gpt-4o-mini-2024-07-18"
    ai_processing_time_ms = Column(Integer)  # Performance tracking

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Relationships
    photo = relationship("Photo")
    room = relationship("Room")
    corrected_by = relationship("User")


# ============================================================================
# MARKETPLACE MODELS (Uber for Removals)
# ============================================================================


class MarketplaceJob(Base):
    """
    Marketplace jobs - Customer submits once, multiple companies can bid

    Flow:
    1. Customer fills out central survey (not company-specific)
    2. Job broadcasts to all companies in area
    3. Companies submit bids
    4. Customer picks winning bid
    5. We charge 15% commission
    """
    __tablename__ = "marketplace_jobs"
    __table_args__ = (
        Index('idx_marketplace_jobs_status', 'status'),
        Index('idx_marketplace_jobs_location', 'pickup_city', 'status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(50), nullable=False, unique=True, index=True)  # Customer-facing token
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Location Data
    pickup = Column(JSONB)  # {"label": "...", "lat": ..., "lng": ..., "city": "..."}
    dropoff = Column(JSONB)
    pickup_city = Column(String(100), index=True)  # For fast location queries
    dropoff_city = Column(String(100), index=True)

    # Property Info
    property_type = Column(String(100))

    # Customer Contact
    customer_name = Column(String(255))
    customer_email = Column(String(255), index=True)
    customer_phone = Column(String(50))

    # Inventory Data
    total_cbm = Column(DECIMAL(10, 2), default=0)
    total_weight_kg = Column(DECIMAL(10, 2), default=0)
    total_items = Column(Integer, default=0)
    inventory_summary = Column(JSONB)  # Summary of all items for quick display

    # Status & Lifecycle
    status = Column(String(50), nullable=False, default='in_progress', index=True)
    # States: in_progress, open_for_bids, bids_received, awarded, completed, canceled

    submitted_at = Column(DateTime(timezone=True), index=True)  # When customer submitted
    broadcast_at = Column(DateTime(timezone=True))  # When sent to companies
    awarded_at = Column(DateTime(timezone=True))  # When customer picked winner
    completed_at = Column(DateTime(timezone=True))  # When job finished
    canceled_at = Column(DateTime(timezone=True))

    # Winning Bid
    winning_company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    winning_bid_id = Column(UUID(as_uuid=True), ForeignKey('bids.id'))
    final_price = Column(DECIMAL(10, 2))  # Winning bid amount

    # Commission
    commission_rate = Column(DECIMAL(5, 4), default=0.15)  # 15%
    commission_amount = Column(DECIMAL(10, 2))  # Calculated: final_price * commission_rate
    commission_paid = Column(Boolean, default=False, index=True)
    commission_paid_at = Column(DateTime(timezone=True))

    # Broadcast Settings
    broadcast_radius_miles = Column(Integer, default=50)  # How far to broadcast job
    bid_deadline = Column(DateTime(timezone=True))  # When bids close (48 hours after submission)

    # Relationships
    winning_company = relationship("Company", foreign_keys=[winning_company_id])
    winning_bid = relationship("Bid", foreign_keys=[winning_bid_id])
    rooms = relationship("MarketplaceRoom", back_populates="job", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="job", foreign_keys="Bid.marketplace_job_id")
    broadcasts = relationship("JobBroadcast", back_populates="job", cascade="all, delete-orphan")


class Bid(Base):
    """
    Bids table - Companies bidding on marketplace jobs
    """
    __tablename__ = "bids"
    __table_args__ = (
        Index('idx_bids_job_company', 'marketplace_job_id', 'company_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_job_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Bid Details
    price = Column(DECIMAL(10, 2), nullable=False)  # Total price in GBP
    message = Column(Text)  # Optional message to customer ("We can do this Thursday!")
    estimated_duration_hours = Column(Integer)  # How long job will take
    crew_size = Column(Integer)  # Number of movers

    # Status
    status = Column(String(50), nullable=False, default='pending', index=True)
    # States: pending, accepted, rejected, withdrawn, expired

    accepted_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))
    withdrawn_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), index=True)  # Bid expiry

    # Metadata
    auto_generated = Column(Boolean, default=False)  # If bid was auto-created from pricing rules

    # Relationships
    job = relationship("MarketplaceJob", back_populates="bids", foreign_keys=[marketplace_job_id])
    company = relationship("Company")


class JobBroadcast(Base):
    """
    Track which companies were notified about which marketplace jobs
    Prevents duplicate notifications and tracks engagement
    """
    __tablename__ = "job_broadcasts"
    __table_args__ = (
        Index('idx_broadcasts_job_company', 'marketplace_job_id', 'company_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_job_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)

    # Notification Tracking
    notified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notification_method = Column(String(50))  # email, sms, push

    # Engagement Tracking
    viewed_at = Column(DateTime(timezone=True))  # When company viewed job details
    bid_submitted_at = Column(DateTime(timezone=True))  # When they submitted bid

    # Relationships
    job = relationship("MarketplaceJob", back_populates="broadcasts")
    company = relationship("Company")


class MarketplaceRoom(Base):
    """
    Rooms for marketplace jobs (separate from company-specific rooms)
    """
    __tablename__ = "marketplace_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_job_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Room Data
    name = Column(String(100), nullable=False)  # Living Room, Bedroom 1, etc.
    summary = Column(Text)  # AI-generated summary

    # Relationships
    job = relationship("MarketplaceJob", back_populates="rooms")
    items = relationship("MarketplaceItem", back_populates="room", cascade="all, delete-orphan")
    photos = relationship("MarketplacePhoto", back_populates="room", cascade="all, delete-orphan")


class MarketplaceItem(Base):
    """
    Items detected in marketplace job rooms
    """
    __tablename__ = "marketplace_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_room_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Item Data
    name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)

    # Dimensions
    length_cm = Column(DECIMAL(10, 2))
    width_cm = Column(DECIMAL(10, 2))
    height_cm = Column(DECIMAL(10, 2))
    weight_kg = Column(DECIMAL(10, 2))
    cbm = Column(DECIMAL(10, 4))

    # Flags
    bulky = Column(Boolean, default=False)
    fragile = Column(Boolean, default=False)
    notes = Column(Text)

    # Relationships
    room = relationship("MarketplaceRoom", back_populates="items")


class MarketplacePhoto(Base):
    """
    Photos uploaded for marketplace jobs
    """
    __tablename__ = "marketplace_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_room_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # File Info
    filename = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)  # Path in uploads directory
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))

    # Relationships
    room = relationship("MarketplaceRoom", back_populates="photos")


class Commission(Base):
    """
    Commission tracking - Money owed to PrimeHaul from marketplace transactions
    """
    __tablename__ = "commissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace_job_id = Column(UUID(as_uuid=True), ForeignKey('marketplace_jobs.id'), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Commission Details
    job_price = Column(DECIMAL(10, 2), nullable=False)  # Final price of job
    commission_rate = Column(DECIMAL(5, 4), nullable=False)  # e.g., 0.15 for 15%
    commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Calculated amount

    # Payment Status
    status = Column(String(50), nullable=False, default='pending', index=True)
    # States: pending, processing, paid, failed, refunded

    # Stripe Details
    stripe_charge_id = Column(String(255), unique=True)
    stripe_transfer_id = Column(String(255))  # If using Stripe Connect

    paid_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    failure_reason = Column(Text)

    # Relationships
    job = relationship("MarketplaceJob")
    company = relationship("Company")


class TermsAcceptance(Base):
    """
    Terms & Conditions acceptance tracking - Legal audit trail

    Stores immutable record of customer T&Cs acceptance with:
    - Exact version accepted
    - Document hash at time of acceptance (proof of what was shown)
    - Customer metadata (IP, user agent for legal compliance)
    - Timestamp of acceptance
    """
    __tablename__ = "terms_acceptances"
    __table_args__ = (
        Index('idx_terms_acceptance_job', 'job_id'),
        Index('idx_terms_acceptance_company', 'company_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Version Information (immutable snapshot)
    tcs_version = Column(String(20), nullable=False)  # Version at time of acceptance (e.g., "1.0", "2.1")
    tcs_document_url = Column(Text, nullable=False)  # Document path at time of acceptance
    tcs_document_hash = Column(String(64), nullable=False)  # SHA-256 hash - proof of exact content

    # Customer Information (for legal compliance)
    customer_name = Column(String(255), nullable=False)  # Redundant but important for audit
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50))

    # Technical Metadata (proves genuine acceptance)
    ip_address = Column(String(45))  # IPv6 compatible - proves geographic acceptance
    user_agent = Column(String(500))  # Browser/device info
    acceptance_method = Column(String(50), default='web_form')  # 'web_form', 'email_link', 'admin_override'

    # Status
    accepted = Column(Boolean, nullable=False, default=True)  # True = accepted, False = declined (rare)
    declined_at = Column(DateTime(timezone=True))  # If customer declined T&Cs

    # Relationships
    job = relationship("Job", back_populates="terms_acceptance")
    company = relationship("Company")
