# ⚡ QUICK FIX: Marketplace Customer Flow
**Time to implement:** 30 minutes
**Fixes:** Critical blocker #3 - Marketplace survey is broken

---

## THE PROBLEM

Marketplace customers can't complete surveys because:
1. Marketplace uses `/marketplace/{token}/*` URLs
2. Photo upload expects company-specific paths: `/s/{company_slug}/{token}/upload`
3. Marketplace jobs have NO company initially (they're company-agnostic)
4. This breaks photo uploads and AI analysis

---

## THE SIMPLE FIX

Reuse the existing B2B survey by creating a "Marketplace System Company" that owns all marketplace jobs until they're awarded.

**Why this works:**
- Minimal code changes (30 minutes vs 3 hours)
- Reuses all existing survey logic
- Photos upload correctly
- AI analysis works
- After job is awarded, ownership stays with winning company

---

## IMPLEMENTATION STEPS

### Step 1: Create Marketplace System Company (5 minutes)

```python
# Run this in Python console or create migration

from app.database import get_db
from app.models import Company, PricingConfig
import uuid
from datetime import datetime, timedelta

db = next(get_db())

# Create marketplace system company
marketplace_company = Company(
    company_name="PrimeHaul Marketplace",
    slug="marketplace",
    email="marketplace@primehaul.co.uk",
    subscription_status="active",  # Never expires
    trial_ends_at=None,
    is_active=True,
    onboarding_completed=True,
    primary_color="#2ee59d",
    secondary_color="#000000"
)
db.add(marketplace_company)
db.commit()

# Create pricing config (uses default UK pricing)
pricing = PricingConfig(
    company_id=marketplace_company.id,
    price_per_cbm=35.00,
    callout_fee=250.00,
    bulky_item_fee=25.00,
    fragile_item_fee=15.00
)
db.add(pricing)
db.commit()

print(f"✅ Created marketplace company: {marketplace_company.id}")
```

### Step 2: Update Marketplace Landing Page (10 minutes)

**File: `app/templates/marketplace_landing.html`**

Find the "Start Free Survey" button and update the link:

```html
<!-- OLD: -->
<a href="/marketplace/start" class="cta-button">
    Start Free Survey - It's Free! →
</a>

<!-- NEW: -->
<a href="/s/marketplace/start" class="cta-button">
    Start Free Survey - It's Free! →
</a>
```

### Step 3: Update POST /marketplace/start Endpoint (5 minutes)

**File: `app/main.py` around line 2341**

```python
# OLD:
@app.post("/marketplace/start")
async def marketplace_start(
    db: Session = Depends(get_db)
):
    # Create marketplace job
    token = str(uuid.uuid4())[:8]
    marketplace_job = MarketplaceJob(token=token, status='in_progress')
    db.add(marketplace_job)
    db.commit()

    return RedirectResponse(url=f"/marketplace/{token}/move", status_code=302)

# NEW: Just redirect to marketplace company survey
@app.post("/marketplace/start")
async def marketplace_start():
    """Redirect to marketplace company survey"""
    # Generate token
    token = str(uuid.uuid4())[:8]

    # Redirect to marketplace company survey
    # Marketplace company slug is "marketplace"
    return RedirectResponse(url=f"/s/marketplace/{token}/move", status_code=302)
```

### Step 4: Convert Job to MarketplaceJob After Submission (10 minutes)

**File: `app/main.py`**

After the customer submits their contact details in the B2B flow, convert the Job to a MarketplaceJob:

Add this new endpoint:

```python
@app.post("/s/marketplace/{token}/submit-to-marketplace")
async def submit_to_marketplace(
    token: str,
    request: Request,
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Convert B2B job to marketplace job and broadcast to companies
    This runs after customer completes the marketplace survey
    """
    # Get the marketplace company
    marketplace_company = db.query(Company).filter(Company.slug == "marketplace").first()

    # Get the job (created as B2B job in marketplace company)
    job = db.query(Job).filter(
        Job.token == token,
        Job.company_id == marketplace_company.id
    ).first()

    if not job:
        raise HTTPException(404, "Job not found")

    # Extract location cities
    pickup_city = job.pickup.get('label', '').split(',')[0] if job.pickup else None
    dropoff_city = job.dropoff.get('label', '').split(',')[0] if job.dropoff else None

    # Count inventory
    total_items = db.query(Item).join(Room).filter(Room.job_id == job.id).count()

    # Count bulky/fragile
    items = db.query(Item).join(Room).filter(Room.job_id == job.id).all()
    bulky_count = sum(1 for item in items if item.bulky)
    fragile_count = sum(1 for item in items if item.fragile)

    # Create marketplace job
    marketplace_job = MarketplaceJob(
        token=token,  # Same token for easy linking
        pickup=job.pickup,
        dropoff=job.dropoff,
        pickup_city=pickup_city,
        dropoff_city=dropoff_city,
        property_type=job.property_type,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        total_cbm=job.total_cbm,
        total_weight_kg=job.total_weight_kg,
        total_items=total_items,
        inventory_summary={
            "total_items": total_items,
            "bulky_items": bulky_count,
            "fragile_items": fragile_count,
            "total_cbm": float(job.total_cbm or 0),
            "total_weight_kg": float(job.total_weight_kg or 0)
        },
        status='in_progress',
        submitted_at=datetime.utcnow()
    )
    db.add(marketplace_job)
    db.commit()
    db.refresh(marketplace_job)

    # Copy rooms, items, photos to marketplace tables
    rooms = db.query(Room).filter(Room.job_id == job.id).all()
    for room in rooms:
        # Create marketplace room
        marketplace_room = MarketplaceRoom(
            marketplace_job_id=marketplace_job.id,
            name=room.name,
            summary=room.summary
        )
        db.add(marketplace_room)
        db.commit()

        # Copy items
        items = db.query(Item).filter(Item.room_id == room.id).all()
        for item in items:
            marketplace_item = MarketplaceItem(
                marketplace_room_id=marketplace_room.id,
                name=item.name,
                quantity=item.qty,
                length_cm=item.length_cm,
                width_cm=item.width_cm,
                height_cm=item.height_cm,
                weight_kg=item.weight_kg,
                cbm=item.cbm,
                bulky=item.bulky,
                fragile=item.fragile,
                notes=item.notes
            )
            db.add(marketplace_item)

        # Copy photos
        photos = db.query(Photo).filter(Photo.room_id == room.id).all()
        for photo in photos:
            marketplace_photo = MarketplacePhoto(
                marketplace_room_id=marketplace_room.id,
                filename=photo.filename,
                storage_path=photo.storage_path,
                file_size_bytes=photo.file_size_bytes,
                mime_type=photo.mime_type
            )
            db.add(marketplace_photo)

    db.commit()

    # Broadcast to companies
    from app import marketplace as mkt_module
    from app import notifications

    broadcast_result = mkt_module.broadcast_job_to_companies(
        marketplace_job_id=str(marketplace_job.id),
        db=db,
        radius_miles=50
    )

    # Send confirmation email to customer
    try:
        subject = f"✅ Your quote request is live - {pickup_city} to {dropoff_city}"
        companies_count = broadcast_result.get('companies_notified', 0)

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2ee59d; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #2ee59d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">🎉 Your quote request has been sent!</h2>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p><strong>Great news!</strong> Your removal quote request from {pickup_city} to {dropoff_city} has been sent to <strong>{companies_count} removal companies</strong> in your area.</p>

                    <h3>What happens next:</h3>
                    <ol>
                        <li><strong>Companies review your request</strong> (next 48 hours)</li>
                        <li><strong>You receive quotes via email</strong> as they come in</li>
                        <li><strong>Compare quotes</strong> and pick your favorite</li>
                        <li><strong>Book your move</strong> - that's it!</li>
                    </ol>

                    <center>
                        <a href="https://app.primehaul.co.uk/marketplace/{token}/quotes" class="button">
                            Track Your Quotes →
                        </a>
                    </center>

                    <p style="color: #666; font-size: 14px; margin-top: 30px;">
                        <strong>💡 Pro tip:</strong> Most customers receive 3-5 quotes within 24 hours. We'll email you each time a new quote arrives.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        notifications.send_email(customer_email, subject, html_body)
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")

    # Redirect to quotes page
    return RedirectResponse(url=f"/marketplace/{token}/quotes", status_code=302)
```

### Step 5: Update Quote Preview Page (5 minutes)

**File: `app/templates/quote_preview.html`**

For marketplace jobs, show different submit button:

```html
<!-- Around line 180, update the form action -->

{% if company.slug == 'marketplace' %}
    <!-- Marketplace job - submit to marketplace -->
    <form method="post" action="/s/marketplace/{{ token }}/submit-to-marketplace">
        <!-- Form fields -->
        <button type="submit" class="submit-btn">Submit to Get Quotes</button>
    </form>
{% else %}
    <!-- Regular B2B job -->
    <form method="post" action="/s/{{ company.slug }}/{{ token }}/submit">
        <!-- Form fields -->
        <button type="submit" class="submit-btn">Request Quote</button>
    </form>
{% endif %}
```

---

## TESTING CHECKLIST

After implementing, test the complete flow:

```bash
# 1. Start server
uvicorn app.main:app --reload

# 2. Test marketplace flow
1. Visit: http://localhost:8000/marketplace
2. Click "Start Free Survey"
3. Select pickup/dropoff locations
4. Choose property type
5. Upload photos for each room
6. AI should analyze photos ✅
7. Review quote estimate ✅
8. Enter contact details
9. Click "Submit to Get Quotes"
10. Should redirect to quotes page ✅
11. Check database for MarketplaceJob created ✅
12. Check email for customer confirmation ✅
13. Check email for company notifications ✅

# 3. Test bid submission
1. Login as test company
2. Go to marketplace dashboard
3. View job details
4. Submit bid
5. Customer should receive bid email ✅

# 4. Test bid acceptance
1. As customer, go to quotes page
2. Accept a bid
3. Winner email sent ✅
4. Loser emails sent ✅
5. Commission created ✅
```

---

## RESULT

✅ Marketplace flow now works end-to-end
✅ Reuses all existing B2B survey logic
✅ Photos upload correctly
✅ AI analysis works
✅ Auto-broadcasts to companies
✅ Sends confirmation emails
✅ 30 minutes vs 3 hours to implement

**Ready to launch! 🚀**

---

## ALTERNATIVE: If You Want Clean Separation

If you prefer NOT to mix marketplace and B2B (more work but cleaner architecture), you'll need to:

1. Create separate marketplace survey templates
2. Create separate photo upload endpoint
3. Duplicate room scanning logic
4. Duplicate AI analysis flow

**Time:** 3-4 hours instead of 30 minutes.

**Recommendation:** Use this quick fix to launch NOW, refactor later if needed.

---

**Next:** Fix the other critical blockers (SMTP, OpenAI, Database) and you're ready to launch!
